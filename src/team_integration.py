"""
Exemplos de Integração com Outras Equipes
Desafio: Integrar dados de outros projetos
"""

import pandas as pd
import numpy as np
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.data_ingestion import CryptoDataIngestion
from src.spark_processor import SparkDataProcessor
from visualizations.plotly_charts import CryptoVisualizer


class TeamIntegration:
    """Classe para integrar dados de outras equipes"""
    
    def __init__(self):
        self.ingestion = CryptoDataIngestion()
        self.processor = SparkDataProcessor()
        self.visualizer = CryptoVisualizer()
    
    def integrate_team_data(
        self,
        team_csv_path: str,
        our_data_path: str = None
    ) -> pd.DataFrame:
        """
        Integra dados de outra equipe com nossos dados
        
        Args:
            team_csv_path: Caminho do CSV da outra equipe
            our_data_path: Caminho dos nossos dados (None = buscar do Yahoo)
        
        Returns:
            DataFrame combinado
        """
        # Carregar dados da outra equipe
        print(f"📥 Carregando dados da equipe: {team_csv_path}")
        df_team = pd.read_csv(team_csv_path)
        df_team['Date'] = pd.to_datetime(df_team['Date'])
        
        # Carregar nossos dados
        if our_data_path:
            print(f"📥 Carregando nossos dados: {our_data_path}")
            df_ours = pd.read_csv(our_data_path)
            df_ours['Date'] = pd.to_datetime(df_ours['Date'])
        else:
            print("📥 Buscando nossos dados do Yahoo Finance...")
            df_ours = self.ingestion.fetch_from_yahoo("BTC-USD", period="5y")
        
        # Combinar dados
        print("🔄 Combinando dados...")
        df_combined = self.merge_datasets(df_ours, df_team)
        
        print(f"✅ Dados integrados: {len(df_combined)} registros")
        return df_combined
    
    def merge_datasets(
        self,
        df1: pd.DataFrame,
        df2: pd.DataFrame,
        merge_on: str = 'Date',
        how: str = 'inner'
    ) -> pd.DataFrame:
        """
        Combina dois datasets
        
        Args:
            df1: Primeiro DataFrame
            df2: Segundo DataFrame
            merge_on: Coluna para merge
            how: Tipo de merge ('inner', 'outer', 'left', 'right')
        
        Returns:
            DataFrame combinado
        """
        # Garantir que ambos têm a coluna de merge
        if merge_on not in df1.columns or merge_on not in df2.columns:
            raise ValueError(f"Coluna {merge_on} não encontrada em ambos DataFrames")
        
        # Renomear colunas conflitantes
        df1_cols = [col if col == merge_on else f"{col}_team1" for col in df1.columns]
        df2_cols = [col if col == merge_on else f"{col}_team2" for col in df2.columns]
        
        df1.columns = df1_cols
        df2.columns = df2_cols
        
        # Fazer merge
        df_merged = pd.merge(df1, df2, on=merge_on, how=how)
        
        return df_merged
    
    def analyze_correlation(
        self,
        df_combined: pd.DataFrame,
        col1: str,
        col2: str
    ) -> dict:
        """
        Analisa correlação entre duas variáveis
        
        Args:
            df_combined: DataFrame combinado
            col1: Primeira coluna
            col2: Segunda coluna
        
        Returns:
            Dicionário com análise de correlação
        """
        # Calcular correlação
        correlation = df_combined[[col1, col2]].corr().iloc[0, 1]
        
        # Análise
        if abs(correlation) > 0.7:
            strength = "Forte"
        elif abs(correlation) > 0.4:
            strength = "Moderada"
        else:
            strength = "Fraca"
        
        direction = "Positiva" if correlation > 0 else "Negativa"
        
        return {
            'correlation': round(correlation, 4),
            'strength': strength,
            'direction': direction,
            'col1': col1,
            'col2': col2
        }
    
    def create_combined_analysis(
        self,
        df_combined: pd.DataFrame,
        output_path: str = "data/processed/combined_analysis.csv"
    ):
        """
        Cria análise completa dos dados combinados
        
        Args:
            df_combined: DataFrame combinado
            output_path: Caminho para salvar análise
        """
        print("📊 Processando dados combinados...")
        
        # Processar com Spark
        df_processed = self.processor.calculate_moving_averages(df_combined)
        df_processed = self.processor.calculate_technical_indicators(df_processed)
        
        # Salvar
        df_processed.to_csv(output_path, index=False)
        print(f"✅ Análise salva em: {output_path}")
        
        return df_processed
    
    def visualize_comparison(
        self,
        df_combined: pd.DataFrame,
        col1: str,
        col2: str,
        title: str = "Comparação de Dados"
    ):
        """
        Cria visualização comparativa
        
        Args:
            df_combined: DataFrame combinado
            col1: Primeira coluna para comparar
            col2: Segunda coluna para comparar
            title: Título do gráfico
        """
        import plotly.graph_objects as go
        
        fig = go.Figure()
        
        # Normalizar dados para comparação
        df_combined[f'{col1}_norm'] = (df_combined[col1] / df_combined[col1].iloc[0]) * 100
        df_combined[f'{col2}_norm'] = (df_combined[col2] / df_combined[col2].iloc[0]) * 100
        
        # Adicionar traces
        fig.add_trace(go.Scatter(
            x=df_combined['Date'],
            y=df_combined[f'{col1}_norm'],
            mode='lines',
            name=col1,
            line=dict(color='#2196F3', width=2)
        ))
        
        fig.add_trace(go.Scatter(
            x=df_combined['Date'],
            y=df_combined[f'{col2}_norm'],
            mode='lines',
            name=col2,
            line=dict(color='#FF5722', width=2)
        ))
        
        fig.update_layout(
            title=title,
            xaxis_title='Data',
            yaxis_title='Variação Normalizada (%)',
            template='plotly_dark',
            width=1200,
            height=600
        )
        
        # Salvar
        output_file = "visualizations/team_comparison.html"
        fig.write_html(output_file)
        print(f"✅ Visualização salva em: {output_file}")
        
        return fig


# Exemplos de uso
if __name__ == "__main__":
    
    # Criar instância
    integration = TeamIntegration()
    
    # Exemplo 1: Integrar dados de CSV externo
    print("\n=== Exemplo 1: Integrar CSV externo ===\n")
    
    # Simular dados de outra equipe
    example_team_data = {
        'Date': pd.date_range(start='2020-01-01', periods=100, freq='D'),
        'Price': np.random.uniform(30000, 40000, 100),
        'Metric_X': np.random.uniform(0, 100, 100)
    }
    df_example = pd.DataFrame(example_team_data)
    df_example.to_csv("data/raw/example_team_data.csv", index=False)
    
    # Integrar
    df_combined = integration.integrate_team_data(
        team_csv_path="data/raw/example_team_data.csv"
    )
    
    print(f"\nColunas combinadas: {df_combined.columns.tolist()}")
    print(f"Shape: {df_combined.shape}")
    
    # Exemplo 2: Analisar correlação
    print("\n=== Exemplo 2: Análise de Correlação ===\n")
    
    if 'Close_team1' in df_combined.columns and 'Price_team2' in df_combined.columns:
        correlation_analysis = integration.analyze_correlation(
            df_combined,
            'Close_team1',
            'Price_team2'
        )
        
        print(f"Correlação: {correlation_analysis['correlation']}")
        print(f"Força: {correlation_analysis['strength']}")
        print(f"Direção: {correlation_analysis['direction']}")
    
    # Exemplo 3: Criar análise combinada
    print("\n=== Exemplo 3: Análise Combinada ===\n")
    
    df_analysis = integration.create_combined_analysis(df_combined)
    
    print(f"Análise completa com {len(df_analysis.columns)} colunas")
    
    # Exemplo 4: Visualização comparativa
    print("\n=== Exemplo 4: Visualização Comparativa ===\n")
    
    if 'Close_team1' in df_combined.columns and 'Price_team2' in df_combined.columns:
        fig = integration.visualize_comparison(
            df_combined,
            'Close_team1',
            'Price_team2',
            title="Comparação: Nosso Projeto vs Equipe 2"
        )
    
    print("\n✅ Exemplos de integração concluídos!")
    print("\n📝 Instruções para integração real:")
    print("1. Obtenha o CSV da outra equipe")
    print("2. Verifique as colunas (Date, valores numéricos)")
    print("3. Execute: integration.integrate_team_data('caminho/arquivo.csv')")
    print("4. Analise correlações e crie visualizações")
