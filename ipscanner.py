#!/usr/bin/env python3
"""
Advanced IP Scanner — Linux
Ponto de entrada principal.

Uso:
    python3 ipscanner.py
    sudo python3 ipscanner.py   ← para detecção de SO (nmap -O)
"""

from core.installer import ensure_dependencies
ensure_dependencies()

from ui.app import AdvancedIPScannerApp

if __name__ == "__main__":
    app = AdvancedIPScannerApp()
    app.mainloop()
