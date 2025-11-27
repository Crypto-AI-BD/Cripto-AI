# 📊 Crypto Analytics Platform

Sistema profissional de análise de criptomoedas com processamento Big Data, Machine Learning e visualizações interativas.

---

## 🚀 Quick Start

### Instalação
```powershell
# 1. Criar ambiente virtual
python -m venv venv
.\venv\Scripts\Activate.ps1

# 2. Instalar dependências
pip install -r requirements.txt

# 3. Executar dashboard
streamlit run app.py
```

Acesse: **http://localhost:8501**

---

## 🎯 Funcionalidades

### 📈 Análise de Dados
- Processamento Big Data com Apache Spark
- Médias móveis (7d, 30d, 90d, 200d)
- Indicadores técnicos (RSI, MACD, Volatilidade)

### 🤖 Machine Learning
- **Prophet AI**: Previsão time-series
- **Random Forest**: Ensemble learning
- **Gradient Boosting**: Regressão avançada

### 📊 Visualizações
- Gráficos interativos Plotly
- Candlestick charts
- Dashboard profissional

### 🌐 Fontes de Dados
- Yahoo Finance API
- Upload CSV

---

## 💻 Tecnologias

- **Apache Spark 3.5.0** - Big Data processing
- **Prophet 1.1.5** - Time series forecasting
- **Scikit-learn 1.3.2** - Machine Learning
- **Streamlit 1.29.0** - Web dashboard
- **Plotly 5.18.0** - Interactive visualizations
- **PyQt5 5.15.10** - Desktop application

---

## 📁 Estrutura

```
bigdata-2/
├── app.py                 # Dashboard web
├── modern_theme.py        # Tema visual
├── requirements.txt       # Dependências
├── config/               # Configurações
├── src/                  # Código principal
│   ├── data_ingestion.py
│   ├── spark_processor.py
│   └── utils.py
├── models/               # ML Models
│   ├── prophet_model.py
│   └── sklearn_model.py
├── visualizations/       # Gráficos
├── desktop_app/          # App desktop
├── notebooks/            # Jupyter notebooks
└── data/                 # Dados
```

---

## 🚀 Como Usar

### Dashboard Web
```powershell
streamlit run app.py
```

### Desktop App
```powershell
python desktop_app/main.py
```

### Notebooks
```powershell
jupyter notebook notebooks/
```

---

## 📊 Workflow

1. **Selecionar Fonte**: Yahoo Finance ou CSV
2. **Escolher Cripto**: BTC, ETH, ADA, SOL, BNB, XRP
3. **Definir Período**: 1-10 anos ou máximo
4. **Carregar Dados**: Click "Load Data"
5. **Analisar**: Navegue pelas tabs
   - Overview
   - Technical Analysis
   - ML Predictions
   - Visualizations

---

## 🤖 Machine Learning

### Prophet
- Detecção de sazonalidade
- Previsões 30-90 dias
- Intervalos de confiança

### Scikit-learn
- Linear/Ridge/Lasso Regression
- Random Forest
- Gradient Boosting
- Features: lags, MAs, volatilidade

---

## ⚙️ Configuração

### Spark (opcional)
- Instalar Java 8 ou 11
- Sistema usa Pandas como fallback

### Prophet (Windows)
```powershell
pip install pystan==2.19.1.1
pip install prophet==1.1.5
```

---

## 🐛 Troubleshooting

**Porta em uso:**
```powershell
streamlit run app.py --server.port=8502
```

**Spark não disponível:**
- Sistema funciona sem Spark (usa Pandas)

---

## 📦 Dependências

```
apache-spark==3.5.0
pyspark==3.5.0
prophet==1.1.5
scikit-learn==1.3.2
streamlit==1.29.0
plotly==5.18.0
PyQt5==5.15.10
yfinance==0.2.32
pandas>=2.0.0
numpy>=1.24.0
```

---

## 🎓 Projeto Acadêmico

### Requisitos Atendidos
✅ Big Data (Apache Spark)  
✅ Machine Learning (Prophet + scikit-learn)  
✅ Visualizações (Plotly)  
✅ Interface profissional  
✅ Documentação completa  

---

<div align="center">

**📊 Crypto Analytics Platform**

*Big Data • Machine Learning • Real-Time Analysis*

</div>
