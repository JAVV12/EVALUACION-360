import pandas as pd
import numpy as np

# Kouzes & Posner 5 Commitments mapping
COMMITMENTS = {
    "Desafiar": [1, 6, 11, 16, 21, 26],
    "Inspirar": [2, 7, 12, 17, 22, 27],
    "Habilitar": [3, 8, 13, 18, 23, 28],
    "Modelar": [4, 9, 14, 19, 24, 29],
    "Alentar": [5, 10, 15, 20, 25, 30]
}

COMMITMENT_DESCRIPTIONS = {
    "Desafiar": "Desafiar los procesos",
    "Inspirar": "Inspirar una visión compartida",
    "Habilitar": "Habilitar a otros para actuar",
    "Modelar": "Modelar el camino",
    "Alentar": "Alentar el corazón"
}

def calculate_scores(df_evaluations):
    """
    df_evaluations input columns: 'leader_name', 'role' (Self vs Observer), 'p1'...'p30'.
    Returns a processed DataFrame with scores per commitment per leader per role-type.
    """
    if df_evaluations.empty:
        return {}

    # Calculate average per commitment for each row
    for comm, questions in COMMITMENTS.items():
        cols = [f"p{q}" for q in questions]
        # Check if columns exist
        available_cols = [c for c in cols if c in df_evaluations.columns]
        if available_cols:
            df_evaluations[comm] = df_evaluations[available_cols].mean(axis=1)
        else:
            df_evaluations[comm] = 0

    results = {}
    
    # Group by Leader
    leaders = df_evaluations['leader_name'].unique()
    
    for leader in leaders:
        leader_df = df_evaluations[df_evaluations['leader_name'] == leader]
        
        # Separate Self vs Observers
        # Assuming role standardized strings
        is_self = leader_df['role'].str.contains("Auto", case=False) | leader_df['role'].str.contains("Self", case=False) | leader_df['role'].str.contains("Líder", case=False)
        
        self_df = leader_df[is_self]
        obs_df = leader_df[~is_self]
        
        leader_stats = {}
        
        for comm in COMMITMENTS.keys():
            s_score = self_df[comm].mean() if not self_df.empty else 0
            o_score = obs_df[comm].mean() if not obs_df.empty else 0
            
            leader_stats[comm] = {
                "Self": round(s_score, 2),
                "Observers": round(o_score, 2),
                "Gap": round(o_score - s_score, 2) # Gap = Obs - Self. If Negative, Self Rated Higher (Overrated?). If Positive, Self Rated Lower.
            }
            
        results[leader] = leader_stats
        
    return results

def generate_insights(leader_stats):
    """
    Generate automated feedback text based on scores.
    leader_stats is the dict of commitments for one leader.
    """
    feedback = []
    
    for comm, stats in leader_stats.items():
        gap = stats["Gap"]
        obs_score = stats["Observers"]
        
        # Rule 1: High Blind Spot (Self >>> Observers)
        # Gap is largely negative (e.g. 3 - 5 = -2)
        if gap < -1.0:
            feedback.append(f"⚠️ **{comm}**: Su autoevaluación es significativamente más alta que la de sus observadores. Podría tener un punto ciego sobre su impacto real en esta área.")
            
        # Rule 2: Hidden Strength (Self <<< Observers)
        # Gap is largely positive (e.g. 5 - 3 = +2)
        elif gap > 1.0:
            feedback.append(f"🌟 **{comm}**: Sus observadores lo valoran mucho más alto que usted mismo. ¡Reconozca sus fortalezas!")
            
        # Rule 3: Low Performance
        if obs_score < 3.5:
             feedback.append(f"📉 **{comm}**: El puntaje promedio ({obs_score}) indica una oportunidad de mejora. Se sugiere reforzar comportamientos relacionados con {COMMITMENT_DESCRIPTIONS[comm].lower()}.")
             
    if not feedback:
        feedback.append("✅ Su perfil muestra un balance saludable entre su autopercepción y la de su equipo.")
        
    return feedback
