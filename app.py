from flask import Flask, jsonify

app = Flask(__name__)

@app.route('/health', methods=['GET'])
def health_check():
    # Simulate a database health check
    db_status = {'status': 'healthy'}  # Replace this with actual DB check logic
    return jsonify(db_status), 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)