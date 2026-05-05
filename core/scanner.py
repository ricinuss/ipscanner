"""
core/scanner.py
Toda a lógica de scan: ping, resolução de hostname, ARP, portas, nmap, fingerprint.
Para adicionar um novo método de detecção, adicione uma função aqui
e chame-a em scan_device().
"""

import logging
import re
import os
import socket
import ssl
import subprocess
import time
from concurrent.futures import ThreadPoolExecutor

from core.constants import (
    COMMON_PORTS, DEVICE_HINTS, HTTP_BANNER_HINTS,
    FG_DIM, FG_ACCENT, FG_GREEN, FG_YELLOW, FG_ORANGE, FG_PRIMARY,
)

logger = logging.getLogger("ipscanner.scanner")

# ── imports opcionais ─────────────────────────────────────────────────────────
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
#  MODELO DE DADOS
# ══════════════════════════════════════════════════════════════════════════════

class DeviceInfo:
    """Representa um dispositivo encontrado na rede."""
    __slots__ = ("ip", "hostname", "mac", "vendor", "os",
                 "services", "icon", "dtype", "color", "alive", "latency")

    def __init__(self, ip: str):
        self.ip       = ip
        self.hostname = ""
        self.mac      = ""
        self.vendor   = ""
        self.os       = ""
        self.services: list[tuple[int, str, str]] = []
        self.icon     = "❓"
        self.dtype    = "Desconhecido"
        self.color    = FG_DIM
        self.alive    = False
        self.latency  = 0.0


# ══════════════════════════════════════════════════════════════════════════════
#  FUNÇÕES DE REDE BÁSICAS
# ══════════════════════════════════════════════════════════════════════════════

def get_local_network() -> str:
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
            s.connect(("8.8.8.8", 80))
            ip = s.getsockname()[0]
        parts = ip.split(".")
        return f"{parts[0]}.{parts[1]}.{parts[2]}.0/24"
    except OSError as e:
        logger.debug("Não foi possível detectar rede local: %s", e)
        return "192.168.1.0/24"


def ping_host(ip: str, timeout: float = 1.0) -> tuple[bool, float]:
    t0 = time.time()
    try:
        # -W espera segundos na maioria das distros Linux (iputils)
        r = subprocess.run(
            ["ping", "-c", "1", "-W", str(max(1, int(timeout))), ip],
            stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
            timeout=timeout + 1.5,
        )
        latency = (time.time() - t0) * 1000
        return r.returncode == 0, round(latency, 1)
    except (subprocess.TimeoutExpired, OSError) as e:
        logger.debug("Ping falhou para %s: %s", ip, e)
        return False, 0.0


def resolve_hostname(ip: str) -> str:
    """Resolve hostname via subprocess (thread-safe — sem alterar estado global)."""
    try:
        result = subprocess.run(
            ["getent", "hosts", ip],
            capture_output=True, text=True, timeout=2,
        )
        if result.returncode == 0 and result.stdout.strip():
            parts = result.stdout.strip().split()
            if len(parts) >= 2:
                return parts[1]
    except (subprocess.TimeoutExpired, OSError) as e:
        logger.debug("Resolução de hostname falhou para %s: %s", ip, e)
    return ""


def get_netbios_name(ip: str) -> str:
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


def get_mac_arp(ip: str) -> str:
    try:
        out = subprocess.check_output(
            ["arp", "-n", ip], stderr=subprocess.DEVNULL, timeout=3,
        ).decode()
        m = re.search(r"([0-9a-f]{2}[:\-]){5}[0-9a-f]{2}", out, re.IGNORECASE)
        if m:
            return m.group(0).upper()
    except (subprocess.TimeoutExpired, subprocess.CalledProcessError, OSError) as e:
        logger.debug("ARP falhou para %s: %s", ip, e)
    return ""


def get_vendor(mac: str) -> str:
    if not mac or not HAS_MAC:
        return ""
    try:
        return _mac_lookup.lookup(mac)
    except Exception as e:
        logger.debug("Vendor lookup falhou para %s: %s", mac, e)
        return ""


# ══════════════════════════════════════════════════════════════════════════════
#  SCAN DE PORTAS
# ══════════════════════════════════════════════════════════════════════════════

def scan_ports_simple(ip: str, timeout: float = 0.4,
                      stop_event=None) -> list[tuple[int, str, str]]:
    """Scan rápido nas portas de COMMON_PORTS via socket."""
    def try_port(port):
        if stop_event and stop_event.is_set():
            return None
        try:
            with socket.create_connection((ip, port), timeout=timeout):
                return port
        except (OSError, socket.error):
            return None

    open_svcs = []
    with ThreadPoolExecutor(max_workers=20) as ex:
        for port in ex.map(try_port, list(COMMON_PORTS.keys())):
            if stop_event and stop_event.is_set():
                break
            if port:
                name, icon, scheme = COMMON_PORTS[port]
                open_svcs.append((port, f"{icon} {name}", scheme))
    open_svcs.sort(key=lambda x: x[0])
    return open_svcs


def http_banner(ip: str, port: int = 80, timeout: float = 2.0) -> str:
    """Coleta Server header, <title> e corpo inicial via HTTP/HTTPS para fingerprint."""
    try:
        with socket.create_connection((ip, port), timeout=timeout) as s:
            # Wrap com TLS para portas HTTPS
            if port in (443, 8443):
                ctx = ssl.create_default_context()
                ctx.check_hostname = False
                ctx.verify_mode = ssl.CERT_NONE
                s = ctx.wrap_socket(s, server_hostname=ip)

            s.sendall(
                f"GET / HTTP/1.0\r\nHost: {ip}\r\nUser-Agent: IPScanner/2\r\n\r\n"
                .encode()
            )
            raw = b""
            s.settimeout(timeout)
            while len(raw) < 8192:
                chunk = s.recv(2048)
                if not chunk:
                    break
                raw += chunk

        text = raw.decode("utf-8", errors="ignore")
        parts = []
        m = re.search(r"(?i)^Server:\s*(.+)$", text, re.MULTILINE)
        if m:
            parts.append(m.group(1).strip())
        m = re.search(r"(?i)<title[^>]*>([^<]{1,120})</title>", text)
        if m:
            parts.append(m.group(1).strip())
        # Inclui trecho do corpo para capturar assets/paths exclusivos de dispositivos
        # (ex: 'steel_gray', 'jquery.cookie.min' nos switches TP-Link Easy Smart)
        body_start = text.find("\r\n\r\n")
        if body_start != -1:
            parts.append(text[body_start:body_start + 2048])
        return " ".join(parts)
    except (OSError, socket.error, ssl.SSLError) as e:
        logger.debug("Banner HTTP falhou para %s:%d: %s", ip, port, e)
        return ""


# ══════════════════════════════════════════════════════════════════════════════
#  SCAN AVANÇADO (nmap)
# ══════════════════════════════════════════════════════════════════════════════

def nmap_scan_full(ip: str) -> dict:
    """Scan nmap com detecção de versão, SO e scripts nbstat/banner."""
    result: dict = {"hostname": "", "os": "", "services": []}
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
        if is_root and h.get("osmatch"):
            result["os"] = h["osmatch"][0].get("name", "")
        for sc in h.get("hostscript", []):
            if "nbstat" in sc.get("id", ""):
                m = re.search(r"NetBIOS name: (\S+)", sc.get("output", ""))
                if m:
                    result["hostname"] = result["hostname"] or m.group(1)
        for proto in h.all_protocols():
            for port in h[proto]:
                svc = h[proto][port]
                if svc["state"] != "open":
                    continue
                parts = [x for x in [svc.get("product", ""),
                                      svc.get("version", ""),
                                      svc.get("extrainfo", "")] if x]
                label = " ".join(parts) or svc.get("name", "")
                icon, scheme = "🔌", ""
                if port in COMMON_PORTS:
                    _, icon, scheme = COMMON_PORTS[port]
                result["services"].append((port, f"{icon} {label}", scheme))
        result["services"].sort(key=lambda x: x[0])
    except Exception as e:
        logger.warning("Nmap scan falhou para %s: %s", ip, e)
    return result


# ══════════════════════════════════════════════════════════════════════════════
#  FINGERPRINT DE DISPOSITIVO
# ══════════════════════════════════════════════════════════════════════════════

def guess_device(hostname: str, vendor: str,
                 services: list, banner: str = "") -> tuple[str, str, str]:
    """
    Detecta tipo do dispositivo em 3 camadas:
      1. hostname + vendor
      2. banner HTTP
      3. portas abertas (fallback)
    """
    ports    = [p for p, _, _ in services]
    combined = f"{hostname} {vendor}".strip()

    if combined:
        for pattern, icon, label, color in DEVICE_HINTS:
            if re.search(pattern, combined):
                return icon, label, color

    if banner:
        for pattern, icon, label, color in HTTP_BANNER_HINTS:
            if re.search(pattern, banner):
                return icon, label, color

    if 3389 in ports: return "🖥️", "Windows (RDP)",  FG_ACCENT
    if 445  in ports: return "🖥️", "Windows/Samba",  FG_ACCENT
    if 22   in ports and 80 not in ports:
        return "🐧", "Linux (SSH)",     FG_YELLOW
    if 9100 in ports or 515 in ports or 631 in ports:
        return "🖨️", "Impressora",      FG_ORANGE
    if 5900 in ports: return "🖥️", "Desktop (VNC)",  FG_PRIMARY
    if 80   in ports or 443 in ports:
        return "🌐", "Servidor Web",    FG_GREEN
    return "❓", "Desconhecido",        FG_DIM


# ══════════════════════════════════════════════════════════════════════════════
#  SCAN COMPLETO DE UM HOST
# ══════════════════════════════════════════════════════════════════════════════

def scan_device(ip: str, advanced: bool = False,
                stop_event=None) -> DeviceInfo | None:
    """
    Escaneia um único host e retorna DeviceInfo ou None se offline.
    stop_event: threading.Event — aborta o scan se sinalizado.
    """
    if stop_event and stop_event.is_set():
        return None

    dev = DeviceInfo(ip)
    alive, latency = ping_host(ip)
    if not alive:
        return None

    dev.alive    = True
    dev.latency  = latency
    dev.hostname = resolve_hostname(ip)
    dev.mac      = get_mac_arp(ip)
    dev.vendor   = get_vendor(dev.mac)
    nb           = get_netbios_name(ip)
    dev.hostname = dev.hostname or nb

    if stop_event and stop_event.is_set():
        return None

    if advanced and HAS_NMAP:
        nm = nmap_scan_full(ip)
        dev.hostname = dev.hostname or nm["hostname"]
        dev.os       = nm["os"]
        dev.services = nm["services"] if nm["services"] else scan_ports_simple(
            ip, stop_event=stop_event)
    else:
        dev.services = scan_ports_simple(ip, stop_event=stop_event)

    # banner HTTP — sempre coletado quando disponível para melhor fingerprint
    banner = ""
    ports = [p for p, _, _ in dev.services]
    for http_port in (80, 8080, 443, 8443):
        if http_port in ports:
            banner = http_banner(ip, http_port)
            if banner:
                break

    dev.icon, dev.dtype, dev.color = guess_device(
        dev.hostname, dev.vendor, dev.services, banner=banner
    )
    return dev
