"""
Aplicação Desktop para Análise de Criptomoedas
Interface gráfica com PyQt5
"""
import sys
import os
from pathlib import Path

# Adicionar diretório raiz ao path
sys.path.insert(0, str(Path(__file__).parent.parent))

from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QLabel, QFileDialog, QComboBox, QTabWidget,
    QTextEdit, QMessageBox, QProgressBar, QGroupBox, QTableWidget,
    QTableWidgetItem, QHeaderView
)
from PyQt5.QtCore import Qt, QThread, pyqtSignal
from PyQt5.QtGui import QFont, QIcon
import pandas as pd
import logging

# Importar módulos do projeto
from src.data_ingestion import CryptoDataIngestion
from src.spark_processor import SparkDataProcessor
from models.prophet_model import CryptoProphetModel, PROPHET_AVAILABLE
from models.sklearn_model import CryptoMLModel, SKLEARN_AVAILABLE
from visualizations.plotly_charts import CryptoVisualizer, PLOTLY_AVAILABLE

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class AnalysisWorker(QThread):
    """Worker thread para executar análises sem bloquear a UI"""
    finished = pyqtSignal(dict)
    error = pyqtSignal(str)
    progress = pyqtSignal(str)
    
    def __init__(self, df, analysis_type):
        super().__init__()
        self.df = df
        self.analysis_type = analysis_type
    
    def run(self):
        try:
            results = {}
            
            if self.analysis_type == "process":
                self.progress.emit("Processando dados com Spark...")
                processor = SparkDataProcessor()
                
                # Calcular médias móveis
                df_with_ma = processor.calculate_moving_averages(self.df)
                
                # Calcular indicadores técnicos
                df_processed = processor.calculate_technical_indicators(df_with_ma)
                
                # Salvar dados processados
                output_path = Path("data/processed/processed_data.csv")
                df_processed.to_csv(output_path, index=False)
                
                processor.stop()
                
                results['df'] = df_processed
                results['message'] = f"Dados processados salvos em: {output_path}"
            
            elif self.analysis_type == "prophet" and PROPHET_AVAILABLE:
                self.progress.emit("Treinando modelo Prophet...")
                
                prophet_model = CryptoProphetModel()
                df_prophet = prophet_model.prepare_data(self.df)
                
                # Dividir dados
                split_idx = int(len(df_prophet) * 0.8)
                df_train = df_prophet[:split_idx]
                
                # Treinar
                prophet_model.train(df_train)
                
                # Prever
                forecast = prophet_model.predict(periods=30)
                
                # Salvar modelo
                model_path = Path("models/prophet_model.pkl")
                prophet_model.save_model(str(model_path))
                
                results['forecast'] = prophet_model.get_forecast_summary(30)
                results['trend'] = prophet_model.get_trend_analysis()
                results['message'] = "Previsão Prophet concluída"
            
            elif self.analysis_type == "sklearn" and SKLEARN_AVAILABLE:
                self.progress.emit("Treinando modelo scikit-learn...")
                
                ml_model = CryptoMLModel(model_type='linear_regression')
                
                # Preparar features
                X, y = ml_model.prepare_features(self.df)
                
                # Dividir dados
                split_idx = int(len(X) * 0.8)
                X_train, X_test = X[:split_idx], X[split_idx:]
                y_train, y_test = y[:split_idx], y[split_idx:]
                
                # Treinar
                ml_model.train(X_train, y_train)
                
                # Avaliar
                metrics = ml_model.evaluate(X_test, y_test)
                
                # Prever próximos dias
                forecast = ml_model.predict_next_days(self.df, days=7)
                
                # Salvar modelo
                model_path = Path("models/sklearn_model.pkl")
                ml_model.save_model(str(model_path))
                
                results['forecast'] = forecast
                results['metrics'] = metrics
                results['message'] = "Modelo scikit-learn treinado"
            
            self.finished.emit(results)
        
        except Exception as e:
            logger.error(f"Erro na análise: {str(e)}")
            self.error.emit(str(e))


class CryptoAnalysisApp(QMainWindow):
    """Aplicação principal"""
    
    def __init__(self):
        super().__init__()
        self.df = None
        self.df_processed = None
        self.init_ui()
    
    def init_ui(self):
        """Inicializa a interface"""
        self.setWindowTitle("Big Data - Análise de Criptomoedas")
        self.setGeometry(100, 100, 1400, 900)
        
        # Widget central
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Layout principal
        main_layout = QVBoxLayout()
        central_widget.setLayout(main_layout)
        
        # Título
        title = QLabel("📊 Análise de Criptomoedas - Big Data")
        title_font = QFont()
        title_font.setPointSize(18)
        title_font.setBold(True)
        title.setFont(title_font)
        title.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(title)
        
        # Tabs
        tabs = QTabWidget()
        main_layout.addWidget(tabs)
        
        # Abas
        tabs.addTab(self.create_data_tab(), "📁 Dados")
        tabs.addTab(self.create_analysis_tab(), "📈 Análise")
        tabs.addTab(self.create_ml_tab(), "🤖 Machine Learning")
        tabs.addTab(self.create_viz_tab(), "📊 Visualizações")
        
        # Barra de status
        self.statusBar().showMessage("Pronto")
        
        # Aplicar estilo
        self.apply_style()
    
    def create_data_tab(self):
        """Cria aba de dados"""
        widget = QWidget()
        layout = QVBoxLayout()
        
        # Grupo: Carregar Dados
        load_group = QGroupBox("Carregar Dados")
        load_layout = QVBoxLayout()
        
        # Botão: Buscar do Yahoo Finance
        yahoo_layout = QHBoxLayout()
        self.symbol_combo = QComboBox()
        self.symbol_combo.addItems(["BTC-USD", "ETH-USD", "ADA-USD", "SOL-USD"])
        yahoo_layout.addWidget(QLabel("Símbolo:"))
        yahoo_layout.addWidget(self.symbol_combo)
        
        btn_yahoo = QPushButton("📥 Buscar do Yahoo Finance")
        btn_yahoo.clicked.connect(self.load_from_yahoo)
        yahoo_layout.addWidget(btn_yahoo)
        
        load_layout.addLayout(yahoo_layout)
        
        # Botão: Carregar CSV
        csv_layout = QHBoxLayout()
        btn_csv = QPushButton("📂 Carregar Arquivo CSV")
        btn_csv.clicked.connect(self.load_from_csv)
        csv_layout.addWidget(btn_csv)
        
        self.csv_path_label = QLabel("Nenhum arquivo selecionado")
        csv_layout.addWidget(self.csv_path_label)
        
        load_layout.addLayout(csv_layout)
        load_group.setLayout(load_layout)
        layout.addWidget(load_group)
        
        # Grupo: Informações dos Dados
        info_group = QGroupBox("Informações dos Dados")
        info_layout = QVBoxLayout()
        
        self.data_info_text = QTextEdit()
        self.data_info_text.setReadOnly(True)
        self.data_info_text.setMaximumHeight(200)
        info_layout.addWidget(self.data_info_text)
        
        info_group.setLayout(info_layout)
        layout.addWidget(info_group)
        
        # Tabela de preview
        preview_group = QGroupBox("Preview dos Dados")
        preview_layout = QVBoxLayout()
        
        self.data_table = QTableWidget()
        preview_layout.addWidget(self.data_table)
        
        preview_group.setLayout(preview_layout)
        layout.addWidget(preview_group)
        
        widget.setLayout(layout)
        return widget
    
    def create_analysis_tab(self):
        """Cria aba de análise"""
        widget = QWidget()
        layout = QVBoxLayout()
        
        # Grupo: Processamento
        process_group = QGroupBox("Processamento com Spark")
        process_layout = QVBoxLayout()
        
        btn_process = QPushButton("⚡ Processar Dados (Spark)")
        btn_process.clicked.connect(self.process_data)
        process_layout.addWidget(btn_process)
        
        self.process_progress = QProgressBar()
        self.process_progress.setVisible(False)
        process_layout.addWidget(self.process_progress)
        
        self.process_status = QTextEdit()
        self.process_status.setReadOnly(True)
        self.process_status.setMaximumHeight(150)
        process_layout.addWidget(self.process_status)
        
        process_group.setLayout(process_layout)
        layout.addWidget(process_group)
        
        # Grupo: Estatísticas
        stats_group = QGroupBox("Estatísticas Descritivas")
        stats_layout = QVBoxLayout()
        
        btn_stats = QPushButton("📊 Calcular Estatísticas")
        btn_stats.clicked.connect(self.show_statistics)
        stats_layout.addWidget(btn_stats)
        
        self.stats_table = QTableWidget()
        stats_layout.addWidget(self.stats_table)
        
        stats_group.setLayout(stats_layout)
        layout.addWidget(stats_group)
        
        widget.setLayout(layout)
        return widget
    
    def create_ml_tab(self):
        """Cria aba de Machine Learning"""
        widget = QWidget()
        layout = QVBoxLayout()
        
        # Grupo: Prophet
        prophet_group = QGroupBox("Prophet (Séries Temporais)")
        prophet_layout = QVBoxLayout()
        
        btn_prophet = QPushButton("🔮 Treinar Prophet")
        btn_prophet.clicked.connect(self.train_prophet)
        btn_prophet.setEnabled(PROPHET_AVAILABLE)
        prophet_layout.addWidget(btn_prophet)
        
        self.prophet_results = QTextEdit()
        self.prophet_results.setReadOnly(True)
        prophet_layout.addWidget(self.prophet_results)
        
        prophet_group.setLayout(prophet_layout)
        layout.addWidget(prophet_group)
        
        # Grupo: scikit-learn
        sklearn_group = QGroupBox("scikit-learn (Regressão Linear)")
        sklearn_layout = QVBoxLayout()
        
        btn_sklearn = QPushButton("🤖 Treinar Modelo")
        btn_sklearn.clicked.connect(self.train_sklearn)
        btn_sklearn.setEnabled(SKLEARN_AVAILABLE)
        sklearn_layout.addWidget(btn_sklearn)
        
        self.sklearn_results = QTextEdit()
        self.sklearn_results.setReadOnly(True)
        sklearn_layout.addWidget(self.sklearn_results)
        
        sklearn_group.setLayout(sklearn_layout)
        layout.addWidget(sklearn_group)
        
        widget.setLayout(layout)
        return widget
    
    def create_viz_tab(self):
        """Cria aba de visualizações"""
        widget = QWidget()
        layout = QVBoxLayout()
        
        # Botões de visualização
        viz_group = QGroupBox("Gerar Visualizações")
        viz_layout = QVBoxLayout()
        
        btn_price = QPushButton("📈 Gráfico de Preços")
        btn_price.clicked.connect(lambda: self.create_visualization("price"))
        viz_layout.addWidget(btn_price)
        
        btn_volume = QPushButton("📊 Gráfico de Volume")
        btn_volume.clicked.connect(lambda: self.create_visualization("volume"))
        viz_layout.addWidget(btn_volume)
        
        btn_dashboard = QPushButton("🎛️ Dashboard Completo")
        btn_dashboard.clicked.connect(lambda: self.create_visualization("dashboard"))
        viz_layout.addWidget(btn_dashboard)
        
        viz_group.setLayout(viz_layout)
        layout.addWidget(viz_group)
        
        # Status
        self.viz_status = QTextEdit()
        self.viz_status.setReadOnly(True)
        layout.addWidget(self.viz_status)
        
        widget.setLayout(layout)
        return widget
    
    def load_from_yahoo(self):
        """Carrega dados do Yahoo Finance"""
        try:
            symbol = self.symbol_combo.currentText()
            self.statusBar().showMessage(f"Buscando dados de {symbol}...")
            
            ingestion = CryptoDataIngestion()
            self.df = ingestion.fetch_from_yahoo(symbol, period="5y")
            
            self.update_data_display()
            self.statusBar().showMessage(f"Dados carregados: {len(self.df)} registros")
            
            QMessageBox.information(self, "Sucesso", f"Dados de {symbol} carregados com sucesso!")
        
        except Exception as e:
            QMessageBox.critical(self, "Erro", f"Erro ao carregar dados: {str(e)}")
            self.statusBar().showMessage("Erro ao carregar dados")
    
    def load_from_csv(self):
        """Carrega dados de arquivo CSV"""
        try:
            file_path, _ = QFileDialog.getOpenFileName(
                self, "Selecionar Arquivo CSV", "", "CSV Files (*.csv)"
            )
            
            if file_path:
                self.csv_path_label.setText(Path(file_path).name)
                self.statusBar().showMessage("Carregando CSV...")
                
                ingestion = CryptoDataIngestion()
                self.df = ingestion.load_from_csv(file_path)
                
                self.update_data_display()
                self.statusBar().showMessage(f"CSV carregado: {len(self.df)} registros")
                
                QMessageBox.information(self, "Sucesso", "CSV carregado com sucesso!")
        
        except Exception as e:
            QMessageBox.critical(self, "Erro", f"Erro ao carregar CSV: {str(e)}")
            self.statusBar().showMessage("Erro ao carregar CSV")
    
    def update_data_display(self):
        """Atualiza exibição dos dados"""
        if self.df is None:
            return
        
        # Atualizar informações
        info = f"Registros: {len(self.df)}\n"
        info += f"Colunas: {', '.join(self.df.columns)}\n"
        
        if 'Date' in self.df.columns:
            info += f"Período: {self.df['Date'].min()} a {self.df['Date'].max()}\n"
        
        self.data_info_text.setText(info)
        
        # Atualizar tabela (primeiras 20 linhas)
        df_preview = self.df.head(20)
        self.data_table.setRowCount(len(df_preview))
        self.data_table.setColumnCount(len(df_preview.columns))
        self.data_table.setHorizontalHeaderLabels(df_preview.columns)
        
        for i, row in df_preview.iterrows():
            for j, value in enumerate(row):
                self.data_table.setItem(i, j, QTableWidgetItem(str(value)))
        
        self.data_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeToContents)
    
    def process_data(self):
        """Processa dados com Spark"""
        if self.df is None:
            QMessageBox.warning(self, "Aviso", "Carregue os dados primeiro!")
            return
        
        self.process_progress.setVisible(True)
        self.process_progress.setRange(0, 0)  # Indeterminado
        
        self.worker = AnalysisWorker(self.df, "process")
        self.worker.progress.connect(lambda msg: self.process_status.append(msg))
        self.worker.finished.connect(self.on_process_finished)
        self.worker.error.connect(self.on_analysis_error)
        self.worker.start()
    
    def on_process_finished(self, results):
        """Callback quando processamento termina"""
        self.process_progress.setVisible(False)
        self.df_processed = results.get('df')
        self.process_status.append(f"\n✅ {results['message']}")
        QMessageBox.information(self, "Sucesso", "Dados processados com sucesso!")
    
    def train_prophet(self):
        """Treina modelo Prophet"""
        if self.df is None:
            QMessageBox.warning(self, "Aviso", "Carregue os dados primeiro!")
            return
        
        self.worker = AnalysisWorker(self.df, "prophet")
        self.worker.progress.connect(lambda msg: self.prophet_results.append(msg))
        self.worker.finished.connect(self.on_prophet_finished)
        self.worker.error.connect(self.on_analysis_error)
        self.worker.start()
    
    def on_prophet_finished(self, results):
        """Callback quando Prophet termina"""
        forecast = results.get('forecast')
        trend = results.get('trend')
        
        output = f"\n✅ {results['message']}\n\n"
        output += f"Análise de Tendência:\n"
        output += f"Direção: {trend['direction']}\n"
        output += f"Variação: {trend['trend_change_pct']}%\n\n"
        output += f"Previsões (próximos 30 dias):\n{forecast.to_string()}"
        
        self.prophet_results.append(output)
        QMessageBox.information(self, "Sucesso", "Modelo Prophet treinado!")
    
    def train_sklearn(self):
        """Treina modelo scikit-learn"""
        if self.df is None:
            QMessageBox.warning(self, "Aviso", "Carregue os dados primeiro!")
            return
        
        self.worker = AnalysisWorker(self.df, "sklearn")
        self.worker.progress.connect(lambda msg: self.sklearn_results.append(msg))
        self.worker.finished.connect(self.on_sklearn_finished)
        self.worker.error.connect(self.on_analysis_error)
        self.worker.start()
    
    def on_sklearn_finished(self, results):
        """Callback quando sklearn termina"""
        metrics = results.get('metrics')
        forecast = results.get('forecast')
        
        output = f"\n✅ {results['message']}\n\n"
        output += f"Métricas de Avaliação:\n"
        for key, value in metrics.items():
            output += f"{key}: {value}\n"
        output += f"\nPrevisões (próximos 7 dias):\n{forecast.to_string()}"
        
        self.sklearn_results.append(output)
        QMessageBox.information(self, "Sucesso", "Modelo scikit-learn treinado!")
    
    def on_analysis_error(self, error_msg):
        """Callback para erros"""
        QMessageBox.critical(self, "Erro", f"Erro na análise: {error_msg}")
    
    def show_statistics(self):
        """Mostra estatísticas descritivas"""
        if self.df is None:
            QMessageBox.warning(self, "Aviso", "Carregue os dados primeiro!")
            return
        
        df_stats = self.df.describe()
        
        self.stats_table.setRowCount(len(df_stats))
        self.stats_table.setColumnCount(len(df_stats.columns))
        self.stats_table.setVerticalHeaderLabels(df_stats.index)
        self.stats_table.setHorizontalHeaderLabels(df_stats.columns)
        
        for i, row in df_stats.iterrows():
            for j, value in enumerate(row):
                self.stats_table.setItem(
                    df_stats.index.get_loc(i),
                    j,
                    QTableWidgetItem(f"{value:.2f}")
                )
    
    def create_visualization(self, viz_type):
        """Cria visualizações"""
        if self.df is None:
            QMessageBox.warning(self, "Aviso", "Carregue os dados primeiro!")
            return
        
        if not PLOTLY_AVAILABLE:
            QMessageBox.warning(self, "Aviso", "Plotly não está disponível!")
            return
        
        try:
            visualizer = CryptoVisualizer()
            
            if viz_type == "price":
                fig = visualizer.plot_price_history(self.df)
                visualizer.save_figure(fig, "price_chart.html")
                self.viz_status.append("✅ Gráfico de preços salvo em visualizations/price_chart.html")
            
            elif viz_type == "volume" and 'Volume' in self.df.columns:
                fig = visualizer.plot_volume(self.df)
                visualizer.save_figure(fig, "volume_chart.html")
                self.viz_status.append("✅ Gráfico de volume salvo em visualizations/volume_chart.html")
            
            elif viz_type == "dashboard":
                # Processar dados se necessário
                if self.df_processed is not None:
                    fig = visualizer.plot_dashboard(self.df_processed)
                else:
                    fig = visualizer.plot_dashboard(self.df)
                visualizer.save_figure(fig, "dashboard.html")
                self.viz_status.append("✅ Dashboard salvo em visualizations/dashboard.html")
            
            # Abrir arquivo no navegador
            import webbrowser
            webbrowser.open(f"visualizations/{viz_type}_chart.html" if viz_type != "dashboard" else "visualizations/dashboard.html")
            
        except Exception as e:
            QMessageBox.critical(self, "Erro", f"Erro ao criar visualização: {str(e)}")
    
    def apply_style(self):
        """Aplica estilo à aplicação"""
        self.setStyleSheet("""
            QMainWindow {
                background-color: #1e1e1e;
            }
            QWidget {
                background-color: #1e1e1e;
                color: #ffffff;
            }
            QGroupBox {
                border: 2px solid #3c3c3c;
                border-radius: 5px;
                margin-top: 10px;
                padding-top: 10px;
                font-weight: bold;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 3px;
            }
            QPushButton {
                background-color: #0d7377;
                color: white;
                border: none;
                padding: 10px;
                border-radius: 5px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #14a085;
            }
            QPushButton:pressed {
                background-color: #0a5f5f;
            }
            QPushButton:disabled {
                background-color: #3c3c3c;
                color: #808080;
            }
            QTextEdit, QTableWidget {
                background-color: #252526;
                border: 1px solid #3c3c3c;
                color: #ffffff;
            }
            QComboBox {
                background-color: #252526;
                border: 1px solid #3c3c3c;
                padding: 5px;
                color: #ffffff;
            }
            QLabel {
                color: #ffffff;
            }
            QProgressBar {
                border: 1px solid #3c3c3c;
                border-radius: 5px;
                text-align: center;
            }
            QProgressBar::chunk {
                background-color: #0d7377;
            }
        """)


def main():
    app = QApplication(sys.argv)
    window = CryptoAnalysisApp()
    window.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
