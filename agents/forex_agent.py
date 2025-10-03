from agno.agent import Agent
from agno.models.perplexity import Perplexity
from agno.tools import tool
import pandas as pd
from typing import Dict, List, Any, Optional
import json

from data.forex_data import ForexDataProvider

class ForexTools:
    """Ferramentas para interação com dados do mercado Forex"""
    
    def __init__(self):
        self.data_provider = ForexDataProvider()
    
    @tool
    def get_available_pairs(self) -> List[str]:
        """Retorna a lista de pares de moedas disponíveis"""
        return self.data_provider.get_available_pairs()
    
    @tool
    def get_ohlc_data(self, symbol: str, timeframe: str = '1d', days_back: int = 2) -> Dict[str, Any]:
        """
        Obtém dados OHLC para um par de moedas
        
        Args:
            symbol (str): Par de moedas (ex: 'EURUSD')
            timeframe (str): Intervalo de tempo ('1h', '4h', '1d')
            days_back (int): Número de dias para retornar
            
        Returns:
            Dict: Dados OHLC em formato JSON
        """
        data = self.data_provider.get_ohlc_data(symbol, timeframe, days_back)
        
        if data.empty:
            return {"error": f"Não foi possível obter dados para {symbol}"}
        
        # Converte o DataFrame para o formato JSON
        data_json = data.reset_index().to_dict(orient='records')
        
        return {
            "symbol": symbol,
            "timeframe": timeframe,
            "data": data_json
        }
    
    @tool
    def get_current_price(self, symbol: str) -> Dict[str, Any]:
        """
        Obtém o preço atual de um par de moedas
        
        Args:
            symbol (str): Par de moedas (ex: 'EURUSD')
            
        Returns:
            Dict: Preço atual em formato JSON
        """
        price = self.data_provider.get_current_price(symbol)
        
        if price is None:
            return {"error": f"Não foi possível obter o preço atual para {symbol}"}
        
        return {
            "symbol": symbol,
            "price": price
        }

class ForexAgent:
    """Agente para análise de mercado Forex"""
    
    def __init__(self, model_id: str = "llama-3.1-sonar-small-128k-online"):
        """
        Inicializa o agente Forex
        
        Args:
            model_id (str): ID do modelo Perplexity a ser utilizado
        """
        self.tools = ForexTools()
        
        # Instruções para o agente
        self.system_prompt = """
        Você é um agente especializado em análise de mercado Forex.
        Sua função é fornecer informações precisas sobre pares de moedas,
        incluindo preços atuais e históricos, além de análises básicas.
        
        Utilize as ferramentas disponíveis para obter dados do mercado e
        responda às consultas de forma clara e objetiva.
        """
        
        # Inicializa o agente com o modelo Perplexity e as ferramentas Forex
        self.agent = Agent(
            model=Perplexity(id=model_id),
            tools=[self.tools],
            markdown=True
        )
        
        # Adiciona o prompt do sistema como contexto adicional
        self.agent.additional_context = self.system_prompt
    def get_forex_data(self, symbol: str, timeframe: str = '1d', days_back: int = 2) -> Dict[str, Any]:
        """
        Obtém dados Forex usando o agente
        
        Args:
            symbol (str): Par de moedas (ex: 'EURUSD')
            timeframe (str): Intervalo de tempo ('1h', '4h', '1d')
            days_back (int): Número de dias para retornar
            
        Returns:
            Dict: Dados Forex
        """
        # Usa diretamente a ferramenta para obter os dados
        # Isso é mais eficiente do que passar pelo LLM para dados brutos
        data = self.tools.data_provider.get_ohlc_data(symbol, timeframe, days_back)
        
        if data.empty:
            return {"error": f"Não foi possível obter dados para {symbol}"}
        
        # Converte o DataFrame para o formato JSON
        data_json = data.reset_index().to_dict(orient='records')
        
        return {
            "symbol": symbol,
            "timeframe": timeframe,
            "data": data_json
        }
    
    def get_available_pairs(self) -> List[str]:
        """Retorna a lista de pares de moedas disponíveis"""
        return self.tools.data_provider.get_available_pairs()
    
    def analyze_market(self, symbol: str, timeframe: str = '1d') -> str:
        """
        Solicita ao agente uma análise do mercado para um par específico
        
        Args:
            symbol (str): Par de moedas (ex: 'EURUSD')
            timeframe (str): Intervalo de tempo ('1h', '4h', '1d')
            
        Returns:
            str: Análise do mercado
        """
        prompt = f"""
        Faça uma análise rápida do par {symbol} no timeframe {timeframe}.
        Utilize os dados disponíveis para fornecer insights sobre o movimento recente do preço.
        """
        
        # Aqui usamos o LLM para gerar uma análise baseada nos dados
        response = self.agent.generate_response(prompt)
        return response
    
    def get_asset_info(self, symbol: str) -> Dict[str, Any]:
        """
        Obtém informações detalhadas sobre um ativo Forex
        
        Args:
            symbol (str): Par de moedas (ex: 'EURUSD')
            
        Returns:
            Dict: Informações detalhadas do ativo
        """
        # Dicionário com informações dos principais pares de moedas
        asset_info = {
            'EURUSD': {
                 'name': 'Euro / Dólar Americano',
                 'description': 'O par de moedas mais negociado no mundo, representando a relação entre o Euro e o Dólar Americano.',
                 'base_currency': 'EUR',
                 'quote_currency': 'USD',
                 'pip_value': 0.0001,
                 'spread_typical': '1-2 pips',
                 'session_hours': 'Londres: 08:00-17:00 GMT, Nova York: 13:00-22:00 GMT',
                 'horario_brasil': 'Londres: 05:00-14:00 BRT, Nova York: 10:00-19:00 BRT',
                 'volatility': 'Média',
                 'category': 'Major'
             },
            'GBPUSD': {
                 'name': 'Libra Esterlina / Dólar Americano',
                 'description': 'Par conhecido como "Cable", representa a relação entre a Libra Esterlina e o Dólar Americano.',
                 'base_currency': 'GBP',
                 'quote_currency': 'USD',
                 'pip_value': 0.0001,
                 'spread_typical': '2-3 pips',
                 'session_hours': 'Londres: 08:00-17:00 GMT, Nova York: 13:00-22:00 GMT',
                 'horario_brasil': 'Londres: 05:00-14:00 BRT, Nova York: 10:00-19:00 BRT',
                 'volatility': 'Alta',
                 'category': 'Major'
             },
            'USDJPY': {
                 'name': 'Dólar Americano / Iene Japonês',
                 'description': 'Par que representa a relação entre o Dólar Americano e o Iene Japonês.',
                 'base_currency': 'USD',
                 'quote_currency': 'JPY',
                 'pip_value': 0.01,
                 'spread_typical': '1-2 pips',
                 'session_hours': 'Tóquio: 00:00-09:00 GMT, Nova York: 13:00-22:00 GMT',
                 'horario_brasil': 'Tóquio: 21:00-06:00 BRT, Nova York: 10:00-19:00 BRT',
                 'volatility': 'Média',
                 'category': 'Major'
             },
            'USDCHF': {
                 'name': 'Dólar Americano / Franco Suíço',
                 'description': 'Par conhecido como "Swissie", representa a relação entre o Dólar Americano e o Franco Suíço.',
                 'base_currency': 'USD',
                 'quote_currency': 'CHF',
                 'pip_value': 0.0001,
                 'spread_typical': '2-3 pips',
                 'session_hours': 'Londres: 08:00-17:00 GMT, Nova York: 13:00-22:00 GMT',
                 'horario_brasil': 'Londres: 05:00-14:00 BRT, Nova York: 10:00-19:00 BRT',
                 'volatility': 'Baixa-Média',
                 'category': 'Major'
             },
            'AUDUSD': {
                 'name': 'Dólar Australiano / Dólar Americano',
                 'description': 'Par conhecido como "Aussie", representa a relação entre o Dólar Australiano e o Dólar Americano.',
                 'base_currency': 'AUD',
                 'quote_currency': 'USD',
                 'pip_value': 0.0001,
                 'spread_typical': '2-4 pips',
                 'session_hours': 'Sydney: 22:00-07:00 GMT, Nova York: 13:00-22:00 GMT',
                 'horario_brasil': 'Sydney: 19:00-04:00 BRT, Nova York: 10:00-19:00 BRT',
                 'volatility': 'Média-Alta',
                 'category': 'Major'
             },
            'USDCAD': {
                 'name': 'Dólar Americano / Dólar Canadense',
                 'description': 'Par conhecido como "Loonie", representa a relação entre o Dólar Americano e o Dólar Canadense.',
                 'base_currency': 'USD',
                 'quote_currency': 'CAD',
                 'pip_value': 0.0001,
                 'spread_typical': '2-3 pips',
                 'session_hours': 'Nova York: 13:00-22:00 GMT',
                 'horario_brasil': 'Nova York: 10:00-19:00 BRT',
                 'volatility': 'Média',
                 'category': 'Major'
             },
            'NZDUSD': {
                 'name': 'Dólar Neozelandês / Dólar Americano',
                 'description': 'Par conhecido como "Kiwi", representa a relação entre o Dólar Neozelandês e o Dólar Americano.',
                 'base_currency': 'NZD',
                 'quote_currency': 'USD',
                 'pip_value': 0.0001,
                 'spread_typical': '3-5 pips',
                 'session_hours': 'Sydney: 22:00-07:00 GMT, Nova York: 13:00-22:00 GMT',
                 'horario_brasil': 'Sydney: 19:00-04:00 BRT, Nova York: 10:00-19:00 BRT',
                 'volatility': 'Alta',
                 'category': 'Major'
             }
        }
        
        # Retorna informações do ativo ou informações padrão se não encontrado
        if symbol in asset_info:
            return asset_info[symbol]
        else:
            # Informações genéricas para pares não catalogados
            return {
                'name': symbol,
                'description': f'Par de moedas {symbol}',
                'base_currency': symbol[:3] if len(symbol) >= 6 else 'N/A',
                'quote_currency': symbol[3:] if len(symbol) >= 6 else 'N/A',
                'pip_value': 0.0001,
                'spread_typical': 'Variável',
                'session_hours': 'Conforme mercado',
                'horario_brasil': 'Conforme mercado',
                'volatility': 'Variável',
                'category': 'Outros'
            }
        