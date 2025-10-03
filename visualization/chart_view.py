import pandas as pd
import plotly.graph_objects as go
from typing import Dict, Any

class ChartView:
    """Componente para visualização de gráficos de candlestick"""
    
    def __init__(self):
        pass
    
    def create_candlestick_chart(self, data: Dict[str, Any]) -> go.Figure:
        """
        Cria um gráfico de candlestick a partir dos dados OHLC
        
        Args:
            data (Dict): Dados OHLC obtidos do agente Forex
            
        Returns:
            go.Figure: Figura do gráfico de candlestick
        """
        if "error" in data:
            # Retorna uma figura vazia em caso de erro
            fig = go.Figure()
            fig.add_annotation(
                text=f"Erro: {data['error']}",
                xref="paper", yref="paper",
                x=0.5, y=0.5,
                showarrow=False
            )
            return fig
        
        # Converte os dados para DataFrame
        df = pd.DataFrame(data["data"])
        
        if df.empty:
            fig = go.Figure()
            fig.add_annotation(
                text="Não há dados disponíveis",
                xref="paper", yref="paper",
                x=0.5, y=0.5,
                showarrow=False
            )
            return fig
        
        # Identifica a coluna de data/hora
        date_column = "Datetime" if "Datetime" in df.columns else "Date"
        
        # Converte para datetime se necessário
        if date_column in df.columns:
            df[date_column] = pd.to_datetime(df[date_column])
            
            # Remove fins de semana (sábado=5, domingo=6)
            # Mantém apenas dias úteis (segunda=0 até sexta=4)
            df = df[df[date_column].dt.weekday < 5]
        
        # Cria o gráfico de candlestick
        fig = go.Figure(data=[go.Candlestick(
            x=df[date_column],
            open=df['open'],
            high=df['high'],
            low=df['low'],
            close=df['close'],
            name=data["symbol"]
        )])
        
        # Configura o layout do gráfico
        fig.update_layout(
            title=f"{data['symbol']} - {data['timeframe']}",
            xaxis_title="Data/Hora",
            yaxis_title="Preço",
            xaxis_rangeslider_visible=False,
            template="plotly_white"
        )
        
        return fig
    
    def get_html_chart(self, data: Dict[str, Any]) -> str:
        """
        Gera o HTML do gráfico de candlestick
        
        Args:
            data (Dict): Dados OHLC obtidos do agente Forex
            
        Returns:
            str: HTML do gráfico
        """
        fig = self.create_candlestick_chart(data)
        
        # Converte a figura para HTML
        html = fig.to_html(
            full_html=False,
            include_plotlyjs='cdn',
            config={'responsive': True}
        )
        
        return html
        