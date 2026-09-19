"""
ChargeGrid Intelligence — Dashboard Desktop em Python (Tkinter)
GoodWe Challenge · FIAP Sprint 3 · 100% Python Standard Library
"""

import os
import csv
import tkinter as tk
from tkinter import ttk, messagebox

# ─────────────────────────────────────────────
# CONFIGURAÇÕES E TEMA VISUAL (DARK MODE)
# ─────────────────────────────────────────────

CSV_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "sessions.csv")

FONT_FAMILY = "Segoe UI"
COLOR_BG       = "#1C1C1C"
COLOR_SURFACE  = "#2A2A2A"
COLOR_SURFACE2 = "#333333"
COLOR_BORDER   = "#3D3D3D"
COLOR_TEXT     = "#F0F0F0"
COLOR_TEXT_DIM = "#9A9A9A"
COLOR_ACCENT   = "#E91C5D"
COLOR_ACCENT_H = "#FF2E70"
COLOR_GREEN    = "#1D9E75"
COLOR_AMBER    = "#BA7517"
COLOR_BLUE     = "#378ADD"
COLOR_PURPLE   = "#7F56D9"

class ChargeGridDashboard(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("ChargeGrid Intelligence — Dashboard de Monitoramento")
        self.geometry("1060x760")
        self.minsize(920, 640)
        self.configure(bg=COLOR_BG)

        self.current_rows = []
        self.setup_styles()
        self.build_ui()
        self.update_idletasks()
        self.load_data()
        self.after(100, self.load_data)

    def setup_styles(self):
        style = ttk.Style(self)
        style.theme_use("clam")

        # Treeview styling (Tabela de Sessões)
        style.configure(
            "Treeview",
            background=COLOR_SURFACE,
            foreground=COLOR_TEXT,
            fieldbackground=COLOR_SURFACE,
            rowheight=26,
            font=(FONT_FAMILY, 9),
            borderwidth=0,
        )
        style.configure(
            "Treeview.Heading",
            background=COLOR_SURFACE2,
            foreground=COLOR_TEXT_DIM,
            font=(FONT_FAMILY, 9, "bold"),
            borderwidth=0,
            relief="flat",
        )
        style.map(
            "Treeview",
            background=[("selected", COLOR_ACCENT)],
            foreground=[("selected", "#FFFFFF")],
        )
        style.map(
            "Treeview.Heading",
            background=[("active", COLOR_BORDER)],
        )

        # Scrollbar styling
        style.configure(
            "Vertical.TScrollbar",
            background=COLOR_SURFACE2,
            troughcolor=COLOR_BG,
            arrowcolor=COLOR_TEXT_DIM,
            borderwidth=0,
            relief="flat",
        )

    def build_ui(self):
        # 1. HEADER
        header_frame = tk.Frame(self, bg=COLOR_SURFACE, height=64, padx=20, pady=12)
        header_frame.pack(fill="x", side="top")
        header_frame.pack_propagate(False)

        # Logo e Título
        title_box = tk.Frame(header_frame, bg=COLOR_SURFACE)
        title_box.pack(side="left", fill="y")

        logo_lbl = tk.Label(
            title_box, text="⚡", bg=COLOR_ACCENT, fg="#FFFFFF",
            font=(FONT_FAMILY, 14, "bold"), width=3, height=1
        )
        logo_lbl.pack(side="left", padx=(0, 12))

        text_box = tk.Frame(title_box, bg=COLOR_SURFACE)
        text_box.pack(side="left")

        lbl_title = tk.Label(
            text_box, text="ChargeGrid Intelligence",
            bg=COLOR_SURFACE, fg=COLOR_TEXT, font=(FONT_FAMILY, 13, "bold")
        )
        lbl_title.pack(anchor="w")

        lbl_sub = tk.Label(
            text_box, text="Painel de Telemetria e Monitoramento · GoodWe Challenge · Sprint 3",
            bg=COLOR_SURFACE, fg=COLOR_TEXT_DIM, font=(FONT_FAMILY, 9)
        )
        lbl_sub.pack(anchor="w")

        # Status e Botão Atualizar
        actions_box = tk.Frame(header_frame, bg=COLOR_SURFACE)
        actions_box.pack(side="right", fill="y")

        status_lbl = tk.Label(
            actions_box, text="● SEMS+ Conectado", bg="#3B1E28", fg=COLOR_ACCENT,
            font=(FONT_FAMILY, 9, "bold"), padx=12, pady=4
        )
        status_lbl.pack(side="left", padx=(0, 10))

        btn_refresh = tk.Button(
            actions_box, text="🔄 Atualizar Dados", bg=COLOR_ACCENT, fg="#FFFFFF",
            activebackground=COLOR_ACCENT_H, activeforeground="#FFFFFF",
            relief="flat", font=(FONT_FAMILY, 9, "bold"), padx=14, pady=4,
            cursor="hand2", command=self.load_data
        )
        btn_refresh.pack(side="left")

        # Container Principal com scroll/padding
        self.main_container = tk.Frame(self, bg=COLOR_BG, padx=20, pady=14)
        self.main_container.pack(fill="both", expand=True)

        # 2. CARDS DE KPIS
        self.kpi_frame = tk.Frame(self.main_container, bg=COLOR_BG)
        self.kpi_frame.pack(fill="x", pady=(0, 12))
        for i in range(4):
            self.kpi_frame.columnconfigure(i, weight=1, uniform="kpi")

        self.kpi_sessions = self.create_kpi_card(self.kpi_frame, 0, "TOTAL DE SESSÕES", "0", "registradas no CSV", COLOR_ACCENT)
        self.kpi_kwh      = self.create_kpi_card(self.kpi_frame, 1, "ENERGIA CONSUMIDA", "0.00 kWh", "acumulados nas estações", COLOR_BLUE)
        self.kpi_revenue  = self.create_kpi_card(self.kpi_frame, 2, "RECEITA TARIFADA", "R$ 0.00", "a R$ 1,35/kWh", COLOR_AMBER)
        self.kpi_co2      = self.create_kpi_card(self.kpi_frame, 3, "CO₂ EVITADO", "0.0000 kg", "fator MCTIC 2023", COLOR_GREEN)

        # 3. BARRA DE SUSTENTABILIDADE
        self.sustain_frame = tk.Frame(self.main_container, bg=COLOR_SURFACE, padx=16, pady=10, highlightbackground=COLOR_BORDER, highlightthickness=1)
        self.sustain_frame.pack(fill="x", pady=(0, 12))

        self.lbl_sustain = tk.Label(
            self.sustain_frame,
            text="🌱 Sustentabilidade:  ☀️ Solar: 0.0 kWh  |  🚗 Km elétricos limpos: 0.0 km  |  ⚖ Atuação do DLM: 0%",
            bg=COLOR_SURFACE, fg=COLOR_TEXT, font=(FONT_FAMILY, 10)
        )
        self.lbl_sustain.pack(side="left")

        # 4. PAINEL DE GRÁFICOS (2 Colunas)
        charts_frame = tk.Frame(self.main_container, bg=COLOR_BG)
        charts_frame.pack(fill="x", pady=(0, 12))
        charts_frame.columnconfigure(0, weight=1, uniform="charts")
        charts_frame.columnconfigure(1, weight=1, uniform="charts")

        # Gráfico 1: Consumo por Estação
        c1_box = tk.Frame(charts_frame, bg=COLOR_SURFACE, padx=14, pady=10, highlightbackground=COLOR_BORDER, highlightthickness=1)
        c1_box.grid(row=0, column=0, sticky="nsew", padx=(0, 6))

        tk.Label(c1_box, text="⚡ CONSUMO POR ESTAÇÃO (kWh)", bg=COLOR_SURFACE, fg=COLOR_TEXT_DIM, font=(FONT_FAMILY, 9, "bold")).pack(anchor="w")
        self.canvas_stations = tk.Canvas(c1_box, bg=COLOR_SURFACE, height=140, highlightthickness=0)
        self.canvas_stations.pack(fill="both", expand=True, pady=(6, 0))
        self.canvas_stations.bind("<Configure>", lambda e: self.draw_station_chart())

        # Gráfico 2: Mix de Energia
        c2_box = tk.Frame(charts_frame, bg=COLOR_SURFACE, padx=14, pady=10, highlightbackground=COLOR_BORDER, highlightthickness=1)
        c2_box.grid(row=0, column=1, sticky="nsew", padx=(6, 0))

        tk.Label(c2_box, text="☀️ DISTRIBUIÇÃO DO MIX ENERGÉTICO", bg=COLOR_SURFACE, fg=COLOR_TEXT_DIM, font=(FONT_FAMILY, 9, "bold")).pack(anchor="w")
        self.canvas_mix = tk.Canvas(c2_box, bg=COLOR_SURFACE, height=140, highlightthickness=0)
        self.canvas_mix.pack(fill="both", expand=True, pady=(6, 0))
        self.canvas_mix.bind("<Configure>", lambda e: self.draw_mix_chart())

        # 5. TABELA DE SESSÕES
        table_card = tk.Frame(self.main_container, bg=COLOR_SURFACE, padx=14, pady=10, highlightbackground=COLOR_BORDER, highlightthickness=1)
        table_card.pack(fill="both", expand=True)

        table_header = tk.Frame(table_card, bg=COLOR_SURFACE)
        table_header.pack(fill="x", pady=(0, 6))

        tk.Label(
            table_header, text="📋 HISTÓRICO COMPLETO DE SESSÕES (sessions.csv)",
            bg=COLOR_SURFACE, fg=COLOR_TEXT_DIM, font=(FONT_FAMILY, 9, "bold")
        ).pack(side="left")

        self.lbl_table_count = tk.Label(
            table_header, text="0 registros", bg=COLOR_SURFACE, fg=COLOR_TEXT_DIM, font=(FONT_FAMILY, 9)
        )
        self.lbl_table_count.pack(side="right")

        # Tabela com Scrollbar
        table_inner = tk.Frame(table_card, bg=COLOR_SURFACE)
        table_inner.pack(fill="both", expand=True)

        columns = ("datetime", "station", "user", "connector", "kwh", "minutes", "cost", "source", "co2")
        self.tree = ttk.Treeview(table_inner, columns=columns, show="headings", selectmode="browse")

        self.tree.heading("datetime", text="Data / Hora")
        self.tree.heading("station", text="Estação")
        self.tree.heading("user", text="Usuário")
        self.tree.heading("connector", text="Conector")
        self.tree.heading("kwh", text="Energia (kWh)")
        self.tree.heading("minutes", text="Tempo")
        self.tree.heading("cost", text="Custo (R$)")
        self.tree.heading("source", text="Fonte")
        self.tree.heading("co2", text="CO₂ Evitado")

        self.tree.column("datetime",  width=140, anchor="center")
        self.tree.column("station",   width=75,  anchor="center")
        self.tree.column("user",      width=85,  anchor="center")
        self.tree.column("connector", width=85,  anchor="center")
        self.tree.column("kwh",       width=95,  anchor="e")
        self.tree.column("minutes",   width=70,  anchor="center")
        self.tree.column("cost",      width=85,  anchor="e")
        self.tree.column("source",    width=115, anchor="center")
        self.tree.column("co2",       width=95,  anchor="e")

        scrollbar = ttk.Scrollbar(table_inner, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)

        self.tree.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        # 6. RODAPÉ
        footer = tk.Frame(self, bg=COLOR_SURFACE, padx=20, pady=6)
        footer.pack(fill="x", side="bottom")
        tk.Label(
            footer,
            text="ChargeGrid Intelligence · Protocolo OCPP 2.0.1 · Fator CO₂: 0,0817 kg/kWh (MCTIC 2023) · 100% Python Standard Library",
            bg=COLOR_SURFACE, fg=COLOR_TEXT_DIM, font=(FONT_FAMILY, 8)
        ).pack(side="left")

    def create_kpi_card(self, parent, col, title, value, subtitle, accent_color):
        card = tk.Frame(parent, bg=COLOR_SURFACE, padx=14, pady=12, highlightbackground=COLOR_BORDER, highlightthickness=1)
        card.grid(row=0, column=col, sticky="nsew", padx=4 if col in (1, 2) else (0, 4) if col == 0 else (4, 0))

        tk.Label(card, text=title, bg=COLOR_SURFACE, fg=COLOR_TEXT_DIM, font=(FONT_FAMILY, 8, "bold")).pack(anchor="w")
        val_lbl = tk.Label(card, text=value, bg=COLOR_SURFACE, fg=accent_color, font=(FONT_FAMILY, 16, "bold"), pady=4)
        val_lbl.pack(anchor="w")
        tk.Label(card, text=subtitle, bg=COLOR_SURFACE, fg=COLOR_TEXT_DIM, font=(FONT_FAMILY, 8)).pack(anchor="w")
        return val_lbl

    def load_data(self):
        rows = []
        if os.path.exists(CSV_FILE):
            try:
                with open(CSV_FILE, "r", encoding="utf-8") as f:
                    reader = csv.reader(f)
                    header = next(reader, None)
                    for r in reader:
                        if len(r) >= 11 and r[1].strip():
                            rows.append({
                                "datetime": r[0].strip(),
                                "station":  r[1].strip(),
                                "user":     r[2].strip(),
                                "connector":r[3].strip(),
                                "auth":     r[4].strip() if len(r) > 4 else "",
                                "kwh":      float(r[5]) if r[5] else 0.0,
                                "minutes":  int(r[6]) if r[6] else 0,
                                "cost":     float(r[7]) if r[7] else 0.0,
                                "source":   r[8].strip() if len(r) > 8 else "—",
                                "solar_pct":float(r[9]) if len(r) > 9 and r[9] else 0.0,
                                "co2":      float(r[10]) if len(r) > 10 and r[10] else 0.0,
                                "dlm":      r[11].strip() if len(r) > 11 else "Não",
                            })
            except Exception as e:
                messagebox.showerror("Erro ao carregar CSV", f"Não foi possível ler {CSV_FILE}:\n{e}")

        self.current_rows = rows

        # Atualiza métricas
        total_kwh     = sum(r["kwh"] for r in rows)
        total_cost    = sum(r["cost"] for r in rows)
        total_co2     = sum(r["co2"] for r in rows)
        avg_solar     = (sum(r["solar_pct"] for r in rows) / len(rows)) if rows else 0.0
        solar_kwh     = total_kwh * (avg_solar / 100.0)
        km_clean      = (total_co2 / 0.089) if total_co2 > 0 else 0.0
        dlm_count     = sum(1 for r in rows if r["dlm"].lower() in ("sim", "true", "1"))
        dlm_rate      = int((dlm_count / len(rows) * 100)) if rows else 0

        self.kpi_sessions.config(text=f"{len(rows)}")
        self.kpi_kwh.config(text=f"{total_kwh:.2f} kWh")
        self.kpi_revenue.config(text=f"R$ {total_cost:.2f}")
        self.kpi_co2.config(text=f"{total_co2:.4f} kg")

        self.lbl_sustain.config(
            text=f"🌱 Sustentabilidade:  ☀️ Solar: {solar_kwh:.2f} kWh ({avg_solar:.0f}%)  |  🚗 Km limpos: {km_clean:.1f} km  |  ⚖ Atuação do DLM: {dlm_rate}%"
        )
        self.lbl_table_count.config(text=f"{len(rows)} sessões registradas")

        # Atualiza Tabela
        for item in self.tree.get_children():
            self.tree.delete(item)

        for r in reversed(rows):
            self.tree.insert("", "end", values=(
                r["datetime"],
                r["station"],
                r["user"],
                r["connector"],
                f"{r['kwh']:.3f}",
                f"{r['minutes']} min",
                f"R$ {r['cost']:.2f}",
                r["source"],
                f"{r['co2']:.4f} kg"
            ))

        # Renderiza Gráficos
        self.draw_station_chart(rows)
        self.draw_mix_chart(rows)

    def draw_station_chart(self, rows=None):
        if rows is None:
            rows = self.current_rows
        self.canvas_stations.delete("all")
        w = self.canvas_stations.winfo_width()
        if w <= 100:
            w = 480
        h = self.canvas_stations.winfo_height()
        if h <= 50:
            h = 140

        station_totals = {f"EV-0{i}": 0.0 for i in range(1, 7)}
        for r in rows:
            st = r["station"]
            if st in station_totals:
                station_totals[st] += r["kwh"]
            else:
                station_totals[st] = station_totals.get(st, 0.0) + r["kwh"]

        max_kwh = max(station_totals.values()) if any(station_totals.values()) else 1.0
        st_keys = sorted(station_totals.keys())

        bar_height = 14
        spacing = (h - 20) / len(st_keys) if st_keys else 20
        start_x = 55
        max_bar_w = w - 140

        for idx, sid in enumerate(st_keys):
            val = station_totals[sid]
            y = 12 + idx * spacing
            self.canvas_stations.create_text(
                20, y + bar_height / 2, text=sid, fill=COLOR_TEXT_DIM,
                font=(FONT_FAMILY, 8, "bold"), anchor="w"
            )
            bar_w = max(4, int((val / max_kwh) * max_bar_w)) if val > 0 else 4
            color = COLOR_ACCENT if val > 0 else COLOR_SURFACE2
            self.canvas_stations.create_rectangle(
                start_x, y, start_x + bar_w, y + bar_height,
                fill=color, outline=""
            )
            label_text = f"{val:.2f} kWh" if val > 0 else "0 kWh"
            self.canvas_stations.create_text(
                start_x + bar_w + 8, y + bar_height / 2, text=label_text,
                fill=COLOR_TEXT if val > 0 else COLOR_TEXT_DIM,
                font=(FONT_FAMILY, 8), anchor="w"
            )

    def draw_mix_chart(self, rows=None):
        if rows is None:
            rows = self.current_rows
        self.canvas_mix.delete("all")
        w = self.canvas_mix.winfo_width()
        if w <= 100:
            w = 480
        h = self.canvas_mix.winfo_height()
        if h <= 50:
            h = 140

        mix_counts = {"Solar": 0, "Bateria": 0, "Rede": 0, "Misto": 0}
        for r in rows:
            src = r["source"]
            if "solar" in src.lower() and "misto" not in src.lower():
                mix_counts["Solar"] += 1
            elif "misto" in src.lower():
                mix_counts["Misto"] += 1
            elif "bateria" in src.lower():
                mix_counts["Bateria"] += 1
            else:
                mix_counts["Rede"] += 1

        total = sum(mix_counts.values()) or 1
        colors = {
            "Solar": COLOR_GREEN,
            "Bateria": COLOR_AMBER,
            "Misto": COLOR_PURPLE,
            "Rede": COLOR_BLUE,
        }

        # Barra de distribuição segmentada
        bar_x = 20
        bar_y = 30
        bar_w = w - 40
        bar_h = 24

        curr_x = bar_x
        for label, count in mix_counts.items():
            pct = (count / total)
            seg_w = int(pct * bar_w)
            if seg_w > 0:
                self.canvas_mix.create_rectangle(
                    curr_x, bar_y, curr_x + seg_w, bar_y + bar_h,
                    fill=colors[label], outline=""
                )
                if seg_w > 35:
                    self.canvas_mix.create_text(
                        curr_x + seg_w / 2, bar_y + bar_h / 2,
                        text=f"{int(pct * 100)}%", fill="#FFFFFF",
                        font=(FONT_FAMILY, 8, "bold"), anchor="center"
                    )
                curr_x += seg_w

        if total == 1 and not rows:
            self.canvas_mix.create_rectangle(
                bar_x, bar_y, bar_x + bar_w, bar_y + bar_h,
                fill=COLOR_SURFACE2, outline=""
            )
            self.canvas_mix.create_text(
                bar_x + bar_w / 2, bar_y + bar_h / 2,
                text="Sem dados ainda", fill=COLOR_TEXT_DIM,
                font=(FONT_FAMILY, 8), anchor="center"
            )

        # Legenda inferior com contagem
        legend_y = 80
        col_w = (w - 40) / 4
        for idx, (label, count) in enumerate(mix_counts.items()):
            lx = 20 + idx * col_w
            self.canvas_mix.create_oval(lx, legend_y + 3, lx + 10, legend_y + 13, fill=colors[label], outline="")
            pct_val = int((count / total) * 100) if rows else 0
            self.canvas_mix.create_text(
                lx + 16, legend_y + 8,
                text=f"{label} ({pct_val}%)\n{count} sessões", fill=COLOR_TEXT,
                font=(FONT_FAMILY, 8), anchor="w"
            )

if __name__ == "__main__":
    app = ChargeGridDashboard()
    app.mainloop()
