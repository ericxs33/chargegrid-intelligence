"""
ChargeGrid Intelligence — Simulador DLM
GoodWe Challenge | Sprint 2 | FIAP 2026
"""

import time
import os
import random

# ─────────────────────────────────────────────
# MÓDULO DE IA — ANÁLISE E DECISÃO
# ─────────────────────────────────────────────

def ai_typing(text, delay=0.018):
    """Efeito de digitação para simular resposta de IA em tempo real."""
    for ch in text:
        print(ch, end="", flush=True)
        time.sleep(delay)
    print()

def ai_analyze_and_decide(demand, limit, active_data, sol_pct, actions_taken):
    """
    Motor de IA simulada do ChargeGrid.
    Analisa o estado real da rede e gera raciocínio técnico baseado
    nos dados das estações ativas, mix de energia e excesso de demanda.
    """
    excess   = demand - limit
    solar_kw = SOLAR_CAP * (sol_pct / 100)
    high_load = [s for s in active_data if s["kw"] >= 20]
    low_load  = [s for s in active_data if s["kw"] < 20]
    n_active  = len(active_data)
    new_demand = demand - excess

    blocks = []

    # 1. Diagnóstico
    blocks.append(
        f"Detectei {n_active} estações ativas com demanda total de {demand:.1f} kW, "
        f"excedendo o limite de {limit:.0f} kW em {excess:.1f} kW. "
        f"Risco de sobrecarga na infraestrutura elétrica identificado."
    )

    # 2. Mix de energia
    if sol_pct >= 60:
        blocks.append(
            f"Geração solar em {sol_pct:.0f}% ({solar_kw:.1f} kW disponíveis). "
            f"Prioridade: absorver o máximo de energia fotovoltaica antes de acionar a rede elétrica."
        )
    elif sol_pct >= 30:
        blocks.append(
            f"Geração solar parcial ({sol_pct:.0f}% — {solar_kw:.1f} kW). "
            f"Sistema combinando solar + bateria para minimizar uso da rede."
        )
    else:
        blocks.append(
            f"Geração solar baixa ({sol_pct:.0f}%). "
            f"Bateria e rede elétrica como fontes primárias. "
            f"Redução de carga é crítica para evitar pico tarifário."
        )

    # 3. Estratégia de redistribuição
    if high_load:
        ids = ", ".join(s["id"] for s in high_load)
        blocks.append(
            f"Estações de alta potência identificadas: {ids}. "
            f"Aplicando throttling proporcional — redução maior em carregadores com maior carga, "
            f"preservando sessões próximas de conclusão."
        )
    if low_load:
        ids = ", ".join(s["id"] for s in low_load)
        blocks.append(
            f"Estações de baixa potência ({ids}) recebem corte mínimo "
            f"para garantir experiência do usuário."
        )

    # 4. Resultado
    blocks.append(
        f"Redistribuição concluída. Nova demanda: {new_demand:.1f} kW / {limit:.0f} kW "
        f"({(new_demand/limit*100):.0f}% do limite). Sistema operando com segurança."
    )

    # 5. Recomendação
    if sol_pct < 50:
        blocks.append(
            "Recomendação: agende sessões de alta potência para o período de maior "
            "irradiação solar (10h–15h) para reduzir custo e dependência da rede."
        )
    else:
        blocks.append(
            "Recomendação: manter DLM ativo. Com geração solar elevada, "
            "o custo por kWh está abaixo da tarifa convencional da rede."
        )

    return blocks

def print_ai_analysis(demand, limit, sol_pct, actions_taken):
    """Imprime análise da IA com efeito visual de processamento."""
    active_data = [
        {"id": sid, "kw": s["kw"], "kwh": s["kwh"], "minutes": s["minutes"]}
        for sid, s in sessions.items() if s["active"]
    ]

    print()
    print(cyan("  ┌─────────────────────────────────────────────────────┐"))
    print(cyan("  │  ") + bold("ChargeGrid IA — Módulo de Análise e Decisão") + cyan("       │"))
    print(cyan("  └─────────────────────────────────────────────────────┘"))
    print()

    steps = [
        "  Coletando dados das estações ativas...",
        "  Analisando mix de energia solar/bateria/rede...",
        "  Calculando estratégia de redistribuição de carga...",
        "  Gerando relatório de decisão...",
    ]
    for step in steps:
        print(dim(step), end="\r", flush=True)
        time.sleep(0.5)
    print(" " * 55, end="\r")

    blocks = ai_analyze_and_decide(demand, limit, active_data, sol_pct, actions_taken)

    print(f"  {bold('Análise da IA:')}\n")
    for block in blocks:
        print(f"  {dim('·')}  ", end="")
        ai_typing(block, delay=0.013)
        time.sleep(0.2)
    print()

    if actions_taken:
        print(f"  {bold('Ações executadas pelo DLM:')}")
        for a in actions_taken:
            print(green(f"    ✓ {a}"))
    print()

# ─────────────────────────────────────────────
# CONFIGURAÇÕES DO SISTEMA
# ─────────────────────────────────────────────

GRID_LIMIT_KW = 120.0
TARIFF_KWH    = 1.35
SOLAR_CAP     = 78.0
BATTERY_CAP   = 30.0
# Fator de emissão da rede elétrica brasileira (kg CO₂/kWh) — fonte: MCTIC 2023
CO2_GRID_KG_KWH = 0.0817

STATIONS = [
    {"id": "EV-01", "name": "Vaga A1", "connector": "CCS2",    "auth": "RFID",    "max_kw": 22},
    {"id": "EV-02", "name": "Vaga A2", "connector": "Tipo 2",  "auth": "App",     "max_kw": 22},
    {"id": "EV-03", "name": "Vaga B1", "connector": "CHAdeMO", "auth": "QR Code", "max_kw": 50},
    {"id": "EV-04", "name": "Vaga B2", "connector": "CCS2",    "auth": "RFID",    "max_kw": 50},
    {"id": "EV-05", "name": "Vaga C1", "connector": "Tipo 2",  "auth": "App",     "max_kw": 22},
    {"id": "EV-06", "name": "Vaga C2", "connector": "CCS2",    "auth": "QR Code", "max_kw": 22},
]

sessions   = {s["id"]: {"active": False, "kw": 0.0, "kwh": 0.0, "minutes": 0, "user": ""} for s in STATIONS}
solar_pct  = 65.0
dlm_active = False
system_log = []

# ─────────────────────────────────────────────
# UTILITÁRIOS VISUAIS
# ─────────────────────────────────────────────

def clear():
    os.system("cls" if os.name == "nt" else "clear")

def bar(value, total, width=20, fill="█", empty="░"):
    filled = min(int((value / total) * width) if total > 0 else 0, width)
    return fill * filled + empty * (width - filled)

def color(text, code):
    return f"\033[{code}m{text}\033[0m"

def green(t):  return color(t, "32")
def yellow(t): return color(t, "33")
def red(t):    return color(t, "31")
def cyan(t):   return color(t, "36")
def bold(t):   return color(t, "1")
def dim(t):    return color(t, "2")

def log(msg, level="INFO"):
    ts = time.strftime("%H:%M:%S")
    prefix = {"INFO": dim, "OK": green, "WARN": yellow, "ERR": red}.get(level, dim)
    entry = f"  [{ts}] {prefix(f'[{level}]')} {msg}"
    system_log.append(entry)
    if len(system_log) > 6:
        system_log.pop(0)

def wait(msg="Pressione ENTER para continuar..."):
    input(f"\n  {dim(msg)}")

# ─────────────────────────────────────────────
# LÓGICA DO SISTEMA
# ─────────────────────────────────────────────

def total_demand():
    return sum(s["kw"] for s in sessions.values() if s["active"])

def is_overloaded():
    return total_demand() > GRID_LIMIT_KW

def energy_mix(demand):
    solar_available = SOLAR_CAP * (solar_pct / 100)
    solar_used   = min(demand, solar_available)
    remaining    = demand - solar_used
    battery_used = min(remaining, BATTERY_CAP * (1 - solar_pct / 100) + 5)
    grid_used    = max(0.0, remaining - battery_used)
    return solar_used, battery_used, grid_used

def run_dlm():
    """Redistribuição proporcional de carga — núcleo do DLM."""
    active_ids = [sid for sid, s in sessions.items() if s["active"]]
    demand = total_demand()
    if demand <= GRID_LIMIT_KW or not active_ids:
        return []

    actions = []
    excess = demand - GRID_LIMIT_KW
    for sid in active_ids:
        s = sessions[sid]
        reduction = (s["kw"] / demand) * excess
        old_kw = s["kw"]
        s["kw"] = max(3.7, s["kw"] - reduction)
        diff = old_kw - s["kw"]
        if diff > 0.05:
            actions.append(f"{sid}: {old_kw:.1f} kW → {s['kw']:.1f} kW (↓{diff:.1f} kW)")
            log(f"DLM reduziu {sid}: {old_kw:.1f}→{s['kw']:.1f} kW", "OK")
    log(f"Demanda pós-DLM: {total_demand():.1f} kW / {GRID_LIMIT_KW} kW", "OK")
    return actions

def simulate_tick(minutes=5):
    for s in sessions.values():
        if s["active"]:
            s["kwh"] += s["kw"] * (minutes / 60)
            s["minutes"] += minutes

# ─────────────────────────────────────────────
# TELAS
# ─────────────────────────────────────────────

def header():
    print(bold(cyan("  ╔══════════════════════════════════════════════════════╗")))
    print(bold(cyan("  ║       ChargeGrid Intelligence — DLM Simulator        ║")))
    print(bold(cyan("  ║         GoodWe Challenge · FIAP Sprint 2             ║")))
    print(bold(cyan("  ╚══════════════════════════════════════════════════════╝")))
    print()

def print_dashboard():
    clear()
    header()

    demand = total_demand()
    active = sum(1 for s in sessions.values() if s["active"])
    solar_u, bat_u, grid_u = energy_mix(demand)
    revenue = sum(s["kwh"] * TARIFF_KWH for s in sessions.values())
    total_kwh_all = sum(s["kwh"] for s in sessions.values())
    solar_u_dash, _, _ = energy_mix(demand)
    solar_kwh_share = (solar_u_dash / demand * total_kwh_all) if demand > 0 else 0
    co2_avoided = solar_kwh_share * CO2_GRID_KG_KWH

    status_dlm = green("ATIVO ✓") if dlm_active else yellow("INATIVO")
    status_net = red("⚠ SOBRECARGA") if is_overloaded() else green("NORMAL ✓")
    print(f"  {'Solar:':<18} {solar_pct:.0f}%       {'DLM:':<12} {status_dlm}")
    print(f"  {'Sessões ativas:':<18} {active}/6       {'Rede:':<12} {status_net}")
    print(f"  {'Receita sessão:':<18} R$ {revenue:.2f}    {green(f'CO₂ evitado: {co2_avoided:.3f} kg')}")
    print()

    demand_bar   = bar(demand, GRID_LIMIT_KW, 30)
    demand_color = red if is_overloaded() else (yellow if demand > GRID_LIMIT_KW * 0.85 else green)
    print(f"  Demanda total  [{demand_color(demand_bar)}] {demand_color(f'{demand:.1f}')} / {GRID_LIMIT_KW} kW")
    print()

    if demand > 0:
        print(f"  Mix de energia:")
        print(f"    Solar   [{green(bar(solar_u, demand, 20))}] {solar_u:.1f} kW ({solar_u/demand*100:.0f}%)")
        print(f"    Bateria [{yellow(bar(bat_u,   demand, 20))}] {bat_u:.1f} kW ({bat_u/demand*100:.0f}%)")
        print(f"    Rede    [{cyan( bar(grid_u,  demand, 20))}] {grid_u:.1f} kW ({grid_u/demand*100:.0f}%)")
    else:
        print(f"  {dim('Nenhuma estação ativa — sem consumo.')}")
    print()

    print(f"  {'─'*58}")
    print(f"  {'ID':<8} {'Vaga':<10} {'kW':>6} {'Cap%':>6} {'kWh':>7} {'Custo':>10}  Status")
    print(f"  {'─'*58}")
    for st in STATIONS:
        sid = st["id"]
        s   = sessions[sid]
        if s["active"]:
            cap  = (s["kw"] / st["max_kw"]) * 100
            cost = s["kwh"] * TARIFF_KWH
            cap_bar = bar(s["kw"], st["max_kw"], 6)
            line = (f"  {sid:<8} {st['name']:<10} {s['kw']:>5.1f}  "
                    f"[{green(cap_bar)}]{cap:>4.0f}%  {s['kwh']:>5.2f}  R${cost:>7.2f}  "
                    f"{green('● ATIVO')} ({s['user']})")
        else:
            st_name = st["name"]
            line = f"  {dim(f'{sid:<8} {st_name:<10}')}{dim('  —      —        —       —'):>42}  {dim('○ livre')}"
        print(line)
    print(f"  {'─'*58}")

    print()
    print(f"  Interoperabilidade (OCPP 2.0.1):")
    for st in STATIONS:
        sid = st["id"]
        mark = green("✓") if sessions[sid]["active"] else dim("·")
        print(f"    {mark} {sid}  {st['connector']:<10} {st['auth']:<10} OCPP 2.0.1")

    print()
    print(f"  Log do sistema:")
    if system_log:
        for entry in system_log[-4:]:
            print(entry)
    else:
        print(dim("  (sem eventos ainda)"))
    print()

def print_menu():
    print(f"  {'─'*42}")
    print(f"  {bold('MENU PRINCIPAL')}")
    print(f"  {'─'*42}")
    print(f"  1 · Iniciar sessão de carregamento")
    print(f"  2 · Encerrar sessão")
    print(f"  3 · Simular avanço de tempo (+ 5 min)")
    print(f"  4 · Ativar / desativar DLM")
    print(f"  5 · Simular cenário de pico  ← demo principal")
    print(f"  6 · Ajustar geração solar")
    print(f"  7 · Análise da IA  ← novo")
    print(f"  8 · Ver relatório de tarifação")
    print(f"  9 · Ver log completo do sistema")
    print(f"  0 · Sair")
    print(f"  {'─'*42}")

# ─────────────────────────────────────────────
# AÇÕES
# ─────────────────────────────────────────────

def action_start_session():
    print_dashboard()
    print(bold("  INICIAR SESSÃO DE CARREGAMENTO"))
    print()

    free = [st for st in STATIONS if not sessions[st["id"]]["active"]]
    if not free:
        print(red("  Todas as estações estão ocupadas."))
        wait()
        return

    print("  Estações disponíveis:")
    for i, st in enumerate(free, 1):
        print(f"  {i}. {st['id']} — {st['name']} ({st['connector']}, max {st['max_kw']} kW)")

    try:
        choice = int(input("\n  Escolha a estação: ")) - 1
        if choice < 0 or choice >= len(free):
            raise ValueError
    except ValueError:
        print(red("  Opção inválida."))
        wait()
        return

    st   = free[choice]
    user = input("  ID do usuário (ex: USR-42): ").strip() or "USR-01"
    try:
        req_kw = float(input(f"  Potência solicitada (max {st['max_kw']} kW): "))
    except ValueError:
        req_kw = st["max_kw"]

    req_kw = min(req_kw, st["max_kw"])
    sid = st["id"]
    sessions[sid].update({"active": True, "kw": req_kw, "kwh": 0.0, "minutes": 0, "user": user})
    log(f"Sessão iniciada: {sid} | {user} | {req_kw:.1f} kW | auth: {st['auth']}", "OK")

    if is_overloaded():
        log(f"Demanda {total_demand():.1f} kW excede limite {GRID_LIMIT_KW} kW", "WARN")
        if dlm_active:
            print(yellow(f"\n  ⚠ Sobrecarga detectada! Acionando IA + DLM..."))
            time.sleep(0.5)
            demand_before = total_demand()
            actions = run_dlm()
            print_ai_analysis(demand_before, GRID_LIMIT_KW, solar_pct, actions)
        else:
            print(red(f"\n  ⚠ SOBRECARGA! Demanda: {total_demand():.1f} kW > {GRID_LIMIT_KW} kW"))
            print(yellow("  DLM está inativo. Ative-o (opção 4) para acionar a IA."))
    wait()

def action_stop_session():
    print_dashboard()
    print(bold("  ENCERRAR SESSÃO"))
    print()

    active = [st for st in STATIONS if sessions[st["id"]]["active"]]
    if not active:
        print(dim("  Nenhuma sessão ativa."))
        wait()
        return

    for i, st in enumerate(active, 1):
        sid  = st["id"]
        s    = sessions[sid]
        cost = s["kwh"] * TARIFF_KWH
        print(f"  {i}. {sid} — {s['user']} | {s['kwh']:.2f} kWh | {s['minutes']} min | R$ {cost:.2f}")

    try:
        choice = int(input("\n  Encerrar qual sessão? ")) - 1
        if choice < 0 or choice >= len(active):
            raise ValueError
    except ValueError:
        print(red("  Opção inválida."))
        wait()
        return

    st   = active[choice]
    sid  = st["id"]
    s    = sessions[sid]
    cost = s["kwh"] * TARIFF_KWH

    print(green(f"\n  ✓ Sessão {sid} encerrada."))
    print(f"    Usuário  : {s['user']}")
    print(f"    Consumo  : {s['kwh']:.3f} kWh")
    print(f"    Tempo    : {s['minutes']} minutos")
    print(f"    Conector : {st['connector']} | Auth: {st['auth']} | OCPP 2.0.1")
    print(f"    {bold(f'Total    : R$ {cost:.2f}')}")

    log(f"Sessão encerrada: {sid} | {s['kwh']:.2f} kWh | R$ {cost:.2f}", "OK")
    sessions[sid].update({"active": False, "kw": 0.0, "kwh": 0.0, "minutes": 0, "user": ""})
    wait()

def action_tick():
    simulate_tick(5)
    log("Simulação: +5 minutos. kWh acumulados.", "INFO")

def action_toggle_dlm():
    global dlm_active
    dlm_active = not dlm_active
    status = "ATIVADO" if dlm_active else "DESATIVADO"
    log(f"DLM {status} pelo operador.", "OK" if dlm_active else "WARN")

    if dlm_active and is_overloaded():
        print_dashboard()
        print(yellow("  ⚠ Sobrecarga detectada! Acionando IA + DLM..."))
        time.sleep(0.5)
        demand_before = total_demand()
        actions = run_dlm()
        print_ai_analysis(demand_before, GRID_LIMIT_KW, solar_pct, actions)
        wait()

def action_simulate_peak():
    print_dashboard()
    print(bold(yellow("  SIMULAÇÃO — HORÁRIO DE PICO")))
    print()
    print("  Iniciando todas as 6 estações simultaneamente...")
    print(dim("  (cenário típico de fim de expediente em ambiente comercial)"))
    print()
    time.sleep(0.6)

    peak_kw = [22, 22, 50, 50, 18, 22]
    users   = ["USR-10", "USR-11", "USR-12", "USR-13", "USR-14", "USR-15"]

    for i, st in enumerate(STATIONS):
        sid = st["id"]
        sessions[sid].update({
            "active": True, "kw": peak_kw[i],
            "kwh": round(random.uniform(1, 5), 2),
            "minutes": random.randint(10, 40),
            "user": users[i]
        })
        log(f"Sessão ativada (pico): {sid} | {users[i]} | {peak_kw[i]} kW", "INFO")

    demand = total_demand()
    print(red(f"  ⚠ Demanda total: {demand:.0f} kW — EXCEDE o limite de {GRID_LIMIT_KW} kW!"))
    print()

    if dlm_active:
        print(green("  DLM ativo — acionando módulo de IA..."))
        time.sleep(0.6)
        actions = run_dlm()
        print_ai_analysis(demand, GRID_LIMIT_KW, solar_pct, actions)
    else:
        print(red("  DLM INATIVO — sistema em sobrecarga!"))
        print(yellow("  Ative o DLM (opção 4) para acionar a IA e redistribuir a carga."))
    wait()

def action_solar():
    global solar_pct
    print_dashboard()
    print(bold("  AJUSTAR GERAÇÃO SOLAR"))
    print()
    print(f"  Geração atual: {solar_pct:.0f}%  ({SOLAR_CAP * solar_pct/100:.1f} kW)")
    print(dim("  0% = noite/nublado   |   100% = geração máxima"))
    print()
    try:
        val = float(input("  Nova porcentagem (0–100): "))
        solar_pct = max(0.0, min(100.0, val))
        log(f"Geração solar ajustada: {solar_pct:.0f}% ({SOLAR_CAP * solar_pct/100:.1f} kW)", "INFO")
    except ValueError:
        print(red("  Valor inválido."))
    wait()

def action_ai_analysis():
    """Opção dedicada à análise da IA — mesmo sem sobrecarga."""
    print_dashboard()
    demand = total_demand()

    if not any(s["active"] for s in sessions.values()):
        print(yellow("  Nenhuma estação ativa. Inicie sessões para a IA analisar."))
        wait()
        return

    if not is_overloaded():
        # Análise de otimização (sem sobrecarga)
        print()
        print(cyan("  ┌─────────────────────────────────────────────────────┐"))
        print(cyan("  │  ") + bold("ChargeGrid IA — Módulo de Análise e Decisão") + cyan("       │"))
        print(cyan("  └─────────────────────────────────────────────────────┘"))
        print()
        steps = ["  Analisando estado atual da rede...", "  Verificando eficiência energética...", "  Gerando recomendações..."]
        for step in steps:
            print(dim(step), end="\r", flush=True)
            time.sleep(0.5)
        print(" " * 55, end="\r")

        solar_u, bat_u, grid_u = energy_mix(demand)
        cost_kwh = TARIFF_KWH * (grid_u / demand) if demand > 0 else TARIFF_KWH
        print(f"  {bold('Análise da IA:')}\n")
        lines = [
            f"Sistema operando dentro do limite ({demand:.1f} kW / {GRID_LIMIT_KW} kW — {demand/GRID_LIMIT_KW*100:.0f}%). Sem necessidade de redistribuição.",
            f"Mix atual: {solar_u/demand*100:.0f}% solar, {bat_u/demand*100:.0f}% bateria, {grid_u/demand*100:.0f}% rede. Custo efetivo estimado: R$ {cost_kwh:.2f}/kWh.",
            f"Eficiência energética: {'ótima' if solar_pct >= 60 else 'moderada' if solar_pct >= 30 else 'baixa'}. Geração solar em {solar_pct:.0f}%.",
            "Sistema estável. DLM em modo de monitoramento contínuo.",
        ]
        for line in lines:
            print(f"  {dim('·')}  ", end="")
            ai_typing(line, delay=0.013)
            time.sleep(0.15)
    else:
        demand_before = demand
        actions = run_dlm() if dlm_active else []
        print_ai_analysis(demand_before, GRID_LIMIT_KW, solar_pct, actions)
        if not dlm_active:
            print(yellow("  (DLM inativo — ative na opção 4 para que a IA execute ações)"))
    print()
    wait()

def action_tariff_report():
    clear()
    header()
    print(bold("  RELATÓRIO DE TARIFAÇÃO"))
    print()
    print(f"  Tarifa: R$ {TARIFF_KWH}/kWh  |  Protocolo: OCPP 2.0.1")
    print()
    print(f"  {'Estação':<8} {'Usuário':<10} {'Conector':<10} {'Auth':<10} {'kWh':>7} {'Tempo':>8} {'R$':>9}")
    print(f"  {'─'*68}")

    total_kwh = total_cost = 0.0
    for st in STATIONS:
        sid = st["id"]
        s   = sessions[sid]
        if s["kwh"] > 0 or s["active"]:
            cost = s["kwh"] * TARIFF_KWH
            total_kwh  += s["kwh"]
            total_cost += cost
            status = green("● ativo") if s["active"] else dim("encerrada")
            print(f"  {sid:<8} {s['user']:<10} {st['connector']:<10} {st['auth']:<10} "
                  f"{s['kwh']:>6.2f}  {s['minutes']:>5} min  R${cost:>6.2f}  {status}")
        else:
            print(dim(f"  {sid:<8} {'—':<10} {st['connector']:<10} {st['auth']:<10} {'—':>7} {'—':>8} {'—':>9}"))

    print(f"  {'─'*68}")
    print(f"  {'TOTAL':<40} {total_kwh:>6.2f} kWh        {bold(f'R$ {total_cost:.2f}')}")

    # Sustentabilidade
    solar_u_rep, _, _ = energy_mix(total_demand())
    demand_rep = total_demand()
    solar_share_rep = (solar_u_rep / demand_rep) if demand_rep > 0 else solar_pct / 100
    solar_kwh_rep = total_kwh * solar_share_rep
    co2_avoided_rep = solar_kwh_rep * CO2_GRID_KG_KWH
    co2_equivalent_rep = co2_avoided_rep / 0.089  # km equivalentes de carro a combustão (IPCC)
    print()
    print(f"  {bold('Impacto Ambiental — Sustentabilidade')}")
    print(f"  {'─'*68}")
    print(f"  Energia solar utilizada  : {solar_kwh_rep:.3f} kWh ({solar_share_rep*100:.0f}% do total consumido)")
    print(f"  {green(f'CO₂ evitado              : {co2_avoided_rep:.4f} kg')}  {dim('(vs. uso 100% da rede)')}")
    print(f"  Equivalente em km evitados: {co2_equivalent_rep:.1f} km  {dim('(carro a combustão, IPCC)')}")
    print(f"  Fator de emissão usado   : {CO2_GRID_KG_KWH} kg CO₂/kWh  {dim('(MCTIC 2023 — Brasil)')}")
    print()
    wait()

def action_full_log():
    clear()
    header()
    print(bold("  LOG COMPLETO DO SISTEMA"))
    print()
    if system_log:
        for entry in system_log:
            print(entry)
    else:
        print(dim("  (sem eventos registrados)"))
    print()
    wait()

# ─────────────────────────────────────────────
# LOOP PRINCIPAL
# ─────────────────────────────────────────────

def main():
    log("Sistema inicializado — SEMS+ conectado", "OK")
    log(f"Limite de demanda: {GRID_LIMIT_KW} kW | Tarifa: R$ {TARIFF_KWH}/kWh", "INFO")
    log("Módulo de IA carregado — aguardando dados das estações", "INFO")

    actions_map = {
        "1": action_start_session,
        "2": action_stop_session,
        "3": action_tick,
        "4": action_toggle_dlm,
        "5": action_simulate_peak,
        "6": action_solar,
        "7": action_ai_analysis,
        "8": action_tariff_report,
        "9": action_full_log,
    }

    while True:
        print_dashboard()
        print_menu()
        choice = input("  Opção: ").strip()

        if choice == "0":
            clear()
            print(bold(cyan("\n  ChargeGrid Intelligence — sessão encerrada.\n")))
            break
        elif choice in actions_map:
            actions_map[choice]()
        else:
            log("Opção inválida.", "WARN")

if __name__ == "__main__":
    main()