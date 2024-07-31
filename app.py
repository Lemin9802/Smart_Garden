from flask import Flask, request, jsonify
from flask_cors import CORS
import sqlite3

app = Flask(__name__)
CORS(app)

def get_db_connection():
    conn = sqlite3.connect('smart_garden.db')
    conn.row_factory = sqlite3.Row
    return conn

@app.route('/register', methods=['POST'])
def register():
    data = request.json
    username = data['username']
    password = data['password']
    role = data['role']
    
    if role != 'staff':
        return jsonify({'message': 'Invalid role, only "staff" role is allowed for registration'}), 400
    
    conn = get_db_connection()
    try:
        conn.execute('INSERT INTO users (username, password, role) VALUES (?, ?, ?)', 
                     (username, password, role))
        conn.commit()
        return jsonify({'message': 'User registered successfully'}), 201
    except sqlite3.IntegrityError:
        return jsonify({'message': 'Username already exists'}), 400
    finally:
        conn.close()

@app.route('/login', methods=['POST'])
def login():
    data = request.json
    username = data['username']
    password = data['password']
    
    conn = get_db_connection()
    user = conn.execute('SELECT * FROM users WHERE username = ? AND password = ?', 
                        (username, password)).fetchone()
    conn.close()
    
    if user:
        return jsonify({'role': user['role']}), 200
    else:
        return jsonify({'message': 'Invalid credentials'}), 401

@app.route('/sensor_data', methods=['GET'])
def get_sensor_data():
    conn = get_db_connection()
    data = conn.execute('SELECT * FROM sensor_data ORDER BY timestamp DESC LIMIT 1').fetchone()
    conn.close()
    
    if data:
        return jsonify({'temperature': data['temperature'], 'humidity': data['humidity'], 'timestamp': data['timestamp']}), 200
    else:
        return jsonify({'message': 'No sensor data available'}), 404

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000, debug=True)
