"""
core/installer.py
Instalação automática de dependências na primeira execução.
Para adicionar novas dependências, edite PIP_PACKAGES ou _install_system_deps().
"""

import sys
import os
import subprocess
import json
import pathlib
import threading

_MARKER      = pathlib.Path.home() / ".ipscan_deps_installed"
_DEPS_VERSION = "4"   # incremente para forçar reinstalação


# ── helpers baixo nível ───────────────────────────────────────────────────────

def _run(cmd, **kw):
    return subprocess.run(cmd, **kw)


def _detect_distro():
    """Retorna ('debian'|'redhat'|'arch'|'suse'|'unknown', pkg_manager)."""
    if pathlib.Path("/etc/debian_version").exists():
        mgr = "apt-get"
        if _run(["which", "nala"], stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL).returncode == 0:
            mgr = "nala"
        return "debian", mgr
    if (pathlib.Path("/etc/fedora-release").exists()
            or pathlib.Path("/etc/redhat-release").exists()):
        for m in ("dnf", "yum"):
            if _run(["which", m], stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL).returncode == 0:
                return "redhat", m
    if pathlib.Path("/etc/arch-release").exists():
        return "arch", "pacman"
    if (pathlib.Path("/etc/SuSE-release").exists()
            or pathlib.Path("/etc/opensuse-release").exists()):
        return "suse", "zypper"
    return "unknown", ""


def _pip_install(*pkgs):
    _run([sys.executable, "-m", "pip", "install", "--quiet",
          "--break-system-packages", "--root-user-action=ignore", *pkgs])


def _install_system_deps(distro, mgr, log=print):
    """
    Instala pacotes de sistema necessários.
    Edite os dicts abaixo para adicionar pacotes por distro.
    """
    PKGS = {
        "debian":  ["nmap", "python3-tk", "python3-pip"],
        "redhat":  ["nmap", "python3-tkinter", "python3-pip"],
        "arch":    ["nmap", "tk", "python-pip"],
        "suse":    ["nmap", "python3-tk", "python3-pip"],
    }
    pkgs = PKGS.get(distro, [])
    if not pkgs:
        log("⚠ Distribuição desconhecida — instale nmap, python3-tk e pip manualmente.")
        return

    is_root = os.geteuid() == 0
    prefix  = [] if is_root else ["sudo"]

    if distro == "debian":
        _run([*prefix, mgr, "install", "-y"] + pkgs, check=False)
    elif distro == "redhat":
        _run([*prefix, mgr, "install", "-y"] + pkgs, check=False)
    elif distro == "arch":
        _run([*prefix, "pacman", "-S", "--noconfirm"] + pkgs, check=False)
    elif distro == "suse":
        _run([*prefix, "zypper", "install", "-y"] + pkgs, check=False)


# ── pip packages a instalar ───────────────────────────────────────────────────
# Para adicionar uma dependência Python, basta incluir aqui.
PIP_PACKAGES = [
    "python-nmap",
    "mac-vendor-lookup",
]


def _update_mac_vendors(timeout_sec=15):
    """Atualiza base de MACs com timeout — evita travamento sem internet."""
    result = {"ok": False, "msg": ""}

    def _do():
        try:
            from mac_vendor_lookup import MacLookup
            MacLookup().update_vendors()
            result["ok"]  = True
            result["msg"] = "✔ Base de fabricantes atualizada."
        except Exception as e:
            result["msg"] = f"⚠ Não foi possível atualizar base de MACs: {e}"

    t = threading.Thread(target=_do, daemon=True)
    t.start()
    t.join(timeout_sec)
    if t.is_alive():
        return False, f"⚠ Timeout ({timeout_sec}s) ao atualizar base de MACs."
    return result["ok"], result["msg"]


def _already_installed():
    if not _MARKER.exists():
        return False
    try:
        return json.loads(_MARKER.read_text()).get("version") == _DEPS_VERSION
    except Exception:
        return False


def _mark_installed():
    _MARKER.write_text(json.dumps({"version": _DEPS_VERSION}))


# ── janela de instalação ──────────────────────────────────────────────────────

def _run_installer_window():
    import tkinter as tk
    from tkinter import ttk

    root = tk.Tk()
    root.title("Advanced IP Scanner — Configuração Inicial")
    root.geometry("560x380")
    root.resizable(False, False)
    root.configure(bg="#1a1d23")

    tk.Label(root, text="🔍  Advanced IP Scanner",
             bg="#1a1d23", fg="#4fc3f7",
             font=("monospace", 15, "bold")).pack(pady=(28, 4))
    tk.Label(root, text="Instalação de Dependências — Primeira Execução",
             bg="#1a1d23", fg="#7a8299",
             font=("monospace", 9)).pack(pady=(0, 18))

    frame = tk.Frame(root, bg="#22262f")
    frame.pack(fill="x", padx=30)
    log_box = tk.Text(frame, bg="#22262f", fg="#e8eaf0", relief="flat",
                      bd=0, height=10, font=("Courier New", 9), state="disabled")
    log_box.pack(fill="x", padx=10, pady=10)

    pbar = ttk.Progressbar(root, mode="indeterminate", length=500)
    pbar.pack(pady=10, padx=30)

    status_var = tk.StringVar(value="Iniciando…")
    tk.Label(root, textvariable=status_var, bg="#1a1d23", fg="#66bb6a",
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
        log(f"► Distribuição: {distro.upper()} ({mgr or 'desconhecido'})")

        status_var.set("Instalando pacotes do sistema…")
        log("► Instalando nmap, python3-tk, pip…")
        _install_system_deps(distro, mgr, log=log)

        for pkg in PIP_PACKAGES:
            status_var.set(f"Instalando {pkg}…")
            log(f"► Instalando {pkg}…")
            try:
                _pip_install(pkg)
                log(f"✔ {pkg} instalado.")
            except Exception as e:
                log(f"⚠ Erro ao instalar {pkg}: {e}")

        status_var.set("Atualizando base de fabricantes (MAC)…")
        log("► Atualizando base de MACs (timeout: 15s)…")
        ok, msg = _update_mac_vendors(timeout_sec=15)
        log(msg)

        _mark_installed()
        pbar.stop()
        status_var.set("Concluído! Abrindo o scanner…")
        log("\n✅ Tudo pronto!")
        root.after(1800, root.destroy)

    root.after(300,
               lambda: threading.Thread(target=run_install, daemon=True).start())
    root.mainloop()


# ── ponto de entrada público ──────────────────────────────────────────────────

def ensure_dependencies():
    """Chame isto no início do programa antes de qualquer import opcional."""
    if _already_installed():
        return
    try:
        _run_installer_window()
    except Exception as e:
        print(f"[Instalador] {e}. Instalando em modo silencioso…")
        distro, mgr = _detect_distro()
        _install_system_deps(distro, mgr)
        for pkg in PIP_PACKAGES:
            _pip_install(pkg)
        _update_mac_vendors(timeout_sec=15)
        _mark_installed()
