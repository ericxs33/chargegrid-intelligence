# ⚡ ChargeGrid Intelligence — DLM Simulator

> **GoodWe Challenge · FIAP 2026**  
> Sistema de Gerenciamento Dinâmico de Carga (DLM) com IA embarcada, dashboard web interativo e coleta de dados persistente para carregamento inteligente de veículos elétricos em ambiente comercial.

---

## 👥 Equipe

| Nome | RM |
|---|---|
| Eric dos Santos Mendes da Silva | 569528 |
| Felipe de Oliveira Doern | 568798 |
| Lígia de Andrade Matheus | 568973 |
| Miguel Marcelo Alves Ramos de Oliveira | 569467 |
| Tom Stringasci Albuquerque Coelho de Morais | 568844 |

---

## 🎯 Sobre o Projeto

O **ChargeGrid Intelligence** é o ecossistema da GoodWe para carregamento inteligente de veículos elétricos. Integra carregadores, painéis solares, baterias e inteligência artificial em uma única plataforma gerenciada pelo app SEMS+.

### O problema que resolvemos

Em ambientes comerciais, múltiplos veículos elétricos carregando simultaneamente em horário de pico podem gerar demandas que excedem o limite da instalação elétrica (ex: 184 kW vs limite de 120 kW), causando sobrecarga e risco de interrupção. Sem gestão inteligente, o sistema também desperdiça energia renovável disponível, recorrendo desnecessariamente à rede elétrica.

### A solução

O DLM monitora a demanda total em tempo real e, quando detecta risco de sobrecarga, aciona o **módulo de IA** que analisa o estado de todas as estações e redistribui a carga proporcionalmente. O sistema prioriza sempre energia solar, depois bateria, e recorre à rede apenas quando necessário.

---

## 📈 Evolução por Sprint

| Sprint | Entrega | Novidades |
|---|---|---|
| **Sprint 1** | Pesquisa e proposição de soluções | Análise dos 4 pilares, 5 problemas identificados |
| **Sprint 2** | Simulador CLI em Python | DLM funcional, IA embarcada, tarifação, CO₂ evitado |
| **Sprint 3** | Integração completa | Coleta de dados CSV, log persistente, dashboard web, diagrama de integração |

---

## 🏗️ Arquitetura do Sistema

```
┌─────────────────────────────────────────────────────────────┐
│                    Fontes de Energia                         │
│   ☀ Solar (78 kW)  →  🔋 Bateria (30 kW)  →  ⚡ Rede       │
│          Prioridade automática: Solar → Bateria → Rede       │
└───────────────────────────┬─────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│              DLM Engine + Módulo de IA (main.py)            │
│  Monitora demanda · Redistribui carga · Detecta sobrecarga  │
│  Calcula mix de energia · Aciona IA · Gera log persistente  │
└──────┬──────────────────────────────────────────────┬───────┘
       │ OCPP 2.0.1                                   │
       ▼                                              ▼
┌─────────────────────────┐              ┌────────────────────┐
│   Estações (EV-01~06)   │              │   Saídas de dados  │
│  CCS2 · Tipo2 · CHAdeMO │              │  sessions.csv      │
│  RFID · App · QR Code   │              │  system.log        │
└─────────────────────────┘              │  relatorio.txt     │
                                         └────────┬───────────┘
                                                  │
                                                  ▼
                                    ┌─────────────────────────┐
                                    │   dashboard.html        │
                                    │  Lê CSV · Exibe gráficos│
                                    │  Métricas · CO₂ · Tabela│
                                    └─────────────────────────┘
```

> O diagrama visual completo está em [`assets/diagrama.png`](assets/diagrama.png)

---

## 🔧 Os 4 Pilares em Prática

| Pilar | Como é demonstrado |
|---|---|
| **1. Controle de Demanda** | Barra de demanda em tempo real, DLM redistribuindo carga ao atingir 120 kW |
| **2. Protocolos Abertos** | 6 estações com CCS2, Tipo 2 e CHAdeMO — todas via OCPP 2.0.1 |
| **3. Tarifação e Pagamento** | R$ 1,35/kWh com relatório por sessão, autenticação RFID/App/QR, exportação CSV |
| **4. Inteligência Artificial** | Módulo de IA analisa a rede, explica cada decisão e recomenda horários sustentáveis |

---

## 🌱 Energias Renováveis e Sustentabilidade

### Prioridade de fontes de energia

```
1. ☀️  Solar    → até 78 kW  (energia limpa, custo zero após instalação)
2. 🔋  Bateria  → até 30 kW  (armazenamento do excedente solar)
3. ⚡  Rede     → restante   (acionada apenas quando necessário)
```

### Cálculo de CO₂ evitado

| Parâmetro | Valor | Fonte |
|---|---|---|
| Fator de emissão da rede BR | 0,0817 kg CO₂/kWh | MCTIC 2023 |
| Referência de km evitados | 0,089 kg CO₂/km | IPCC |

```
CO₂ evitado (kg) = kWh solar utilizado × 0,0817
```

O sistema calcula e exibe o CO₂ evitado em tempo real no terminal e no dashboard.

---

## 🆕 Novidades da Sprint 3

### Coleta de dados persistente

Ao encerrar uma sessão, o sistema salva automaticamente em `sessions.csv`:

| Campo | Descrição |
|---|---|
| data_hora | Timestamp completo da sessão |
| estacao | ID da estação (EV-01 a EV-06) |
| usuario | ID do usuário autenticado |
| conector | Tipo de conector (CCS2, Tipo 2, CHAdeMO) |
| auth | Método de autenticação (RFID, App, QR Code) |
| kwh | Energia consumida na sessão |
| tempo_min | Duração em minutos |
| custo_brl | Valor cobrado em R$ |
| fonte_energia | Solar / Misto / Bateria / Rede |
| solar_pct | Porcentagem de geração solar |
| co2_evitado_kg | CO₂ evitado vs. uso 100% da rede |
| dlm_ativo | Se o DLM estava ativo na sessão |
| protocolo | OCPP 2.0.1 |

### 📊 Dashboard Web de Monitoramento (`dashboard.html`)

> 🔗 **Arquivo local:** [`dashboard.html`](dashboard.html)  
> 🌐 **Online (GitHub Pages):** [https://ericxs33.github.io/chargegrid-intelligence/dashboard.html](https://ericxs33.github.io/chargegrid-intelligence/dashboard.html)

Interface analítica interativa em modo escuro desenvolvida com HTML5, CSS3 e Chart.js via CDN. O dashboard consome o arquivo `sessions.csv` gerado pelo simulador e apresenta:

- **Cards de KPIs em tempo real:** Total de sessões, volume de kWh consumidos, receita tarifada (R$) e CO₂ evitado acumulado.
- **Indicadores de Sustentabilidade:** Volume de energia solar aproveitada, km equivalentes limpos rodados e taxa percentual de atuação do algoritmo DLM.
- **Gráficos interativos:**
  - Consumo total acumulado por estação de recarga (EV-01 a EV-06).
  - Distribuição do mix energético por fontes (Solar, Bateria, Rede e Misto).
- **Tabela de auditoria detalhada:** Histórico completo das sessões com data/hora, conector (CCS2/Tipo 2/CHAdeMO), autenticação (RFID/App/QR), custo e protocolo OCPP 2.0.1.

#### 💡 Como acessar e utilizar o Dashboard:

1. **Abrir o Dashboard:**
   - **Localmente:** Dê um duplo clique no arquivo [`dashboard.html`](dashboard.html) na raiz do projeto (abre em qualquer navegador) ou execute no terminal PowerShell:
     ```powershell
     start dashboard.html
     ```
   - **Online:** Acesse diretamente via [GitHub Pages](https://ericxs33.github.io/chargegrid-intelligence/dashboard.html).
2. **Gerar os dados:**
   - Execute o simulador CLI (`python main.py`), inicie e encerre sessões de recarga para que os dados consolidados sejam salvos automaticamente no arquivo `sessions.csv`.
3. **Carregar no Dashboard:**
   - Na tela do dashboard, clique no botão central **"Carregar sessions.csv"** e selecione o arquivo gerado na raiz do projeto. Todos os dados, gráficos e tabelas serão renderizados instantaneamente.

### Log persistente (`system.log`)

Todos os eventos do sistema são gravados em arquivo com timestamp real, mantendo o histórico mesmo após fechar o programa.

---

## 🚀 Como executar

### Pré-requisitos

- Python 3.10 ou superior
- Nenhuma biblioteca externa necessária
- Navegador moderno para o dashboard

### Simulador CLI

```bash
git clone https://github.com/ericxs33/chargegrid-intelligence.git
cd chargegrid-intelligence
python main.py
```

### Dashboard Web

1. Execute o simulador (`python main.py`) e encerre sessões para gerar o `sessions.csv`
2. Abra [`dashboard.html`](dashboard.html) no navegador (duplo clique ou `start dashboard.html`)
3. Clique em **"Carregar sessions.csv"** e selecione o arquivo
4. Os dados, gráficos e indicadores aparecem automaticamente (ou acesse online via [GitHub Pages](https://ericxs33.github.io/chargegrid-intelligence/dashboard.html))

### Compatibilidade

| Sistema | Status |
|---|---|
| Windows 10/11 | ✅ Use PowerShell ou Windows Terminal |
| macOS | ✅ |
| Linux | ✅ |

---

## 📋 Menu do Simulador

```
  1 · Iniciar sessão de carregamento
  2 · Encerrar sessão          ← salva automaticamente no CSV
  3 · Simular avanço de tempo (+ 5 min)
  4 · Ativar / desativar DLM
  5 · Simular cenário de pico
  6 · Ajustar geração solar
  7 · Análise da IA
  8 · Ver relatório de tarifação
  9 · Exportar relatório .txt
  L · Ver log completo do sistema
  D · Ver dados do CSV
  C · Limpar dados do CSV
  0 · Sair
```

---

## 📁 Estrutura do Repositório

```
chargegrid-intelligence/
│
├── main.py           # Simulador CLI — ponto de entrada
├── dashboard.html    # Dashboard web interativo
├── README.md         # Este arquivo
│
├── docs/
│   └── arquitetura.md    # Detalhamento técnico da solução
│
└── assets/
    ├── diagrama.png              # Diagrama de integração dos componentes
    └── (screenshots do simulador)
```

---

## 🔗 Links

- 📊 **Dashboard Web Online:** https://ericxs33.github.io/chargegrid-intelligence/dashboard.html
- 📄 **Código do Dashboard:** [dashboard.html](dashboard.html)
- 🎥 **Vídeo Sprint 2:** https://youtu.be/9wmg-8ojMLE
- 🎥 **Vídeo Sprint 3:** *(em breve)*
- 📋 **Quadro Kanban:** https://trello.com/invite/b/6a2855abfaa8d2266be81030/ATTI953e9abb1a8572be50e19a9213686f9fAA9C9467/chargegrid-intelligence-sprint-2

---

## 📚 Referências Técnicas

- [OCPP 2.0.1 — Open Charge Alliance](https://www.openchargealliance.org/)
- [GoodWe ChargeGrid HCA G2](https://br.goodwe.com/carregadores-hca-g2-goodwe)
- [Fator de Emissão — MCTIC 2023](https://www.gov.br/mcti/pt-br)
- [Dynamic Load Management — IEC 61851](https://webstore.iec.ch/publication/6029)
- [Tarifa Branca ANEEL](https://www.aneel.gov.br/tarifa-branca)
- [IPCC — Emissões por km](https://www.ipcc.ch/)
