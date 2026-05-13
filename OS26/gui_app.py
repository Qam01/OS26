import tkinter as tk
from tkinter import ttk, font
import cpu_scheduling
import memory_allocation
import page_replacement

# ── Atlas Color Palette ──────────────────────────────────────────────────────
BG_DARK    = "#0D1117"   # deep space background
BG_PANEL   = "#161B22"   # card/panel surface
BG_HEADER  = "#0A0E14"   # header bar
ACCENT     = "#2EA8A8"   # atlas teal
ACCENT2    = "#F0A500"   # atlas gold
TEXT_PRI   = "#E6EDF3"   # primary text
TEXT_SEC   = "#8B949E"   # secondary / muted
BORDER     = "#30363D"   # subtle border
DANGER     = "#DA3633"   # exit / error red
SUCCESS    = "#3FB950"   # success green
BTN_HOVER  = "#1F6B6B"   # teal hover


class OSSimulatorGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("OS Simulator — PMU Spring 2026")
        self.root.geometry("980x760")
        self.root.configure(bg=BG_DARK)
        self.root.resizable(True, True)
        self._setup_styles()
        self.main_menu()

    # ── Style bootstrap ──────────────────────────────────────────────────────
    def _setup_styles(self):
        self.style = ttk.Style()
        self.style.theme_use("clam")
        self.style.configure("TFrame",           background=BG_DARK)
        self.style.configure("Panel.TFrame",     background=BG_PANEL)
        self.style.configure("Header.TFrame",    background=BG_HEADER)
        self.style.configure("TLabel",           background=BG_DARK,   foreground=TEXT_PRI,  font=("Courier New", 11))
        self.style.configure("Header.TLabel",    background=BG_HEADER, foreground=ACCENT,    font=("Courier New", 22, "bold"))
        self.style.configure("Sub.TLabel",       background=BG_DARK,   foreground=TEXT_SEC,  font=("Courier New", 10))
        self.style.configure("Panel.TLabel",     background=BG_PANEL,  foreground=TEXT_PRI,  font=("Courier New", 11))
        self.style.configure("PanelSub.TLabel",  background=BG_PANEL,  foreground=TEXT_SEC,  font=("Courier New", 9))
        self.style.configure("Accent.TLabel",    background=BG_DARK,   foreground=ACCENT,    font=("Courier New", 11, "bold"))
        self.style.configure("TEntry",
                             fieldbackground=BG_PANEL, foreground=TEXT_PRI,
                             insertcolor=ACCENT, bordercolor=BORDER,
                             focuscolor=ACCENT, font=("Courier New", 11))
        self.style.map("TEntry", bordercolor=[("focus", ACCENT)])

    # ── Reusable widget builders ──────────────────────────────────────────────
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
            b.bind("<Leave>", lambda e: b.config(bg=bg, fg=BG_DARK))
        return b

    def _label_entry(self, parent, label_text, default_val, width=55):
        row = ttk.Frame(parent, style="Panel.TFrame")
        row.pack(fill="x", padx=20, pady=4)
        ttk.Label(row, text=label_text, style="PanelSub.TLabel").pack(anchor="w")
        var = tk.StringVar(value=default_val)
        e = ttk.Entry(row, textvariable=var, width=width)
        e.pack(fill="x", ipady=4)
        return var

    def _output_box(self, parent, height=14):
        frame = ttk.Frame(parent, style="Panel.TFrame")
        frame.pack(fill="both", expand=True, padx=20, pady=(0, 14))
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
        ttk.Label(inner, text=title, style="Header.TLabel").pack(anchor="w")
        if subtitle:
            ttk.Label(inner, text=subtitle, style="Sub.TLabel",
                      background=BG_HEADER, foreground=TEXT_SEC,
                      font=("Courier New", 9)).pack(anchor="w")
        # Accent line
        sep = tk.Frame(self.root, bg=ACCENT, height=2)
        sep.pack(fill="x")

    def _section_label(self, parent, text):
        ttk.Label(parent, text=f"  {text}", style="Accent.TLabel").pack(anchor="w", padx=20, pady=(10, 2))

    def _back_btn(self):
        self._btn(self.root, "← Back to Menu", self.main_menu, color=BG_PANEL, width=18).pack(anchor="nw", padx=20, pady=10)

    def clear_screen(self):
        for w in self.root.winfo_children():
            w.destroy()

    # ── Main Menu ─────────────────────────────────────────────────────────────
    def main_menu(self):
        self.clear_screen()
        self._header_bar("OS SIMULATOR", "Principles of Operating Systems  •  PMU Spring 2026")

        center = ttk.Frame(self.root)
        center.pack(expand=True)

        ttk.Label(center, text="SELECT A MODULE", style="Sub.TLabel",
                  font=("Courier New", 9, "bold"), foreground=ACCENT2).pack(pady=(30, 16))

        modules = [
            ("⚙   CPU Scheduling Algorithms",   self.cpu_menu,    ACCENT),
            ("◫   Contiguous Memory Allocation", self.memory_menu, ACCENT),
            ("◈   Page Replacement Algorithms",  self.paging_menu, ACCENT),
        ]
        for label, cmd, color in modules:
            self._btn(center, label, cmd, color=color, width=40).pack(pady=8)

        ttk.Frame(center, height=10).pack()
        self._btn(center, "✕   Exit", self.root.quit, danger=True, width=40).pack(pady=4)

        ttk.Label(center, text="PMU — Spring 2026  |  OS Project Group 26",
                  style="Sub.TLabel", font=("Courier New", 8)).pack(pady=(24, 0))

    # ── CPU Scheduling ────────────────────────────────────────────────────────
    def cpu_menu(self):
        self.clear_screen()
        self._header_bar("CPU SCHEDULING", "FCFS  •  SJF Non-Preemptive  •  SJF Preemptive (SRTF)  •  Round Robin")
        self._back_btn()

        panel = ttk.Frame(self.root, style="Panel.TFrame",
                          relief="flat")
        panel.pack(fill="x", padx=20, pady=(0, 6))

        self._section_label(panel, "INPUT")
        data_var = self._label_entry(panel,
            "Processes — Arrival,Burst separated by semicolons  (e.g. 0,5; 1,3; 2,8)",
            "0,5; 1,3; 2,8; 3,2", width=60)
        q_var = self._label_entry(panel,
            "Time Quantum — used by Round Robin", "2", width=10)

        self._section_label(self.root, "ALGORITHM")
        btn_row = ttk.Frame(self.root)
        btn_row.pack(padx=20, pady=(0, 6))

        out = self._output_box(self.root, height=14)

        def run(algo):
            res = cpu_scheduling.run_algorithm(algo, data_var.get(), q_var.get())
            out.config(state="normal")
            out.delete("1.0", tk.END)
            out.insert(tk.END, res)

        for algo in ["FCFS", "SJF-NP", "SJF-P", "RR"]:
            lbl = {"FCFS": "FCFS", "SJF-NP": "SJF Non-Preemptive",
                   "SJF-P": "SJF Preemptive (SRTF)", "RR": "Round Robin"}[algo]
            self._btn(btn_row, lbl, lambda a=algo: run(a), width=22).pack(side="left", padx=4)

    # ── Memory Allocation ────────────────────────────────────────────────────
    def memory_menu(self):
        self.clear_screen()
        self._header_bar("MEMORY ALLOCATION", "First Fit  •  Best Fit  •  Worst Fit")
        self._back_btn()

        panel = ttk.Frame(self.root, style="Panel.TFrame")
        panel.pack(fill="x", padx=20, pady=(0, 6))

        self._section_label(panel, "INPUT")
        b_var = self._label_entry(panel,
            "Block Sizes — comma-separated (e.g. 100, 500, 200, 300, 600)",
            "100, 500, 200, 300, 600")
        p_var = self._label_entry(panel,
            "Process Sizes — comma-separated (e.g. 212, 417, 112)",
            "212, 417, 112")

        self._section_label(self.root, "ALGORITHM")
        btn_row = ttk.Frame(self.root)
        btn_row.pack(padx=20, pady=(0, 6))

        out = self._output_box(self.root, height=14)

        def run(algo):
            res = memory_allocation.simulate(algo, b_var.get(), p_var.get())
            out.config(state="normal")
            out.delete("1.0", tk.END)
            out.insert(tk.END, res)

        for algo in ["First Fit", "Best Fit", "Worst Fit"]:
            self._btn(btn_row, algo, lambda a=algo: run(a), width=18).pack(side="left", padx=4)

    # ── Page Replacement ─────────────────────────────────────────────────────
    def paging_menu(self):
        self.clear_screen()
        self._header_bar("PAGE REPLACEMENT", "FIFO  •  LRU  •  Optimal")
        self._back_btn()

        panel = ttk.Frame(self.root, style="Panel.TFrame")
        panel.pack(fill="x", padx=20, pady=(0, 6))

        self._section_label(panel, "INPUT")
        ref_var = self._label_entry(panel,
            "Reference String — comma-separated page numbers",
            "7,0,1,2,0,3,0,4,2,3,0,3,2")
        f_var = self._label_entry(panel,
            "Number of Frames", "3", width=10)

        self._section_label(self.root, "RUN")
        btn_row = ttk.Frame(self.root)
        btn_row.pack(padx=20, pady=(0, 6))

        out = self._output_box(self.root, height=12)

        def run():
            res = page_replacement.simulate_all(ref_var.get(), f_var.get())
            out.config(state="normal")
            out.delete("1.0", tk.END)
            out.insert(tk.END, res)

        self._btn(btn_row, "▶  Run All Algorithms", run, width=28).pack(side="left", padx=4)
