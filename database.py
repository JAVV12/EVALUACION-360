import os
import json
from supabase import create_client, Client
import streamlit as st

# Cargar credenciales desde secrets de Streamlit (o variables de entorno)
SUPABASE_URL = st.secrets.get("SUPABASE_URL") or os.environ.get("SUPABASE_URL")
SUPABASE_KEY = st.secrets.get("SUPABASE_KEY") or os.environ.get("SUPABASE_KEY")

# Solo inicializar si las credenciales están presentes
supabase: Client = None
if SUPABASE_URL and SUPABASE_KEY:
    supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

def init_db():
    """En Supabase las tablas se crean vía SQL Editor, por lo que esta función es un placeholder."""
    pass

def create_company(name):
    if not supabase: return None
    try:
        # Intentar insertar
        response = supabase.table("companies").insert({"name": name}).execute()
        if response.data:
            return response.data[0]["id"]
    except Exception:
        # Si ya existe, buscarlo
        response = supabase.table("companies").select("id").eq("name", name).execute()
        if response.data:
            return response.data[0]["id"]
    return None

def get_company_by_id(company_id):
    if not supabase: return None
    response = supabase.table("companies").select("*").eq("id", company_id).execute()
    return response.data[0] if response.data else None

def get_company_by_name(name):
    if not supabase: return None
    response = supabase.table("companies").select("*").eq("name", name).execute()
    return response.data[0] if response.data else None

def add_evaluation(company_id, leader_name, role, scores):
    if not supabase: return None
    # Asegurar que scores sea una lista para JSONB
    if isinstance(scores, str):
        scores = json.loads(scores)
        
    data = {
        "company_id": company_id,
        "leader_name": leader_name,
        "role": role,
        "scores": scores
    }
    response = supabase.table("evaluations").insert(data).execute()
    return response.data[0]["id"] if response.data else None

def get_evaluations_by_company(company_id):
    if not supabase: return []
    response = supabase.table("evaluations").select("*").eq("company_id", company_id).execute()
    rows = response.data
    
    data = []
    for r in rows:
        # r: id, company_id, leader_name, role, scores (list/dict), created_at
        scores = r["scores"]
        entry = {
            "id": r["id"],
            "leader_name": r["leader_name"],
            "role": r["role"],
            "created_at": r["created_at"]
        }
        # Desempaquetar scores p1..p30 (asumimos que scores es una lista de 30 elementos)
        for i, s in enumerate(scores):
            entry[f"p{i+1}"] = s
        data.append(entry)
    return data

def get_all_companies():
    if not supabase: return []
    response = supabase.table("companies").select("name").order("name").execute()
    return [r["name"] for r in response.data] if response.data else []
