# ⚡ ChargeGrid Intelligence — DLM Simulator

> **GoodWe Challenge · Sprint 2 · FIAP 2026**  
> Prova de conceito funcional do sistema de Gerenciamento Dinâmico de Carga (DLM) com IA embarcada para carregamento inteligente de veículos elétricos em ambiente comercial.

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

O **ChargeGrid Intelligence** é o ecossistema da GoodWe para carregamento inteligente de veículos elétricos. Integra carregadores, painéis solares, baterias e inteligência artificial em uma única plataforma.

Este repositório contém a **prova de conceito funcional** da Sprint 2: um simulador CLI em Python que demonstra a lógica central do sistema — o **Dynamic Load Management (DLM)** com análise por IA.

### O problema que resolvemos

Em ambientes comerciais, múltiplos veículos elétricos carregando simultaneamente em horário de pico podem gerar demandas que excedem o limite da instalação elétrica (ex: 184 kW vs limite de 120 kW), causando sobrecarga e risco de interrupção.

### A solução

O DLM monitora a demanda total em tempo real e, quando detecta risco de sobrecarga, aciona o **módulo de IA** que analisa o estado de todas as estações e redistribui a carga proporcionalmente — sem interromper nenhuma sessão de carregamento.

---

## 🏗️ Arquitetura do Sistema

```
┌─────────────────────────────────────────────────────────┐
│                  ChargeGrid Intelligence                  │
│                                                           │
│  ┌─────────┐   ┌─────────┐   ┌──────────┐               │
│  │  Solar  │   │Bateria  │   │  Rede    │  Fontes        │
│  │ 78 kW   │──▶│ 30 kW   │──▶│ Elétrica │  de energia   │
│  └─────────┘   └─────────┘   └──────────┘               │
│        │             │             │                      │
│        └─────────────┴─────────────┘                     │
│                      │                                    │
│              ┌───────▼────────┐                          │
│              │  DLM Engine    │  Gerenciamento            │
│              │  + Módulo IA   │  Dinâmico de Carga       │
│              └───────┬────────┘                          │
│                      │  OCPP 2.0.1                       │
│        ┌─────────────┼─────────────┐                     │
│        ▼             ▼             ▼                      │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐               │
│  │  EV-01   │  │  EV-03   │  │  EV-05   │  Estações     │
│  │  CCS2    │  │ CHAdeMO  │  │  Tipo 2  │  de carga     │
│  │  22 kW   │  │  50 kW   │  │  22 kW   │               │
│  └──────────┘  └──────────┘  └──────────┘               │
└─────────────────────────────────────────────────────────┘
```

### Fluxo de decisão do DLM

```
Sessão iniciada
      │
      ▼
Demanda total > 120 kW?
      │
  NÃO ▼               SIM ▼
Sistema normal    IA analisa estações
                        │
                        ▼
              Calcula excesso de carga
                        │
                        ▼
              Redução proporcional por estação
              (maior carga = maior redução)
                        │
                        ▼
              Demanda volta ao limite seguro
                        │
                        ▼
              Log de decisão gerado
```

---

## 🔧 Os 4 Pilares em Prática

| Pilar | Como é demonstrado no simulador |
|---|---|
| **1. Controle de Demanda** | Barra de demanda em tempo real, limite de 120 kW, DLM redistribuindo carga |
| **2. Protocolos Abertos** | 6 estações com CCS2, Tipo 2 e CHAdeMO — todas via OCPP 2.0.1 |
| **3. Tarifação e Pagamento** | Cobrança por kWh (R$ 1,35/kWh) com relatório por sessão e autenticação RFID/App/QR |
| **4. Inteligência Artificial** | Módulo de IA analisa o estado da rede e explica cada decisão de redistribuição |

---

## 🚀 Como executar

### Pré-requisitos

- Python 3.10 ou superior
- Nenhuma biblioteca externa necessária (apenas biblioteca padrão)

### Instalação e execução

```bash
# Clone o repositório
git clone https://github.com/ericxs33/chargegrid-intelligence.git
cd chargegrid-intelligence

# Execute o simulador
python main.py
```

### Compatibilidade

| Sistema | Status |
|---|---|
| Windows 10/11 | ✅ Compatível |
| macOS | ✅ Compatível |
| Linux | ✅ Compatível |

> **Nota Windows:** para cores ANSI funcionarem corretamente, use o **Windows Terminal** ou **PowerShell** (não o prompt clássico `cmd`).

---

## 📋 Menu do Simulador

```
  1 · Iniciar sessão de carregamento
  2 · Encerrar sessão
  3 · Simular avanço de tempo (+ 5 min)
  4 · Ativar / desativar DLM
  5 · Simular cenário de pico  ← demo principal
  6 · Ajustar geração solar
  7 · Análise da IA            ← módulo de IA
  8 · Ver relatório de tarifação
  9 · Ver log completo do sistema
  0 · Sair
```

### Demo recomendada (para o vídeo)

1. Abra o sistema — veja o log com `Módulo de IA carregado`
2. Inicie 2–3 sessões manualmente (opção **1**)
3. Rode a **opção 7** — IA analisa o estado atual da rede
4. Simule o pico (opção **5**) com DLM **desativado** — barra fica vermelha
5. Ative o DLM (opção **4**) — IA digita o raciocínio ao vivo, sistema volta ao verde
6. Abra o relatório de tarifação (opção **8**)

---

## 📁 Estrutura do Repositório

```
chargegrid-intelligence/
│
├── main.py          # Simulador completo — ponto de entrada
├── README.md        # Este arquivo
│
├── docs/
│   └── arquitetura.md   # Detalhamento técnico da solução
│
└── assets/
    └── (screenshots do simulador)
```

---

## 🔗 Links

- 🎥 **Vídeo demonstração:** https://youtu.be/B-EpYfbEh6Y
- 📋 **Quadro Kanban:** https://trello.com/invite/b/6a2855abfaa8d2266be81030/ATTI953e9abb1a8572be50e19a9213686f9fAA9C9467/chargegrid-intelligence-sprint-2
- 📄 **Sprint 1:** Pesquisa, Problemas e Soluções

---

## 📚 Referências Técnicas

- [OCPP 2.0.1 — Open Charge Alliance](https://www.openchargealliance.org/)
- [GoodWe ChargeGrid](https://br.goodwe.com/carregadores-hca-g2-goodwe)
- [Dynamic Load Management — IEC 61851](https://webstore.iec.ch/publication/6029)
- [Tarifa Branca ANEEL](https://www.aneel.gov.br/tarifa-branca)
