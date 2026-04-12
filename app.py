from flask import Flask, jsonify, render_template_string, request, redirect, url_for
import os
import pymysql

app = Flask(__name__)

def get_db_connection():
    return pymysql.connect(
        host=os.environ.get('MYSQL_HOST', 'localhost'),
        user=os.environ.get('MYSQL_USER', 'root'),
        password=os.environ.get('MYSQL_PASSWORD', 'root'),
        database=os.environ.get('MYSQL_DB', 'devops'),
        cursorclass=pymysql.cursors.DictCursor
    )

def init_db():
    # This runs automatically to ensure our table exists in MySQL
    try:
        conn = get_db_connection()
        with conn.cursor() as cursor:
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS messages (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    content VARCHAR(255) NOT NULL,
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
        conn.commit()
        conn.close()
    except Exception as e:
        print("Database not ready yet.")

# HTML Template with Bootstrap UI
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>Azure DevOps Project</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css">
    <style>
        body { background-color: #f4f7f9; }
        .hero-section { background: linear-gradient(135deg, #0078D4, #005A9E); color: white; padding: 60px 0; border-radius: 0 0 20px 20px; }
        .status-card { border: none; border-radius: 15px; box-shadow: 0 8px 30px rgba(0,0,0,0.08); margin-top: -30px; }
    </style>
</head>
<body>
    <div class="hero-section text-center">
        <div class="container">
            <h1 class="display-5 fw-bold"><i class="fa-brands fa-microsoft"></i> Azure CI/CD Pipeline</h1>
            <p class="lead mt-2">Two-Tier Application: Web UI + MySQL Database</p>
        </div>
    </div>

    <div class="container pb-5">
        <div class="row justify-content-center">
            <div class="col-md-8">
                
                <div class="card status-card mb-4">
                    <div class="card-body text-center p-4">
                        {% if db_status == 'connected' %}
                            <span class="badge bg-success p-2 fs-6 rounded-pill"><i class="fas fa-database"></i> MySQL Connected</span>
                        {% else %}
                            <span class="badge bg-danger p-2 fs-6 rounded-pill"><i class="fas fa-exclamation-triangle"></i> DB Error: {{ error_msg }}</span>
                        {% endif %}
                    </div>
                </div>

                <div class="card border-0 shadow-sm rounded-4">
                    <div class="card-header bg-white border-0 pt-4 pb-0 px-4">
                        <h4 class="fw-bold text-secondary"><i class="fas fa-comments text-primary"></i> DevOps Message Board</h4>
                        <p class="text-muted small">This data is being actively written to and read from the MySQL Docker container.</p>
                    </div>
                    <div class="card-body p-4">
                        
                        <form method="POST" action="/" class="mb-4">
                            <div class="input-group">
                                <input type="text" name="message" class="form-control form-control-lg" placeholder="Type a message to save in the database..." required>
                                <button class="btn btn-primary px-4" type="submit">Save to DB</button>
                            </div>
                        </form>

                        <div class="list-group">
                            {% for msg in messages %}
                                <div class="list-group-item list-group-item-action d-flex justify-content-between align-items-center py-3">
                                    <span>{{ msg.content }}</span>
                                    <small class="text-muted"><i class="far fa-clock"></i> {{ msg.timestamp }}</small>
                                </div>
                            {% else %}
                                <div class="text-center text-muted py-4">No messages in the database yet. Be the first to add one!</div>
                            {% endfor %}
                        </div>

                    </div>
                </div>

            </div>
        </div>
    </div>
</body>
</html>
"""

@app.route('/', methods=['GET', 'POST'])
def home():
    init_db() # Run the setup function to ensure the table exists
    db_status = "disconnected"
    error_msg = ""
    messages = []
    
    try:
        conn = get_db_connection()
        db_status = "connected"
        
        with conn.cursor() as cursor:
            # 1. WRITE: If a user clicked submit, save the message to MySQL
            if request.method == 'POST':
                new_message = request.form.get('message')
                if new_message:
                    cursor.execute("INSERT INTO messages (content) VALUES (%s)", (new_message,))
                    conn.commit()
                    return redirect(url_for('home')) # Refresh the page to prevent duplicate submissions
            
            # 2. READ: Fetch the 10 most recent messages from MySQL
            cursor.execute("SELECT * FROM messages ORDER BY timestamp DESC LIMIT 10")
            messages = cursor.fetchall()
            
        conn.close()
    except Exception as e:
        error_msg = str(e)
    
    return render_template_string(HTML_TEMPLATE, db_status=db_status, error_msg=error_msg, messages=messages)

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