"""
Módulo para ingestão de dados de criptomoedas
Suporta Yahoo Finance API e upload de arquivos CSV
"""
import pandas as pd
import yfinance as yf
from pathlib import Path
from typing import Optional, List
import logging
from datetime import datetime

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class CryptoDataIngestion:
    """Classe para ingestão de dados de criptomoedas"""
    
    def __init__(self, output_dir: str = "data/raw"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
    
    def fetch_from_yahoo(
        self,
        symbol: str = "BTC-USD",
        period: str = "5y",
        interval: str = "1d"
    ) -> pd.DataFrame:
        """
        Busca dados históricos do Yahoo Finance
        
        Args:
            symbol: Símbolo da criptomoeda (ex: BTC-USD, ETH-USD)
            period: Período de dados (1d, 5d, 1mo, 3mo, 6mo, 1y, 2y, 5y, 10y, ytd, max)
            interval: Intervalo dos dados (1m, 2m, 5m, 15m, 30m, 60m, 90m, 1h, 1d, 5d, 1wk, 1mo, 3mo)
        
        Returns:
            DataFrame com dados históricos
        """
        try:
            logger.info(f"Buscando dados de {symbol} do Yahoo Finance...")
            ticker = yf.Ticker(symbol)
            df = ticker.history(period=period, interval=interval)
            
            if df.empty:
                raise ValueError(f"Nenhum dado encontrado para {symbol}")
            
            # Adicionar coluna com o símbolo
            df['Symbol'] = symbol
            
            # Reset index para ter Date como coluna
            df.reset_index(inplace=True)
            
            # Remover timezone se existir na coluna Date
            if 'Date' in df.columns and df['Date'].dt.tz is not None:
                df['Date'] = df['Date'].dt.tz_localize(None)
            
            # Salvar localmente
            filename = f"{symbol.replace('-', '_').lower()}_historical.csv"
            output_path = self.output_dir / filename
            df.to_csv(output_path, index=False)
            logger.info(f"Dados salvos em: {output_path}")
            
            return df
        
        except Exception as e:
            logger.error(f"Erro ao buscar dados: {str(e)}")
            raise
    
    def load_from_csv(self, filepath: str) -> pd.DataFrame:
        """
        Carrega dados de um arquivo CSV
        
        Args:
            filepath: Caminho do arquivo CSV
        
        Returns:
            DataFrame com os dados
        """
        try:
            logger.info(f"Carregando dados de {filepath}...")
            df = pd.read_csv(filepath)
            
            # Tentar converter coluna de data
            date_columns = ['Date', 'date', 'Datetime', 'datetime', 'timestamp']
            for col in date_columns:
                if col in df.columns:
                    df[col] = pd.to_datetime(df[col])
                    # Remover timezone se existir
                    if df[col].dt.tz is not None:
                        df[col] = df[col].dt.tz_localize(None)
                    break
            
            logger.info(f"Dados carregados: {len(df)} registros")
            return df
        
        except Exception as e:
            logger.error(f"Erro ao carregar CSV: {str(e)}")
            raise
    
    def fetch_multiple_symbols(
        self,
        symbols: List[str],
        period: str = "5y",
        interval: str = "1d"
    ) -> dict:
        """
        Busca dados de múltiplas criptomoedas
        
        Args:
            symbols: Lista de símbolos
            period: Período de dados
            interval: Intervalo dos dados
        
        Returns:
            Dicionário com DataFrames para cada símbolo
        """
        data_dict = {}
        
        for symbol in symbols:
            try:
                df = self.fetch_from_yahoo(symbol, period, interval)
                data_dict[symbol] = df
            except Exception as e:
                logger.error(f"Falha ao buscar {symbol}: {str(e)}")
        
        return data_dict
    
    def validate_data(self, df: pd.DataFrame) -> bool:
        """
        Valida se o DataFrame possui as colunas necessárias
        
        Args:
            df: DataFrame para validar
        
        Returns:
            True se válido, False caso contrário
        """
        required_columns = ['Date', 'Close']
        
        # Verificar variações de nomes de colunas
        df_columns_lower = [col.lower() for col in df.columns]
        
        for req_col in required_columns:
            if req_col.lower() not in df_columns_lower:
                logger.error(f"Coluna obrigatória ausente: {req_col}")
                return False
        
        return True
    
    def get_data_info(self, df: pd.DataFrame) -> dict:
        """
        Retorna informações sobre o dataset
        
        Args:
            df: DataFrame para analisar
        
        Returns:
            Dicionário com informações
        """
        return {
            "rows": len(df),
            "columns": len(df.columns),
            "column_names": df.columns.tolist(),
            "date_range": {
                "start": df['Date'].min() if 'Date' in df.columns else None,
                "end": df['Date'].max() if 'Date' in df.columns else None
            },
            "missing_values": df.isnull().sum().to_dict(),
            "dtypes": df.dtypes.to_dict()
        }


if __name__ == "__main__":
    # Exemplo de uso
    ingestion = CryptoDataIngestion()
    
    # Buscar dados do Bitcoin
    btc_data = ingestion.fetch_from_yahoo("BTC-USD", period="5y")
    print(f"Bitcoin: {len(btc_data)} registros")
    
    # Buscar dados do Ethereum
    eth_data = ingestion.fetch_from_yahoo("ETH-USD", period="5y")
    print(f"Ethereum: {len(eth_data)} registros")
    
    # Informações sobre os dados
    info = ingestion.get_data_info(btc_data)
    print(f"\nInformações do dataset: {info}")
