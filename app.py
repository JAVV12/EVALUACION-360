import streamlit as st
import pandas as pd
import importlib
import database as db
import logic
from utils import clean_expired_data

# Force reload database module to pick up new functions
importlib.reload(db)

# v1.1 - Added get_all_companies support

# Initialize DB and clean old data
db.init_db()
clean_expired_data()

st.set_page_config(page_title="Liderazgo 360", layout="wide")

# Custom CSS & Tailwind Integration
st.markdown("""
    <!-- Tailwind CSS CDN -->
    <script src="https://cdn.tailwindcss.com"></script>
    
    <!-- Bootstrap Icons CDN -->
    <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap-icons@1.11.3/font/bootstrap-icons.min.css">
    
    <script>
      tailwind.config = {
        theme: {
          extend: {
            colors: {
              navy: '#001f3f',
              sand: '#fffcf2',
              gold: '#d4af37',
              goldlight: '#f1d592',
            },
            animation: {
              'fade-in': 'fadeIn 0.6s ease-out forwards',
            },
            keyframes: {
              fadeIn: {
                '0%': { opacity: '0', transform: 'translateY(10px)' },
                '100%': { opacity: '1', transform: 'translateY(0)' },
              }
            }
          }
        }
      }
    </script>
    
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;700;800&display=swap');

    /* Header Branding */
    header[data-testid="stHeader"] {
        background-color: #001f3f !important;
    }
    
    header[data-testid="stHeader"] * {
        color: #FFFFFF !important;
    }
    
    /* Ensure form submission button matches the premium style */
    div[data-testid="stFormSubmitButton"] button {
      --bezier: cubic-bezier(0.22, 0.61, 0.36, 1);
      --edge-light: hsla(46, 65%, 80%, 0.8);
      --text-light: rgba(255, 255, 255, 0.4);
      --back-color: 46, 65%; /* Gold base */

      cursor: pointer;
      padding: 0.7em 2em !important;
      border-radius: 0.8em !important;
      min-height: 2.8em !important;
      display: flex;
      align-items: center;
      gap: 0.5em;

      font-size: 18px !important;
      letter-spacing: 0.05em;
      line-height: 1;
      font-weight: bold !important;

      background: linear-gradient(
        140deg,
        hsla(var(--back-color), 52%, 1) 20%,
        hsla(var(--back-color), 40%, 0.6) 100%
      ) !important;
      color: #001f3f !important; /* Navy text */
      border: 0 !important;
      box-shadow: inset 0.4px 1px 4px var(--edge-light), 0 4px 15px rgba(212, 175, 55, 0.2) !important;

      transition: all 0.2s var(--bezier) !important;
      width: 100% !important; /* Make it consistent in form */
    }

    div[data-testid="stFormSubmitButton"] button:hover {
      --edge-light: hsla(46, 65%, 90%, 1);
      text-shadow: 0px 0px 10px var(--text-light);
      box-shadow: inset 0.4px 1px 4px var(--edge-light),
        0 8px 20px hsla(46, 65%, 10%, 0.3) !important;
      transform: scale(1.02) translateY(-2px) !important;
      background: white !important;
      color: #001f3f !important;
    }
    
    .stApp {
        background-color: #fffcf2; /* Blanco Arena */
        color: #001f3f; /* Azul Marino (Global Default) */
        font-family: 'Inter', sans-serif;
    }
    
    /* Global Markdown & Text override to Navy */
    .stApp [data-testid="stMarkdownContainer"], 
    .stApp p, .stApp span, .stApp label, .stApp h1, .stApp h2, .stApp h3 {
        color: #001f3f !important;
    }

    /* Uiverse Style Search Box Adaptation */
    .uiverse-search-wrapper {
        background-color: rgba(0, 31, 63, 0.05);
        padding: 2rem;
        border-radius: 1.5rem;
        margin-bottom: 2rem;
        border: 1px solid rgba(0, 31, 63, 0.1);
    }
    
    .uiverse-flex {
        display: flex;
        border: 2px solid rgba(0, 31, 63, 0.1);
        border-radius: 1rem;
        overflow: hidden;
        background: #fffcf2;
        transition: all 0.3s ease;
        align-items: stretch;
    }
    
    .uiverse-flex:focus-within {
        border-color: #d4af37;
        box-shadow: 0 0 15px rgba(212, 175, 55, 0.2);
    }

    .uiverse-icon-container {
        width: 60px;
        display: flex;
        align-items: center;
        justify-content: center;
        border-right: 1px solid rgba(0, 31, 63, 0.1);
        background: #fffcf2;
    }

    .uiverse-search-wrapper div[data-testid="stTextInput"] {
        flex: 1;
        margin: 0 !important;
    }

    .uiverse-search-wrapper div[data-testid="stTextInput"] input {
        border-radius: 0 !important;
        border: none !important;
        height: 60px !important;
        background-color: #fffcf2 !important;
        color: #001f3f !important;
        font-size: 1.1rem !important;
        font-weight: 600 !important;
        padding-left: 15px !important;
    }

    .uiverse-search-wrapper [data-testid="stBaseButton-secondary"] {
        height: 60px !important;
        border-radius: 0 !important;
        margin: 0 !important;
        background: #d4af37 !important;
        color: #001f3f !important;
        border: none !important;
        padding: 0 30px !important;
        font-weight: 800 !important;
        text-transform: uppercase !important;
        transition: all 0.3s ease !important;
    }
    
    .uiverse-search-wrapper [data-testid="stBaseButton-secondary"]:hover {
        background: #001f3f !important;
        color: #d4af37 !important;
        transform: none !important; /* Keep it flat within the search box */
    }

    /* Global Premium Input (Ensuring maximum visibility) */
    div[data-testid="stTextInput"] input {
        background-color: #FFFFFF !important;
        background: #FFFFFF !important;
        color: #001f3f !important;
        border: 1px solid rgba(0, 31, 63, 0.2) !important; /* Subtle Gray/Navy border */
        border-radius: 8px !important;
        padding: 10px 15px !important;
        font-weight: 600 !important;
        transition: all 0.3s ease-out !important;
        box-shadow: 0 1px 2px rgba(0,0,0,0.05) !important;
    }

    div[data-testid="stTextInput"] input:focus {
        border-color: #d4af37 !important; /* Highlights Gold only on Focus */
        box-shadow: 0 0 0 2px rgba(212, 175, 55, 0.2) !important;
        outline: none !important;
    }

    /* Style for labels used as top description */
    .premium-label-top {
        color: #001f3f !important;
        font-weight: 700 !important;
        font-size: 0.9rem !important;
        margin-bottom: 4px !important;
        display: block;
    }

    .premium-label-bottom {
        color: rgba(0, 31, 63, 0.6) !important;
        font-size: 0.8rem !important;
        margin-top: 4px !important;
        display: block;
    }

    /* Override Streamlit UI with CSS (Tailwind can't directly target these) */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #001f3f 0%, #00152b 100%) !important;
        border-right: 2px solid #d4af37;
    }
    
    [data-testid="stSidebar"] [data-testid="stMarkdownContainer"],
    [data-testid="stSidebar"] p, [data-testid="stSidebar"] span, [data-testid="stSidebar"] label,
    [data-testid="stSidebar"] h1, [data-testid="stSidebar"] h2, [data-testid="stSidebar"] h3 {
        color: #fffcf2 !important; /* Texto Arena en Sidebar Azul */
    }
    
    /* Custom Button Style (Adapted from Uiverse.io) */
    .stButton>button {
      --bezier: cubic-bezier(0.22, 0.61, 0.36, 1);
      --edge-light: hsla(46, 65%, 80%, 0.8);
      --text-light: rgba(255, 255, 255, 0.4);
      --back-color: 46, 65%; /* Gold base */

      cursor: pointer;
      padding: 0.7em 2em !important;
      border-radius: 0.8em !important;
      min-height: 2.8em !important;
      display: flex;
      align-items: center;
      gap: 0.5em;

      font-size: 18px !important;
      letter-spacing: 0.05em;
      line-height: 1;
      font-weight: bold !important;

      background: linear-gradient(
        140deg,
        hsla(var(--back-color), 52%, 1) 20%,
        hsla(var(--back-color), 40%, 0.6) 100%
      ) !important;
      color: #001f3f !important; /* Navy text */
      border: 0 !important;
      box-shadow: inset 0.4px 1px 4px var(--edge-light), 0 4px 15px rgba(212, 175, 55, 0.2) !important;

      transition: all 0.2s var(--bezier) !important;
    }

    .stButton>button:hover {
      --edge-light: hsla(46, 65%, 90%, 1);
      text-shadow: 0px 0px 10px var(--text-light);
      box-shadow: inset 0.4px 1px 4px var(--edge-light),
        0 8px 20px hsla(46, 65%, 10%, 0.3) !important;
      transform: scale(1.05) translateY(-2px) !important;
      background: white !important;
      color: #001f3f !important;
    }

    .stButton>button:active {
      --text-light: rgba(255, 255, 255, 1);
      background: linear-gradient(
        140deg,
        hsla(var(--back-color), 52%, 1) 20%,
        hsla(var(--back-color), 40%, 0.6) 100%
      ) !important;
      box-shadow: inset 0.4px 1px 8px var(--edge-light),
        0px 0px 8px hsla(var(--back-color), 52%, 0.6) !important;
      text-shadow: 0px 0px 20px var(--text-light);
      color: #001f3f !important;
      letter-spacing: 0.1em;
      transform: scale(0.98) !important;
    }
    
    .stSlider > div > div > div > div {
        background-color: #d4af37 !important;
    }
    
    /* Metrics */
    div[data-testid="stMetricValue"] {
        color: #d4af37 !important;
        font-weight: 800 !important;
    }
    
    /* Custom Sidebar Menu (Premium Adaptation) */
    div[data-testid="stSidebar"] div.stRadio div[role="radiogroup"] {
        display: flex !important;
        flex-direction: column !important;
        gap: 10px !important;
        background-color: #001f3f !important; /* Brand Navy */
        padding: 20px 12px !important;
        border-radius: 16px !important;
        border: 1px solid rgba(212, 175, 55, 0.2) !important;
        box-shadow: 0 12px 30px rgba(0, 0, 0, 0.6) !important;
    }
    
    div[data-testid="stSidebar"] div.stRadio label {
        display: flex !important;
        align-items: center !important;
        color: rgba(255, 252, 242, 0.75) !important; /* Muted Sand */
        gap: 12px !important;
        transition: all 0.3s cubic-bezier(0.22, 0.61, 0.36, 1) !important;
        padding: 10px 15px !important;
        border-radius: 10px !important;
        cursor: pointer !important;
        border: 1px solid transparent !important;
        margin-bottom: 0px !important;
        font-weight: 600 !important;
    }

    div[data-testid="stSidebar"] div.stRadio label:hover {
        background-color: #d4af37 !important; /* Gold */
        color: #001f3f !important; /* Navy */
        transform: translate(3px, -3px) !important;
        box-shadow: 0 10px 20px rgba(0, 0, 0, 0.4), 0 0 15px rgba(212, 175, 55, 0.4) !important;
        text-shadow: 0 1px 2px rgba(0, 0, 0, 0.2) !important;
    }
    
    div[data-testid="stSidebar"] div.stRadio label[data-selected="true"] {
        background-color: rgba(212, 175, 55, 0.15) !important;
        border: 1px solid rgba(212, 175, 55, 0.4) !important;
        color: #d4af37 !important;
        box-shadow: 0 4px 10px rgba(0,0,0,0.3) !important;
    }
    </style>
    """, unsafe_allow_html=True)

# Sidebar
st.sidebar.markdown(f"""
    <div style="text-align: center; padding-bottom: 25px;">
        <h2 style="color: #d4af37; font-weight: 800; margin-bottom: 0; text-shadow: 2px 2px 4px rgba(0,0,0,0.5);">LIDERAZGO</h2>
        <h1 style="color: #fffcf2; font-size: 2.8rem; font-weight: 900; margin-top: -10px; text-shadow: 3px 3px 6px rgba(0,0,0,0.6);">360</h1>
    </div>
""", unsafe_allow_html=True)

# Navigation Modes with Icons
mode_options = {
    "Inicio": "Inicio",
    "Nueva Evaluación": "Nueva Evaluación",
    "Panel de Resultados": "Panel de Resultados",
    "Carga Masiva (Excel)": "Carga Masiva (Excel)"
}

# Icon mapping for Bootstrap Icons
mode_icons = {
    "Inicio": "bi-house-fill",
    "Nueva Evaluación": "bi-pencil-square",
    "Panel de Resultados": "bi-bar-chart-fill",
    "Carga Masiva (Excel)": "bi-file-earmark-spreadsheet-fill"
}

# Initialize session state for navigation
if 'selected_mode' not in st.session_state:
    st.session_state.selected_mode = "Inicio"

# Create menu with styled buttons
st.sidebar.markdown("### MENÚ PRINCIPAL", unsafe_allow_html=True)

# Custom CSS for navigation buttons with icons
st.sidebar.markdown("""
<style>
/* Navigation buttons styling */
div[data-testid="stSidebar"] button[kind="secondary"] {
    width: 100% !important;
    text-align: left !important;
    padding-left: 45px !important;
    position: relative !important;
    margin-bottom: 10px !important;
}

/* Add icon before button text using ::before */
div[data-testid="stSidebar"] button[key="nav_inicio"]::before {
    font-family: 'bootstrap-icons' !important;
    content: "\\f425";
    position: absolute;
    left: 15px;
    font-size: 1.1rem;
}

div[data-testid="stSidebar"] button[key="nav_nueva"]::before {
    font-family: 'bootstrap-icons' !important;
    content: "\\f4ca";
    position: absolute;
    left: 15px;
    font-size: 1.1rem;
}

div[data-testid="stSidebar"] button[key="nav_panel"]::before {
    font-family: 'bootstrap-icons' !important;
    content: "\\f1fe";
    position: absolute;
    left: 15px;
    font-size: 1.1rem;
}

div[data-testid="stSidebar"] button[key="nav_carga"]::before {
    font-family: 'bootstrap-icons' !important;
    content: "\\f2e4";
    position: absolute;
    left: 15px;
    font-size: 1.1rem;
}
</style>
""", unsafe_allow_html=True)

# Create navigation buttons
for key, value in mode_options.items():
    button_key = f"nav_{key.lower().replace(' ', '_').replace('(', '').replace(')', '').split('_')[0]}"
    if st.sidebar.button(key, key=button_key, use_container_width=True):
        st.session_state.selected_mode = value

mode = st.session_state.selected_mode

st.sidebar.markdown("""
    <div style="padding: 20px; color: rgba(255,252,242,0.5); font-size: 0.8rem; text-align: center;">
        Modelo Kouzes & Posner • v1.0
    </div>
""", unsafe_allow_html=True)

if mode == "Inicio":
    st.markdown("""
<div class="animate-fade-in space-y-8">
    <h1 class="text-5xl font-extrabold text-navy tracking-tight mt-4">
        Liderazgo <span class="text-gold">360</span>
    </h1>
    <div class="bg-navy p-10 rounded-3xl shadow-2xl border-b-4 border-gold group hover:bg-opacity-95 hover:shadow-[0_20px_60px_rgba(212,175,55,0.3)] transition-all duration-500">
        <h2 class="text-3xl font-black text-sand mb-4 transition-all group-hover:text-gold">La Excelencia al Alcance de tu Organización</h2>
        <p class="text-sand text-xl leading-relaxed">
            Potencia el talento de tus líderes con análisis precisos basados en el modelo de 
            <b>Kouzes & Posner</b>. Una experiencia minimalista, efímera y de alto impacto.
        </p>
    </div>
    <div class="grid grid-cols-1 md:grid-cols-2 gap-8">
        <div class="bg-sand p-8 rounded-2xl shadow-lg border border-navy/10 hover:border-gold hover:-translate-y-2 hover:shadow-2xl transition-all duration-300">
            <h3 class="text-xl font-bold text-navy mb-2"><i class="bi bi-shield-fill-check text-gold" style="margin-right: 8px;"></i>Máxima Privacidad</h3>
            <p class="text-navy">Tus datos desaparecen después de 72 horas. Sin rastro, sin riesgo, total confianza.</p>
        </div>
        <div class="bg-sand p-8 rounded-2xl shadow-lg border border-navy/10 hover:border-gold hover:-translate-y-2 hover:shadow-2xl transition-all duration-300">
            <h3 class="text-xl font-bold text-navy mb-2"><i class="bi bi-lightning-charge-fill text-gold" style="margin-right: 8px;"></i>Insights Reales</h3>
            <p class="text-navy">Detección instantánea de brechas críticas y fortalezas ocultas con motor avanzado.</p>
        </div>
    </div>
</div>
""", unsafe_allow_html=True)
    
    st.divider()
    st.markdown("""
        <div class="bg-blue-50 border-l-4 border-blue-400 p-4 rounded" style="background-color: #e0f2fe; border-left: 4px solid #3b82f6;">
            <p class="text-navy" style="margin: 0; color: #001f3f;">
                <i class="bi bi-arrow-left-circle-fill" style="color: #3b82f6; margin-right: 8px;"></i>
                Selecciona <strong>'Nueva Evaluación'</strong> en el menú lateral para registrar tu primer líder.
            </p>
        </div>
    """, unsafe_allow_html=True)

elif mode == "Nueva Evaluación":
    st.markdown("<h1 class='text-4xl font-extrabold text-navy mb-6'><i class='bi bi-pencil-square' style='margin-right: 12px;'></i>Gestión de Evaluaciones</h1>", unsafe_allow_html=True)
    
    # Step 1: Company Identification (Fixed Clean Implementation)
    st.markdown('<label class="premium-label-top">ID DE SESIÓN (Empresa)</label>', unsafe_allow_html=True)
    company_name = st.text_input("ID DE SESIÓN", label_visibility="collapsed", placeholder="Ej: Mi Empresa Corp", key="comp_final_v5")
    st.markdown('<label class="premium-label-bottom">Los datos se borrarán automáticamente en 72h.</label>', unsafe_allow_html=True)
    st.write("") # Spacer
    
    if company_name:
        # Check or create company
        comp = db.get_company_by_name(company_name)
        if not comp:
            if st.button(f"Crear sesión para '{company_name}'"):
                db.create_company(company_name)
                st.success(f"Sesión creada para {company_name}. ¡Comience a evaluar!")
                st.rerun()
        else:
            st.info(f"Sesión activa detectada para: **{company_name}**")
            
            # Step 2: Leader & Role
            col1, col2 = st.columns(2)
            leader_name = col1.text_input("Nombre del Líder a Evaluar")
            role = col2.radio("Su Rol", ["Autoevaluación (Líder)", "Observador (Equipo/Par/Jefe)"])
            
            st.divider()
            
            # Step 3: Questionnaire
            st.subheader("Cuestionario de 30 Preguntas")
            st.caption("Califique de 1 (Casi nunca) a 5 (Casi siempre)")
            
            questions_self = [
                "1. Busca oportunidades retadoras que prueban sus aptitudes y habilidades.",
                "2. Describe el tipo de futuro que le gustaría crear en conjunto con las personas que laboran con usted.",
                "3. Involucra a los demás en planear las acciones que se llevarán a cabo.",
                "4. Tiene clara su propia filosofía de liderazgo.",
                "5. Se toma tiempo para celebrar los logros cuando se alcanzan en un proyecto importante.",
                "6. Está al día con los más recientes descubrimientos que afectan nuestra organización.",
                "7. Se acerca a los demás para compartir con ellos su sueño del futuro.",
                "8. Trata a los demás con dignidad y respeto.",
                "9. Se asegura que los proyectos que usted dirige se dividan en etapas manejables.",
                "10. Se asegura que la gente sea reconocida por sus contribuciones al éxito de los proyectos.",
                "11. Cuestiona la forma rutinaria en que se realiza el trabajo.",
                "12. Claramente comunica su idea positiva y llena de esperanza del futuro de su organización.",
                "13. Le da a la gente margen de acción para tomar sus propias decisiones.",
                "14. Gasta tiempo y energía en asegurarse que la gente sea congruente con los valores que se han acordado.",
                "15. Felicita a la gente por un trabajo bien realizado.",
                "16. Busca formas innovadoras para que todos puedan mejorar en beneficio de la organización.",
                "17. Les demuestra a los demás cómo sus intereses a largo plazo pueden ser alcanzados al unirse en una visión común de empresa.",
                "18. Reconoce relaciones de cooperación con la gente que trabaja.",
                "19. Fomenta que los demás conozcan sus ideas sobre cómo manejar mejor la organización en la que está al frente.",
                "20. Les da a los miembros del equipo mucho aprecio y apoyo por sus contribuciones.",
                "21. Pregunta, ¿qué podemos aprender?, cuando las cosas no caminan como se esperaba.",
                "22. Ve siempre adelante y anticipa lo que espera que suceda en el futuro.",
                "23. Crea una atmósfera de mutua confianza en los proyectos que dirige.",
                "24. Es consistente en practicar los valores que predica.",
                "25. Encuentra formas para celebrar los logros.",
                "26. Experimenta y toma riesgos en nuevas formas para realizar su trabajo aún cuando exista posibilidad de fracasar.",
                "27. Es entusiasta y contagia su confianza acerca de las posibilidades a futuro.",
                "28. Involucra a los demás para hacerlos sentir copropietarios-dueños de los proyectos en los que trabajan.",
                "29. Se asegura que el grupo establezca objetivos claros, haga planes y defina acciones para los proyectos en los que trabaja.",
                "30. Defiende con énfasis ante el resto de la organización cuando su equipo hace un buen trabajo."
            ]

            questions_observer = [
                "1. Busca oportunidades retadoras que prueban sus aptitudes y habilidades.",
                "2. Describe el tipo de futuro que le gustaría crear en conjunto con las personas que laboran con él o ella.",
                "3. Involucra a los demás en planear las acciones que se llevarán a cabo.",
                "4. Tiene clara su propia filosofía de liderazgo.",
                "5. Se toma tiempo para celebrar los logros cuando se alcanzan en un proyecto importante.",
                "6. Está al día con los más recientes descubrimientos que afectan nuestra organización.",
                "7. Se acerca a los demás para compartir con ellos su sueño del futuro como propio.",
                "8. Trata a los demás con dignidad y respeto.",
                "9. Se asegura que los proyectos que él o ella dirige se dividan en etapas manejables.",
                "10. Se asegura que la gente sea reconocida por sus contribuciones al éxito de los proyectos.",
                "11. Cuestiona la forma rutinaria en que se realiza el trabajo.",
                "12. Claramente comunica su idea positiva y llena de esperanza del futuro de su organización.",
                "13. Le da a la gente margen de acción para tomar sus propias decisiones.",
                "14. Gasta tiempo y energía en asegurarse que la gente sea congruente con los valores que se han acordado.",
                "15. Felicita a la gente por un trabajo bien realizado.",
                "16. Busca formas innovadoras para que todos puedan mejorar en beneficio de la organización.",
                "17. Les demuestra a los demás cómo sus intereses a largo plazo pueden ser alcanzados al unirse en una visión común de empresa.",
                "18. Reconoce relaciones de cooperación con la gente que trabaja.",
                "19. Fomenta que los demás conozcan sus ideas sobre cómo manejar mejor la organización en la que está al frente.",
                "20. Les da a los miembros del equipo mucho aprecio y apoyo por sus contribuciones.",
                "21. Pregunta, ¿qué podemos aprender?, cuando las cosas no caminan como se esperaba.",
                "22. Ve siempre adelante y anticipa lo que espera que suceda en el futuro.",
                "23. Crea una atmósfera de mutua confianza en los proyectos que dirige.",
                "24. Es consistente en practicar los valores que predica.",
                "25. Encuentra formas para celebrar los logros.",
                "26. Experimenta y toma riesgos en nuevas formas para realizar su trabajo aún cuando exista posibilidad de fracasar.",
                "27. Es entusiasta y contagia su confianza acerca de las posibilidades a futuro.",
                "28. Involucra a los demás para hacerlos sentir copropietarios-dueños de los proyectos en los que trabajan.",
                "29. Se asegura que el grupo establezca objetivos claros, haga planes y defina acciones para los proyectos en los que trabaja.",
                "30. Defiende con énfasis ante el resto de la organización cuando su equipo hace un buen trabajo."
            ]

            active_questions = questions_self if "Autoevaluación" in role else questions_observer
            
            scores = []
            with st.form("evaluation_form"):
                for i, q_text in enumerate(active_questions):
                    scores.append(st.slider(q_text, 1, 5, 3, key=f"q{i+1}"))
                
                submitted = st.form_submit_button("Enviar Evaluación")
                if submitted:
                    if not leader_name:
                        st.error("Por favor ingrese el nombre del líder.")
                    else:
                        # Save to DB
                        comp_id = comp[0]
                        db.add_evaluation(comp_id, leader_name, role, scores)
                        st.success("¡Evaluación guardada exitosamente!")

elif mode == "Panel de Resultados":
    st.markdown("<h1 class='text-4xl font-extrabold text-navy mb-6'><i class='bi bi-bar-chart-fill' style='margin-right: 12px;'></i>Panel de Resultados</h1>", unsafe_allow_html=True)
    
    with st.container():
        companies = db.get_all_companies()
        
        if not companies:
            st.info("No hay evaluaciones registradas actualmente.")
        else:
            st.markdown('<label class="premium-label-top">CONSULTAR SESIÓN ACTIVA:</label>', unsafe_allow_html=True)
            # Add custom styling for white background, navy text and arrow on selectbox
            st.markdown("""
                <style>
                /* Selectbox container */
                div[data-baseweb="select"] {
                    background-color: #FFFFFF !important;
                }
                /* Selectbox main div and text */
                div[data-baseweb="select"] > div {
                    background-color: #FFFFFF !important;
                    color: #001f3f !important;
                }
                /* Text inside selectbox */
                div[data-baseweb="select"] span {
                    color: #001f3f !important;
                }
                /* Arrow icon */
                div[data-baseweb="select"] svg {
                    fill: #001f3f !important;
                    color: #001f3f !important;
                }
                /* Dropdown menu - multiple selectors for complete coverage */
                div[role="listbox"],
                ul[role="listbox"],
                div[data-baseweb="popover"] > div,
                div[data-baseweb="menu"] {
                    background-color: #FFFFFF !important;
                }
                /* Dropdown menu items */
                div[role="option"],
                li[role="option"] {
                    background-color: #FFFFFF !important;
                    color: #001f3f !important;
                }
                /* Dropdown menu items on hover */
                div[role="option"]:hover,
                li[role="option"]:hover {
                    background-color: #f0f0f0 !important;
                }
                </style>
            """, unsafe_allow_html=True)
            company_query = st.selectbox("Seleccione Empresa", ["Seleccione..."] + companies, label_visibility="collapsed")
            
            if company_query and company_query != "Seleccione...":
                comp = db.get_company_by_name(company_query)
                if comp:
                    st.markdown(f"""
                        <div class='bg-navy text-sand p-6 rounded-2xl shadow-lg border-b-4 border-gold mb-8'>
                            <h3 class='text-xl font-bold'>Resultados Estratégicos: <span class='text-gold'>{company_query}</span></h3>
                        </div>
                    """, unsafe_allow_html=True)
                    
                    data = db.get_evaluations_by_company(comp[0])
                    
                    if data:
                        df = pd.DataFrame(data)
                        
                        # Metrics Row
                        m1, m2, m3 = st.columns(3)
                        with m1:
                            st.metric("Total de Muestras", len(df))
                        with m2:
                            st.metric("Líderes Evaluados", len(df['leader_name'].unique()))
                        with m3:
                            st.metric("Horas Restantes", "72h") # Fixed representation
                        
                        # Calculate Scores
                        results = logic.calculate_scores(df)
                        
                        # List Leaders
                        leaders = list(results.keys())
                        st.markdown("<p class='text-navy font-bold mt-4'>Seleccione un Líder:</p>", unsafe_allow_html=True)
                        selected_leader = st.selectbox("", leaders, label_visibility="collapsed")
                        
                        if selected_leader:
                            stats = results[selected_leader]
                            
                            st.markdown(f"""
                                <div class='mt-8 mb-4'>
                                    <h2 class='text-3xl font-black text-navy border-b-2 border-gold pb-2 inline-block'>
                                        Dashboard: {selected_leader}
                                    </h2>
                                </div>
                            """, unsafe_allow_html=True)
                            
                            # Charts
                            col1, col2 = st.columns([1, 1])
                            
                            with col1:
                                categories = list(stats.keys())
                                self_values = [stats[c]["Self"] for c in categories]
                                obs_values = [stats[c]["Observers"] for c in categories]
                                
                                import plotly.graph_objects as go
                                fig = go.Figure()
                                fig.add_trace(go.Scatterpolar(
                                    r=self_values, theta=categories, fill='toself', 
                                    name='Autoevaluación', line=dict(color='#d4af37', width=4)
                                ))
                                fig.add_trace(go.Scatterpolar(
                                    r=obs_values, theta=categories, fill='toself', 
                                    name='Promedio Observadores', line=dict(color='#001f3f', width=4)
                                ))
                                fig.update_layout(
                                    polar=dict(
                                        radialaxis=dict(
                                            visible=True, 
                                            range=[0, 5],
                                            tickfont=dict(color='#001f3f')
                                        ),
                                        angularaxis=dict(
                                            tickfont=dict(color='#001f3f')
                                        ),
                                        bgcolor='white'
                                    ),
                                    showlegend=True,
                                    legend=dict(
                                        font=dict(color='#001f3f'),
                                        bgcolor='rgba(255,255,255,0.8)'
                                    ),
                                    paper_bgcolor='white',
                                    plot_bgcolor='white',
                                    font=dict(color='#001f3f'),
                                    margin=dict(t=30, b=30, l=40, r=40)
                                )
                                st.plotly_chart(fig, use_container_width=True)
                            
                            with col2:
                                gaps = [stats[c]["Gap"] for c in categories]
                                colors = ['#d4af37' if g >= 0 else '#001f3f' for g in gaps]
                                fig_bar = go.Figure(data=[go.Bar(x=categories, y=gaps, marker_color=colors)])
                                fig_bar.update_layout(
                                    title=dict(
                                        text="Análisis de Brecha (Obs - Auto)",
                                        font=dict(color='#001f3f')
                                    ),
                                    paper_bgcolor='white',
                                    plot_bgcolor='white',
                                    xaxis=dict(tickfont=dict(color='#001f3f')),
                                    yaxis=dict(tickfont=dict(color='#001f3f')),
                                    font=dict(color='#001f3f'),
                                    margin=dict(t=50)
                                )
                                st.plotly_chart(fig_bar, use_container_width=True)
                            
                            # Insights with Tailwind
                            st.markdown("<h3 class='text-2xl font-bold text-navy mt-8 mb-4'><i class='bi bi-lightbulb-fill' style='margin-right: 8px;'></i>Recomendaciones Directivas</h3>", unsafe_allow_html=True)
                            insights = logic.generate_insights(stats)
                            for insight in insights:
                                st.markdown(f"""
                                    <div class='bg-sand p-5 rounded-xl shadow-sm border border-navy/20 mb-4 hover:shadow-md transition-shadow text-navy'>
                                        {insight}
                                    </div>
                                """, unsafe_allow_html=True)
                                
                            # Download
                            st.divider()
                            
                            # Style for download button with white background
                            st.markdown("""
                                <style>
                                /* Download button styling */
                                div[data-testid="stDownloadButton"] button {
                                    background-color: #FFFFFF !important;
                                    color: #001f3f !important;
                                    border: 2px solid #001f3f !important;
                                    font-weight: 700 !important;
                                }
                                div[data-testid="stDownloadButton"] button:hover {
                                    background-color: #001f3f !important;
                                    color: #FFFFFF !important;
                                }
                                </style>
                            """, unsafe_allow_html=True)
                            
                            import reports
                            pdf_bytes = reports.generate_pdf_report(selected_leader, company_query, stats)
                            st.download_button(
                                label="⬇️ Descargar Reporte PDF Ejecutivo",
                                data=pdf_bytes,
                                file_name=f"Reporte_Liderazgo_{selected_leader}.pdf",
                                mime='application/pdf'
                            )
                    else:
                        st.warning("No hay evaluaciones registradas aún para esta empresa.")
                else:
                    st.error("No se encontró la sesión de la empresa. Verifique el nombre.")

elif mode == "Carga Masiva (Excel)":
    st.markdown("<h1 class='text-4xl font-extrabold text-navy mb-6'><i class='bi bi-file-earmark-spreadsheet-fill' style='margin-right: 12px;'></i>Importador de Excel Inteligente</h1>", unsafe_allow_html=True)
    st.markdown("Suba un archivo `.xlsx` o `.csv` con las columnas: `Lider`, `Rol`, `P1`...`P30`.")
    
    # Style for file uploader with white background
    st.markdown("""
        <style>
        /* File uploader container */
        div[data-testid="stFileUploader"] {
            background-color: #FFFFFF !important;
            border: 2px solid rgba(0, 31, 63, 0.2) !important;
            border-radius: 8px !important;
            padding: 10px !important;
        }
        /* File uploader section */
        div[data-testid="stFileUploader"] > section {
            background-color: #FFFFFF !important;
            border: 1px dashed rgba(0, 31, 63, 0.3) !important;
        }
        /* Browse files button */
        div[data-testid="stFileUploader"] button {
            background-color: #FFFFFF !important;
            color: #001f3f !important;
            border: 2px solid #001f3f !important;
            font-weight: 700 !important;
        }
        div[data-testid="stFileUploader"] button:hover {
            background-color: #001f3f !important;
            color: #FFFFFF !important;
        }
        /* File uploader text */
        div[data-testid="stFileUploader"] label,
        div[data-testid="stFileUploader"] span,
        div[data-testid="stFileUploader"] p {
            color: #001f3f !important;
        }
        </style>
    """, unsafe_allow_html=True)
    
    company_upload = st.text_input("Asignar a Empresa:")
    uploaded_file = st.file_uploader("Seleccionar archivo", type=['xlsx', 'csv'])
    
    if uploaded_file and company_upload:
        if st.button("Procesar Archivo"):
             # Get or create company
            comp = db.get_company_by_name(company_upload)
            if not comp:
                 comp_id = db.create_company(company_upload)
                 st.success(f"Nueva sesión creada: {company_upload}")
            else:
                 comp_id = comp[0]
            
            from utils import process_excel_upload
            count, msg = process_excel_upload(uploaded_file, comp_id)
            
            if count > 0:
                st.success(f"Se importaron {count} evaluaciones correctamente.")
            else:
                st.error(f"Error en la importación: {msg}")
