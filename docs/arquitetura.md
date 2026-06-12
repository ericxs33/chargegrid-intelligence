# Arquitetura Técnica — ChargeGrid Intelligence

## Visão Geral

O simulador é um sistema CLI single-file (`main.py`) organizado em três camadas:

### 1. Camada de Dados
Estado global das 6 estações de carregamento, incluindo potência alocada, kWh consumidos, usuário autenticado e método de autenticação (RFID, App SEMS+, QR Code).

### 2. Camada de Lógica (DLM Engine)
- `total_demand()` — soma a demanda de todas as sessões ativas
- `energy_mix()` — calcula a divisão Solar / Bateria / Rede com base na geração solar atual
- `run_dlm()` — algoritmo de redistribuição proporcional: reduz mais quem consome mais, respeitando mínimo de 3,7 kW por estação (carregamento mínimo viável)
- `simulate_tick()` — avança o tempo e acumula kWh nas sessões ativas

### 3. Camada de IA
- `ai_analyze_and_decide()` — recebe os dados reais da rede e gera blocos de raciocínio técnico contextualizados: diagnóstico, análise do mix, estratégia de redistribuição, resultado e recomendação
- `print_ai_analysis()` — exibe o raciocínio com efeito de digitação em tempo real, simulando uma resposta de modelo de linguagem

## Algoritmo DLM

```python
# Pseudocódigo do núcleo de redistribuição
excesso = demanda_total - limite_120kw

para cada estação ativa:
    reducao = (potencia_estacao / demanda_total) * excesso
    nova_potencia = max(3.7kW, potencia_atual - reducao)
```

Propriedades do algoritmo:
- **Proporcional**: quem mais consome, mais cede
- **Justo**: nenhuma estação é desligada, apenas throttled
- **Seguro**: mínimo de 3,7 kW garante carregamento contínuo (padrão AC Modo 2)

## Mix de Energia

Ordem de prioridade (igual ao ChargeGrid real):

```
1. Solar  → até 78 kW (configurável via slider 0–100%)
2. Bateria → até 30 kW (complementa o solar)
3. Rede   → restante (acionada apenas quando necessário)
```

## Protocolo OCPP 2.0.1

Cada estação no simulador possui:
- Conector padronizado (CCS2, Tipo 2 ou CHAdeMO)
- Método de autenticação (RFID, App SEMS+, QR Code)
- Comunicação via OCPP 2.0.1 — protocolo aberto, independente de fabricante

Isso demonstra o **Pilar 2 (Interoperabilidade)**: diferentes conectores e autenticações coexistindo no mesmo sistema de gestão.

## Tarifação

```
Custo da sessão = kWh consumidos × R$ 1,35/kWh
kWh = potência_alocada (kW) × tempo (h)
```

Modelos suportados: por kWh (implementado), por tempo, por assinatura (mencionados no relatório).
