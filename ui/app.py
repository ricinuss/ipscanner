"""
ui/app.py
Janela principal — monta a UI e coordena os módulos.
Lógica de scan em core/scanner.py | Estilo em ui/style.py
"""

import csv
import ipaddress
import logging
import queue
import socket
import threading
import webbrowser
from concurrent.futures import ThreadPoolExecutor, as_completed

import tkinter as tk
from tkinter import ttk, messagebox, filedialog

from core.constants import (
    APP_TITLE, APP_VERSION, APP_AUTHOR, GITHUB_REPO_URL,
    BG_DARK, BG_MID, BG_LIGHT, BG_SELECT,
    FG_PRIMARY, FG_DIM, FG_ACCENT, FG_GREEN, FG_RED, FG_YELLOW,
    BORDER, BTN_BG,
    FONT_BODY, FONT_BOLD, FONT_MONO, FONT_TITLE,
)
from core.scanner import (
    DeviceInfo, HAS_NMAP, HAS_MAC,
    scan_device,
)
from ui import style as ui_style
from ui.dialogs import UpdateDialog
from utils.updater import check_for_updates
from utils.help_text import HELP_TEXT, get_about_text

logger = logging.getLogger("ipscanner.ui")


class AdvancedIPScannerApp(tk.Tk):
    """Janela principal do Advanced IP Scanner."""

    def __init__(self):
        super().__init__()
        self.title(f"{APP_TITLE} {APP_VERSION} — by {APP_AUTHOR}")
        self.geometry("1080x680")
        self.minsize(800, 500)
        self.configure(bg=BG_DARK)

        self._scan_thread  = None
        self._stop_event   = threading.Event()
        self._result_queue: queue.Queue = queue.Queue()
        self._devices:  dict[str, DeviceInfo] = {}
        self._tree_ids: dict[str, str]         = {}
        self._scan_running = False
        self._total_hosts  = 0
        self._scanned      = 0
        self._row_idx      = 0
        self._sort_reverse: dict[str, bool]    = {}  # toggle ASC/DESC por coluna

        ui_style.apply(self)
        self._build_ui()
        self._detect_network()
        self._bind_shortcuts()
        self.after(100, self._poll_results)

        # verifica updates em background
        threading.Thread(target=self._auto_check_updates, daemon=True).start()

    # ══════════════════════════════════════════════════════════════════════════
    #  ATALHOS DE TECLADO
    # ══════════════════════════════════════════════════════════════════════════

    def _bind_shortcuts(self):
        """Registra atalhos de teclado globais."""
        self.bind("<F5>",           lambda e: self._start_scan())
        self.bind("<Escape>",       lambda e: self._stop_scan())
        self.bind("<Control-e>",    lambda e: self._export_csv())
        self.bind("<Control-E>",    lambda e: self._export_csv())
        self.bind("<Control-l>",    lambda e: self._clear_results())
        self.bind("<Control-L>",    lambda e: self._clear_results())

    # ══════════════════════════════════════════════════════════════════════════
    #  CONSTRUÇÃO DA UI
    # ══════════════════════════════════════════════════════════════════════════

    def _build_ui(self):
        self._build_menubar()
        self._build_toolbar()
        self._build_main()
        self._build_statusbar()

    def _build_menubar(self):
        MB_STYLE = dict(
            bg=BG_MID, fg=FG_PRIMARY,
            activebackground=BG_SELECT, activeforeground=FG_PRIMARY,
            borderwidth=0, relief="flat",
        )
        mb = tk.Menu(self, **MB_STYLE)
        self.config(menu=mb)

        def menu(parent, items):
            m = tk.Menu(parent, tearoff=0, **MB_STYLE)
            for item in items:
                if item is None:
                    m.add_separator()
                else:
                    label, cmd = item
                    m.add_command(label=label, command=cmd)
            return m

        mb.add_cascade(label="Arquivo", menu=menu(mb, [
            ("Exportar resultados (CSV)…", self._export_csv),
            None,
            ("Sair", self.destroy),
        ]))
        mb.add_cascade(label="Scan", menu=menu(mb, [
            ("Iniciar scan",  self._start_scan),
            ("Parar scan",    self._stop_scan),
            None,
            ("Limpar tabela", self._clear_results),
        ]))
        mb.add_cascade(label="Ajuda", menu=menu(mb, [
            ("📖  Como usar (Guia completo)",  self._show_help),
            None,
            ("🔔  Verificar atualizações",     self._check_updates_manual),
            ("🌐  Ver repositório no GitHub",  lambda: webbrowser.open(GITHUB_REPO_URL)),
            None,
            ("🔁  Reinstalar dependências",    self._reinstall_deps),
            None,
            ("⭐  Sobre / Créditos",           self._show_about),
        ]))

    def _build_toolbar(self):
        bar = tk.Frame(self, bg=BG_MID, height=52, bd=0)
        bar.pack(fill="x", side="top")
        bar.pack_propagate(False)

        def lbl(text):
            return tk.Label(bar, text=text, bg=BG_MID, fg=FG_DIM, font=FONT_BODY)

        lbl("Rede:").pack(side="left", padx=(14, 4), pady=12)

        self._net_var = tk.StringVar()
        self._net_cb  = ttk.Combobox(bar, textvariable=self._net_var,
                                      width=22, font=FONT_MONO)
        self._net_cb.pack(side="left", padx=(0, 10), pady=12, ipady=3)

        lbl("De:").pack(side="left", padx=(0, 4))
        self._ip_start = ttk.Entry(bar, width=5, font=FONT_MONO)
        self._ip_start.insert(0, "1")
        self._ip_start.pack(side="left", padx=(0, 4), ipady=3)

        lbl("Até:").pack(side="left", padx=(0, 4))
        self._ip_end = ttk.Entry(bar, width=5, font=FONT_MONO)
        self._ip_end.insert(0, "254")
        self._ip_end.pack(side="left", padx=(0, 12), ipady=3)

        self._adv_var = tk.BooleanVar(value=False)
        adv = ttk.Checkbutton(bar, text="Scan avançado (nmap)",
                               variable=self._adv_var)
        adv.pack(side="left", padx=(0, 14))
        if not HAS_NMAP:
            adv.config(state="disabled")
            tk.Label(bar, text="[nmap não instalado]",
                     bg=BG_MID, fg=FG_RED, font=FONT_BODY).pack(side="left")

        self._btn_scan = ttk.Button(bar, text="▶  Verificar",
                                    style="Primary.TButton", command=self._start_scan)
        self._btn_scan.pack(side="left", padx=(0, 6))

        self._btn_stop = ttk.Button(bar, text="⏹  Parar",
                                    style="Danger.TButton", command=self._stop_scan,
                                    state="disabled")
        self._btn_stop.pack(side="left", padx=(0, 6))

        ttk.Button(bar, text="🗑 Limpar", style="Small.TButton",
                   command=self._clear_results).pack(side="left")

        lbl("Threads:").pack(side="right", padx=(0, 4))
        self._threads_var = tk.IntVar(value=64)
        self._threads_spin = tk.Spinbox(
            bar, from_=8, to=256, increment=8,
            textvariable=self._threads_var, width=4,
            bg=BG_LIGHT, fg=FG_PRIMARY, buttonbackground=BG_LIGHT,
            relief="flat", font=FONT_MONO,
            validate="key",
            validatecommand=(
                self.register(lambda v: v.isdigit() or v == ""), "%P"
            ),
        )
        self._threads_spin.pack(side="right", padx=(0, 14))

    def _build_main(self):
        paned = tk.PanedWindow(self, orient="vertical", bg=BORDER,
                               sashwidth=4, sashrelief="flat")
        paned.pack(fill="both", expand=True)

        # ── tabela ────────────────────────────────────────────────────────────
        top = tk.Frame(paned, bg=BG_DARK)
        paned.add(top, minsize=250)

        cols = ("ip", "name", "mac", "vendor", "dtype", "os", "ping")
        self._tree = ttk.Treeview(top, columns=cols,
                                   show="tree headings", selectmode="extended")
        self._tree.tag_configure("row_odd",  background="#1e2229")
        self._tree.tag_configure("row_even", background=BG_MID)
        self._tree.tag_configure("service",  background=BG_DARK, foreground=FG_DIM)
        self._tree.tag_configure("alive",    foreground=FG_GREEN)

        self._tree.heading("#0", text="", anchor="w")
        self._tree.column("#0", width=22, minwidth=22, stretch=False)

        for cid, text, w, anch in [
            ("ip",     "Endereço IP",  130, "w"),
            ("name",   "Nome",         200, "w"),
            ("mac",    "Endereço MAC", 145, "w"),
            ("vendor", "Fabricante",   170, "w"),
            ("dtype",  "Tipo",         190, "w"),
            ("os",     "Sistema Op.",  160, "w"),
            ("ping",   "Ping (ms)",     80, "e"),
        ]:
            self._tree.heading(cid, text=text,
                               command=lambda c=cid: self._sort_col(c))
            self._tree.column(cid, width=w, minwidth=60, anchor=anch)

        vsb = ttk.Scrollbar(top, orient="vertical",   command=self._tree.yview)
        hsb = ttk.Scrollbar(top, orient="horizontal", command=self._tree.xview)
        self._tree.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)
        vsb.pack(side="right",  fill="y")
        hsb.pack(side="bottom", fill="x")
        self._tree.pack(fill="both", expand=True)

        self._tree.bind("<Double-Button-1>",  self._on_double_click)
        self._tree.bind("<Button-3>",         self._on_right_click)
        self._tree.bind("<<TreeviewSelect>>", self._on_select)

        # ── painel de detalhes ────────────────────────────────────────────────
        bot = tk.Frame(paned, bg=BG_MID)
        paned.add(bot, minsize=100)

        hdr = tk.Frame(bot, bg=BG_LIGHT, height=26)
        hdr.pack(fill="x")
        hdr.pack_propagate(False)
        tk.Label(hdr, text="  Detalhes do dispositivo",
                 bg=BG_LIGHT, fg=FG_ACCENT, font=FONT_BOLD).pack(side="left", pady=3)

        self._detail_text = tk.Text(
            bot, bg=BG_MID, fg=FG_PRIMARY, relief="flat", bd=0,
            font=FONT_MONO, wrap="none", state="disabled",
            insertbackground=FG_PRIMARY, selectbackground=BG_SELECT, height=6,
        )
        dsb = ttk.Scrollbar(bot, orient="vertical",
                            command=self._detail_text.yview)
        self._detail_text.configure(yscrollcommand=dsb.set)
        dsb.pack(side="right", fill="y")
        self._detail_text.pack(fill="both", expand=True, padx=6, pady=4)

        for tag, fg, extra in [
            ("h",    FG_ACCENT,  {"font": FONT_BOLD}),
            ("key",  FG_DIM,     {}),
            ("val",  FG_PRIMARY, {}),
            ("svc",  FG_GREEN,   {}),
            ("link", FG_ACCENT,  {"underline": True}),
        ]:
            self._detail_text.tag_config(tag, foreground=fg, **extra)

    def _build_statusbar(self):
        bar = tk.Frame(self, bg=BG_LIGHT, height=26)
        bar.pack(fill="x", side="bottom")
        bar.pack_propagate(False)

        tk.Label(bar, text=f"  {APP_TITLE} {APP_VERSION} by {APP_AUTHOR}",
                 bg=BG_LIGHT, fg="#3a4055", font=FONT_BODY).pack(side="left")

        self._count_var = tk.StringVar(value="")
        tk.Label(bar, textvariable=self._count_var,
                 bg=BG_LIGHT, fg=FG_GREEN, font=FONT_BOLD).pack(side="right", padx=10)

        self._progress = ttk.Progressbar(
            bar, style="Horizontal.TProgressbar",
            mode="determinate", length=220,
        )
        self._progress.pack(side="right", padx=(0, 12), pady=5)

        self._status_var = tk.StringVar(
            value="Pronto. Use Ajuda → Como usar para instruções."
        )
        tk.Label(bar, textvariable=self._status_var,
                 bg=BG_LIGHT, fg=FG_DIM, font=FONT_BODY).pack(side="left", padx=10)

    # ══════════════════════════════════════════════════════════════════════════
    #  DETECÇÃO DE REDE
    # ══════════════════════════════════════════════════════════════════════════

    def _saved_networks(self) -> list[str]:
        nets = []
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
                s.connect(("8.8.8.8", 80))
                ip = s.getsockname()[0]
            parts = ip.split(".")
            nets.append(f"{parts[0]}.{parts[1]}.{parts[2]}.0/24")
        except OSError:
            pass
        for n in ["192.168.0.0/24", "192.168.1.0/24",
                  "10.0.0.0/24", "172.16.0.0/24"]:
            if n not in nets:
                nets.append(n)
        return nets

    def _detect_network(self):
        nets = self._saved_networks()
        self._net_var.set(nets[0] if nets else "192.168.1.0/24")
        self._net_cb["values"] = nets

    # ══════════════════════════════════════════════════════════════════════════
    #  SCAN
    # ══════════════════════════════════════════════════════════════════════════

    def _get_hosts(self) -> list:
        raw = self._net_var.get().strip()
        try:
            net = ipaddress.ip_network(raw, strict=False)
        except ValueError:
            messagebox.showerror("Erro",
                                 f"Rede inválida: {raw}\nExemplo: 192.168.1.0/24")
            return []
        all_hosts = list(net.hosts())
        try:
            s = max(1,   min(int(self._ip_start.get()), 254))
            e = max(s,   min(int(self._ip_end.get()),   254))
            all_hosts = [h for h in all_hosts
                         if s <= int(str(h).split(".")[-1]) <= e]
        except ValueError:
            pass
        return all_hosts

    def _start_scan(self):
        if self._scan_running:
            return
        hosts = self._get_hosts()
        if not hosts:
            return
        self._clear_results()
        self._scan_running = True
        self._total_hosts  = len(hosts)
        self._scanned      = 0
        self._stop_event.clear()
        self._btn_scan.config(state="disabled")
        self._btn_stop.config(state="normal")
        self._progress.config(maximum=self._total_hosts, value=0)
        self._status_var.set(f"Escaneando {self._total_hosts} hosts…")
        self._count_var.set("")

        adv     = self._adv_var.get()
        raw_threads = self._threads_var.get()
        threads = max(8, min(256, raw_threads))  # clamp para faixa segura
        stop    = self._stop_event
        q       = self._result_queue

        def runner():
            def worker(ip_obj):
                if stop.is_set():
                    q.put(("progress", None)); return
                dev = scan_device(str(ip_obj), advanced=adv, stop_event=stop)
                q.put(("progress", dev))

            with ThreadPoolExecutor(max_workers=threads) as pool:
                futures = [pool.submit(worker, ip) for ip in hosts]
                for _ in as_completed(futures):
                    if stop.is_set():
                        break
            q.put(("done", None))

        self._scan_thread = threading.Thread(target=runner, daemon=True)
        self._scan_thread.start()

    def _stop_scan(self):
        self._stop_event.set()
        self._status_var.set("Parando…")

    def _poll_results(self):
        processed = 0
        while not self._result_queue.empty() and processed < 20:
            kind, dev = self._result_queue.get_nowait()
            processed += 1
            if kind == "progress":
                self._scanned += 1
                self._progress["value"] = self._scanned
                pct = int(self._scanned / self._total_hosts * 100) \
                      if self._total_hosts else 0
                self._status_var.set(
                    f"Escaneando… {self._scanned}/{self._total_hosts} ({pct}%)"
                )
                if dev:
                    self._add_device(dev)
                    self._count_var.set(
                        f"{len(self._devices)} dispositivos encontrados"
                    )
            elif kind == "done":
                self._scan_running = False
                self._btn_scan.config(state="normal")
                self._btn_stop.config(state="disabled")
                self._status_var.set(
                    f"Scan concluído — {len(self._devices)} dispositivos "
                    f"em {self._total_hosts} hosts verificados."
                )
                self._progress["value"] = self._total_hosts
        self.after(100, self._poll_results)

    # ══════════════════════════════════════════════════════════════════════════
    #  TREEVIEW
    # ══════════════════════════════════════════════════════════════════════════

    def _sorted_ip_index(self, new_ip: str) -> int:
        """Retorna o índice onde inserir new_ip para manter ordem numérica."""
        children = self._tree.get_children("")
        try:
            new_addr = ipaddress.ip_address(new_ip)
        except ValueError:
            return len(children)
        for i, iid in enumerate(children):
            vals = self._tree.item(iid, "values")
            if not vals:
                continue
            try:
                if new_addr < ipaddress.ip_address(vals[0].strip()):
                    return i
            except ValueError:
                continue
        return len(children)

    def _add_device(self, dev: DeviceInfo):
        self._devices[dev.ip] = dev

        # Inserir na posição correta (ordem numérica de IP)
        idx = self._sorted_ip_index(dev.ip)

        # Determina tag de cor com base no índice real na árvore
        tag = "row_odd" if idx % 2 else "row_even"
        self._row_idx += 1

        iid = self._tree.insert(
            "", idx, text="",
            values=(
                dev.ip,
                dev.hostname or "—",
                dev.mac      or "—",
                dev.vendor   or "—",
                f"{dev.icon} {dev.dtype}",
                dev.os       or "—",
                f"{dev.latency:.0f}" if dev.latency else "—",
            ),
            tags=(tag, "alive"), open=False,
        )
        self._tree_ids[dev.ip] = iid
        for port, label, scheme in dev.services:
            url = self._make_url(dev.ip, port, scheme)
            child = f"{iid}_svc_{port}"
            self._tree.insert(iid, "end", text="",
                values=(f"  ↳ :{port}", label, "", "", "", "", ""),
                tags=("service",), iid=child)
            self._tree.set(child, "mac", url or "")
        self._tree.see(iid)

    def _reapply_zebra(self):
        """Recalcula as tags de zebra (odd/even) para todas as linhas de topo."""
        for i, iid in enumerate(self._tree.get_children("")):
            current_tags = list(self._tree.item(iid, "tags"))
            # Remove tags de zebra existentes
            new_tags = [t for t in current_tags
                        if t not in ("row_odd", "row_even")]
            new_tags.insert(0, "row_odd" if i % 2 else "row_even")
            self._tree.item(iid, tags=tuple(new_tags))

    @staticmethod
    def _make_url(ip: str, port: int, scheme: str) -> str:
        if not scheme:
            return ""
        if scheme in ("http", "https", "ftp"):
            return f"{scheme}://{ip}:{port}"
        if scheme == "ssh":
            return f"ssh://{ip}:{port}"
        if scheme == "vnc":
            return f"vnc://{ip}:{port}"
        return ""

    def _clear_results(self):
        for iid in self._tree.get_children():
            self._tree.delete(iid)
        self._devices.clear()
        self._tree_ids.clear()
        self._row_idx = 0
        self._detail_text.config(state="normal")
        self._detail_text.delete("1.0", "end")
        self._detail_text.config(state="disabled")
        self._count_var.set("")

    def _sort_col(self, col: str):
        """Ordena a coluna clicada com toggle ASC/DESC; recalcula zebra."""
        # Toggle direção
        reverse = self._sort_reverse.get(col, False)
        self._sort_reverse[col] = not reverse

        # Coleta apenas nós de topo (dispositivos, não serviços-filhos)
        top_items = self._tree.get_children("")
        data = [(self._tree.set(k, col), k) for k in top_items]
        if col == "ip":
            try:
                data.sort(key=lambda x: ipaddress.ip_address(x[0].strip()),
                          reverse=reverse)
            except Exception:
                data.sort(reverse=reverse)
        elif col == "ping":
            def ping_key(x):
                try:
                    return float(x[0])
                except Exception:
                    return float("inf")
            data.sort(key=ping_key, reverse=reverse)
        else:
            data.sort(key=lambda x: x[0].lower(), reverse=reverse)
        for i, (_, k) in enumerate(data):
            self._tree.move(k, "", i)
        self._reapply_zebra()

        # Indicador visual na coluna
        arrow = " ▲" if not reverse else " ▼"
        col_headings = {
            "ip": "Endereço IP", "name": "Nome", "mac": "Endereço MAC",
            "vendor": "Fabricante", "dtype": "Tipo", "os": "Sistema Op.",
            "ping": "Ping (ms)",
        }
        for c, text in col_headings.items():
            self._tree.heading(c, text=text + (arrow if c == col else ""))

    # ══════════════════════════════════════════════════════════════════════════
    #  EVENTOS
    # ══════════════════════════════════════════════════════════════════════════

    def _on_select(self, _event):
        sel = self._tree.selection()
        if not sel:
            return
        iid = sel[0]
        if self._tree.parent(iid):
            iid = self._tree.parent(iid)
        vals = self._tree.item(iid, "values")
        if not vals:
            return
        dev = self._devices.get(vals[0].strip())
        if dev:
            self._show_detail(dev)

    def _on_double_click(self, event):
        iid = self._tree.identify_row(event.y)
        if not iid:
            return
        if self._tree.parent(iid):
            url = self._tree.set(iid, "mac")
            if url:
                webbrowser.open(url)
            return
        vals = self._tree.item(iid, "values")
        ip   = vals[0].strip()
        dev  = self._devices.get(ip)
        if dev:
            for port, label, scheme in dev.services:
                if scheme in ("http", "https"):
                    webbrowser.open(f"{scheme}://{ip}:{port}")
                    return

    def _on_right_click(self, event):
        iid = self._tree.identify_row(event.y)
        if not iid:
            return
        self._tree.selection_set(iid)
        parent = self._tree.parent(iid)
        vals = self._tree.item(parent or iid, "values")
        if not vals:
            return
        ip  = vals[0].strip()
        dev = self._devices.get(ip)

        MN = dict(bg=BG_MID, fg=FG_PRIMARY,
                  activebackground=BG_SELECT, activeforeground=FG_PRIMARY)
        menu = tk.Menu(self, tearoff=0, **MN)
        menu.add_command(label=f"📋  Copiar IP  ({ip})",
                         command=lambda: self._copy(ip))
        if dev and dev.mac:
            menu.add_command(label=f"📋  Copiar MAC  ({dev.mac})",
                             command=lambda: self._copy(dev.mac))
        if dev and dev.hostname:
            menu.add_command(label=f"📋  Copiar hostname  ({dev.hostname})",
                             command=lambda: self._copy(dev.hostname))
        menu.add_separator()
        if dev:
            for port, label, scheme in dev.services:
                url = self._make_url(ip, port, scheme)
                if url:
                    menu.add_command(
                        label=f"🌐  Abrir {label.split(' ', 1)[-1]}  ({url})",
                        command=lambda u=url: webbrowser.open(u),
                    )
        menu.add_separator()
        menu.add_command(label="🔁  Re-escanear este host",
                         command=lambda: self._rescan_host(ip))
        menu.add_command(label="📄  Ver detalhes completos",
                         command=lambda: self._show_detail(dev) if dev else None)
        menu.post(event.x_root, event.y_root)

    # ══════════════════════════════════════════════════════════════════════════
    #  PAINEL DE DETALHES
    # ══════════════════════════════════════════════════════════════════════════

    def _show_detail(self, dev: DeviceInfo):
        t = self._detail_text
        t.config(state="normal")
        t.delete("1.0", "end")

        def w(text, tag=None):
            t.insert("end", text, tag) if tag else t.insert("end", text)

        w(f"  {dev.icon}  {dev.dtype}  —  {dev.ip}\n", "h")
        w("\n")
        w("  Hostname:   ", "key"); w(f"{dev.hostname or '—'}\n", "val")
        w("  MAC:        ", "key"); w(f"{dev.mac      or '—'}\n", "val")
        w("  Fabricante: ", "key"); w(f"{dev.vendor   or '—'}\n", "val")
        w("  Sistema Op: ", "key"); w(f"{dev.os       or '—'}\n", "val")
        w("  Latência:   ", "key"); w(f"{dev.latency:.1f} ms\n", "val")

        if dev.services:
            w("\n  Serviços abertos:\n", "key")
            for port, label, scheme in dev.services:
                url = self._make_url(dev.ip, port, scheme)
                w(f"    • {label:<28}", "svc")
                if url:
                    tag_name = f"link_{port}"
                    t.insert("end", url, ("link", tag_name))
                    t.tag_bind(tag_name, "<Button-1>",
                               lambda e, u=url: webbrowser.open(u))
                    t.tag_bind(tag_name, "<Enter>",
                               lambda e: t.config(cursor="hand2"))
                    t.tag_bind(tag_name, "<Leave>",
                               lambda e: t.config(cursor=""))
                w("\n")
        t.config(state="disabled")

    # ══════════════════════════════════════════════════════════════════════════
    #  AÇÕES
    # ══════════════════════════════════════════════════════════════════════════

    def _copy(self, text: str):
        self.clipboard_clear()
        self.clipboard_append(text)
        self._status_var.set(f"Copiado: {text}")

    def _rescan_host(self, ip: str):
        adv = self._adv_var.get()
        self._status_var.set(f"Re-escaneando {ip}…")

        def worker():
            dev = scan_device(ip, advanced=adv)
            if dev:
                self.after(0, lambda: self._update_device(dev))
                self.after(0, lambda: self._status_var.set(
                    f"Re-scan concluído: {ip}"))
            else:
                self.after(0, lambda: self._status_var.set(
                    f"{ip} não respondeu."))

        threading.Thread(target=worker, daemon=True).start()

    def _update_device(self, dev: DeviceInfo):
        old_iid = self._tree_ids.get(dev.ip)
        if old_iid:
            try:
                self._tree.delete(old_iid)
            except Exception:
                pass
        self._devices.pop(dev.ip, None)
        self._tree_ids.pop(dev.ip, None)
        self._add_device(dev)
        self._reapply_zebra()

    def _export_csv(self):
        path = filedialog.asksaveasfilename(
            defaultextension=".csv",
            filetypes=[("CSV", "*.csv"), ("Todos", "*.*")],
            title="Exportar resultados",
        )
        if not path:
            return
        with open(path, "w", newline="", encoding="utf-8") as f:
            w = csv.writer(f)
            w.writerow(["IP", "Hostname", "MAC", "Fabricante",
                        "Tipo", "SO", "Ping(ms)", "Serviços"])
            for dev in self._devices.values():
                svcs = ", ".join(f"{p}={l}" for p, l, _ in dev.services)
                w.writerow([dev.ip, dev.hostname, dev.mac, dev.vendor,
                            dev.dtype, dev.os, dev.latency, svcs])
        self._status_var.set(f"Exportado: {path}")

    # ══════════════════════════════════════════════════════════════════════════
    #  ATUALIZAÇÕES
    # ══════════════════════════════════════════════════════════════════════════

    def _auto_check_updates(self):
        has_update, latest, url, _ = check_for_updates(timeout=8)
        if has_update:
            self.after(0, lambda: self._status_var.set(
                f"🔔  Nova versão disponível: v{latest}"
                "  —  Ajuda → Verificar atualizações"
            ))

    def _check_updates_manual(self):
        UpdateDialog(self)

    # ══════════════════════════════════════════════════════════════════════════
    #  JANELAS DE AJUDA
    # ══════════════════════════════════════════════════════════════════════════

    def _show_text_window(self, title: str, content: str,
                          width: int = 72, height: int = 36):
        win = tk.Toplevel(self)
        win.title(title)
        win.configure(bg=BG_DARK)
        win.geometry(f"{width * 9}x{height * 20}")
        win.resizable(True, True)
        win.grab_set()

        hdr = tk.Frame(win, bg=BG_MID, height=36)
        hdr.pack(fill="x")
        hdr.pack_propagate(False)
        tk.Label(hdr, text=f"  {title}", bg=BG_MID, fg=FG_ACCENT,
                 font=FONT_BOLD).pack(side="left", pady=8)

        frame = tk.Frame(win, bg=BG_DARK)
        frame.pack(fill="both", expand=True, padx=10, pady=10)

        txt = tk.Text(frame, bg=BG_MID, fg=FG_PRIMARY, relief="flat", bd=0,
                      font=FONT_MONO, wrap="none", state="normal",
                      selectbackground=BG_SELECT,
                      insertbackground=FG_PRIMARY)
        vsb = ttk.Scrollbar(frame, orient="vertical",   command=txt.yview)
        hsb = ttk.Scrollbar(frame, orient="horizontal", command=txt.xview)
        txt.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)
        vsb.pack(side="right",  fill="y")
        hsb.pack(side="bottom", fill="x")
        txt.pack(fill="both", expand=True)
        txt.insert("1.0", content)
        txt.config(state="disabled")

        ttk.Button(win, text="Fechar", style="Small.TButton",
                   command=win.destroy).pack(pady=(0, 10))

    def _show_help(self):
        self._show_text_window("📖  Como usar", HELP_TEXT, width=74, height=38)

    def _show_about(self):
        self._show_text_window(
            f"⭐  Sobre — {APP_TITLE}",
            get_about_text(HAS_NMAP, HAS_MAC),
            width=66, height=32,
        )

    def _reinstall_deps(self):
        from core.installer import _MARKER
        if messagebox.askyesno(
            "Reinstalar dependências",
            "Isso apagará o marcador de instalação.\n"
            "Feche e reabra o programa para reinstalar.\n\nDeseja continuar?"
        ):
            _MARKER.unlink(missing_ok=True)
            messagebox.showinfo("Agendado",
                                "Feche e reabra o programa para reinstalar.")
