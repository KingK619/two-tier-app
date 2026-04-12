from flask import Flask, jsonify
import os
import pymysql
app = Flask(__name__)
def get_db_connection():
    return pymysql.connect(
    host=os.environ.get('MYSQL_HOST', 'localhost'),
    users=os.environ.get('MYSQL_USER', 'root'),
    password=os.environ.get('MYSQL_PASSWORD', 'root'),
    database=os.environ.get('MYSQL_DB', 'devops')
)
@app.route('/')
def home():
    return "<h1>Welcome to my Automated Azure Project!</h1>"
@app.route('/health')
def health():
    try:
        conn = get_db_connection()
        conn.close()
        return jsonify({"status": "healthy", "database": "connected"}), 200
    except Exception as e:
        return jsonify({"status": "unhealthy", "error": str(e)}), 500
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
