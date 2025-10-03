from fastapi import FastAPI, Request, Form, UploadFile, File
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
import uvicorn
from typing import Optional
import pandas as pd
import io
import json
from datetime import datetime

import sys
import os
# Adiciona o diretório raiz ao path para importação dos módulos
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from agents.forex_agent import ForexAgent
from visualization.table_view import TableView
from visualization.chart_view import ChartView 

from dotenv import load_dotenv

app = FastAPI(title="Forex Agents")
templates = Jinja2Templates(directory="app/templates")

# Armazenamento temporário dos dados CSV
uploaded_data_store = {}

# Carrega variáveis de ambiente (.env)
load_dotenv()

# Inicializa os componentes com configuração via ambiente
MODEL_ID = os.getenv("MODEL_ID", "llama-3.1-sonar-small-128k-online")
forex_agent = ForexAgent(model_id=MODEL_ID)
table_view = TableView()
chart_view = ChartView()

@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    """Rota principal da aplicação"""
    # Obtém a lista de pares disponíveis
    available_pairs = forex_agent.get_available_pairs()
    
    # Define valores padrão
    selected_symbol = "EURUSD"
    timeframe = "1d"
    days_back = 2
    
    # Obtém os dados do par selecionado
    data = forex_agent.get_forex_data(selected_symbol, timeframe, days_back)
    
    # Gera a tabela HTML
    table_html = table_view.get_html_table(data)
    
    # Gera o gráfico HTML
    chart_html = chart_view.get_html_chart(data)
    
    # Obtém estatísticas resumidas
    stats = table_view.get_summary_stats(data)
    
    # Obtém informações do ativo
    asset_info = forex_agent.get_asset_info(selected_symbol)
    
    return templates.TemplateResponse(
        "index.html",
        {
            "request": request,
            "available_pairs": available_pairs,
            "selected_symbol": selected_symbol,
            "timeframe": timeframe,
            "days_back": days_back,
            "table_html": table_html,
            "chart_html": chart_html,
            "stats": stats,
            "asset_info": asset_info
        }
    )

@app.post("/", response_class=HTMLResponse)
async def update_data(
    request: Request,
    symbol: str = Form(...),
    timeframe: str = Form(...),
    days_back: int = Form(...)
):
    """Atualiza os dados com base nos parâmetros selecionados"""
    # Obtém a lista de pares disponíveis
    available_pairs = forex_agent.get_available_pairs()
    
    # Obtém os dados do par selecionado
    data = forex_agent.get_forex_data(symbol, timeframe, days_back)
    
    # Gera a tabela HTML
    table_html = table_view.get_html_table(data)
    
    # Gera o gráfico HTML
    chart_html = chart_view.get_html_chart(data)
    
    # Obtém estatísticas resumidas
    stats = table_view.get_summary_stats(data)
    
    # Obtém informações do ativo
    asset_info = forex_agent.get_asset_info(symbol)
    
    return templates.TemplateResponse(
        "index.html",
        {
            "request": request,
            "available_pairs": available_pairs,
            "selected_symbol": symbol,
            "timeframe": timeframe,
            "days_back": days_back,
            "table_html": table_html,
            "chart_html": chart_html,
            "stats": stats,
            "asset_info": asset_info
        }
    )

@app.get("/upload", response_class=HTMLResponse)
async def upload_page(request: Request):
    """Página de upload de arquivos"""
    return templates.TemplateResponse(
        "upload.html",
        {
            "request": request,
            "message": None,
            "error": None
        }
    )

@app.post("/upload", response_class=HTMLResponse)
async def process_upload(
    request: Request,
    file: UploadFile = File(...)
):
    """Processa o arquivo enviado"""
    try:
        # Verifica se o arquivo foi enviado
        if not file.filename:
            raise ValueError("Nenhum arquivo foi selecionado")
        
        # Verifica a extensão do arquivo
        if not file.filename.lower().endswith(('.csv', '.xlsx', '.xls')):
            raise ValueError("Formato de arquivo não suportado. Use CSV ou Excel (.xlsx, .xls)")
        
        # Lê o conteúdo do arquivo
        contents = await file.read()
        
        # Processa o arquivo baseado na extensão
        if file.filename.lower().endswith('.csv'):
            # Tenta diferentes encodings e separadores para CSV
            content_str = None
            for encoding in ['utf-8', 'latin-1', 'cp1252', 'iso-8859-1']:
                try:
                    content_str = contents.decode(encoding)
                    break
                except UnicodeDecodeError:
                    continue
            
            if content_str is None:
                raise ValueError("Não foi possível decodificar o arquivo CSV. Verifique a codificação do arquivo.")
            
            # Tenta diferentes separadores
            df = None
            separators = [',', ';', '\t', '|']
            for sep in separators:
                try:
                    df = pd.read_csv(
                        io.StringIO(content_str), 
                        sep=sep,
                        on_bad_lines='skip',  # Pula linhas problemáticas
                        skipinitialspace=True,  # Remove espaços extras
                        encoding_errors='ignore'  # Ignora erros de encoding
                    )
                    # Verifica se o DataFrame tem pelo menos 2 colunas (indicando separação correta)
                    if len(df.columns) >= 2:
                        break
                except Exception:
                    continue
            
            if df is None or len(df.columns) < 2:
                raise ValueError("Não foi possível processar o arquivo CSV. Verifique se o arquivo está formatado corretamente com separadores válidos (vírgula, ponto e vírgula, tab ou pipe).")
        else:
            df = pd.read_excel(io.BytesIO(contents))
        
        # Colunas obrigatórias
        required_columns = [
            'data', 'min_pts_gain', 'max_pts_gain', 
            'min_pts_stop', 'max_pts_stop', 'min_resultado', 'max_resultado'
        ]
        
        # Verifica se todas as colunas obrigatórias estão presentes
        missing_columns = [col for col in required_columns if col not in df.columns]
        if missing_columns:
            raise ValueError(f"Colunas obrigatórias ausentes: {', '.join(missing_columns)}")
        
        # Processa os dados (aqui você pode adicionar lógica específica)
        processed_data = df[required_columns].copy()
        
        # Armazena os dados processados temporariamente
        data_id = f"data_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        uploaded_data_store[data_id] = processed_data.to_dict('records')
        
        # Converte para HTML para exibição
        table_html = processed_data.to_html(classes='table table-striped table-hover', table_id='uploaded-data')
        
        return templates.TemplateResponse(
            "upload.html",
            {
                "request": request,
                "message": f"✅ Arquivo '{file.filename}' processado com sucesso! {len(processed_data)} registros carregados.",
                "error": None,
                "table_html": table_html,
                "data_summary": {
                    "filename": file.filename,
                    "rows": len(processed_data),
                    "columns": len(processed_data.columns),
                    "separator_used": "Detectado automaticamente" if file.filename.lower().endswith('.csv') else "N/A",
                    "data_id": data_id  # ID para acessar os gráficos
                }
            }
        )
        
    except ValueError as ve:
        # Erros específicos de validação
        return templates.TemplateResponse(
            "upload.html",
            {
                "request": request,
                "message": None,
                "error": f"❌ Erro de validação: {str(ve)}"
            }
        )
    except pd.errors.EmptyDataError:
        return templates.TemplateResponse(
            "upload.html",
            {
                "request": request,
                "message": None,
                "error": "❌ O arquivo está vazio ou não contém dados válidos."
            }
        )
    except pd.errors.ParserError as pe:
        return templates.TemplateResponse(
            "upload.html",
            {
                "request": request,
                "message": None,
                "error": f"❌ Erro ao analisar o arquivo: {str(pe)}. Verifique se o formato está correto."
            }
        )
    except Exception as e:
        # Outros erros gerais
        return templates.TemplateResponse(
            "upload.html",
            {
                "request": request,
                "message": None,
                "error": f"❌ Erro inesperado ao processar arquivo: {str(e)}"
            }
         )

@app.get("/charts/{data_id}", response_class=HTMLResponse)
async def charts_page(request: Request, data_id: str, start_date: Optional[str] = None, end_date: Optional[str] = None):
    """Página de visualização de gráficos dos dados CSV"""
    if data_id not in uploaded_data_store:
        return templates.TemplateResponse(
            "upload.html",
            {
                "request": request,
                "message": None,
                "error": "❌ Dados não encontrados. Faça upload de um arquivo primeiro."
            }
        )
    
    # Recupera os dados
    data = pd.DataFrame(uploaded_data_store[data_id]).copy()
    
    # Converte a coluna de data
    data['data'] = pd.to_datetime(data['data'], errors='coerce')
    
    # Aplica filtros de data se fornecidos
    if start_date:
        data = data[data['data'] >= pd.to_datetime(start_date)]
    if end_date:
        data = data[data['data'] <= pd.to_datetime(end_date)]
    
    # Remove linhas com datas inválidas
    data = data.dropna(subset=['data'])
    
    # Preparar dados para os gráficos
    chart_data = {
        'dates': [],
        'lucros': [],
        'perdas': [],
        'resultados': [],
        'eficiencia': {'positivos': 0, 'negativos': 0},
        # Novos dados para gráficos adicionais
        'historico_min_max': {'dates': [], 'min_resultado': [], 'max_resultado': [], 'resultado_acumulado': []},
        'consolidado_periodo': {'mensal': {}, 'trimestral': {}, 'semestral': {}, 'anual': {}},
        'dispersao_risco': {'min_pts_gain': [], 'min_pts_stop': [], 'max_pts_gain': [], 'max_pts_stop': []}
    }
    
    if len(data) > 0:
        # Converte colunas numéricas e trata valores NaN como zero
        numeric_columns = ['max_pts_gain', 'min_pts_gain', 'max_pts_stop', 'min_pts_stop', 'min_resultado', 'max_resultado']
        for col in numeric_columns:
            if col in data.columns:
                data[col] = pd.to_numeric(data[col], errors='coerce').fillna(0)
        
        # Ordena por data para cálculos corretos
        data_clean = data.sort_values('data').copy()
        
        if len(data_clean) > 0:
            # 1. HISTÓRICO DO RESULTADO (gráfico de linha)
            # Eixo X = data (ordenada), Eixo Y = min_resultado e max_resultado
            # Também gerar linha acumulada: resultado_acumulado[i] = soma(resultado_dia[0..i])
            historico_data = data_clean[['data', 'min_resultado', 'max_resultado']].copy()
            historico_data = historico_data.sort_values('data')
            
            # Calcular resultado acumulado usando max_resultado
            historico_data['resultado_acumulado'] = historico_data['max_resultado'].cumsum()
            
            chart_data['historico_min_max'] = {
                'dates': historico_data['data'].dt.strftime('%Y-%m-%d').tolist(),
                'min_resultado': historico_data['min_resultado'].tolist(),
                'max_resultado': historico_data['max_resultado'].tolist(),
                'resultado_acumulado': historico_data['resultado_acumulado'].tolist()
            }
            
            # 2. LUCRO E PERDA (gráfico de barras)
            # Converter data em datetime, agrupar por período
            # lucro_total = soma dos resultados positivos (max_resultado > 0)
            # perda_total = soma dos resultados negativos (max_resultado < 0)
            data_clean['ano'] = data_clean['data'].dt.year
            data_clean['mes'] = data_clean['data'].dt.month
            data_clean['trimestre'] = data_clean['data'].dt.quarter
            data_clean['semestre'] = ((data_clean['data'].dt.month - 1) // 6) + 1
            
            def calcular_lucro_perda_periodo(grupo):
                lucro_total = grupo[grupo['max_resultado'] > 0]['max_resultado'].sum()
                perda_total = abs(grupo[grupo['max_resultado'] < 0]['max_resultado'].sum())
                return pd.Series({'lucro_total': lucro_total, 'perda_total': perda_total})
            
            # Mensal
            mensal = data_clean.groupby(['ano', 'mes']).apply(calcular_lucro_perda_periodo).reset_index()
            mensal['periodo'] = mensal['ano'].astype(str) + '-' + mensal['mes'].astype(str).str.zfill(2)
            
            # Trimestral
            trimestral = data_clean.groupby(['ano', 'trimestre']).apply(calcular_lucro_perda_periodo).reset_index()
            trimestral['periodo'] = trimestral['ano'].astype(str) + '-T' + trimestral['trimestre'].astype(str)
            
            # Semestral
            semestral = data_clean.groupby(['ano', 'semestre']).apply(calcular_lucro_perda_periodo).reset_index()
            semestral['periodo'] = semestral['ano'].astype(str) + '-S' + semestral['semestre'].astype(str)
            
            # Anual
            anual = data_clean.groupby('ano').apply(calcular_lucro_perda_periodo).reset_index()
            anual['periodo'] = anual['ano'].astype(str)
            
            chart_data['consolidado_periodo'] = {
                'mensal': {
                    'periodos': mensal['periodo'].tolist(),
                    'lucros': mensal['lucro_total'].tolist(),
                    'perdas': mensal['perda_total'].tolist()
                },
                'trimestral': {
                    'periodos': trimestral['periodo'].tolist(),
                    'lucros': trimestral['lucro_total'].tolist(),
                    'perdas': trimestral['perda_total'].tolist()
                },
                'semestral': {
                    'periodos': semestral['periodo'].tolist(),
                    'lucros': semestral['lucro_total'].tolist(),
                    'perdas': semestral['perda_total'].tolist()
                },
                'anual': {
                    'periodos': anual['periodo'].tolist(),
                    'lucros': anual['lucro_total'].tolist(),
                    'perdas': anual['perda_total'].tolist()
                }
            }
            
            # 3. EFICIÊNCIA DAS OPERAÇÕES (gráfico de pizza)
            # Contar dias vencedores = número de dias em que max_resultado > 0
            # Contar dias perdedores = número de dias em que max_resultado <= 0
            dias_vencedores = len(data_clean[data_clean['max_resultado'] > 0])
            dias_perdedores = len(data_clean[data_clean['max_resultado'] <= 0])
            
            chart_data['eficiencia'] = {
                'positivos': dias_vencedores,
                'negativos': dias_perdedores
            }
            
            # 4. RISCO X RETORNO (gráfico de dispersão)
            # Cada ponto representa 1 dia
            # Eixo X = min_pts_stop (ou max_pts_stop), Eixo Y = min_pts_gain (ou max_pts_gain)
            # Usar valores diretos das colunas, adicionar linha Y = X
            chart_data['dispersao_risco'] = {
                'min_pts_gain': data_clean['min_pts_gain'].tolist(),
                'min_pts_stop': data_clean['min_pts_stop'].tolist(),
                'max_pts_gain': data_clean['max_pts_gain'].tolist(),
                'max_pts_stop': data_clean['max_pts_stop'].tolist()
            }
            
            # Dados para compatibilidade com gráficos antigos (manter estrutura)
            chart_data.update({
                'dates': historico_data['data'].dt.strftime('%Y-%m-%d').tolist(),
                'lucros': [max(0, x) for x in historico_data['max_resultado']],
                'perdas': [abs(min(0, x)) for x in historico_data['max_resultado']],
                'resultados': historico_data['max_resultado'].tolist()
            })
    
    # Se não houver dados suficientes, criar dados de exemplo
    if not chart_data['dates']:
        chart_data = {
            'dates': ['Sem dados'],
            'lucros': [0],
            'perdas': [0],
            'resultados': [0],
            'eficiencia': {'positivos': 0, 'negativos': 0}
        }
    
    return templates.TemplateResponse(
        "charts.html",
        {
            "request": request,
            "data_id": data_id,
            "chart_data": json.dumps(chart_data),
            "start_date": start_date or "",
            "end_date": end_date or "",
            "total_records": len(data)
        }
    )

@app.get("/b3", response_class=HTMLResponse)
async def b3_page(request: Request):
    """Página para visualização de ativos da B3"""
    # Lista de ativos da B3 disponíveis
    b3_assets = ["WINFUT", "WDOFUT"]
    
    # Dados padrão para WINFUT
    selected_asset = "WINFUT"
    timeframe = "1d"
    days_back = 7
    
    try:
        # Obtém dados do ativo selecionado
        data = forex_agent.get_forex_data(selected_asset, timeframe, days_back)
        
        # Gera a tabela HTML
        table_html = table_view.get_html_table(data)
        
        # Gera o gráfico HTML
        chart_html = chart_view.get_html_chart(data)
        
        return templates.TemplateResponse(
            "b3.html",
            {
                "request": request,
                "available_assets": b3_assets,
                "selected_asset": selected_asset,
                "timeframe": timeframe,
                "days_back": days_back,
                "table_html": table_html,
                "chart_html": chart_html
            }
        )
    except Exception as e:
        return templates.TemplateResponse(
            "b3.html",
            {
                "request": request,
                "available_assets": b3_assets,
                "selected_asset": selected_asset,
                "timeframe": timeframe,
                "days_back": days_back,
                "error": f"Erro ao carregar dados: {str(e)}",
                "table_html": "",
                "chart_html": ""
            }
        )

@app.post("/b3", response_class=HTMLResponse)
async def update_b3_data(
    request: Request,
    asset: str = Form(...),
    timeframe: str = Form(...),
    days_back: int = Form(...)
):
    """Atualiza dados dos ativos da B3"""
    b3_assets = ["WINFUT", "WDOFUT"]
    
    try:
        # Obtém dados do ativo selecionado
        data = forex_agent.get_forex_data(asset, timeframe, days_back)
        
        # Gera a tabela HTML
        table_html = table_view.get_html_table(data)
        
        # Gera o gráfico HTML
        chart_html = chart_view.get_html_chart(data)
        
        return templates.TemplateResponse(
            "b3.html",
            {
                "request": request,
                "available_assets": b3_assets,
                "selected_asset": asset,
                "timeframe": timeframe,
                "days_back": days_back,
                "table_html": table_html,
                "chart_html": chart_html
            }
        )
    except Exception as e:
        return templates.TemplateResponse(
            "b3.html",
            {
                "request": request,
                "available_assets": b3_assets,
                "selected_asset": asset,
                "timeframe": timeframe,
                "days_back": days_back,
                "error": f"Erro ao carregar dados: {str(e)}",
                "table_html": "",
                "chart_html": ""
            }
        )

if __name__ == "__main__":
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
    