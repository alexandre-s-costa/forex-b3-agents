import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta

class ForexDataProvider:
    """Provedor de dados para o mercado Forex"""
    
    def __init__(self):
        # Pares de moedas comuns no Forex
        self.available_pairs = [
            'EURUSD=X', 'GBPUSD=X', 'USDJPY=X', 'AUDUSD=X', 
            'USDCAD=X', 'USDCHF=X', 'NZDUSD=X'
        ]
        
        # Ativos da B3 (Bolsa Brasileira)
        self.b3_assets = [
            'WINFUT', 'WDOFUT'  # Mini Índice Futuro e Mini Dólar Futuro
        ]
    
    def get_available_pairs(self):
        """Retorna a lista de pares disponíveis"""
        return [pair.replace('=X', '') for pair in self.available_pairs]
    
    def get_ohlc_data(self, symbol, timeframe='1d', days_back=2):
        """
        Obtém dados OHLC para um par de moedas ou ativo B3
        
        Args:
            symbol (str): Par de moedas (ex: 'EURUSD') ou ativo B3 (ex: 'WINFUT')
            timeframe (str): Intervalo de tempo ('1h', '4h', '1d')
            days_back (int): Número de dias para retornar
            
        Returns:
            pandas.DataFrame: Dados OHLC
        """
        # Verifica se é um ativo B3
        if symbol in self.b3_assets:
            # Para ativos B3, usa símbolos específicos do Yahoo Finance
            if symbol == 'WINFUT':
                yf_symbol = '^BVSP'  # Índice Bovespa como proxy para mini índice
            elif symbol == 'WDOFUT':
                yf_symbol = 'USDBRL=X'  # Par USD/BRL como proxy para mini dólar
            else:
                raise ValueError(f"Ativo B3 {symbol} não suportado")
        else:
            # Adiciona o sufixo =X se não estiver presente (para Forex)
            if not symbol.endswith('=X'):
                symbol = f"{symbol}=X"
                
            # Verifica se o símbolo está disponível
            if symbol not in self.available_pairs:
                raise ValueError(f"Par de moedas {symbol} não disponível")
            
            yf_symbol = symbol
        
        # Mapeia timeframe para formato yfinance
        timeframe_map = {
            '1h': '1h',
            '4h': '4h',
            '1d': '1d'
        }
        
        interval = timeframe_map.get(timeframe, '1d')
        
        # Calcula datas de início e fim
        end_date = datetime.now()
        
        # Para intervalos intradiários, precisamos de mais dias para obter os dados corretos
        if interval in ['1h', '4h']:
            # Para dados intradiários, yfinance tem limitações de histórico
            # Adicionamos mais dias para garantir que temos dados suficientes
            start_date = end_date - timedelta(days=max(days_back * 7, 14))  # Mínimo 14 dias
            period = f"{max(days_back * 7, 14)}d"
        else:
            # Para dados diários, usa período fixo para garantir dados
            start_date = end_date - timedelta(days=max(days_back * 3, 7))  # Mínimo 7 dias
            period = f"{max(days_back * 3, 7)}d"
        
        # Obtém os dados do yfinance
        try:
            data = yf.download(
                yf_symbol,
                start=start_date,
                end=end_date,
                interval=interval,
                progress=False,
                auto_adjust=True
            )
            
            # Se não houver dados, retorna DataFrame vazio
            if data.empty:
                return pd.DataFrame()
                
            # Achata as colunas multi-level se necessário
            if isinstance(data.columns, pd.MultiIndex):
                data.columns = [col[0].lower() if col[0] else col[1].lower() for col in data.columns]
            else:
                # Renomeia as colunas para o formato padrão
                data = data.rename(columns={
                    'Open': 'open',
                    'High': 'high',
                    'Low': 'low',
                    'Close': 'close',
                    'Volume': 'volume'
                })
            
            # Para timeframes intradiários, filtra apenas os dias solicitados
            if interval in ['1h', '4h']:
                # Filtra apenas os últimos 'days_back' dias
                cutoff_date = end_date - timedelta(days=days_back)
                # Converte cutoff_date para timezone-aware se necessário
                if data.index.tz is not None and cutoff_date.tzinfo is None:
                    cutoff_date = cutoff_date.replace(tzinfo=data.index.tz)
                elif data.index.tz is None and cutoff_date.tzinfo is not None:
                    cutoff_date = cutoff_date.replace(tzinfo=None)
                data = data[data.index >= cutoff_date]
            
            return data
            
        except Exception as e:
            print(f"Erro ao obter dados para {yf_symbol}: {e}")
            return pd.DataFrame()
    
    def get_current_price(self, symbol):
        """
        Obtém o preço atual de um par de moedas ou ativo B3
        
        Args:
            symbol (str): Par de moedas (ex: 'EURUSD') ou ativo B3 (ex: 'WINFUT')
            
        Returns:
            float: Preço atual
        """
        # Verifica se é um ativo B3
        if symbol in self.b3_assets:
            # Para ativos B3, usa símbolos específicos do Yahoo Finance
            if symbol == 'WINFUT':
                yf_symbol = '^BVSP'  # Índice Bovespa como proxy para mini índice
            elif symbol == 'WDOFUT':
                yf_symbol = 'USDBRL=X'  # Par USD/BRL como proxy para mini dólar
            else:
                raise ValueError(f"Ativo B3 {symbol} não suportado")
        else:
            # Adiciona o sufixo =X se não estiver presente (para Forex)
            if not symbol.endswith('=X'):
                symbol = f"{symbol}=X"
            yf_symbol = symbol
        
        try:
            ticker = yf.Ticker(yf_symbol)
            data = ticker.history(period='1d')
            
            if data.empty:
                return None
                
            return data['Close'].iloc[-1]
            
        except Exception as e:
            print(f"Erro ao obter preço atual para {symbol}: {e}")
            return None
            