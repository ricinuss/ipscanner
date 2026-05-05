"""
utils/updater.py
Verificação de atualizações via GitHub Releases API.
"""

import re
import json
import urllib.request
import urllib.error

from core.constants import APP_VERSION, GITHUB_API_URL, GITHUB_REPO_URL


def check_for_updates(timeout: int = 8) -> tuple[bool, str, str, str | None]:
    """
    Consulta a API do GitHub e compara com APP_VERSION.
    Retorna: (has_update, latest_version, download_url, error_msg)
    """
    try:
        req = urllib.request.Request(
            GITHUB_API_URL,
            headers={
                "User-Agent": f"AdvancedIPScanner/{APP_VERSION}",
                "Accept": "application/vnd.github.v3+json",
            },
        )
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            data = json.loads(resp.read().decode())

        latest = data.get("tag_name", "").lstrip("v")
        url    = data.get("html_url", GITHUB_REPO_URL)

        if not latest:
            return False, APP_VERSION, GITHUB_REPO_URL, "Nenhuma release encontrada."

        return _version_gt(latest, APP_VERSION), latest, url, None

    except urllib.error.URLError as e:
        return False, APP_VERSION, GITHUB_REPO_URL, f"Sem conexão: {e.reason}"
    except Exception as e:
        return False, APP_VERSION, GITHUB_REPO_URL, str(e)


def _version_gt(v1: str, v2: str) -> bool:
    """True se v1 > v2 (comparação numérica por partes)."""
    try:
        def parts(v):
            return [int(x) for x in re.split(r"[.\-]", v) if x.isdigit()]
        p1, p2 = parts(v1), parts(v2)
        if not p1 or not p2:
            return False  # não conseguiu parsear → sem update
        return p1 > p2
    except Exception:
        return False  # em caso de erro, não sinalizar update falso
