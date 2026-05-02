"""
core/constants.py
Todas as constantes visuais, fontes, paleta de cores e dados de portas/dispositivos.
Para personalizar a aparência, edite apenas este arquivo.
"""

import sys

# ── versão e repositório ──────────────────────────────────────────────────────
APP_VERSION    = "2.2"
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
COMMON_PORTS: dict[int, tuple[str, str, str]] = {
    # ── Infraestrutura / Rede ─────────────────────────────────────────────────
    21:    ("FTP",             "🗂️",  "ftp"),
    22:    ("SSH",             "🔐",  "ssh"),
    23:    ("Telnet",          "📟",  "telnet"),
    25:    ("SMTP",            "📧",  ""),
    53:    ("DNS",             "🔍",  ""),
    67:    ("DHCP Server",     "🌐",  ""),
    68:    ("DHCP Client",     "💻",  ""),
    69:    ("TFTP",            "🗂️",  ""),
    80:    ("HTTP",            "🌐",  "http"),
    88:    ("Kerberos",        "🔑",  ""),
    110:   ("POP3",            "📧",  ""),
    113:   ("Ident",           "🆔",  ""),
    123:   ("NTP",             "🕐",  ""),
    139:   ("NetBIOS",         "🪟",  ""),
    143:   ("IMAP",            "📧",  ""),
    161:   ("SNMP",            "📊",  ""),
    162:   ("SNMP Trap",       "🪤",  ""),
    179:   ("BGP",             "🔀",  ""),
    389:   ("LDAP",            "📇",  ""),
    443:   ("HTTPS",           "🔒",  "https"),
    445:   ("SMB",             "🪟",  ""),
    465:   ("SMTPS",           "🔒",  ""),
    514:   ("Syslog",          "📜",  ""),
    515:   ("Printer (LPD)",   "🖨️",  ""),
    520:   ("RIP",             "🔀",  ""),
    587:   ("SMTP Submission", "📧",  ""),
    631:   ("IPP",             "🖨️",  "http"),
    636:   ("LDAPS",           "🔒",  ""),
    873:   ("Rsync",           "🔄",  ""),
    993:   ("IMAPS",           "🔒",  ""),
    995:   ("POP3S",           "🔒",  ""),
    1080:  ("SOCKS Proxy",     "🧦",  ""),
    1194:  ("OpenVPN",         "🔒",  ""),
    1433:  ("MSSQL",           "🗄️",  ""),
    1521:  ("Oracle DB",       "🗄️",  ""),
    2049:  ("NFS",             "📂",  ""),
    3306:  ("MySQL/MariaDB",   "🗄️",  ""),
    3389:  ("RDP",             "🖥️",  ""),
    5432:  ("PostgreSQL",      "🗄️",  ""),
    5900:  ("VNC",             "🖥️",  "vnc"),
    6379:  ("Redis",           "⚡",  ""),
    8080:  ("HTTP-Alt",        "🌐",  "http"),
    8443:  ("HTTPS-Alt",       "🔒",  "https"),
    8888:  ("HTTP-Alt 2",      "🌐",  "http"),
    9090:  ("Prometheus/UI",   "📊",  "http"),
    9100:  ("Printer (JetDirect)", "🖨️", ""),
    9443:  ("HTTPS-Alt 3",     "🔒",  "https"),
    10000: ("Webmin",          "🖥️",  "https"),
    11211: ("Memcached",       "⚡",  ""),
    27017: ("MongoDB",         "🗄️",  ""),
    27018: ("MongoDB Shard",   "🗄️",  ""),
    28017: ("MongoDB Web UI",  "🗄️",  "http"),
    
    # ── IoT, Automação e Smart Home ───────────────────────────────────────────
    1883:  ("MQTT",            "📡",  ""),
    5353:  ("mDNS",            "🔍",  ""),
    8123:  ("Home Assistant",  "🏠",  "http"),
    8883:  ("MQTT/SSL",        "🔒",  ""),
    
    # ─– Desenvolvimento e DevOps ──────────────────────────────────────────────
    2375:  ("Docker API",      "🐳",  "http"),
    2376:  ("Docker API SSL",  "🐳",  "https"),
    3000:  ("Dev Server (Node/React)", "💻", "http"),
    4000:  ("Dev Server (Gulp/Edge)", "💻", "http"),
    5000:  ("Dev Server (Flask/Python)", "🐍", "http"),
    8000:  ("Dev Server (Django)", "🐍", "http"),
    8081:  ("Dev Server (Alt)", "💻",  "http"),
    8443:  ("Dev Server SSL",  "💻",  "https"),
    9000:  ("Portainer",       "🐳",  "http"),
    9200:  ("Elasticsearch",   "🔍",  "http"),
    15672: ("RabbitMQ Mgmt",   "🐰",  "http"),
    
    # ── Streaming, Jogos e Mídia ──────────────────────────────────────────────
    25565: ("Minecraft",       "⛏️",  ""),
    27015: ("Steam/Source",    "🎮",  ""),
    32400: ("Plex",            "🎬",  "http"),
    7878:  ("Radarr",          "🎬",  "http"),
    8989:  ("Sonarr",          "🎬",  "http"),
    9696:  ("Prowlarr",        "🔍",  "http"),
    
    # ── Painéis e Sistemas Específicos ────────────────────────────────────────
    2082:  ("cPanel",          "🖥️",  "http"),
    2083:  ("cPanel SSL",      "🔒",  "https"),
    2086:  ("WHM",             "🖥️",  "http"),
    2087:  ("WHM SSL",         "🔒",  "https"),
    2222:  ("DirectAdmin",     "🖥️",  "http"),
    8090:  ("Jupyter Notebook","📓",  "http"),
}

# ── hints de dispositivo por hostname/vendor ──────────────────────────────────
# Formato: (regex, ícone, label, cor)
DEVICE_HINTS = [
    # ── Roteadores, Switches e Firewalls ──────────────────────────────────────
    (r"(?i)(tp.?link|tplink)",                         "🔀", "Switch/Roteador TP-Link",  FG_TEAL),
    (r"(?i)(cisco)",                                   "🔀", "Cisco",                    FG_TEAL),
    (r"(?i)(mikrotik)",                                "🔀", "MikroTik Router",          FG_TEAL),
    (r"(?i)(ubiquiti|unifi)",                          "📡", "Ubiquiti",                 FG_TEAL),
    (r"(?i)(asus.?rt|asus.*router)",                   "🔀", "ASUS Router",              FG_TEAL),
    (r"(?i)(dlink|d-link)",                            "🔀", "D-Link",                   FG_TEAL),
    (r"(?i)(netgear)",                                 "🔀", "Netgear",                  FG_TEAL),
    (r"(?i)(juniper)",                                 "🔀", "Juniper",                  FG_TEAL),
    (r"(?i)(fortinet|fortigate)",                      "🔥", "Fortinet Firewall",        FG_RED),
    (r"(?i)(meraki)",                                  "🔀", "Cisco Meraki",             FG_TEAL),
    (r"(?i)(draytek)",                                 "🔀", "DrayTek",                  FG_TEAL),
    (r"(?i)(intelbras)",                               "🔀", "Intelbras",                FG_TEAL),
    (r"(?i)(hawking)",                                 "🔀", "Hawking",                  FG_TEAL),
    (r"(?i)(tenda)",                                   "🔀", "Tenda",                    FG_TEAL),
    (r"(?i)(multilaser)",                              "🔀", "Multilaser",               FG_TEAL),

    # ── Impressoras e Multifuncionais ─────────────────────────────────────────
    (r"(?i)(hewlett.?packard|hp.*laser|hp.*jet|hp.*print)", "🖨️", "HP Printer",          FG_ORANGE),
    (r"(?i)(epson)",                                   "🖨️", "Epson Printer",           FG_ORANGE),
    (r"(?i)(canon)",                                   "🖨️", "Canon Printer",           FG_ORANGE),
    (r"(?i)(brother)",                                 "🖨️", "Brother Printer",         FG_ORANGE),
    (r"(?i)(xerox)",                                   "🖨️", "Xerox Printer",           FG_ORANGE),
    (r"(?i)(ricoh)",                                   "🖨️", "Ricoh Printer",           FG_ORANGE),
    (r"(?i)(kyocera)",                                 "🖨️", "Kyocera Printer",         FG_ORANGE),
    (r"(?i)(lexmark)",                                 "🖨️", "Lexmark Printer",         FG_ORANGE),
    (r"(?i)(zebra)",                                   "🖨️", "Zebra (Etiquetas)",        FG_ORANGE),

    # ── Dispositivos Móveis ───────────────────────────────────────────────────
    (r"(?i)(iphone|ipad)",                             "📱", "Dispositivo Apple",        FG_PRIMARY),
    (r"(?i)(android|samsung.*mobile)",                 "📱", "Smartphone Android",       FG_GREEN),
    (r"(?i)(xiaomi|redmi|poco)",                       "📱", "Smartphone Xiaomi",        FG_GREEN),
    (r"(?i)(huawei|honor)",                            "📱", "Smartphone Huawei",        FG_GREEN),
    (r"(?i)(motorola|moto ?[g,x,z])",                  "📱", "Smartphone Motorola",      FG_GREEN),

    # ── Smart TV e Streaming ──────────────────────────────────────────────────
    (r"(?i)(xbox)",                                    "🎮", "Xbox",                     FG_GREEN),
    (r"(?i)(playstation|ps[345])",                     "🎮", "PlayStation",              FG_ACCENT),
    (r"(?i)(nintendo|switch)",                         "🎮", "Nintendo",                 FG_RED),
    (r"(?i)(chromecast|nest.*hub)",                    "📺", "Chromecast/Google TV",     FG_ACCENT),
    (r"(?i)(smart.?tv|samsung.*tv|lg.*tv|sony.*tv)",   "📺", "Smart TV",                 FG_ACCENT),
    (r"(?i)(apple.?tv)",                               "📺", "Apple TV",                 FG_PRIMARY),
    (r"(?i)(fire.?stick|firetv)",                      "📺", "Amazon Fire TV",           FG_ACCENT),
    (r"(?i)(roku)",                                    "📺", "Roku",                     FG_ACCENT),

    # ── Câmeras e Segurança ───────────────────────────────────────────────────
    (r"(?i)(hikvision)",                               "📷", "Câmera Hikvision",         FG_YELLOW),
    (r"(?i)(dahua)",                                   "📷", "Câmera Dahua",             FG_YELLOW),
    (r"(?i)(intelbras.*cam|intelbras.*video)",         "📷", "Câmera Intelbras",         FG_YELLOW),
    (r"(?i)(axis.*cam|axis.*com)",                     "📷", "Câmera Axis",              FG_YELLOW),
    (r"(?i)(reolink)",                                 "📷", "Câmera Reolink",           FG_YELLOW),
    (r"(?i)(ring)",                                    "🔔", "Ring (Campainha/Câmera)",   FG_YELLOW),

    # ── IoT e Automação ───────────────────────────────────────────────────────
    (r"(?i)(philips.?hue|signify)",                    "💡", "Philips Hue",              FG_YELLOW),
    (r"(?i)(sonos)",                                   "🔊", "Sonos (Speaker)",          FG_GREEN),
    (r"(?i)(amazon.*echo|alexa)",                      "🔊", "Amazon Echo",              FG_ACCENT),
    (r"(?i)(google.*nest|nest.*therm)",                "🏠", "Google Nest",              FG_GREEN),
    (r"(?i)(tuya|smart.?life|smart.?things)",          "📡", "Dispositivo IoT Genérico",  FG_TEAL),
    (r"(?i)(shelly)",                                  "💡", "Shelly (IoT)",             FG_YELLOW),
    (r"(?i)(yeelight)",                                "💡", "Yeelight",                 FG_YELLOW),
    (r"(?i)(esp[0-9]{2}|esp32|esp8266)",               "🔌", "Dispositivo ESP",          FG_GREEN),
    (r"(?i)(arduino)",                                 "🔌", "Arduino",                  FG_TEAL),

    # ── Sistemas Operacionais e Servidores ────────────────────────────────────
    (r"(?i)(raspberrypi|raspberry|raspbian)",          "🍓", "Raspberry Pi",             FG_RED),
    (r"(?i)(synology|diskstation)",                    "🗄️", "Synology NAS",             FG_PURPLE),
    (r"(?i)(qnap)",                                    "🗄️", "QNAP NAS",                 FG_PURPLE),
    (r"(?i)(truenas|freenas)",                         "🗄️", "TrueNAS",                  FG_PURPLE),
    (r"(?i)(unraid)",                                  "🗄️", "Unraid Server",            FG_PURPLE),
    (r"(?i)(vmware|esxi|vsphere)",                     "🖥️", "Servidor VMware",          FG_PURPLE),
    (r"(?i)(proxmox)",                                 "🖥️", "Proxmox VE",              FG_PURPLE),
    (r"(?i)(docker|container)",                        "🐳", "Docker Host",              FG_ACCENT),
    (r"(?i)(ubuntu|debian|centos|fedora|linux.*server)","🐧", "Servidor Linux",           FG_YELLOW),
    (r"(?i)(red.?hat|rhel)",                           "🎩", "Red Hat Enterprise",       FG_RED),
    (r"(?i)(arch.?linux|manjaro)",                     "🐧", "Arch/Manjaro Linux",       FG_YELLOW),
    (r"(?i)(freebsd|pfsense|opnsense)",                "👹", "FreeBSD / Firewall",       FG_RED),
    (r"(?i)(windows.?server|win.*srv)",                "🖥️", "Windows Server",           FG_ACCENT),
    (r"(?i)(macOS|mac.?mini|mac.?pro|macbook|imac)",   "🍎", "Apple Mac",               FG_PRIMARY),

    # ── Fabricantes de PC / Notebook ──────────────────────────────────────────
    (r"(?i)(dell)",                                    "🖥️", "Dell",                    FG_PRIMARY),
    (r"(?i)(lenovo)",                                  "💻", "Lenovo",                   FG_PRIMARY),
    (r"(?i)(acer)",                                    "💻", "Acer",                     FG_PRIMARY),
    (r"(?i)(asus.*pc|asus.*book|rog)",                 "💻", "ASUS PC",                  FG_PRIMARY),
    (r"(?i)(msi)",                                     "💻", "MSI",                      FG_PRIMARY),
    (r"(?i)(samsung.*book|samsung.*pc)",               "💻", "Samsung PC",               FG_PRIMARY),

    # ── Genéricos ─────────────────────────────────────────────────────────────
    (r"(?i)(desktop|pc|workstation)",                  "💻", "PC/Desktop",               FG_PRIMARY),
    (r"(?i)(laptop|notebook)",                         "💻", "Notebook",                 FG_PRIMARY),
]

# ── hints por banner HTTP ─────────────────────────────────────────────────────
HTTP_BANNER_HINTS = [
    # ── Roteadores e Firewalls (Painéis Web) ───────────────────────────────────
    (r"(?i)(tp.?link|tplink)",                         "🔀", "Switch/Roteador TP-Link",   FG_TEAL),
    (r"(?i)(mikrotik|routeros)",                       "🔀", "MikroTik Router",           FG_TEAL),
    (r"(?i)(ubiquiti|unifi|airmax)",                   "📡", "Ubiquiti",                  FG_TEAL),
    (r"(?i)(cisco)",                                   "🔀", "Cisco",                     FG_TEAL),
    (r"(?i)(asus.*router|asuswrt|merlin)",             "🔀", "ASUS Router",               FG_TEAL),
    (r"(?i)(d.?link)",                                 "🔀", "D-Link",                    FG_TEAL),
    (r"(?i)(netgear)",                                 "🔀", "Netgear",                   FG_TEAL),
    (r"(?i)(intelbras)",                               "🔀", "Intelbras",                 FG_TEAL),
    (r"(?i)(openwrt|luci)",                            "🔀", "Roteador OpenWRT",          FG_TEAL),
    (r"(?i)(dd.?wrt)",                                 "🔀", "Roteador DD-WRT",           FG_TEAL),
    (r"(?i)(pfsense)",                                 "🔥", "Firewall pfSense",          FG_RED),
    (r"(?i)(opnsense)",                                "🔥", "Firewall OPNsense",         FG_RED),
    (r"(?i)(fortinet|fortigate)",                      "🔥", "Fortinet Firewall",         FG_RED),

    # ── NAS e Armazenamento ────────────────────────────────────────────────────
    (r"(?i)(synology|diskstation)",                    "🗄️", "Synology NAS",             FG_PURPLE),
    (r"(?i)(qnap)",                                    "🗄️", "QNAP NAS",                 FG_PURPLE),
    (r"(?i)(truenas|freenas)",                         "🗄️", "TrueNAS",                  FG_PURPLE),

    # ── Impressoras ───────────────────────────────────────────────────────────
    (r"(?i)(hp.*printer|jetdirect|laserjet|officejet)", "🖨️", "HP Printer",              FG_ORANGE),
    (r"(?i)(epson.*print|epsonnet)",                   "🖨️", "Epson Printer",            FG_ORANGE),
    (r"(?i)(canon.*print|pixma|imagerunner)",          "🖨️", "Canon Printer",            FG_ORANGE),
    (r"(?i)(brother.*print|brother.*mfc)",             "🖨️", "Brother Printer",          FG_ORANGE),
    (r"(?i)(xerox)",                                   "🖨️", "Xerox Printer",            FG_ORANGE),

    # ── Câmeras IP ─────────────────────────────────────────────────────────────
    (r"(?i)(hikvision|dahua|axis|reolink|intelbras.*video)", "📷", "Câmera IP",          FG_YELLOW),

    # ── Virtualização e Containers ─────────────────────────────────────────────
    (r"(?i)(proxmox)",                                 "🖥️", "Proxmox VE",              FG_PURPLE),
    (r"(?i)(vmware|vsphere|esxi)",                     "🖥️", "VMware ESXi",             FG_PURPLE),
    (r"(?i)(portainer)",                               "🐳", "Portainer (Docker)",       FG_ACCENT),

    # ── Smart Home e IoT ───────────────────────────────────────────────────────
    (r"(?i)(home.?assistant)",                         "🏠", "Home Assistant",           FG_GREEN),
    (r"(?i)(shelly)",                                  "💡", "Shelly IoT",               FG_YELLOW),
    (r"(?i)(tasmota)",                                 "🔌", "Tasmota (ESP)",            FG_GREEN),

    # ── Servidores Web ─────────────────────────────────────────────────────────
    (r"(?i)(nginx)",                                   "🌐", "Servidor Nginx",           FG_GREEN),
    (r"(?i)(apache)",                                  "🌐", "Servidor Apache",          FG_GREEN),
    (r"(?i)(litepeed|litespeed)",                      "🌐", "Servidor LiteSpeed",       FG_GREEN),
    (r"(?i)(caddy)",                                   "🌐", "Servidor Caddy",           FG_GREEN),
    (r"(?i)(microsoft-iis|iis)",                       "🪟", "Servidor IIS",             FG_ACCENT),
    (r"(?i)(tomcat|jakarta)",                          "☕", "Servidor Tomcat",          FG_ORANGE),
    (r"(?i)(gunicorn)",                                "🐍", "Gunicorn (Python)",        FG_GREEN),
    (r"(?i)(node.?js|express)",                        "🟢", "Node.js / Express",        FG_GREEN),

    # ── CMS e Sistemas Web Conhecidos ─────────────────────────────────────────
    (r"(?i)(wordpress|wp-)",                           "📝", "WordPress",                FG_ACCENT),
    (r"(?i)(joomla)",                                  "📝", "Joomla",                   FG_ORANGE),
    (r"(?i)(nextcloud)",                               "☁️", "Nextcloud",                FG_ACCENT),
    (r"(?i)(owncloud)",                                "☁️", "ownCloud",                 FG_ACCENT),
    (r"(?i)(phpmyadmin)",                              "🗄️", "phpMyAdmin",               FG_ORANGE),
    (r"(?i)(cpanel)",                                  "🖥️", "cPanel",                   FG_ORANGE),
    (r"(?i)(plesk)",                                   "🖥️", "Plesk",                    FG_ACCENT),
    (r"(?i)(webmin)",                                  "🖥️", "Webmin",                   FG_TEAL),

    # ── Streaming e Media Servers ─────────────────────────────────────────────
    (r"(?i)(plex)",                                    "🎬", "Plex Media Server",         FG_ACCENT),
    (r"(?i)(jellyfin)",                                "🎬", "Jellyfin",                  FG_GREEN),
    (r"(?i)(emby)",                                    "🎬", "Emby",                     FG_GREEN),
    
    # ── Sistemas Operacionais Identificados via HTTP ───────────────────────────
    (r"(?i)(raspberry|raspbian)",                      "🍓", "Raspberry Pi",             FG_RED),
]
