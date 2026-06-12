# ⚡ ChargeGrid Intelligence — DLM Simulator

> **GoodWe Challenge · Sprint 2 · FIAP 2026**  
> Prova de conceito funcional do sistema de Gerenciamento Dinâmico de Carga (DLM) com IA embarcada para carregamento inteligente de veículos elétricos em ambiente comercial, com foco em eficiência energética e sustentabilidade.

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

Este repositório contém a **prova de conceito funcional** da Sprint 2: um simulador CLI em Python que demonstra a lógica central do sistema — o **Dynamic Load Management (DLM)** com análise por IA e rastreamento de impacto ambiental em tempo real.

### O problema que resolvemos

Em ambientes comerciais, múltiplos veículos elétricos carregando simultaneamente em horário de pico podem gerar demandas que excedem o limite da instalação elétrica (ex: 184 kW vs limite de 120 kW), causando sobrecarga e risco de interrupção. Sem gestão inteligente, o sistema também desperdiça energia renovável disponível, recorrendo desnecessariamente à rede elétrica.

### A solução

O DLM monitora a demanda total em tempo real e, quando detecta risco de sobrecarga, aciona o **módulo de IA** que analisa o estado de todas as estações e redistribui a carga proporcionalmente. O sistema prioriza sempre energia solar, depois bateria, e recorre à rede apenas quando necessário — reduzindo custos e emissões de CO₂.

---

## 🌱 Energias Renováveis e Sustentabilidade

### Prioridade de fontes de energia

O ChargeGrid implementa uma hierarquia automática de fontes:

```
1. ☀️  Solar    → até 78 kW  (energia limpa, custo zero após instalação)
2. 🔋  Bateria  → até 30 kW  (armazenamento do excedente solar)
3. ⚡  Rede     → restante   (acionada apenas quando necessário)
```

Essa lógica garante que a maior parte da energia consumida no carregamento venha de fontes renováveis, reduzindo a dependência da rede elétrica e as emissões associadas.

### Cálculo de CO₂ evitado

O simulador calcula em tempo real o CO₂ evitado com base no fator de emissão oficial da matriz elétrica brasileira:

| Parâmetro | Valor | Fonte |
|---|---|---|
| Fator de emissão da rede BR | 0,0817 kg CO₂/kWh | MCTIC 2023 |
| Referência de km evitados | 0,089 kg CO₂/km | IPCC |

**Fórmula aplicada:**
```
CO₂ evitado (kg) = kWh solar utilizado × 0,0817
```

O relatório de tarifação exibe o impacto ambiental de cada sessão, incluindo a equivalência em quilômetros de carro a combustão evitados.

### Benefícios ambientais demonstrados

- **Redução de emissões**: cada kWh solar substitui energia da rede, evitando a emissão de 81,7 g de CO₂
- **Eficiência energética**: o DLM evita desperdício ao distribuir a carga de forma otimizada, sem desligar sessões
- **Carregamento bidirecional (V2G)**: conceito presente na arquitetura — veículos podem devolver energia à rede em horários de alta demanda
- **Gestão preditiva**: a IA recomenda horários de carregamento no período de maior irradiação solar (10h–15h)

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
  NÃO ▼                    SIM ▼
Sistema normal         IA analisa estações
Monitora CO₂ evitado         │
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
                   Log de decisão + CO₂ atualizado
```

---

## 🔧 Os 4 Pilares em Prática

| Pilar | Como é demonstrado no simulador |
|---|---|
| **1. Controle de Demanda** | Barra de demanda em tempo real, limite de 120 kW, DLM redistribuindo carga automaticamente |
| **2. Protocolos Abertos** | 6 estações com CCS2, Tipo 2 e CHAdeMO — todas via OCPP 2.0.1 |
| **3. Tarifação e Pagamento** | Cobrança por kWh (R$ 1,35/kWh) com relatório por sessão, autenticação RFID/App/QR |
| **4. Inteligência Artificial** | Módulo de IA analisa o estado da rede, explica cada decisão e recomenda horários sustentáveis |

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
  7 · Análise da IA
  8 · Ver relatório de tarifação + impacto ambiental
  9 · Ver log completo do sistema
  0 · Sair
```

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

- 🎥 **Vídeo demonstração:** https://youtu.be/9wmg-8ojMLE?si=p_nfuaNmTZyNHDjt
- 📋 **Quadro Kanban:** https://trello.com/invite/b/6a2855abfaa8d2266be81030/ATTI953e9abb1a8572be50e19a9213686f9fAA9C9467/chargegrid-intelligence-sprint-2

---

## 📚 Referências Técnicas

- [OCPP 2.0.1 — Open Charge Alliance](https://www.openchargealliance.org/)
- [GoodWe ChargeGrid](https://br.goodwe.com/carregadores-hca-g2-goodwe)
- [Fator de Emissão — MCTIC 2023](https://www.gov.br/mcti/pt-br)
- [Dynamic Load Management — IEC 61851](https://webstore.iec.ch/publication/6029)
- [Tarifa Branca ANEEL](https://www.aneel.gov.br/tarifa-branca)
- [IPCC — Emissões por km, veículos a combustão](https://www.ipcc.ch/)
