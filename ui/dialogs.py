"""
ui/dialogs.py
Janelas modais reutilizáveis.
Para adicionar um novo diálogo, crie uma classe tk.Toplevel aqui.
"""

import threading
import webbrowser
import tkinter as tk
from tkinter import ttk

from core.constants import (
    APP_VERSION, GITHUB_REPO_URL,
    BG_DARK, BG_MID,
    FG_PRIMARY, FG_DIM, FG_ACCENT, FG_GREEN, FG_RED, FG_YELLOW,
    FONT_BODY, FONT_BOLD, FONT_TITLE,
)
from utils.updater import check_for_updates


class UpdateDialog(tk.Toplevel):
    """Janela de verificação de atualizações."""

    def __init__(self, master):
        super().__init__(master)
        self.title("Verificar atualizações")
        self.geometry("500x260")
        self.resizable(False, False)
        self.configure(bg=BG_DARK)
        self.grab_set()

        tk.Label(self, text="🔍  Verificando atualizações…",
                 bg=BG_DARK, fg=FG_ACCENT, font=FONT_TITLE).pack(pady=(24, 8))

        self._msg_var = tk.StringVar(value="Conectando ao GitHub…")
        self._msg_lbl = tk.Label(self, textvariable=self._msg_var,
                                  bg=BG_DARK, fg=FG_DIM, font=FONT_BODY,
                                  wraplength=440, justify="center")
        self._msg_lbl.pack(pady=6, padx=20)

        self._ver_lbl = tk.Label(self, text="", bg=BG_DARK,
                                  fg=FG_GREEN, font=FONT_BOLD)
        self._ver_lbl.pack(pady=4)

        self._link_var = tk.StringVar(value="")
        self._link_lbl = tk.Label(self, textvariable=self._link_var,
                                   bg=BG_DARK, fg=FG_ACCENT,
                                   font=FONT_BODY, cursor="hand2",
                                   underline=True)
        self._link_lbl.pack(pady=2)
        self._link_url = GITHUB_REPO_URL
        self._link_lbl.bind("<Button-1>",
                            lambda e: webbrowser.open(self._link_url))

        ttk.Button(self, text="Fechar", style="Small.TButton",
                   command=self.destroy).pack(pady=16)

        threading.Thread(target=self._do_check, daemon=True).start()

    def _do_check(self):
        has_update, latest, url, error = check_for_updates(timeout=10)

        def update_ui():
            if error and not has_update:
                self._msg_var.set(f"Não foi possível verificar: {error}")
                self._msg_lbl.config(fg=FG_RED)
                self._ver_lbl.config(text=f"Versão atual: v{APP_VERSION}",
                                     fg=FG_DIM)
            elif has_update:
                self._msg_var.set(
                    f"Nova versão disponível! Sua versão: v{APP_VERSION}"
                )
                self._msg_lbl.config(fg=FG_YELLOW)
                self._ver_lbl.config(text=f"Versão disponível: v{latest} ✨",
                                     fg=FG_GREEN)
                self._link_var.set(f"🌐  Baixar em: {url}")
                self._link_url = url
            else:
                self._msg_var.set("Você já está usando a versão mais recente!")
                self._msg_lbl.config(fg=FG_GREEN)
                self._ver_lbl.config(text=f"Versão atual: v{APP_VERSION} ✔",
                                     fg=FG_GREEN)
                self._link_var.set(f"Repositório: {GITHUB_REPO_URL}")
                self._link_url = GITHUB_REPO_URL

        self.after(0, update_ui)
