from flask import Flask, jsonify, request

app = Flask(__name__)

@app.route('/')
def home():
    return jsonify({"message": "Flask app is running on port 5000"})

@app.route('/predict', methods=['POST'])
def predict():
    data = request.get_json()
    result = {"prediction": "model result here", "input": data}
    return jsonify(result)

@app.route('/health', methods=['GET'])
def health():
    return jsonify({"status": "ok", "service": "Flask App"})

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000)
