import tkinter as tk
from tkinter import ttk
import cpu_scheduling
import memory_allocation
import page_replacement

# ── Color Palette ─────────────────────────────────────────────────────────────
BG_DARK    = "#0D1117"
BG_PANEL   = "#161B22"
BG_HEADER  = "#0A0E14"
ACCENT     = "#2EA8A8"
ACCENT2    = "#F0A500"
TEXT_PRI   = "#E6EDF3"
TEXT_SEC   = "#8B949E"
BORDER     = "#30363D"
DANGER     = "#DA3633"
SUCCESS    = "#3FB950"
BTN_HOVER  = "#1F6B6B"

# Distinct colours for Gantt bars (process slots 0-9, then repeats)
GANTT_COLORS = [
    "#2EA8A8", "#F0A500", "#3FB950", "#DA3633",
    "#6E40C9", "#F78166", "#79C0FF", "#FFB3BA",
    "#B5EAD7", "#C7CEEA",
]
IDLE_COLOR = "#30363D"


class OSSimulatorGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("OS Simulator — PMU Spring 2026")
        self.root.geometry("1020x800")
        self.root.configure(bg=BG_DARK)
        self.root.resizable(True, True)
        self._setup_styles()
        self.main_menu()

    # ── Style bootstrap ───────────────────────────────────────────────────────
    def _setup_styles(self):
        s = ttk.Style()
        s.theme_use("clam")
        s.configure("TFrame",          background=BG_DARK)
        s.configure("Panel.TFrame",    background=BG_PANEL)
        s.configure("Header.TFrame",   background=BG_HEADER)
        s.configure("TLabel",          background=BG_DARK,   foreground=TEXT_PRI, font=("Courier New", 11))
        s.configure("Header.TLabel",   background=BG_HEADER, foreground=ACCENT,   font=("Courier New", 22, "bold"))
        s.configure("Sub.TLabel",      background=BG_DARK,   foreground=TEXT_SEC, font=("Courier New", 10))
        s.configure("Panel.TLabel",    background=BG_PANEL,  foreground=TEXT_PRI, font=("Courier New", 11))
        s.configure("PanelSub.TLabel", background=BG_PANEL,  foreground=TEXT_SEC, font=("Courier New", 9))
        s.configure("Accent.TLabel",   background=BG_DARK,   foreground=ACCENT,   font=("Courier New", 11, "bold"))
        s.configure("TEntry",
                    fieldbackground=BG_PANEL, foreground=TEXT_PRI,
                    insertcolor=ACCENT, bordercolor=BORDER,
                    focuscolor=ACCENT,  font=("Courier New", 11))
        s.map("TEntry", bordercolor=[("focus", ACCENT)])

    # ── Widget helpers ────────────────────────────────────────────────────────
    def _btn(self, parent, text, cmd, color=ACCENT, width=24, danger=False):
        bg = DANGER if danger else color
        b = tk.Button(parent, text=text, command=cmd,
                      bg=bg, fg=BG_DARK if not danger else TEXT_PRI,
                      activebackground=BTN_HOVER, activeforeground=TEXT_PRI,
                      font=("Courier New", 11, "bold"),
                      relief="flat", bd=0, cursor="hand2",
                      width=width, padx=8, pady=6)
        if not danger:
            b.bind("<Enter>", lambda e: b.config(bg=BTN_HOVER, fg=TEXT_PRI))
            b.bind("<Leave>", lambda e: b.config(bg=bg,       fg=BG_DARK))
        return b

    def _label_entry(self, parent, label_text, default_val, width=58):
        row = ttk.Frame(parent, style="Panel.TFrame")
        row.pack(fill="x", padx=20, pady=3)
        ttk.Label(row, text=label_text, style="PanelSub.TLabel").pack(anchor="w")
        var = tk.StringVar(value=default_val)
        e = ttk.Entry(row, textvariable=var, width=width)
        e.pack(fill="x", ipady=4)
        return var

    def _output_box(self, parent, height=10):
        frame = ttk.Frame(parent, style="Panel.TFrame")
        frame.pack(fill="both", expand=True, padx=20, pady=(0, 12))
        t = tk.Text(frame, height=height, font=("Courier New", 10),
                    bg="#0A0E14", fg=TEXT_PRI, insertbackground=ACCENT,
                    relief="flat", bd=0, padx=10, pady=8,
                    selectbackground=ACCENT, selectforeground=BG_DARK)
        sb = ttk.Scrollbar(frame, command=t.yview)
        t.configure(yscrollcommand=sb.set)
        sb.pack(side="right", fill="y")
        t.pack(side="left", fill="both", expand=True)
        return t

    def _header_bar(self, title, subtitle=""):
        bar = ttk.Frame(self.root, style="Header.TFrame")
        bar.pack(fill="x")
        inner = ttk.Frame(bar, style="Header.TFrame")
        inner.pack(fill="x", padx=28, pady=14)
        ttk.Label(inner, text=title,    style="Header.TLabel").pack(anchor="w")
        if subtitle:
            ttk.Label(inner, text=subtitle, style="Sub.TLabel",
                      background=BG_HEADER, foreground=TEXT_SEC,
                      font=("Courier New", 9)).pack(anchor="w")
        tk.Frame(self.root, bg=ACCENT, height=2).pack(fill="x")

    def _section_label(self, parent, text):
        ttk.Label(parent, text=f"  {text}", style="Accent.TLabel").pack(
            anchor="w", padx=20, pady=(8, 2))

    def _back_btn(self):
        self._btn(self.root, "← Back to Menu", self.main_menu,
                  color=BG_PANEL, width=18).pack(anchor="nw", padx=20, pady=8)

    def clear_screen(self):
        for w in self.root.winfo_children():
            w.destroy()

    # ── Visual Gantt Chart ────────────────────────────────────────────────────
    def _draw_gantt(self, gantt_data):
        """Draw a coloured bar Gantt chart onto self._gantt_canvas."""
        canvas = self._gantt_canvas
        canvas.delete("all")
        if not gantt_data:
            canvas.create_text(60, 25, text="(no data)", fill=TEXT_SEC,
                               font=("Courier New", 9), anchor="w")
            return

        # Geometry
        canvas.update_idletasks()
        cw = canvas.winfo_width() or 940
        margin_l, margin_r = 46, 18
        bar_y, bar_h = 10, 34
        tick_h    = 8
        label_y   = bar_y + bar_h + tick_h + 8

        max_time  = max(s[2] for s in gantt_data)
        min_time  = min(s[1] for s in gantt_data)
        span      = max(max_time - min_time, 1)
        draw_w    = cw - margin_l - margin_r
        scale     = draw_w / span

        # Assign colours to unique process IDs (IDLE is grey)
        proc_ids  = list(dict.fromkeys(
            s[0] for s in gantt_data if s[0] != "IDLE"))
        color_map = {pid: GANTT_COLORS[i % len(GANTT_COLORS)]
                     for i, pid in enumerate(proc_ids)}
        color_map["IDLE"] = IDLE_COLOR

        # Draw bars
        for seg in gantt_data:
            pid, start, end = seg
            x1 = margin_l + (start - min_time) * scale
            x2 = margin_l + (end   - min_time) * scale
            col = color_map.get(pid, ACCENT)

            canvas.create_rectangle(
                x1, bar_y, x2, bar_y + bar_h,
                fill=col, outline=BG_DARK, width=1)

            bar_w = x2 - x1
            if bar_w > 14:
                txt_col = "#111" if pid != "IDLE" else TEXT_SEC
                canvas.create_text(
                    (x1 + x2) / 2, bar_y + bar_h / 2,
                    text=pid, font=("Courier New", 8, "bold"), fill=txt_col)

        # Tick marks and time labels at every boundary
        boundaries = sorted({t for seg in gantt_data for t in (seg[1], seg[2])})
        drawn_labels = set()
        for t in boundaries:
            x = margin_l + (t - min_time) * scale
            canvas.create_line(x, bar_y + bar_h, x, bar_y + bar_h + tick_h,
                               fill=TEXT_SEC, width=1)
            # Avoid overlapping labels when bars are tiny
            slot = round(x / 12)
            if slot not in drawn_labels:
                drawn_labels.add(slot)
                canvas.create_text(x, label_y, text=str(t),
                                   font=("Courier New", 7), fill=TEXT_SEC)

        # Axis label
        canvas.create_text(margin_l / 2, bar_y + bar_h / 2,
                           text="CPU", font=("Courier New", 8), fill=TEXT_SEC)

        # Legend
        legend_x = margin_l
        legend_y  = bar_y + bar_h + tick_h + 22
        for pid in proc_ids[:10]:
            col = color_map[pid]
            canvas.create_rectangle(legend_x, legend_y,
                                    legend_x + 10, legend_y + 10,
                                    fill=col, outline="")
            canvas.create_text(legend_x + 14, legend_y + 5,
                               text=pid, font=("Courier New", 7),
                               fill=TEXT_PRI, anchor="w")
            legend_x += 52

    # ── Main Menu ─────────────────────────────────────────────────────────────
    def main_menu(self):
        self.clear_screen()
        self._header_bar("OS SIMULATOR",
                         "Principles of Operating Systems  •  PMU Spring 2026")

        center = ttk.Frame(self.root)
        center.pack(expand=True)

        ttk.Label(center, text="SELECT A MODULE", style="Sub.TLabel",
                  font=("Courier New", 9, "bold"),
                  foreground=ACCENT2).pack(pady=(28, 14))

        modules = [
            ("⚙   CPU Scheduling Algorithms",   self.cpu_menu,    ACCENT),
            ("◫   Contiguous Memory Allocation", self.memory_menu, ACCENT),
            ("◈   Page Replacement Algorithms",  self.paging_menu, ACCENT),
        ]
        for label, cmd, color in modules:
            self._btn(center, label, cmd, color=color, width=42).pack(pady=8)

        ttk.Frame(center, height=8).pack()
        self._btn(center, "✕   Exit", self.root.quit,
                  danger=True, width=42).pack(pady=4)

        ttk.Label(center,
                  text="PMU — Spring 2026  |  OS Project",
                  style="Sub.TLabel",
                  font=("Courier New", 8)).pack(pady=(22, 0))

    # ── CPU Scheduling ────────────────────────────────────────────────────────
    def cpu_menu(self):
        self.clear_screen()
        self._header_bar(
            "CPU SCHEDULING",
            "FCFS  •  SJF Non-Preemptive  •  SJF Preemptive (SRTF)  •  Round Robin")
        self._back_btn()

        # Input panel
        panel = ttk.Frame(self.root, style="Panel.TFrame")
        panel.pack(fill="x", padx=20, pady=(0, 4))
        self._section_label(panel, "INPUT")
        data_var = self._label_entry(
            panel,
            "Processes — format: ArrivalTime,BurstTime  separated by semicolons"
            "  (e.g.  0,5 ; 1,3 ; 2,8 ; 3,2)",
            "0,5; 1,3; 2,8; 3,2", width=64)
        q_var = self._label_entry(
            panel,
            "Time Quantum — used by Round Robin only", "2", width=10)

        # Algorithm buttons
        self._section_label(self.root, "ALGORITHM")
        btn_row = ttk.Frame(self.root)
        btn_row.pack(padx=20, pady=(0, 4))

        # Gantt canvas (visual)
        gantt_frame = ttk.Frame(self.root, style="Panel.TFrame")
        gantt_frame.pack(fill="x", padx=20, pady=(0, 4))
        ttk.Label(gantt_frame, text="  GANTT CHART",
                  style="Accent.TLabel").pack(anchor="w", pady=(6, 2))
        self._gantt_canvas = tk.Canvas(
            gantt_frame, height=78, bg=BG_HEADER,
            highlightthickness=1, highlightbackground=BORDER)
        self._gantt_canvas.pack(fill="x", padx=10, pady=(0, 8))

        # Text output
        self._section_label(self.root, "RESULTS TABLE")
        out = self._output_box(self.root, height=10)

        def run(algo):
            result = cpu_scheduling.run_algorithm(
                algo, data_var.get(), q_var.get())
            if isinstance(result, tuple):
                text, gantt_data = result
            else:
                text, gantt_data = result, []

            out.config(state="normal")
            out.delete("1.0", tk.END)
            out.insert(tk.END, text)
            # Draw visual Gantt after window has rendered
            self.root.after(50, lambda: self._draw_gantt(gantt_data))

        labels = {
            "FCFS":   "FCFS",
            "SJF-NP": "SJF Non-Preemptive",
            "SJF-P":  "SJF Preemptive (SRTF)",
            "RR":     "Round Robin",
        }
        for algo in ["FCFS", "SJF-NP", "SJF-P", "RR"]:
            self._btn(btn_row, labels[algo],
                      lambda a=algo: run(a), width=22).pack(side="left", padx=4)

    # ── Memory Allocation ─────────────────────────────────────────────────────
    def memory_menu(self):
        self.clear_screen()
        self._header_bar("MEMORY ALLOCATION",
                         "First Fit  •  Best Fit  •  Worst Fit")
        self._back_btn()

        panel = ttk.Frame(self.root, style="Panel.TFrame")
        panel.pack(fill="x", padx=20, pady=(0, 4))
        self._section_label(panel, "INPUT")
        b_var = self._label_entry(
            panel,
            "Block Sizes (KB) — comma-separated  (e.g.  100, 500, 200, 300, 600)",
            "100, 500, 200, 300, 600")
        p_var = self._label_entry(
            panel,
            "Process Sizes (KB) — comma-separated  (e.g.  212, 417, 112)",
            "212, 417, 112")

        self._section_label(self.root, "ALGORITHM")
        btn_row = ttk.Frame(self.root)
        btn_row.pack(padx=20, pady=(0, 4))

        out = self._output_box(self.root, height=18)

        def run(algo):
            if algo == "All":
                res = memory_allocation.simulate_all(b_var.get(), p_var.get())
            else:
                res = memory_allocation.simulate(algo, b_var.get(), p_var.get())
            out.config(state="normal")
            out.delete("1.0", tk.END)
            out.insert(tk.END, res)

        for algo in ["First Fit", "Best Fit", "Worst Fit"]:
            self._btn(btn_row, algo,
                      lambda a=algo: run(a), width=18).pack(side="left", padx=3)

        self._btn(btn_row, "▶  Run All Three",
                  lambda: run("All"),
                  color=ACCENT2, width=18).pack(side="left", padx=3)

    # ── Page Replacement ──────────────────────────────────────────────────────
    def paging_menu(self):
        self.clear_screen()
        self._header_bar("PAGE REPLACEMENT",
                         "FIFO  •  LRU  •  Optimal")
        self._back_btn()

        panel = ttk.Frame(self.root, style="Panel.TFrame")
        panel.pack(fill="x", padx=20, pady=(0, 4))
        self._section_label(panel, "INPUT")
        ref_var = self._label_entry(
            panel,
            "Reference String — comma-separated page numbers"
            "  (e.g.  7,0,1,2,0,3,0,4,2,3,0,3,2)",
            "7,0,1,2,0,3,0,4,2,3,0,3,2")
        f_var = self._label_entry(
            panel,
            "Number of Frames", "3", width=10)

        self._section_label(self.root, "RUN")
        btn_row = ttk.Frame(self.root)
        btn_row.pack(padx=20, pady=(0, 4))

        out = self._output_box(self.root, height=12)

        def run():
            res = page_replacement.simulate_all(ref_var.get(), f_var.get())
            out.config(state="normal")
            out.delete("1.0", tk.END)
            out.insert(tk.END, res)

        self._btn(btn_row, "▶  Run All Algorithms (FIFO / LRU / Optimal)",
                  run, width=46).pack(side="left", padx=4)
