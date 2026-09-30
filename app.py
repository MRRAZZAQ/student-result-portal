from flask import Flask, request, jsonify, Response

app = Flask(__name__)
results = []

@app.route('/items', methods=['GET'])
def get_results():
    return jsonify(results), 200

@app.route('/items', methods=['POST'])
def add_result():
    data = request.get_json()
    new_result = {'id': len(results) + 1, 'student_name': data['student_name'], 'marks': data['marks']}
    results.append(new_result)
    return jsonify(new_result), 201

@app.route('/health', methods=['GET'])
def health_check():
    # Prometheus requires metrics in plain text format
    return Response("flask_app_status 1\n", mimetype="text/plain")

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)