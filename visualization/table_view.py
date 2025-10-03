import pandas as pd
from typing import Dict, List, Any

class TableView:
    """Componente para visualização tabular de dados OHLC"""
    
    def __init__(self):
        pass
    
    def format_ohlc_data(self, data: Dict[str, Any]) -> pd.DataFrame:
        """
        Formata os dados OHLC para exibição em tabela
        
        Args:
            data (Dict): Dados OHLC obtidos do agente Forex
            
        Returns:
            pd.DataFrame: DataFrame formatado para exibição
        """
        if "error" in data:
            # Retorna DataFrame vazio em caso de erro
            return pd.DataFrame()
        
        # Converte os dados para DataFrame
        df = pd.DataFrame(data["data"])
        
        # Renomeia as colunas para o formato de exibição
        column_mapping = {
            "Datetime": "Data/Hora",
            "Date": "Data",
            "open": "Abertura",
            "high": "Máxima",
            "low": "Mínima",
            "close": "Fechamento",
            "volume": "Volume"
        }
        
        # Identifica a coluna de data/hora
        date_column = "Datetime" if "Datetime" in df.columns else "Date"
        
        # Formata a coluna de data/hora
        if date_column in df.columns:
            df[date_column] = pd.to_datetime(df[date_column])
            
            # Remove fins de semana (sábado=5, domingo=6)
            # Mantém apenas dias úteis (segunda=0 até sexta=4)
            df = df[df[date_column].dt.weekday < 5]
            
            if date_column == "Datetime":
                df[date_column] = df[date_column].dt.strftime("%Y-%m-%d %H:%M")
            else:
                df[date_column] = df[date_column].dt.strftime("%Y-%m-%d")
        
        # Renomeia as colunas
        df = df.rename(columns=column_mapping)
        
        # Arredonda os valores numéricos para 5 casas decimais
        for col in ["Abertura", "Máxima", "Mínima", "Fechamento"]:
            if col in df.columns:
                df[col] = df[col].round(5)
        
        # Seleciona apenas as colunas relevantes
        relevant_columns = [col for col in ["Data/Hora", "Data", "Abertura", "Máxima", "Mínima", "Fechamento", "Volume"] if col in df.columns]
        df = df[relevant_columns]
        
        return df
    
    def get_html_table(self, data: Dict[str, Any]) -> str:
        """
        Gera uma tabela HTML a partir dos dados OHLC
        
        Args:
            data (Dict): Dados OHLC obtidos do agente Forex
            
        Returns:
            str: Tabela HTML
        """
        if "error" in data:
            return f"<div class='error'>Erro: {data['error']}</div>"
        
        df = self.format_ohlc_data(data)
        
        if df.empty:
            return "<div class='error'>Não há dados disponíveis</div>"
        
        # Gera a tabela HTML com estilo
        html = df.to_html(
            classes="table table-striped table-hover table-bordered",
            index=False
        )
        
        return html
    
    def get_summary_stats(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Calcula estatísticas resumidas dos dados OHLC
        
        Args:
            data (Dict): Dados OHLC obtidos do agente Forex
            
        Returns:
            Dict: Estatísticas resumidas
        """
        if "error" in data:
            return {"error": data["error"]}
        
        # Converte os dados para DataFrame
        df = pd.DataFrame(data["data"])
        
        if df.empty:
            return {"error": "Não há dados disponíveis"}
        
        # Identifica a coluna de data/hora e aplica filtragem de fins de semana
        date_column = "Datetime" if "Datetime" in df.columns else "Date"
        if date_column in df.columns:
            df[date_column] = pd.to_datetime(df[date_column])
            
            # Remove fins de semana (sábado=5, domingo=6)
            # Mantém apenas dias úteis (segunda=0 até sexta=4)
            df = df[df[date_column].dt.weekday < 5]
            
            if df.empty:
                return {"error": "Não há dados disponíveis após filtragem"}
        
        # Calcula estatísticas básicas
        stats = {
            "symbol": data["symbol"],
            "timeframe": data["timeframe"],
            "period_start": df["Datetime"].iloc[0] if "Datetime" in df.columns else df["Date"].iloc[0],
            "period_end": df["Datetime"].iloc[-1] if "Datetime" in df.columns else df["Date"].iloc[-1],
            "open_first": df["open"].iloc[0],
            "close_last": df["close"].iloc[-1],
            "high_max": df["high"].max(),
            "low_min": df["low"].min(),
            "change": df["close"].iloc[-1] - df["open"].iloc[0],
            "change_pct": (df["close"].iloc[-1] - df["open"].iloc[0]) / df["open"].iloc[0] * 100
        }
        
        return stats
        