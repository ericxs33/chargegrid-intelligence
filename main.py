"""
ChargeGrid Intelligence — App Desktop Completo
GoodWe Challenge · FIAP Sprint 4 · 100% Python Standard Library
"""

import os
import csv
import time
import random
import threading
import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime

# ─────────────────────────────────────────────
# CONFIGURAÇÕES
# ─────────────────────────────────────────────

CSV_FILE        = os.path.join(os.path.dirname(os.path.abspath(__file__)), "sessions.csv")
LOG_FILE        = os.path.join(os.path.dirname(os.path.abspath(__file__)), "system.log")
GRID_LIMIT_KW   = 120.0
TARIFF_KWH      = 1.35
SOLAR_CAP       = 78.0
BATTERY_CAP     = 30.0
CO2_FACTOR      = 0.0817

FONT            = "Segoe UI"
C_BG            = "#1C1C1C"
C_SURFACE       = "#2A2A2A"
C_SURFACE2      = "#333333"
C_BORDER        = "#3D3D3D"
C_TEXT          = "#F0F0F0"
C_DIM           = "#9A9A9A"
C_ACCENT        = "#E91C5D"
C_ACCENT2       = "#FF2E70"
C_GREEN         = "#1D9E75"
C_AMBER         = "#BA7517"
C_BLUE          = "#378ADD"
C_RED           = "#E24B4A"

STATIONS_DEF = [
    {"id": "EV-01", "name": "Vaga A1", "connector": "CCS2",    "auth": "RFID",    "max_kw": 22},
    {"id": "EV-02", "name": "Vaga A2", "connector": "Tipo 2",  "auth": "App",     "max_kw": 22},
    {"id": "EV-03", "name": "Vaga B1", "connector": "CHAdeMO", "auth": "QR Code", "max_kw": 50},
    {"id": "EV-04", "name": "Vaga B2", "connector": "CCS2",    "auth": "RFID",    "max_kw": 50},
    {"id": "EV-05", "name": "Vaga C1", "connector": "Tipo 2",  "auth": "App",     "max_kw": 22},
    {"id": "EV-06", "name": "Vaga C2", "connector": "CCS2",    "auth": "QR Code", "max_kw": 22},
]

# ─────────────────────────────────────────────
# ESTADO DO SISTEMA
# ─────────────────────────────────────────────

sessions = {
    s["id"]: {"active": False, "kw": 0.0, "kwh": 0.0, "minutes": 0, "user": "", "start": ""}
    for s in STATIONS_DEF
}
solar_pct  = 65.0
dlm_active = False

# ─────────────────────────────────────────────
# LÓGICA DO SISTEMA
# ─────────────────────────────────────────────

def total_demand():
    return sum(s["kw"] for s in sessions.values() if s["active"])

def is_overloaded():
    return total_demand() > GRID_LIMIT_KW

def energy_mix(demand):
    solar_av = SOLAR_CAP * (solar_pct / 100)
    solar_u  = min(demand, solar_av)
    rem      = demand - solar_u
    bat_u    = min(rem, BATTERY_CAP * (1 - solar_pct / 100) + 5)
    grid_u   = max(0.0, rem - bat_u)
    return solar_u, bat_u, grid_u

def run_dlm():
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
            actions.append(f"{sid}: {old_kw:.1f}→{s['kw']:.1f} kW (↓{diff:.1f})")
    return actions

def simulate_tick(minutes=5):
    for s in sessions.values():
        if s["active"]:
            s["kwh"] += s["kw"] * (minutes / 60)
            s["minutes"] += minutes

def init_csv():
    if not os.path.exists(CSV_FILE):
        with open(CSV_FILE, "w", newline="", encoding="utf-8") as f:
            csv.writer(f).writerow([
                "data_hora","estacao","usuario","conector","auth",
                "kwh","tempo_min","custo_brl","fonte_energia",
                "solar_pct","co2_evitado_kg","dlm_ativo","protocolo"
            ])

def save_session_csv(sid, st, s):
    demand = total_demand() or 1
    solar_u, bat_u, grid_u = energy_mix(demand)
    total = solar_u + bat_u + grid_u or 1
    solar_share = solar_u / total
    fonte = "Solar" if solar_share > 0.6 else ("Misto Solar+Bateria" if solar_share > 0.3 else "Rede")
    co2 = s["kwh"] * solar_share * CO2_FACTOR
    with open(CSV_FILE, "a", newline="", encoding="utf-8") as f:
        csv.writer(f).writerow([
            datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            sid, s["user"], st["connector"], st["auth"],
            f"{s['kwh']:.4f}", s["minutes"], f"{s['kwh']*TARIFF_KWH:.2f}",
            fonte, f"{solar_pct:.0f}", f"{co2:.4f}",
            "Sim" if dlm_active else "Não", "OCPP 2.0.1"
        ])

def persist_log(msg, level="INFO"):
    ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(f"[{ts}] [{level}] {msg}\n")

def load_csv_rows():
    rows = []
    if not os.path.exists(CSV_FILE):
        return rows
    try:
        with open(CSV_FILE, "r", encoding="utf-8") as f:
            reader = csv.reader(f)
            next(reader, None)
            for r in reader:
                if len(r) >= 11 and r[1].strip():
                    rows.append({
                        "datetime": r[0], "station": r[1], "user": r[2],
                        "connector": r[3], "kwh": float(r[5] or 0),
                        "minutes": int(r[6] or 0), "cost": float(r[7] or 0),
                        "source": r[8] if len(r)>8 else "—",
                        "solar_pct": float(r[9] or 0) if len(r)>9 else 0,
                        "co2": float(r[10] or 0) if len(r)>10 else 0,
                        "dlm": r[11] if len(r)>11 else "Não",
                    })
    except Exception:
        pass
    return rows

def ai_analysis_text():
    demand = total_demand()
    active_data = [{"id": sid, "kw": s["kw"]} for sid, s in sessions.items() if s["active"]]
    solar_u, bat_u, grid_u = energy_mix(demand)
    n = len(active_data)
    if n == 0:
        return "Nenhuma estação ativa. Aguardando sessões de carregamento."
    lines = []
    if is_overloaded():
        excess = demand - GRID_LIMIT_KW
        lines.append(f"⚠ Sobrecarga detectada: {n} estações ativas, demanda {demand:.1f} kW excede o limite de {GRID_LIMIT_KW:.0f} kW em {excess:.1f} kW.")
        high = [s["id"] for s in active_data if s["kw"] >= 20]
        if high:
            lines.append(f"Estações de alta potência: {', '.join(high)}. Aplicando throttling proporcional.")
        if dlm_active:
            lines.append("DLM ativo — redistribuindo carga automaticamente para proteger a infraestrutura.")
        else:
            lines.append("DLM inativo — ative o DLM para redistribuir a carga automaticamente.")
    else:
        lines.append(f"Sistema operando normalmente. Demanda: {demand:.1f} kW / {GRID_LIMIT_KW:.0f} kW ({demand/GRID_LIMIT_KW*100:.0f}%).")
    if demand > 0:
        lines.append(f"Mix energético: {solar_u/demand*100:.0f}% solar, {bat_u/demand*100:.0f}% bateria, {grid_u/demand*100:.0f}% rede.")
    if solar_pct >= 60:
        lines.append(f"Geração solar elevada ({solar_pct:.0f}%). Aproveitamento máximo de energia renovável.")
    elif solar_pct < 30:
        lines.append(f"Geração solar baixa ({solar_pct:.0f}%). Recomenda-se agendar sessões de maior potência para horário de pico solar (10h–15h).")
    total_kwh = sum(s["kwh"] for s in sessions.values())
    solar_kwh = total_kwh * (solar_u / demand if demand > 0 else solar_pct / 100)
    co2 = solar_kwh * CO2_FACTOR
    lines.append(f"CO₂ evitado na sessão atual: {co2:.4f} kg (fator MCTIC 2023: {CO2_FACTOR} kg/kWh).")
    return "\n\n".join(lines)

# ─────────────────────────────────────────────
# APP PRINCIPAL
# ─────────────────────────────────────────────

class ChargeGridApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("ChargeGrid Intelligence — GoodWe Challenge · FIAP Sprint 4")
        self.geometry("1100x780")
        self.minsize(960, 680)
        self.configure(bg=C_BG)

        init_csv()
        self.setup_styles()
        self.build_header()
        self.build_notebook()
        self.build_footer()

        persist_log("App inicializado — SEMS+ conectado", "OK")
        self.after(500, self.refresh_all)
        self.after(2000, self.auto_refresh)

    # ── ESTILOS ──────────────────────────────
    def setup_styles(self):
        s = ttk.Style(self)
        s.theme_use("clam")
        s.configure("TNotebook", background=C_BG, borderwidth=0)
        s.configure("TNotebook.Tab", background=C_SURFACE, foreground=C_DIM,
                    font=(FONT, 10, "bold"), padding=(18, 8), borderwidth=0)
        s.map("TNotebook.Tab",
              background=[("selected", C_SURFACE2)],
              foreground=[("selected", C_TEXT)])
        s.configure("Treeview", background=C_SURFACE, foreground=C_TEXT,
                    fieldbackground=C_SURFACE, rowheight=24, font=(FONT, 9), borderwidth=0)
        s.configure("Treeview.Heading", background=C_SURFACE2, foreground=C_DIM,
                    font=(FONT, 9, "bold"), relief="flat")
        s.map("Treeview", background=[("selected", C_ACCENT)], foreground=[("selected", "#FFF")])
        s.configure("Vertical.TScrollbar", background=C_SURFACE2, troughcolor=C_BG,
                    arrowcolor=C_DIM, borderwidth=0, relief="flat")

    # ── HEADER ───────────────────────────────
    def build_header(self):
        hf = tk.Frame(self, bg=C_SURFACE, height=60, padx=20, pady=10)
        hf.pack(fill="x")
        hf.pack_propagate(False)

        logo = tk.Label(hf, text="⚡", bg=C_ACCENT, fg="#FFF",
                        font=(FONT, 14, "bold"), width=3)
        logo.pack(side="left", padx=(0, 12))

        tb = tk.Frame(hf, bg=C_SURFACE)
        tb.pack(side="left")
        tk.Label(tb, text="ChargeGrid Intelligence", bg=C_SURFACE, fg=C_TEXT,
                 font=(FONT, 13, "bold")).pack(anchor="w")
        tk.Label(tb, text="GoodWe Challenge · FIAP Sprint 4 · Solução Final Integrada",
                 bg=C_SURFACE, fg=C_DIM, font=(FONT, 9)).pack(anchor="w")

        ab = tk.Frame(hf, bg=C_SURFACE)
        ab.pack(side="right")
        self.lbl_status = tk.Label(ab, text="● SEMS+ Conectado", bg="#3B1E28",
                                   fg=C_ACCENT, font=(FONT, 9, "bold"), padx=10, pady=4)
        self.lbl_status.pack(side="left", padx=(0, 10))

    # ── NOTEBOOK ─────────────────────────────
    def build_notebook(self):
        self.nb = ttk.Notebook(self)
        self.nb.pack(fill="both", expand=True, padx=0, pady=0)

        self.tab_control = tk.Frame(self.nb, bg=C_BG)
        self.tab_ai      = tk.Frame(self.nb, bg=C_BG)
        self.tab_data    = tk.Frame(self.nb, bg=C_BG)

        self.nb.add(self.tab_control, text="  ⚡ Painel de Controle  ")
        self.nb.add(self.tab_ai,      text="  🤖 IA e Log  ")
        self.nb.add(self.tab_data,    text="  📊 Dashboard e Dados  ")

        self.build_tab_control()
        self.build_tab_ai()
        self.build_tab_data()

    # ═══════════════════════════════════════════
    # ABA 1 — PAINEL DE CONTROLE
    # ═══════════════════════════════════════════
    def build_tab_control(self):
        pad = {"padx": 16, "pady": 12}
        main = tk.Frame(self.tab_control, bg=C_BG, **pad)
        main.pack(fill="both", expand=True)

        # — Status geral —
        status_row = tk.Frame(main, bg=C_BG)
        status_row.pack(fill="x", pady=(0, 10))

        self.lbl_demand_val = self._stat_card(status_row, "DEMANDA TOTAL", "0.0 kW", C_GREEN, 0)
        self.lbl_solar_val  = self._stat_card(status_row, "GERAÇÃO SOLAR", f"{solar_pct:.0f}%", C_AMBER, 1)
        self.lbl_sessions_v = self._stat_card(status_row, "SESSÕES ATIVAS", "0 / 6", C_BLUE, 2)
        self.lbl_revenue_v  = self._stat_card(status_row, "RECEITA ATUAL", "R$ 0.00", C_ACCENT, 3)
        for i in range(4):
            status_row.columnconfigure(i, weight=1, uniform="stat")

        # — Barra de demanda —
        bar_frame = tk.Frame(main, bg=C_SURFACE, padx=14, pady=10,
                             highlightbackground=C_BORDER, highlightthickness=1)
        bar_frame.pack(fill="x", pady=(0, 10))
        tk.Label(bar_frame, text="DEMANDA vs LIMITE (120 kW)", bg=C_SURFACE,
                 fg=C_DIM, font=(FONT, 8, "bold")).pack(anchor="w")
        self.canvas_bar = tk.Canvas(bar_frame, bg=C_SURFACE, height=24, highlightthickness=0)
        self.canvas_bar.pack(fill="x", pady=(4, 0))
        self.lbl_bar_info = tk.Label(bar_frame, text="", bg=C_SURFACE, fg=C_DIM, font=(FONT, 8))
        self.lbl_bar_info.pack(anchor="e")

        # — Mix de energia —
        mix_frame = tk.Frame(main, bg=C_SURFACE, padx=14, pady=10,
                             highlightbackground=C_BORDER, highlightthickness=1)
        mix_frame.pack(fill="x", pady=(0, 10))
        tk.Label(mix_frame, text="MIX DE ENERGIA", bg=C_SURFACE,
                 fg=C_DIM, font=(FONT, 8, "bold")).pack(anchor="w")
        self.canvas_mix_ctrl = tk.Canvas(mix_frame, bg=C_SURFACE, height=18, highlightthickness=0)
        self.canvas_mix_ctrl.pack(fill="x", pady=(4, 2))
        self.lbl_mix_info = tk.Label(mix_frame, text="", bg=C_SURFACE, fg=C_DIM, font=(FONT, 8))
        self.lbl_mix_info.pack(anchor="w")

        # — Cards das estações —
        tk.Label(main, text="ESTAÇÕES DE CARREGAMENTO — OCPP 2.0.1",
                 bg=C_BG, fg=C_DIM, font=(FONT, 8, "bold")).pack(anchor="w", pady=(0, 6))
        stations_grid = tk.Frame(main, bg=C_BG)
        stations_grid.pack(fill="x", pady=(0, 10))
        self.station_cards = {}
        for i in range(6):
            stations_grid.columnconfigure(i, weight=1, uniform="st")
        for i, st in enumerate(STATIONS_DEF):
            card = self._build_station_card(stations_grid, st, i)
            self.station_cards[st["id"]] = card

        # — Botões de ação —
        btn_frame = tk.Frame(main, bg=C_BG)
        btn_frame.pack(fill="x")
        self._action_btn(btn_frame, "⏱ +5 min", self.action_tick, C_SURFACE2)
        self._action_btn(btn_frame, "🔀 DLM", self.action_toggle_dlm, C_SURFACE2)
        self._action_btn(btn_frame, "⚡ Simular Pico", self.action_peak, C_RED)
        self._action_btn(btn_frame, "🗑 Limpar CSV", self.action_clear_csv, C_SURFACE2)

        # — Slider solar —
        slider_frame = tk.Frame(main, bg=C_BG)
        slider_frame.pack(fill="x", pady=(8, 0))
        tk.Label(slider_frame, text="☀ Geração Solar:", bg=C_BG,
                 fg=C_DIM, font=(FONT, 9)).pack(side="left", padx=(0, 8))
        self.solar_var = tk.DoubleVar(value=solar_pct)
        sl = tk.Scale(slider_frame, from_=0, to=100, orient="horizontal",
                      variable=self.solar_var, command=self.on_solar_change,
                      bg=C_BG, fg=C_TEXT, troughcolor=C_SURFACE2,
                      highlightthickness=0, activebackground=C_ACCENT,
                      font=(FONT, 9), length=300, sliderlength=16)
        sl.pack(side="left")
        self.lbl_solar_slider = tk.Label(slider_frame, text=f"{solar_pct:.0f}%  ({SOLAR_CAP*solar_pct/100:.0f} kW)",
                                         bg=C_BG, fg=C_AMBER, font=(FONT, 9, "bold"))
        self.lbl_solar_slider.pack(side="left", padx=10)

    def _stat_card(self, parent, title, value, color, col):
        card = tk.Frame(parent, bg=C_SURFACE, padx=12, pady=8,
                        highlightbackground=C_BORDER, highlightthickness=1)
        card.grid(row=0, column=col, sticky="nsew",
                  padx=(0, 6) if col < 3 else 0)
        tk.Label(card, text=title, bg=C_SURFACE, fg=C_DIM,
                 font=(FONT, 8, "bold")).pack(anchor="w")
        lbl = tk.Label(card, text=value, bg=C_SURFACE, fg=color,
                       font=(FONT, 14, "bold"), pady=2)
        lbl.pack(anchor="w")
        return lbl

    def _build_station_card(self, parent, st, col):
        sid = st["id"]
        card = tk.Frame(parent, bg=C_SURFACE, padx=10, pady=8,
                        highlightbackground=C_BORDER, highlightthickness=1)
        card.grid(row=0, column=col, sticky="nsew", padx=(0, 6) if col < 5 else 0)

        lbl_id = tk.Label(card, text=sid, bg=C_SURFACE, fg=C_DIM,
                          font=(FONT, 8, "bold"))
        lbl_id.pack(anchor="w")
        lbl_name = tk.Label(card, text=st["name"], bg=C_SURFACE, fg=C_TEXT,
                            font=(FONT, 9, "bold"))
        lbl_name.pack(anchor="w")
        lbl_conn = tk.Label(card, text=f"{st['connector']} · {st['auth']}",
                            bg=C_SURFACE, fg=C_DIM, font=(FONT, 8))
        lbl_conn.pack(anchor="w")

        canvas_bar = tk.Canvas(card, bg=C_SURFACE, height=6, highlightthickness=0)
        canvas_bar.pack(fill="x", pady=(4, 2))

        lbl_kw = tk.Label(card, text="— kW", bg=C_SURFACE, fg=C_DIM,
                          font=(FONT, 9, "bold"))
        lbl_kw.pack(anchor="w")
        lbl_kwh = tk.Label(card, text="0.000 kWh · R$ 0.00",
                           bg=C_SURFACE, fg=C_DIM, font=(FONT, 8))
        lbl_kwh.pack(anchor="w")

        btn = tk.Button(card, text="Iniciar", bg=C_GREEN, fg="#FFF",
                        relief="flat", font=(FONT, 8, "bold"),
                        cursor="hand2", pady=2,
                        command=lambda s=sid: self.toggle_station(s))
        btn.pack(fill="x", pady=(6, 0))

        return {
            "frame": card, "lbl_kw": lbl_kw, "lbl_kwh": lbl_kwh,
            "btn": btn, "canvas_bar": canvas_bar, "lbl_id": lbl_id
        }

    def _action_btn(self, parent, text, cmd, color):
        tk.Button(parent, text=text, bg=color, fg=C_TEXT, relief="flat",
                  font=(FONT, 9, "bold"), padx=14, pady=6, cursor="hand2",
                  command=cmd, activebackground=C_SURFACE2,
                  activeforeground=C_TEXT).pack(side="left", padx=(0, 8))

    # ═══════════════════════════════════════════
    # ABA 2 — IA E LOG
    # ═══════════════════════════════════════════
    def build_tab_ai(self):
        main = tk.Frame(self.tab_ai, bg=C_BG, padx=16, pady=12)
        main.pack(fill="both", expand=True)

        # Análise da IA
        ia_frame = tk.Frame(main, bg=C_SURFACE, padx=14, pady=12,
                            highlightbackground=C_BORDER, highlightthickness=1)
        ia_frame.pack(fill="x", pady=(0, 12))

        hdr = tk.Frame(ia_frame, bg=C_SURFACE)
        hdr.pack(fill="x", pady=(0, 8))
        tk.Label(hdr, text="🤖 ChargeGrid IA — Módulo de Análise e Decisão",
                 bg=C_SURFACE, fg=C_TEXT, font=(FONT, 11, "bold")).pack(side="left")
        tk.Button(hdr, text="Analisar agora", bg=C_ACCENT, fg="#FFF",
                  relief="flat", font=(FONT, 9, "bold"), padx=12, pady=3,
                  cursor="hand2", command=self.run_ai_analysis).pack(side="right")

        self.txt_ai = tk.Text(ia_frame, bg=C_SURFACE2, fg=C_TEXT,
                              font=(FONT, 10), relief="flat", height=8,
                              wrap="word", state="disabled",
                              insertbackground=C_ACCENT)
        self.txt_ai.pack(fill="both", expand=True)

        # Log
        log_frame = tk.Frame(main, bg=C_SURFACE, padx=14, pady=12,
                             highlightbackground=C_BORDER, highlightthickness=1)
        log_frame.pack(fill="both", expand=True)

        hdr2 = tk.Frame(log_frame, bg=C_SURFACE)
        hdr2.pack(fill="x", pady=(0, 8))
        tk.Label(hdr2, text="📋 Log do Sistema", bg=C_SURFACE,
                 fg=C_TEXT, font=(FONT, 11, "bold")).pack(side="left")
        tk.Button(hdr2, text="Limpar log", bg=C_SURFACE2, fg=C_DIM,
                  relief="flat", font=(FONT, 9), padx=10, pady=3,
                  cursor="hand2", command=self.clear_log_display).pack(side="right")

        self.txt_log = tk.Text(log_frame, bg=C_SURFACE2, fg=C_DIM,
                               font=("Consolas", 9), relief="flat",
                               wrap="word", state="disabled")
        sb = ttk.Scrollbar(log_frame, orient="vertical", command=self.txt_log.yview)
        self.txt_log.configure(yscrollcommand=sb.set)
        self.txt_log.pack(side="left", fill="both", expand=True)
        sb.pack(side="right", fill="y")

    # ═══════════════════════════════════════════
    # ABA 3 — DASHBOARD E DADOS
    # ═══════════════════════════════════════════
    def build_tab_data(self):
        main = tk.Frame(self.tab_data, bg=C_BG, padx=16, pady=12)
        main.pack(fill="both", expand=True)

        # KPIs
        kpi_row = tk.Frame(main, bg=C_BG)
        kpi_row.pack(fill="x", pady=(0, 10))
        for i in range(4):
            kpi_row.columnconfigure(i, weight=1, uniform="kpi")
        self.kpi_sessions = self._kpi(kpi_row, 0, "SESSÕES REGISTRADAS", "0", C_ACCENT)
        self.kpi_kwh      = self._kpi(kpi_row, 1, "ENERGIA TOTAL (kWh)", "0.00", C_BLUE)
        self.kpi_revenue  = self._kpi(kpi_row, 2, "RECEITA TOTAL", "R$ 0.00", C_AMBER)
        self.kpi_co2      = self._kpi(kpi_row, 3, "CO₂ EVITADO (kg)", "0.0000", C_GREEN)

        # Sustentabilidade
        sust = tk.Frame(main, bg=C_SURFACE, padx=14, pady=10,
                        highlightbackground=C_BORDER, highlightthickness=1)
        sust.pack(fill="x", pady=(0, 10))
        self.lbl_sust = tk.Label(sust,
            text="🌱 Sustentabilidade: aguardando dados...",
            bg=C_SURFACE, fg=C_TEXT, font=(FONT, 10))
        self.lbl_sust.pack(side="left")

        # Gráficos
        charts = tk.Frame(main, bg=C_BG)
        charts.pack(fill="x", pady=(0, 10))
        charts.columnconfigure(0, weight=1, uniform="ch")
        charts.columnconfigure(1, weight=1, uniform="ch")

        c1 = tk.Frame(charts, bg=C_SURFACE, padx=14, pady=10,
                      highlightbackground=C_BORDER, highlightthickness=1)
        c1.grid(row=0, column=0, sticky="nsew", padx=(0, 6))
        tk.Label(c1, text="⚡ CONSUMO POR ESTAÇÃO (kWh)", bg=C_SURFACE,
                 fg=C_DIM, font=(FONT, 8, "bold")).pack(anchor="w")
        self.canvas_stations = tk.Canvas(c1, bg=C_SURFACE, height=130, highlightthickness=0)
        self.canvas_stations.pack(fill="both", expand=True, pady=(4, 0))

        c2 = tk.Frame(charts, bg=C_SURFACE, padx=14, pady=10,
                      highlightbackground=C_BORDER, highlightthickness=1)
        c2.grid(row=0, column=1, sticky="nsew", padx=(6, 0))
        tk.Label(c2, text="☀ MIX ENERGÉTICO", bg=C_SURFACE,
                 fg=C_DIM, font=(FONT, 8, "bold")).pack(anchor="w")
        self.canvas_energy = tk.Canvas(c2, bg=C_SURFACE, height=130, highlightthickness=0)
        self.canvas_energy.pack(fill="both", expand=True, pady=(4, 0))

        # Tabela
        tbl = tk.Frame(main, bg=C_SURFACE, padx=14, pady=10,
                       highlightbackground=C_BORDER, highlightthickness=1)
        tbl.pack(fill="both", expand=True)

        hdr = tk.Frame(tbl, bg=C_SURFACE)
        hdr.pack(fill="x", pady=(0, 6))
        tk.Label(hdr, text="📋 HISTÓRICO DE SESSÕES — sessions.csv",
                 bg=C_SURFACE, fg=C_DIM, font=(FONT, 9, "bold")).pack(side="left")
        self.lbl_tbl_count = tk.Label(hdr, text="0 registros",
                                      bg=C_SURFACE, fg=C_DIM, font=(FONT, 9))
        self.lbl_tbl_count.pack(side="right")

        cols = ("datetime","station","user","connector","kwh","minutes","cost","source","co2")
        self.tree = ttk.Treeview(tbl, columns=cols, show="headings", selectmode="browse")
        heads = ["Data/Hora","Estação","Usuário","Conector","kWh","Tempo","Custo","Fonte","CO₂ (kg)"]
        widths = [140, 70, 80, 80, 80, 60, 80, 120, 90]
        for c, h, w in zip(cols, heads, widths):
            self.tree.heading(c, text=h)
            self.tree.column(c, width=w, anchor="center")
        sb2 = ttk.Scrollbar(tbl, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=sb2.set)
        self.tree.pack(side="left", fill="both", expand=True)
        sb2.pack(side="right", fill="y")

    def _kpi(self, parent, col, title, value, color):
        card = tk.Frame(parent, bg=C_SURFACE, padx=12, pady=8,
                        highlightbackground=C_BORDER, highlightthickness=1)
        card.grid(row=0, column=col, sticky="nsew", padx=(0,6) if col<3 else 0)
        tk.Label(card, text=title, bg=C_SURFACE, fg=C_DIM,
                 font=(FONT, 8, "bold")).pack(anchor="w")
        lbl = tk.Label(card, text=value, bg=C_SURFACE, fg=color,
                       font=(FONT, 14, "bold"), pady=2)
        lbl.pack(anchor="w")
        return lbl

    # ── FOOTER ───────────────────────────────
    def build_footer(self):
        ft = tk.Frame(self, bg=C_SURFACE, padx=20, pady=6)
        ft.pack(fill="x", side="bottom")
        tk.Label(ft,
            text="ChargeGrid Intelligence · OCPP 2.0.1 · CO₂: 0,0817 kg/kWh (MCTIC 2023) · 100% Python Standard Library",
            bg=C_SURFACE, fg=C_DIM, font=(FONT, 8)).pack(side="left")

    # ─────────────────────────────────────────
    # AÇÕES
    # ─────────────────────────────────────────

    def toggle_station(self, sid):
        s = sessions[sid]
        st = next(x for x in STATIONS_DEF if x["id"] == sid)
        if s["active"]:
            # Encerrar
            save_session_csv(sid, st, s)
            persist_log(f"Sessão encerrada: {sid} | {s['user']} | {s['kwh']:.3f} kWh | R$ {s['kwh']*TARIFF_KWH:.2f}", "OK")
            sessions[sid].update({"active": False, "kw": 0.0, "kwh": 0.0,
                                  "minutes": 0, "user": "", "start": ""})
            self.add_log(f"[OK] Sessão {sid} encerrada e salva no CSV.")
        else:
            # Iniciar — diálogo simples
            dlg = tk.Toplevel(self)
            dlg.title(f"Iniciar sessão — {sid}")
            dlg.configure(bg=C_BG)
            dlg.geometry("320x200")
            dlg.resizable(False, False)
            dlg.grab_set()

            tk.Label(dlg, text=f"Estação: {sid} ({st['connector']} · max {st['max_kw']} kW)",
                     bg=C_BG, fg=C_TEXT, font=(FONT, 10, "bold")).pack(pady=(16, 4))

            row1 = tk.Frame(dlg, bg=C_BG)
            row1.pack(pady=4)
            tk.Label(row1, text="Usuário:", bg=C_BG, fg=C_DIM,
                     font=(FONT, 9), width=10, anchor="e").pack(side="left")
            user_var = tk.StringVar(value="USR-01")
            tk.Entry(row1, textvariable=user_var, bg=C_SURFACE, fg=C_TEXT,
                     insertbackground=C_TEXT, relief="flat", font=(FONT, 9),
                     width=14).pack(side="left", padx=6)

            row2 = tk.Frame(dlg, bg=C_BG)
            row2.pack(pady=4)
            tk.Label(row2, text="Potência (kW):", bg=C_BG, fg=C_DIM,
                     font=(FONT, 9), width=10, anchor="e").pack(side="left")
            kw_var = tk.StringVar(value=str(st["max_kw"]))
            tk.Entry(row2, textvariable=kw_var, bg=C_SURFACE, fg=C_TEXT,
                     insertbackground=C_TEXT, relief="flat", font=(FONT, 9),
                     width=14).pack(side="left", padx=6)

            def confirm():
                user = user_var.get().strip() or "USR-01"
                try:
                    kw = min(float(kw_var.get()), st["max_kw"])
                except ValueError:
                    kw = st["max_kw"]
                sessions[sid].update({
                    "active": True, "kw": kw, "kwh": 0.0,
                    "minutes": 0, "user": user,
                    "start": datetime.now().strftime("%H:%M:%S")
                })
                persist_log(f"Sessão iniciada: {sid} | {user} | {kw:.1f} kW", "OK")
                self.add_log(f"[OK] Sessão {sid} iniciada — {user} | {kw:.1f} kW | {st['auth']}")
                if is_overloaded() and dlm_active:
                    acts = run_dlm()
                    for a in acts:
                        self.add_log(f"[DLM] {a}")
                    persist_log(f"DLM executado após sobrecarga", "OK")
                elif is_overloaded():
                    self.add_log(f"[WARN] Sobrecarga! {total_demand():.1f} kW > {GRID_LIMIT_KW} kW. Ative o DLM.")
                dlg.destroy()
                self.refresh_all()

            tk.Button(dlg, text="Confirmar", bg=C_ACCENT, fg="#FFF",
                      relief="flat", font=(FONT, 10, "bold"),
                      cursor="hand2", command=confirm).pack(pady=12)

    def action_tick(self):
        simulate_tick(5)
        self.add_log("[INFO] +5 minutos simulados. kWh acumulados.")
        self.refresh_all()

    def action_toggle_dlm(self):
        global dlm_active
        dlm_active = not dlm_active
        status = "ATIVADO" if dlm_active else "DESATIVADO"
        self.add_log(f"[INFO] DLM {status} pelo operador.")
        persist_log(f"DLM {status}", "OK" if dlm_active else "WARN")
        if dlm_active and is_overloaded():
            acts = run_dlm()
            for a in acts:
                self.add_log(f"[DLM] {a}")
        self.refresh_all()

    def action_peak(self):
        peak_kw = [22, 22, 50, 50, 18, 22]
        users   = ["USR-10","USR-11","USR-12","USR-13","USR-14","USR-15"]
        for i, st in enumerate(STATIONS_DEF):
            sid = st["id"]
            sessions[sid].update({
                "active": True, "kw": peak_kw[i],
                "kwh": round(random.uniform(1, 5), 2),
                "minutes": random.randint(10, 40),
                "user": users[i],
                "start": datetime.now().strftime("%H:%M:%S")
            })
        self.add_log(f"[WARN] Cenário de pico ativado! Demanda: {total_demand():.0f} kW > {GRID_LIMIT_KW} kW")
        if dlm_active:
            acts = run_dlm()
            for a in acts:
                self.add_log(f"[DLM] {a}")
            self.add_log(f"[OK] DLM redistribuiu carga. Nova demanda: {total_demand():.1f} kW")
        persist_log(f"Cenário de pico simulado. Demanda: {total_demand():.1f} kW", "WARN")
        self.refresh_all()

    def action_clear_csv(self):
        if not messagebox.askyesno("Limpar CSV", "Apagar todos os dados de sessões?"):
            return
        with open(CSV_FILE, "w", newline="", encoding="utf-8") as f:
            csv.writer(f).writerow([
                "data_hora","estacao","usuario","conector","auth",
                "kwh","tempo_min","custo_brl","fonte_energia",
                "solar_pct","co2_evitado_kg","dlm_ativo","protocolo"
            ])
        self.add_log("[OK] CSV limpo — pronto para nova simulação.")
        self.refresh_data_tab()

    def on_solar_change(self, val):
        global solar_pct
        solar_pct = float(val)
        self.lbl_solar_slider.config(
            text=f"{solar_pct:.0f}%  ({SOLAR_CAP*solar_pct/100:.0f} kW)")
        self.refresh_control_tab()

    def run_ai_analysis(self):
        text = ai_analysis_text()
        self.txt_ai.config(state="normal")
        self.txt_ai.delete("1.0", "end")
        self.txt_ai.config(state="disabled")

        def type_text(remaining):
            if remaining:
                self.txt_ai.config(state="normal")
                self.txt_ai.insert("end", remaining[0])
                self.txt_ai.see("end")
                self.txt_ai.config(state="disabled")
                self.after(12, lambda: type_text(remaining[1:]))

        type_text(text)
        persist_log("Análise de IA executada", "INFO")

    def add_log(self, msg):
        ts = datetime.now().strftime("%H:%M:%S")
        self.txt_log.config(state="normal")
        self.txt_log.insert("end", f"[{ts}] {msg}\n")
        self.txt_log.see("end")
        self.txt_log.config(state="disabled")

    def clear_log_display(self):
        self.txt_log.config(state="normal")
        self.txt_log.delete("1.0", "end")
        self.txt_log.config(state="disabled")

    # ─────────────────────────────────────────
    # REFRESH
    # ─────────────────────────────────────────

    def refresh_all(self):
        self.refresh_control_tab()
        self.refresh_data_tab()

    def refresh_control_tab(self):
        demand = total_demand()
        active_count = sum(1 for s in sessions.values() if s["active"])
        revenue = sum(s["kwh"] * TARIFF_KWH for s in sessions.values())
        solar_u, bat_u, grid_u = energy_mix(demand)

        # Stat cards
        d_color = C_RED if is_overloaded() else (C_AMBER if demand > GRID_LIMIT_KW*0.85 else C_GREEN)
        self.lbl_demand_val.config(text=f"{demand:.1f} kW", fg=d_color)
        self.lbl_solar_val.config(text=f"{solar_pct:.0f}%")
        self.lbl_sessions_v.config(text=f"{active_count} / 6")
        self.lbl_revenue_v.config(text=f"R$ {revenue:.2f}")

        # Barra demanda
        self.canvas_bar.update_idletasks()
        w = self.canvas_bar.winfo_width() or 600
        self.canvas_bar.delete("all")
        pct = min(demand / GRID_LIMIT_KW, 1.0)
        color = C_RED if is_overloaded() else (C_AMBER if pct > 0.85 else C_GREEN)
        self.canvas_bar.create_rectangle(0, 0, w, 24, fill=C_SURFACE2, outline="")
        self.canvas_bar.create_rectangle(0, 0, int(w * pct), 24, fill=color, outline="")
        self.canvas_bar.create_line(int(w * 0.833), 0, int(w * 0.833), 24,
                                    fill=C_RED, width=2, dash=(4, 2))
        self.lbl_bar_info.config(
            text=f"{demand:.1f} kW / {GRID_LIMIT_KW:.0f} kW  ({pct*100:.0f}%)  {'⚠ SOBRECARGA' if is_overloaded() else '✓ Normal'}",
            fg=color)

        # Mix
        self.canvas_mix_ctrl.update_idletasks()
        w2 = self.canvas_mix_ctrl.winfo_width() or 600
        self.canvas_mix_ctrl.delete("all")
        if demand > 0:
            sx = int(w2 * solar_u / demand)
            bx = int(w2 * bat_u / demand)
            gx = w2 - sx - bx
            self.canvas_mix_ctrl.create_rectangle(0, 0, sx, 18, fill=C_GREEN, outline="")
            self.canvas_mix_ctrl.create_rectangle(sx, 0, sx+bx, 18, fill=C_AMBER, outline="")
            self.canvas_mix_ctrl.create_rectangle(sx+bx, 0, sx+bx+gx, 18, fill=C_BLUE, outline="")
            self.lbl_mix_info.config(
                text=f"☀ Solar {solar_u:.1f} kW ({solar_u/demand*100:.0f}%)   "
                     f"🔋 Bateria {bat_u:.1f} kW ({bat_u/demand*100:.0f}%)   "
                     f"⚡ Rede {grid_u:.1f} kW ({grid_u/demand*100:.0f}%)")
        else:
            self.canvas_mix_ctrl.create_rectangle(0, 0, w2, 18, fill=C_SURFACE2, outline="")
            self.lbl_mix_info.config(text="Sem consumo ativo")

        # Station cards
        for st in STATIONS_DEF:
            sid = st["id"]
            s = sessions[sid]
            card = self.station_cards[sid]
            if s["active"]:
                cap = s["kw"] / st["max_kw"]
                card["lbl_kw"].config(text=f"{s['kw']:.1f} kW", fg=C_ACCENT)
                card["lbl_kwh"].config(
                    text=f"{s['kwh']:.3f} kWh · R$ {s['kwh']*TARIFF_KWH:.2f}", fg=C_DIM)
                card["btn"].config(text="Encerrar", bg=C_RED)
                card["frame"].config(highlightbackground=C_ACCENT)
                card["canvas_bar"].delete("all")
                w3 = card["canvas_bar"].winfo_width() or 100
                card["canvas_bar"].create_rectangle(0, 0, w3, 6, fill=C_SURFACE2, outline="")
                card["canvas_bar"].create_rectangle(0, 0, int(w3*cap), 6, fill=C_ACCENT, outline="")
            else:
                card["lbl_kw"].config(text="— kW", fg=C_DIM)
                card["lbl_kwh"].config(text="livre", fg=C_DIM)
                card["btn"].config(text="Iniciar", bg=C_GREEN)
                card["frame"].config(highlightbackground=C_BORDER)
                card["canvas_bar"].delete("all")
                w3 = card["canvas_bar"].winfo_width() or 100
                card["canvas_bar"].create_rectangle(0, 0, w3, 6, fill=C_SURFACE2, outline="")

        # DLM label
        dlm_txt = "DLM ✓ ATIVO" if dlm_active else "DLM INATIVO"
        self.lbl_status.config(
            text=f"● {dlm_txt}",
            fg=C_ACCENT if dlm_active else C_DIM,
            bg="#3B1E28" if dlm_active else C_SURFACE2)

    def refresh_data_tab(self):
        rows = load_csv_rows()
        total_kwh  = sum(r["kwh"] for r in rows)
        total_cost = sum(r["cost"] for r in rows)
        total_co2  = sum(r["co2"] for r in rows)
        avg_solar  = (sum(r["solar_pct"] for r in rows) / len(rows)) if rows else 0
        solar_kwh  = total_kwh * (avg_solar / 100)
        km         = total_co2 / 0.089 if total_co2 > 0 else 0
        dlm_rate   = int(sum(1 for r in rows if r["dlm"].lower() in ("sim","true","1")) / len(rows) * 100) if rows else 0

        self.kpi_sessions.config(text=str(len(rows)))
        self.kpi_kwh.config(text=f"{total_kwh:.2f}")
        self.kpi_revenue.config(text=f"R$ {total_cost:.2f}")
        self.kpi_co2.config(text=f"{total_co2:.4f}")
        self.lbl_sust.config(
            text=f"🌱  ☀ Solar utilizado: {solar_kwh:.2f} kWh ({avg_solar:.0f}%)   "
                 f"🚗 Km limpos: {km:.1f} km   ⚖ DLM atuou em: {dlm_rate}% das sessões")
        self.lbl_tbl_count.config(text=f"{len(rows)} sessões")

        # Tabela
        for item in self.tree.get_children():
            self.tree.delete(item)
        for r in reversed(rows):
            self.tree.insert("", "end", values=(
                r["datetime"], r["station"], r["user"], r["connector"],
                f"{r['kwh']:.3f}", f"{r['minutes']} min",
                f"R$ {r['cost']:.2f}", r["source"], f"{r['co2']:.4f}"
            ))

        # Gráfico estações
        self.canvas_stations.update_idletasks()
        self.canvas_stations.delete("all")
        w = self.canvas_stations.winfo_width() or 400
        h = self.canvas_stations.winfo_height() or 130
        station_totals = {s["id"]: 0.0 for s in STATIONS_DEF}
        for r in rows:
            if r["station"] in station_totals:
                station_totals[r["station"]] += r["kwh"]
        max_v = max(station_totals.values()) or 1
        keys = sorted(station_totals.keys())
        spacing = (h - 10) / len(keys)
        for idx, sid in enumerate(keys):
            val = station_totals[sid]
            y = 6 + idx * spacing
            self.canvas_stations.create_text(
                4, y+7, text=sid, fill=C_DIM, font=(FONT, 8), anchor="w")
            bar_w = max(2, int((val/max_v) * (w-110))) if val > 0 else 2
            self.canvas_stations.create_rectangle(
                52, y, 52+bar_w, y+14,
                fill=C_ACCENT if val > 0 else C_SURFACE2, outline="")
            self.canvas_stations.create_text(
                56+bar_w, y+7, text=f"{val:.2f} kWh",
                fill=C_TEXT if val > 0 else C_DIM, font=(FONT, 8), anchor="w")

        # Gráfico mix
        self.canvas_energy.update_idletasks()
        self.canvas_energy.delete("all")
        w2 = self.canvas_energy.winfo_width() or 400
        mix = {"Solar": 0, "Bateria": 0, "Rede": 0, "Misto": 0}
        colors_mix = {"Solar": C_GREEN, "Bateria": C_AMBER, "Rede": C_BLUE, "Misto": "#7F56D9"}
        for r in rows:
            src = r["source"].lower()
            if "solar" in src and "misto" not in src:
                mix["Solar"] += 1
            elif "misto" in src:
                mix["Misto"] += 1
            elif "bateria" in src:
                mix["Bateria"] += 1
            else:
                mix["Rede"] += 1
        total_mix = sum(mix.values()) or 1
        cx = 20
        bar_w_total = w2 - 40
        for label, count in mix.items():
            seg = int((count/total_mix) * bar_w_total)
            if seg > 0:
                self.canvas_energy.create_rectangle(
                    cx, 20, cx+seg, 44, fill=colors_mix[label], outline="")
                if seg > 30:
                    self.canvas_energy.create_text(
                        cx+seg//2, 32, text=f"{int(count/total_mix*100)}%",
                        fill="#FFF", font=(FONT, 8, "bold"))
                cx += seg
        leg_x = 20
        for idx, (label, count) in enumerate(mix.items()):
            lx = 20 + idx * (w2-40)//4
            self.canvas_energy.create_oval(lx, 60, lx+10, 70, fill=colors_mix[label], outline="")
            self.canvas_energy.create_text(
                lx+14, 65, text=f"{label} ({int(count/total_mix*100)}%)",
                fill=C_TEXT, font=(FONT, 8), anchor="w")

    def auto_refresh(self):
        self.refresh_all()
        self.after(3000, self.auto_refresh)

if __name__ == "__main__":
    app = ChargeGridApp()
    app.mainloop()