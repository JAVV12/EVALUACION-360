import os
import sqlite3
import json
import pandas as pd
from datetime import datetime, timedelta
import database as db
import logic
import utils

def test_logic_calculations():
    print("Testing Logic Calculations...")
    # Mock data for one leader
    # All 5s for Self
    # All 3s for Observers (1 obsever)
    mock_data = [
        {"leader_name": "Test Leader", "role": "Líder", "scores": [5]*30},
        {"leader_name": "Test Leader", "role": "Observador", "scores": [3]*30}
    ]
    
    # Process into DF
    flat_data = []
    for m in mock_data:
        entry = {"leader_name": m["leader_name"], "role": m["role"]}
        for i, s in enumerate(m["scores"]):
            entry[f"p{i+1}"] = s
        flat_data.append(entry)
    
    df = pd.DataFrame(flat_data)
    results = logic.calculate_scores(df)
    
    leader_stats = results["Test Leader"]
    for comm in logic.COMMITMENTS.keys():
        assert leader_stats[comm]["Self"] == 5.0
        assert leader_stats[comm]["Observers"] == 3.0
        assert leader_stats[comm]["Gap"] == -2.0
    
    print("Logic calculations passed.")

def test_database_operations():
    print("Testing Database Operations...")
    db.init_db()
    comp_id = db.create_company("Test Company Inc")
    assert comp_id is not None
    
    eval_id = db.add_evaluation(comp_id, "Jane Doe", "Lider", [4]*30)
    assert eval_id is not None
    
    data = db.get_evaluations_by_company(comp_id)
    assert len(data) == 1
    assert data[0]["leader_name"] == "Jane Doe"
    assert data[0]["p1"] == 4
    
    print("Database operations passed.")

def test_ttl_logic():
    print("Testing TTL (Retention) Logic...")
    conn = db.get_connection()
    c = conn.cursor()
    
    # Create an old company (73 hours ago)
    old_time = datetime.now() - timedelta(hours=73)
    c.execute("INSERT INTO companies (name, created_at) VALUES (?, ?)", ("Expired Co", old_time))
    comp_id = c.lastrowid
    
    # Add evaluation for it
    c.execute("INSERT INTO evaluations (company_id, leader_name, role, scores, created_at) VALUES (?, ?, ?, ?, ?)",
              (comp_id, "Old Leader", "Lider", json.dumps([3]*30), old_time))
    conn.commit()
    
    # Verify they exist
    c.execute("SELECT count(*) FROM companies WHERE name = 'Expired Co'")
    assert c.fetchone()[0] == 1
    
    # Run cleaner
    utils.clean_expired_data()
    
    # Verify they are gone
    c.execute("SELECT count(*) FROM companies WHERE name = 'Expired Co'")
    assert c.fetchone()[0] == 0
    c.execute("SELECT count(*) FROM evaluations WHERE company_id = ?", (comp_id,))
    assert c.fetchone()[0] == 0
    
    conn.close()
    print("TTL logic passed.")

if __name__ == "__main__":
    try:
        # Clear existing DB for tests
        if os.path.exists(db.DB_NAME):
            os.remove(db.DB_NAME)
            
        test_logic_calculations()
        test_database_operations()
        test_ttl_logic()
        print("\nALL TESTS PASSED. CODE IS READY FOR DELIVERY.")
    except Exception as e:
        print(f"\nTEST FAILED: {str(e)}")
        import traceback
        traceback.print_exc()
