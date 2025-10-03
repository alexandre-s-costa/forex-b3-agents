# Forex Agents

Sistema de agentes para análise de mercado Forex e B3 utilizando o framework Agno com interface web moderna e visualizações interativas.

## Funcionalidades

### 📊 Análise de Dados
- Captura de dados históricos do mercado Forex e B3 via Yahoo Finance
- Visualização tabular de dados OHLC (Open, High, Low, Close) com formatação profissional
- Gráficos de candlestick interativos usando Plotly para análise visual avançada
- Estatísticas resumidas automáticas (máximas, mínimas, variações percentuais)

### ⏰ Timeframes Flexíveis
- **1 hora (1h)**: Análise intradiária detalhada
- **4 horas (4h)**: Análise de médio prazo
- **Diário (1d)**: Análise de tendências de longo prazo
- Seleção dinâmica de período histórico (configurável)

### 💱 Pares de Moedas Suportados
- **EURUSD**: Euro / Dólar Americano
- **GBPUSD**: Libra Esterlina / Dólar Americano  
- **USDJPY**: Dólar Americano / Iene Japonês
- **AUDUSD**: Dólar Australiano / Dólar Americano
- **USDCAD**: Dólar Americano / Dólar Canadense
- **USDCHF**: Dólar Americano / Franco Suíço
- **NZDUSD**: Dólar Neozelandês / Dólar Americano

### 🖥️ Interface Web
- Interface responsiva com Bootstrap 5
- Formulários dinâmicos para seleção de parâmetros
- Atualização em tempo real dos dados e gráficos
- Design moderno e intuitivo

### 🤖 Agentes Inteligentes
- Agente Forex especializado com ferramentas dedicadas
- Integração com modelo Perplexity para análises de mercado
- Processamento automatizado de dados com tratamento de erros robusto

## Requisitos

- Python 3.8+
- Dependências listadas em `requirements.txt`

## Instalação

```bash
# Clonar o repositório
git clone https://github.com/alexandre-s-costa/forex-b3-agents.git
cd forex-agents

# Instalar dependências
pip install -r requirements.txt
```

## Uso

```bash
# Iniciar a aplicação (opções)
python main.py
# ou
python -m app.main
```

Acesse a interface web em `http://localhost:8000`

## Rotas da Aplicação

- `/` — Dashboard principal (Forex)
- `/upload` — Upload de dados (CSV/Excel) com pré-visualização e gráficos
- `/b3` — Visualização de Ativos B3 (WINFUT, WDOFUT)
- `/charts/{data_id}` — Gráficos gerados a partir de um upload

## Ativos B3 (WINFUT e WDOFUT)

- Página dedicada em `/b3` para visualização dos ativos da B3: `WINFUT` (Mini Índice Futuro) e `WDOFUT` (Mini Dólar Futuro).
- Configurações disponíveis: seleção do ativo, `timeframe` (`1h`, `4h`, `1d`) e período histórico (`days_back`).
- Gráficos de candlestick e tabela OHLC são exibidos com base nos dados processados, destacando preços e variações.
- Filtragem de fins de semana: os dados são pré-processados para remover sábados e domingos, garantindo consistência nas séries temporais.
- Horário de negociação típico: 9h às 18h (BRT); métricas e estatísticas são calculadas considerando somente dias úteis.
- Objetivo da página: facilitar a análise visual e tabular dos principais contratos futuros negociados na B3.

## Navegação no Cabeçalho

- Menu suspenso “Menu” com atalhos para: `Dashboard`, `Upload de Dados` e `Ativos B3`
- Links diretos permanecem na navbar para acesso rápido
- Implementado com Bootstrap 5 (`dropdown-toggle`, `dropdown-menu`)

## Regras de Filtro — Ativos B3

- Converte a coluna `data` para `datetime`
- Remove sábados e domingos, mantendo apenas dias úteis (`weekday < 5`)
- Aplica a filtragem antes de cálculos acumulados, agrupamentos e estatísticas
- Objetivo: evitar intervalos vazios em gráficos de histórico

## Upload de Arquivos (CSV/Excel)

- Página dedicada em `/upload` para enviar arquivos `.csv`, `.xlsx` ou `.xls` com dados de trading.
- Validações automáticas: extensão suportada, tentativa de decodificação (UTF-8, Latin-1, CP1252, ISO-8859-1) e detecção de separadores comuns (`,`, `;`, `\t`, `|`).
- Colunas obrigatórias esperadas: `data`, `min_pts_gain`, `max_pts_gain`, `min_pts_stop`, `max_pts_stop`, `min_resultado`, `max_resultado`.
- Após o processamento, a página exibe:
  - Resumo de dados (arquivo, número de registros, colunas e separador detectado);
  - Tabela HTML com os dados carregados;
  - Link “Ver Gráficos” apontando para `/charts/{data_id}` para visualizações adicionais.
- Armazenamento temporário: os dados são guardados em memória com um `data_id` único para navegação entre páginas.
- Tratamento de erros amigável: mensagens claras para arquivos vazios, formato inválido ou falhas de parsing.

## Informações de Ativos Forex

- Exibição detalhada por par: `name`, `description`, `base_currency`, `quote_currency`, `pip_value`, `spread_typical`, `volatility`, `session_hours`, `horario_brasil`
- Campo `horario_brasil` mostra horários convertidos de GMT para BRT (UTC-3)
- Principais pares cobertos: EURUSD, GBPUSD, USDJPY, USDCHF, AUDUSD, USDCAD, NZDUSD


## Estrutura do Projeto

```
forex-agents/
├── agents/                 # Agentes especializados
│   ├── __init__.py
│   └── forex_agent.py      # Agente Forex com ferramentas integradas
├── data/                   # Módulos de dados
│   ├── __init__.py
│   └── forex_data.py       # Provedor de dados Forex (Yahoo Finance)
├── visualization/          # Componentes de visualização
│   ├── __init__.py
│   ├── table_view.py       # Visualização tabular com estatísticas
│   └── chart_view.py       # Gráficos interativos Plotly
├── app/                    # Aplicação web FastAPI
│   ├── __init__.py
│   ├── main.py             # Servidor web e rotas
│   └── templates/          # Templates HTML Jinja2
│       └── index.html      # Interface principal
├── main.py                 # Ponto de entrada principal
├── requirements.txt        # Dependências do projeto
└── README.md               # Documentação
```

## Melhorias Técnicas Implementadas

### 🔧 Robustez de Dados
- **Períodos Adaptativos**: Sistema automaticamente ajusta períodos de busca para garantir dados suficientes
- **Tratamento de Fins de Semana**: Lógica inteligente para lidar com mercados fechados
- **Fallback Inteligente**: Para timeframes intradiários, busca até 14 dias; para diários, até 7 dias
- **Validação de Símbolos**: Verificação automática de pares de moedas disponíveis

### 🚀 Performance
- **Cache de Dados**: Otimização de requisições ao Yahoo Finance
- **Processamento Assíncrono**: Interface web não-bloqueante
- **Filtragem Eficiente**: Dados filtrados após download para máxima precisão

### 🛡️ Tratamento de Erros
- **Exceções Graceful**: Tratamento robusto de erros de rede e dados
- **Feedback ao Usuário**: Mensagens claras sobre problemas de conectividade
- **Logs Detalhados**: Sistema de logging para debugging e monitoramento