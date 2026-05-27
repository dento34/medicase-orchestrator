"""
Verify UiPath PAT authentication — diagnostic version.

Reads UIPATH_PAT + UIPATH_TENANT_URL from .env (project root), then runs
a sequence of probes from "no auth needed" to "scope-protected" so we
can pinpoint why auth might fail:

  Probe 1: Public OpenID discovery (no auth) — confirms host reachable
  Probe 2: Identity userinfo (PAT, OpenID) — confirms PAT itself is valid
  Probe 3: Orchestrator CurrentUser (PAT, Orchestrator scope)
  Probe 4: Orchestrator Folders list (PAT, Folders.Read scope)

DOES NOT print the token. Only reports success/failure + tenant identity.

Run from project root:
    python agents/scripts/verify_uipath_auth.py
"""
from __future__ import annotations

import io
import sys
import urllib.request
import urllib.error
import json
from pathlib import Path

# Force UTF-8 stdout so non-ASCII tags render on Windows cp1254.
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
else:
    sys.stdout = io.TextIOWrapper(
        sys.stdout.buffer, encoding="utf-8", errors="replace"
    )

# Browser-style User-Agent so UiPath's edge doesn't bot-block us.
USER_AGENT = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
    "AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/126.0.0.0 Safari/537.36"
)


def load_env(env_path: Path) -> dict[str, str]:
    if not env_path.exists():
        print(f"[FAIL] .env not found at {env_path}")
        sys.exit(1)
    env: dict[str, str] = {}
    for line in env_path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, _, value = line.partition("=")
        env[key.strip()] = value.strip()
    return env


def call(url: str, token: str | None) -> tuple[int, str]:
    headers = {
        "Accept": "application/json",
        "User-Agent": USER_AGENT,
    }
    if token:
        headers["Authorization"] = f"Bearer {token}"

    req = urllib.request.Request(url, headers=headers)
    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            return resp.status, resp.read().decode("utf-8", errors="replace")
    except urllib.error.HTTPError as e:
        try:
            err_body = e.read().decode("utf-8", errors="replace")
        except Exception:
            err_body = ""
        return e.code, err_body
    except Exception as e:
        return -1, f"{type(e).__name__}: {e}"


def mask(token: str) -> str:
    if not token or len(token) < 12:
        return "<missing>"
    return f"{token[:6]}…{token[-4:]}"


def trim(body: str, limit: int = 220) -> str:
    body = body.replace("\n", " ").replace("\r", " ").strip()
    return body[:limit] + ("…" if len(body) > limit else "")


def main() -> int:
    project_root = Path(__file__).resolve().parents[2]
    env = load_env(project_root / ".env")

    tenant_url = env.get("UIPATH_TENANT_URL", "").rstrip("/")
    token = env.get("UIPATH_PAT", "")

    if not tenant_url or not token:
        print("[FAIL] UIPATH_TENANT_URL or UIPATH_PAT missing from .env")
        return 1

    parts = tenant_url.split("/")
    host = "/".join(parts[:3])
    org = parts[3] if len(parts) > 3 else ""

    print(f"Tenant URL : {tenant_url}")
    print(f"Host       : {host}")
    print(f"Org        : {org}")
    print(f"Token      : {mask(token)} (length={len(token)}, not logged)")
    print()

    probes = [
        # (label, url, needs_token, ok_codes)
        (
            "1. OpenID discovery (no auth)",
            f"{host}/identity_/.well-known/openid-configuration",
            False,
            {200},
        ),
        (
            "2. Identity userinfo (OpenID scope)",
            f"{host}/identity_/connect/userinfo",
            True,
            {200},
        ),
        (
            "3. Identity ME (org-scoped)",
            f"{tenant_url}/identity_/api/me",
            True,
            {200},
        ),
        (
            "4. Orchestrator CurrentUser",
            f"{tenant_url}/orchestrator_/odata/Users/UiPath.Server.Configuration.OData.GetCurrentUser",
            True,
            {200},
        ),
        (
            "5. Orchestrator Folders ($top=5)",
            f"{tenant_url}/orchestrator_/odata/Folders?$top=5&$select=Id,DisplayName",
            True,
            {200},
        ),
        # Maestro / Case Management — endpoint URL is undocumented for our
        # tenant; probe several plausible shapes to discover the real one.
        (
            "6. Maestro root (maestro_)",
            f"{tenant_url}/maestro_/api/v1/instances?pageSize=5",
            True,
            {200},
        ),
        (
            "7. Maestro alt path (orchestration_)",
            f"{tenant_url}/orchestrator_/api/Maestro/Processes?pageSize=5",
            True,
            {200},
        ),
        (
            "8. Process Apps (apps_)",
            f"{tenant_url}/apps_/api/v1/apps?pageSize=5",
            True,
            {200},
        ),
        (
            "9. Studio Web projects",
            f"{tenant_url}/studio_/api/v1/projects?pageSize=5",
            True,
            {200},
        ),
        (
            "10. Document Understanding",
            f"{tenant_url}/du_/api/framework/projects?pageSize=5",
            True,
            {200},
        ),
    ]

    any_ok = False
    pat_accepted_anywhere = False
    for label, url, needs_token, ok_codes in probes:
        code, body = call(url, token if needs_token else None)
        status = "[OK]  " if code in ok_codes else f"[{code}]"
        print(f"{status} {label}")
        print(f"       URL: {url}")
        if code in ok_codes:
            any_ok = True
            if needs_token:
                pat_accepted_anywhere = True
            try:
                data = json.loads(body)
                if isinstance(data, dict):
                    keep = {
                        k: v
                        for k, v in data.items()
                        if k.lower()
                        in {
                            "issuer",
                            "name",
                            "username",
                            "preferred_username",
                            "email",
                            "sub",
                            "@odata.count",
                            "value",
                        }
                    }
                    if "value" in keep and isinstance(keep["value"], list):
                        keep["value"] = f"<{len(keep['value'])} items>"
                    if keep:
                        print(f"       Body: {trim(json.dumps(keep, ensure_ascii=False))}")
                    else:
                        print(f"       Body: {trim(body)}")
            except json.JSONDecodeError:
                print(f"       Body (non-JSON): {trim(body)}")
        else:
            print(f"       Error: {trim(body, 300)}")
        print()

    print("=" * 70)
    if pat_accepted_anywhere:
        print("[OK]   PAT was accepted by at least one PAT-protected endpoint.")
        return 0
    elif any_ok:
        print("[WARN] Host reachable but PAT was rejected on every PAT endpoint.")
        print("       Most likely cause: the PAT has no resource scopes assigned.")
        print()
        print("       Fix in UiPath:")
        print("       1. Automation Cloud → Preferences → Personal Access Tokens")
        print("       2. Click your token 'claude-project' (or delete + recreate)")
        print("       3. Under 'Resources', add at minimum:")
        print("          - Orchestrator API Access")
        print("          - Maestro API Access")
        print("          - Platform Management API Access")
        print("       4. For each resource, grant the broadest scope offered")
        print("       5. Save / regenerate, replace UIPATH_PAT in .env, rerun this")
        return 2
    else:
        print("[FAIL] Could not reach the host at all. Check network / VPN / DNS.")
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
