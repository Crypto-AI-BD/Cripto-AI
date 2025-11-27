"""
Configurações gerais do projeto Big Data - Análise de Criptomoedas
"""
import os
from pathlib import Path

# Diretórios do Projeto
BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
RAW_DATA_DIR = DATA_DIR / "raw"
PROCESSED_DATA_DIR = DATA_DIR / "processed"
MODELS_DIR = BASE_DIR / "models"
VISUALIZATIONS_DIR = BASE_DIR / "visualizations"

# Criar diretórios se não existirem
for directory in [RAW_DATA_DIR, PROCESSED_DATA_DIR, MODELS_DIR, VISUALIZATIONS_DIR]:
    directory.mkdir(parents=True, exist_ok=True)

# Configurações do Spark
SPARK_CONFIG = {
    "app_name": "CryptoAnalysis_BigData",
    "master": "local[*]",  # Para execução local; no Databricks use o cluster
    "memory": "4g",
    "cores": "4",
}

# Configurações Delta Lake
DELTA_LAKE_CONFIG = {
    "enabled": True,
    "warehouse_path": str(PROCESSED_DATA_DIR / "delta_warehouse"),
}

# Configurações de Dados
DATA_CONFIG = {
    "crypto_symbols": ["BTC-USD", "ETH-USD"],
    "default_symbol": "BTC-USD",
    "period": "5y",  # 5 anos de dados históricos
    "interval": "1d",  # Dados diários
}

# Configurações de Modelagem
MODEL_CONFIG = {
    "prophet": {
        "changepoint_prior_scale": 0.05,
        "seasonality_mode": "multiplicative",
        "forecast_days": 30,
    },
    "sklearn": {
        "test_size": 0.2,
        "random_state": 42,
    },
    "moving_averages": [7, 30, 90, 200],  # Dias para médias móveis
}

# Configurações de Visualização
VIZ_CONFIG = {
    "theme": "plotly_dark",
    "default_width": 1200,
    "default_height": 600,
    "colors": {
        "primary": "#1f77b4",
        "secondary": "#ff7f0e",
        "success": "#2ca02c",
        "danger": "#d62728",
    },
}

# Configurações da API Yahoo Finance
YFINANCE_CONFIG = {
    "max_retries": 3,
    "timeout": 30,
    "proxy": None,
}

# Configurações do Streamlit
STREAMLIT_CONFIG = {
    "page_title": "Análise de Criptomoedas - Big Data",
    "page_icon": "₿",
    "layout": "wide",
    "initial_sidebar_state": "expanded",
}

# Configurações do Desktop App
DESKTOP_CONFIG = {
    "window_title": "Big Data - Análise de Criptomoedas",
    "window_width": 1400,
    "window_height": 900,
    "theme": "dark",
}

# Configurações de Logging
LOGGING_CONFIG = {
    "level": "INFO",
    "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    "log_file": str(BASE_DIR / "logs" / "app.log"),
}

# Criar diretório de logs
log_dir = BASE_DIR / "logs"
log_dir.mkdir(exist_ok=True)
