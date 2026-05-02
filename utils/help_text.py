"""
utils/help_text.py
Textos de ajuda e sobre. Edite aqui para atualizar a documentação interna.
"""

from core.constants import APP_VERSION, GITHUB_REPO_URL

HELP_TEXT = """
╔══════════════════════════════════════════════════════════════════╗
║          ADVANCED IP SCANNER — Guia Completo de Uso             ║
╚══════════════════════════════════════════════════════════════════╝

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
 O QUE É ESTE PROGRAMA?
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

 Advanced IP Scanner é uma ferramenta de descoberta de rede que
 localiza todos os dispositivos ativos em uma rede local (LAN).
 Identifica computadores, roteadores, impressoras, câmeras,
 smart TVs e outros dispositivos, exibindo IP, nome, fabricante,
 MAC address e serviços abertos.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
 COMO FAZER UM SCAN BÁSICO
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

 1. Verifique o campo "Rede" na barra superior.
    • A rede local é detectada automaticamente (ex: 192.168.1.0/24)
    • Formato CIDR obrigatório: ex. 10.0.0.0/24

 2. Defina o intervalo (De / Até):
    • "De: 1  Até: 254" escaneia todos os 254 hosts da sub-rede

 3. Clique em "▶ Verificar" ou Scan → Iniciar scan.

 4. Os dispositivos aparecem em tempo real.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
 SCAN AVANÇADO (nmap)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

 Marque "Scan avançado (nmap)" para obter:
   ✔ Detecção de SO (requer sudo)
   ✔ Versões dos serviços (Apache 2.4, OpenSSH 8.9…)
   ✔ Nome NetBIOS via script nmap
   ✔ Serviços em portas não-padrão

 ⚠ ATENÇÃO: Muito mais lento. Use apenas em redes pequenas.

 Para detecção de SO:
   sudo python3 ipscanner.py

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
 INTERAGINDO COM OS RESULTADOS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

 • Clique simples    → painel de detalhes no rodapé
 • Clique duplo      → abre serviço HTTP/HTTPS no navegador
 • Botão direito     → menu: copiar IP/MAC, abrir serviços, re-scan
 • Clique no cabeçalho → ordena a tabela por aquela coluna

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
 EXPORTAR RESULTADOS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

 Arquivo → Exportar resultados (CSV)…
 Contém: IP, Hostname, MAC, Fabricante, Tipo, SO, Ping, Serviços.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
 SOLUÇÃO DE PROBLEMAS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

 • MAC em branco     → faça ping manual e re-execute o scanner
 • Nenhum resultado  → confirme a rede com: ip route
 • Reinstalar deps   → delete ~/.ipscan_deps_installed e reinicie

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
 USO ÉTICO E LEGAL
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

 ⚠ Use APENAS em redes que você tem autorização para analisar.
"""


def get_about_text(has_nmap: bool, has_mac: bool) -> str:
    import sys
    return f"""
╔══════════════════════════════════════════════════════════════╗
║           Advanced IP Scanner {APP_VERSION} — Linux                  ║
╚══════════════════════════════════════════════════════════════╝

  Clone do Advanced IP Scanner para Linux.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  👤  DESENVOLVIDO POR
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

       ricinus

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  🛠️  TECNOLOGIAS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

   • Python 3.x / Tkinter / ttk
   • python-nmap + nmap
   • mac-vendor-lookup
   • ThreadPoolExecutor
   • urllib (GitHub API)

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  ℹ️  STATUS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

   Versão:     {APP_VERSION}
   Python:     {sys.version.split()[0]}
   nmap:       {"disponível ✔" if has_nmap else "não instalado ✘"}
   mac-lookup: {"disponível ✔" if has_mac else "não instalado ✘"}
   Repositório: {GITHUB_REPO_URL}
"""
