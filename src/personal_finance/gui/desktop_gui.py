"""Very small Tkinter GUI that uses GUIService for CRUD operations.

This is intentionally minimal: it demonstrates wiring rather than a polished UI.
Run with: PYTHONPATH=src python -m personal_finance.desktop_gui
"""

import tkinter as tk
from tkinter import ttk, messagebox

from .gui_service import GUIService

service = GUIService()


class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Personal Finance - Mini GUI")
        self.geometry("600x400")

        self.create_widgets()
        self.refresh_tickers()

    def create_widgets(self):
        frm = ttk.Frame(self)
        frm.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Tickers list
        self.ticker_list = tk.Listbox(frm, height=8)
        self.ticker_list.grid(row=0, column=0, columnspan=3, sticky="nsew")

        ttk.Label(frm, text="Symbol").grid(row=1, column=0)
        self.symbol_entry = ttk.Entry(frm)
        self.symbol_entry.grid(row=1, column=1)
        self.name_entry = ttk.Entry(frm)
        self.name_entry.grid(row=1, column=2)

        add_btn = ttk.Button(frm, text="Add Ticker", command=self.add_ticker)
        add_btn.grid(row=1, column=3)

        refresh_btn = ttk.Button(
            frm, text="Refresh", command=self.refresh_tickers
        )
        refresh_btn.grid(row=0, column=3)

        frm.columnconfigure(0, weight=1)
        frm.rowconfigure(0, weight=1)

    def refresh_tickers(self):
        self.ticker_list.delete(0, tk.END)
        try:
            for t in service.list_tickers():
                self.ticker_list.insert(
                    tk.END, f"{t.symbol} - {t.name} - {t.price}"
                )
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def add_ticker(self):
        sym = self.symbol_entry.get().strip().upper()
        name = self.name_entry.get().strip()
        if not sym or not name:
            messagebox.showwarning(
                "Validation", "Symbol and name are required"
            )
            return
        try:
            service.add_ticker(sym, name)
            self.symbol_entry.delete(0, tk.END)
            self.name_entry.delete(0, tk.END)
            self.refresh_tickers()
        except Exception as e:
            messagebox.showerror("Error", str(e))


if __name__ == "__main__":
    app = App()
    app.mainloop()
