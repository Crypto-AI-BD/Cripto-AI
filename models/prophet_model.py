"""
Modelo de previsão usando Prophet (Facebook)
Para análise de séries temporais de criptomoedas
"""
import pandas as pd
import numpy as np
from pathlib import Path
import logging
from typing import Optional, Dict, Any
import pickle
import json

logger = logging.getLogger(__name__)

try:
    from prophet import Prophet
    from prophet.plot import plot_plotly, plot_components_plotly
    PROPHET_AVAILABLE = True
except ImportError:
    logger.warning("Prophet não está disponível. Instale com: pip install prophet")
    PROPHET_AVAILABLE = False


class CryptoProphetModel:
    """Classe para previsão de preços com Prophet"""
    
    def __init__(self):
        self.model = None
        self.forecast = None
        self.model_params = {}
    
    def prepare_data(self, df: pd.DataFrame, date_col: str = 'Date', value_col: str = 'Close') -> pd.DataFrame:
        """
        Prepara dados no formato esperado pelo Prophet (ds, y)
        
        Args:
            df: DataFrame com dados históricos
            date_col: Nome da coluna de data
            value_col: Nome da coluna de valor (preço)
        
        Returns:
            DataFrame preparado
        """
        if not PROPHET_AVAILABLE:
            raise ImportError("Prophet não está disponível")
        
        df_prophet = pd.DataFrame()
        # Converter para datetime e remover timezone se existir
        df_prophet['ds'] = pd.to_datetime(df[date_col])
        if df_prophet['ds'].dt.tz is not None:
            df_prophet['ds'] = df_prophet['ds'].dt.tz_localize(None)
        df_prophet['y'] = df[value_col]
        
        logger.info(f"Dados preparados: {len(df_prophet)} registros")
        return df_prophet
    
    def train(
        self,
        df: pd.DataFrame,
        changepoint_prior_scale: float = 0.05,
        seasonality_mode: str = 'multiplicative',
        yearly_seasonality: bool = True,
        weekly_seasonality: bool = True,
        daily_seasonality: bool = False
    ):
        """
        Treina o modelo Prophet
        
        Args:
            df: DataFrame preparado (ds, y)
            changepoint_prior_scale: Flexibilidade da tendência
            seasonality_mode: Modo de sazonalidade ('additive' ou 'multiplicative')
            yearly_seasonality: Incluir sazonalidade anual
            weekly_seasonality: Incluir sazonalidade semanal
            daily_seasonality: Incluir sazonalidade diária
        """
        if not PROPHET_AVAILABLE:
            raise ImportError("Prophet não está disponível")
        
        logger.info("Iniciando treinamento do Prophet...")
        
        # Salvar parâmetros
        self.model_params = {
            'changepoint_prior_scale': changepoint_prior_scale,
            'seasonality_mode': seasonality_mode,
            'yearly_seasonality': yearly_seasonality,
            'weekly_seasonality': weekly_seasonality,
            'daily_seasonality': daily_seasonality
        }
        
        # Criar e treinar modelo
        self.model = Prophet(
            changepoint_prior_scale=changepoint_prior_scale,
            seasonality_mode=seasonality_mode,
            yearly_seasonality=yearly_seasonality,
            weekly_seasonality=weekly_seasonality,
            daily_seasonality=daily_seasonality
        )
        
        self.model.fit(df)
        logger.info("Modelo Prophet treinado com sucesso")
    
    def predict(self, periods: int = 30, freq: str = 'D') -> pd.DataFrame:
        """
        Faz previsões futuras
        
        Args:
            periods: Número de períodos para prever
            freq: Frequência ('D' para dias, 'H' para horas)
        
        Returns:
            DataFrame com previsões
        """
        if not PROPHET_AVAILABLE or self.model is None:
            raise ValueError("Modelo não foi treinado")
        
        logger.info(f"Fazendo previsões para {periods} períodos...")
        
        # Criar dataframe futuro
        future = self.model.make_future_dataframe(periods=periods, freq=freq)
        
        # Fazer previsões
        self.forecast = self.model.predict(future)
        
        logger.info("Previsões concluídas")
        return self.forecast
    
    def get_forecast_summary(self, last_n: int = 30) -> pd.DataFrame:
        """
        Retorna resumo das previsões
        
        Args:
            last_n: Número de últimas previsões para retornar
        
        Returns:
            DataFrame com resumo
        """
        if self.forecast is None:
            raise ValueError("Nenhuma previsão disponível. Execute predict() primeiro.")
        
        summary = self.forecast[['ds', 'yhat', 'yhat_lower', 'yhat_upper']].tail(last_n)
        summary = summary.rename(columns={
            'ds': 'Date',
            'yhat': 'Predicted',
            'yhat_lower': 'Lower_Bound',
            'yhat_upper': 'Upper_Bound'
        })
        
        return summary
    
    def evaluate(self, df_test: pd.DataFrame) -> Dict[str, float]:
        """
        Avalia o modelo com dados de teste
        
        Args:
            df_test: DataFrame de teste preparado (ds, y)
        
        Returns:
            Dicionário com métricas de avaliação
        """
        if not PROPHET_AVAILABLE or self.model is None:
            raise ValueError("Modelo não foi treinado")
        
        # Fazer previsões para as datas de teste
        forecast_test = self.model.predict(df_test[['ds']])
        
        # Calcular métricas
        y_true = df_test['y'].values
        y_pred = forecast_test['yhat'].values
        
        mae = np.mean(np.abs(y_true - y_pred))
        rmse = np.sqrt(np.mean((y_true - y_pred) ** 2))
        mape = np.mean(np.abs((y_true - y_pred) / y_true)) * 100
        
        metrics = {
            'MAE': round(mae, 2),
            'RMSE': round(rmse, 2),
            'MAPE': round(mape, 2)
        }
        
        logger.info(f"Métricas de avaliação: {metrics}")
        return metrics
    
    def save_model(self, filepath: str):
        """
        Salva o modelo treinado
        
        Args:
            filepath: Caminho para salvar o modelo
        """
        if self.model is None:
            raise ValueError("Nenhum modelo para salvar")
        
        model_path = Path(filepath)
        model_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(model_path, 'wb') as f:
            pickle.dump(self.model, f)
        
        # Salvar parâmetros
        params_path = model_path.with_suffix('.json')
        with open(params_path, 'w') as f:
            json.dump(self.model_params, f, indent=2)
        
        logger.info(f"Modelo salvo em: {model_path}")
    
    def load_model(self, filepath: str):
        """
        Carrega um modelo salvo
        
        Args:
            filepath: Caminho do modelo
        """
        model_path = Path(filepath)
        
        if not model_path.exists():
            raise FileNotFoundError(f"Modelo não encontrado: {model_path}")
        
        with open(model_path, 'rb') as f:
            self.model = pickle.load(f)
        
        # Carregar parâmetros
        params_path = model_path.with_suffix('.json')
        if params_path.exists():
            with open(params_path, 'r') as f:
                self.model_params = json.load(f)
        
        logger.info(f"Modelo carregado de: {model_path}")
    
    def get_trend_analysis(self) -> Dict[str, Any]:
        """
        Analisa a tendência dos dados
        
        Returns:
            Dicionário com análise de tendência
        """
        if self.forecast is None:
            raise ValueError("Nenhuma previsão disponível")
        
        # Análise da tendência
        trend = self.forecast['trend'].values
        trend_start = trend[0]
        trend_end = trend[-1]
        trend_change = ((trend_end - trend_start) / trend_start) * 100
        
        # Direção da tendência
        if trend_change > 5:
            direction = "Alta (Bullish)"
        elif trend_change < -5:
            direction = "Baixa (Bearish)"
        else:
            direction = "Lateral (Sideways)"
        
        analysis = {
            'trend_start': round(trend_start, 2),
            'trend_end': round(trend_end, 2),
            'trend_change_pct': round(trend_change, 2),
            'direction': direction
        }
        
        return analysis


if __name__ == "__main__":
    # Exemplo de uso
    if PROPHET_AVAILABLE:
        # Carregar dados de exemplo
        data_path = Path("data/raw/btc_usd_historical.csv")
        if data_path.exists():
            df = pd.read_csv(data_path)
            
            # Preparar dados
            prophet_model = CryptoProphetModel()
            df_prophet = prophet_model.prepare_data(df)
            
            # Dividir em treino e teste (80/20)
            split_idx = int(len(df_prophet) * 0.8)
            df_train = df_prophet[:split_idx]
            df_test = df_prophet[split_idx:]
            
            # Treinar modelo
            prophet_model.train(df_train)
            
            # Fazer previsões
            forecast = prophet_model.predict(periods=30)
            
            # Avaliar
            metrics = prophet_model.evaluate(df_test)
            print(f"Métricas: {metrics}")
            
            # Análise de tendência
            trend = prophet_model.get_trend_analysis()
            print(f"Tendência: {trend}")
            
            # Salvar modelo
            prophet_model.save_model("models/prophet_btc_model.pkl")
    else:
        print("Prophet não está disponível. Instale com: pip install prophet")
