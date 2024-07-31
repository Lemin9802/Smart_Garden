import sqlite3

def create_db():
    conn = sqlite3.connect('smart_garden.db')
    c = conn.cursor()

    c.execute('''CREATE TABLE IF NOT EXISTS users (
                 id INTEGER PRIMARY KEY AUTOINCREMENT,
                 username TEXT UNIQUE NOT NULL,
                 password TEXT NOT NULL,
                 role TEXT NOT NULL)''')

    c.execute('''CREATE TABLE IF NOT EXISTS sensor_data (
                 id INTEGER PRIMARY KEY AUTOINCREMENT,
                 temperature REAL,
                 humidity REAL,
                 timestamp DATETIME DEFAULT CURRENT_TIMESTAMP)''')

    c.execute('''CREATE TABLE IF NOT EXISTS face_images (
                 id INTEGER PRIMARY KEY AUTOINCREMENT,
                 image BLOB,
                 timestamp DATETIME DEFAULT CURRENT_TIMESTAMP)''')

    try:
        c.execute('''INSERT INTO users (username, password, role) 
                     VALUES (?, ?, ?)''', 
                     ('admin', 'admin_password', 'admin'))
        conn.commit()
    except sqlite3.IntegrityError:
        pass  

    conn.close()

if __name__ == "__main__":
    create_db()
