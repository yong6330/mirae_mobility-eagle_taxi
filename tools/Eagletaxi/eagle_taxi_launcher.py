import re
import json
import importlib
import os
import platform
import queue
import shlex
import shutil
import signal
import socket
import subprocess
import sys
import threading
import time
import webbrowser
from pathlib import Path
import tkinter as tk
from tkinter import ttk, filedialog, messagebox

def bootstrap_psutil_dependency():
    """psutil이 없으면 런처 시작 전에 자동 설치를 시도한다.

    개발 실행 환경에서는 python3/sys.executable에 설치하고, 패키징 환경에서는
    설치 실패 시 조용히 None으로 처리한다. PyInstaller 빌드 전 psutil이 설치되어
    있으면 번들에 포함된다.
    """
    try:
        import psutil as installed_psutil
        return installed_psutil
    except Exception:
        pass

    # 무한 재시도 방지
    if os.environ.get("EAGLE_TAXI_SKIP_PSUTIL_BOOTSTRAP") == "1":
        return None

    candidates = []
    if not getattr(sys, "frozen", False):
        candidates.append(sys.executable)
    for name in ["python3", "python"]:
        path = shutil.which(name)
        if path and path not in candidates:
            candidates.append(path)

    for python_cmd in candidates:
        try:
            subprocess.run(
                [python_cmd, "-m", "pip", "install", "psutil"],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                stdin=subprocess.DEVNULL,
                timeout=180,
                check=False,
            )
            importlib.invalidate_caches()
            import psutil as installed_psutil
            return installed_psutil
        except Exception:
            continue

    return None


psutil = bootstrap_psutil_dependency()


APP_NAME = "Eagle Taxi Dev Launcher"
APP_VERSION = "v.0.1.0-alpha"
APP_TITLE = f"{APP_NAME} {APP_VERSION}"
APP_CONFIG_VERSION = 9
CONFIG_FILE = Path.home() / ".eagle_taxi_launcher_config.json"
TOOL_DIR = Path(__file__).resolve().parent
REPO_ROOT = TOOL_DIR.parents[1]


def first_existing_path(*paths):
    for path in paths:
        if path.exists():
            return path
    return paths[0]


APP_ICON_PATH = first_existing_path(
    TOOL_DIR / "dist" / "assets" / "Eagle Taxi Logo.png",
    REPO_ROOT / "frontend" / "public" / "assets" / "eagle-logo.png",
    REPO_ROOT / "assets" / "Eagle Taxi.png",
)
TITLE_ICON_PATH = first_existing_path(
    TOOL_DIR / "dist" / "assets" / "Eagle Taxi icon.png",
    REPO_ROOT / "frontend" / "public" / "assets" / "eagle-logo.png",
    REPO_ROOT / "assets" / "Eagle Taxi.png",
)
TEAM_LOGO_PATH = first_existing_path(
    TOOL_DIR / "dist" / "assets" / "Mirae Mobility Logo.png",
    REPO_ROOT / "admin" / "public" / "assets" / "eagle-taxi-logo.png",
    REPO_ROOT / "assets" / "Eagle Taxi.png",
)


BACKEND_ENV_TEMPLATE = """# 독수리 택시 백엔드 환경 변수
# 실제 .env 파일은 GitHub에 업로드하지 않는다 (개발 계획안 원칙)

# JWT
JWT_SECRET_KEY=change-this-to-a-random-string
JWT_ALGORITHM=HS256
JWT_EXPIRES_MINUTES=1440

# Database
DATABASE_URL=sqlite:///./eagle_taxi.db

# CORS
CORS_ORIGINS=http://localhost:5173,http://localhost:5174,http://127.0.0.1:5173,http://127.0.0.1:5174

# External mobility REST API Key (요금 산정)
# 명세 §10-3: Key가 없으면 GET /api/fares/estimate, POST /api/parties는
#   500(FARE_CONFIG_MISSING)을 반환한다. 아래 ALLOW_FARE_FALLBACK 참고.
MOBILITY_REST_API_KEY=

# 요금 산정 fallback 허용 (로컬·시연용). true이면 외부 요금 API 실패 시 요금 0 + 경고로 대체.
# 운영 기본은 false (실패를 500/502로 노출). 시연 안정성이 필요하면 true로 둔다.
ALLOW_FARE_FALLBACK=false

# 관리자 이메일 (콤마 구분) — 가입 시 자동 admin 부여
ADMIN_EMAILS=

# 마스터 관리자 이메일 (콤마 구분) — role 변경(ADMIN-006) 권한 + 보호 대상.
# 주의: 비워두면 아무도 마스터가 아니라서 관리자 권한 변경이 전부 403이 된다.
#   운영/시연 시 최소 1개는 반드시 설정할 것.
MASTER_ADMIN_EMAILS=
"""

FRONTEND_ENV_TEMPLATE = """# Keep API requests relative during local Vite development so /api is proxied.
VITE_API_BASE_URL=

# Ask the team lead for the campus map JavaScript key.
# Allowed domains should include http://localhost:5173 and http://127.0.0.1:5173.
VITE_MAP_JS_KEY=your-map-javascript-key
"""


# ============================================================
# 기본 유틸
# ============================================================

def get_system_name():
    return platform.system()


def get_os_label():
    system_name = get_system_name()

    if system_name == "Windows":
        return "Windows"
    if system_name == "Darwin":
        return "macOS"
    if system_name == "Linux":
        return "Linux"

    return system_name or "Unknown"


def get_font_family():
    system_name = get_system_name()

    if system_name == "Windows":
        return "Malgun Gothic"
    if system_name == "Darwin":
        return "Arial"

    return "Arial"


def quote_path(path):
    path = str(path)

    if get_system_name() == "Windows":
        return f'"{path}"'

    return shlex.quote(path)


def short_path(path, max_len=34):
    if not path:
        return "경로 미지정"

    path = str(path)

    if len(path) <= max_len:
        return path

    return "..." + path[-max_len:]


def get_project_root_guess():
    """
    개발 중 실행 / PyInstaller .app 실행 / tools/Eagletaxi 내부 패키징 모두 대응.
    현재 위치 주변에서 backend, frontend, admin 폴더를 가진 프로젝트 루트를 찾는다.
    """
    candidates = []

    try:
        candidates.append(Path(__file__).resolve())
    except Exception:
        pass

    try:
        if getattr(sys, "frozen", False):
            candidates.append(Path(sys.executable).resolve())
    except Exception:
        pass

    candidates.append(Path.cwd().resolve())

    checked = set()

    for start in candidates:
        for path in [start] + list(start.parents):
            if path in checked:
                continue

            checked.add(path)

            if (
                (path / "backend").exists()
                and (path / "frontend").exists()
                and (path / "admin").exists()
            ):
                return path

    # 현재 구조 기준 fallback:
    # /project/tools/Eagletaxi 안에서 실행되는 경우
    try:
        current = Path(__file__).resolve()
        for path in current.parents:
            if path.name == "mirae_mobility-eagle_taxi":
                return path
    except Exception:
        pass

    return Path.cwd()

def get_local_ipv4():
    candidates = []

    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.settimeout(0.2)
        sock.connect(("8.8.8.8", 80))
        ip = sock.getsockname()[0]
        sock.close()

        if ip and not ip.startswith("127."):
            candidates.append(ip)

    except Exception:
        pass

    try:
        hostname = socket.gethostname()
        for ip in socket.gethostbyname_ex(hostname)[2]:
            if ip and not ip.startswith("127.") and ip not in candidates:
                candidates.append(ip)

    except Exception:
        pass

    if candidates:
        return candidates[0]

    return "127.0.0.1"




def get_common_tool_paths():
    """
    macOS .app 실행 시 터미널 PATH가 전달되지 않는 문제를 보완한다.
    Homebrew / 공식 Python / 기본 시스템 경로를 강제로 후보에 넣는다.
    """
    system_name = get_system_name()

    if system_name == "Darwin":
        return [
            "/opt/homebrew/bin",
            "/opt/homebrew/sbin",
            "/usr/local/bin",
            "/usr/local/sbin",
            "/Library/Frameworks/Python.framework/Versions/3.12/bin",
            "/Library/Frameworks/Python.framework/Versions/3.13/bin",
            "/Library/Frameworks/Python.framework/Versions/3.14/bin",
            "/usr/bin",
            "/bin",
            "/usr/sbin",
            "/sbin",
        ]

    if system_name == "Windows":
        return []

    return [
        "/usr/local/bin",
        "/usr/bin",
        "/bin",
        "/usr/sbin",
        "/sbin",
    ]


def get_effective_env(base_env=None):
    """
    .app/.exe로 실행되어도 node/npm/python 명령을 찾을 수 있게 PATH를 보강한다.
    """
    env = dict(base_env or os.environ)

    original_path = env.get("PATH", "")
    original_parts = original_path.split(os.pathsep) if original_path else []

    extra_parts = [
        path for path in get_common_tool_paths()
        if Path(path).exists()
    ]

    merged_parts = []
    seen = set()

    for path in extra_parts + original_parts:
        if not path:
            continue

        try:
            normalized = str(Path(path).resolve())
        except Exception:
            normalized = path

        if normalized in seen:
            continue

        seen.add(normalized)
        merged_parts.append(path)

    env["PATH"] = os.pathsep.join(merged_parts)

    return env


def resolve_command_path(command_name):
    """
    node, npm, python3.12 같은 명령을 현재 PATH + 보강 PATH에서 절대경로로 찾는다.
    """
    env = get_effective_env()
    return shutil.which(command_name, path=env.get("PATH", ""))

def command_exists(command_name):
    return resolve_command_path(command_name) is not None

def get_command_output(command, timeout=8):
    try:
        result = subprocess.run(
            command,
            capture_output=True,
            text=True,
            timeout=timeout,
            encoding="utf-8",
            errors="replace",
            env=get_effective_env(),
        )

        output = (result.stdout or result.stderr or "").strip()

        if result.returncode == 0 and output:
            return output.splitlines()[0]

        return None

    except Exception:
        return None


# ============================================================
# Python / Node 탐지
# ============================================================

def get_default_python_command():
    system_name = get_system_name()

    if system_name == "Windows":
        if command_exists("py"):
            return "py -3"
        return "python"

    if command_exists("python3"):
        return "python3"

    return "python"


def get_python_312_command():
    system_name = get_system_name()

    if system_name == "Windows":
        if command_exists("py"):
            return "py -3.12"
        return "python"

    if command_exists("python3.12"):
        return "python3.12"

    if command_exists("python3"):
        return "python3"

    return "python"


def get_venv_python_path(folder):
    if not folder:
        return None

    folder_path = Path(folder).expanduser()

    candidates = []

    if get_system_name() == "Windows":
        candidates.extend([
            folder_path / ".venv" / "Scripts" / "python.exe",
            folder_path / "venv" / "Scripts" / "python.exe",
        ])
    else:
        candidates.extend([
            folder_path / ".venv" / "bin" / "python",
            folder_path / ".venv" / "bin" / "python3",
            folder_path / "venv" / "bin" / "python",
            folder_path / "venv" / "bin" / "python3",
        ])

    for candidate in candidates:
        if candidate.exists():
            return candidate

    return None


def get_backend_python_command(backend_path):
    venv_python = get_venv_python_path(backend_path)

    if venv_python:
        return quote_path(venv_python)

    return get_python_312_command()


def find_python_status():
    system_name = get_system_name()

    if system_name == "Windows":
        candidates = [
            (["py", "-3.12", "--version"], "py -3.12"),
            (["py", "-3", "--version"], "py -3"),
            (["python", "--version"], "python"),
        ]
    else:
        candidates = [
            (["python3.12", "--version"], "python3.12"),
            (["python3", "--version"], "python3"),
            (["python", "--version"], "python"),
        ]

    for command, label in candidates:
        if command_exists(command[0]):
            version = get_command_output(command)

            if version:
                return {
                    "ok": True,
                    "label": label,
                    "message": version,
                }

    return {
        "ok": False,
        "label": None,
        "message": "Python 명령을 찾지 못했습니다.",
    }


def find_node_status():
    node_exists = command_exists("node")
    npm_exists = command_exists("npm")

    node_version = get_command_output(["node", "--version"]) if node_exists else None
    npm_version = get_command_output(["npm", "--version"]) if npm_exists else None

    if node_exists and npm_exists:
        return {
            "ok": True,
            "message": f"node {node_version}, npm {npm_version}",
        }

    if node_exists and not npm_exists:
        return {
            "ok": False,
            "message": f"node는 있으나 npm을 찾지 못했습니다. node {node_version}",
        }

    if not node_exists and npm_exists:
        return {
            "ok": False,
            "message": f"npm은 있으나 node를 찾지 못했습니다. npm {npm_version}",
        }

    return {
        "ok": False,
        "message": "Node.js와 npm을 찾지 못했습니다.",
    }

def get_default_cloudflared_install_command():
    system_name = get_system_name()

    if system_name == "Windows":
        return (
            "winget install --id Cloudflare.cloudflared -e "
            "--accept-source-agreements --accept-package-agreements"
        )

    if system_name == "Darwin":
        return (
            'if command -v brew >/dev/null 2>&1; then '
            'brew install cloudflared; '
            'else '
            'echo "Homebrew가 없어 Cloudflare 다운로드 페이지를 엽니다."; '
            'open https://developers.cloudflare.com/cloudflare-one/connections/connect-networks/downloads/; '
            'fi'
        )

    return (
        'echo "Linux는 배포판별 설치 방식이 다릅니다."; '
        'echo "Cloudflare 공식 다운로드 문서를 확인하세요."; '
        'echo "https://developers.cloudflare.com/cloudflare-one/connections/connect-networks/downloads/"'
    )


def get_cloudflared_command():
    cloudflared_path = resolve_command_path("cloudflared")

    if cloudflared_path:
        return quote_path(cloudflared_path)

    return "cloudflared"


def find_cloudflared_status():
    if not command_exists("cloudflared"):
        return {
            "ok": False,
            "message": "cloudflared를 찾지 못했습니다.",
        }

    version = get_command_output(["cloudflared", "--version"])

    return {
        "ok": bool(version),
        "message": version or "cloudflared 버전 확인 실패",
    }


def get_default_git_install_command():
    system_name = get_system_name()

    if system_name == "Windows":
        return (
            "winget install --id Git.Git -e "
            "--accept-source-agreements --accept-package-agreements"
        )

    if system_name == "Darwin":
        return (
            'if command -v brew >/dev/null 2>&1; then '
            'brew install git; '
            'else '
            'echo "Git 설치 안내를 엽니다."; '
            'open https://git-scm.com/download/mac; '
            'fi'
        )

    return (
        'echo "Linux는 배포판별 설치 방식이 다릅니다."; '
        'echo "Ubuntu/Debian 예시:"; '
        'echo "sudo apt update && sudo apt install -y git"'
    )


def find_git_status():
    if not command_exists("git"):
        return {
            "ok": False,
            "message": "git을 찾지 못했습니다.",
        }

    version = get_command_output(["git", "--version"])

    return {
        "ok": bool(version),
        "message": version or "git 버전 확인 실패",
    }


def extract_cloudflare_url(line):
    match = re.search(r"https://[a-zA-Z0-9-]+\.trycloudflare\.com", line)

    if match:
        return match.group(0)

    return None


def parse_access_log_line(line):
    """
    Uvicorn 또는 백엔드 로그에서 접속 IP/경로를 최대한 추정한다.
    정확한 외부 IP를 보려면 백엔드에서 CF-Connecting-IP 또는 X-Forwarded-For 로그를 찍는 것이 가장 좋다.
    """
    patterns = [
        r"INFO:\s+([0-9a-fA-F:\.]+):\d+\s+-\s+\"([A-Z]+)\s+([^ ]+)",
        r"\[ACCESS\]\s+ip=([^ ]+)\s+method=([^ ]+)\s+path=([^ ]+)",
    ]

    for pattern in patterns:
        match = re.search(pattern, line)

        if match:
            if len(match.groups()) == 3:
                first, second, third = match.groups()

                if second in ["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"]:
                    return {
                        "ip": first,
                        "method": second,
                        "path": third,
                    }

                return {
                    "ip": first,
                    "method": second,
                    "path": third,
                }

    return None

def find_winget_status():
    if get_system_name() != "Windows":
        return None

    if not command_exists("winget"):
        return {
            "ok": False,
            "message": "winget을 찾지 못했습니다.",
        }

    version = get_command_output(["winget", "--version"])

    return {
        "ok": bool(version),
        "message": version or "winget 버전 확인 실패",
    }


def find_homebrew_status():
    if get_system_name() != "Darwin":
        return None

    if not command_exists("brew"):
        return {
            "ok": False,
            "message": "Homebrew를 찾지 못했습니다.",
        }

    version = get_command_output(["brew", "--version"])

    return {
        "ok": bool(version),
        "message": version or "Homebrew 버전 확인 실패",
    }


# ============================================================
# 기본 명령 생성
# ============================================================

def get_default_python_install_command():
    system_name = get_system_name()

    if system_name == "Windows":
        return (
            "winget install -e --id Python.Python.3.12 "
            "--accept-source-agreements --accept-package-agreements "
            '|| start "" https://www.python.org/downloads/'
        )

    if system_name == "Darwin":
        return (
            'if command -v brew >/dev/null 2>&1; then '
            'brew install python@3.12; '
            'else '
            'echo "Homebrew가 없어 Python 공식 다운로드 페이지를 엽니다."; '
            'open https://www.python.org/downloads/macos/; '
            'fi'
        )

    return (
        'echo "Linux는 배포판마다 설치 명령이 다릅니다."; '
        'echo "Ubuntu/Debian 예시:"; '
        'echo "sudo apt update && sudo apt install -y python3 python3-pip"'
    )


def get_default_node_install_command():
    system_name = get_system_name()

    if system_name == "Windows":
        return (
            "winget install -e --id OpenJS.NodeJS.LTS "
            "--accept-source-agreements --accept-package-agreements "
            '|| start "" https://nodejs.org/en/download'
        )

    if system_name == "Darwin":
        return (
            'if command -v brew >/dev/null 2>&1; then '
            'brew install node; '
            'else '
            'echo "Homebrew가 없어 Node.js 공식 다운로드 페이지를 엽니다."; '
            'open https://nodejs.org/en/download; '
            'fi'
        )

    return (
        'echo "Linux는 배포판마다 설치 명령이 다릅니다."; '
        'echo "Ubuntu/Debian 예시:"; '
        'echo "sudo apt update && sudo apt install -y nodejs npm"'
    )


def get_default_homebrew_install_command():
    if get_system_name() == "Darwin":
        return '/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"'

    return 'echo "Homebrew는 주로 macOS에서 사용하는 설치 도우미입니다."'



def get_backend_create_venv_command():
    if get_system_name() == "Windows":
        return "py -3.12 -m venv .venv || python -m venv .venv"

    return "python3.12 -m venv .venv || python3 -m venv .venv"


def build_backend_install_cmd(backend_path):
    python_cmd = get_backend_python_command(backend_path)
    return f"{python_cmd} -m pip install --upgrade pip && {python_cmd} -m pip install -r requirements.txt"


def build_backend_run_cmd(backend_path):
    python_cmd = get_backend_python_command(backend_path)
    return f"{python_cmd} -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000"




def get_npm_command():
    """
    .app 실행 환경에서도 npm을 확실히 찾기 위한 함수.
    macOS에서는 /opt/homebrew/bin/npm 또는 /usr/local/bin/npm을 우선적으로 잡는다.
    Windows에서는 shell=True가 npm.cmd를 찾을 수 있게 한다.
    """
    npm_path = resolve_command_path("npm")

    if npm_path:
        return quote_path(npm_path)

    return "npm"


def build_frontend_install_cmd(_frontend_path):
    npm_cmd = get_npm_command()
    return f"{npm_cmd} install"


def build_frontend_run_cmd(_frontend_path):
    npm_cmd = get_npm_command()
    return f"{npm_cmd} run dev -- --host 0.0.0.0 --port 5174"


def build_admin_install_cmd(_admin_path):
    npm_cmd = get_npm_command()
    return f"{npm_cmd} install"


def build_admin_run_cmd(_admin_path):
    npm_cmd = get_npm_command()
    return f"{npm_cmd} run dev -- --host 0.0.0.0 --port 5173"


DEFAULT_CONFIG = {
    "config_version": APP_CONFIG_VERSION,

    "backend_path": "",
    "frontend_path": "",
    "admin_path": "",

    "python_install_cmd": get_default_python_install_command(),
    "node_install_cmd": get_default_node_install_command(),
    "homebrew_install_cmd": get_default_homebrew_install_command(),
    "cloudflared_install_cmd": get_default_cloudflared_install_command(),
    "cloudflare_service_domain": "eagle.onestudio.kr",
    "cloudflare_admin_domain": "admin-eagle.onestudio.kr",
    "cloudflare_named_tunnel_name": "eagle-taxi",
    "cloudflare_named_config_path": "~/.cloudflared/eagle-taxi.yml",

    "wizard_repo_url": "https://github.com/yong6330/mirae_mobility-eagle_taxi.git",
    "wizard_target_dir": str(Path.home() / "Downloads" / "mirae_mobility-eagle_taxi"),
    "wizard_env_text": "",
    "wizard_backend_env_text": BACKEND_ENV_TEMPLATE,
    "wizard_frontend_env_text": FRONTEND_ENV_TEMPLATE,

    "backend_create_venv_cmd": get_backend_create_venv_command(),

    "backend_install_cmd": "",
    "frontend_install_cmd": "",
    "admin_install_cmd": "",

    "backend_cmd": "",
    "frontend_cmd": "",
    "admin_cmd": "",
}


SERVER_INFO = {
    "backend": {
        "label": "Backend Server",
        "short": "Backend",
        "path_key": "backend_path",
        "cmd_key": "backend_cmd",
        "install_cmd_key": "backend_install_cmd",
        "port": 8000,
        "run_check_files": ["app/main.py"],
        "install_check_files": ["requirements.txt"],
        "local_url": "http://localhost:8000/api/health",
        "share_path": "/api/health",
    },
    "frontend": {
        "label": "Service Frontend",
        "short": "Service Frontend",
        "path_key": "frontend_path",
        "cmd_key": "frontend_cmd",
        "install_cmd_key": "frontend_install_cmd",
        "port": 5174,
        "run_check_files": ["package.json"],
        "install_check_files": ["package.json"],
        "local_url": "http://localhost:5174",
        "share_path": "",
    },
    "admin": {
        "label": "Admin Frontend",
        "short": "Admin Console",
        "path_key": "admin_path",
        "cmd_key": "admin_cmd",
        "install_cmd_key": "admin_install_cmd",
        "port": 5173,
        "run_check_files": ["package.json"],
        "install_check_files": ["package.json"],
        "local_url": "http://localhost:5173",
        "share_path": "",
    },
}


def build_share_url(server_key, ip_address):
    info = SERVER_INFO[server_key]
    return f"http://{ip_address}:{info['port']}{info['share_path']}"


def build_https_url(hostname):
    hostname = (hostname or "").strip()

    if not hostname:
        return ""

    if hostname.startswith("http://") or hostname.startswith("https://"):
        return hostname

    return f"https://{hostname}"


def build_cloudflare_named_tunnel_command(config_path, tunnel_name):
    config_path = (config_path or "~/.cloudflared/eagle-taxi.yml").strip()
    tunnel_name = (tunnel_name or "eagle-taxi").strip()
    expanded_config = Path(config_path).expanduser()
    return f"{get_cloudflared_command()} tunnel --config {quote_path(expanded_config)} run {tunnel_name}"


def build_cloudflare_setup_commands(tunnel_name, service_domain, admin_domain, config_path):
    tunnel_name = (tunnel_name or "eagle-taxi").strip()
    service_domain = (service_domain or "eagle.onestudio.kr").strip()
    admin_domain = (admin_domain or "admin-eagle.onestudio.kr").strip()
    config_path = (config_path or "~/.cloudflared/eagle-taxi.yml").strip()

    return "\n".join([
        "# 1) Cloudflare 로그인",
        f"{get_cloudflared_command()} tunnel login",
        "",
        "# 2) 고정 터널 생성",
        f"{get_cloudflared_command()} tunnel create {tunnel_name}",
        "",
        "# 3) DNS 라우팅 연결",
        f"{get_cloudflared_command()} tunnel route dns {tunnel_name} {service_domain}",
        f"{get_cloudflared_command()} tunnel route dns {tunnel_name} {admin_domain}",
        "",
        "# 4) 설정 파일 경로",
        f"# {config_path}",
        "",
        "# 5) 설정 파일 작성 예시",
        f"# tunnel: {tunnel_name}",
        "# credentials-file: /Users/사용자명/.cloudflared/터널-UUID.json",
        "# ingress:",
        f"#   - hostname: {service_domain}",
        "#     service: http://localhost:5174",
        f"#   - hostname: {admin_domain}",
        "#     service: http://localhost:5173",
        "#   - service: http_status:404",
        "",
        "# 6) 고정 도메인 터널 실행",
        build_cloudflare_named_tunnel_command(config_path, tunnel_name),
    ])




def get_cloudflared_dir():
    """cloudflared의 기본 설정/인증 파일 폴더."""
    return Path.home() / ".cloudflared"


def get_cloudflare_config_file_path(config_path=None):
    config_path = (config_path or "~/.cloudflared/eagle-taxi.yml").strip()
    return Path(config_path).expanduser()


def find_latest_cloudflare_credentials_file():
    """~/.cloudflared 안에서 가장 최근에 생성/수정된 터널 credentials JSON을 찾는다."""
    cloudflared_dir = get_cloudflared_dir()
    if not cloudflared_dir.exists():
        return None

    candidates = [p for p in cloudflared_dir.glob("*.json") if p.is_file()]
    if not candidates:
        return None

    candidates.sort(key=lambda p: p.stat().st_mtime, reverse=True)
    return candidates[0]


def extract_credentials_file_from_cloudflared_output(line):
    """cloudflared tunnel create 출력에서 credentials JSON 경로를 추출한다."""
    match = re.search(r"([/A-Za-z0-9_ .~\-]+\.cloudflared[/\\][A-Za-z0-9_.\-]+\.json)", line)
    if match:
        return str(Path(match.group(1)).expanduser())
    return None


def build_cloudflare_config_content(tunnel_name, service_domain, admin_domain, credentials_file):
    tunnel_name = (tunnel_name or "eagle-taxi").strip()
    service_domain = (service_domain or "eagle.onestudio.kr").strip()
    admin_domain = (admin_domain or "admin-eagle.onestudio.kr").strip()
    credentials_file = str(Path(credentials_file).expanduser())

    return "\n".join([
        f"tunnel: {tunnel_name}",
        f"credentials-file: {credentials_file}",
        "",
        "ingress:",
        f"  - hostname: {service_domain}",
        "    service: http://localhost:5174",
        "",
        f"  - hostname: {admin_domain}",
        "    service: http://localhost:5173",
        "",
        "  - service: http_status:404",
        "",
    ])


def write_cloudflare_config_file(config_path, tunnel_name, service_domain, admin_domain, credentials_file):
    config_file = get_cloudflare_config_file_path(config_path)
    config_file.parent.mkdir(parents=True, exist_ok=True)
    config_file.write_text(
        build_cloudflare_config_content(tunnel_name, service_domain, admin_domain, credentials_file),
        encoding="utf-8",
    )
    return config_file
def apply_config_migration(config):
    old_version = int(config.get("config_version", 0) or 0)

    if old_version < 4:
        config["frontend_cmd"] = ""
        config["admin_cmd"] = ""
        config["backend_cmd"] = ""
        config["backend_install_cmd"] = ""
        config["frontend_install_cmd"] = ""
        config["admin_install_cmd"] = ""
        config["backend_create_venv_cmd"] = get_backend_create_venv_command()

    if old_version < 6:
        config.setdefault("cloudflare_service_domain", "eagle.onestudio.kr")
        config.setdefault("cloudflare_admin_domain", "admin-eagle.onestudio.kr")
        config.setdefault("cloudflare_named_tunnel_name", "eagle-taxi")
        config.setdefault("cloudflare_named_config_path", "~/.cloudflared/eagle-taxi.yml")

    if old_version < 7:
        config.setdefault("wizard_repo_url", "https://github.com/yong6330/mirae_mobility-eagle_taxi.git")
        config.setdefault("wizard_target_dir", str(Path.home() / "Downloads" / "mirae_mobility-eagle_taxi"))
        config.setdefault("wizard_env_text", "")

    config["config_version"] = APP_CONFIG_VERSION
    return config


def load_config():
    if not CONFIG_FILE.exists():
        return DEFAULT_CONFIG.copy()

    try:
        with open(CONFIG_FILE, "r", encoding="utf-8") as f:
            saved = json.load(f)

        config = DEFAULT_CONFIG.copy()
        config.update(saved)
        return apply_config_migration(config)

    except Exception:
        return DEFAULT_CONFIG.copy()


def save_config(config):
    config["config_version"] = APP_CONFIG_VERSION

    with open(CONFIG_FILE, "w", encoding="utf-8") as f:
        json.dump(config, f, ensure_ascii=False, indent=2)


# ============================================================
# 외부 설치 터미널
# ============================================================

def escape_terminal_script_text(text):
    return text.replace("\\", "\\\\").replace('"', '\\"')


def run_command_external_terminal(title, command):
    system_name = get_system_name()
    home = str(Path.home())

    if system_name == "Windows":
        subprocess.Popen(
            ["cmd.exe", "/k", f'title {title} && cd /d "{home}" && {command}'],
            creationflags=subprocess.CREATE_NEW_CONSOLE,
        )
        return

    if system_name == "Darwin":
        shell_command = f"cd {quote_path(home)} && {command}"
        terminal_script = (
            f'tell application "Terminal" '
            f'to do script "{escape_terminal_script_text(shell_command)}"'
        )
        subprocess.Popen(["osascript", "-e", terminal_script])
        return

    shell_command = f"cd {quote_path(home)} && {command}; exec bash"

    terminal_candidates = [
        ["x-terminal-emulator", "-e", "bash", "-lc", shell_command],
        ["gnome-terminal", "--", "bash", "-lc", shell_command],
        ["konsole", "-e", "bash", "-lc", shell_command],
    ]

    for terminal_command in terminal_candidates:
        try:
            subprocess.Popen(terminal_command)
            return
        except FileNotFoundError:
            continue

    subprocess.Popen(["bash", "-lc", shell_command])


# ============================================================
# 런처 클래스
# ============================================================

class EagleTaxiLauncher:
    def __init__(self, root):
        self.root = root
        self.root.title(APP_TITLE)
        self.apply_app_icon()
        self.root.geometry("1240x820")
        self.root.minsize(1080, 720)

        self.font_family = get_font_family()
        self.config = load_config()

        self.vars = {
            "backend_path": tk.StringVar(value=self.config["backend_path"]),
            "frontend_path": tk.StringVar(value=self.config["frontend_path"]),
            "admin_path": tk.StringVar(value=self.config["admin_path"]),

            "python_install_cmd": tk.StringVar(value=self.config["python_install_cmd"]),
            "node_install_cmd": tk.StringVar(value=self.config["node_install_cmd"]),
            "homebrew_install_cmd": tk.StringVar(value=self.config["homebrew_install_cmd"]),
            "cloudflared_install_cmd": tk.StringVar(
                value=self.config.get(
                    "cloudflared_install_cmd",
                    get_default_cloudflared_install_command(),
                )
            ),
            "cloudflare_service_domain": tk.StringVar(
                value=self.config.get("cloudflare_service_domain", "eagle.onestudio.kr")
            ),
            "cloudflare_admin_domain": tk.StringVar(
                value=self.config.get("cloudflare_admin_domain", "admin-eagle.onestudio.kr")
            ),
            "cloudflare_named_tunnel_name": tk.StringVar(
                value=self.config.get("cloudflare_named_tunnel_name", "eagle-taxi")
            ),
            "cloudflare_named_config_path": tk.StringVar(
                value=self.config.get("cloudflare_named_config_path", "~/.cloudflared/eagle-taxi.yml")
            ),
            "wizard_repo_url": tk.StringVar(
                value=self.config.get("wizard_repo_url", "https://github.com/yong6330/mirae_mobility-eagle_taxi.git")
            ),
            "wizard_target_dir": tk.StringVar(
                value=self.config.get("wizard_target_dir", str(Path.home() / "Downloads" / "mirae_mobility-eagle_taxi"))
            ),

            "backend_create_venv_cmd": tk.StringVar(value=self.config["backend_create_venv_cmd"]),

            "backend_install_cmd": tk.StringVar(value=self.config["backend_install_cmd"]),
            "frontend_install_cmd": tk.StringVar(value=self.config["frontend_install_cmd"]),
            "admin_install_cmd": tk.StringVar(value=self.config["admin_install_cmd"]),

            "backend_cmd": tk.StringVar(value=self.config["backend_cmd"]),
            "frontend_cmd": tk.StringVar(value=self.config["frontend_cmd"]),
            "admin_cmd": tk.StringVar(value=self.config["admin_cmd"]),
        }

        self.status_var = tk.StringVar(value="준비됨")
        self.ip_var = tk.StringVar(value=get_local_ipv4())
        self.tool_status_var = tk.StringVar(value="Check Status 전")

        self.path_summary_vars = {
            "backend": tk.StringVar(value="경로 미지정"),
            "frontend": tk.StringVar(value="경로 미지정"),
            "admin": tk.StringVar(value="경로 미지정"),
        }

        self.server_status_vars = {}
        self.log_widgets = {}
        self.processes = {}
        self.process_meta = {}
        self.output_queue = queue.Queue()

        self.tunnel_url_vars = {
            "frontend": tk.StringVar(value="서비스 공개 URL 없음"),
            "admin": tk.StringVar(value="관리자 공개 URL 없음"),
        }

        self.visitor_events = []
        self.singleton_windows = {}
        self.server_toggle_buttons = {}
        self.all_server_toggle_button = None
        self.all_tunnel_toggle_button = None
        self.named_tunnel_toggle_button = None
        self.quick_tunnel_toggle_button = None
        self.traffic_history = []
        self.system_monitor_history = {"cpu": [], "ram": [], "net": []}
        self.traffic_last_sample = None
        self.traffic_monitor_running = False
        self.cloudflare_wizard_log_text = None
        self.wizard_env_text = self.config.get("wizard_env_text", "")
        self.wizard_backend_env_text = self.config.get("wizard_backend_env_text") or BACKEND_ENV_TEMPLATE
        self.wizard_frontend_env_text = self.config.get("wizard_frontend_env_text") or FRONTEND_ENV_TEMPLATE
        self.wizard_current_step = 0
        self.wizard_step_body = None
        self.wizard_step_title_var = tk.StringVar(value="")
        self.wizard_prev_button = None
        self.wizard_next_button = None
        self.wizard_finish_button = None
        self.wizard_log_text = None

        self.setup_style()
        self.ensure_auto_commands(fill_empty_only=True)
        self.build_ui()
        self.refresh_all_summaries()

        self.root.protocol("WM_DELETE_WINDOW", self.on_close)
        self.root.after(100, self.process_log_queue)
        self.root.after(300, self.set_initial_sash_position)
        self.root.after(700, self.auto_check_tools_on_start)

    # --------------------------------------------------------
    # UI
    # --------------------------------------------------------

    def setup_style(self):
        style = ttk.Style()

        try:
            style.theme_use("clam")
        except Exception:
            pass

        # A compact, consistent light UI that behaves similarly across macOS/Windows/Linux.
        self.ui_bg = "#F4F7FA"
        self.ui_card = self.ui_bg  # unify panel/card background to avoid floating white blocks
        self.ui_border = "#D8DEE4"
        self.ui_text = "#1F2328"
        self.ui_muted = "#6E7781"
        self.ui_primary = "#0969DA"
        self.ui_primary_active = "#0550AE"
        self.ui_danger = "#CF222E"
        self.ui_success = "#1A7F37"
        self.ui_warn = "#9A6700"
        self.ui_log_bg = "#0D1117"
        self.ui_log_fg = "#E6EDF3"

        try:
            self.root.configure(bg=self.ui_bg)
        except Exception:
            pass

        base_font = (self.font_family, 11)
        small_font = (self.font_family, 10)
        tiny_font = (self.font_family, 9)

        style.configure(".", font=base_font, background=self.ui_bg, foreground=self.ui_text)
        style.configure("TFrame", background=self.ui_bg)
        style.configure("Panel.TFrame", background=self.ui_bg)
        style.configure("CardBody.TFrame", background=self.ui_card)
        style.configure("Inset.TFrame", background=self.ui_bg, bordercolor=self.ui_border, relief="solid")
        style.configure("Title.TLabel", font=(self.font_family, 21, "bold"), background=self.ui_bg, foreground=self.ui_text)
        style.configure("WizardTitle.TLabel", font=(self.font_family, 17, "bold"), background=self.ui_bg, foreground=self.ui_text)
        style.configure("SectionTitle.TLabel", font=(self.font_family, 12, "bold"), background=self.ui_card, foreground=self.ui_text)
        style.configure("Subtle.TLabel", font=small_font, background=self.ui_bg, foreground=self.ui_muted)
        style.configure("CardSubtle.TLabel", font=small_font, background=self.ui_card, foreground=self.ui_muted)
        style.configure("Version.TLabel", font=(self.font_family, 11, "bold"), background=self.ui_bg, foreground=self.ui_muted)
        style.configure("Brand.TLabel", font=(self.font_family, 11, "bold"), background=self.ui_bg, foreground=self.ui_muted)
        style.configure("Status.TLabel", font=(self.font_family, 11, "bold"), background=self.ui_bg, foreground=self.ui_text)
        style.configure("CardStatus.TLabel", font=(self.font_family, 11, "bold"), background=self.ui_card, foreground=self.ui_text)
        style.configure("Good.TLabel", font=(self.font_family, 10, "bold"), background=self.ui_card, foreground=self.ui_success)
        style.configure("Warn.TLabel", font=(self.font_family, 10, "bold"), background=self.ui_card, foreground=self.ui_warn)
        style.configure("Bad.TLabel", font=(self.font_family, 10, "bold"), background=self.ui_card, foreground=self.ui_danger)

        style.configure("Card.TLabelframe", background=self.ui_card, bordercolor=self.ui_border, relief="solid", padding=(8, 5))
        style.configure("Card.TLabelframe.Label", background=self.ui_card, foreground=self.ui_text, font=(self.font_family, 10, "bold"))
        style.configure("Global.TLabelframe", background=self.ui_card, bordercolor=self.ui_border, relief="solid", padding=(8, 5))
        style.configure("Global.TLabelframe.Label", background=self.ui_card, foreground=self.ui_text, font=(self.font_family, 10, "bold"))

        style.configure("TNotebook", background=self.ui_bg, borderwidth=0)
        style.configure("TNotebook.Tab", padding=(12, 5), font=(self.font_family, 9, "bold"))
        style.map("TNotebook.Tab", background=[("selected", self.ui_card)], foreground=[("selected", self.ui_text)])
        style.configure("Main.TNotebook", background=self.ui_bg, borderwidth=0)
        style.configure("Main.TNotebook.Tab", padding=(18, 8), font=(self.font_family, 11, "bold"))
        style.map("Main.TNotebook.Tab", background=[("selected", self.ui_card)], foreground=[("selected", self.ui_text)])

        style.configure("TEntry", fieldbackground="#FFFFFF", bordercolor=self.ui_border, padding=(4, 2))
        style.configure("TButton", padding=(8, 4), font=(self.font_family, 10, "bold"))
        style.configure("Compact.TButton", padding=(6, 2), font=(self.font_family, 9, "bold"))
        style.configure("LogTab.TButton", padding=(8, 2), font=(self.font_family, 9, "bold"), background=self.ui_bg, foreground=self.ui_muted)
        style.configure("LogActive.TButton", padding=(8, 2), font=(self.font_family, 9, "bold"), background="#DDF4FF", foreground=self.ui_primary)
        style.configure("Small.TButton", padding=(8, 3), font=(self.font_family, 10, "bold"))
        style.configure("Primary.TButton", padding=(10, 4), font=(self.font_family, 10, "bold"), background="#DDF4FF", foreground=self.ui_primary)
        style.configure("Danger.TButton", padding=(10, 4), font=(self.font_family, 10, "bold"), background="#FFEBE9", foreground=self.ui_danger)
        style.configure("Success.TButton", padding=(10, 4), font=(self.font_family, 10, "bold"), background="#DAFBE1", foreground=self.ui_success)
        style.map("Primary.TButton", background=[("active", "#B6E3FF")], foreground=[("active", self.ui_primary_active)])
        style.map("Danger.TButton", background=[("active", "#FFD8D3")])
        style.map("Small.TButton", background=[("active", "#EAEEF2")])

        try:
            style.configure("Treeview", rowheight=22, font=small_font, background="#FFFFFF", fieldbackground="#FFFFFF", foreground=self.ui_text)
            style.configure("Treeview.Heading", font=(self.font_family, 9, "bold"), background="#F6F8FA", foreground=self.ui_text)
        except Exception:
            pass

    def apply_app_icon(self):
        """앱 타이틀바/작업표시줄 로고 적용. 파일이 없으면 조용히 건너뛴다."""
        try:
            icon_path = APP_ICON_PATH
            if not icon_path.exists() and TITLE_ICON_PATH.exists():
                icon_path = TITLE_ICON_PATH
            if getattr(sys, "frozen", False):
                for bundled_name in ["Eagle Taxi Logo.png", "Eagle Taxi icon.png"]:
                    bundled = Path(getattr(sys, "_MEIPASS", "")) / bundled_name
                    if bundled.exists():
                        icon_path = bundled
                        break
            if icon_path.exists():
                self._app_icon_image = tk.PhotoImage(file=str(icon_path))
                self.root.iconphoto(True, self._app_icon_image)
        except Exception:
            pass

    def load_title_icon_image(self):
        """헤더 타이틀 왼쪽에 표시할 작은 아이콘을 로드한다."""
        try:
            icon_path = TITLE_ICON_PATH
            if not icon_path.exists():
                icon_path = APP_ICON_PATH
            if getattr(sys, "frozen", False):
                for bundled_name in ["Eagle Taxi icon.png", "Eagle Taxi Logo.png"]:
                    bundled = Path(getattr(sys, "_MEIPASS", "")) / bundled_name
                    if bundled.exists():
                        icon_path = bundled
                        break
            if not icon_path.exists():
                return None
            image = tk.PhotoImage(file=str(icon_path))
            width = max(int(image.width()), 1)
            height = max(int(image.height()), 1)
            target_height = 28
            factor = max(1, int(round(height / target_height)))
            if factor > 1:
                image = image.subsample(factor, factor)
            self._title_icon_image = image
            return image
        except Exception:
            return None



    def load_team_logo_image(self):
        """헤더 우측에 표시할 팀 로고를 로드한다."""
        try:
            logo_path = TEAM_LOGO_PATH
            if getattr(sys, "frozen", False):
                for bundled_name in ["Mirae Mobility Logo.png"]:
                    bundled = Path(getattr(sys, "_MEIPASS", "")) / bundled_name
                    if bundled.exists():
                        logo_path = bundled
                        break
            if not logo_path.exists():
                return None
            image = tk.PhotoImage(file=str(logo_path))
            width = max(int(image.width()), 1)
            height = max(int(image.height()), 1)
            target_height = 30
            factor = max(1, int(round(height / target_height)))
            if factor > 1:
                image = image.subsample(factor, factor)
            self._team_logo_image = image
            return image
        except Exception:
            return None

    def focus_existing_window(self, key):
        win = self.singleton_windows.get(key)
        try:
            if win is not None and win.winfo_exists():
                win.lift()
                win.focus_set()
                return True
        except Exception:
            pass
        self.singleton_windows.pop(key, None)
        return False

    def register_singleton_window(self, key, win, cleanup=None):
        self.singleton_windows[key] = win

        def on_close():
            try:
                if cleanup:
                    cleanup()
            finally:
                self.singleton_windows.pop(key, None)
                win.destroy()

        win.protocol("WM_DELETE_WINDOW", on_close)
        return win

    def append_to_text_widget(self, widget, message):
        try:
            if widget is None or not widget.winfo_exists():
                return
            widget.configure(state="normal")
            widget.insert("end", message + "\n")
            widget.see("end")
            widget.configure(state="normal")
        except Exception:
            pass

    def append_cloudflare_wizard_log(self, message):
        if getattr(self, "cloudflare_wizard_log_text", None) is not None:
            self.append_to_text_widget(self.cloudflare_wizard_log_text, message)

    def is_process_running(self, process_key):
        process = self.processes.get(process_key)
        return bool(process and process.poll() is None)

    def is_server_running(self, server_key):
        return self.is_process_running(f"{server_key}_run")

    def update_server_toggle_button(self, server_key):
        button = self.server_toggle_buttons.get(server_key)
        if not button:
            return
        try:
            if self.is_server_running(server_key):
                button.configure(text="⏹️ Stop", style="Danger.TButton")
            else:
                button.configure(text="▶️ Start", style="Primary.TButton")
        except Exception:
            pass


    def update_all_server_toggle_buttons(self):
        for key in ["backend", "frontend", "admin"]:
            self.update_server_toggle_button(key)
        self.update_all_server_batch_toggle_button()


    def update_all_server_batch_toggle_button(self):
        button = getattr(self, "all_server_toggle_button", None)
        if not button:
            return
        try:
            if self.is_any_server_running():
                button.configure(text="⏹️ Stop All Servers", style="Danger.TButton")
            else:
                button.configure(text="▶️ Start All Servers", style="Primary.TButton")
        except Exception:
            pass


    def toggle_server(self, server_key):
        if self.is_server_running(server_key):
            self.stop_server(server_key)
        else:
            self.run_server(server_key)


    def is_any_server_running(self):
        return any(self.is_server_running(key) for key in ["backend", "frontend", "admin"])


    def toggle_all_servers(self):
        if self.is_any_server_running():
            self.stop_all_servers()
        else:
            self.run_all_servers()


    def is_named_tunnel_running(self):
        return self.is_process_running("named_tunnel")


    def is_quick_tunnels_running(self):
        return self.is_process_running("frontend_tunnel") or self.is_process_running("admin_tunnel")


    def is_any_tunnel_running(self):
        return self.is_named_tunnel_running() or self.is_quick_tunnels_running()


    def update_tunnel_toggle_buttons(self):
        try:
            if getattr(self, "all_tunnel_toggle_button", None):
                if self.is_any_tunnel_running():
                    self.all_tunnel_toggle_button.configure(text="⏹️ Stop All Tunnels", style="Danger.TButton")
                else:
                    self.all_tunnel_toggle_button.configure(text="▶️ Start All Tunnels", style="Primary.TButton")
            if getattr(self, "named_tunnel_toggle_button", None):
                if self.is_named_tunnel_running():
                    self.named_tunnel_toggle_button.configure(text="⏹️ Stop Named Tunnel", style="Danger.TButton")
                else:
                    self.named_tunnel_toggle_button.configure(text="▶️ Start Named Tunnel", style="Primary.TButton")
            if getattr(self, "quick_tunnel_toggle_button", None):
                if self.is_quick_tunnels_running():
                    self.quick_tunnel_toggle_button.configure(text="⏹️ Stop Quick Tunnels", style="Danger.TButton")
                else:
                    self.quick_tunnel_toggle_button.configure(text="⚡ Start Quick Tunnels", style="Primary.TButton")
        except Exception:
            pass


    def update_all_runtime_toggle_buttons(self):
        self.update_all_server_toggle_buttons()
        self.update_tunnel_toggle_buttons()


    def toggle_all_tunnels(self):
        if self.is_any_tunnel_running():
            self.stop_cloudflare_tunnels()
        else:
            self.start_all_cloudflare_tunnels()


    def toggle_named_tunnel(self):
        if self.is_named_tunnel_running():
            self.stop_cloudflare_named_tunnel()
        else:
            self.start_cloudflare_named_tunnel()


    def toggle_quick_tunnels(self):
        if self.is_quick_tunnels_running():
            self.stop_cloudflare_tunnel("frontend")
            self.stop_cloudflare_tunnel("admin")
        else:
            self.start_cloudflare_tunnel("frontend")
            self.start_cloudflare_tunnel("admin")

    def start_traffic_monitor(self):
        if self.traffic_monitor_running:
            return
        self.traffic_monitor_running = True
        self.root.after(500, self.update_traffic_monitor)

    def stop_traffic_monitor(self):
        self.traffic_monitor_running = False

    def update_traffic_monitor(self):
        if not self.traffic_monitor_running:
            return

        cpu_percent = 0.0
        ram_percent = 0.0
        net_kbps = 0.0
        status = "psutil unavailable"

        if psutil is not None:
            try:
                now = time.time()
                counters = psutil.net_io_counters()
                cpu_percent = float(psutil.cpu_percent(interval=None))
                ram_percent = float(psutil.virtual_memory().percent)

                if self.traffic_last_sample is not None:
                    last_time, last_sent, last_recv = self.traffic_last_sample
                    elapsed = max(now - last_time, 0.001)
                    tx_kbps = max((counters.bytes_sent - last_sent) / 1024 / elapsed, 0.0)
                    rx_kbps = max((counters.bytes_recv - last_recv) / 1024 / elapsed, 0.0)
                    net_kbps = tx_kbps + rx_kbps
                    status = f"CPU {cpu_percent:4.1f}%   RAM {ram_percent:4.1f}%   NET {net_kbps:,.1f} KB/s"
                else:
                    status = f"CPU {cpu_percent:4.1f}%   RAM {ram_percent:4.1f}%   NET sampling..."

                self.traffic_last_sample = (now, counters.bytes_sent, counters.bytes_recv)
            except Exception as e:
                status = f"monitor error: {e}"

        self.system_monitor_history["cpu"].append(cpu_percent)
        self.system_monitor_history["ram"].append(ram_percent)
        self.system_monitor_history["net"].append(net_kbps)
        for key in ["cpu", "ram", "net"]:
            self.system_monitor_history[key] = self.system_monitor_history[key][-80:]

        # 이전 버전 호환: traffic_history는 네트워크 값만 유지
        self.traffic_history = self.system_monitor_history["net"][-80:]

        if hasattr(self, "traffic_status_var"):
            self.traffic_status_var.set(status)
        if hasattr(self, "traffic_canvas"):
            self.draw_traffic_graph()

        self.root.after(1000, self.update_traffic_monitor)

    def draw_traffic_graph(self):
        canvas = self.traffic_canvas
        try:
            canvas.delete("all")
            width = max(canvas.winfo_width(), 360)
            height = max(canvas.winfo_height(), 110)
            padding_left = 34
            padding_right = 14
            padding_top = 24
            padding_bottom = 20
            plot_w = max(width - padding_left - padding_right, 20)
            plot_h = max(height - padding_top - padding_bottom, 20)

            canvas.create_rectangle(0, 0, width, height, fill="#FAFAFA", outline="#D0D7DE")
            canvas.create_line(padding_left, padding_top, padding_left, padding_top + plot_h, fill="#D0D7DE")
            canvas.create_line(padding_left, padding_top + plot_h, padding_left + plot_w, padding_top + plot_h, fill="#D0D7DE")

            if psutil is None:
                canvas.create_text(width // 2, height // 2, text="psutil not installed - python3 -m pip install psutil", fill="#555555")
                return

            cpu = self.system_monitor_history.get("cpu", [])
            ram = self.system_monitor_history.get("ram", [])
            net = self.system_monitor_history.get("net", [])
            if not any([cpu, ram, net]):
                canvas.create_text(width // 2, height // 2, text="waiting for monitor data", fill="#555555")
                return

            def make_points(values, max_value):
                if not values:
                    return []
                count = len(values)
                pts = []
                max_value = max(float(max_value), 1.0)
                for idx, value in enumerate(values):
                    x = padding_left + plot_w * (idx / max(count - 1, 1))
                    y = padding_top + plot_h - (plot_h * (max(min(value, max_value), 0.0) / max_value))
                    pts.extend([x, y])
                return pts

            # CPU/RAM은 0~100% 축, Network는 최근 최대값 기준 축으로 정규화
            series = [
                ("CPU", cpu, 100.0, "#D1242F"),
                ("RAM", ram, 100.0, "#1A7F37"),
                ("NET", net, max(max(net) if net else 1.0, 1.0), "#0969DA"),
            ]
            for label, values, max_value, color in series:
                pts = make_points(values, max_value)
                if len(pts) >= 4:
                    canvas.create_line(*pts, fill=color, width=2, smooth=True)

            latest_cpu = cpu[-1] if cpu else 0.0
            latest_ram = ram[-1] if ram else 0.0
            latest_net = net[-1] if net else 0.0
            legend = f"CPU {latest_cpu:4.1f}%   RAM {latest_ram:4.1f}%   NET {latest_net:,.1f} KB/s"
            canvas.create_text(padding_left, 10, anchor="w", text=legend, fill="#24292F")
            canvas.create_text(width - padding_right, 10, anchor="e", text="CPU/RAM/Network", fill="#57606A")
            canvas.create_text(8, padding_top, anchor="w", text="100", fill="#8C959F")
            canvas.create_text(8, padding_top + plot_h, anchor="w", text="0", fill="#8C959F")
        except Exception:
            pass

    def build_ui(self):
        try:
            self.root.geometry("1240x760")
            self.root.minsize(1120, 700)
            self.root.configure(bg=self.ui_bg)
        except Exception:
            pass

        self.shell = ttk.Frame(self.root, padding=(10, 6, 10, 8), style="Panel.TFrame")
        self.shell.pack(fill="both", expand=True)

        header = ttk.Frame(self.shell, style="Panel.TFrame")
        header.pack(fill="x", pady=(0, 5))
        header.columnconfigure(0, weight=1)
        header.columnconfigure(1, weight=0)

        title_group = ttk.Frame(header, style="Panel.TFrame")
        title_group.grid(row=0, column=0, sticky="w")

        title_icon = self.load_title_icon_image()
        if title_icon is not None:
            ttk.Label(title_group, image=title_icon, style="Subtle.TLabel").pack(side="left", anchor="center", padx=(0, 7))

        ttk.Label(title_group, text=APP_NAME, style="Title.TLabel").pack(side="left", anchor="w")
        ttk.Label(title_group, text=f" {APP_VERSION}", style="Version.TLabel").pack(side="left", anchor="w", padx=(5, 12), pady=(7, 0))
        ttk.Label(title_group, text=f"OS: {get_os_label()}", style="Version.TLabel").pack(side="left", anchor="w", pady=(7, 0))

        ttk.Label(header, text="Mirae Mobility", style="Brand.TLabel").grid(row=0, column=1, sticky="e", padx=(12, 0))

        self.content_frame = ttk.Frame(self.shell, style="Panel.TFrame")
        self.content_frame.pack(fill="both", expand=True)

        if self.should_show_initial_wizard():
            self.show_initial_wizard()
        else:
            self.show_main_console()

    def set_initial_sash_position(self):
        try:
            if hasattr(self, "main_pane"):
                height = self.main_pane.winfo_height()
                self.main_pane.sashpos(0, int(height * 0.62))
            if hasattr(self, "console_pane"):
                width = self.console_pane.winfo_width()
                self.console_pane.sashpos(0, int(width * 0.74))
        except Exception:
            pass


    def clear_content(self):
        for child in self.content_frame.winfo_children():
            child.destroy()
        self.log_widgets = {}
        if hasattr(self, "visitor_tree"):
            try:
                del self.visitor_tree
            except Exception:
                pass
        if hasattr(self, "share_text"):
            try:
                del self.share_text
            except Exception:
                pass
        if hasattr(self, "cloudflare_text"):
            try:
                del self.cloudflare_text
            except Exception:
                pass

    def should_show_initial_wizard(self):
        """최초 실행 또는 필수 프로젝트 파일 부재 시 Zero-to-Hero Wizard로 진입한다."""
        for key, required_files in [
            ("backend_path", ["app/main.py", "requirements.txt"]),
            ("frontend_path", ["package.json"]),
            ("admin_path", ["package.json"]),
        ]:
            folder = self.vars.get(key).get().strip() if key in self.vars else ""
            if not folder:
                return True
            folder_path = Path(folder).expanduser()
            if not folder_path.exists():
                return True
            for file_name in required_files:
                if not (folder_path / file_name).exists():
                    return True
        return False

    def show_initial_wizard(self):
        self.clear_content()
        self.build_initial_wizard_view(self.content_frame)
        self.status_var.set("초기 설정 마법사 진행 중")

    def show_main_console(self):
        self.clear_content()
        self.build_main_console_view(self.content_frame)
        self.refresh_all_summaries()
        self.status_var.set("메인 콘솔 준비됨")
        self.root.after(200, self.set_initial_sash_position)

    def build_initial_wizard_view(self, parent):
        self.wizard_current_step = 0
        wizard = ttk.Frame(parent, padding=(2, 0, 2, 0), style="Panel.TFrame")
        wizard.pack(fill="both", expand=True)
        wizard.columnconfigure(0, weight=1)
        wizard.rowconfigure(1, weight=1)
        wizard.rowconfigure(2, weight=0)

        header = ttk.Frame(wizard, style="Panel.TFrame")
        header.grid(row=0, column=0, sticky="ew", pady=(0, 6))
        ttk.Label(header, text="Zero-to-Hero Setup Wizard", style="WizardTitle.TLabel").pack(side="left", anchor="w")
        ttk.Label(header, textvariable=self.wizard_step_title_var, style="Status.TLabel").pack(side="right", anchor="e")

        # Body and log are intentionally separated so the step UI does not become a huge empty canvas.
        self.wizard_step_body = ttk.Frame(wizard, style="Panel.TFrame")
        self.wizard_step_body.grid(row=1, column=0, sticky="nsew")
        self.wizard_step_body.columnconfigure(0, weight=1)
        self.wizard_step_body.rowconfigure(0, weight=1)

        log_frame = ttk.LabelFrame(wizard, text="Wizard Output", style="Card.TLabelframe")
        log_frame.grid(row=2, column=0, sticky="ew", pady=(6, 4))
        log_frame.columnconfigure(0, weight=1)
        self.wizard_log_text = tk.Text(
            log_frame,
            height=5,
            wrap="word",
            font=("Menlo" if get_system_name() == "Darwin" else "Consolas", 9),
            bg=self.ui_log_bg,
            fg=self.ui_log_fg,
            insertbackground=self.ui_log_fg,
            relief="flat",
            borderwidth=0,
        )
        self.wizard_log_text.grid(row=0, column=0, sticky="ew", padx=2, pady=2)

        footer = ttk.Frame(wizard, style="Panel.TFrame")
        footer.grid(row=3, column=0, sticky="ew", pady=(2, 0))
        footer.columnconfigure(0, weight=1)
        footer.columnconfigure(1, weight=1)
        footer.columnconfigure(2, weight=1)

        self.wizard_prev_button = ttk.Button(footer, text="◀ Prev", command=self.wizard_prev_step, style="Small.TButton")
        self.wizard_prev_button.grid(row=0, column=0, sticky="w")
        self.wizard_next_button = ttk.Button(footer, text="Next ▶", command=self.wizard_next_step, style="Primary.TButton")
        self.wizard_next_button.grid(row=0, column=2, sticky="e")
        self.wizard_finish_button = ttk.Button(footer, text="Finish Setup", command=self.finish_initial_wizard, style="Primary.TButton")
        self.wizard_finish_button.grid(row=0, column=2, sticky="e")

        self.append_wizard_log("[READY] Zero-to-Hero Setup Wizard ready")
        self.render_wizard_step()

    def render_wizard_step(self):
        if not self.wizard_step_body:
            return
        for child in self.wizard_step_body.winfo_children():
            child.destroy()
        titles = [
            "1/4 · System Tools",
            "2/4 · GitHub Clone",
            "3/4 · Environment Files",
            "4/4 · Install Dependencies",
        ]
        self.wizard_step_title_var.set(titles[self.wizard_current_step])
        builders = [
            self.build_wizard_step_tools,
            self.build_wizard_step_clone,
            self.build_wizard_step_env,
            self.build_wizard_step_install,
        ]
        builders[self.wizard_current_step](self.wizard_step_body)
        self.update_wizard_nav_buttons()

    def update_wizard_nav_buttons(self):
        if self.wizard_prev_button:
            self.wizard_prev_button.configure(state="normal" if self.wizard_current_step > 0 else "disabled")
        if self.wizard_next_button:
            if self.wizard_current_step >= 3:
                self.wizard_next_button.grid_remove()
            else:
                self.wizard_next_button.grid()
        if self.wizard_finish_button:
            if self.wizard_current_step >= 3:
                self.wizard_finish_button.grid()
            else:
                self.wizard_finish_button.grid_remove()

    def wizard_prev_step(self):
        if self.wizard_current_step > 0:
            self.wizard_current_step -= 1
            self.render_wizard_step()

    def wizard_next_step(self):
        if self.wizard_current_step < 3:
            self.wizard_current_step += 1
            self.render_wizard_step()

    def build_wizard_step_tools(self, parent):
        shell = ttk.Frame(parent, style="Panel.TFrame")
        shell.grid(row=0, column=0, sticky="nsew")
        shell.columnconfigure(0, weight=1)
        shell.rowconfigure(0, weight=1)
        frame = ttk.LabelFrame(shell, text="Step 1 · System Tools", style="Global.TLabelframe")
        frame.grid(row=0, column=0, sticky="nsew", padx=0, pady=0)
        frame.columnconfigure(1, weight=1)

        ttk.Label(frame, text="Check required tools. Install only missing items.", style="CardSubtle.TLabel").grid(row=0, column=0, columnspan=3, sticky="w", pady=(0, 8))

        self.wizard_tool_rows = {}
        tools = [
            ("python", "Python", find_python_status, self.install_python_tool),
            ("node", "Node.js / npm", find_node_status, self.install_node_tool),
            ("cloudflared", "Cloudflare Tunnel", find_cloudflared_status, self.install_cloudflared_tool),
            ("git", "Git", find_git_status, self.install_git_tool),
        ]
        for row_index, (key, label, checker, installer) in enumerate(tools, start=1):
            ttk.Label(frame, text=label, width=20, style="CardSubtle.TLabel").grid(row=row_index, column=0, sticky="w", padx=2, pady=4)
            status_label = ttk.Label(frame, text="checking...", style="Warn.TLabel")
            status_label.grid(row=row_index, column=1, sticky="ew", padx=2, pady=4)
            install_button = ttk.Button(frame, text="Install", command=installer, style="Small.TButton")
            install_button.grid(row=row_index, column=2, sticky="e", padx=2, pady=4)
            self.wizard_tool_rows[key] = (status_label, install_button, checker)

        ttk.Button(frame, text="Refresh Tool Status", command=self.refresh_wizard_tool_status, style="Primary.TButton").grid(row=len(tools)+1, column=0, columnspan=3, sticky="ew", padx=2, pady=(10, 0))
        self.refresh_wizard_tool_status()

    def build_wizard_step_clone(self, parent):
        shell = ttk.Frame(parent, style="Panel.TFrame")
        shell.grid(row=0, column=0, sticky="nsew")
        shell.columnconfigure(0, weight=1)
        shell.rowconfigure(0, weight=1)
        frame = ttk.LabelFrame(shell, text="Step 2 · GitHub Clone", style="Global.TLabelframe")
        frame.grid(row=0, column=0, sticky="nsew")
        frame.columnconfigure(1, weight=1)

        ttk.Label(frame, text="Clone the project or reuse an existing project folder.", style="CardSubtle.TLabel").grid(row=0, column=0, columnspan=3, sticky="w", pady=(0, 8))
        ttk.Label(frame, text="Target Folder", width=14, style="CardSubtle.TLabel").grid(row=1, column=0, sticky="w", padx=2, pady=5)
        ttk.Entry(frame, textvariable=self.vars["wizard_target_dir"]).grid(row=1, column=1, sticky="ew", padx=2, pady=5)
        ttk.Button(frame, text="Browse", command=self.select_wizard_target_dir, style="Small.TButton").grid(row=1, column=2, sticky="ew", padx=2, pady=5)

        ttk.Label(frame, text="Repository URL", width=14, style="CardSubtle.TLabel").grid(row=2, column=0, sticky="w", padx=2, pady=5)
        ttk.Entry(frame, textvariable=self.vars["wizard_repo_url"]).grid(row=2, column=1, columnspan=2, sticky="ew", padx=2, pady=5)

        ttk.Button(frame, text="Clone Project", command=self.clone_project_from_wizard, style="Primary.TButton").grid(row=3, column=0, columnspan=3, sticky="ew", padx=2, pady=(12, 0), ipady=3)

    def build_wizard_step_env(self, parent):
        frame = ttk.LabelFrame(parent, text="Step 3 · Environment Files", style="Global.TLabelframe")
        frame.grid(row=0, column=0, sticky="nsew")
        frame.columnconfigure(0, weight=1)
        frame.columnconfigure(1, weight=1)
        frame.rowconfigure(1, weight=1)

        ttk.Label(frame, text="Create backend/.env and frontend/.env from editable templates.", style="CardSubtle.TLabel").grid(row=0, column=0, columnspan=2, sticky="w", pady=(0, 4))

        backend_box = ttk.LabelFrame(frame, text="Backend .env", style="Card.TLabelframe")
        backend_box.grid(row=1, column=0, sticky="nsew", padx=(0, 3), pady=0)
        backend_box.rowconfigure(0, weight=1)
        backend_box.columnconfigure(0, weight=1)
        self.wizard_backend_env_textbox = tk.Text(backend_box, height=13, wrap="none", font=("Menlo" if get_system_name() == "Darwin" else "Consolas", 9), bg="#FFFFFF", fg=self.ui_text, relief="solid", borderwidth=1)
        self.wizard_backend_env_textbox.grid(row=0, column=0, sticky="nsew")
        self.wizard_backend_env_textbox.insert("1.0", self.wizard_backend_env_text or BACKEND_ENV_TEMPLATE)

        frontend_box = ttk.LabelFrame(frame, text="Service Frontend .env", style="Card.TLabelframe")
        frontend_box.grid(row=1, column=1, sticky="nsew", padx=(3, 0), pady=0)
        frontend_box.rowconfigure(0, weight=1)
        frontend_box.columnconfigure(0, weight=1)
        self.wizard_frontend_env_textbox = tk.Text(frontend_box, height=13, wrap="none", font=("Menlo" if get_system_name() == "Darwin" else "Consolas", 9), bg="#FFFFFF", fg=self.ui_text, relief="solid", borderwidth=1)
        self.wizard_frontend_env_textbox.grid(row=0, column=0, sticky="nsew")
        self.wizard_frontend_env_textbox.insert("1.0", self.wizard_frontend_env_text or FRONTEND_ENV_TEMPLATE)

        ttk.Button(frame, text="Save .env Files", command=self.save_wizard_env_file, style="Primary.TButton").grid(row=2, column=0, columnspan=2, sticky="ew", padx=2, pady=(6, 0), ipady=2)

    def build_wizard_step_install(self, parent):
        shell = ttk.Frame(parent, style="Panel.TFrame")
        shell.grid(row=0, column=0, sticky="nsew")
        shell.columnconfigure(0, weight=1)
        shell.rowconfigure(0, weight=1)
        frame = ttk.LabelFrame(shell, text="Step 4 · Install Dependencies", style="Global.TLabelframe")
        frame.grid(row=0, column=0, sticky="nsew")
        frame.columnconfigure(0, weight=1)
        ttk.Label(frame, text="Install backend/frontend/admin dependencies using the configured project paths.", style="CardSubtle.TLabel").grid(row=0, column=0, sticky="w", pady=(0, 10))
        ttk.Button(frame, text="Install All Packages", command=self.install_all_dependencies, style="Primary.TButton").grid(row=1, column=0, sticky="ew", ipady=5)
        ttk.Label(frame, text="After installation, click Finish Setup to enter the main console.", style="CardSubtle.TLabel").grid(row=2, column=0, sticky="w", pady=(10, 0))

    def refresh_wizard_tool_status(self):
        if not hasattr(self, "wizard_tool_rows"):
            return
        for key, (label, button, checker) in self.wizard_tool_rows.items():
            status = checker()
            if status["ok"]:
                label.configure(text=f"정상 - {status['message']}", style="Good.TLabel")
                button.configure(state="disabled")
            else:
                label.configure(text=f"확인 필요 - {status['message']}", style="Bad.TLabel")
                button.configure(state="normal")
        self.append_wizard_log("[CHECK] 필수 도구 점검 완료")

    def append_wizard_log(self, message):
        if not hasattr(self, "wizard_log_text") or self.wizard_log_text is None:
            self.append_log("system", message)
            return
        self.wizard_log_text.configure(state="normal")
        self.wizard_log_text.insert("end", message + "\n")
        self.wizard_log_text.see("end")
        self.wizard_log_text.configure(state="normal")

    def select_wizard_target_dir(self):
        selected = filedialog.askdirectory()
        if selected:
            self.vars["wizard_target_dir"].set(selected)
            self.save_current_config(show_popup=False)

    def get_wizard_project_root(self):
        target = Path(self.vars["wizard_target_dir"].get().strip()).expanduser()
        return target

    def clone_project_from_wizard(self):
        repo_url = self.vars["wizard_repo_url"].get().strip()
        target = self.get_wizard_project_root()

        if not repo_url:
            messagebox.showwarning("Repository URL 필요", "GitHub Repository URL을 입력하세요.")
            return

        if not command_exists("git"):
            messagebox.showwarning("Git 필요", "Git이 설치되어 있지 않습니다. 1단계에서 Git을 먼저 설치하세요.")
            return

        if target.exists() and any(target.iterdir()) and not ((target / "backend").exists() and (target / "frontend").exists()):
            if not messagebox.askyesno("대상 폴더 확인", f"대상 폴더가 비어 있지 않습니다. 계속 진행할까요?\n\n{target}"):
                return

        if (target / "backend").exists() and (target / "frontend").exists():
            self.append_wizard_log(f"[CLONE] 이미 프로젝트 구조가 감지되어 clone을 생략합니다: {target}")
            self.apply_project_paths_from_root(target)
            return

        target.parent.mkdir(parents=True, exist_ok=True)
        command = f"git clone {quote_path(repo_url)} {quote_path(target)}"
        self.save_current_config(show_popup=False)
        self.start_wizard_command("GitHub 프로젝트 다운로드", command, str(target.parent), on_done=lambda ok: self.apply_project_paths_from_root(target) if ok else None)

    def start_wizard_command(self, title, command, cwd, on_done=None):
        self.append_wizard_log("")
        self.append_wizard_log(f"========== {title} ==========")
        self.append_wizard_log(f"$ cd {cwd}")
        self.append_wizard_log(f"$ {command}")

        def worker():
            ok = False
            try:
                process = subprocess.Popen(
                    command,
                    cwd=cwd,
                    shell=True,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.STDOUT,
                    stdin=subprocess.DEVNULL,
                    text=True,
                    encoding="utf-8",
                    errors="replace",
                    env=self.build_clean_env(),
                )
                if process.stdout:
                    for line in process.stdout:
                        self.root.after(0, self.append_wizard_log, line.rstrip("\n"))
                return_code = process.wait()
                ok = return_code == 0
                self.root.after(0, self.append_wizard_log, f"[DONE] exit={return_code}")
            except Exception as e:
                self.root.after(0, self.append_wizard_log, f"[ERROR] {e}")
            finally:
                if on_done:
                    self.root.after(0, lambda: on_done(ok))

        threading.Thread(target=worker, daemon=True).start()

    def apply_project_paths_from_root(self, root):
        root = Path(root).expanduser()
        self.vars["backend_path"].set(str(root / "backend"))
        self.vars["frontend_path"].set(str(root / "frontend"))
        self.vars["admin_path"].set(str(root / "admin"))
        self.reset_auto_commands(show_popup=False)
        self.refresh_all_summaries()
        self.save_current_config(show_popup=False)
        self.append_wizard_log(f"[PATH] 프로젝트 경로 자동 반영: {root}")

    def save_wizard_env_file(self):
        root = self.get_wizard_project_root()
        backend_text = self.wizard_backend_env_textbox.get("1.0", "end").strip() if hasattr(self, "wizard_backend_env_textbox") else (self.wizard_backend_env_text or BACKEND_ENV_TEMPLATE).strip()
        frontend_text = self.wizard_frontend_env_textbox.get("1.0", "end").strip() if hasattr(self, "wizard_frontend_env_textbox") else (self.wizard_frontend_env_text or FRONTEND_ENV_TEMPLATE).strip()
        self.wizard_backend_env_text = backend_text
        self.wizard_frontend_env_text = frontend_text
        self.wizard_env_text = backend_text
        self.config["wizard_backend_env_text"] = backend_text
        self.config["wizard_frontend_env_text"] = frontend_text
        self.config["wizard_env_text"] = backend_text

        backend_dir = root / "backend"
        frontend_dir = root / "frontend"
        if not backend_dir.exists():
            backend_dir = Path(self.vars["backend_path"].get().strip()).expanduser()
        if not frontend_dir.exists():
            frontend_dir = Path(self.vars["frontend_path"].get().strip()).expanduser()

        missing = []
        if not backend_dir.exists():
            missing.append("backend")
        if not frontend_dir.exists():
            missing.append("frontend")
        if missing:
            messagebox.showwarning("프로젝트 경로 필요", f"다음 폴더를 찾지 못했습니다: {', '.join(missing)}\n먼저 프로젝트 경로를 설정하거나 clone을 완료하세요.")
            return

        backend_env = backend_dir / ".env"
        frontend_env = frontend_dir / ".env"
        overwrite_targets = [p for p in [backend_env, frontend_env] if p.exists()]
        if overwrite_targets:
            listed = "\n".join(str(p) for p in overwrite_targets)
            if not messagebox.askyesno(".env 덮어쓰기", f"이미 .env 파일이 있습니다. 덮어쓸까요?\n\n{listed}"):
                return

        backend_env.write_text(backend_text + ("\n" if backend_text else ""), encoding="utf-8")
        frontend_env.write_text(frontend_text + ("\n" if frontend_text else ""), encoding="utf-8")
        self.save_current_config(show_popup=False)
        self.append_wizard_log(f"[ENV] backend .env saved: {backend_env}")
        self.append_wizard_log(f"[ENV] frontend .env saved: {frontend_env}")
        messagebox.showinfo("저장 완료", f".env 파일 2개를 저장했습니다.\n\n{backend_env}\n{frontend_env}")

    def finish_initial_wizard(self):
        self.save_current_config(show_popup=False)
        self.show_main_console()

    def build_main_console_view(self, parent):
        # Vertical rhythm: overview / logs / tabs. Heights are fixed enough for 14-inch screens.
        self.global_status_frame = self.build_global_system_status(parent)
        self.global_status_frame.pack(fill="x", pady=(0, 4))

        log_holder = ttk.Frame(parent, height=270, style="Panel.TFrame")
        log_holder.pack(fill="x", expand=False, pady=(0, 4))
        log_holder.pack_propagate(False)
        self.build_console_panel(log_holder)

        notebook_holder = ttk.Frame(parent, style="Panel.TFrame")
        notebook_holder.pack(fill="both", expand=True)
        self.control_notebook = ttk.Notebook(notebook_holder, style="Main.TNotebook")
        self.control_notebook.pack(fill="both", expand=True)

        dashboard_tab = ttk.Frame(self.control_notebook, padding=(4, 4), style="Panel.TFrame")
        control_tab = ttk.Frame(self.control_notebook, padding=(4, 4), style="Panel.TFrame")
        settings_tab = ttk.Frame(self.control_notebook, padding=(4, 4), style="Panel.TFrame")

        self.control_notebook.add(dashboard_tab, text="Dashboard")
        self.control_notebook.add(control_tab, text="Service Control")
        self.control_notebook.add(settings_tab, text="Environment & Tunneling")

        self.build_dashboard_tab(dashboard_tab)
        self.build_control_tower_tab(control_tab)
        self.build_external_settings_tab(settings_tab)
        self.start_traffic_monitor()
        self.update_all_server_toggle_buttons()
        self.update_tunnel_toggle_buttons()

    def build_global_system_status(self, parent):
        frame = ttk.LabelFrame(parent, text="System Overview", style="Global.TLabelframe")
        frame.columnconfigure(0, weight=40, uniform="overview")
        frame.columnconfigure(1, weight=60, uniform="overview")
        frame.rowconfigure(0, weight=1)

        left = ttk.Frame(frame, style="CardBody.TFrame")
        left.grid(row=0, column=0, sticky="nsew", padx=(0, 5), pady=0)
        right = ttk.Frame(frame, style="CardBody.TFrame")
        right.grid(row=0, column=1, sticky="nsew", padx=(5, 0), pady=0)
        left.columnconfigure(0, weight=1)
        left.rowconfigure(1, weight=1)
        left.rowconfigure(3, weight=1)
        right.columnconfigure(0, weight=1)
        right.rowconfigure(1, weight=1)

        local_header = ttk.Frame(left, style="CardBody.TFrame")
        local_header.grid(row=0, column=0, sticky="ew", pady=(0, 1))
        ttk.Label(local_header, text="Local URLs", style="CardStatus.TLabel").pack(side="left")
        ttk.Button(local_header, text="Refresh IP", command=self.refresh_ip, style="Compact.TButton").pack(side="right")
        self.global_local_text = tk.Text(left, height=3, wrap="word", font=(self.font_family, 11, "bold"), bg=self.ui_log_bg, fg=self.ui_log_fg, relief="solid", borderwidth=1)
        self.global_local_text.grid(row=1, column=0, sticky="nsew", pady=(0, 4))
        self.global_local_text.configure(state="disabled")

        tunnel_header = ttk.Frame(left, style="CardBody.TFrame")
        tunnel_header.grid(row=2, column=0, sticky="ew", pady=(0, 1))
        ttk.Label(tunnel_header, text="Cloudflare URLs", style="CardStatus.TLabel").pack(side="left")
        ttk.Label(tunnel_header, text="drag text to copy", style="CardSubtle.TLabel").pack(side="right")
        self.cloudflare_text = tk.Text(left, height=3, wrap="word", font=(self.font_family, 11, "bold"), bg=self.ui_log_bg, fg=self.ui_log_fg, relief="solid", borderwidth=1)
        self.cloudflare_text.grid(row=3, column=0, sticky="nsew")
        self.cloudflare_text.configure(state="disabled")

        monitor_header = ttk.Frame(right, style="CardBody.TFrame")
        monitor_header.grid(row=0, column=0, sticky="ew", pady=(0, 1))
        ttk.Label(monitor_header, text="System Monitor", style="CardStatus.TLabel").pack(side="left")
        self.traffic_status_var = tk.StringVar(value="monitor initializing")
        ttk.Label(monitor_header, textvariable=self.traffic_status_var, style="CardSubtle.TLabel").pack(side="right")
        self.traffic_canvas = tk.Canvas(right, height=138, highlightthickness=0, bg=self.ui_bg)
        self.traffic_canvas.grid(row=1, column=0, sticky="nsew")
        if psutil is None:
            self.traffic_status_var.set("psutil unavailable")

        self.share_text = self.global_local_text
        self.refresh_share_text()
        return frame

    def build_dashboard_tab(self, parent):
        parent.columnconfigure(0, weight=1, uniform="dash")
        parent.columnconfigure(1, weight=1, uniform="dash")
        parent.rowconfigure(0, weight=1, uniform="dashrow")
        parent.rowconfigure(1, weight=1, uniform="dashrow")

        summary = ttk.LabelFrame(parent, text="System Status", style="Card.TLabelframe")
        summary.grid(row=0, column=0, sticky="nsew", padx=(0, 4), pady=(0, 4))
        summary.columnconfigure(0, weight=1)
        summary.rowconfigure(3, weight=1)
        for idx, key in enumerate(["backend", "frontend", "admin"]):
            row = ttk.Frame(summary, style="CardBody.TFrame")
            row.grid(row=idx, column=0, sticky="ew", padx=2, pady=3)
            row.columnconfigure(2, weight=1)
            ttk.Label(row, text=SERVER_INFO[key]["label"], width=18, style="CardSubtle.TLabel").grid(row=0, column=0, sticky="w")
            ttk.Label(row, textvariable=self.server_status_vars.setdefault(key, tk.StringVar(value="중지됨")), style="Good.TLabel").grid(row=0, column=1, sticky="w", padx=(8, 8))
            ttk.Label(row, textvariable=self.path_summary_vars[key], style="CardSubtle.TLabel").grid(row=0, column=2, sticky="e")

        settings = ttk.LabelFrame(parent, text="Global Settings", style="Card.TLabelframe")
        settings.grid(row=0, column=1, sticky="nsew", padx=(4, 0), pady=(0, 4))
        for col in range(3):
            settings.columnconfigure(col, weight=1)
        settings.rowconfigure(0, weight=0)
        settings.rowconfigure(1, weight=0)
        settings.rowconfigure(2, weight=1)
        buttons = [
            ("Auto Detect Paths", self.auto_set_project_paths),
            ("Refresh Commands", lambda: self.reset_auto_commands(show_popup=True)),
            ("Open Local URLs", self.open_all_local_urls),
            ("Environment Settings", self.open_tool_settings_window),
            ("Cloudflare Settings", self.open_cloudflare_settings_window),
            ("Save Settings", self.save_current_config),
        ]
        for i, (label, cmd) in enumerate(buttons):
            ttk.Button(settings, text=label, command=cmd, style="Small.TButton").grid(row=i//3, column=i%3, sticky="ew", padx=2, pady=3, ipady=3)
        ttk.Frame(settings, style="CardBody.TFrame").grid(row=2, column=0, columnspan=3, sticky="nsew")

        tunnel = ttk.LabelFrame(parent, text="Tunnel Batch", style="Card.TLabelframe")
        tunnel.grid(row=1, column=0, sticky="nsew", padx=(0, 4), pady=(4, 0))
        for col in range(2):
            tunnel.columnconfigure(col, weight=1)
        tunnel.rowconfigure(0, weight=0)
        tunnel.rowconfigure(1, weight=0)
        tunnel.rowconfigure(2, weight=1)
        self.all_tunnel_toggle_button = ttk.Button(tunnel, text="▶️ Start All Tunnels", command=self.toggle_all_tunnels, style="Primary.TButton")
        self.all_tunnel_toggle_button.grid(row=0, column=0, columnspan=2, sticky="ew", padx=2, pady=(3, 4), ipady=5)
        ttk.Button(tunnel, text="Cloudflare Wizard", command=self.open_cloudflare_wizard_window, style="Small.TButton").grid(row=1, column=0, sticky="ew", padx=2, pady=2, ipady=3)
        ttk.Button(tunnel, text="Copy Tunnel URLs", command=self.copy_cloudflare_urls, style="Small.TButton").grid(row=1, column=1, sticky="ew", padx=2, pady=2, ipady=3)
        ttk.Frame(tunnel, style="CardBody.TFrame").grid(row=2, column=0, columnspan=2, sticky="nsew")

        server_batch = ttk.LabelFrame(parent, text="Server Batch", style="Card.TLabelframe")
        server_batch.grid(row=1, column=1, sticky="nsew", padx=(4, 0), pady=(4, 0))
        for col in range(2):
            server_batch.columnconfigure(col, weight=1)
        server_batch.rowconfigure(0, weight=0)
        server_batch.rowconfigure(1, weight=0)
        server_batch.rowconfigure(2, weight=1)
        self.all_server_toggle_button = ttk.Button(server_batch, text="▶️ Start All Servers", command=self.toggle_all_servers, style="Primary.TButton")
        self.all_server_toggle_button.grid(row=0, column=0, columnspan=2, sticky="ew", padx=2, pady=(3, 4), ipady=5)
        ttk.Button(server_batch, text="Install All Deps", command=self.install_all_dependencies, style="Small.TButton").grid(row=1, column=0, sticky="ew", padx=2, pady=2, ipady=3)
        ttk.Button(server_batch, text="Auto Cmd", command=lambda: self.reset_auto_commands(show_popup=True), style="Small.TButton").grid(row=1, column=1, sticky="ew", padx=2, pady=2, ipady=3)
        ttk.Frame(server_batch, style="CardBody.TFrame").grid(row=2, column=0, columnspan=2, sticky="nsew")

        self.update_all_runtime_toggle_buttons()

    def create_traffic_monitor_card(self, parent):
        """이전 버전 호환용. 실제 모니터는 System Overview에 통합되어 있다."""
        frame = ttk.LabelFrame(parent, text="System Monitor", style="Card.TLabelframe")
        if not hasattr(self, "traffic_status_var"):
            self.traffic_status_var = tk.StringVar(value="waiting for monitor data")
        ttk.Label(frame, textvariable=self.traffic_status_var, style="Status.TLabel").pack(anchor="w", pady=(0, 4))
        self.traffic_canvas = tk.Canvas(frame, height=110, highlightthickness=1, highlightbackground="#D0D7DE")
        self.traffic_canvas.pack(fill="both", expand=True)
        if psutil is None:
            self.traffic_status_var.set("psutil not installed - run: python3 -m pip install psutil")
        return frame

    def populate_batch_controls(self, parent):
        for i in range(2):
            parent.columnconfigure(i, weight=1)
        self.all_server_toggle_button = ttk.Button(parent, text="▶️ Start All Servers", command=self.toggle_all_servers, style="Primary.TButton")
        self.all_server_toggle_button.grid(row=0, column=0, columnspan=2, sticky="ew", padx=4, pady=4)
        self.all_tunnel_toggle_button = ttk.Button(parent, text="▶️ Start All Tunnels", command=self.toggle_all_tunnels, style="Primary.TButton")
        self.all_tunnel_toggle_button.grid(row=1, column=0, columnspan=2, sticky="ew", padx=4, pady=4)
        ttk.Button(parent, text="Install All Deps", command=self.install_all_dependencies, style="Small.TButton").grid(row=2, column=0, sticky="ew", padx=4, pady=4)
        ttk.Button(parent, text="Auto Detect Paths", command=self.auto_set_project_paths, style="Small.TButton").grid(row=2, column=1, sticky="ew", padx=4, pady=4)
        ttk.Button(parent, text="Refresh Commands", command=lambda: self.reset_auto_commands(show_popup=True), style="Small.TButton").grid(row=3, column=0, sticky="ew", padx=4, pady=4)
        ttk.Button(parent, text="Save Settings", command=self.save_current_config, style="Small.TButton").grid(row=3, column=1, sticky="ew", padx=4, pady=4)
        self.update_all_runtime_toggle_buttons()

    def build_control_tower_tab(self, parent):
        parent.columnconfigure(0, weight=1, uniform="servers")
        parent.columnconfigure(1, weight=1, uniform="servers")
        parent.columnconfigure(2, weight=1, uniform="servers")
        parent.rowconfigure(0, weight=1)
        self.create_server_card(parent, "backend").grid(row=0, column=0, sticky="nsew", padx=(0, 4), pady=0)
        self.create_server_card(parent, "frontend").grid(row=0, column=1, sticky="nsew", padx=4, pady=0)
        self.create_server_card(parent, "admin").grid(row=0, column=2, sticky="nsew", padx=(4, 0), pady=0)

    def build_external_settings_tab(self, parent):
        parent.columnconfigure(0, weight=1)
        parent.rowconfigure(0, weight=1)
        tool = self.create_tool_card(parent)
        tool.grid(row=0, column=0, sticky="nsew", padx=0, pady=0)

    def build_menu_area(self, parent):
        """이전 버전 호환용. 실제 메인 화면은 build_main_console_view에서 Notebook 구조로 구성한다."""
        parent.columnconfigure(0, weight=1)
        parent.columnconfigure(1, weight=1)
        parent.columnconfigure(2, weight=1)
        parent.rowconfigure(0, weight=1)
        parent.rowconfigure(1, weight=1)

        self.create_access_card(parent).grid(row=0, column=0, sticky="nsew", padx=(0, 6), pady=(0, 6))
        self.create_server_card(parent, "backend").grid(row=0, column=1, sticky="nsew", padx=6, pady=(0, 6))
        self.create_tool_card(parent).grid(row=0, column=2, sticky="nsew", padx=(6, 0), pady=(0, 6))
        self.create_action_card(parent).grid(row=1, column=0, sticky="nsew", padx=(0, 6), pady=(6, 0))
        self.create_server_card(parent, "frontend").grid(row=1, column=1, sticky="nsew", padx=6, pady=(6, 0))
        self.create_server_card(parent, "admin").grid(row=1, column=2, sticky="nsew", padx=(6, 0), pady=(6, 0))

    def create_access_card(self, parent):
        frame = ttk.LabelFrame(parent, text="System Overview", style="Card.TLabelframe")

        ip_row = ttk.Frame(frame)
        ip_row.pack(fill="x", pady=(0, 4))

        ttk.Label(ip_row, text="IPv4", width=6).pack(side="left")
        ttk.Entry(ip_row, textvariable=self.ip_var).pack(side="left", fill="x", expand=True, padx=5)
        ttk.Button(ip_row, text="새로고침", command=self.refresh_ip, style="Small.TButton").pack(side="left")

        self.share_text = tk.Text(frame, height=3, wrap="word", font=(self.font_family, 9), relief="solid", borderwidth=1)
        self.share_text.pack(fill="both", expand=True, pady=(2, 4))
        self.share_text.configure(state="disabled")

        ttk.Label(frame, text="Cloudflare Public URLs", style="Subtle.TLabel").pack(anchor="w")
        self.cloudflare_text = tk.Text(frame, height=3, wrap="word", font=(self.font_family, 9), relief="solid", borderwidth=1)
        self.cloudflare_text.pack(fill="both", expand=True, pady=(2, 4))
        self.cloudflare_text.configure(state="disabled")

        button_row = ttk.Frame(frame)
        button_row.pack(fill="x")
        ttk.Button(button_row, text="📋 로컬 주소 복사", command=self.copy_share_info, style="Small.TButton").pack(side="left", fill="x", expand=True, padx=(0, 3))
        ttk.Button(button_row, text="🔗 외부 터널 주소 복사", command=self.copy_cloudflare_urls, style="Small.TButton").pack(side="left", fill="x", expand=True, padx=3)
        ttk.Button(button_row, text="로컬 Open", command=self.open_all_local_urls, style="Small.TButton").pack(side="left", fill="x", expand=True, padx=(3, 0))

        self.refresh_share_text()
        return frame

    def create_action_card(self, parent):
        frame = ttk.LabelFrame(parent, text="Server Batch", style="Card.TLabelframe")
        self.populate_batch_controls(frame)

        tunnel_box = ttk.LabelFrame(frame, text="Tunnel Batch", style="Card.TLabelframe")
        tunnel_box.grid(row=3, column=0, columnspan=2, sticky="ew", padx=4, pady=(8, 4))
        tunnel_box.columnconfigure(0, weight=1)
        tunnel_box.columnconfigure(1, weight=1)
        ttk.Button(tunnel_box, text="Start All Tunnels", command=self.start_all_cloudflare_tunnels, style="Primary.TButton").grid(row=0, column=0, sticky="ew", padx=4, pady=4)
        ttk.Button(tunnel_box, text="Stop All Tunnels", command=self.stop_cloudflare_tunnels, style="Danger.TButton").grid(row=0, column=1, sticky="ew", padx=4, pady=4)
        return frame

    def create_tool_card(self, parent):
        frame = ttk.LabelFrame(parent, text="Environment & Tunneling", style="Card.TLabelframe")
        for i in range(4):
            frame.columnconfigure(i, weight=1, uniform="env")
        frame.rowconfigure(0, weight=0)
        frame.rowconfigure(1, weight=0)
        frame.rowconfigure(2, weight=0)
        frame.rowconfigure(3, weight=0)
        frame.rowconfigure(4, weight=1)

        ttk.Label(frame, text="Toolchain", style="CardStatus.TLabel").grid(row=0, column=0, sticky="w", padx=2, pady=(0, 2))
        ttk.Label(frame, textvariable=self.tool_status_var, style="CardSubtle.TLabel").grid(row=0, column=1, columnspan=3, sticky="w", padx=2, pady=(0, 2))

        ttk.Button(frame, text="Check Status", command=lambda: self.check_developer_tools(show_popup=True), style="Small.TButton").grid(row=1, column=0, sticky="ew", padx=2, pady=2, ipady=2)
        ttk.Button(frame, text="Tool Settings", command=self.open_tool_settings_window, style="Small.TButton").grid(row=1, column=1, sticky="ew", padx=2, pady=2, ipady=2)
        ttk.Button(frame, text="⚙️ Cloudflare Settings", command=self.open_cloudflare_settings_window, style="Small.TButton").grid(row=1, column=2, sticky="ew", padx=2, pady=2, ipady=2)
        ttk.Button(frame, text="Zero-to-Hero Wizard", command=self.show_initial_wizard, style="Primary.TButton").grid(row=1, column=3, sticky="ew", padx=2, pady=2, ipady=2)

        self.named_tunnel_toggle_button = ttk.Button(frame, text="▶️ Start Named Tunnel", command=self.toggle_named_tunnel, style="Primary.TButton")
        self.named_tunnel_toggle_button.grid(row=2, column=0, columnspan=2, sticky="ew", padx=2, pady=3, ipady=3)
        self.quick_tunnel_toggle_button = ttk.Button(frame, text="⚡ Start Quick Tunnels", command=self.toggle_quick_tunnels, style="Primary.TButton")
        self.quick_tunnel_toggle_button.grid(row=2, column=2, columnspan=2, sticky="ew", padx=2, pady=3, ipady=3)

        ttk.Button(frame, text="Cloudflare Wizard", command=self.open_cloudflare_wizard_window, style="Small.TButton").grid(row=3, column=0, sticky="ew", padx=2, pady=2, ipady=2)
        ttk.Button(frame, text="Open Config Folder", command=self.open_cloudflare_config_folder, style="Small.TButton").grid(row=3, column=1, sticky="ew", padx=2, pady=2, ipady=2)
        ttk.Button(frame, text="Copy Tunnel URLs", command=self.copy_cloudflare_urls, style="Small.TButton").grid(row=3, column=2, sticky="ew", padx=2, pady=2, ipady=2)
        ttk.Button(frame, text="Save Settings", command=self.save_current_config, style="Small.TButton").grid(row=3, column=3, sticky="ew", padx=2, pady=2, ipady=2)
        ttk.Frame(frame, style="CardBody.TFrame").grid(row=4, column=0, columnspan=4, sticky="nsew")

        self.update_tunnel_toggle_buttons()
        return frame

    def create_server_card(self, parent, server_key):
        info = SERVER_INFO[server_key]
        frame = ttk.LabelFrame(parent, text=f"{info['label']} · {info['port']}", style="Card.TLabelframe")
        frame.columnconfigure(1, weight=1)
        frame.columnconfigure(2, weight=0)
        frame.rowconfigure(99, weight=1)

        if server_key not in self.server_status_vars:
            self.server_status_vars[server_key] = tk.StringVar(value="중지됨")
        status_var = self.server_status_vars[server_key]

        path_key = info["path_key"]
        install_key = info["install_cmd_key"]
        cmd_key = info["cmd_key"]

        row = 0
        ttk.Label(frame, text="Status", width=7, style="CardSubtle.TLabel").grid(row=row, column=0, sticky="w", padx=1, pady=1)
        ttk.Label(frame, textvariable=status_var, style="CardStatus.TLabel").grid(row=row, column=1, sticky="w", padx=1, pady=1)
        ttk.Button(frame, text="Open", command=lambda key=server_key: webbrowser.open(SERVER_INFO[key]["local_url"]), style="Compact.TButton").grid(row=row, column=2, sticky="ew", padx=1, pady=1)
        row += 1

        ttk.Label(frame, text="URL", width=7, style="CardSubtle.TLabel").grid(row=row, column=0, sticky="w", padx=1, pady=1)
        ttk.Label(frame, text=info["local_url"], style="CardSubtle.TLabel").grid(row=row, column=1, columnspan=2, sticky="w", padx=1, pady=1)
        row += 1

        ttk.Label(frame, text="Path", width=7, style="CardSubtle.TLabel").grid(row=row, column=0, sticky="w", padx=1, pady=1)
        ttk.Entry(frame, textvariable=self.vars[path_key]).grid(row=row, column=1, sticky="ew", padx=1, pady=1)
        ttk.Button(frame, text="Browse", command=lambda k=path_key, s=server_key: [self.select_folder(k), self.auto_update_commands_for_server(s)], style="Compact.TButton").grid(row=row, column=2, sticky="ew", padx=1, pady=1)
        row += 1

        ttk.Label(frame, text="Install", width=7, style="CardSubtle.TLabel").grid(row=row, column=0, sticky="w", padx=1, pady=1)
        ttk.Entry(frame, textvariable=self.vars[install_key]).grid(row=row, column=1, columnspan=2, sticky="ew", padx=1, pady=1)
        row += 1

        ttk.Label(frame, text="Run", width=7, style="CardSubtle.TLabel").grid(row=row, column=0, sticky="w", padx=1, pady=1)
        ttk.Entry(frame, textvariable=self.vars[cmd_key]).grid(row=row, column=1, columnspan=2, sticky="ew", padx=1, pady=1)
        row += 1

        if server_key == "backend":
            ttk.Label(frame, text=".venv", width=7, style="CardSubtle.TLabel").grid(row=row, column=0, sticky="w", padx=1, pady=1)
            ttk.Entry(frame, textvariable=self.vars["backend_create_venv_cmd"]).grid(row=row, column=1, columnspan=2, sticky="ew", padx=1, pady=1)
            row += 1

        spacer = ttk.Frame(frame, style="CardBody.TFrame")
        spacer.grid(row=99, column=0, columnspan=3, sticky="nsew")

        button_row = ttk.Frame(frame, style="CardBody.TFrame")
        button_row.grid(row=100, column=0, columnspan=3, sticky="ew", padx=1, pady=(3, 0))
        for i in range(4):
            button_row.columnconfigure(i, weight=1)

        if server_key == "backend":
            ttk.Button(button_row, text="Create .venv", command=self.create_backend_venv, style="Compact.TButton").grid(row=0, column=0, sticky="ew", padx=(0, 1), pady=0)
        else:
            ttk.Button(button_row, text="Auto Cmd", command=lambda key=server_key: self.auto_update_commands_for_server(key, show_popup=True), style="Compact.TButton").grid(row=0, column=0, sticky="ew", padx=(0, 1), pady=0)

        ttk.Button(button_row, text="📦 Install", command=lambda key=server_key: self.install_dependencies(key), style="Compact.TButton").grid(row=0, column=1, sticky="ew", padx=1, pady=0)
        toggle = ttk.Button(button_row, text="▶️ Start", command=lambda key=server_key: self.toggle_server(key), style="Primary.TButton")
        toggle.grid(row=0, column=2, sticky="ew", padx=1, pady=0)
        ttk.Button(button_row, text="Open", command=lambda key=server_key: webbrowser.open(SERVER_INFO[key]["local_url"]), style="Compact.TButton").grid(row=0, column=3, sticky="ew", padx=(1, 0), pady=0)

        self.server_toggle_buttons[server_key] = toggle
        self.update_server_toggle_button(server_key)
        return frame

    def build_console_panel(self, parent):
        frame = ttk.LabelFrame(parent, text="System Logs", style="Card.TLabelframe")
        frame.pack(fill="both", expand=True)
        frame.columnconfigure(0, weight=1)
        frame.rowconfigure(0, weight=1)

        self.console_pane = ttk.PanedWindow(frame, orient="horizontal")
        self.console_pane.grid(row=0, column=0, sticky="nsew")

        log_area = ttk.Frame(self.console_pane, style="CardBody.TFrame")
        visitor_area = ttk.LabelFrame(self.console_pane, text="Live Access Logs", style="Card.TLabelframe")
        self.console_pane.add(log_area, weight=3)
        self.console_pane.add(visitor_area, weight=1)

        log_area.columnconfigure(0, weight=1)
        log_area.rowconfigure(1, weight=1)
        toolbar = ttk.Frame(log_area, style="CardBody.TFrame")
        toolbar.grid(row=0, column=0, sticky="ew", pady=(0, 2))
        toolbar.columnconfigure(0, weight=1)
        self.log_tab_buttons = {}
        left_tabs = ttk.Frame(toolbar, style="CardBody.TFrame")
        left_tabs.grid(row=0, column=0, sticky="w")
        right_tools = ttk.Frame(toolbar, style="CardBody.TFrame")
        right_tools.grid(row=0, column=1, sticky="e")

        self.current_log_key = "system"
        for key, title in [
            ("system", "System"),
            ("cloudflare", "Tunnel"),
            ("frontend", "Service"),
            ("admin", "Admin"),
            ("backend", "Backend"),
        ]:
            btn = ttk.Button(left_tabs, text=title, command=lambda k=key: self.switch_log_tab(k), style="LogTab.TButton")
            btn.pack(side="left", padx=(0, 2))
            self.log_tab_buttons[key] = btn
        ttk.Button(right_tools, text="🧹 Clear Logs", command=lambda: self.clear_log(getattr(self, "current_log_key", "system")), style="Compact.TButton").pack(side="right")

        self.log_stack = ttk.Frame(log_area, style="CardBody.TFrame")
        self.log_stack.grid(row=1, column=0, sticky="nsew")
        self.log_stack.columnconfigure(0, weight=1)
        self.log_stack.rowconfigure(0, weight=1)
        self.log_frames = {}

        for key, title in [
            ("system", "System"),
            ("cloudflare", "Tunnel"),
            ("frontend", "Service"),
            ("admin", "Admin"),
            ("backend", "Backend"),
        ]:
            tab = ttk.Frame(self.log_stack, style="CardBody.TFrame")
            tab.grid(row=0, column=0, sticky="nsew")
            tab.columnconfigure(0, weight=1)
            tab.rowconfigure(0, weight=1)
            body = ttk.Frame(tab, style="CardBody.TFrame")
            body.grid(row=0, column=0, sticky="nsew")
            text = tk.Text(body, wrap="word", font=("Menlo" if get_system_name() == "Darwin" else "Consolas", 10), bg=self.ui_log_bg, fg=self.ui_log_fg, insertbackground=self.ui_log_fg, relief="flat", borderwidth=0)
            text.pack(side="left", fill="both", expand=True)
            scrollbar = ttk.Scrollbar(body, command=text.yview)
            scrollbar.pack(side="right", fill="y")
            text.configure(yscrollcommand=scrollbar.set)
            self.log_widgets[key] = text
            self.log_frames[key] = tab
        self.switch_log_tab("system")

        visitor_area.columnconfigure(0, weight=1)
        visitor_area.rowconfigure(0, weight=1)
        columns = ("time", "ip", "method", "path")
        self.visitor_tree = ttk.Treeview(visitor_area, columns=columns, show="headings", height=6)
        self.visitor_tree.heading("time", text="Time")
        self.visitor_tree.heading("ip", text="IP")
        self.visitor_tree.heading("method", text="Method")
        self.visitor_tree.heading("path", text="Path")
        self.visitor_tree.column("time", width=64, anchor="center")
        self.visitor_tree.column("ip", width=112, anchor="w")
        self.visitor_tree.column("method", width=70, anchor="center")
        self.visitor_tree.column("path", width=260, anchor="w")
        self.visitor_tree.grid(row=0, column=0, sticky="nsew", padx=2, pady=2)
        visitor_scroll = ttk.Scrollbar(visitor_area, command=self._visitor_scrollbar_command)
        visitor_scroll.grid(row=0, column=1, sticky="ns")
        self.visitor_tree.configure(yscrollcommand=visitor_scroll.set)
        self.visitor_tree.bind("<MouseWheel>", self.pause_visitor_autoscroll)
        self.visitor_tree.bind("<Button-4>", self.pause_visitor_autoscroll)
        self.visitor_tree.bind("<Button-5>", self.pause_visitor_autoscroll)
        self.visitor_autoscroll_pause_until = 0

        self.append_log("system", f"[READY] {APP_TITLE}")
        self.append_log("system", f"[OS] {get_os_label()}")
        self.append_log("system", f"[IPv4] {self.ip_var.get()}")
        self.append_log("system", "[PORT] Backend 8000 / Admin Frontend 5173 / Service Frontend 5174")
        self.append_log("system", "[INFO] Cloudflare Tunnel은 서비스/관리자 프론트엔드를 외부 URL로 공개합니다.")
        self.append_log("system", "[INFO] 고정 도메인 기본값: eagle.onestudio.kr / admin-eagle.onestudio.kr")
        self.update_visitors_panel()

    def switch_log_tab(self, log_key):
        self.current_log_key = log_key
        if hasattr(self, "log_frames"):
            for key, frame in self.log_frames.items():
                try:
                    frame.grid_remove()
                except Exception:
                    pass
            try:
                self.log_frames[log_key].grid()
            except Exception:
                pass
        if hasattr(self, "log_tab_buttons"):
            for key, btn in self.log_tab_buttons.items():
                try:
                    btn.configure(style="LogActive.TButton" if key == log_key else "LogTab.TButton")
                except Exception:
                    pass

    def pause_visitor_autoscroll(self, event=None):
        self.visitor_autoscroll_pause_until = time.time() + 30

    def _visitor_scrollbar_command(self, *args):
        self.pause_visitor_autoscroll()
        if hasattr(self, "visitor_tree"):
            self.visitor_tree.yview(*args)

    def open_tool_settings_window(self):
        if self.focus_existing_window("tool_settings"):
            return
        win = tk.Toplevel(self.root)
        win.title("개발 Tool Status / 설치 설정")
        win.geometry("940x420")
        win.transient(self.root)
        self.register_singleton_window("tool_settings", win)

        frame = ttk.Frame(win, padding=16)
        frame.pack(fill="both", expand=True)

        status_box = tk.Text(
            frame,
            height=8,
            wrap="word",
            font=(self.font_family, 10),
            relief="solid",
            borderwidth=1,
        )
        status_box.pack(fill="x", pady=(0, 12))

        def refresh_status():
            python_status, node_status, cloudflared_status, lines = self.check_developer_tools(show_popup=False, return_lines=True)

            status_box.configure(state="normal")
            status_box.delete("1.0", "end")
            status_box.insert("end", "\n".join(lines))
            status_box.configure(state="disabled")

        refresh_status()

        rows = [
            ("Python 설치 명령", "python_install_cmd"),
            ("Node.js 설치 명령", "node_install_cmd"),
            ("Homebrew 설치 명령", "homebrew_install_cmd"),
            ("Cloudflare 설치 명령", "cloudflared_install_cmd"),
        ]

        for label, key in rows:
            row = ttk.Frame(frame)
            row.pack(fill="x", pady=5)

            ttk.Label(row, text=label, width=18).pack(side="left")
            ttk.Entry(row, textvariable=self.vars[key]).pack(side="left", fill="x", expand=True, padx=8)

        button_row = ttk.Frame(frame)
        button_row.pack(fill="x", pady=(14, 0))

        ttk.Button(
            button_row,
            text="상태 새로고침",
            command=refresh_status,
            style="Small.TButton",
        ).pack(side="left", padx=(0, 6))

        ttk.Button(
            button_row,
            text="Python 설치",
            command=self.install_python_tool,
            style="Small.TButton",
        ).pack(side="left", padx=6)

        ttk.Button(
            button_row,
            text="Node.js 설치",
            command=self.install_node_tool,
            style="Small.TButton",
        ).pack(side="left", padx=6)

        ttk.Button(
            button_row,
            text="Homebrew 설치",
            command=self.install_homebrew_tool,
            style="Small.TButton",
        ).pack(side="left", padx=6)

        ttk.Button(
            button_row,
            text="Git 설치",
            command=self.install_git_tool,
            style="Small.TButton",
        ).pack(side="left", padx=6)

        ttk.Button(
            button_row,
            text="Cloudflare 설치",
            command=self.install_cloudflared_tool,
            style="Small.TButton",
        ).pack(side="left", padx=6)

        ttk.Button(
            button_row,
            text="저장 후 닫기",
            command=lambda: [self.save_current_config(show_popup=False), win.destroy()],
            style="Primary.TButton",
        ).pack(side="right")

    def open_cloudflare_settings_window(self):
        if self.focus_existing_window("cloudflare_settings"):
            return
        win = tk.Toplevel(self.root)
        win.title("Cloudflare Settings")
        win.geometry("920x420")
        win.transient(self.root)
        self.register_singleton_window("cloudflare_settings", win)

        frame = ttk.Frame(win, padding=12)
        frame.pack(fill="both", expand=True)

        ttk.Label(frame, text="Cloudflare Settings", font=(self.font_family, 15, "bold")).pack(anchor="w", pady=(0, 8))

        rows = [
            ("Install Command", "cloudflared_install_cmd"),
            ("Service Domain", "cloudflare_service_domain"),
            ("Admin Domain", "cloudflare_admin_domain"),
            ("Tunnel Name", "cloudflare_named_tunnel_name"),
            ("Config Path", "cloudflare_named_config_path"),
        ]
        for label, key in rows:
            row = ttk.Frame(frame)
            row.pack(fill="x", pady=2)
            ttk.Label(row, text=label, width=16).pack(side="left")
            ttk.Entry(row, textvariable=self.vars[key]).pack(side="left", fill="x", expand=True, padx=(6, 0))

        info = ttk.Label(
            frame,
            text="Config default: ~/.cloudflared/eagle-taxi.yml  ·  Named Tunnel 실행 전 Cloudflare Wizard에서 login/create/route/config를 완료하세요.",
            style="Subtle.TLabel",
        )
        info.pack(anchor="w", pady=(6, 8))

        action = ttk.LabelFrame(frame, text="Actions", style="Card.TLabelframe")
        action.pack(fill="x", pady=(0, 8))
        for i in range(5):
            action.columnconfigure(i, weight=1)
        ttk.Button(action, text="Cloudflare Wizard", command=self.open_cloudflare_wizard_window, style="Primary.TButton").grid(row=0, column=0, sticky="ew", padx=2, pady=2)
        ttk.Button(action, text="Create Config", command=self.create_cloudflare_named_config_file, style="Small.TButton").grid(row=0, column=1, sticky="ew", padx=2, pady=2)
        ttk.Button(action, text="Route DNS", command=self.route_cloudflare_dns, style="Small.TButton").grid(row=0, column=2, sticky="ew", padx=2, pady=2)
        ttk.Button(action, text="Open Folder", command=self.open_cloudflare_config_folder, style="Small.TButton").grid(row=0, column=3, sticky="ew", padx=2, pady=2)
        ttk.Button(action, text="Install cloudflared", command=self.install_cloudflared_tool, style="Small.TButton").grid(row=0, column=4, sticky="ew", padx=2, pady=2)

        bottom = ttk.Frame(frame)
        bottom.pack(fill="x")
        ttk.Button(bottom, text="Save", command=lambda: [self.save_current_config(show_popup=False), self.refresh_share_text()], style="Primary.TButton").pack(side="right", padx=(4, 0))
        ttk.Button(bottom, text="Close", command=win.destroy, style="Small.TButton").pack(side="right")


    def open_cloudflare_wizard_window(self):
        if self.focus_existing_window("cloudflare_wizard"):
            return
        win = tk.Toplevel(self.root)
        win.title("Cloudflare Start Named Tunnel 마법사")
        win.geometry("1080x720")
        win.transient(self.root)

        def cleanup_cloudflare_wizard():
            self.cloudflare_wizard_log_text = None

        self.register_singleton_window("cloudflare_wizard", win, cleanup=cleanup_cloudflare_wizard)

        frame = ttk.Frame(win, padding=16)
        frame.pack(fill="both", expand=True)

        ttk.Label(
            frame,
            text="Cloudflare Start Named Tunnel 마법사",
            font=(self.font_family, 15, "bold"),
        ).pack(anchor="w", pady=(0, 8))

        config_file = get_cloudflare_config_file_path(self.vars["cloudflare_named_config_path"].get())
        info_text = (
            "이 마법사는 로그인 → 터널 생성 → DNS 라우팅 → 설정 파일 생성 → 고정 도메인 실행 순서로 진행합니다.\n"
            "브라우저 로그인이 필요한 단계는 Cloudflare 화면에서 직접 승인해야 합니다.\n"
            f"설정 파일 생성 위치: {config_file}"
        )
        ttk.Label(frame, text=info_text, style="Subtle.TLabel", justify="left").pack(anchor="w", pady=(0, 10))

        settings_box = ttk.LabelFrame(frame, text="현재 설정", style="Card.TLabelframe")
        settings_box.pack(fill="x", pady=(0, 8))

        rows = [
            ("서비스 도메인", "cloudflare_service_domain"),
            ("관리자 도메인", "cloudflare_admin_domain"),
            ("터널 이름", "cloudflare_named_tunnel_name"),
            ("설정 파일", "cloudflare_named_config_path"),
        ]
        for label, key in rows:
            row = ttk.Frame(settings_box)
            row.pack(fill="x", pady=3)
            ttk.Label(row, text=label, width=14).pack(side="left")
            ttk.Entry(row, textvariable=self.vars[key]).pack(side="left", fill="x", expand=True, padx=8)

        step_box = ttk.LabelFrame(frame, text="단계별 실행", style="Card.TLabelframe")
        step_box.pack(fill="x", pady=(0, 8))

        for i in range(5):
            step_box.columnconfigure(i, weight=1)

        ttk.Button(step_box, text="1. 로그인", command=self.run_cloudflare_login, style="Small.TButton").grid(row=0, column=0, sticky="ew", padx=3, pady=3)
        ttk.Button(step_box, text="2. 터널 생성", command=self.create_cloudflare_named_tunnel, style="Small.TButton").grid(row=0, column=1, sticky="ew", padx=3, pady=3)
        ttk.Button(step_box, text="3. DNS 연결", command=self.route_cloudflare_dns, style="Small.TButton").grid(row=0, column=2, sticky="ew", padx=3, pady=3)
        ttk.Button(step_box, text="4. 설정 파일 생성", command=self.create_cloudflare_named_config_file, style="Primary.TButton").grid(row=0, column=3, sticky="ew", padx=3, pady=3)
        ttk.Button(step_box, text="5. 고정 도메인 실행", command=self.start_cloudflare_named_tunnel, style="Primary.TButton").grid(row=0, column=4, sticky="ew", padx=3, pady=3)

        quick_box = ttk.LabelFrame(frame, text="보조 작업", style="Card.TLabelframe")
        quick_box.pack(fill="x", pady=(0, 8))

        for i in range(4):
            quick_box.columnconfigure(i, weight=1)

        ttk.Button(quick_box, text="설치", command=self.install_cloudflared_tool, style="Small.TButton").grid(row=0, column=0, sticky="ew", padx=3, pady=3)
        ttk.Button(quick_box, text="Check Status", command=lambda: self.check_developer_tools(show_popup=True), style="Small.TButton").grid(row=0, column=1, sticky="ew", padx=3, pady=3)
        ttk.Button(quick_box, text="Open Config Folder", command=self.open_cloudflare_config_folder, style="Small.TButton").grid(row=0, column=2, sticky="ew", padx=3, pady=3)
        ttk.Button(quick_box, text="Stop Named Tunnel", command=self.stop_cloudflare_named_tunnel, style="Danger.TButton").grid(row=0, column=3, sticky="ew", padx=3, pady=3)

        log_box = ttk.LabelFrame(frame, text="마법사 안내 / 결과", style="Card.TLabelframe")
        log_box.pack(fill="both", expand=True)

        text = tk.Text(
            log_box,
            wrap="word",
            font=("Menlo" if get_system_name() == "Darwin" else "Consolas", 10),
            relief="solid",
            borderwidth=1,
        )
        text.pack(fill="both", expand=True)
        text.insert("end", self.build_cloudflare_wizard_guide())
        text.configure(state="normal")
        self.cloudflare_wizard_log_text = text

        bottom = ttk.Frame(frame)
        bottom.pack(fill="x", pady=(8, 0))
        ttk.Button(bottom, text="저장 후 닫기", command=lambda: [self.save_current_config(show_popup=False), self.refresh_share_text(), win.destroy()], style="Primary.TButton").pack(side="right")

    def build_cloudflare_wizard_guide(self):
        config_file = get_cloudflare_config_file_path(self.vars["cloudflare_named_config_path"].get())
        credentials = find_latest_cloudflare_credentials_file()
        credentials_text = str(credentials) if credentials else "아직 감지된 credentials JSON 없음"

        return (
            "[진행 순서]\n"
            "1. 로그인: Cloudflare 브라우저 인증을 진행합니다. 이미 cert.pem이 있으면 생략 가능할 수 있습니다.\n"
            "2. 터널 생성: eagle-taxi 터널을 생성하고 ~/.cloudflared 안에 UUID.json credentials 파일을 만듭니다.\n"
            "3. DNS 연결: eagle.onestudio.kr, admin-eagle.onestudio.kr을 터널에 연결합니다.\n"
            "4. 설정 파일 생성: 가장 최근 credentials JSON을 사용해 YAML 파일을 자동 작성합니다.\n"
            "5. 고정 도메인 실행: YAML 설정으로 터널을 실행합니다.\n\n"
            f"[설정 파일 위치]\n{config_file}\n\n"
            f"[감지된 credentials]\n{credentials_text}\n\n"
            "참고: credentials가 여러 개 있으면 가장 최근 JSON을 사용합니다. 다른 파일을 써야 하면 ~/.cloudflared 폴더에서 이전 JSON을 정리하거나 설정 파일을 직접 확인하세요."
        )

    def run_cloudflare_login(self):
        if not find_cloudflared_status()["ok"]:
            if messagebox.askyesno("cloudflared 필요", "cloudflared가 없습니다. 설치 도우미를 실행할까요?"):
                self.install_cloudflared_tool()
            return

        command = f"{get_cloudflared_command()} tunnel login"
        self.append_log("cloudflare", "[WIZARD] Cloudflare 로그인 시작")
        self.start_process(
            process_key="cloudflare_login",
            log_key="cloudflare",
            title="Cloudflare 로그인",
            cwd=str(Path.home()),
            command=command,
            server_key=None,
        )

    def create_cloudflare_named_tunnel(self):
        if not find_cloudflared_status()["ok"]:
            if messagebox.askyesno("cloudflared 필요", "cloudflared가 없습니다. 설치 도우미를 실행할까요?"):
                self.install_cloudflared_tool()
            return

        tunnel_name = self.vars["cloudflare_named_tunnel_name"].get().strip() or "eagle-taxi"
        command = f"{get_cloudflared_command()} tunnel create {tunnel_name}"
        self.append_log("cloudflare", f"[WIZARD] 터널 생성 시작: {tunnel_name}")
        self.start_process(
            process_key="cloudflare_create_tunnel",
            log_key="cloudflare",
            title="Cloudflare 고정 터널 생성",
            cwd=str(Path.home()),
            command=command,
            server_key=None,
        )

    def route_cloudflare_dns(self):
        if not find_cloudflared_status()["ok"]:
            if messagebox.askyesno("cloudflared 필요", "cloudflared가 없습니다. 설치 도우미를 실행할까요?"):
                self.install_cloudflared_tool()
            return

        tunnel_name = self.vars["cloudflare_named_tunnel_name"].get().strip() or "eagle-taxi"
        service_domain = self.vars["cloudflare_service_domain"].get().strip() or "eagle.onestudio.kr"
        admin_domain = self.vars["cloudflare_admin_domain"].get().strip() or "admin-eagle.onestudio.kr"

        command = (
            f"{get_cloudflared_command()} tunnel route dns {tunnel_name} {service_domain} && "
            f"{get_cloudflared_command()} tunnel route dns {tunnel_name} {admin_domain}"
        )
        self.append_log("cloudflare", f"[WIZARD] DNS 라우팅 연결 시작: {service_domain}, {admin_domain}")
        self.start_process(
            process_key="cloudflare_route_dns",
            log_key="cloudflare",
            title="Cloudflare DNS 라우팅 연결",
            cwd=str(Path.home()),
            command=command,
            server_key=None,
        )

    def create_cloudflare_named_config_file(self):
        tunnel_name = self.vars["cloudflare_named_tunnel_name"].get().strip() or "eagle-taxi"
        service_domain = self.vars["cloudflare_service_domain"].get().strip() or "eagle.onestudio.kr"
        admin_domain = self.vars["cloudflare_admin_domain"].get().strip() or "admin-eagle.onestudio.kr"
        config_path = self.vars["cloudflare_named_config_path"].get().strip() or "~/.cloudflared/eagle-taxi.yml"

        credentials_file = find_latest_cloudflare_credentials_file()
        if not credentials_file:
            messagebox.showwarning(
                "credentials 파일 없음",
                "~/.cloudflared 폴더에서 터널 credentials JSON을 찾지 못했습니다.\n\n"
                "먼저 '1. 로그인'과 '2. 터널 생성'을 진행한 뒤 다시 시도하세요."
            )
            return

        config_file = write_cloudflare_config_file(
            config_path=config_path,
            tunnel_name=tunnel_name,
            service_domain=service_domain,
            admin_domain=admin_domain,
            credentials_file=credentials_file,
        )

        self.append_log("cloudflare", f"[WIZARD] 설정 파일 생성 완료: {config_file}")
        self.append_log("cloudflare", f"[WIZARD] credentials-file: {credentials_file}")
        self.status_var.set("Cloudflare Settings 파일 생성 완료")
        messagebox.showinfo("설정 파일 생성 완료", f"설정 파일을 생성했습니다.\n\n{config_file}")

    def open_cloudflare_config_folder(self):
        folder = get_cloudflared_dir()
        folder.mkdir(parents=True, exist_ok=True)

        if get_system_name() == "Darwin":
            subprocess.Popen(["open", str(folder)])
        elif get_system_name() == "Windows":
            subprocess.Popen(["explorer", str(folder)])
        else:
            subprocess.Popen(["xdg-open", str(folder)])

    def stop_cloudflare_named_tunnel(self):
        process = self.processes.get("named_tunnel")
        if process and process.poll() is None:
            self.terminate_process("named_tunnel")
            self.append_log("cloudflare", "[TUNNEL] Named Tunnel 중지 요청 완료")
        else:
            self.append_log("cloudflare", "[TUNNEL] 실행 중인 Named Tunnel 없음")

        self.update_tunnel_toggle_buttons()
        self.status_var.set("Named Tunnel 중지 요청 완료")
    def open_server_settings_window(self, server_key):
        info = SERVER_INFO[server_key]
        window_key = f"server_settings_{server_key}"
        if self.focus_existing_window(window_key):
            return

        win = tk.Toplevel(self.root)
        win.title(f"{info['label']} 설정")
        win.geometry("980x440")
        win.transient(self.root)
        self.register_singleton_window(window_key, win)

        frame = ttk.Frame(win, padding=16)
        frame.pack(fill="both", expand=True)

        path_key = info["path_key"]
        install_cmd_key = info["install_cmd_key"]
        cmd_key = info["cmd_key"]

        title = ttk.Label(
            frame,
            text=f"{info['label']} 설정 · 포트 {info['port']}",
            font=(self.font_family, 15, "bold"),
        )
        title.pack(anchor="w", pady=(0, 14))

        path_row = ttk.Frame(frame)
        path_row.pack(fill="x", pady=6)

        ttk.Label(path_row, text="폴더 경로", width=14).pack(side="left")
        ttk.Entry(path_row, textvariable=self.vars[path_key]).pack(side="left", fill="x", expand=True, padx=8)

        ttk.Button(
            path_row,
            text="경로 선택",
            command=lambda: [self.select_folder(path_key), self.auto_update_commands_for_server(server_key)],
            style="Small.TButton",
        ).pack(side="left", padx=(0, 4))

        ttk.Button(
            path_row,
            text="명령 자동 생성",
            command=lambda: self.auto_update_commands_for_server(server_key, show_popup=True),
            style="Small.TButton",
        ).pack(side="left")

        install_row = ttk.Frame(frame)
        install_row.pack(fill="x", pady=6)

        ttk.Label(install_row, text="설치 명령", width=14).pack(side="left")
        ttk.Entry(install_row, textvariable=self.vars[install_cmd_key]).pack(
            side="left",
            fill="x",
            expand=True,
            padx=8,
        )

        run_row = ttk.Frame(frame)
        run_row.pack(fill="x", pady=6)

        ttk.Label(run_row, text="실행 명령", width=14).pack(side="left")
        ttk.Entry(run_row, textvariable=self.vars[cmd_key]).pack(
            side="left",
            fill="x",
            expand=True,
            padx=8,
        )

        if server_key == "backend":
            venv_row = ttk.Frame(frame)
            venv_row.pack(fill="x", pady=6)

            ttk.Label(venv_row, text=".venv 생성", width=14).pack(side="left")
            ttk.Entry(venv_row, textvariable=self.vars["backend_create_venv_cmd"]).pack(
                side="left",
                fill="x",
                expand=True,
                padx=8,
            )

        info_box = tk.Text(
            frame,
            height=7,
            wrap="word",
            font=(self.font_family, 10),
            relief="solid",
            borderwidth=1,
        )
        info_box.pack(fill="both", expand=True, pady=(10, 8))

        info_box.insert("end", self.build_server_settings_info(server_key))
        info_box.configure(state="disabled")

        button_row = ttk.Frame(frame)
        button_row.pack(fill="x", pady=(8, 0))

        if server_key == "backend":
            ttk.Button(
                button_row,
                text="백엔드 .venv 생성",
                command=self.create_backend_venv,
                style="Small.TButton",
            ).pack(side="left", padx=(0, 6))

        ttk.Button(
            button_row,
            text="의존성 설치",
            command=lambda: self.install_dependencies(server_key),
            style="Small.TButton",
        ).pack(side="left", padx=6)

        ttk.Button(
            button_row,
            text="서버 실행",
            command=lambda: self.run_server(server_key),
            style="Primary.TButton",
        ).pack(side="left", padx=6)

        ttk.Button(
            button_row,
            text="저장 후 닫기",
            command=lambda: [self.save_current_config(show_popup=False), self.refresh_all_summaries(), win.destroy()],
            style="Primary.TButton",
        ).pack(side="right")

    def build_server_settings_info(self, server_key):
        info = SERVER_INFO[server_key]
        folder = self.vars[info["path_key"]].get().strip()

        lines = [
            f"[{info['label']} 설정 안내]",
            f"- 실행 기준 폴더: {folder or '미지정'}",
            f"- 로컬 주소: {info['local_url']}",
            f"- 공유 주소: {build_share_url(server_key, self.ip_var.get().strip())}",
            "",
        ]

        if server_key == "backend":
            venv_python = get_venv_python_path(folder)

            if venv_python:
                lines.append(f"- 감지된 백엔드 가상환경 Python: {venv_python}")
            else:
                lines.append("- backend 폴더 내부 .venv를 찾지 못했습니다.")
                lines.append("- 먼저 '.venv 생성'을 실행한 뒤 의존성 설치를 권장합니다.")
        else:
            lines.append("- React/Vite 프론트는 지정한 폴더에서 npm install / npm run dev로 실행됩니다.")
            lines.append("- Service Frontend는 5174, Admin Frontend는 5173으로 고정했습니다.")

        return "\n".join(lines)

    # --------------------------------------------------------
    # 설정/명령 자동화
    # --------------------------------------------------------

    def ensure_auto_commands(self, fill_empty_only=True):
        mapping = [
            ("backend", build_backend_install_cmd, build_backend_run_cmd),
            ("frontend", build_frontend_install_cmd, build_frontend_run_cmd),
            ("admin", build_admin_install_cmd, build_admin_run_cmd),
        ]

        for server_key, install_builder, run_builder in mapping:
            info = SERVER_INFO[server_key]
            folder = self.vars[info["path_key"]].get().strip()
            install_key = info["install_cmd_key"]
            run_key = info["cmd_key"]

            if not fill_empty_only or not self.vars[install_key].get().strip():
                self.vars[install_key].set(install_builder(folder))

            if not fill_empty_only or not self.vars[run_key].get().strip():
                self.vars[run_key].set(run_builder(folder))

    def auto_update_commands_for_server(self, server_key, show_popup=False):
        info = SERVER_INFO[server_key]
        folder = self.vars[info["path_key"]].get().strip()

        if server_key == "backend":
            self.vars["backend_install_cmd"].set(build_backend_install_cmd(folder))
            self.vars["backend_cmd"].set(build_backend_run_cmd(folder))

        elif server_key == "frontend":
            self.vars["frontend_install_cmd"].set(build_frontend_install_cmd(folder))
            self.vars["frontend_cmd"].set(build_frontend_run_cmd(folder))

        elif server_key == "admin":
            self.vars["admin_install_cmd"].set(build_admin_install_cmd(folder))
            self.vars["admin_cmd"].set(build_admin_run_cmd(folder))

        self.save_current_config(show_popup=False)
        self.refresh_all_summaries()

        self.append_log("system", f"[AUTO] {info['label']} 명령 자동 생성 완료")

        if show_popup:
            messagebox.showinfo("자동 생성 완료", f"{info['label']} 설치/실행 명령을 자동 생성했습니다.")

    def reset_auto_commands(self, show_popup=False):
        self.ensure_auto_commands(fill_empty_only=False)
        self.save_current_config(show_popup=False)
        self.refresh_all_summaries()
        self.append_log("system", "[AUTO] 전체 서버 명령 자동 갱신 완료")

        if show_popup:
            messagebox.showinfo("Refresh Auto Commands", "전체 서버의 설치/실행 명령을 현재 경로 기준으로 다시 생성했습니다.")

    def auto_set_project_paths(self):
        root = get_project_root_guess()

        backend = root / "backend"
        frontend = root / "frontend"
        admin = root / "admin"

        found_any = False

        if backend.exists():
            self.vars["backend_path"].set(str(backend))
            found_any = True

        if frontend.exists():
            self.vars["frontend_path"].set(str(frontend))
            found_any = True

        if admin.exists():
            self.vars["admin_path"].set(str(admin))
            found_any = True

        self.reset_auto_commands(show_popup=False)
        self.refresh_all_summaries()

        if found_any:
            messagebox.showinfo("자동 설정 완료", f"프로젝트 루트 기준으로 경로를 자동 설정했습니다.\n\n{root}")
            self.append_log("system", f"[PATH] Auto Detect Project Paths: {root}")
        else:
            messagebox.showwarning(
                "자동 설정 실패",
                f"현재 위치 기준으로 backend/frontend/admin 폴더를 찾지 못했습니다.\n\n{root}"
            )

    def collect_config(self):
        return {key: var.get().strip() for key, var in self.vars.items()}

    def save_current_config(self, show_popup=True):
        self.config.update(self.collect_config())
        self.config["wizard_env_text"] = self.wizard_env_text
        self.config["wizard_backend_env_text"] = getattr(self, "wizard_backend_env_text", BACKEND_ENV_TEMPLATE)
        self.config["wizard_frontend_env_text"] = getattr(self, "wizard_frontend_env_text", FRONTEND_ENV_TEMPLATE)
        save_config(self.config)
        self.status_var.set("Save Settings 완료")
        self.append_log("system", f"[CONFIG] Save Settings: {CONFIG_FILE}")

        if show_popup:
            messagebox.showinfo("저장 완료", "현재 설정을 저장했습니다.")

    def select_folder(self, variable_key):
        selected = filedialog.askdirectory()

        if selected:
            self.vars[variable_key].set(selected)
            self.status_var.set("경로 선택 완료")
            self.save_current_config(show_popup=False)
            self.refresh_all_summaries()

    def refresh_all_summaries(self):
        for server_key, info in SERVER_INFO.items():
            folder = self.vars[info["path_key"]].get().strip()
            self.path_summary_vars[server_key].set(short_path(folder, 30))

        self.refresh_share_text()

    # --------------------------------------------------------
    # 접속 주소
    # --------------------------------------------------------

    def refresh_ip(self):
        self.ip_var.set(get_local_ipv4())
        self.refresh_share_text()
        self.append_log("system", f"[IP] IPv4 새로고침: {self.ip_var.get()}")
        self.status_var.set("IP 새로고침 완료")

    def refresh_share_text(self):
        ip = self.ip_var.get().strip()

        local_lines = [
            f"Service: {build_share_url('frontend', ip)}",
            f"Admin: {build_share_url('admin', ip)}",
        ]
        service_tunnel = self.get_tunnel_service_url()
        admin_tunnel = self.get_tunnel_admin_url()
        cloudflare_lines = [
            f"Service: {service_tunnel}",
            f"Admin: {admin_tunnel}",
        ]

        if hasattr(self, "share_text"):
            self.share_text.configure(state="normal")
            self.share_text.delete("1.0", "end")
            self.share_text.insert("end", "\n".join(local_lines))
            self.share_text.configure(state="disabled")

        if hasattr(self, "global_local_text") and self.global_local_text is not self.share_text:
            self.global_local_text.configure(state="normal")
            self.global_local_text.delete("1.0", "end")
            self.global_local_text.insert("end", "\n".join(local_lines))
            self.global_local_text.configure(state="disabled")

        if hasattr(self, "cloudflare_text"):
            self.cloudflare_text.configure(state="normal")
            self.cloudflare_text.delete("1.0", "end")
            self.cloudflare_text.insert("end", "\n".join(cloudflare_lines))
            self.cloudflare_text.configure(state="disabled")


    def copy_share_info(self):
        self.refresh_share_text()
        text = self.share_text.get("1.0", "end").strip()
        self.copy_text_to_clipboard(text, "[COPY] Local URLs copied")
        self.status_var.set("Local URLs copied")

    def copy_text_to_clipboard(self, text, log_message=None):
        self.root.clipboard_clear()
        self.root.clipboard_append(text)
        self.root.update()
        if log_message:
            self.append_log("system", log_message)

    def get_tunnel_service_url(self):
        value = self.tunnel_url_vars["frontend"].get().strip()
        if value.startswith("https://"):
            return value
        return build_https_url(self.vars["cloudflare_service_domain"].get())

    def get_tunnel_admin_url(self):
        value = self.tunnel_url_vars["admin"].get().strip()
        if value.startswith("https://"):
            return value
        return build_https_url(self.vars["cloudflare_admin_domain"].get())

    def copy_local_service_url(self):
        url = build_share_url("frontend", self.ip_var.get().strip())
        self.copy_text_to_clipboard(url, "[COPY] Local Service URL copied")
        self.status_var.set("Local Service URL copied")

    def copy_local_admin_url(self):
        url = build_share_url("admin", self.ip_var.get().strip())
        self.copy_text_to_clipboard(url, "[COPY] Local Admin URL copied")
        self.status_var.set("Local Admin URL copied")

    def copy_tunnel_service_url(self):
        url = self.get_tunnel_service_url()
        self.copy_text_to_clipboard(url, "[COPY] Tunnel Service URL copied")
        self.status_var.set("Tunnel Service URL copied")

    def copy_tunnel_admin_url(self):
        url = self.get_tunnel_admin_url()
        self.copy_text_to_clipboard(url, "[COPY] Tunnel Admin URL copied")
        self.status_var.set("Tunnel Admin URL copied")


    def open_all_local_urls(self):
        webbrowser.open(SERVER_INFO["backend"]["local_url"])
        webbrowser.open(SERVER_INFO["admin"]["local_url"])
        webbrowser.open(SERVER_INFO["frontend"]["local_url"])

    # --------------------------------------------------------
    # 로그
    # --------------------------------------------------------

    def append_log(self, log_key, message):
        if log_key == "cloudflare":
            self.append_cloudflare_wizard_log(message)

        widget = self.log_widgets.get(log_key) or self.log_widgets.get("system")
        if widget is None:
            return
        self.append_to_text_widget(widget, message)

    def process_log_queue(self):
        try:
            while True:
                log_key, message = self.output_queue.get_nowait()
                self.append_log(log_key, message)
        except queue.Empty:
            pass

        self.root.after(100, self.process_log_queue)

    def clear_log(self, log_key):
        widget = self.log_widgets.get(log_key)
        if not widget:
            return
        widget.configure(state="normal")
        widget.delete("1.0", "end")
        widget.configure(state="normal")
        if log_key != "system":
            self.append_log("system", f"[LOG] {log_key} log cleared")

    def clear_all_logs(self):
        for widget in self.log_widgets.values():
            widget.configure(state="normal")
            widget.delete("1.0", "end")
            widget.configure(state="normal")

        self.append_log("system", "[LOG] 전체 로그를 지웠습니다.")

    # --------------------------------------------------------
    # 실행 환경 정리
    # --------------------------------------------------------

    def build_clean_env(self):
        env = os.environ.copy()

        env.pop("VIRTUAL_ENV", None)
        env.pop("PYTHONHOME", None)
        env["PYTHONUNBUFFERED"] = "1"
        env["FORCE_COLOR"] = "1"

        path_value = env.get("PATH", "")
        path_parts = path_value.split(os.pathsep)

        remove_targets = set()

        try:
            launcher_prefix = Path(sys.prefix).resolve()
            remove_targets.add(str(launcher_prefix / "bin"))
            remove_targets.add(str(launcher_prefix / "Scripts"))
        except Exception:
            pass

        cleaned_parts = []

        for part in path_parts:
            try:
                resolved = str(Path(part).resolve())
            except Exception:
                resolved = part

            if resolved in remove_targets:
                continue

            cleaned_parts.append(part)

        env["PATH"] = os.pathsep.join(cleaned_parts)

        # .app 실행 환경에서 Homebrew node/npm/python 경로가 빠지는 문제 보완
        env = get_effective_env(env)

        return env

    # --------------------------------------------------------
    # 검증
    # --------------------------------------------------------

    def validate_server(self, server_key, mode):
        info = SERVER_INFO[server_key]
        path_key = info["path_key"]

        if mode == "run":
            command_key = info["cmd_key"]
            check_files = info["run_check_files"]
            mode_label = "실행"
        else:
            command_key = info["install_cmd_key"]
            check_files = info["install_check_files"]
            mode_label = "의존성 설치"

        folder = self.vars[path_key].get().strip()
        command = self.vars[command_key].get().strip()

        if not folder:
            messagebox.showwarning("경로 필요", f"{info['label']} 폴더 경로를 먼저 선택하세요.")
            return False

        folder_path = Path(folder).expanduser()

        if not folder_path.exists():
            messagebox.showwarning("경로 오류", f"{info['label']} 폴더가 존재하지 않습니다.\n\n{folder_path}")
            return False

        for check_file in check_files:
            expected_file = folder_path / check_file

            if not expected_file.exists():
                answer = messagebox.askyesno(
                    "파일 확인 필요",
                    f"{info['label']} 폴더에서 다음 파일을 찾지 못했습니다.\n\n"
                    f"{expected_file}\n\n"
                    f"그래도 {mode_label}를 진행할까요?"
                )

                if not answer:
                    return False

        if not command:
            messagebox.showwarning("명령어 필요", f"{info['label']} {mode_label} 명령어가 비어 있습니다.")
            return False

        return True

    # --------------------------------------------------------
    # 프로세스 실행/종료
    # --------------------------------------------------------

    def start_process(self, process_key, log_key, title, cwd, command, server_key=None):
        old_process = self.processes.get(process_key)

        if old_process and old_process.poll() is None:
            messagebox.showinfo("이미 실행 중", f"{title} 작업이 이미 실행 중입니다.")
            return

        self.save_current_config(show_popup=False)

        cwd_path = Path(cwd).expanduser().resolve()

        if not cwd_path.exists():
            messagebox.showerror("경로 오류", f"작업 경로가 존재하지 않습니다.\n\n{cwd_path}")
            return

        system_name = get_system_name()
        creationflags = 0
        preexec_fn = None

        if system_name == "Windows":
            creationflags = subprocess.CREATE_NEW_PROCESS_GROUP
        else:
            preexec_fn = os.setsid

        env = self.build_clean_env()

        self.append_log(log_key, "")
        self.append_log(log_key, f"========== {title} ==========")
        self.append_log(log_key, f"$ cd {cwd_path}")
        self.append_log(log_key, f"$ {command}")

        try:
            process = subprocess.Popen(
                command,
                cwd=str(cwd_path),
                shell=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                stdin=subprocess.DEVNULL,
                text=True,
                encoding="utf-8",
                errors="replace",
                bufsize=1,
                env=env,
                creationflags=creationflags,
                preexec_fn=preexec_fn,
            )

        except Exception as e:
            self.append_log(log_key, f"[ERROR] 실행 실패: {e}")
            messagebox.showerror("실행 실패", f"{title} 실행 중 오류가 발생했습니다.\n\n{e}")
            return

        self.processes[process_key] = process
        self.process_meta[process_key] = {
            "title": title,
            "log_key": log_key,
            "server_key": server_key,
            "started_at": time.time(),
        }

        if server_key:
            self.server_status_vars[server_key].set("실행 중")
            self.update_server_toggle_button(server_key)

        self.root.after(0, self.update_all_runtime_toggle_buttons)
        self.status_var.set(f"{title} 시작")
        if hasattr(self, "log_notebook") and log_key in self.log_widgets:
            try:
                self.log_notebook.select(self.log_widgets[log_key].master)
            except Exception:
                pass

        thread = threading.Thread(
            target=self.read_process_output,
            args=(process_key, process, log_key, server_key),
            daemon=True,
        )
        thread.start()

    def read_process_output(self, process_key, process, log_key, server_key):
        try:
            if process.stdout:
                for line in process.stdout:
                    clean_line = line.rstrip("\n")
                    self.handle_process_line(process_key, log_key, clean_line)
                    self.output_queue.put((log_key, clean_line))

            return_code = process.wait()

            if return_code == 0:
                self.output_queue.put((log_key, f"[DONE] 작업이 정상 종료되었습니다. exit={return_code}"))
            else:
                self.output_queue.put((log_key, f"[STOP] 작업이 종료되었습니다. exit={return_code}"))

        except Exception as e:
            self.output_queue.put((log_key, f"[ERROR] 로그 읽기 오류: {e}"))

        finally:
            current = self.processes.get(process_key)

            if current is process:
                self.processes.pop(process_key, None)
                self.process_meta.pop(process_key, None)

            if server_key:
                self.root.after(0, lambda key=server_key: [self.server_status_vars[key].set("중지됨"), self.update_server_toggle_button(key), self.update_all_runtime_toggle_buttons()])
            else:
                self.root.after(0, self.update_all_runtime_toggle_buttons)

    def terminate_process(self, process_key):
        process = self.processes.get(process_key)
        meta = self.process_meta.get(process_key, {})
        log_key = meta.get("log_key", "system")

        if not process or process.poll() is not None:
            return

        try:
            if get_system_name() == "Windows":
                subprocess.run(
                    ["taskkill", "/F", "/T", "/PID", str(process.pid)],
                    capture_output=True,
                    text=True,
                )
            else:
                os.killpg(os.getpgid(process.pid), signal.SIGTERM)

                try:
                    process.wait(timeout=3)
                except subprocess.TimeoutExpired:
                    os.killpg(os.getpgid(process.pid), signal.SIGKILL)

            self.append_log(log_key, f"[KILL] 프로세스 종료 요청: PID {process.pid}")
            self.root.after(0, self.update_all_runtime_toggle_buttons)

        except Exception as e:
            self.append_log(log_key, f"[ERROR] 프로세스 종료 실패: {e}")

    def kill_port(self, port, show_popup=False):
        system_name = get_system_name()
        killed_pids = set()

        try:
            if system_name == "Windows":
                result = subprocess.run(
                    f'netstat -ano | findstr :{port}',
                    shell=True,
                    capture_output=True,
                    text=True,
                    encoding="utf-8",
                    errors="replace",
                )

                for line in result.stdout.splitlines():
                    parts = line.split()

                    if len(parts) >= 5:
                        local_address = parts[1]
                        state = parts[-2]
                        pid = parts[-1]

                        if f":{port}" in local_address and state.upper() == "LISTENING":
                            killed_pids.add(pid)

                for pid in killed_pids:
                    subprocess.run(
                        ["taskkill", "/F", "/T", "/PID", pid],
                        capture_output=True,
                        text=True,
                    )

            else:
                result = subprocess.run(
                    ["lsof", "-ti", f"tcp:{port}"],
                    capture_output=True,
                    text=True,
                    encoding="utf-8",
                    errors="replace",
                )

                for pid in result.stdout.splitlines():
                    pid = pid.strip()

                    if pid:
                        killed_pids.add(pid)

                for pid in killed_pids:
                    subprocess.run(
                        ["kill", "-9", pid],
                        capture_output=True,
                        text=True,
                    )

        except Exception as e:
            self.append_log("system", f"[ERROR] {port} 포트 종료 실패: {e}")
            if show_popup:
                messagebox.showerror("포트 종료 실패", f"{port} 포트 종료 중 오류가 발생했습니다.\n\n{e}")
            return False

        if killed_pids:
            self.append_log("system", f"[PORT] {port} 포트 종료: PID {', '.join(killed_pids)}")
        else:
            self.append_log("system", f"[PORT] {port} 포트에서 실행 중인 프로세스 없음")

        return True

    # --------------------------------------------------------
    # 서버 작업
    # --------------------------------------------------------

    def create_backend_venv(self):
        backend_path = self.vars["backend_path"].get().strip()

        if not backend_path:
            messagebox.showwarning("경로 필요", "백엔드 폴더 경로를 먼저 선택하세요.")
            return

        backend_folder = Path(backend_path).expanduser()

        if not backend_folder.exists():
            messagebox.showwarning("경로 오류", f"백엔드 폴더가 존재하지 않습니다.\n\n{backend_folder}")
            return

        command = self.vars["backend_create_venv_cmd"].get().strip()

        if not command:
            command = get_backend_create_venv_command()
            self.vars["backend_create_venv_cmd"].set(command)

        self.start_process(
            process_key="backend_create_venv",
            log_key="backend",
            title="백엔드 .venv 생성",
            cwd=backend_path,
            command=command,
            server_key=None,
        )

    def install_dependencies(self, server_key):
        self.auto_update_commands_for_server(server_key, show_popup=False)

        if not self.validate_server(server_key, mode="install"):
            return

        info = SERVER_INFO[server_key]
        folder = self.vars[info["path_key"]].get().strip()
        command = self.vars[info["install_cmd_key"]].get().strip()

        self.start_process(
            process_key=f"{server_key}_install",
            log_key=server_key,
            title=f"{info['label']} 의존성 설치",
            cwd=folder,
            command=command,
            server_key=None,
        )

    def install_all_dependencies(self):
        for server_key in ["backend", "frontend", "admin"]:
            self.auto_update_commands_for_server(server_key, show_popup=False)
            if not self.validate_server(server_key, mode="install"):
                return

        for server_key in ["backend", "frontend", "admin"]:
            self.install_dependencies(server_key)

        self.status_var.set("Install All Deps 시작")

    def run_server(self, server_key):
        self.auto_update_commands_for_server(server_key, show_popup=False)

        if not self.validate_server(server_key, mode="run"):
            return

        info = SERVER_INFO[server_key]
        folder = self.vars[info["path_key"]].get().strip()
        command = self.vars[info["cmd_key"]].get().strip()

        self.start_process(
            process_key=f"{server_key}_run",
            log_key=server_key,
            title=f"{info['label']} 서버 실행",
            cwd=folder,
            command=command,
            server_key=server_key,
        )

    def run_all_servers(self):
        for server_key in ["backend", "admin", "frontend"]:
            self.auto_update_commands_for_server(server_key, show_popup=False)
            if not self.validate_server(server_key, mode="run"):
                return

        for server_key in ["backend", "admin", "frontend"]:
            if not self.is_server_running(server_key):
                self.run_server(server_key)

        self.refresh_ip()
        self.update_all_runtime_toggle_buttons()
        self.status_var.set("Start All Servers 시작")

    def stop_server(self, server_key):
        process_key = f"{server_key}_run"
        process = self.processes.get(process_key)

        info = SERVER_INFO[server_key]

        if process and process.poll() is None:
            self.terminate_process(process_key)

        self.kill_port(info["port"], show_popup=False)
        self.server_status_vars[server_key].set("중지됨")
        self.update_server_toggle_button(server_key)
        self.append_log(server_key, f"[STOP] {info['port']} 포트 종료 요청 완료")
        self.status_var.set(f"{info['label']} 중지 요청 완료")

    def stop_all_servers(self):
        for server_key in ["backend", "frontend", "admin"]:
            self.stop_server(server_key)

        self.update_all_runtime_toggle_buttons()
        self.status_var.set("Stop All Servers 요청 완료")

    # --------------------------------------------------------
    # 개발 도구
    # --------------------------------------------------------

    def check_developer_tools(self, show_popup=True, return_lines=False):
        python_status = find_python_status()
        node_status = find_node_status()
        cloudflared_status = find_cloudflared_status()
        git_status = find_git_status()
        winget_status = find_winget_status()
        homebrew_status = find_homebrew_status()

        lines = [
            f"운영체제: {get_os_label()}",
            f"IPv4: {self.ip_var.get()}",
            "",
            f"Python: {'정상' if python_status['ok'] else '확인 필요'} - {python_status['message']}",
            f"Node.js/npm: {'정상' if node_status['ok'] else '확인 필요'} - {node_status['message']}",
            f"Git: {'정상' if git_status['ok'] else '확인 필요'} - {git_status['message']}",
            f"Cloudflare Tunnel: {'정상' if cloudflared_status['ok'] else '확인 필요'} - {cloudflared_status['message']}",
        ]

        if winget_status is not None:
            lines.append(f"winget: {'정상' if winget_status['ok'] else '확인 필요'} - {winget_status['message']}")

        if homebrew_status is not None:
            lines.append(f"Homebrew: {'정상' if homebrew_status['ok'] else '확인 필요'} - {homebrew_status['message']}")

        self.tool_status_var.set(
            f"Python {'정상' if python_status['ok'] else '필요'} / "
            f"Node {'정상' if node_status['ok'] else '필요'} / "
            f"Git {'정상' if git_status['ok'] else '필요'} / "
            f"Cloudflare {'정상' if cloudflared_status['ok'] else '필요'}"
        )

        self.append_log("system", "[CHECK] 개발 Tool Status 확인")
        for line in lines:
            self.append_log("system", line)

        if show_popup:
            messagebox.showinfo("개발 Tool Status", "\n".join(lines))

        if return_lines:
            return python_status, node_status, cloudflared_status, lines

        return python_status, node_status, cloudflared_status

    def auto_check_tools_on_start(self):
        python_status, node_status, cloudflared_status = self.check_developer_tools(show_popup=False)
        git_status = find_git_status()

        missing = []

        if not python_status["ok"]:
            missing.append("Python")

        if not node_status["ok"]:
            missing.append("Node.js/npm")

        if not git_status["ok"]:
            missing.append("Git")

        if not cloudflared_status["ok"]:
            missing.append("Cloudflare Tunnel")

        if not missing:
            return

        message = (
            "개발 도구 확인 결과, 다음 항목이 설치되어 있지 않거나 PATH에서 찾을 수 없습니다.\n\n"
            + "\n".join(f"- {name}" for name in missing)
            + "\n\n초기 설정 마법사 또는 도구 설정에서 설치 도우미를 실행할 수 있습니다."
        )

        if self.should_show_initial_wizard():
            self.status_var.set("초기 설정 마법사에서 필수 도구 설치 필요")
            return

        answer = messagebox.askyesno("개발 도구 설치 안내", message + "\n\n지금 초기 설정 마법사를 열까요?")
        if answer:
            self.show_initial_wizard()

    def install_python_tool(self):
        command = self.vars["python_install_cmd"].get().strip()

        if not command:
            messagebox.showwarning("명령어 필요", "Python 설치 명령이 비어 있습니다.")
            return

        if not messagebox.askyesno(
            "Python 설치",
            "Python 설치 도우미를 실행할까요?\n\n"
            "설치 과정에서 관리자 권한 요청이나 추가 확인이 뜰 수 있습니다.\n"
            "설치 후에는 런처/터미널을 다시 실행하세요."
        ):
            return

        self.save_current_config(show_popup=False)
        self.append_log("system", f"[INSTALL] Python 설치 도우미 실행: {command}")
        run_command_external_terminal("Eagle Taxi - Python Install", command)

    def install_node_tool(self):
        command = self.vars["node_install_cmd"].get().strip()

        if not command:
            messagebox.showwarning("명령어 필요", "Node.js 설치 명령이 비어 있습니다.")
            return

        if not messagebox.askyesno(
            "Node.js 설치",
            "Node.js 설치 도우미를 실행할까요?\n\n"
            "설치 과정에서 관리자 권한 요청이나 추가 확인이 뜰 수 있습니다.\n"
            "설치 후에는 런처/터미널을 다시 실행하세요."
        ):
            return

        self.save_current_config(show_popup=False)
        self.append_log("system", f"[INSTALL] Node.js 설치 도우미 실행: {command}")
        run_command_external_terminal("Eagle Taxi - Node Install", command)

    def install_homebrew_tool(self):
        if get_system_name() != "Darwin":
            messagebox.showinfo(
                "Homebrew 안내",
                "Homebrew는 macOS에서 주로 사용하는 패키지 관리자입니다.\n"
                "Windows에서는 winget 사용을 권장합니다."
            )
            return

        command = self.vars["homebrew_install_cmd"].get().strip()

        if not command:
            messagebox.showwarning("명령어 필요", "Homebrew 설치 명령이 비어 있습니다.")
            return

        if not messagebox.askyesno(
            "Homebrew 설치",
            "Homebrew 설치 도우미를 실행할까요?\n\n"
            "설치 중 비밀번호 입력이나 추가 확인이 필요할 수 있습니다."
        ):
            return

        self.save_current_config(show_popup=False)
        self.append_log("system", f"[INSTALL] Homebrew 설치 도우미 실행: {command}")
        run_command_external_terminal("Eagle Taxi - Homebrew Install", command)

    def install_cloudflared_tool(self):
        command = self.vars["cloudflared_install_cmd"].get().strip()

        if not command:
            messagebox.showwarning("명령어 필요", "Cloudflare Tunnel 설치 명령이 비어 있습니다.")
            return

        if not messagebox.askyesno(
            "Cloudflare Tunnel 설치",
            "cloudflared 설치 도우미를 실행할까요?\n\n"
            "설치 과정에서 관리자 권한 요청이나 추가 확인이 뜰 수 있습니다.\n"
            "설치 후에는 런처/터미널을 다시 실행하는 것이 안전합니다."
        ):
            return

        self.save_current_config(show_popup=False)
        self.append_log("cloudflare" if "cloudflare" in self.log_widgets else "system", f"[INSTALL] cloudflared 설치 도우미 실행: {command}")
        run_command_external_terminal("Eagle Taxi - Cloudflared Install", command)

    def install_git_tool(self):
        command = get_default_git_install_command()
        if not messagebox.askyesno(
            "Git 설치",
            "Git 설치 도우미를 실행할까요?\n\n설치 후에는 런처/터미널을 다시 실행하는 것이 안전합니다."
        ):
            return
        self.append_log("system", f"[INSTALL] Git 설치 도우미 실행: {command}")
        run_command_external_terminal("Eagle Taxi - Git Install", command)

    def copy_cloudflare_setup_commands(self):
        text = build_cloudflare_setup_commands(
            self.vars["cloudflare_named_tunnel_name"].get(),
            self.vars["cloudflare_service_domain"].get(),
            self.vars["cloudflare_admin_domain"].get(),
            self.vars["cloudflare_named_config_path"].get(),
        )
        self.root.clipboard_clear()
        self.root.clipboard_append(text)
        self.root.update()
        self.append_log("cloudflare", "[COPY] Cloudflare 고정 도메인 설정 명령 복사 완료")
        self.status_var.set("Cloudflare Settings 명령 복사 완료")

    def start_cloudflare_tunnel(self, server_key):
        cloudflared_status = find_cloudflared_status()

        if not cloudflared_status["ok"]:
            answer = messagebox.askyesno(
                "Cloudflare Tunnel 필요",
                "cloudflared가 설치되어 있지 않거나 PATH에서 찾을 수 없습니다.\n\n"
                "지금 설치 도우미를 실행할까요?"
            )
            if answer:
                self.install_cloudflared_tool()
            return

        if server_key not in ["frontend", "admin"]:
            messagebox.showwarning("지원하지 않는 터널", "Service/Admin Quick Tunnel만 지원합니다.")
            return

        info = SERVER_INFO[server_key]
        port = info["port"]
        process_key = f"{server_key}_tunnel"

        if self.is_process_running(process_key):
            self.append_log("cloudflare", f"[TUNNEL] {info['label']} Quick Tunnel이 이미 실행 중입니다.")
            self.update_tunnel_toggle_buttons()
            return

        command = f"{get_cloudflared_command()} tunnel --url http://localhost:{port}"

        self.tunnel_url_vars[server_key].set(f"{info['label']} Quick URL 생성 중...")
        self.refresh_share_text()

        self.start_process(
            process_key=process_key,
            log_key="cloudflare",
            title=f"{info['label']} Quick Cloudflare Tunnel",
            cwd=str(Path.home()),
            command=command,
            server_key=None,
        )

        self.status_var.set(f"{info['label']} Quick Tunnel 시작")
        self.root.after(0, self.update_all_runtime_toggle_buttons)

    def start_all_cloudflare_tunnels(self):
        config_path = get_cloudflare_config_file_path(self.vars["cloudflare_named_config_path"].get())
        if config_path.exists():
            if not self.is_named_tunnel_running():
                self.start_cloudflare_named_tunnel()
            self.status_var.set("Named Tunnel 시작 요청 완료")
            self.root.after(0, self.update_all_runtime_toggle_buttons)
            return

        if not self.is_process_running("frontend_tunnel"):
            self.start_cloudflare_tunnel("frontend")
        if not self.is_process_running("admin_tunnel"):
            self.start_cloudflare_tunnel("admin")
        self.status_var.set("Quick Tunnels 시작 요청 완료")
        self.root.after(0, self.update_all_runtime_toggle_buttons)

    def start_cloudflare_named_tunnel(self):
        cloudflared_status = find_cloudflared_status()

        if not cloudflared_status["ok"]:
            answer = messagebox.askyesno(
                "Cloudflare Tunnel 필요",
                "cloudflared가 설치되어 있지 않거나 PATH에서 찾을 수 없습니다.\n\n"
                "지금 설치 도우미를 실행할까요?"
            )
            if answer:
                self.install_cloudflared_tool()
            return

        if self.is_named_tunnel_running():
            self.append_log("cloudflare", "[TUNNEL] Named Tunnel이 이미 실행 중입니다.")
            self.update_tunnel_toggle_buttons()
            return

        tunnel_name = self.vars["cloudflare_named_tunnel_name"].get().strip() or "eagle-taxi"
        config_path = self.vars["cloudflare_named_config_path"].get().strip() or "~/.cloudflared/eagle-taxi.yml"
        service_url = build_https_url(self.vars["cloudflare_service_domain"].get())
        admin_url = build_https_url(self.vars["cloudflare_admin_domain"].get())
        config_file = get_cloudflare_config_file_path(config_path)

        if not config_file.exists():
            answer = messagebox.askyesno(
                "설정 파일 필요",
                f"Cloudflare Tunnel 설정 파일을 찾지 못했습니다.\n\n{config_file}\n\n"
                "시작 마법사를 열어 로그인/터널 생성/DNS 연결/설정 파일 생성을 진행할까요?"
            )
            if answer:
                self.open_cloudflare_wizard_window()
            return

        command = build_cloudflare_named_tunnel_command(config_path, tunnel_name)

        self.tunnel_url_vars["frontend"].set(service_url)
        self.tunnel_url_vars["admin"].set(admin_url)
        self.refresh_share_text()

        self.start_process(
            process_key="named_tunnel",
            log_key="cloudflare",
            title="Named Cloudflare Tunnel",
            cwd=str(Path.home()),
            command=command,
            server_key=None,
        )

        self.append_log("cloudflare", f"[TUNNEL] Service URL: {service_url}")
        self.append_log("cloudflare", f"[TUNNEL] Admin URL: {admin_url}")
        self.status_var.set("Named Cloudflare Tunnel 시작")
        self.root.after(0, self.update_all_runtime_toggle_buttons)

    def stop_cloudflare_tunnel(self, server_key):
        if server_key not in ["frontend", "admin"]:
            return

        process_key = f"{server_key}_tunnel"
        process = self.processes.get(process_key)
        label = SERVER_INFO[server_key]["label"]

        if process and process.poll() is None:
            self.terminate_process(process_key)
            self.append_log("cloudflare", f"[TUNNEL] {label} Quick Tunnel 중지 요청 완료")
        else:
            self.append_log("cloudflare", f"[TUNNEL] 실행 중인 {label} Quick Tunnel 없음")

        default_text = "서비스 공개 URL 없음" if server_key == "frontend" else "관리자 공개 URL 없음"
        self.tunnel_url_vars[server_key].set(default_text)
        self.refresh_share_text()
        self.update_tunnel_toggle_buttons()
        self.status_var.set(f"{label} Quick Tunnel 중지 요청 완료")

    def stop_cloudflare_tunnels(self):
        for key in ["frontend_tunnel", "admin_tunnel", "named_tunnel"]:
            process = self.processes.get(key)
            if process and process.poll() is not None:
                self.processes.pop(key, None)
                continue
            if process and process.poll() is None:
                self.terminate_process(key)

        self.tunnel_url_vars["frontend"].set("서비스 공개 URL 없음")
        self.tunnel_url_vars["admin"].set("관리자 공개 URL 없음")
        self.refresh_share_text()
        self.update_tunnel_toggle_buttons()

        self.append_log("cloudflare", "[TUNNEL] Cloudflare Tunnel 전체 중지 요청 완료")
        self.status_var.set("Cloudflare Tunnel 전체 중지 요청 완료")

    def copy_cloudflare_urls(self):
        lines = [
            f"Service Frontend: {self.get_tunnel_service_url()}",
            f"Admin Frontend: {self.get_tunnel_admin_url()}",
        ]
        text = "\n".join(lines)

        self.root.clipboard_clear()
        self.root.clipboard_append(text)
        self.root.update()

        self.append_log("cloudflare", "[COPY] Cloudflare 공개 URL 복사 완료")
        self.status_var.set("Cloudflare 공개 URL 복사 완료")


    def handle_process_line(self, process_key, log_key, line):
        tunnel_url = extract_cloudflare_url(line)

        if tunnel_url:
            if process_key == "frontend_tunnel":
                self.root.after(0, lambda url=tunnel_url: self.tunnel_url_vars["frontend"].set(url))
                self.root.after(0, self.refresh_share_text)
                self.output_queue.put(("cloudflare", f"[TUNNEL] Service Frontend Quick URL: {tunnel_url}"))

            elif process_key == "admin_tunnel":
                self.root.after(0, lambda url=tunnel_url: self.tunnel_url_vars["admin"].set(url))
                self.root.after(0, self.refresh_share_text)
                self.output_queue.put(("cloudflare", f"[TUNNEL] Admin Frontend Quick URL: {tunnel_url}"))

        credentials_file = extract_credentials_file_from_cloudflared_output(line)
        if credentials_file:
            self.output_queue.put(("cloudflare", f"[WIZARD] credentials 감지: {credentials_file}"))

        access = parse_access_log_line(line)

        if access:
            self.record_visitor(log_key, access["ip"], access["method"], access["path"])

    def record_visitor(self, source, ip, method, path):
        now = time.strftime("%H:%M:%S")

        item = {
            "time": now,
            "source": source,
            "ip": ip,
            "method": method,
            "path": path,
        }

        self.visitor_events.insert(0, item)
        self.visitor_events = self.visitor_events[:30]

        self.root.after(0, self.update_visitors_panel)

    def update_visitors_panel(self):
        if hasattr(self, "visitor_tree"):
            for item in self.visitor_tree.get_children():
                self.visitor_tree.delete(item)
            # 오래된 항목부터 위, 최신 항목이 아래로 쌓이게 표시한다.
            for event in list(reversed(self.visitor_events[:50])):
                self.visitor_tree.insert(
                    "",
                    "end",
                    values=(
                        event.get("time", ""),
                        event.get("ip", ""),
                        event.get("method", ""),
                        event.get("path", ""),
                    ),
                )
            if time.time() >= getattr(self, "visitor_autoscroll_pause_until", 0):
                try:
                    self.visitor_tree.yview_moveto(1.0)
                except Exception:
                    pass
            return

        if not hasattr(self, "visitor_text"):
            return

        self.visitor_text.configure(state="normal")
        self.visitor_text.delete("1.0", "end")

        if not self.visitor_events:
            self.visitor_text.insert(
                "end",
                "시간 | IP | Method | 경로\n"
                "감지된 접속자가 아직 없습니다.\n"
                "백엔드 [ACCESS] 로그가 출력되면 이 영역에 표시됩니다."
            )
        else:
            self.visitor_text.insert("end", "시간 | IP | Method | 경로\n")
            self.visitor_text.insert("end", "-" * 72 + "\n")
            for event in reversed(self.visitor_events):
                self.visitor_text.insert(
                    "end",
                    f"{event['time']} | {event['ip']} | {event['method']} | {event['path']}\n"
                )
            if time.time() >= getattr(self, "visitor_autoscroll_pause_until", 0):
                self.visitor_text.see("end")

        self.visitor_text.configure(state="disabled")

    def on_close(self):
        running = [
            key for key, process in self.processes.items()
            if process and process.poll() is None
        ]

        if running:
            answer = messagebox.askyesno(
                "종료 확인",
                "실행 중인 서버/작업이 있습니다.\n\n"
                "런처를 종료하면서 프로세스도 중지할까요?"
            )

            if answer:
                for key in list(self.processes.keys()):
                    self.terminate_process(key)

                for server_key in ["backend", "frontend", "admin"]:
                    self.kill_port(SERVER_INFO[server_key]["port"], show_popup=False)
            else:
                return

        self.save_current_config(show_popup=False)
        self.root.destroy()


def main():
    root = tk.Tk()
    EagleTaxiLauncher(root)
    root.mainloop()


if __name__ == "__main__":
    main()
