"""
Módulo para processamento de dados com Apache Spark
Inclui cálculo de médias móveis e transformações de Big Data
"""
import os
import sys
from pathlib import Path
import pandas as pd
import logging
from typing import Optional, List

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

try:
    import findspark
    findspark.init()
    from pyspark.sql import SparkSession
    from pyspark.sql.functions import (
        col, avg, lag, lit, round as spark_round,
        stddev, max as spark_max, min as spark_min,
        year, month, dayofmonth, when
    )
    from pyspark.sql.window import Window
    SPARK_AVAILABLE = True
except ImportError:
    logger.warning("PySpark não está disponível. Usando processamento com Pandas.")
    SPARK_AVAILABLE = False


class SparkDataProcessor:
    """Classe para processamento de dados com Spark"""
    
    def __init__(self, app_name: str = "CryptoAnalysis", master: str = "local[*]"):
        self.app_name = app_name
        self.master = master
        self.spark = None
        
        if SPARK_AVAILABLE:
            self._initialize_spark()
        else:
            logger.info("Spark não disponível. Usando processamento alternativo.")
    
    def _initialize_spark(self):
        """Inicializa a sessão Spark"""
        try:
            self.spark = SparkSession.builder \
                .appName(self.app_name) \
                .master(self.master) \
                .config("spark.sql.execution.arrow.pyspark.enabled", "true") \
                .config("spark.driver.memory", "4g") \
                .config("spark.executor.memory", "4g") \
                .getOrCreate()
            
            logger.info(f"Spark Session iniciada: {self.spark.version}")
        
        except Exception as e:
            logger.error(f"Erro ao inicializar Spark: {str(e)}")
            self.spark = None
            raise
    
    def pandas_to_spark(self, df: pd.DataFrame):
        """Converte DataFrame Pandas para Spark"""
        if not SPARK_AVAILABLE or self.spark is None:
            return df
        
        return self.spark.createDataFrame(df)
    
    def spark_to_pandas(self, spark_df) -> pd.DataFrame:
        """Converte DataFrame Spark para Pandas"""
        if not SPARK_AVAILABLE or spark_df is None:
            return spark_df
        
        return spark_df.toPandas()
    
    def calculate_moving_averages(
        self,
        df: pd.DataFrame,
        windows: List[int] = [7, 30, 90, 200],
        price_column: str = "Close"
    ) -> pd.DataFrame:
        """
        Calcula médias móveis usando Spark
        
        Args:
            df: DataFrame com dados de preços
            windows: Lista de janelas para médias móveis
            price_column: Nome da coluna de preço
        
        Returns:
            DataFrame com médias móveis calculadas
        """
        if not SPARK_AVAILABLE or self.spark is None:
            return self._calculate_moving_averages_pandas(df, windows, price_column)
        
        try:
            logger.info("Calculando médias móveis com Spark...")
            
            # Converter para Spark DataFrame
            spark_df = self.pandas_to_spark(df)
            
            # Ordenar por data
            if 'Date' in df.columns:
                spark_df = spark_df.orderBy('Date')
            
            # Calcular médias móveis
            for window in windows:
                window_spec = Window.orderBy('Date').rowsBetween(-(window-1), 0)
                col_name = f'MA_{window}'
                spark_df = spark_df.withColumn(
                    col_name,
                    spark_round(avg(col(price_column)).over(window_spec), 2)
                )
            
            # Converter de volta para Pandas
            result_df = self.spark_to_pandas(spark_df)
            logger.info(f"Médias móveis calculadas: {windows}")
            
            return result_df
        
        except Exception as e:
            logger.error(f"Erro ao calcular médias móveis: {str(e)}")
            return self._calculate_moving_averages_pandas(df, windows, price_column)
    
    def _calculate_moving_averages_pandas(
        self,
        df: pd.DataFrame,
        windows: List[int],
        price_column: str
    ) -> pd.DataFrame:
        """Fallback: Calcula médias móveis com Pandas"""
        logger.info("Calculando médias móveis com Pandas (fallback)...")
        
        df_copy = df.copy()
        
        for window in windows:
            col_name = f'MA_{window}'
            df_copy[col_name] = df_copy[price_column].rolling(window=window).mean().round(2)
        
        return df_copy
    
    def calculate_technical_indicators(
        self,
        df: pd.DataFrame,
        price_column: str = "Close"
    ) -> pd.DataFrame:
        """
        Calcula indicadores técnicos adicionais
        
        Args:
            df: DataFrame com dados de preços
            price_column: Nome da coluna de preço
        
        Returns:
            DataFrame com indicadores calculados
        """
        if not SPARK_AVAILABLE or self.spark is None:
            return self._calculate_indicators_pandas(df, price_column)
        
        try:
            spark_df = self.pandas_to_spark(df)
            
            # Retorno diário
            window_spec = Window.orderBy('Date')
            spark_df = spark_df.withColumn(
                'Daily_Return',
                spark_round(
                    ((col(price_column) - lag(col(price_column), 1).over(window_spec)) /
                     lag(col(price_column), 1).over(window_spec)) * 100,
                    2
                )
            )
            
            # Volatilidade (desvio padrão de 30 dias)
            window_30d = Window.orderBy('Date').rowsBetween(-29, 0)
            spark_df = spark_df.withColumn(
                'Volatility_30d',
                spark_round(stddev(col('Daily_Return')).over(window_30d), 2)
            )
            
            # High-Low Spread
            if 'High' in df.columns and 'Low' in df.columns:
                spark_df = spark_df.withColumn(
                    'HL_Spread',
                    spark_round(col('High') - col('Low'), 2)
                )
            
            # Volume Moving Average
            if 'Volume' in df.columns:
                volume_window = Window.orderBy('Date').rowsBetween(-19, 0)
                spark_df = spark_df.withColumn(
                    'Volume_MA_20',
                    spark_round(avg(col('Volume')).over(volume_window), 0)
                )
            
            return self.spark_to_pandas(spark_df)
        
        except Exception as e:
            logger.error(f"Erro ao calcular indicadores: {str(e)}")
            return self._calculate_indicators_pandas(df, price_column)
    
    def _calculate_indicators_pandas(
        self,
        df: pd.DataFrame,
        price_column: str
    ) -> pd.DataFrame:
        """Fallback: Calcula indicadores com Pandas"""
        df_copy = df.copy()
        
        # Retorno diário
        df_copy['Daily_Return'] = df_copy[price_column].pct_change() * 100
        
        # Volatilidade
        df_copy['Volatility_30d'] = df_copy['Daily_Return'].rolling(window=30).std()
        
        # High-Low Spread
        if 'High' in df.columns and 'Low' in df.columns:
            df_copy['HL_Spread'] = df_copy['High'] - df_copy['Low']
        
        # Volume MA
        if 'Volume' in df.columns:
            df_copy['Volume_MA_20'] = df_copy['Volume'].rolling(window=20).mean()
        
        return df_copy
    
    def aggregate_by_period(
        self,
        df: pd.DataFrame,
        period: str = "month",
        price_column: str = "Close"
    ) -> pd.DataFrame:
        """
        Agrega dados por período (dia, semana, mês, ano)
        
        Args:
            df: DataFrame com dados
            period: Período de agregação (day, week, month, year)
            price_column: Coluna de preço
        
        Returns:
            DataFrame agregado
        """
        if not SPARK_AVAILABLE or self.spark is None:
            return self._aggregate_pandas(df, period, price_column)
        
        try:
            spark_df = self.pandas_to_spark(df)
            
            # Adicionar colunas de data
            spark_df = spark_df.withColumn('Year', year(col('Date')))
            spark_df = spark_df.withColumn('Month', month(col('Date')))
            
            # Agregar
            if period == "month":
                agg_df = spark_df.groupBy('Year', 'Month').agg(
                    spark_round(avg(col(price_column)), 2).alias('Avg_Price'),
                    spark_round(spark_max(col(price_column)), 2).alias('Max_Price'),
                    spark_round(spark_min(col(price_column)), 2).alias('Min_Price')
                )
            
            return self.spark_to_pandas(agg_df)
        
        except Exception as e:
            logger.error(f"Erro ao agregar dados: {str(e)}")
            return self._aggregate_pandas(df, period, price_column)
    
    def _aggregate_pandas(
        self,
        df: pd.DataFrame,
        period: str,
        price_column: str
    ) -> pd.DataFrame:
        """Fallback: Agrega dados com Pandas"""
        df_copy = df.copy()
        
        if 'Date' in df_copy.columns:
            df_copy['Date'] = pd.to_datetime(df_copy['Date'])
            
            if period == "month":
                df_copy['Year'] = df_copy['Date'].dt.year
                df_copy['Month'] = df_copy['Date'].dt.month
                
                agg_df = df_copy.groupby(['Year', 'Month'])[price_column].agg([
                    ('Avg_Price', 'mean'),
                    ('Max_Price', 'max'),
                    ('Min_Price', 'min')
                ]).reset_index()
                
                return agg_df
        
        return df_copy
    
    def stop(self):
        """Para a sessão Spark"""
        if self.spark:
            self.spark.stop()
            logger.info("Spark Session encerrada")


if __name__ == "__main__":
    # Exemplo de uso
    processor = SparkDataProcessor()
    
    # Carregar dados de exemplo
    data_path = Path("data/raw/btc_usd_historical.csv")
    if data_path.exists():
        df = pd.read_csv(data_path)
        df['Date'] = pd.to_datetime(df['Date'])
        
        # Calcular médias móveis
        df_with_ma = processor.calculate_moving_averages(df)
        print(f"Colunas após MAs: {df_with_ma.columns.tolist()}")
        
        # Calcular indicadores técnicos
        df_with_indicators = processor.calculate_technical_indicators(df_with_ma)
        print(f"Colunas após indicadores: {df_with_indicators.columns.tolist()}")
        
        # Salvar resultado
        output_path = Path("data/processed/btc_processed.csv")
        df_with_indicators.to_csv(output_path, index=False)
        print(f"Dados processados salvos em: {output_path}")
    
    processor.stop()
