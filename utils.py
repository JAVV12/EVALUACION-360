import os
import shutil
import sqlite3
from datetime import datetime, timedelta
import pandas as pd
import json
import database as db

RETENTION_HOURS = 72

def clean_expired_data():
    """
    Removes companies and their data that are older than RETENTION_HOURS.
    """
    conn = db.get_connection()
    c = conn.cursor()
    
    threshold = datetime.now() - timedelta(hours=RETENTION_HOURS)
    
    # Find expired companies
    c.execute("SELECT id, name FROM companies WHERE created_at < ?", (threshold,))
    expired_companies = c.fetchall()
    
    for comp_id, comp_name in expired_companies:
        # Delete evaluations
        c.execute("DELETE FROM evaluations WHERE company_id = ?", (comp_id,))
        # Delete company
        c.execute("DELETE FROM companies WHERE id = ?", (comp_id,))
        print(f"Deleted expired company: {comp_name}")
        
    conn.commit()
    conn.close()

def process_excel_upload(file_obj, company_id):
    """
    Reads an Excel/CSV file and saves evaluations to the database.
    Expected columns: 'Lider', 'Rol', 'P1', 'P2', ... 'P30'.
    """
    try:
        if file_obj.name.endswith('.csv'):
            df = pd.read_csv(file_obj)
        else:
            df = pd.read_excel(file_obj)
        
        # Normalize columns
        df.columns = [c.strip().lower() for c in df.columns]
        
        # Identify generic columns
        leader_col = next((c for c in df.columns if 'lider' in c or 'leader' in c or 'nombre' in c), None)
        role_col = next((c for c in df.columns if 'rol' in c or 'role' in c), None)
        
        if not leader_col or not role_col:
            return 0, "No se encontraron las columnas 'Lider' o 'Rol'."
        
        # Find score columns (P1..P30)
        # Assuming they contain numbers 1-30 or start with 'p'
        # We'll just look for columns that likely map to 1-30
        
        count = 0
        for _, row in df.iterrows():
            leader = row[leader_col]
            role = row[role_col]
            
            # Extract scores
            # Try to find columns P1..P30 specifically
            scores = []
            valid_row = True
            for i in range(1, 31):
                # Try variations: "P1", "p1", "1", "Pregunta 1"
                col_name = next((c for c in df.columns if c == f"p{i}" or c == str(i)), None)
                if not col_name:
                    # Fallback: maybe columns are ordered and we skip first few?
                    # Let's be strict for now: Input file MUST have P1..P30 or similiar
                    valid_row = False
                    break
                
                try:
                    score = int(row[col_name])
                    if not (1 <= score <= 5):
                        score = 3 # Default if out of range
                except:
                    score = 3
                scores.append(score)
            
            if valid_row and len(scores) == 30:
                # Save to DB
                # Map role to standard names
                std_role = "Autoevaluación (Líder)" if "auto" in str(role).lower() or "self" in str(role).lower() or "lider" in str(role).lower() else "Observador (Equipo/Par/Jefe)"
                
                db.add_evaluation(company_id, leader, std_role, scores)
                count += 1
                
        return count, ""
    
    except Exception as e:
        return 0, str(e)
