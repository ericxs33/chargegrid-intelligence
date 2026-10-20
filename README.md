# ⚡ ChargeGrid Intelligence — Solução Final Integrada

> **GoodWe Challenge · FIAP 2026**  
> Sistema de Gerenciamento Dinâmico de Carga (DLM) com IA embarcada, app desktop completo e coleta de dados persistente para carregamento inteligente de veículos elétricos em ambiente comercial.

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
| **Sprint 3** | Integração completa | Coleta CSV, log persistente, dashboard desktop Tkinter |
| **Sprint 4** | Solução final integrada | App desktop unificado com 3 abas, painel de controle interativo, atualização automática |

---

## 🆕 Sprint 4 — App Desktop Unificado (`app.py`)

O `app.py` é a evolução final do projeto: um **app desktop completo em Python puro (Tkinter)** que unifica o simulador CLI e o dashboard em uma única interface com 3 abas integradas.

### Aba 1 — Painel de Controle
- Cards de status em tempo real: demanda total, geração solar, sessões ativas e receita
- Barra visual de demanda vs limite (120 kW) com cor dinâmica — verde / amarelo / vermelho
- Barra de mix energético Solar / Bateria / Rede atualizada em tempo real
- 6 cards interativos de estações — botão Iniciar/Encerrar com diálogo de configuração
- Botões de ação: +5 min, Ativar DLM, Simular Pico, Limpar CSV
- Slider de geração solar (0–100%)

### Aba 2 — IA e Log
- Módulo de IA com análise contextual e efeito de digitação em tempo real
- Log do sistema com todos os eventos e timestamps
- Detecção automática de sobrecarga e acionamento do DLM

### Aba 3 — Dashboard e Dados
- 4 KPIs do CSV: sessões, kWh, receita, CO₂ evitado
- Cards de sustentabilidade: energia solar, km limpos, % DLM ativo
- Gráfico de consumo por estação (Canvas nativo)
- Gráfico de mix energético segmentado (Canvas nativo)
- Tabela histórica completa de sessões

**Atualização automática a cada 3 segundos. 100% Python Standard Library — zero dependências externas.**

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
│           DLM Engine + Módulo de IA (app.py)                │
│  Monitora demanda · Redistribui carga · Detecta sobrecarga  │
│  Calcula mix de energia · Aciona IA · Gera log persistente  │
└──────┬──────────────────────────────────────────────┬───────┘
       │ OCPP 2.0.1                                   │
       ▼                                              ▼
┌─────────────────────────┐         ┌─────────────────────────┐
│   Estações (EV-01~06)   │         │      Saídas de dados     │
│  CCS2 · Tipo2 · CHAdeMO │         │  sessions.csv            │
│  RFID · App · QR Code   │         │  system.log              │
└─────────────────────────┘         │  relatorio.txt           │
                                    └────────────┬────────────┘
                                                 │
                                                 ▼
                                  ┌──────────────────────────┐
                                  │  Dashboard (Aba 3)       │
                                  │  KPIs · Gráficos · Tabela│
                                  └──────────────────────────┘
```

> O diagrama visual completo está em `assets/diagrama.png`

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

### Análise de Impacto

| Indicador | Valor simulado (sessão típica) |
|---|---|
| Demanda máxima sem DLM | 184 kW (sobrecarga) |
| Demanda com DLM ativo | ~110 kW (dentro do limite) |
| Redução de pico | ~40% |
| CO₂ evitado por sessão | 0,02–0,10 kg (65% solar) |
| Tarifa média efetiva | R$ 0,47/kWh (vs R$ 1,35 rede pura) |

---

## 🚀 Como executar

### Pré-requisitos

- Python 3.10 ou superior
- Nenhuma biblioteca externa necessária (100% Python Standard Library)

### App Desktop Completo (Sprint 4 — recomendado)

```bash
git clone https://github.com/ericxs33/chargegrid-intelligence.git
cd chargegrid-intelligence
python app.py
```

### Simulador CLI (Sprint 2/3)

```bash
python main.py
```

### Dashboard Standalone (Sprint 3)

```bash
python dashboard.py
```

### Compatibilidade

| Sistema | Status |
|---|---|
| Windows 10/11 | ✅ Use PowerShell ou Windows Terminal |
| macOS | ✅ |
| Linux | ✅ |

---

## 📁 Estrutura do Repositório

```
chargegrid-intelligence/
│
├── app.py            # App desktop completo — Sprint 4 (ponto de entrada final)
├── main.py           # Simulador CLI — Sprint 2/3
├── dashboard.py      # Dashboard standalone — Sprint 3
├── sessions.csv      # Base de dados persistente das sessões
├── system.log        # Histórico de eventos do sistema
├── README.md         # Este arquivo
│
├── docs/
│   └── arquitetura.md    # Detalhamento técnico da solução
│
└── assets/
    ├── diagrama.png              # Diagrama de integração
    └── (screenshots do app)
```

---

## 🔗 Links

- 🎥 **Vídeo Sprint 2:** https://youtu.be/9wmg-8ojMLE
- 🎥 **Vídeo Sprint 3:** https://www.youtube.com/watch?v=dn-p8uNGKpM
- 🎥 **Vídeo Sprint 4:** *(em breve)*
- 📋 **Quadro Kanban:** https://trello.com/invite/b/6a2855abfaa8d2266be81030/ATTI953e9abb1a8572be50e19a9213686f9fAA9C9467/chargegrid-intelligence-sprint-2

---

## 📚 Referências Técnicas

- [OCPP 2.0.1 — Open Charge Alliance](https://www.openchargealliance.org/)
- [GoodWe ChargeGrid HCA G2](https://br.goodwe.com/carregadores-hca-g2-goodwe)
- [Fator de Emissão — MCTIC 2023](https://www.gov.br/mcti/pt-br)
- [Dynamic Load Management — IEC 61851](https://webstore.iec.ch/publication/6029)
- [Tarifa Branca ANEEL](https://www.aneel.gov.br/tarifa-branca)
- [IPCC — Emissões por km](https://www.ipcc.ch/)
