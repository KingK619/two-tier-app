from flask import Flask, jsonify, render_template_string
import os
import pymysql

app = Flask(__name__)

# Database connection function
def get_db_connection():
    return pymysql.connect(
        host=os.environ.get('MYSQL_HOST', 'localhost'),
        user=os.environ.get('MYSQL_USER', 'root'),
        password=os.environ.get('MYSQL_PASSWORD', 'root'),
        database=os.environ.get('MYSQL_DB', 'devops'),
        cursorclass=pymysql.cursors.DictCursor
    )

# The HTML & CSS User Interface (Using Bootstrap 5)
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Azure DevOps Project</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css">
    <style>
        body { background-color: #f4f7f9; }
        .hero-section { 
            background: linear-gradient(135deg, #0078D4, #005A9E); /* Azure Blue Gradient */
            color: white; 
            padding: 80px 0; 
            border-radius: 0 0 20px 20px; 
            box-shadow: 0 4px 15px rgba(0,0,0,0.1); 
        }
        .status-card { 
            border: none; 
            border-radius: 15px; 
            box-shadow: 0 8px 30px rgba(0,0,0,0.08); 
            margin-top: -40px; /* Overlaps the hero section slightly */
        }
    </style>
</head>
<body>
    <div class="hero-section text-center">
        <div class="container">
            <h1 class="display-4 fw-bold"><i class="fa-brands fa-microsoft"></i> Azure CI/CD Pipeline</h1>
            <p class="lead mt-3">Automated Containerized Deployment using Jenkins & Docker</p>
        </div>
    </div>

    <div class="container pb-5">
        <div class="row justify-content-center">
            <div class="col-md-8">
                <div class="card status-card">
                    <div class="card-body text-center p-5">
                        <h3 class="card-title text-secondary mb-4">Live Architecture Status</h3>
                        
                        {% if db_status == 'connected' %}
                            <div class="alert alert-success mb-4 py-4" role="alert">
                                <i class="fas fa-check-circle fs-1 mb-3"></i>
                                <h4 class="alert-heading fw-bold">All Systems Operational!</h4>
                                <p class="mb-0">The Flask application has successfully authenticated and connected to the internal MySQL database container.</p>
                            </div>
                            <span class="badge bg-success p-2 fs-6 rounded-pill"><i class="fas fa-database"></i> MySQL: Online</span>
                            <span class="badge bg-primary p-2 fs-6 rounded-pill ms-2"><i class="fas fa-server"></i> Web: Online</span>
                        {% else %}
                            <div class="alert alert-danger mb-4 py-4" role="alert">
                                <i class="fas fa-exclamation-triangle fs-1 mb-3"></i>
                                <h4 class="alert-heading fw-bold">Database Connection Failed</h4>
                                <p class="mb-0">The web server is running, but it cannot reach the MySQL database.</p>
                                <hr>
                                <small class="text-muted">Error Output: {{ error_msg }}</small>
                            </div>
                            <span class="badge bg-danger p-2 fs-6 rounded-pill"><i class="fas fa-database"></i> MySQL: Offline</span>
                            <span class="badge bg-primary p-2 fs-6 rounded-pill ms-2"><i class="fas fa-server"></i> Web: Online</span>
                        {% endif %}
                        
                    </div>
                    <div class="card-footer text-muted text-center py-3 bg-white border-0">
                        <small>Engineered by Prashant Gohel</small>
                    </div>
                </div>
            </div>
        </div>
    </div>
</body>
</html>
"""

@app.route('/')
def home():
    # Variables to pass to the HTML
    db_status = "disconnected"
    error_msg = ""
    
    try:
        # We attempt to ping the database to prove the Docker Network is working
        conn = get_db_connection()
        conn.close()
        db_status = "connected"
    except Exception as e:
        error_msg = str(e)
    
    # render_template_string reads the HTML block above and injects our variables
    return render_template_string(HTML_TEMPLATE, db_status=db_status, error_msg=error_msg)

# Do not touch the health check, Docker needs this!
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