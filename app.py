from flask import Flask, request, render_template, jsonify
import psycopg2
import os

app = Flask(__name__, template_folder='templates', static_folder='static')


def get_db_connection():
    try:
        return psycopg2.connect(
            host=os.getenv("DB_HOST"),
            database=os.getenv("DB_NAME"),
            user=os.getenv("DB_USER"),
            password=os.getenv("DB_PASS")
        )
    except Exception as e:
        print(f"Database connection failed: {str(e)}")
        raise
    
    
@app.route('/receive', methods=['POST'])
def receive_data():
    data = request.json
    print(f"Received on EC2: {data}")
    
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        
        if "detections" in data:
            for detection in data["detections"]:
                cur.execute(
                    "INSERT INTO license_plates (detection_id, detection_time, license_plate_text) VALUES (%s, %s, %s)",
                    (detection["id"], detection["time"].replace("Z", "").replace("T", " "), detection["license_plate_text"])
                )
        conn.commit()
        cur.close()
        conn.close()
        print("Data saved to RDS")
        return {"status": "success"}, 200
    except Exception as e:
        print(f"Error saving to RDS: {str(e)}")
        return {"status": "error", "message": str(e)}, 500

@app.route('/', methods=['GET'])
def home():
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("SELECT record_id, detection_id, detection_time, license_plate_text FROM license_plates ORDER BY detection_time DESC")
        rows = cur.fetchall()
        cur.close()
        conn.close()

        detections = [
            {
                "record_id": row[0],
                "id": row[1],
                "time": row[2].isoformat(),
                "license_plate_text": row[3]
            } for row in rows
        ]
        return render_template('index.html', detections=detections)
    except Exception as e:
        print(f"Error fetching data: {str(e)}")
        return f"Error: {str(e)}", 500

@app.route('/detections', methods=['GET'])
def detections():
    try:
        conn = get_db_connection()
        cur = conn.cursor()
       
        items_per_page = 10
        page = request.args.get('page', 1, type=int)  
        offset = (page - 1) * items_per_page
    
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')
      
        count_query = "SELECT COUNT(*) FROM license_plates"
        count_params = []
      
        query = "SELECT record_id, detection_id, detection_time, license_plate_text FROM license_plates"
        params = []
       
        if start_date and end_date:
            count_query += " WHERE detection_time BETWEEN %s AND %s"
            query += " WHERE detection_time BETWEEN %s AND %s"
            count_params.extend([start_date, end_date])
            params.extend([start_date, end_date])
        elif start_date:
            count_query += " WHERE detection_time >= %s"
            query += " WHERE detection_time >= %s"
            count_params.append(start_date)
            params.append(start_date)
        elif end_date:
            count_query += " WHERE detection_time <= %s"
            query += " WHERE detection_time <= %s"
            count_params.append(end_date)
            params.append(end_date)
        
        query += " ORDER BY record_id DESC LIMIT %s OFFSET %s"
        params.extend([items_per_page, offset])
       
        cur.execute(count_query, count_params)
        total_detections = cur.fetchone()[0]
      
        total_pages = (total_detections + items_per_page - 1) // items_per_page
      
        cur.execute(query, params)
        rows = cur.fetchall()
        cur.close()
        conn.close()

        detections = [
            {
                "record_id": row[0],
                "id": row[1],
                "time": row[2].isoformat(),
                "license_plate_text": row[3]
            } for row in rows
        ]

        return render_template(
            'detections.html',
            detections=detections,
            total_detections=total_detections,
            items_per_page=items_per_page,
            current_page=page,
            total_pages=total_pages
        )
    except Exception as e:
        print(f"Error fetching data: {str(e)}")
        return f"Error: {str(e)}", 500

@app.route('/about', methods=['GET'])
def about():
    return render_template('about.html')

@app.route('/developer', methods=['GET'])
def developer():
    return render_template('developer.html')

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=8080)
    
    
    
    