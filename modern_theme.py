"""
Tema Profissional Moderno
Configurações de estilo equilibradas
"""

# Cores Modernas e Profissionais
COLORS = {
    'primary_blue': '#0066FF',
    'accent_cyan': '#00B4D8',
    'success_green': '#06D6A0',
    'warning_orange': '#FF6B35',
    'danger_red': '#EF476F',
    'purple': '#7209B7',
    'dark_bg': '#1a1d29',
    'darker_bg': '#13151f',
    'card_bg': '#23262f',
    'text_primary': '#E8E9EB',
    'text_secondary': '#A0A3AB',
}

# CSS Moderno e Profissional
MODERN_CSS = """
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=Poppins:wght@400;600;700&display=swap');
    
    :root {
        --primary-blue: #0066FF;
        --accent-cyan: #00B4D8;
        --success-green: #06D6A0;
        --warning-orange: #FF6B35;
        --purple: #7209B7;
        --dark-bg: #1a1d29;
        --darker-bg: #13151f;
        --card-bg: #23262f;
        --text-primary: #E8E9EB;
        --text-secondary: #A0A3AB;
    }
    
    /* Background Moderno */
    .stApp {
        background: linear-gradient(135deg, #13151f 0%, #1a1d29 50%, #13151f 100%);
        font-family: 'Inter', sans-serif;
    }
    
    /* Headers Profissionais */
    h1, h2, h3 {
        font-family: 'Poppins', sans-serif !important;
        font-weight: 600;
        color: var(--text-primary) !important;
        letter-spacing: -0.5px;
    }
    
    h1 {
        background: linear-gradient(120deg, #0066FF, #00B4D8);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-size: 2.5em !important;
    }
    
    /* Botões Modernos */
    .stButton>button {
        background: linear-gradient(135deg, #0066FF, #00B4D8) !important;
        border: none !important;
        color: white !important;
        font-family: 'Inter', sans-serif !important;
        font-weight: 600 !important;
        padding: 0.6rem 1.5rem !important;
        border-radius: 8px !important;
        box-shadow: 0 4px 12px rgba(0, 102, 255, 0.3) !important;
        transition: all 0.3s ease !important;
        text-transform: none !important;
    }
    
    .stButton>button:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 20px rgba(0, 102, 255, 0.4) !important;
    }
    
    /* Inputs e Selectbox */
    div[data-baseweb="select"] > div,
    .stTextInput > div > div > input {
        background-color: var(--card-bg) !important;
        border: 1px solid rgba(0, 102, 255, 0.3) !important;
        border-radius: 8px !important;
        color: var(--text-primary) !important;
        font-family: 'Inter', sans-serif !important;
    }
    
    div[data-baseweb="select"] > div:hover,
    .stTextInput > div > div > input:hover {
        border-color: var(--primary-blue) !important;
    }
    
    /* Métricas */
    .stMetric {
        background: var(--card-bg) !important;
        border: 1px solid rgba(0, 102, 255, 0.2) !important;
        border-radius: 12px !important;
        padding: 1.2rem !important;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.2) !important;
    }
    
    .stMetric label {
        font-family: 'Inter', sans-serif !important;
        color: var(--text-secondary) !important;
        font-weight: 500 !important;
        font-size: 0.9em !important;
    }
    
    .stMetric [data-testid="stMetricValue"] {
        font-family: 'Poppins', sans-serif !important;
        font-size: 2em !important;
        font-weight: 600 !important;
        color: var(--primary-blue) !important;
    }
    
    /* Sidebar */
    section[data-testid="stSidebar"] {
        background: linear-gradient(180deg, #13151f 0%, #1a1d29 100%) !important;
        border-right: 1px solid rgba(0, 102, 255, 0.2) !important;
    }
    
    section[data-testid="stSidebar"] > div {
        background: transparent !important;
    }
    
    /* Tabs Modernas */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
        background-color: transparent !important;
    }
    
    .stTabs [data-baseweb="tab"] {
        background: var(--card-bg) !important;
        border: 1px solid rgba(0, 102, 255, 0.2) !important;
        border-radius: 8px !important;
        color: var(--text-secondary) !important;
        font-family: 'Inter', sans-serif !important;
        font-weight: 500 !important;
        padding: 0.6rem 1.2rem !important;
        transition: all 0.3s ease !important;
    }
    
    .stTabs [data-baseweb="tab"]:hover {
        border-color: var(--primary-blue) !important;
        color: var(--text-primary) !important;
    }
    
    .stTabs [aria-selected="true"] {
        background: linear-gradient(135deg, #0066FF, #00B4D8) !important;
        border-color: transparent !important;
        color: white !important;
        box-shadow: 0 2px 8px rgba(0, 102, 255, 0.3) !important;
    }
    
    /* Upload de arquivo */
    .uploadedFile {
        border: 2px dashed rgba(0, 102, 255, 0.3) !important;
        background: var(--card-bg) !important;
        border-radius: 8px !important;
    }
    
    /* DataFrame */
    .stDataFrame {
        border: 1px solid rgba(0, 102, 255, 0.2) !important;
        border-radius: 8px !important;
        overflow: hidden !important;
    }
    
    /* Alertas */
    .stAlert {
        border-left: 4px solid var(--primary-blue) !important;
        background: var(--card-bg) !important;
        border-radius: 8px !important;
        font-family: 'Inter', sans-serif !important;
    }
    
    /* Expander */
    .streamlit-expanderHeader {
        font-family: 'Inter', sans-serif !important;
        font-weight: 500 !important;
        color: var(--text-primary) !important;
        background: var(--card-bg) !important;
        border: 1px solid rgba(0, 102, 255, 0.2) !important;
        border-radius: 8px !important;
    }
    
    /* Progress bar */
    .stProgress > div > div {
        background: linear-gradient(90deg, #0066FF, #00B4D8) !important;
    }
    
    /* Radio buttons */
    .stRadio > label {
        font-family: 'Inter', sans-serif !important;
        color: var(--text-primary) !important;
        font-weight: 500 !important;
    }
    
    /* Markdown */
    .stMarkdown {
        font-family: 'Inter', sans-serif !important;
        color: var(--text-primary) !important;
    }
    
    /* Scrollbar */
    ::-webkit-scrollbar {
        width: 8px;
        height: 8px;
    }
    
    ::-webkit-scrollbar-track {
        background: var(--darker-bg);
    }
    
    ::-webkit-scrollbar-thumb {
        background: var(--primary-blue);
        border-radius: 4px;
    }
    
    ::-webkit-scrollbar-thumb:hover {
        background: var(--accent-cyan);
    }
</style>
"""

# Configuração Plotly Moderna
PLOTLY_LAYOUT = {
    'template': 'plotly_dark',
    'plot_bgcolor': 'rgba(26, 29, 41, 0.8)',
    'paper_bgcolor': 'rgba(19, 21, 31, 0.9)',
    'font': {
        'family': 'Inter, sans-serif',
        'color': '#E8E9EB',
        'size': 12
    },
    'title': {
        'font': {
            'family': 'Poppins, sans-serif',
            'size': 18,
            'color': '#0066FF'
        }
    },
    'xaxis': {
        'gridcolor': 'rgba(0, 102, 255, 0.1)',
        'linecolor': 'rgba(0, 102, 255, 0.3)',
        'color': '#E8E9EB',
    },
    'yaxis': {
        'gridcolor': 'rgba(0, 180, 216, 0.1)',
        'linecolor': 'rgba(0, 180, 216, 0.3)',
        'color': '#E8E9EB',
    },
    'legend': {
        'bgcolor': 'rgba(35, 38, 47, 0.8)',
        'bordercolor': 'rgba(0, 102, 255, 0.3)',
        'borderwidth': 1,
        'font': {
            'family': 'Inter',
            'color': '#E8E9EB',
            'size': 11
        }
    }
}

# Cores para traces
TRACE_COLORS = {
    'price': '#0066FF',
    'volume': '#00B4D8',
    'ma_short': '#06D6A0',
    'ma_medium': '#7209B7',
    'ma_long': '#FF6B35',
    'prediction': '#EF476F',
    'upper_band': '#00B4D8',
    'lower_band': '#00B4D8'
}
