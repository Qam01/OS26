import tkinter as tk
from tkinter import ttk, messagebox
import cpu_scheduling
import memory_allocation
import page_replacement

class OSSimulatorGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("OS Simulator - PMU Spring 2026")
        self.root.geometry("900x750")
        self.main_menu()

    def clear_screen(self):
        for widget in self.root.winfo_children():
            widget.destroy()

    def main_menu(self):
        self.clear_screen()
        tk.Label(self.root, text="Principles of Operating System Simulator", font=("Arial", 18, "bold")).pack(pady=20)
        
        btn_frame = tk.Frame(self.root)
        btn_frame.pack(expand=True)

        tk.Button(btn_frame, text="CPU Scheduling Algorithms", width=30, height=2, command=self.cpu_menu).pack(pady=10)
        tk.Button(btn_frame, text="Contiguous Memory Allocation", width=30, height=2, command=self.memory_menu).pack(pady=10)
        tk.Button(btn_frame, text="Page Replacement Algorithms", width=30, height=2, command=self.paging_menu).pack(pady=10)
        tk.Button(btn_frame, text="Exit", width=30, height=2, command=self.root.quit, bg="#ffcccb").pack(pady=10)

    def cpu_menu(self):
        self.clear_screen()
        tk.Button(self.root, text="← Back", command=self.main_menu).pack(anchor="nw", padx=10, pady=10)
        
        tk.Label(self.root, text="Input: Arrival,Burst (e.g. 0,5; 1,3)").pack()
        entry = tk.Entry(self.root, width=50)
        entry.insert(0, "0,5; 1,3; 2,8")
        entry.pack(pady=5)

        tk.Label(self.root, text="Quantum (for RR)").pack()
        q_entry = tk.Entry(self.root, width=10)
        q_entry.insert(0, "2")
        q_entry.pack(pady=5)

        output = tk.Text(self.root, height=15, width=90)
        
        def run(algo):
            data = entry.get()
            q = q_entry.get()
            res = cpu_scheduling.run_algorithm(algo, data, q)
            output.delete("1.0", tk.END)
            output.insert(tk.END, res)

        btn_container = tk.Frame(self.root)
        btn_container.pack()
        for a in ["FCFS", "SJF-NP", "SJF-P", "RR"]:
            tk.Button(btn_container, text=a, command=lambda algo=a: run(algo)).pack(side=tk.LEFT, padx=5)
        
        output.pack(pady=10)

    def memory_menu(self):
        self.clear_screen()
        tk.Button(self.root, text="← Back", command=self.main_menu).pack(anchor="nw", padx=10, pady=10)
        
        tk.Label(self.root, text="Block Sizes (e.g. 100, 500, 200)").pack()
        b_entry = tk.Entry(self.root, width=50)
        b_entry.insert(0, "100, 500, 200, 300, 600")
        b_entry.pack()

        tk.Label(self.root, text="Process Sizes (e.g. 212, 417)").pack()
        p_entry = tk.Entry(self.root, width=50)
        p_entry.insert(0, "212, 417, 112")
        p_entry.pack()

        output = tk.Text(self.root, height=15, width=80)

        def run(algo):
            res = memory_allocation.simulate(algo, b_entry.get(), p_entry.get())
            output.delete("1.0", tk.END)
            output.insert(tk.END, res)

        btn_container = tk.Frame(self.root)
        btn_container.pack(pady=5)
        for a in ["First Fit", "Best Fit", "Worst Fit"]:
            tk.Button(btn_container, text=a, command=lambda algo=a: run(algo)).pack(side=tk.LEFT, padx=5)

        output.pack(pady=10)

    def paging_menu(self):
        self.clear_screen()
        tk.Button(self.root, text="← Back", command=self.main_menu).pack(anchor="nw", padx=10, pady=10)

        tk.Label(self.root, text="Reference String (e.g. 7,0,1,2,0,3)").pack()
        ref_entry = tk.Entry(self.root, width=50)
        ref_entry.insert(0, "7,0,1,2,0,3,0,4,2,3,0,3,2")
        ref_entry.pack()

        tk.Label(self.root, text="Frame Size").pack()
        f_entry = tk.Entry(self.root, width=10)
        f_entry.insert(0, "3")
        f_entry.pack()

        output = tk.Text(self.root, height=15, width=80)

        def run():
            res = page_replacement.simulate_all(ref_entry.get(), f_entry.get())
            output.delete("1.0", tk.END)
            output.insert(tk.END, res)

        tk.Button(self.root, text="Run All Algorithms", command=run).pack(pady=10)
        output.pack(pady=10)
