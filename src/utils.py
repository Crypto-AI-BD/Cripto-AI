"""
Utilitários auxiliares para o projeto
"""
import pandas as pd
import numpy as np
from pathlib import Path
import logging
from typing import Optional, Dict, Any

logger = logging.getLogger(__name__)


def ensure_datetime(df: pd.DataFrame, date_column: str = 'Date') -> pd.DataFrame:
    """
    Garante que a coluna de data esteja no formato datetime
    
    Args:
        df: DataFrame
        date_column: Nome da coluna de data
    
    Returns:
        DataFrame com coluna de data convertida
    """
    df_copy = df.copy()
    
    if date_column in df_copy.columns:
        if not pd.api.types.is_datetime64_any_dtype(df_copy[date_column]):
            df_copy[date_column] = pd.to_datetime(df_copy[date_column])
    
    return df_copy


def remove_outliers(
    df: pd.DataFrame,
    column: str,
    method: str = 'iqr',
    threshold: float = 1.5
) -> pd.DataFrame:
    """
    Remove outliers de uma coluna
    
    Args:
        df: DataFrame
        column: Nome da coluna
        method: Método de detecção ('iqr' ou 'zscore')
        threshold: Limiar para remoção
    
    Returns:
        DataFrame sem outliers
    """
    df_copy = df.copy()
    
    if method == 'iqr':
        Q1 = df_copy[column].quantile(0.25)
        Q3 = df_copy[column].quantile(0.75)
        IQR = Q3 - Q1
        
        lower_bound = Q1 - threshold * IQR
        upper_bound = Q3 + threshold * IQR
        
        df_copy = df_copy[
            (df_copy[column] >= lower_bound) &
            (df_copy[column] <= upper_bound)
        ]
    
    elif method == 'zscore':
        z_scores = np.abs((df_copy[column] - df_copy[column].mean()) / df_copy[column].std())
        df_copy = df_copy[z_scores < threshold]
    
    logger.info(f"Outliers removidos: {len(df) - len(df_copy)} registros")
    
    return df_copy


def fill_missing_values(
    df: pd.DataFrame,
    method: str = 'ffill',
    columns: Optional[list] = None
) -> pd.DataFrame:
    """
    Preenche valores faltantes
    
    Args:
        df: DataFrame
        method: Método de preenchimento ('ffill', 'bfill', 'mean', 'median')
        columns: Lista de colunas para preencher (None = todas)
    
    Returns:
        DataFrame com valores preenchidos
    """
    df_copy = df.copy()
    
    if columns is None:
        columns = df_copy.columns
    
    for col in columns:
        if col in df_copy.columns:
            if method == 'ffill':
                df_copy[col].fillna(method='ffill', inplace=True)
            elif method == 'bfill':
                df_copy[col].fillna(method='bfill', inplace=True)
            elif method == 'mean':
                df_copy[col].fillna(df_copy[col].mean(), inplace=True)
            elif method == 'median':
                df_copy[col].fillna(df_copy[col].median(), inplace=True)
    
    return df_copy


def calculate_percentage_change(
    df: pd.DataFrame,
    column: str,
    periods: int = 1
) -> pd.Series:
    """
    Calcula a variação percentual
    
    Args:
        df: DataFrame
        column: Coluna para calcular variação
        periods: Número de períodos
    
    Returns:
        Serie com variações percentuais
    """
    return df[column].pct_change(periods=periods) * 100


def get_data_summary(df: pd.DataFrame) -> Dict[str, Any]:
    """
    Retorna um resumo estatístico dos dados
    
    Args:
        df: DataFrame
    
    Returns:
        Dicionário com estatísticas
    """
    summary = {
        'rows': len(df),
        'columns': len(df.columns),
        'missing_values': df.isnull().sum().to_dict(),
        'dtypes': {col: str(dtype) for col, dtype in df.dtypes.items()},
        'numeric_summary': df.describe().to_dict() if not df.select_dtypes(include=[np.number]).empty else {}
    }
    
    return summary


def save_processed_data(
    df: pd.DataFrame,
    filename: str,
    output_dir: str = "data/processed",
    format: str = "csv"
) -> Path:
    """
    Salva dados processados
    
    Args:
        df: DataFrame para salvar
        filename: Nome do arquivo
        output_dir: Diretório de saída
        format: Formato do arquivo ('csv', 'parquet', 'json')
    
    Returns:
        Path do arquivo salvo
    """
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    
    file_path = output_path / f"{filename}.{format}"
    
    if format == "csv":
        df.to_csv(file_path, index=False)
    elif format == "parquet":
        df.to_parquet(file_path, index=False)
    elif format == "json":
        df.to_json(file_path, orient='records', date_format='iso')
    
    logger.info(f"Dados salvos em: {file_path}")
    
    return file_path
