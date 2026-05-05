"""
core/constants.py
Todas as constantes visuais, fontes, paleta de cores e dados de portas/dispositivos.
Para personalizar a aparência, edite apenas este arquivo.
"""

import sys

# ── versão e repositório ──────────────────────────────────────────────────────
APP_VERSION    = "2.5"
APP_TITLE      = "Advanced IP Scanner"
APP_AUTHOR     = "ricinus"
GITHUB_REPO    = "ricinuss/ipscanner"
GITHUB_API_URL = f"https://api.github.com/repos/{GITHUB_REPO}/releases/latest"
GITHUB_REPO_URL = f"https://github.com/{GITHUB_REPO}/tree/main"

# ── paleta de cores ───────────────────────────────────────────────────────────
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

# ── fontes ────────────────────────────────────────────────────────────────────
_WIN = sys.platform == "win32"
FONT_MONO  = ("Courier New", 9)
FONT_BODY  = ("Segoe UI", 9)  if _WIN else ("Ubuntu", 9)
FONT_BOLD  = ("Segoe UI", 9, "bold") if _WIN else ("Ubuntu", 9, "bold")
FONT_TITLE = ("Segoe UI", 11, "bold") if _WIN else ("Ubuntu", 11, "bold")

# ── portas conhecidas ─────────────────────────────────────────────────────────
# Formato: porta -> (nome, ícone, scheme_url)
# Para adicionar uma porta, basta inserir aqui.
COMMON_PORTS: dict[int, tuple[str, str, str]] = {
    21:   ("FTP",       "🗂️",  "ftp"),
    22:   ("SSH",       "🔐",  "ssh"),
    23:   ("Telnet",    "📟",  "telnet"),
    25:   ("SMTP",      "📧",  ""),
    53:   ("DNS",       "🔍",  ""),
    80:   ("HTTP",      "🌐",  "http"),
    110:  ("POP3",      "📧",  ""),
    139:  ("NetBIOS",   "🪟",  ""),
    143:  ("IMAP",      "📧",  ""),
    161:  ("SNMP",      "📊",  ""),
    443:  ("HTTPS",     "🔒",  "https"),
    445:  ("SMB",       "🪟",  ""),
    515:  ("Printer",   "🖨️", ""),
    631:  ("IPP",       "🖨️", "http"),
    3389: ("RDP",       "🖥️", ""),
    5900: ("VNC",       "🖥️", "vnc"),
    8080: ("HTTP-Alt",  "🌐",  "http"),
    8443: ("HTTPS-Alt", "🔒",  "https"),
    9100: ("Printer",   "🖨️", ""),
}

# ── hints de dispositivo por hostname/vendor ──────────────────────────────────
# Formato: (regex, ícone, label, cor)
DEVICE_HINTS = [
    (r"(?i)(tp.?link|tplink)",                         "🔀", "Switch/Roteador TP-Link",  FG_TEAL),
    (r"(?i)(cisco)",                                    "🔀", "Cisco",                    FG_TEAL),
    (r"(?i)(mikrotik)",                                 "🔀", "MikroTik Router",          FG_TEAL),
    (r"(?i)(ubiquiti|unifi)",                           "📡", "Ubiquiti",                 FG_TEAL),
    (r"(?i)(asus.?rt|asus.*router)",                    "🔀", "ASUS Router",              FG_TEAL),
    (r"(?i)(dlink|d-link)",                             "🔀", "D-Link",                   FG_TEAL),
    (r"(?i)(netgear)",                                  "🔀", "Netgear",                  FG_TEAL),
    (r"(?i)(hewlett.?packard|hp.*laser|hp.*jet|hp.*print)", "🖨️", "HP Printer",          FG_ORANGE),
    (r"(?i)(epson)",                                    "🖨️", "Epson Printer",           FG_ORANGE),
    (r"(?i)(canon)",                                    "🖨️", "Canon Printer",           FG_ORANGE),
    (r"(?i)(brother)",                                  "🖨️", "Brother Printer",         FG_ORANGE),
    (r"(?i)(iphone|ipad)",                              "📱", "Dispositivo Apple",        FG_PRIMARY),
    (r"(?i)(android|samsung.*mobile)",                  "📱", "Smartphone Android",       FG_GREEN),
    (r"(?i)(xbox)",                                     "🎮", "Xbox",                     FG_GREEN),
    (r"(?i)(playstation|ps[345])",                      "🎮", "PlayStation",              FG_ACCENT),
    (r"(?i)(chromecast|nest.*hub)",                     "📺", "Chromecast/Google TV",     FG_ACCENT),
    (r"(?i)(smart.?tv|samsung.*tv|lg.*tv|sony.*tv)",    "📺", "Smart TV",                 FG_ACCENT),
    (r"(?i)(hikvision|dahua|axis.*cam)",                "📷", "Câmera IP",               FG_YELLOW),
    (r"(?i)(raspberrypi|raspberry)",                    "🍓", "Raspberry Pi",             FG_RED),
    (r"(?i)(synology|qnap|nas)",                        "🗄️", "NAS",                     FG_PURPLE),
    (r"(?i)(vmware|esxi|proxmox)",                      "🖥️", "Servidor VM",             FG_PURPLE),
    (r"(?i)(ubuntu|debian|centos|fedora|linux.*server)","🐧", "Servidor Linux",           FG_YELLOW),
    (r"(?i)(windows.?server|win.*srv)",                 "🖥️", "Windows Server",          FG_ACCENT),
    (r"(?i)(desktop|pc|workstation)",                   "💻", "PC/Desktop",               FG_PRIMARY),
    (r"(?i)(laptop|notebook)",                          "💻", "Notebook",                 FG_PRIMARY),
    (r"(?i)(dell)",                                     "🖥️", "Dell",                    FG_PRIMARY),
    (r"(?i)(lenovo)",                                   "💻", "Lenovo",                   FG_PRIMARY),
    (r"(?i)(apple|macbook|imac)",                       "🍎", "Apple Mac",               FG_PRIMARY),
]

# ── hints por banner HTTP ─────────────────────────────────────────────────────
HTTP_BANNER_HINTS = [
    # ── TP-Link: identificadores únicos dos switches Easy Smart ────────────────
    # Server header exato retornado por switches TL-SG / TL-SF
    (r"(?i)\bweb switch\b",                                "🔀", "Switch TP-Link (Easy Smart)", FG_TEAL),
    # Tema CSS / asset exclusivo da interface web TP-Link Easy Smart
    (r"(?i)(steel_gray|jquery\.cookie\.min)",              "🔀", "Switch TP-Link (Easy Smart)", FG_TEAL),
    # ── TP-Link: nome explícito OU modelos de switch/roteador ─────────────────
    (r"(?i)(tp.?link|tplink)",                             "🔀", "Switch/Roteador TP-Link",   FG_TEAL),
    # Modelos de switch gerenciado TP-Link (TL-SG, TL-SF, TL-SL)
    (r"(?i)(TL-S[GLF][0-9])",                              "🔀", "Switch TP-Link",            FG_TEAL),
    # Switch Easy Smart / Smart Switch (interface web padrão TP-Link)
    (r"(?i)(easy.?smart|smart.?switch)",                   "🔀", "Switch TP-Link (Smart)",    FG_TEAL),
    # Interface Omada (TP-Link SDN / Access Points e switches ent. empresa)
    (r"(?i)(omada)",                                       "📡", "TP-Link Omada",             FG_TEAL),

    # ── Outros fabricantes de rede ────────────────────────────────────────────
    (r"(?i)(mikrotik|routeros)",                          "🔀", "MikroTik Router",           FG_TEAL),
    (r"(?i)(ubiquiti|unifi|airmax|edgeos)",               "📡", "Ubiquiti",                  FG_TEAL),
    (r"(?i)(cisco)",                                      "🔀", "Cisco",                     FG_TEAL),
    (r"(?i)(asus.*router|asuswrt|merlin)",                "🔀", "ASUS Router",               FG_TEAL),
    (r"(?i)(d.?link)",                                    "🔀", "D-Link",                    FG_TEAL),
    (r"(?i)(netgear)",                                    "🔀", "Netgear",                   FG_TEAL),
    (r"(?i)(openwrt|luci)",                               "🔀", "Roteador OpenWRT",          FG_TEAL),
    (r"(?i)(dd.?wrt)",                                    "🔀", "Roteador DD-WRT",           FG_TEAL),
    (r"(?i)(pfsense|opnsense)",                           "🔥", "Firewall pfSense/OPNsense", FG_RED),
    # ── NAS ───────────────────────────────────────────────────────────────────
    (r"(?i)(synology|diskstation)",                       "🗄️", "Synology NAS",             FG_PURPLE),
    (r"(?i)(qnap)",                                       "🗄️", "QNAP NAS",                 FG_PURPLE),
    # ── Câmeras ───────────────────────────────────────────────────────────────
    (r"(?i)(hikvision|dahua|axis)",                       "📷", "Câmera IP",               FG_YELLOW),
    # ── Impressoras ───────────────────────────────────────────────────────────
    (r"(?i)(hp.*printer|jetdirect|laserjet|officejet)",   "🖨️", "HP Printer",     FG_ORANGE),
    (r"(?i)(epson.*print|epsonnet)",                      "🖨️", "Epson Printer",           FG_ORANGE),
    (r"(?i)(canon.*print|pixma|imagerunner)",              "🖨️", "Canon Printer",           FG_ORANGE),
    (r"(?i)(brother.*print|brother.*mfc)",                "🖨️", "Brother Printer",         FG_ORANGE),
    # ── Servidores de virtualização ────────────────────────────────────────────
    (r"(?i)(proxmox)",                                    "🖥️", "Proxmox VE",             FG_PURPLE),
    (r"(?i)(vmware|vsphere|esxi)",                        "🖥️", "VMware ESXi",            FG_PURPLE),
    (r"(?i)(raspberry|raspbian)",                         "🍓", "Raspberry Pi",             FG_RED),
    # ── Servidores web ────────────────────────────────────────────────────────
    (r"(?i)(nginx)",                                      "🌐", "Servidor Nginx",           FG_GREEN),
    (r"(?i)(apache)",                                     "🌐", "Servidor Apache",          FG_GREEN),
]
