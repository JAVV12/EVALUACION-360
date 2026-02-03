import sqlite3
import datetime
import json

DB_NAME = "liderazgo360.db"

def get_connection():
    return sqlite3.connect(DB_NAME)

def init_db():
    conn = get_connection()
    c = conn.cursor()
    # Create tables
    c.execute('''CREATE TABLE IF NOT EXISTS companies
                 (id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT UNIQUE, created_at TIMESTAMP)''')
    
    c.execute('''CREATE TABLE IF NOT EXISTS evaluations
                 (id INTEGER PRIMARY KEY AUTOINCREMENT, company_id INTEGER, leader_name TEXT, 
                  role TEXT, scores TEXT, created_at TIMESTAMP,
                  FOREIGN KEY(company_id) REFERENCES companies(id))''')
    conn.commit()
    conn.close()

def create_company(name):
    conn = get_connection()
    c = conn.cursor()
    try:
        created_at = datetime.datetime.now()
        c.execute("INSERT INTO companies (name, created_at) VALUES (?, ?)", (name, created_at))
        conn.commit()
        return c.lastrowid
    except sqlite3.IntegrityError:
        # Company already exists, get ID and update timestamp? Or just get ID.
        # For ephemeral nature, maybe we just return the existing ID.
        c.execute("SELECT id FROM companies WHERE name = ?", (name,))
        res = c.fetchone()
        return res[0] if res else None
    finally:
        conn.close()

def get_company_by_id(company_id):
    conn = get_connection()
    c = conn.cursor()
    c.execute("SELECT * FROM companies WHERE id = ?", (company_id,))
    res = c.fetchone()
    conn.close()
    return res

def get_company_by_name(name):
    conn = get_connection()
    c = conn.cursor()
    c.execute("SELECT * FROM companies WHERE name = ?", (name,))
    res = c.fetchone()
    conn.close()
    return res

def add_evaluation(company_id, leader_name, role, scores):
    """
    scores should be a list of 30 integers (1-5) or a JSON string.
    We'll store it as JSON string.
    """
    if isinstance(scores, list):
        scores = json.dumps(scores)
        
    conn = get_connection()
    c = conn.cursor()
    created_at = datetime.datetime.now()
    c.execute("INSERT INTO evaluations (company_id, leader_name, role, scores, created_at) VALUES (?, ?, ?, ?, ?)",
              (company_id, leader_name, role, scores, created_at))
    conn.commit()
    row_id = c.lastrowid
    conn.close()
    return row_id

def get_evaluations_by_company(company_id):
    conn = get_connection()
    c = conn.cursor()
    c.execute("SELECT * FROM evaluations WHERE company_id = ?", (company_id,))
    rows = c.fetchall()
    conn.close()
    
    # Process rows to return a structured list/df friendly format
    data = []
    for r in rows:
        # r: id, company_id, leader_name, role, scores, created_at
        scores = json.loads(r[4])
        entry = {
            "id": r[0],
            "leader_name": r[2],
            "role": r[3],
            "created_at": r[5]
        }
        # Unpack scores p1..p30
        for i, s in enumerate(scores):
            entry[f"p{i+1}"] = s
        data.append(entry)
    return data

def get_all_companies():
    conn = get_connection()
    c = conn.cursor()
    c.execute("SELECT name FROM companies ORDER BY name ASC")
    res = c.fetchall()
    conn.close()
    return [r[0] for r in res]

if __name__ == "__main__":
    init_db()
