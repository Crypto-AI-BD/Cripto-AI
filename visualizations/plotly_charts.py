"""
Visualizações interativas com Plotly
Gráficos para análise de criptomoedas
"""
import pandas as pd
import numpy as np
from pathlib import Path
import logging
from typing import Optional, List, Dict, Any

logger = logging.getLogger(__name__)

try:
    import plotly.graph_objects as go
    from plotly.subplots import make_subplots
    import plotly.express as px
    PLOTLY_AVAILABLE = True
except ImportError:
    logger.warning("Plotly não está disponível")
    PLOTLY_AVAILABLE = False


class CryptoVisualizer:
    """Classe para criação de visualizações de criptomoedas - Tema Moderno"""
    
    def __init__(self, theme: str = 'plotly_dark'):
        self.theme = theme
        self.default_width = 1200
        self.default_height = 600
        
        # Cores Modernas
        self.colors = {
            'primary_blue': '#0066FF',
            'accent_cyan': '#00B4D8',
            'success_green': '#06D6A0',
            'warning_orange': '#FF6B35',
            'purple': '#7209B7',
            'danger_red': '#EF476F',
        }
        
        # Layout padrão Moderno
        self.default_layout = {
            'plot_bgcolor': 'rgba(26, 29, 41, 0.8)',
            'paper_bgcolor': 'rgba(19, 21, 31, 0.9)',
            'font': {
                'family': 'Inter, sans-serif',
                'color': '#E8E9EB',
                'size': 12
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
                }
            }
        }
    
    def plot_price_history(
        self,
        df: pd.DataFrame,
        date_col: str = 'Date',
        price_col: str = 'Close',
        title: str = 'Histórico de Preços',
        show_ma: bool = True,
        ma_windows: List[int] = [7, 30, 90]
    ):
        """
        Cria gráfico de linha do histórico de preços
        
        Args:
            df: DataFrame com dados
            date_col: Coluna de data
            price_col: Coluna de preço
            title: Título do gráfico
            show_ma: Mostrar médias móveis
            ma_windows: Janelas das médias móveis
        
        Returns:
            Figura Plotly
        """
        if not PLOTLY_AVAILABLE:
            raise ImportError("Plotly não está disponível")
        
        fig = go.Figure()
        
        # Linha de preço
        fig.add_trace(go.Scatter(
            x=df[date_col],
            y=df[price_col],
            mode='lines',
            name='Price',
            line=dict(color=self.colors['primary_blue'], width=2.5),
            fill='tozeroy',
            fillcolor='rgba(0, 102, 255, 0.1)',
            hovertemplate='<b>Price:</b> $%{y:,.2f}<br><b>Date:</b> %{x}<extra></extra>'
        ))
        
        # Médias móveis
        if show_ma:
            ma_colors = [self.colors['success_green'], self.colors['purple'], self.colors['warning_orange']]
            for i, window in enumerate(ma_windows):
                ma_col = f'MA_{window}'
                if ma_col in df.columns:
                    fig.add_trace(go.Scatter(
                        x=df[date_col],
                        y=df[ma_col],
                        mode='lines',
                        name=f'MA {window}d',
                        line=dict(color=ma_colors[i % len(ma_colors)], width=1.8),
                        hovertemplate=f'<b>MA {window}d:</b> $%{{y:,.2f}}<extra></extra>'
                    ))
        
        # Aplicar layout moderno
        fig.update_layout(
            title=dict(
                text=title,
                font=dict(family='Poppins', size=18, color=self.colors['primary_blue']),
                x=0.5,
                xanchor='center'
            ),
            xaxis_title='Date',
            yaxis_title='Price (USD)',
            template=self.theme,
            width=self.default_width,
            height=self.default_height,
            hovermode='x unified',
            **self.default_layout
        )
        
        return fig
    
    def plot_candlestick(
        self,
        df: pd.DataFrame,
        date_col: str = 'Date',
        title: str = 'Candlestick Chart'
    ):
        """
        Cria gráfico de candlestick
        
        Args:
            df: DataFrame com dados (Open, High, Low, Close)
            date_col: Coluna de data
            title: Título do gráfico
        
        Returns:
            Figura Plotly
        """
        if not PLOTLY_AVAILABLE:
            raise ImportError("Plotly não está disponível")
        
        fig = go.Figure(data=[go.Candlestick(
            x=df[date_col],
            open=df['Open'],
            high=df['High'],
            low=df['Low'],
            close=df['Close'],
            name='OHLC'
        )])
        
        fig.update_layout(
            title=title,
            xaxis_title='Data',
            yaxis_title='Preço (USD)',
            template=self.theme,
            width=self.default_width,
            height=self.default_height,
            xaxis_rangeslider_visible=False
        )
        
        return fig
    
    def plot_volume(
        self,
        df: pd.DataFrame,
        date_col: str = 'Date',
        volume_col: str = 'Volume',
        title: str = 'Volume de Negociação'
    ):
        """
        Cria gráfico de volume
        
        Args:
            df: DataFrame com dados
            date_col: Coluna de data
            volume_col: Coluna de volume
            title: Título do gráfico
        
        Returns:
            Figura Plotly
        """
        if not PLOTLY_AVAILABLE:
            raise ImportError("Plotly não está disponível")
        
        fig = go.Figure()
        
        # Definir cores baseado na variação de preço
        colors = ['red' if row['Close'] < row['Open'] else 'green' 
                 for _, row in df.iterrows()]
        
        fig.add_trace(go.Bar(
            x=df[date_col],
            y=df[volume_col],
            name='Volume',
            marker_color=colors
        ))
        
        fig.update_layout(
            title=title,
            xaxis_title='Data',
            yaxis_title='Volume',
            template=self.theme,
            width=self.default_width,
            height=400,
            showlegend=False
        )
        
        return fig
    
    def plot_forecast(
        self,
        df_historical: pd.DataFrame,
        df_forecast: pd.DataFrame,
        date_col: str = 'Date',
        actual_col: str = 'Close',
        pred_col: str = 'Predicted',
        title: str = 'Previsão de Preços'
    ):
        """
        Cria gráfico com dados históricos e previsões
        
        Args:
            df_historical: DataFrame com dados históricos
            df_forecast: DataFrame com previsões
            date_col: Coluna de data
            actual_col: Coluna de valores reais
            pred_col: Coluna de previsões
            title: Título do gráfico
        
        Returns:
            Figura Plotly
        """
        if not PLOTLY_AVAILABLE:
            raise ImportError("Plotly não está disponível")
        
        fig = go.Figure()
        
        # Dados históricos
        fig.add_trace(go.Scatter(
            x=df_historical[date_col],
            y=df_historical[actual_col],
            mode='lines',
            name='Histórico',
            line=dict(color='#2196F3', width=2)
        ))
        
        # Previsões
        fig.add_trace(go.Scatter(
            x=df_forecast[date_col],
            y=df_forecast[pred_col],
            mode='lines+markers',
            name='Previsão',
            line=dict(color='#FF5722', width=2, dash='dash'),
            marker=dict(size=8)
        ))
        
        # Intervalos de confiança (se disponível)
        if 'Lower_Bound' in df_forecast.columns and 'Upper_Bound' in df_forecast.columns:
            fig.add_trace(go.Scatter(
                x=df_forecast[date_col],
                y=df_forecast['Upper_Bound'],
                mode='lines',
                name='Limite Superior',
                line=dict(width=0),
                showlegend=False
            ))
            
            fig.add_trace(go.Scatter(
                x=df_forecast[date_col],
                y=df_forecast['Lower_Bound'],
                mode='lines',
                name='Intervalo de Confiança',
                line=dict(width=0),
                fillcolor='rgba(255, 87, 34, 0.2)',
                fill='tonexty'
            ))
        
        fig.update_layout(
            title=title,
            xaxis_title='Data',
            yaxis_title='Preço (USD)',
            template=self.theme,
            width=self.default_width,
            height=self.default_height,
            hovermode='x unified'
        )
        
        return fig
    
    def plot_returns(
        self,
        df: pd.DataFrame,
        date_col: str = 'Date',
        returns_col: str = 'Daily_Return',
        title: str = 'Retornos Diários'
    ):
        """
        Cria gráfico de retornos
        
        Args:
            df: DataFrame com dados
            date_col: Coluna de data
            returns_col: Coluna de retornos
            title: Título do gráfico
        
        Returns:
            Figura Plotly
        """
        if not PLOTLY_AVAILABLE:
            raise ImportError("Plotly não está disponível")
        
        colors = ['green' if val > 0 else 'red' for val in df[returns_col]]
        
        fig = go.Figure()
        
        fig.add_trace(go.Bar(
            x=df[date_col],
            y=df[returns_col],
            name='Retorno',
            marker_color=colors
        ))
        
        fig.update_layout(
            title=title,
            xaxis_title='Data',
            yaxis_title='Retorno (%)',
            template=self.theme,
            width=self.default_width,
            height=500,
            showlegend=False
        )
        
        return fig
    
    def plot_correlation_heatmap(
        self,
        df: pd.DataFrame,
        columns: Optional[List[str]] = None,
        title: str = 'Matriz de Correlação'
    ):
        """
        Cria heatmap de correlação
        
        Args:
            df: DataFrame com dados
            columns: Colunas para incluir (None = todas numéricas)
            title: Título do gráfico
        
        Returns:
            Figura Plotly
        """
        if not PLOTLY_AVAILABLE:
            raise ImportError("Plotly não está disponível")
        
        if columns is None:
            columns = df.select_dtypes(include=[np.number]).columns.tolist()
        
        corr_matrix = df[columns].corr()
        
        fig = go.Figure(data=go.Heatmap(
            z=corr_matrix.values,
            x=corr_matrix.columns,
            y=corr_matrix.columns,
            colorscale='RdBu',
            zmid=0,
            text=np.round(corr_matrix.values, 2),
            texttemplate='%{text}',
            textfont={"size": 10},
            colorbar=dict(title="Correlação")
        ))
        
        fig.update_layout(
            title=title,
            template=self.theme,
            width=800,
            height=800
        )
        
        return fig
    
    def plot_comparison(
        self,
        dfs: Dict[str, pd.DataFrame],
        date_col: str = 'Date',
        value_col: str = 'Close',
        title: str = 'Comparação de Criptomoedas'
    ):
        """
        Compara múltiplas criptomoedas
        
        Args:
            dfs: Dicionário {nome: DataFrame}
            date_col: Coluna de data
            value_col: Coluna de valor
            title: Título do gráfico
        
        Returns:
            Figura Plotly
        """
        if not PLOTLY_AVAILABLE:
            raise ImportError("Plotly não está disponível")
        
        fig = go.Figure()
        
        colors = ['#2196F3', '#FF5722', '#4CAF50', '#FFC107', '#9C27B0']
        
        for i, (name, df) in enumerate(dfs.items()):
            # Normalizar para comparação
            normalized = (df[value_col] / df[value_col].iloc[0]) * 100
            
            fig.add_trace(go.Scatter(
                x=df[date_col],
                y=normalized,
                mode='lines',
                name=name,
                line=dict(color=colors[i % len(colors)], width=2)
            ))
        
        fig.update_layout(
            title=title,
            xaxis_title='Data',
            yaxis_title='Variação Normalizada (%)',
            template=self.theme,
            width=self.default_width,
            height=self.default_height,
            hovermode='x unified'
        )
        
        return fig
    
    def plot_dashboard(
        self,
        df: pd.DataFrame,
        date_col: str = 'Date'
    ):
        """
        Cria dashboard completo com múltiplos gráficos
        
        Args:
            df: DataFrame com dados
            date_col: Coluna de data
        
        Returns:
            Figura Plotly
        """
        if not PLOTLY_AVAILABLE:
            raise ImportError("Plotly não está disponível")
        
        fig = make_subplots(
            rows=3, cols=1,
            subplot_titles=('Preço e Médias Móveis', 'Volume', 'Retornos Diários'),
            row_heights=[0.5, 0.25, 0.25],
            vertical_spacing=0.08
        )
        
        # 1. Preço e MAs
        fig.add_trace(go.Scatter(
            x=df[date_col], y=df['Close'],
            mode='lines', name='Preço',
            line=dict(color='#2196F3', width=2)
        ), row=1, col=1)
        
        if 'MA_7' in df.columns:
            fig.add_trace(go.Scatter(
                x=df[date_col], y=df['MA_7'],
                mode='lines', name='MA 7d',
                line=dict(color='#FFC107', width=1, dash='dash')
            ), row=1, col=1)
        
        if 'MA_30' in df.columns:
            fig.add_trace(go.Scatter(
                x=df[date_col], y=df['MA_30'],
                mode='lines', name='MA 30d',
                line=dict(color='#4CAF50', width=1, dash='dash')
            ), row=1, col=1)
        
        # 2. Volume
        if 'Volume' in df.columns:
            colors = ['red' if row['Close'] < row['Open'] else 'green' 
                     for _, row in df.iterrows()]
            
            fig.add_trace(go.Bar(
                x=df[date_col], y=df['Volume'],
                name='Volume', marker_color=colors,
                showlegend=False
            ), row=2, col=1)
        
        # 3. Retornos
        if 'Daily_Return' in df.columns:
            returns_colors = ['green' if val > 0 else 'red' 
                            for val in df['Daily_Return']]
            
            fig.add_trace(go.Bar(
                x=df[date_col], y=df['Daily_Return'],
                name='Retorno', marker_color=returns_colors,
                showlegend=False
            ), row=3, col=1)
        
        fig.update_xaxes(title_text="Data", row=3, col=1)
        fig.update_yaxes(title_text="Preço (USD)", row=1, col=1)
        fig.update_yaxes(title_text="Volume", row=2, col=1)
        fig.update_yaxes(title_text="Retorno (%)", row=3, col=1)
        
        fig.update_layout(
            template=self.theme,
            width=self.default_width,
            height=1000,
            showlegend=True,
            hovermode='x unified'
        )
        
        return fig
    
    def save_figure(self, fig, filename: str, output_dir: str = "visualizations"):
        """
        Salva figura em arquivo
        
        Args:
            fig: Figura Plotly
            filename: Nome do arquivo
            output_dir: Diretório de saída
        """
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)
        
        file_path = output_path / filename
        
        if filename.endswith('.html'):
            fig.write_html(str(file_path))
        elif filename.endswith('.png'):
            fig.write_image(str(file_path))
        elif filename.endswith('.jpg'):
            fig.write_image(str(file_path))
        
        logger.info(f"Figura salva em: {file_path}")


if __name__ == "__main__":
    # Exemplo de uso
    if PLOTLY_AVAILABLE:
        data_path = Path("data/raw/btc_usd_historical.csv")
        if data_path.exists():
            df = pd.read_csv(data_path)
            df['Date'] = pd.to_datetime(df['Date'])
            
            visualizer = CryptoVisualizer()
            
            # Criar gráfico de preços
            fig = visualizer.plot_price_history(df)
            visualizer.save_figure(fig, 'price_history.html')
            
            print("Visualização criada com sucesso!")
    else:
        print("Plotly não está disponível")
