from flask import Flask, jsonify, render_template
import psycopg2
import os

app = Flask(__name__)

# Database connection
def get_db_connection():
    return psycopg2.connect(
        host=os.getenv("DB_HOST"),
        database=os.getenv("DB_NAME"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASS")
    )

@app.route('/')
def home():
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("SELECT id, detection_time, license_plate_text FROM license_plates ORDER BY detection_time DESC")
        rows = cur.fetchall()
        cur.close()
        conn.close()

        detections = [{"id": row[0], "time": row[1].isoformat(), "license_plate_text": row[2]} for row in rows]
        return render_template('index.html', detections=detections)
    except Exception as e:
        return f"Error: {str(e)}", 500

@app.route('/data', methods=['GET'])
def get_data():
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("SELECT id, detection_time, license_plate_text FROM license_plates ORDER BY detection_time DESC")
        rows = cur.fetchall()
        cur.close()
        conn.close()

        data = [{"id": row[0], "time": row[1].isoformat(), "license_plate_text": row[2]} for row in rows]
        return jsonify(data)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=8080)