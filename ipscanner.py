#!/usr/bin/env python3
"""
Advanced IP Scanner GUI — Linux
Tkinter clone do Advanced IP Scanner com hierarquia de serviços,
scan avançado (nmap), abertura de serviços e seleção de rede.

Uso:
    python3 ip_scanner_gui.py
    sudo python3 ip_scanner_gui.py   ← para detecção de SO (nmap -O)

Dependências (instaladas automaticamente na primeira execução):
    python-nmap, mac-vendor-lookup
    nmap (via apt/dnf/pacman)

Créditos:
    Desenvolvido por ricinus
"""

# ══════════════════════════════════════════════════════════════════════════════
#  INSTALADOR AUTOMÁTICO — roda ANTES de qualquer import opcional
# ══════════════════════════════════════════════════════════════════════════════
import sys, os, subprocess, json, pathlib

_MARKER = pathlib.Path.home() / ".ipscan_deps_installed"
_DEPS_VERSION = "3"   # incremente para forçar reinstalação futura

# ── versão atual do app (usada também na verificação de updates) ──────────────
APP_VERSION = "2.1"
GITHUB_REPO = "ricinuss/ipscanner"
GITHUB_API_URL = f"https://api.github.com/repos/{GITHUB_REPO}/releases/latest"
GITHUB_REPO_URL = f"https://github.com/{GITHUB_REPO}/tree/main"

def _run(cmd, **kw):
    return subprocess.run(cmd, **kw)

def _detect_distro():
    """Retorna ('debian'|'redhat'|'arch'|'suse'|'unknown', pkg_manager)"""
    if pathlib.Path("/etc/debian_version").exists():
        mgr = "apt-get"
        if _run(["which","nala"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL).returncode == 0:
            mgr = "nala"
        return "debian", mgr
    if pathlib.Path("/etc/fedora-release").exists() or pathlib.Path("/etc/redhat-release").exists():
        for m in ("dnf","yum"):
            if _run(["which",m], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL).returncode == 0:
                return "redhat", m
    if pathlib.Path("/etc/arch-release").exists():
        return "arch", "pacman"
    if pathlib.Path("/etc/SuSE-release").exists() or pathlib.Path("/etc/opensuse-release").exists():
        return "suse", "zypper"
    return "unknown", ""

def _pip_install(*pkgs):
    _run([sys.executable, "-m", "pip", "install", "--quiet",
          "--break-system-packages", "--root-user-action=ignore", *pkgs])

def _install_nmap_bin(distro, mgr):
    try:
        is_root = os.geteuid() == 0
        prefix = [] if is_root else ["sudo"]
        if distro == "debian":
            _run([*prefix, mgr, "install", "-y", "nmap"], check=False)
        elif distro == "redhat":
            _run([*prefix, mgr, "install", "-y", "nmap"], check=False)
        elif distro == "arch":
            _run([*prefix, "pacman", "-S", "--noconfirm", "nmap"], check=False)
        elif distro == "suse":
            _run([*prefix, "zypper", "install", "-y", "nmap"], check=False)
    except Exception:
        pass

def _already_installed():
    if not _MARKER.exists():
        return False
    try:
        data = json.loads(_MARKER.read_text())
        return data.get("version") == _DEPS_VERSION
    except Exception:
        return False

def _mark_installed():
    _MARKER.write_text(json.dumps({"version": _DEPS_VERSION}))

def _update_mac_vendors_with_timeout(timeout_sec=15):
    """
    Atualiza a base de MACs com timeout — evita travamento indefinido.
    Roda em thread separada com join(timeout).
    """
    import threading
    result = {"ok": False, "msg": ""}

    def _do_update():
        try:
            from mac_vendor_lookup import MacLookup
            MacLookup().update_vendors()
            result["ok"]  = True
            result["msg"] = "✔ Base de fabricantes atualizada."
        except Exception as e:
            result["ok"]  = False
            result["msg"] = f"⚠ Não foi possível atualizar a base de fabricantes: {e}"

    t = threading.Thread(target=_do_update, daemon=True)
    t.start()
    t.join(timeout_sec)
    if t.is_alive():
        return False, f"⚠ Atualização da base de MACs expirou após {timeout_sec}s (sem internet?). Continuando com base local."
    return result["ok"], result["msg"]

def _run_installer_window():
    """Exibe janela de instalação Tkinter (básico, sem dependências externas)."""
    import tkinter as tk
    from tkinter import ttk

    root = tk.Tk()
    root.title("Advanced IP Scanner — Configuração Inicial")
    root.geometry("560x380")
    root.resizable(False, False)
    root.configure(bg="#1a1d23")

    tk.Label(root, text="🔍  Advanced IP Scanner",
             bg="#1a1d23", fg="#4fc3f7",
             font=("monospace", 15, "bold")).pack(pady=(28,4))
    tk.Label(root, text="Instalação de Dependências — Primeira Execução",
             bg="#1a1d23", fg="#7a8299",
             font=("monospace", 9)).pack(pady=(0,18))

    frame = tk.Frame(root, bg="#22262f", bd=0)
    frame.pack(fill="x", padx=30)

    log_box = tk.Text(frame, bg="#22262f", fg="#e8eaf0",
                      relief="flat", bd=0, height=10,
                      font=("Courier New", 9), state="disabled",
                      insertbackground="#4fc3f7")
    log_box.pack(fill="x", padx=10, pady=10)

    pbar = ttk.Progressbar(root, mode="indeterminate", length=500)
    pbar.pack(pady=10, padx=30)

    status_var = tk.StringVar(value="Iniciando…")
    tk.Label(root, textvariable=status_var,
             bg="#1a1d23", fg="#66bb6a",
             font=("monospace", 9)).pack()

    def log(msg):
        log_box.config(state="normal")
        log_box.insert("end", msg + "\n")
        log_box.see("end")
        log_box.config(state="disabled")
        root.update_idletasks()

    def run_install():
        pbar.start(12)
        distro, mgr = _detect_distro()
        log(f"► Distribuição detectada: {distro.upper()} ({mgr or 'desconhecido'})")

        # nmap binário
        nmap_ok = _run(["which","nmap"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL).returncode == 0
        if nmap_ok:
            log("✔ nmap já instalado.")
        else:
            status_var.set("Instalando nmap…")
            log("► Instalando nmap via gerenciador de pacotes…")
            _install_nmap_bin(distro, mgr)
            nmap_ok2 = _run(["which","nmap"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL).returncode == 0
            log("✔ nmap instalado com sucesso." if nmap_ok2 else
                "⚠ Não foi possível instalar nmap automaticamente.\n  Instale manualmente: sudo apt install nmap")

        # python-nmap
        status_var.set("Instalando python-nmap…")
        log("► Instalando python-nmap (wrapper Python)…")
        try:
            _pip_install("python-nmap")
            log("✔ python-nmap instalado.")
        except Exception as e:
            log(f"⚠ Erro ao instalar python-nmap: {e}")

        # mac-vendor-lookup
        status_var.set("Instalando mac-vendor-lookup…")
        log("► Instalando mac-vendor-lookup…")
        try:
            _pip_install("mac-vendor-lookup")
            log("✔ mac-vendor-lookup instalado.")
        except Exception as e:
            log(f"⚠ Erro ao instalar mac-vendor-lookup: {e}")

        # atualiza base de MACs com timeout
        status_var.set("Atualizando base de fabricantes (MAC)…")
        log("► Atualizando base de dados de fabricantes (timeout: 15s)…")
        ok, msg = _update_mac_vendors_with_timeout(timeout_sec=15)
        log(msg)

        _mark_installed()
        pbar.stop()
        status_var.set("Instalação concluída! Iniciando scanner…")
        log("\n✅ Tudo pronto! O scanner será aberto em instantes.")
        root.after(1800, root.destroy)

    root.after(300, lambda: __import__("threading").Thread(target=run_install, daemon=True).start())
    root.mainloop()

# ── ponto de entrada do instalador ───────────────────────────────────────────
if not _already_installed():
    try:
        _run_installer_window()
    except Exception as e:
        print(f"[Instalador] {e}. Tentando instalar dependências em modo silencioso…")
        distro, mgr = _detect_distro()
        _install_nmap_bin(distro, mgr)
        _pip_install("python-nmap", "mac-vendor-lookup")
        _update_mac_vendors_with_timeout(timeout_sec=15)
        _mark_installed()

# ══════════════════════════════════════════════════════════════════════════════
#  IMPORTS (após instalação garantida)
# ══════════════════════════════════════════════════════════════════════════════
import re, socket, threading, time, webbrowser, ipaddress
from concurrent.futures import ThreadPoolExecutor, as_completed
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import queue
import urllib.request
import urllib.error

try:
    import nmap as nmap_lib
    HAS_NMAP = True
except ImportError:
    HAS_NMAP = False

try:
    from mac_vendor_lookup import MacLookup
    _mac_lookup = MacLookup()
    HAS_MAC = True
except Exception:
    HAS_MAC = False

# ══════════════════════════════════════════════════════════════════════════════
#  CONSTANTES / PALETA
# ══════════════════════════════════════════════════════════════════════════════
APP_TITLE   = "Advanced IP Scanner"
APP_AUTHOR  = "ricinus"

BG_DARK     = "#1a1d23"
BG_MID      = "#22262f"
BG_LIGHT    = "#2b303c"
BG_ROW_ODD  = "#1e2229"
BG_ROW_EVEN = "#22262f"
BG_HOVER    = "#2e3a4e"
BG_SELECT   = "#1e4a7a"

FG_PRIMARY  = "#e8eaf0"
FG_DIM      = "#7a8299"
FG_ACCENT   = "#4fc3f7"
FG_GREEN    = "#66bb6a"
FG_YELLOW   = "#ffca28"
FG_RED      = "#ef5350"
FG_ORANGE   = "#ffa726"
FG_PURPLE   = "#ab47bc"
FG_TEAL     = "#26c6da"

BORDER      = "#3a3f4d"
BTN_BG      = "#2e3a4e"
BTN_HOVER   = "#3d5166"
BTN_ACTIVE  = "#4fc3f7"

FONT_MONO   = ("Courier New", 9)
FONT_BODY   = ("Segoe UI", 9) if sys.platform == "win32" else ("Ubuntu", 9)
FONT_BOLD   = ("Segoe UI", 9, "bold") if sys.platform == "win32" else ("Ubuntu", 9, "bold")
FONT_TITLE  = ("Segoe UI", 11, "bold") if sys.platform == "win32" else ("Ubuntu", 11, "bold")
FONT_ICON   = ("Segoe UI Emoji", 11) if sys.platform == "win32" else ("Noto Color Emoji", 10)

COMMON_PORTS = {
    21: ("FTP",       "🗂️",  "ftp"),
    22: ("SSH",       "🔐",  "ssh"),
    23: ("Telnet",    "📟",  "telnet"),
    25: ("SMTP",      "📧",  ""),
    53: ("DNS",       "🔍",  ""),
    80: ("HTTP",      "🌐",  "http"),
    110:("POP3",      "📧",  ""),
    139:("NetBIOS",   "🪟",  ""),
    143:("IMAP",      "📧",  ""),
    443:("HTTPS",     "🔒",  "https"),
    445:("SMB",       "🪟",  ""),
    515:("Printer",   "🖨️", ""),
    631:("IPP",       "🖨️", "http"),
    3389:("RDP",      "🖥️", ""),
    5900:("VNC",      "🖥️", "vnc"),
    8080:("HTTP-Alt", "🌐",  "http"),
    8443:("HTTPS-Alt","🔒",  "https"),
    9100:("Printer",  "🖨️", ""),
}

DEVICE_HINTS = [
    (r"(?i)(tp.?link|tplink)",                          "🔀", "Switch/Roteador TP-Link",  FG_TEAL),
    (r"(?i)(cisco)",                                     "🔀", "Cisco",                    FG_TEAL),
    (r"(?i)(mikrotik)",                                  "🔀", "MikroTik Router",          FG_TEAL),
    (r"(?i)(ubiquiti|unifi)",                            "📡", "Ubiquiti",                 FG_TEAL),
    (r"(?i)(asus.?rt|asus.*router)",                     "🔀", "ASUS Router",              FG_TEAL),
    (r"(?i)(dlink|d-link)",                              "🔀", "D-Link",                   FG_TEAL),
    (r"(?i)(netgear)",                                   "🔀", "Netgear",                  FG_TEAL),
    (r"(?i)(hewlett.?packard|hp.*laser|hp.*jet|hp.*print)","🖨️","HP Printer",             FG_ORANGE),
    (r"(?i)(epson)",                                     "🖨️","Epson Printer",            FG_ORANGE),
    (r"(?i)(canon)",                                     "🖨️","Canon Printer",            FG_ORANGE),
    (r"(?i)(brother)",                                   "🖨️","Brother Printer",          FG_ORANGE),
    (r"(?i)(iphone|ipad)",                               "📱", "Dispositivo Apple",        FG_PRIMARY),
    (r"(?i)(android|samsung.*mobile)",                   "📱", "Smartphone Android",       FG_GREEN),
    (r"(?i)(xbox)",                                      "🎮", "Xbox",                     FG_GREEN),
    (r"(?i)(playstation|ps[345])",                       "🎮", "PlayStation",              FG_ACCENT),
    (r"(?i)(chromecast|nest.*hub)",                      "📺", "Chromecast/Google TV",     FG_ACCENT),
    (r"(?i)(smart.?tv|samsung.*tv|lg.*tv|sony.*tv)",     "📺", "Smart TV",                 FG_ACCENT),
    (r"(?i)(hikvision|dahua|axis.*cam)",                 "📷", "Câmera IP",               FG_YELLOW),
    (r"(?i)(raspberrypi|raspberry)",                     "🍓", "Raspberry Pi",             FG_RED),
    (r"(?i)(synology|qnap|nas)",                         "🗄️", "NAS",                     FG_PURPLE),
    (r"(?i)(vmware|esxi|proxmox)",                       "🖥️","Servidor VM",              FG_PURPLE),
    (r"(?i)(ubuntu|debian|centos|fedora|linux.*server)", "🐧", "Servidor Linux",           FG_YELLOW),
    (r"(?i)(windows.?server|win.*srv)",                  "🖥️","Windows Server",           FG_ACCENT),
    (r"(?i)(desktop|pc|workstation)",                    "💻", "PC/Desktop",               FG_PRIMARY),
    (r"(?i)(laptop|notebook)",                           "💻", "Notebook",                 FG_PRIMARY),
    (r"(?i)(dell)",                                      "🖥️","Dell",                     FG_PRIMARY),
    (r"(?i)(lenovo)",                                    "💻", "Lenovo",                   FG_PRIMARY),
    (r"(?i)(apple|macbook|imac)",                        "🍎", "Apple Mac",               FG_PRIMARY),
]

# ══════════════════════════════════════════════════════════════════════════════
#  VERIFICAÇÃO DE ATUALIZAÇÕES (GitHub)
# ══════════════════════════════════════════════════════════════════════════════
def check_for_updates(timeout=8):
    """
    Verifica a última release no GitHub.
    Retorna (has_update: bool, latest_version: str, url: str, error: str|None)
    """
    try:
        req = urllib.request.Request(
            GITHUB_API_URL,
            headers={"User-Agent": f"AdvancedIPScanner/{APP_VERSION}",
                     "Accept": "application/vnd.github.v3+json"}
        )
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            data = json.loads(resp.read().decode())
        latest = data.get("tag_name", "").lstrip("v")
        url    = data.get("html_url", GITHUB_REPO_URL)
        if not latest:
            # sem releases ainda — aponta direto para o repositório
            return False, APP_VERSION, GITHUB_REPO_URL, "Nenhuma release encontrada no repositório."
        has_update = _version_gt(latest, APP_VERSION)
        return has_update, latest, url, None
    except urllib.error.URLError as e:
        return False, APP_VERSION, GITHUB_REPO_URL, f"Sem conexão: {e.reason}"
    except Exception as e:
        return False, APP_VERSION, GITHUB_REPO_URL, str(e)

def _version_gt(v1, v2):
    """Retorna True se v1 > v2 (comparação numérica de partes separadas por ponto)."""
    try:
        def parts(v):
            return [int(x) for x in re.split(r"[.\-]", v) if x.isdigit()]
        return parts(v1) > parts(v2)
    except Exception:
        return v1 != v2

# ══════════════════════════════════════════════════════════════════════════════
#  MODELO DE DADOS
# ══════════════════════════════════════════════════════════════════════════════
class DeviceInfo:
    def __init__(self, ip):
        self.ip       = ip
        self.hostname = ""
        self.mac      = ""
        self.vendor   = ""
        self.os       = ""
        self.services = []
        self.icon     = "❓"
        self.dtype    = "Desconhecido"
        self.color    = FG_DIM
        self.alive    = False
        self.latency  = 0.0

# ══════════════════════════════════════════════════════════════════════════════
#  FUNÇÕES DE SCAN
# ══════════════════════════════════════════════════════════════════════════════
def get_local_network():
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        parts = ip.split(".")
        return f"{parts[0]}.{parts[1]}.{parts[2]}.0/24"
    except Exception:
        return "192.168.1.0/24"

def ping_host(ip, timeout=1.0):
    t0 = time.time()
    try:
        r = subprocess.run(
            ["ping", "-c", "1", "-W", str(int(timeout * 1000)), ip],
            stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
            timeout=timeout + 0.5
        )
        latency = (time.time() - t0) * 1000
        return r.returncode == 0, round(latency, 1)
    except Exception:
        return False, 0.0

def resolve_hostname(ip):
    try:
        socket.setdefaulttimeout(1)
        return socket.gethostbyaddr(ip)[0]
    except Exception:
        return ""

def get_netbios_name(ip):
    try:
        out = subprocess.check_output(
            ["nmblookup", "-A", ip], timeout=3, stderr=subprocess.DEVNULL
        ).decode()
        for line in out.splitlines():
            if "<00>" in line and "GROUP" not in line:
                name = line.strip().split()[0]
                if name and name != ip:
                    return name.upper()
    except Exception:
        pass
    return ""

def get_mac_arp(ip):
    try:
        out = subprocess.check_output(["arp", "-n", ip], stderr=subprocess.DEVNULL).decode()
        m = re.search(r"([0-9a-f]{2}[:\-]){5}[0-9a-f]{2}", out, re.IGNORECASE)
        if m:
            return m.group(0).upper()
    except Exception:
        pass
    return ""

def get_vendor(mac):
    if not mac or not HAS_MAC:
        return ""
    try:
        return _mac_lookup.lookup(mac)
    except Exception:
        return ""

def scan_ports_simple(ip, timeout=0.4):
    open_svcs = []
    def try_port(port):
        try:
            with socket.create_connection((ip, port), timeout=timeout):
                return port
        except Exception:
            return None
    with ThreadPoolExecutor(max_workers=20) as ex:
        results = ex.map(try_port, list(COMMON_PORTS.keys()))
    for port in results:
        if port:
            name, icon, scheme = COMMON_PORTS[port]
            open_svcs.append((port, f"{icon} {name}", scheme))
    open_svcs.sort(key=lambda x: x[0])
    return open_svcs

def nmap_scan_full(ip):
    result = {"hostname": "", "os": "", "services": []}
    if not HAS_NMAP:
        return result
    try:
        nm = nmap_lib.PortScanner()
        is_root = os.geteuid() == 0
        args = "-sV --script=nbstat,banner -T4"
        if is_root:
            args += " -O --osscan-guess"
        nm.scan(hosts=ip, arguments=args, timeout=60)
        if ip not in nm.all_hosts():
            return result
        h = nm[ip]
        if h.hostname():
            result["hostname"] = h.hostname()
        if is_root and "osmatch" in h and h["osmatch"]:
            result["os"] = h["osmatch"][0].get("name", "")
        if "hostscript" in h:
            for sc in h["hostscript"]:
                if "nbstat" in sc.get("id",""):
                    m = re.search(r"NetBIOS name: (\S+)", sc.get("output",""))
                    if m:
                        result["hostname"] = result["hostname"] or m.group(1)
        for proto in h.all_protocols():
            for port in h[proto]:
                svc = h[proto][port]
                if svc["state"] != "open":
                    continue
                sname      = svc.get("name","")
                product    = svc.get("product","")
                version    = svc.get("version","")
                extrainfo  = svc.get("extrainfo","")
                parts = [x for x in [product, version, extrainfo] if x]
                label = " ".join(parts) or sname
                icon, scheme = "🔌", ""
                if port in COMMON_PORTS:
                    _, icon, scheme = COMMON_PORTS[port]
                result["services"].append((port, f"{icon} {label}", scheme))
        result["services"].sort(key=lambda x: x[0])
    except Exception:
        pass
    return result

def guess_device(hostname, vendor, services):
    ports = [p for p, _, _ in services]
    combined = f"{hostname} {vendor}"
    for pattern, icon, label, color in DEVICE_HINTS:
        if re.search(pattern, combined):
            return icon, label, color
    if 3389 in ports: return "🖥️", "Windows (RDP)",     FG_ACCENT
    if 445  in ports: return "🖥️", "Windows/Samba",     FG_ACCENT
    if 22   in ports and 80 not in ports:
        return "🐧", "Linux (SSH)",      FG_YELLOW
    if 9100 in ports or 515 in ports or 631 in ports:
        return "🖨️", "Impressora",       FG_ORANGE
    if 5900 in ports: return "🖥️", "Desktop (VNC)",     FG_PRIMARY
    if 80   in ports or 443 in ports:
        return "🌐", "Servidor Web",     FG_GREEN
    return "❓", "Desconhecido",         FG_DIM

def scan_device(ip, advanced=False, stop_event=None):
    if stop_event and stop_event.is_set():
        return None
    dev = DeviceInfo(ip)
    alive, latency = ping_host(ip)
    if not alive:
        return None
    dev.alive   = True
    dev.latency = latency
    dev.hostname = resolve_hostname(ip)
    dev.mac    = get_mac_arp(ip)
    dev.vendor = get_vendor(dev.mac)
    nb = get_netbios_name(ip)
    dev.hostname = dev.hostname or nb
    if stop_event and stop_event.is_set():
        return None
    if advanced and HAS_NMAP:
        nm = nmap_scan_full(ip)
        dev.hostname = dev.hostname or nm["hostname"]
        dev.os       = nm["os"]
        if nm["services"]:
            dev.services = nm["services"]
        else:
            dev.services = scan_ports_simple(ip)
    else:
        dev.services = scan_ports_simple(ip)
    dev.icon, dev.dtype, dev.color = guess_device(dev.hostname, dev.vendor, dev.services)
    return dev

# ══════════════════════════════════════════════════════════════════════════════
#  TEXTOS DE AJUDA
# ══════════════════════════════════════════════════════════════════════════════
HELP_TEXT = """
╔══════════════════════════════════════════════════════════════════╗
║          ADVANCED IP SCANNER — Guia Completo de Uso             ║
╚══════════════════════════════════════════════════════════════════╝

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
 O QUE É ESTE PROGRAMA?
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

 Advanced IP Scanner é uma ferramenta de descoberta de rede que
 localiza todos os dispositivos ativos em uma rede local (LAN).
 Ele identifica computadores, roteadores, impressoras, câmeras,
 smart TVs e outros dispositivos conectados, exibindo informações
 como IP, nome, fabricante, MAC address e serviços abertos.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
 COMO FAZER UM SCAN BÁSICO
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

 1. Verifique o campo "Rede" na barra superior.
    • A rede local é detectada automaticamente (ex: 192.168.1.0/24)
    • Você pode digitar manualmente outra rede no campo
    • O formato CIDR é obrigatório: ex. 10.0.0.0/24

 2. Defina o intervalo de IPs (De / Até):
    • "De: 1  Até: 254" escaneia todos os 254 hosts da sub-rede
    • Reduza o intervalo para scans mais rápidos (ex: De 1 Até 50)

 3. Clique em "▶ Verificar" ou acesse Scan → Iniciar scan.

 4. Aguarde. Os dispositivos vão aparecendo em tempo real.

 Dica: Aumente "Threads" para scans mais rápidos em redes grandes.
        Reduza se a rede for instável ou houver muitos timeouts.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
 SCAN AVANÇADO (nmap)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

 Marque "Scan avançado (nmap)" para obter informações extras:

   ✔ Detecção do sistema operacional (requer sudo)
   ✔ Versões dos serviços (Apache 2.4, OpenSSH 8.9, etc.)
   ✔ Nome NetBIOS via script nmap
   ✔ Detecção de serviços não-padrão em portas aleatórias

 ⚠ ATENÇÃO: O scan avançado é MUITO mais lento.
   Recomendado apenas para redes pequenas ou hosts específicos.

 Para detecção de SO, execute com privilégios root:
   sudo python3 ip_scanner_gui.py

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
 VERIFICAÇÃO DE ATUALIZAÇÕES
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

 Acesse Ajuda → Verificar atualizações para checar se há uma
 versão mais nova disponível no GitHub. Se houver, um link
 para download será exibido.

 O programa também verifica automaticamente ao iniciar
 (em background, sem bloquear a interface).

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
 INTERAGINDO COM OS RESULTADOS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

 • Clique simples em um dispositivo → painel de detalhes é exibido
   no rodapé com todas as informações coletadas.

 • Clique duplo em um dispositivo → abre o serviço web (HTTP/HTTPS)
   no navegador padrão, se disponível.

 • Clique duplo em um serviço (↳ filho) → abre a URL desse serviço
   específico no navegador.

 • Botão direito em qualquer item → menu de contexto com opções:
     - Copiar IP / MAC / hostname para área de transferência
     - Abrir serviços diretamente (HTTP, SSH, FTP, VNC…)
     - Re-escanear apenas aquele host
     - Ver detalhes completos

 • Clique nos cabeçalhos das colunas → ordena a tabela por aquela
   coluna (IP, Nome, Fabricante, etc.)

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
 EXPORTAR RESULTADOS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

 Acesse Arquivo → Exportar resultados (CSV)…
 O arquivo CSV pode ser aberto no LibreOffice Calc, Excel, etc.
 Contém: IP, Hostname, MAC, Fabricante, Tipo, SO, Ping, Serviços.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
 DICAS E SOLUÇÃO DE PROBLEMAS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

 • MAC address em branco → o dispositivo não estava na tabela ARP.
   Faça ping manual antes: ping -c1 <ip> e execute o scanner novamente.

 • Nenhum dispositivo encontrado → verifique se a rede no campo
   "Rede" está correta. Use `ip route` no terminal para confirmar.

 • Scan avançado travando → aumente o timeout ou reduza threads.

 • Para reinstalar as dependências Python do zero, delete o arquivo:
   ~/.ipscan_deps_installed   e reinicie o programa.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
 USO ÉTICO E LEGAL
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

 ⚠ Este programa deve ser usado APENAS em redes que você tem
   autorização para analisar (sua própria rede, redes de clientes
   com contrato, ambientes de laboratório/teste).
"""

# ══════════════════════════════════════════════════════════════════════════════
#  GUI PRINCIPAL
# ══════════════════════════════════════════════════════════════════════════════
class AdvancedIPScannerApp(tk.Tk):

    def __init__(self):
        super().__init__()
        self.title(f"{APP_TITLE} {APP_VERSION} — by {APP_AUTHOR}")
        self.geometry("1080x680")
        self.minsize(800, 500)
        self.configure(bg=BG_DARK)

        self._scan_thread  = None
        self._stop_event   = threading.Event()
        self._result_queue = queue.Queue()
        self._devices      = {}
        self._tree_ids     = {}
        self._scan_running = False
        self._total_hosts  = 0
        self._scanned      = 0

        self._setup_style()
        self._build_ui()
        self._detect_network()
        self.after(100, self._poll_results)

        # verifica atualizações em background ao iniciar
        threading.Thread(target=self._auto_check_updates, daemon=True).start()

    # ── verificação de atualizações ──────────────────────────────────────────
    def _auto_check_updates(self):
        """Roda em background; notifica apenas se houver update disponível."""
        has_update, latest, url, error = check_for_updates(timeout=8)
        if has_update:
            self.after(0, lambda: self._notify_update(latest, url))

    def _notify_update(self, latest, url):
        """Banner discreto na status bar + diálogo opcional."""
        self._status_var.set(
            f"🔔  Nova versão disponível: v{latest}  —  Ajuda → Verificar atualizações"
        )
        # muda cor da status bar para chamar atenção
        for w in self.winfo_children():
            pass  # já atualizado via StringVar

    def _check_updates_manual(self):
        """Chamado pelo menu — abre janela com resultado."""
        win = tk.Toplevel(self)
        win.title("Verificar atualizações")
        win.geometry("500x260")
        win.resizable(False, False)
        win.configure(bg=BG_DARK)
        win.grab_set()

        tk.Label(win, text="🔍  Verificando atualizações…",
                 bg=BG_DARK, fg=FG_ACCENT, font=FONT_TITLE).pack(pady=(24,8))

        msg_var = tk.StringVar(value="Conectando ao GitHub…")
        msg_lbl = tk.Label(win, textvariable=msg_var, bg=BG_DARK,
                           fg=FG_DIM, font=FONT_BODY, wraplength=440, justify="center")
        msg_lbl.pack(pady=6, padx=20)

        ver_lbl = tk.Label(win, text="", bg=BG_DARK, fg=FG_GREEN,
                           font=FONT_BOLD)
        ver_lbl.pack(pady=4)

        link_var = tk.StringVar(value="")
        link_lbl = tk.Label(win, textvariable=link_var, bg=BG_DARK,
                            fg=FG_ACCENT, font=FONT_BODY, cursor="hand2",
                            underline=True)
        link_lbl.pack(pady=2)
        link_lbl.bind("<Button-1>", lambda e, u=GITHUB_REPO_URL: webbrowser.open(u))

        btn_frame = tk.Frame(win, bg=BG_DARK)
        btn_frame.pack(pady=16)
        ttk.Button(btn_frame, text="Fechar", style="Small.TButton",
                   command=win.destroy).pack()

        def _do_check():
            has_update, latest, url, error = check_for_updates(timeout=10)
            def _update_ui():
                if error and not has_update:
                    msg_var.set(f"Não foi possível verificar: {error}")
                    msg_lbl.config(fg=FG_RED)
                    ver_lbl.config(text=f"Versão atual: v{APP_VERSION}", fg=FG_DIM)
                elif has_update:
                    msg_var.set(
                        f"Nova versão disponível! Sua versão: v{APP_VERSION}"
                    )
                    msg_lbl.config(fg=FG_YELLOW)
                    ver_lbl.config(text=f"Versão disponível: v{latest} ✨", fg=FG_GREEN)
                    link_var.set(f"🌐  Baixar em: {url}")
                    link_lbl.bind("<Button-1>", lambda e, u=url: webbrowser.open(u))
                else:
                    msg_var.set("Você já está usando a versão mais recente!")
                    msg_lbl.config(fg=FG_GREEN)
                    ver_lbl.config(text=f"Versão atual: v{APP_VERSION} ✔", fg=FG_GREEN)
                    link_var.set(f"Repositório: {GITHUB_REPO_URL}")
                    link_lbl.bind("<Button-1>",
                                  lambda e: webbrowser.open(GITHUB_REPO_URL))
            win.after(0, _update_ui)

        threading.Thread(target=_do_check, daemon=True).start()

    # ── setup estilo ─────────────────────────────────────────────────────────
    def _setup_style(self):
        style = ttk.Style(self)
        style.theme_use("clam")
        style.configure(".",
            background=BG_DARK, foreground=FG_PRIMARY,
            fieldbackground=BG_MID, insertcolor=FG_PRIMARY,
            troughcolor=BG_MID, bordercolor=BORDER,
            darkcolor=BG_MID, lightcolor=BG_LIGHT,
            selectbackground=BG_SELECT, selectforeground=FG_PRIMARY,
            font=FONT_BODY)
        style.configure("TFrame",  background=BG_DARK)
        style.configure("TLabel",  background=BG_DARK, foreground=FG_PRIMARY)
        style.configure("TEntry",  fieldbackground=BG_LIGHT, foreground=FG_PRIMARY,
                         insertcolor=FG_PRIMARY, borderwidth=1, relief="flat")
        style.configure("Primary.TButton",
            background=BTN_BG, foreground=FG_ACCENT,
            borderwidth=1, relief="flat", padding=(12,5), font=FONT_BOLD)
        style.map("Primary.TButton",
            background=[("active", BTN_HOVER), ("pressed", BG_SELECT)],
            foreground=[("active", FG_PRIMARY)])
        style.configure("Danger.TButton",
            background="#3d1f1f", foreground=FG_RED,
            borderwidth=1, relief="flat", padding=(12,5), font=FONT_BOLD)
        style.map("Danger.TButton",
            background=[("active", "#5a2a2a")],
            foreground=[("active", "#ff8080")])
        style.configure("Small.TButton",
            background=BG_LIGHT, foreground=FG_DIM,
            borderwidth=0, relief="flat", padding=(6,3), font=FONT_BODY)
        style.map("Small.TButton",
            background=[("active", BTN_HOVER)],
            foreground=[("active", FG_PRIMARY)])
        style.configure("Treeview",
            background=BG_MID, foreground=FG_PRIMARY,
            fieldbackground=BG_MID, borderwidth=0,
            rowheight=22, font=FONT_BODY)
        style.configure("Treeview.Heading",
            background=BG_LIGHT, foreground=FG_ACCENT,
            borderwidth=0, relief="flat", font=FONT_BOLD, padding=(8,5))
        style.map("Treeview",
            background=[("selected", BG_SELECT)],
            foreground=[("selected", FG_PRIMARY)])
        style.map("Treeview.Heading",
            background=[("active", BTN_HOVER)])
        style.configure("Horizontal.TProgressbar",
            troughcolor=BG_LIGHT, background=FG_ACCENT,
            borderwidth=0, thickness=4)
        style.configure("TCombobox",
            fieldbackground=BG_LIGHT, background=BG_LIGHT,
            foreground=FG_PRIMARY, arrowcolor=FG_ACCENT, borderwidth=1)
        style.map("TCombobox",
            fieldbackground=[("readonly", BG_LIGHT)],
            selectbackground=[("readonly", BG_SELECT)])
        style.configure("TCheckbutton",
            background=BG_DARK, foreground=FG_PRIMARY,
            indicatorcolor=BG_LIGHT, indicatordiameter=13)
        style.map("TCheckbutton",
            indicatorcolor=[("selected", FG_ACCENT)])

    def _build_ui(self):
        self._build_menubar()
        self._build_toolbar()
        self._build_main()
        self._build_statusbar()

    def _build_menubar(self):
        mb = tk.Menu(self, bg=BG_MID, fg=FG_PRIMARY,
                     activebackground=BG_SELECT, activeforeground=FG_PRIMARY,
                     borderwidth=0, relief="flat")
        self.config(menu=mb)

        m_file = tk.Menu(mb, tearoff=0, bg=BG_MID, fg=FG_PRIMARY,
                         activebackground=BG_SELECT, activeforeground=FG_PRIMARY)
        m_file.add_command(label="Exportar resultados (CSV)…", command=self._export_csv)
        m_file.add_separator()
        m_file.add_command(label="Sair", command=self.destroy)

        m_scan = tk.Menu(mb, tearoff=0, bg=BG_MID, fg=FG_PRIMARY,
                         activebackground=BG_SELECT, activeforeground=FG_PRIMARY)
        m_scan.add_command(label="Iniciar scan",  command=self._start_scan)
        m_scan.add_command(label="Parar scan",    command=self._stop_scan)
        m_scan.add_separator()
        m_scan.add_command(label="Limpar tabela", command=self._clear_results)

        m_help = tk.Menu(mb, tearoff=0, bg=BG_MID, fg=FG_PRIMARY,
                         activebackground=BG_SELECT, activeforeground=FG_PRIMARY)
        m_help.add_command(label="📖  Como usar (Guia completo)", command=self._show_help)
        m_help.add_separator()
        m_help.add_command(label="🔔  Verificar atualizações",    command=self._check_updates_manual)
        m_help.add_command(label="🌐  Ver repositório no GitHub", command=lambda: webbrowser.open(GITHUB_REPO_URL))
        m_help.add_separator()
        m_help.add_command(label="🔁  Reinstalar dependências",   command=self._reinstall_deps)
        m_help.add_separator()
        m_help.add_command(label="⭐  Sobre / Créditos",          command=self._show_about)

        mb.add_cascade(label="Arquivo",  menu=m_file)
        mb.add_cascade(label="Scan",     menu=m_scan)
        mb.add_cascade(label="Ajuda",    menu=m_help)

    def _build_toolbar(self):
        bar = tk.Frame(self, bg=BG_MID, height=52, bd=0)
        bar.pack(fill="x", side="top")
        bar.pack_propagate(False)

        tk.Label(bar, text="Rede:", bg=BG_MID, fg=FG_DIM,
                 font=FONT_BODY).pack(side="left", padx=(14,4), pady=12)

        self._net_var = tk.StringVar()
        net_cb = ttk.Combobox(bar, textvariable=self._net_var,
                              width=22, font=FONT_MONO, style="TCombobox")
        net_cb["values"] = self._saved_networks()
        net_cb.pack(side="left", padx=(0,10), pady=12, ipady=3)
        self._net_cb = net_cb

        tk.Label(bar, text="De:", bg=BG_MID, fg=FG_DIM, font=FONT_BODY)\
            .pack(side="left", padx=(0,4))
        self._ip_start = ttk.Entry(bar, width=5, font=FONT_MONO)
        self._ip_start.insert(0, "1")
        self._ip_start.pack(side="left", padx=(0,4), ipady=3)

        tk.Label(bar, text="Até:", bg=BG_MID, fg=FG_DIM, font=FONT_BODY)\
            .pack(side="left", padx=(0,4))
        self._ip_end = ttk.Entry(bar, width=5, font=FONT_MONO)
        self._ip_end.insert(0, "254")
        self._ip_end.pack(side="left", padx=(0,12), ipady=3)

        self._adv_var = tk.BooleanVar(value=False)
        adv_chk = ttk.Checkbutton(bar, text="Scan avançado (nmap)",
                                   variable=self._adv_var, style="TCheckbutton")
        adv_chk.pack(side="left", padx=(0,14))
        if not HAS_NMAP:
            adv_chk.config(state="disabled")
            tk.Label(bar, text="[nmap não instalado]",
                     bg=BG_MID, fg=FG_RED, font=FONT_BODY).pack(side="left")

        self._btn_scan = ttk.Button(bar, text="▶  Verificar",
                                    style="Primary.TButton", command=self._start_scan)
        self._btn_scan.pack(side="left", padx=(0,6))

        self._btn_stop = ttk.Button(bar, text="⏹  Parar",
                                    style="Danger.TButton", command=self._stop_scan,
                                    state="disabled")
        self._btn_stop.pack(side="left", padx=(0,6))

        ttk.Button(bar, text="🗑 Limpar", style="Small.TButton",
                   command=self._clear_results).pack(side="left")

        tk.Label(bar, text="Threads:", bg=BG_MID, fg=FG_DIM, font=FONT_BODY)\
            .pack(side="right", padx=(0,4))
        self._threads_var = tk.IntVar(value=64)
        th_spin = tk.Spinbox(bar, from_=8, to=256, increment=8,
                             textvariable=self._threads_var, width=4,
                             bg=BG_LIGHT, fg=FG_PRIMARY, buttonbackground=BG_LIGHT,
                             relief="flat", font=FONT_MONO)
        th_spin.pack(side="right", padx=(0,14))

    def _build_main(self):
        paned = tk.PanedWindow(self, orient="vertical", bg=BORDER,
                               sashwidth=4, sashrelief="flat")
        paned.pack(fill="both", expand=True)

        top_frame = tk.Frame(paned, bg=BG_DARK)
        paned.add(top_frame, minsize=250)

        cols = ("ip", "name", "mac", "vendor", "dtype", "os", "ping")
        self._tree = ttk.Treeview(top_frame, columns=cols,
                                  show="tree headings", selectmode="extended")
        self._tree.tag_configure("row_odd",  background=BG_ROW_ODD)
        self._tree.tag_configure("row_even", background=BG_ROW_EVEN)
        self._tree.tag_configure("service",  background=BG_DARK, foreground=FG_DIM)
        self._tree.tag_configure("alive",    foreground=FG_GREEN)
        self._tree.tag_configure("dim",      foreground=FG_DIM)

        self._tree.heading("#0", text="", anchor="w")
        self._tree.column("#0", width=22, minwidth=22, stretch=False)

        headers = [
            ("ip",     "Endereço IP",   130, "w"),
            ("name",   "Nome",          200, "w"),
            ("mac",    "Endereço MAC",  145, "w"),
            ("vendor", "Fabricante",    170, "w"),
            ("dtype",  "Tipo",          190, "w"),
            ("os",     "Sistema Op.",   160, "w"),
            ("ping",   "Ping (ms)",      80, "e"),
        ]
        for cid, text, w, anch in headers:
            self._tree.heading(cid, text=text, command=lambda c=cid: self._sort_col(c))
            self._tree.column(cid, width=w, minwidth=60, anchor=anch)

        vsb = ttk.Scrollbar(top_frame, orient="vertical",   command=self._tree.yview)
        hsb = ttk.Scrollbar(top_frame, orient="horizontal", command=self._tree.xview)
        self._tree.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)
        vsb.pack(side="right",  fill="y")
        hsb.pack(side="bottom", fill="x")
        self._tree.pack(fill="both", expand=True)

        self._tree.bind("<Double-Button-1>", self._on_double_click)
        self._tree.bind("<Button-3>",        self._on_right_click)
        self._tree.bind("<<TreeviewSelect>>",self._on_select)

        bot_frame = tk.Frame(paned, bg=BG_MID)
        paned.add(bot_frame, minsize=100)

        hdr = tk.Frame(bot_frame, bg=BG_LIGHT, height=26)
        hdr.pack(fill="x")
        hdr.pack_propagate(False)
        tk.Label(hdr, text="  Detalhes do dispositivo",
                 bg=BG_LIGHT, fg=FG_ACCENT, font=FONT_BOLD).pack(side="left", pady=3)

        self._detail_text = tk.Text(bot_frame, bg=BG_MID, fg=FG_PRIMARY,
                                    relief="flat", bd=0, font=FONT_MONO,
                                    wrap="none", state="disabled",
                                    insertbackground=FG_PRIMARY,
                                    selectbackground=BG_SELECT, height=6)
        dsb = ttk.Scrollbar(bot_frame, orient="vertical", command=self._detail_text.yview)
        self._detail_text.configure(yscrollcommand=dsb.set)
        dsb.pack(side="right", fill="y")
        self._detail_text.pack(fill="both", expand=True, padx=6, pady=4)

        self._detail_text.tag_config("h",    foreground=FG_ACCENT, font=FONT_BOLD)
        self._detail_text.tag_config("key",  foreground=FG_DIM)
        self._detail_text.tag_config("val",  foreground=FG_PRIMARY)
        self._detail_text.tag_config("svc",  foreground=FG_GREEN)
        self._detail_text.tag_config("link", foreground=FG_ACCENT, underline=True)

    def _build_statusbar(self):
        bar = tk.Frame(self, bg=BG_LIGHT, height=26)
        bar.pack(fill="x", side="bottom")
        bar.pack_propagate(False)

        tk.Label(bar, text=f"  {APP_TITLE} {APP_VERSION} by {APP_AUTHOR}",
                 bg=BG_LIGHT, fg="#3a4055", font=FONT_BODY,
                 anchor="w").pack(side="left")

        self._count_var = tk.StringVar(value="")
        tk.Label(bar, textvariable=self._count_var,
                 bg=BG_LIGHT, fg=FG_GREEN, font=FONT_BOLD,
                 anchor="e").pack(side="right", padx=10)

        self._progress = ttk.Progressbar(bar, style="Horizontal.TProgressbar",
                                         mode="determinate", length=220)
        self._progress.pack(side="right", padx=(0,12), pady=5)

        self._status_var = tk.StringVar(value="Pronto. Use Ajuda → Como usar para instruções.")
        tk.Label(bar, textvariable=self._status_var,
                 bg=BG_LIGHT, fg=FG_DIM, font=FONT_BODY,
                 anchor="w").pack(side="left", padx=10)

    # ── rede ──────────────────────────────────────────────────────────────────
    def _saved_networks(self):
        nets = []
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(("8.8.8.8", 80))
            ip = s.getsockname()[0]
            s.close()
            parts = ip.split(".")
            nets.append(f"{parts[0]}.{parts[1]}.{parts[2]}.0/24")
        except Exception:
            pass
        for n in ["192.168.0.0/24","192.168.1.0/24","10.0.0.0/24","172.16.0.0/24"]:
            if n not in nets:
                nets.append(n)
        return nets

    def _detect_network(self):
        nets = self._saved_networks()
        if nets:
            self._net_var.set(nets[0])
            self._net_cb["values"] = nets

    # ── scan ──────────────────────────────────────────────────────────────────
    def _get_hosts(self):
        raw = self._net_var.get().strip()
        try:
            net = ipaddress.ip_network(raw, strict=False)
        except ValueError:
            messagebox.showerror("Erro", f"Rede inválida: {raw}\nExemplo: 192.168.1.0/24")
            return []
        all_hosts = list(net.hosts())
        try:
            s = int(self._ip_start.get())
            e = int(self._ip_end.get())
            s = max(1, min(s, 254))
            e = max(s, min(e, 254))
            all_hosts = [h for h in all_hosts
                         if s <= int(str(h).split(".")[-1]) <= e]
        except Exception:
            pass
        return all_hosts

    def _start_scan(self):
        if self._scan_running:
            return
        hosts = self._get_hosts()
        if not hosts:
            return
        self._clear_results()
        self._scan_running   = True
        self._total_hosts    = len(hosts)
        self._scanned        = 0
        self._stop_event.clear()
        self._btn_scan.config(state="disabled")
        self._btn_stop.config(state="normal")
        self._progress["maximum"] = self._total_hosts
        self._progress["value"]   = 0
        self._status_var.set(f"Escaneando {self._total_hosts} hosts…")
        self._count_var.set("")

        adv     = self._adv_var.get()
        threads = self._threads_var.get()
        stop    = self._stop_event

        def runner():
            q = self._result_queue
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
                pct = int(self._scanned / self._total_hosts * 100) if self._total_hosts else 0
                self._status_var.set(f"Escaneando… {self._scanned}/{self._total_hosts} ({pct}%)")
                if dev:
                    self._add_device(dev)
                    self._count_var.set(f"{len(self._devices)} dispositivos encontrados")
            elif kind == "done":
                self._scan_running = False
                self._btn_scan.config(state="normal")
                self._btn_stop.config(state="disabled")
                self._status_var.set(
                    f"Scan concluído — {len(self._devices)} dispositivos em {self._total_hosts} hosts verificados."
                )
                self._progress["value"] = self._total_hosts
        self.after(100, self._poll_results)

    # ── treeview ──────────────────────────────────────────────────────────────
    _row_idx = 0

    def _add_device(self, dev: DeviceInfo):
        self._devices[dev.ip] = dev
        tag  = "row_odd" if self._row_idx % 2 else "row_even"
        self._row_idx += 1
        iid = self._tree.insert(
            "", "end", text="",
            values=(dev.ip, dev.hostname or "—", dev.mac or "—",
                    dev.vendor or "—", f"{dev.icon} {dev.dtype}",
                    dev.os or "—",
                    f"{dev.latency:.0f}" if dev.latency else "—"),
            tags=(tag, "alive"), open=False
        )
        self._tree_ids[dev.ip] = iid
        for port, label, scheme in dev.services:
            url = self._make_url(dev.ip, port, scheme)
            self._tree.insert(iid, "end", text="",
                values=(f"  ↳ :{port}", label, "", "", "", "", ""),
                tags=("service",), iid=f"{iid}_svc_{port}")
            self._tree.set(f"{iid}_svc_{port}", "mac", url or "")
        self._tree.see(iid)

    def _make_url(self, ip, port, scheme):
        if not scheme: return ""
        if scheme in ("http","https","ftp"): return f"{scheme}://{ip}:{port}"
        if scheme == "ssh":  return f"ssh://{ip}:{port}"
        if scheme == "vnc":  return f"vnc://{ip}:{port}"
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

    def _sort_col(self, col):
        data = [(self._tree.set(k, col), k) for k in self._tree.get_children("")]
        try:
            data.sort(key=lambda x: ipaddress.ip_address(x[0]))
        except Exception:
            data.sort()
        for i, (_, k) in enumerate(data):
            self._tree.move(k, "", i)

    # ── eventos ───────────────────────────────────────────────────────────────
    def _on_select(self, _event):
        sel = self._tree.selection()
        if not sel: return
        iid = sel[0]
        parent = self._tree.parent(iid)
        if parent: iid = parent
        vals = self._tree.item(iid, "values")
        if not vals: return
        dev = self._devices.get(vals[0].strip())
        if dev: self._show_detail(dev)

    def _on_double_click(self, event):
        iid = self._tree.identify_row(event.y)
        if not iid: return
        parent = self._tree.parent(iid)
        if parent:
            url = self._tree.set(iid, "mac")
            if url: webbrowser.open(url)
            return
        vals = self._tree.item(iid, "values")
        ip   = vals[0].strip()
        dev  = self._devices.get(ip)
        if dev:
            for port, label, scheme in dev.services:
                if scheme in ("http","https"):
                    webbrowser.open(f"{scheme}://{ip}:{port}"); return

    def _on_right_click(self, event):
        iid = self._tree.identify_row(event.y)
        if not iid: return
        self._tree.selection_set(iid)
        parent = self._tree.parent(iid)
        if parent:
            ip = self._tree.item(parent, "values")[0].strip()
        else:
            ip = self._tree.item(iid, "values")[0].strip()
        dev  = self._devices.get(ip)
        menu = tk.Menu(self, tearoff=0, bg=BG_MID, fg=FG_PRIMARY,
                       activebackground=BG_SELECT, activeforeground=FG_PRIMARY)
        menu.add_command(label=f"📋  Copiar IP  ({ip})", command=lambda: self._copy(ip))
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
                        label=f"🌐  Abrir {label.split(' ',1)[-1]}  ({url})",
                        command=lambda u=url: webbrowser.open(u))
        menu.add_separator()
        menu.add_command(label="🔁  Re-escanear este host",
                         command=lambda: self._rescan_host(ip))
        menu.add_command(label="📄  Ver detalhes completos",
                         command=lambda: self._show_detail(dev) if dev else None)
        menu.post(event.x_root, event.y_root)

    # ── painel de detalhes ────────────────────────────────────────────────────
    def _show_detail(self, dev: DeviceInfo):
        t = self._detail_text
        t.config(state="normal")
        t.delete("1.0", "end")
        def w(text, tag=None):
            t.insert("end", text, tag) if tag else t.insert("end", text)
        w(f"  {dev.icon}  {dev.dtype}  —  {dev.ip}\n", "h")
        w("\n")
        w("  Hostname:   ", "key"); w(f"{dev.hostname or '—'}\n", "val")
        w("  MAC:        ", "key"); w(f"{dev.mac or '—'}\n", "val")
        w("  Fabricante: ", "key"); w(f"{dev.vendor or '—'}\n", "val")
        w("  Sistema Op: ", "key"); w(f"{dev.os or '—'}\n", "val")
        w("  Latência:   ", "key"); w(f"{dev.latency:.1f} ms\n", "val")
        if dev.services:
            w("\n  Serviços abertos:\n", "key")
            for port, label, scheme in dev.services:
                url = self._make_url(dev.ip, port, scheme)
                w(f"    • {label:<28}", "svc")
                if url:
                    tag_name = f"link_{port}"
                    t.insert("end", url, ("link", tag_name))
                    t.tag_bind(tag_name, "<Button-1>", lambda e, u=url: webbrowser.open(u))
                    t.tag_bind(tag_name, "<Enter>", lambda e: t.config(cursor="hand2"))
                    t.tag_bind(tag_name, "<Leave>", lambda e: t.config(cursor=""))
                w("\n")
        t.config(state="disabled")

    # ── ações ─────────────────────────────────────────────────────────────────
    def _copy(self, text):
        self.clipboard_clear()
        self.clipboard_append(text)
        self._status_var.set(f"Copiado: {text}")

    def _rescan_host(self, ip):
        adv = self._adv_var.get()
        self._status_var.set(f"Re-escaneando {ip}…")
        def worker():
            dev = scan_device(ip, advanced=adv)
            if dev:
                self.after(0, lambda: self._update_device(dev))
                self.after(0, lambda: self._status_var.set(f"Re-scan concluído: {ip}"))
            else:
                self.after(0, lambda: self._status_var.set(f"{ip} não respondeu."))
        threading.Thread(target=worker, daemon=True).start()

    def _update_device(self, dev):
        old_iid = self._tree_ids.get(dev.ip)
        if old_iid:
            try: self._tree.delete(old_iid)
            except Exception: pass
        self._devices.pop(dev.ip, None)
        self._tree_ids.pop(dev.ip, None)
        self._add_device(dev)

    def _export_csv(self):
        path = filedialog.asksaveasfilename(
            defaultextension=".csv",
            filetypes=[("CSV", "*.csv"), ("Todos", "*.*")],
            title="Exportar resultados"
        )
        if not path: return
        import csv
        with open(path, "w", newline="", encoding="utf-8") as f:
            w = csv.writer(f)
            w.writerow(["IP","Hostname","MAC","Fabricante","Tipo","SO","Ping(ms)","Serviços"])
            for dev in self._devices.values():
                svcs = ", ".join(f"{p}={l}" for p,l,_ in dev.services)
                w.writerow([dev.ip, dev.hostname, dev.mac, dev.vendor,
                            dev.dtype, dev.os, dev.latency, svcs])
        self._status_var.set(f"Exportado: {path}")

    # ── janelas de ajuda / sobre ──────────────────────────────────────────────
    def _show_text_window(self, title, content, width=72, height=36):
        win = tk.Toplevel(self)
        win.title(title)
        win.configure(bg=BG_DARK)
        win.geometry(f"{width*9}x{height*20}")
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
                      selectbackground=BG_SELECT, insertbackground=FG_PRIMARY)
        vsb = ttk.Scrollbar(frame, orient="vertical",   command=txt.yview)
        hsb = ttk.Scrollbar(frame, orient="horizontal", command=txt.xview)
        txt.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)
        vsb.pack(side="right",  fill="y")
        hsb.pack(side="bottom", fill="x")
        txt.pack(fill="both", expand=True)

        txt.insert("1.0", content)
        txt.config(state="disabled")

        ttk.Button(win, text="Fechar", style="Small.TButton",
                   command=win.destroy).pack(pady=(0,10))

    def _show_help(self):
        self._show_text_window("📖  Como usar — Advanced IP Scanner", HELP_TEXT,
                               width=74, height=38)

    def _show_about(self):
        about = f"""
╔══════════════════════════════════════════════════════════════╗
║              Advanced IP Scanner {APP_VERSION} — Linux                ║
╚══════════════════════════════════════════════════════════════╝

  Clone do Advanced IP Scanner para Linux, desenvolvido
  com foco em usabilidade, performance e estética.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  👤  DESENVOLVIDO POR
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

       ricinus

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  🛠️  TECNOLOGIAS UTILIZADAS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

   • Python 3.x          — linguagem principal
   • Tkinter / ttk        — interface gráfica nativa
   • python-nmap          — wrapper para o nmap
   • nmap                 — scanner de portas e SO
   • mac-vendor-lookup    — resolução de fabricantes por MAC
   • ThreadPoolExecutor   — scan paralelo de alta performance
   • urllib               — verificação de atualizações (GitHub)

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  ℹ️  VERSÃO
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

   Versão:     {APP_VERSION}
   Python:     {sys.version.split()[0]}
   nmap:       {"disponível ✔" if HAS_NMAP else "não instalado ✘"}
   mac-lookup: {"disponível ✔" if HAS_MAC else "não instalado ✘"}
   Repositório: {GITHUB_REPO_URL}
"""
        self._show_text_window(f"⭐  Sobre / Créditos — {APP_TITLE}", about,
                               width=66, height=32)

    def _reinstall_deps(self):
        if messagebox.askyesno(
            "Reinstalar dependências",
            "Isso irá apagar o marcador de instalação e reiniciar\n"
            "o processo de instalação de dependências.\n\nDeseja continuar?"
        ):
            _MARKER.unlink(missing_ok=True)
            messagebox.showinfo(
                "Reinstalação agendada",
                "Feche e reabra o programa para reinstalar as dependências."
            )

# ══════════════════════════════════════════════════════════════════════════════
#  ENTRY
# ══════════════════════════════════════════════════════════════════════════════
if __name__ == "__main__":
    app = AdvancedIPScannerApp()
    app.mainloop()
