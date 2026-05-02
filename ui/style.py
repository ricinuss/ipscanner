"""
ui/style.py
Configuração centralizada do ttk.Style.
Para mudar a aparência da UI, edite apenas este arquivo.
"""

from tkinter import ttk
from core.constants import (
    BG_DARK, BG_MID, BG_LIGHT, BG_SELECT, BG_ROW_ODD, BG_ROW_EVEN,
    FG_PRIMARY, FG_DIM, FG_ACCENT,
    BORDER, BTN_BG, BTN_HOVER,
    FONT_BODY, FONT_BOLD, FONT_MONO,
)


def apply(root):
    """Aplica o tema dark ao widget root e todos os filhos ttk."""
    style = ttk.Style(root)
    style.theme_use("clam")

    style.configure(".",
        background=BG_DARK, foreground=FG_PRIMARY,
        fieldbackground=BG_MID, insertcolor=FG_PRIMARY,
        troughcolor=BG_MID, bordercolor=BORDER,
        darkcolor=BG_MID, lightcolor=BG_LIGHT,
        selectbackground=BG_SELECT, selectforeground=FG_PRIMARY,
        font=FONT_BODY,
    )
    style.configure("TFrame",  background=BG_DARK)
    style.configure("TLabel",  background=BG_DARK, foreground=FG_PRIMARY)
    style.configure("TEntry",
        fieldbackground=BG_LIGHT, foreground=FG_PRIMARY,
        insertcolor=FG_PRIMARY, borderwidth=1, relief="flat",
    )

    # ── botões ────────────────────────────────────────────────────────────────
    style.configure("Primary.TButton",
        background=BTN_BG, foreground=FG_ACCENT,
        borderwidth=1, relief="flat", padding=(12, 5), font=FONT_BOLD,
    )
    style.map("Primary.TButton",
        background=[("active", BTN_HOVER), ("pressed", BG_SELECT)],
        foreground=[("active", FG_PRIMARY)],
    )
    style.configure("Danger.TButton",
        background="#3d1f1f", foreground="#ef5350",
        borderwidth=1, relief="flat", padding=(12, 5), font=FONT_BOLD,
    )
    style.map("Danger.TButton",
        background=[("active", "#5a2a2a")],
        foreground=[("active", "#ff8080")],
    )
    style.configure("Small.TButton",
        background=BG_LIGHT, foreground=FG_DIM,
        borderwidth=0, relief="flat", padding=(6, 3), font=FONT_BODY,
    )
    style.map("Small.TButton",
        background=[("active", BTN_HOVER)],
        foreground=[("active", FG_PRIMARY)],
    )

    # ── treeview ──────────────────────────────────────────────────────────────
    style.configure("Treeview",
        background=BG_MID, foreground=FG_PRIMARY,
        fieldbackground=BG_MID, borderwidth=0,
        rowheight=22, font=FONT_BODY,
    )
    style.configure("Treeview.Heading",
        background=BG_LIGHT, foreground=FG_ACCENT,
        borderwidth=0, relief="flat", font=FONT_BOLD, padding=(8, 5),
    )
    style.map("Treeview",
        background=[("selected", BG_SELECT)],
        foreground=[("selected", FG_PRIMARY)],
    )
    style.map("Treeview.Heading",
        background=[("active", BTN_HOVER)],
    )

    # ── outros ────────────────────────────────────────────────────────────────
    style.configure("Horizontal.TProgressbar",
        troughcolor=BG_LIGHT, background=FG_ACCENT, borderwidth=0, thickness=4,
    )
    style.configure("TCombobox",
        fieldbackground=BG_LIGHT, background=BG_LIGHT,
        foreground=FG_PRIMARY, arrowcolor=FG_ACCENT, borderwidth=1,
    )
    style.map("TCombobox",
        fieldbackground=[("readonly", BG_LIGHT)],
        selectbackground=[("readonly", BG_SELECT)],
    )
    style.configure("TCheckbutton",
        background=BG_DARK, foreground=FG_PRIMARY,
        indicatorcolor=BG_LIGHT, indicatordiameter=13,
    )
    style.map("TCheckbutton",
        indicatorcolor=[("selected", FG_ACCENT)],
    )
