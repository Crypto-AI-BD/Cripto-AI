"""
Modelos de Machine Learning com scikit-learn
Regressão Linear e outros modelos para previsão de preços
"""
import pandas as pd
import numpy as np
from pathlib import Path
import logging
from typing import Optional, Dict, Any, Tuple
import pickle
import json

logger = logging.getLogger(__name__)

try:
    from sklearn.model_selection import train_test_split
    from sklearn.linear_model import LinearRegression, Ridge, Lasso
    from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
    from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
    from sklearn.preprocessing import StandardScaler
    SKLEARN_AVAILABLE = True
except ImportError:
    logger.warning("scikit-learn não está disponível")
    SKLEARN_AVAILABLE = False


class CryptoMLModel:
    """Classe para modelos de Machine Learning"""
    
    def __init__(self, model_type: str = 'linear_regression'):
        """
        Inicializa o modelo
        
        Args:
            model_type: Tipo de modelo ('linear_regression', 'ridge', 'lasso', 
                       'random_forest', 'gradient_boosting')
        """
        if not SKLEARN_AVAILABLE:
            raise ImportError("scikit-learn não está disponível")
        
        self.model_type = model_type
        self.model = None
        self.scaler = StandardScaler()
        self.feature_names = []
        self.model_params = {}
        
        self._initialize_model()
    
    def _initialize_model(self):
        """Inicializa o modelo baseado no tipo"""
        if self.model_type == 'linear_regression':
            self.model = LinearRegression()
        elif self.model_type == 'ridge':
            self.model = Ridge(alpha=1.0)
        elif self.model_type == 'lasso':
            self.model = Lasso(alpha=1.0)
        elif self.model_type == 'random_forest':
            self.model = RandomForestRegressor(n_estimators=100, random_state=42)
        elif self.model_type == 'gradient_boosting':
            self.model = GradientBoostingRegressor(n_estimators=100, random_state=42)
        else:
            raise ValueError(f"Modelo não suportado: {self.model_type}")
        
        logger.info(f"Modelo inicializado: {self.model_type}")
    
    def prepare_features(
        self,
        df: pd.DataFrame,
        target_col: str = 'Close',
        feature_cols: Optional[list] = None,
        lag_days: int = 5
    ) -> Tuple[pd.DataFrame, pd.Series]:
        """
        Prepara features para o modelo
        
        Args:
            df: DataFrame com dados
            target_col: Coluna alvo (preço a prever)
            feature_cols: Colunas de features (None = automático)
            lag_days: Dias de lag para criar features
        
        Returns:
            Tuple com (X, y)
        """
        df_copy = df.copy()
        
        # Criar features de lag (preços anteriores)
        for i in range(1, lag_days + 1):
            df_copy[f'Close_Lag_{i}'] = df_copy[target_col].shift(i)
        
        # Criar features de médias móveis
        for window in [7, 14, 30]:
            df_copy[f'MA_{window}'] = df_copy[target_col].rolling(window=window).mean()
        
        # Criar features de volatilidade
        df_copy['Volatility_7d'] = df_copy[target_col].rolling(window=7).std()
        df_copy['Volatility_30d'] = df_copy[target_col].rolling(window=30).std()
        
        # Criar features de retorno
        df_copy['Return_1d'] = df_copy[target_col].pct_change()
        df_copy['Return_7d'] = df_copy[target_col].pct_change(periods=7)
        
        # Features de volume (se disponível)
        if 'Volume' in df_copy.columns:
            df_copy['Volume_MA_7'] = df_copy['Volume'].rolling(window=7).mean()
            df_copy['Volume_Change'] = df_copy['Volume'].pct_change()
        
        # Remover linhas com NaN
        df_copy = df_copy.dropna()
        
        # Selecionar features
        if feature_cols is None:
            # Usar todas as colunas exceto o target e Date
            feature_cols = [col for col in df_copy.columns 
                          if col not in [target_col, 'Date', 'Symbol'] 
                          and df_copy[col].dtype in ['float64', 'int64']]
        
        self.feature_names = feature_cols
        
        X = df_copy[feature_cols]
        y = df_copy[target_col]
        
        logger.info(f"Features preparadas: {len(feature_cols)} features, {len(df_copy)} amostras")
        
        return X, y
    
    def train(
        self,
        X_train: pd.DataFrame,
        y_train: pd.Series,
        scale: bool = True
    ):
        """
        Treina o modelo
        
        Args:
            X_train: Features de treino
            y_train: Target de treino
            scale: Se deve escalar as features
        """
        logger.info("Iniciando treinamento do modelo...")
        
        if scale:
            X_train_scaled = self.scaler.fit_transform(X_train)
        else:
            X_train_scaled = X_train
        
        self.model.fit(X_train_scaled, y_train)
        
        logger.info("Modelo treinado com sucesso")
    
    def predict(self, X: pd.DataFrame, scale: bool = True) -> np.ndarray:
        """
        Faz previsões
        
        Args:
            X: Features para previsão
            scale: Se deve escalar as features
        
        Returns:
            Array com previsões
        """
        if self.model is None:
            raise ValueError("Modelo não foi treinado")
        
        if scale:
            X_scaled = self.scaler.transform(X)
        else:
            X_scaled = X
        
        predictions = self.model.predict(X_scaled)
        
        return predictions
    
    def evaluate(
        self,
        X_test: pd.DataFrame,
        y_test: pd.Series,
        scale: bool = True
    ) -> Dict[str, float]:
        """
        Avalia o modelo
        
        Args:
            X_test: Features de teste
            y_test: Target de teste
            scale: Se deve escalar as features
        
        Returns:
            Dicionário com métricas
        """
        y_pred = self.predict(X_test, scale=scale)
        
        mae = mean_absolute_error(y_test, y_pred)
        rmse = np.sqrt(mean_squared_error(y_test, y_pred))
        r2 = r2_score(y_test, y_pred)
        mape = np.mean(np.abs((y_test - y_pred) / y_test)) * 100
        
        metrics = {
            'MAE': round(mae, 2),
            'RMSE': round(rmse, 2),
            'R2': round(r2, 4),
            'MAPE': round(mape, 2)
        }
        
        logger.info(f"Métricas de avaliação: {metrics}")
        
        return metrics
    
    def get_feature_importance(self) -> pd.DataFrame:
        """
        Retorna a importância das features (para modelos tree-based)
        
        Returns:
            DataFrame com importância das features
        """
        if not hasattr(self.model, 'feature_importances_'):
            logger.warning("Modelo não suporta feature importance")
            return pd.DataFrame()
        
        importance_df = pd.DataFrame({
            'Feature': self.feature_names,
            'Importance': self.model.feature_importances_
        }).sort_values('Importance', ascending=False)
        
        return importance_df
    
    def save_model(self, filepath: str):
        """
        Salva o modelo
        
        Args:
            filepath: Caminho para salvar
        """
        if self.model is None:
            raise ValueError("Nenhum modelo para salvar")
        
        model_path = Path(filepath)
        model_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Salvar modelo e scaler
        model_data = {
            'model': self.model,
            'scaler': self.scaler,
            'feature_names': self.feature_names,
            'model_type': self.model_type
        }
        
        with open(model_path, 'wb') as f:
            pickle.dump(model_data, f)
        
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
            model_data = pickle.load(f)
        
        self.model = model_data['model']
        self.scaler = model_data['scaler']
        self.feature_names = model_data['feature_names']
        self.model_type = model_data['model_type']
        
        logger.info(f"Modelo carregado de: {model_path}")
    
    def predict_next_days(
        self,
        df: pd.DataFrame,
        days: int = 7,
        target_col: str = 'Close'
    ) -> pd.DataFrame:
        """
        Prevê os próximos dias
        
        Args:
            df: DataFrame com dados históricos
            days: Número de dias para prever
            target_col: Coluna alvo
        
        Returns:
            DataFrame com previsões
        """
        predictions = []
        df_copy = df.copy()
        
        for _ in range(days):
            # Preparar features para o último registro
            X, _ = self.prepare_features(df_copy, target_col=target_col)
            X_last = X.tail(1)
            
            # Fazer previsão
            pred = self.predict(X_last)[0]
            predictions.append(pred)
            
            # Adicionar previsão ao DataFrame para próxima iteração
            last_date = df_copy['Date'].max()
            new_date = last_date + pd.Timedelta(days=1)
            
            new_row = df_copy.iloc[-1].copy()
            new_row['Date'] = new_date
            new_row[target_col] = pred
            
            df_copy = pd.concat([df_copy, pd.DataFrame([new_row])], ignore_index=True)
        
        # Criar DataFrame com previsões
        forecast_df = pd.DataFrame({
            'Date': pd.date_range(
                start=df['Date'].max() + pd.Timedelta(days=1),
                periods=days
            ),
            'Predicted_Close': predictions
        })
        
        return forecast_df


if __name__ == "__main__":
    # Exemplo de uso
    if SKLEARN_AVAILABLE:
        data_path = Path("data/raw/btc_usd_historical.csv")
        if data_path.exists():
            df = pd.read_csv(data_path)
            df['Date'] = pd.to_datetime(df['Date'])
            
            # Criar modelo
            ml_model = CryptoMLModel(model_type='linear_regression')
            
            # Preparar features
            X, y = ml_model.prepare_features(df)
            
            # Dividir dados
            X_train, X_test, y_train, y_test = train_test_split(
                X, y, test_size=0.2, shuffle=False
            )
            
            # Treinar
            ml_model.train(X_train, y_train)
            
            # Avaliar
            metrics = ml_model.evaluate(X_test, y_test)
            print(f"Métricas: {metrics}")
            
            # Prever próximos dias
            forecast = ml_model.predict_next_days(df, days=7)
            print(f"\nPrevisões para próximos 7 dias:\n{forecast}")
            
            # Salvar modelo
            ml_model.save_model("models/sklearn_btc_model.pkl")
    else:
        print("scikit-learn não está disponível")
