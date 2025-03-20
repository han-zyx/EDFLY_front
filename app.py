from flask import Flask, request, render_template

app = Flask(__name__)

@app.route('/receive', methods=['POST'])
def receive_data():
    data = request.json
    print(f"Received on EC2: {data}")
    return {"status": "success"}, 200

@app.route('/', methods=['GET'])
def home():
    return render_template('index.html')

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=8080)