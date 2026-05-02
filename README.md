# Advanced IP Scanner — Linux

Scanner de rede com interface gráfica (Tkinter), desenvolvido por **ricinus**.

---

## Instalação rápida (Debian/Ubuntu)

```bash
sudo apt install python3-tk python3-pip -y
python3 ipscanner.py
```

Para detecção de sistema operacional (requer nmap -O):
```bash
sudo python3 ipscanner.py
```

---

## Estrutura do projeto

```
ipscanner/
├── ipscanner.py          ← ponto de entrada (apenas 10 linhas)
│
├── core/
│   ├── constants.py      ← paleta, fontes, portas, hints de dispositivo
│   ├── installer.py      ← instalação automática de dependências
│   └── scanner.py        ← toda a lógica de scan (ping, nmap, ports, fingerprint)
│
├── ui/
│   ├── app.py            ← janela principal + eventos + treeview
│   ├── dialogs.py        ← janelas modais reutilizáveis (UpdateDialog, etc.)
│   └── style.py          ← tema dark (ttk.Style) centralizado
│
└── utils/
    ├── help_text.py      ← textos de ajuda e "Sobre"
    └── updater.py        ← verificação de atualizações via GitHub API
```

---

## Como expandir

| O que fazer | Onde editar |
|---|---|
| Adicionar porta monitorada | `core/constants.py` → `COMMON_PORTS` |
| Novo hint de dispositivo | `core/constants.py` → `DEVICE_HINTS` ou `HTTP_BANNER_HINTS` |
| Nova dependência Python | `core/installer.py` → `PIP_PACKAGES` |
| Suporte a nova distro | `core/installer.py` → `_install_system_deps()` |
| Novo método de detecção | `core/scanner.py` → nova função + chamada em `scan_device()` |
| Mudar cores/fontes | `core/constants.py` |
| Novo diálogo | `ui/dialogs.py` → nova classe `tk.Toplevel` |
| Novo item de menu | `ui/app.py` → `_build_menubar()` |

---

## Dependências

- `python3-tk` (via apt)
- `python3-pip` (via apt)  
- `nmap` (instalado automaticamente)
- `python-nmap` (instalado automaticamente via pip)
- `mac-vendor-lookup` (instalado automaticamente via pip)
