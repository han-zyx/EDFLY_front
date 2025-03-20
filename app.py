from flask import Flask, request, render_template, jsonify
import psycopg2
import os

app = Flask(__name__)

# Database connection using environment variables
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

        # Map database fields to front-end expected keys
        detections = [
            {
                "record_id": row[0],           # Unique record ID
                "id": row[1],                  # Detection ID from JSON
                "time": row[2].isoformat(),    # Detection time
                "license_plate_text": row[3]   # License plate text
            } for row in rows
        ]
        return render_template('index.html', detections=detections)
    except Exception as e:
        print(f"Error fetching data: {str(e)}")
        return f"Error: {str(e)}", 500

if __name__ == "__main__":
    # For local testing only; Gunicorn is used in Docker
    app.run(host='0.0.0.0', port=8080)