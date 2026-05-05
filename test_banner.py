#!/usr/bin/env python3
"""
test_banner.py — Diagnóstico de detecção de switches TP-Link
Uso: python3 test_banner.py
"""

import re
import socket
import subprocess
import sys

IPS = ["192.168.88.3", "192.168.88.4"]
HTTP_PORTS = [80, 8080, 443, 8443]
TIMEOUT = 3.0

# ── Paleta ANSI ────────────────────────────────────────────────────────────────
R  = "\033[91m"
G  = "\033[92m"
Y  = "\033[93m"
C  = "\033[96m"
B  = "\033[94m"
DIM = "\033[2m"
RST = "\033[0m"
BOLD = "\033[1m"

def sep(char="─", n=64):
    print(f"{DIM}{char * n}{RST}")

def title(text):
    sep("═")
    print(f"{BOLD}{C}  {text}{RST}")
    sep("═")

def ok(msg):   print(f"  {G}✔{RST}  {msg}")
def err(msg):  print(f"  {R}✘{RST}  {msg}")
def info(msg): print(f"  {Y}→{RST}  {msg}")
def dim(msg):  print(f"  {DIM}{msg}{RST}")


# ── 1. Ping ────────────────────────────────────────────────────────────────────
def ping(ip):
    try:
        r = subprocess.run(
            ["ping", "-c", "1", "-W", "1000", ip],
            stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, timeout=2,
        )
        return r.returncode == 0
    except Exception:
        return False


# ── 2. ARP / MAC ───────────────────────────────────────────────────────────────
def get_mac(ip):
    try:
        out = subprocess.check_output(["arp", "-n", ip], stderr=subprocess.DEVNULL).decode()
        m = re.search(r"([0-9a-f]{2}[:\-]){5}[0-9a-f]{2}", out, re.IGNORECASE)
        return m.group(0).upper() if m else ""
    except Exception:
        return ""


# ── 3. Hostname DNS ────────────────────────────────────────────────────────────
def get_hostname(ip):
    try:
        old = socket.getdefaulttimeout()
        socket.setdefaulttimeout(1)
        try:
            name = socket.gethostbyaddr(ip)[0]
        finally:
            socket.setdefaulttimeout(old)
        return name
    except Exception:
        return ""


# ── 4. Portas abertas ──────────────────────────────────────────────────────────
def check_port(ip, port):
    try:
        with socket.create_connection((ip, port), timeout=1.5):
            return True
    except Exception:
        return False


# ── 5. Banner HTTP bruto ───────────────────────────────────────────────────────
def raw_banner(ip, port):
    """Retorna o cabeçalho HTTP + corpo inicial (até 8 KB)."""
    try:
        s = socket.create_connection((ip, port), timeout=TIMEOUT)
        s.sendall(
            f"GET / HTTP/1.0\r\nHost: {ip}\r\nUser-Agent: IPScanner-Diag/1\r\n\r\n"
            .encode()
        )
        raw = b""
        s.settimeout(TIMEOUT)
        while len(raw) < 8192:
            chunk = s.recv(2048)
            if not chunk:
                break
            raw += chunk
        s.close()
        return raw.decode("utf-8", errors="replace")
    except Exception as e:
        return f"[ERRO: {e}]"


# ── 6. Extrai Server header + <title> ─────────────────────────────────────────
def extract_fields(text):
    server, title_tag = "", ""
    m = re.search(r"(?i)^Server:\s*(.+)$", text, re.MULTILINE)
    if m:
        server = m.group(1).strip()
    m = re.search(r"(?i)<title[^>]*>([^<]{1,200})</title>", text)
    if m:
        title_tag = m.group(1).strip()
    return server, title_tag


# ── 7. Testa padrões de detecção ──────────────────────────────────────────────
PATTERNS = [
    (r"(?i)(tp.?link|tplink)",             "TP-Link explícito"),
    (r"(?i)(TL-S[GLF][0-9])",              "Modelo TL-SG/SF/SL"),
    (r"(?i)(easy.?smart|smart.?switch)",   "Easy Smart / Smart Switch"),
    (r"(?i)(omada)",                        "Omada SDN"),
    (r"(?i)(mikrotik|routeros)",            "MikroTik"),
    (r"(?i)(cisco)",                        "Cisco"),
    (r"(?i)(ubiquiti|unifi|edgeos)",        "Ubiquiti"),
    (r"(?i)(nginx)",                        "Nginx"),
    (r"(?i)(apache)",                       "Apache"),
]

def test_patterns(text):
    combined = " ".join(text.splitlines())
    matched = []
    for pat, label in PATTERNS:
        if re.search(pat, combined):
            matched.append(label)
    return matched


# ══════════════════════════════════════════════════════════════════════════════
#  MAIN
# ══════════════════════════════════════════════════════════════════════════════

def diagnose(ip):
    title(f"Diagnosticando  {ip}")

    # Ping
    alive = ping(ip)
    (ok if alive else err)(f"Ping: {'respondeu' if alive else 'SEM RESPOSTA'}")
    if not alive:
        print()
        return

    # ARP / hostname
    mac      = get_mac(ip)
    hostname = get_hostname(ip)
    info(f"MAC:      {mac or '(não resolvido)'}")
    info(f"Hostname: {hostname or '(não resolvido)'}")

    # Portas abertas
    open_ports = [p for p in HTTP_PORTS if check_port(ip, p)]
    if open_ports:
        ok(f"Portas HTTP abertas: {open_ports}")
    else:
        err("Nenhuma porta HTTP aberta (80, 8080, 443, 8443)")
        print()
        return

    # Banner por porta
    for port in open_ports:
        sep()
        print(f"\n  {B}Porta {port}{RST}\n")

        text = raw_banner(ip, port)

        if text.startswith("[ERRO"):
            err(f"Falha ao obter banner: {text}")
            continue

        server, title_tag = extract_fields(text)
        info(f"Server header : {server or '(ausente)'}")
        info(f"<title>       : {title_tag or '(ausente)'}")

        # Banner combinado (como o scanner usa)
        banner_combined = f"{server} {title_tag}".strip()
        matched = test_patterns(banner_combined)
        if matched:
            ok(f"Padrões detectados : {', '.join(matched)}")
        else:
            err(f"Nenhum padrão detectado no banner: {repr(banner_combined)}")

        # Cabeçalhos HTTP completos
        print(f"\n  {DIM}── Cabeçalhos HTTP ──{RST}")
        headers_end = text.find("\r\n\r\n")
        headers = text[:headers_end] if headers_end != -1 else text[:500]
        for line in headers.splitlines()[:20]:
            dim(f"  {line}")

        # Primeiras linhas do corpo (para debug)
        body_start = headers_end + 4 if headers_end != -1 else 0
        body = text[body_start:body_start + 1200]
        if body.strip():
            print(f"\n  {DIM}── Corpo (primeiros 1200 chars) ──{RST}")
            for line in body.splitlines()[:30]:
                if line.strip():
                    dim(f"  {line}")

    print()


if __name__ == "__main__":
    targets = sys.argv[1:] if len(sys.argv) > 1 else IPS
    for ip in targets:
        diagnose(ip)

    sep("═")
    print(f"\n{BOLD}  Dica:{RST} Se <title> ou Server não contiverem 'tp-link',")
    print("  copie a linha '{DIM}── Corpo{RST}' e me mande para eu ajustar os padrões.\n")
