import json
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


APP_NAME = "Eagle Taxi Dev Launcher"
APP_VERSION = "v.0.1.0-alpha"
APP_TITLE = f"{APP_NAME} {APP_VERSION}"
APP_CONFIG_VERSION = 5
CONFIG_FILE = Path.home() / ".eagle_taxi_launcher_config.json"


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
    macOS .app / Windows / Linux 실행 환경에서 터미널 PATH가 누락되는 문제를 보완한다.
    특히 macOS Finder에서 .app으로 실행하면 /opt/homebrew/bin, /usr/local/bin을 못 잡는 경우가 많다.
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
    런처가 .app/.exe로 실행되어도 node/npm/python을 찾을 수 있도록 PATH를 보강한다.
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
        "label": "백엔드",
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
        "label": "사용자 프론트",
        "short": "User Front",
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
        "label": "관리자 프론트",
        "short": "Admin Front",
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
        self.tool_status_var = tk.StringVar(value="상태 확인 전")

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

        style.configure(".", font=(self.font_family, 10))
        style.configure("Title.TLabel", font=(self.font_family, 21, "bold"))
        style.configure("Subtle.TLabel", font=(self.font_family, 9))
        style.configure("Version.TLabel", font=(self.font_family, 11, "bold"), foreground="#555555")
        style.configure("Card.TLabelframe", padding=8)
        style.configure("Card.TLabelframe.Label", font=(self.font_family, 10, "bold"))
        style.configure("Primary.TButton", font=(self.font_family, 10, "bold"), padding=(10, 5))
        style.configure("Small.TButton", padding=(8, 4))
        style.configure("Danger.TButton", padding=(8, 4))
        style.configure("Status.TLabel", font=(self.font_family, 10, "bold"))

    def build_ui(self):
        shell = ttk.Frame(self.root, padding=14)
        shell.pack(fill="both", expand=True)

        header = ttk.Frame(shell)
        header.pack(fill="x", pady=(0, 10))

        title_group = ttk.Frame(header)
        title_group.pack(side="left", anchor="w")

        ttk.Label(
            title_group,
            text=APP_NAME,
            style="Title.TLabel",
        ).pack(side="left", anchor="w")

        ttk.Label(
            title_group,
            text=f" {APP_VERSION}",
            style="Version.TLabel",
        ).pack(side="left", anchor="w", padx=(4, 0), pady=(8, 0))

        right_header = ttk.Frame(header)
        right_header.pack(side="right", anchor="e")

        ttk.Label(
            right_header,
            text=f"OS: {get_os_label()}",
            style="Status.TLabel",
        ).pack(anchor="e")

        self.main_pane = ttk.PanedWindow(shell, orient="vertical")
        self.main_pane.pack(fill="both", expand=True)

        menu_area = ttk.Frame(self.main_pane)
        console_area = ttk.Frame(self.main_pane)

        self.main_pane.add(menu_area, weight=3)
        self.main_pane.add(console_area, weight=2)

        self.build_menu_area(menu_area)
        self.build_console_panel(console_area)

    def set_initial_sash_position(self):
        try:
            height = self.main_pane.winfo_height()
            self.main_pane.sashpos(0, int(height * 0.58))
        except Exception:
            pass

    def build_menu_area(self, parent):
        parent.columnconfigure(0, weight=1)
        parent.columnconfigure(1, weight=1)
        parent.columnconfigure(2, weight=1)
        parent.rowconfigure(0, weight=1)
        parent.rowconfigure(1, weight=1)

        access_card = self.create_access_card(parent)
        access_card.grid(row=0, column=0, sticky="nsew", padx=(0, 6), pady=(0, 6))

        backend_card = self.create_server_card(parent, "backend")
        backend_card.grid(row=0, column=1, sticky="nsew", padx=6, pady=(0, 6))

        tool_card = self.create_tool_card(parent)
        tool_card.grid(row=0, column=2, sticky="nsew", padx=(6, 0), pady=(0, 6))

        action_card = self.create_action_card(parent)
        action_card.grid(row=1, column=0, sticky="nsew", padx=(0, 6), pady=(6, 0))

        frontend_card = self.create_server_card(parent, "frontend")
        frontend_card.grid(row=1, column=1, sticky="nsew", padx=6, pady=(6, 0))

        admin_card = self.create_server_card(parent, "admin")
        admin_card.grid(row=1, column=2, sticky="nsew", padx=(6, 0), pady=(6, 0))

    def create_access_card(self, parent):
        frame = ttk.LabelFrame(parent, text="접속 주소", style="Card.TLabelframe")

        ip_row = ttk.Frame(frame)
        ip_row.pack(fill="x", pady=(0, 5))

        ttk.Label(ip_row, text="IPv4", width=6).pack(side="left")
        ttk.Entry(ip_row, textvariable=self.ip_var).pack(side="left", fill="x", expand=True, padx=5)

        ttk.Button(
            ip_row,
            text="새로고침",
            command=self.refresh_ip,
            style="Small.TButton",
        ).pack(side="left")

        self.share_text = tk.Text(
            frame,
            height=3,
            wrap="word",
            font=(self.font_family, 9),
            relief="solid",
            borderwidth=1,
        )
        self.share_text.pack(fill="both", expand=True, pady=(2, 5))
        self.share_text.configure(state="disabled")

        button_row = ttk.Frame(frame)
        button_row.pack(fill="x")

        ttk.Button(
            button_row,
            text="공유 주소 복사",
            command=self.copy_share_info,
            style="Small.TButton",
        ).pack(side="left", fill="x", expand=True, padx=(0, 3))

        ttk.Button(
            button_row,
            text="로컬 열기",
            command=self.open_all_local_urls,
            style="Small.TButton",
        ).pack(side="left", fill="x", expand=True, padx=(3, 0))

        self.refresh_share_text()
        return frame

    def create_action_card(self, parent):
        frame = ttk.LabelFrame(parent, text="전체 작업", style="Card.TLabelframe")

        grid = ttk.Frame(frame)
        grid.pack(fill="both", expand=True)

        for i in range(2):
            grid.columnconfigure(i, weight=1)

        buttons = [
            ("프로젝트 경로 자동 설정", self.auto_set_project_paths, "Small.TButton"),
            ("자동 명령 갱신", lambda: self.reset_auto_commands(show_popup=True), "Small.TButton"),
            ("전체 의존성 설치", self.install_all_dependencies, "Small.TButton"),
            ("전체 서버 실행", self.run_all_servers, "Primary.TButton"),
            ("전체 서버 중지", self.stop_all_servers, "Danger.TButton"),
            ("설정 저장", self.save_current_config, "Small.TButton"),
        ]

        for index, (text, command, style_name) in enumerate(buttons):
            row = index // 2
            col = index % 2

            ttk.Button(
                grid,
                text=text,
                command=command,
                style=style_name,
            ).grid(row=row, column=col, sticky="ew", padx=3, pady=3)

        return frame

    def create_tool_card(self, parent):
        frame = ttk.LabelFrame(parent, text="도구 상태", style="Card.TLabelframe")

        ttk.Label(
            frame,
            textvariable=self.tool_status_var,
            style="Status.TLabel",
        ).pack(anchor="w", pady=(0, 8))

        ttk.Label(
            frame,
            text="Python 3.12 / Node.js / npm 상태 확인",
            style="Subtle.TLabel",
        ).pack(anchor="w", pady=(0, 8))

        button_row = ttk.Frame(frame)
        button_row.pack(fill="x")

        ttk.Button(
            button_row,
            text="상태 확인",
            command=lambda: self.check_developer_tools(show_popup=True),
            style="Small.TButton",
        ).pack(side="left", fill="x", expand=True, padx=(0, 3))

        ttk.Button(
            button_row,
            text="설치/명령 설정",
            command=self.open_tool_settings_window,
            style="Small.TButton",
        ).pack(side="left", fill="x", expand=True, padx=(3, 0))

        return frame

    def create_server_card(self, parent, server_key):
        info = SERVER_INFO[server_key]

        frame = ttk.LabelFrame(
            parent,
            text=f"{info['label']} · {info['port']}",
            style="Card.TLabelframe",
        )

        status_var = tk.StringVar(value="중지됨")
        self.server_status_vars[server_key] = status_var

        status_row = ttk.Frame(frame)
        status_row.pack(fill="x", pady=(0, 5))

        ttk.Label(status_row, textvariable=status_var, style="Status.TLabel").pack(side="left")
        ttk.Label(status_row, textvariable=self.path_summary_vars[server_key], style="Subtle.TLabel").pack(side="right")

        url_label = ttk.Label(
            frame,
            text=info["local_url"],
            style="Subtle.TLabel",
        )
        url_label.pack(anchor="w", pady=(0, 6))

        row_1 = ttk.Frame(frame)
        row_1.pack(fill="x", pady=2)

        ttk.Button(
            row_1,
            text="설정",
            command=lambda key=server_key: self.open_server_settings_window(key),
            style="Small.TButton",
        ).pack(side="left", fill="x", expand=True, padx=(0, 3))

        ttk.Button(
            row_1,
            text="의존성",
            command=lambda key=server_key: self.install_dependencies(key),
            style="Small.TButton",
        ).pack(side="left", fill="x", expand=True, padx=3)

        if server_key == "backend":
            ttk.Button(
                row_1,
                text=".venv",
                command=self.create_backend_venv,
                style="Small.TButton",
            ).pack(side="left", fill="x", expand=True, padx=(3, 0))

        row_2 = ttk.Frame(frame)
        row_2.pack(fill="x", pady=2)

        ttk.Button(
            row_2,
            text="실행",
            command=lambda key=server_key: self.run_server(key),
            style="Primary.TButton",
        ).pack(side="left", fill="x", expand=True, padx=(0, 3))

        ttk.Button(
            row_2,
            text="중지",
            command=lambda key=server_key: self.stop_server(key),
            style="Danger.TButton",
        ).pack(side="left", fill="x", expand=True, padx=3)

        ttk.Button(
            row_2,
            text="열기",
            command=lambda key=server_key: webbrowser.open(SERVER_INFO[key]["local_url"]),
            style="Small.TButton",
        ).pack(side="left", fill="x", expand=True, padx=(3, 0))

        return frame

    def build_console_panel(self, parent):
        frame = ttk.LabelFrame(parent, text="콘솔 로그", style="Card.TLabelframe")
        frame.pack(fill="both", expand=True, pady=(10, 0))

        top = ttk.Frame(frame)
        top.pack(fill="x", pady=(0, 5))

        left_top = ttk.Frame(top)
        left_top.pack(side="left", fill="x", expand=True)

        ttk.Label(
            left_top,
            textvariable=self.status_var,
            style="Status.TLabel",
        ).pack(anchor="w", pady=(2, 0))

        ttk.Button(
            top,
            text="전체 로그 지우기",
            command=self.clear_all_logs,
            style="Small.TButton",
        ).pack(side="right", anchor="n")

        self.log_notebook = ttk.Notebook(frame)
        self.log_notebook.pack(fill="both", expand=True)

        for key, title in [
            ("backend", "백엔드"),
            ("frontend", "사용자 프론트"),
            ("admin", "관리자 프론트"),
            ("system", "시스템"),
        ]:
            tab = ttk.Frame(self.log_notebook)
            self.log_notebook.add(tab, text=title)

            text = tk.Text(
                tab,
                wrap="word",
                font=("Menlo" if get_system_name() == "Darwin" else "Consolas", 10),
                bg="#101418",
                fg="#E9EEF2",
                insertbackground="#E9EEF2",
                relief="flat",
                borderwidth=0,
            )
            text.pack(side="left", fill="both", expand=True)

            scrollbar = ttk.Scrollbar(tab, command=text.yview)
            scrollbar.pack(side="right", fill="y")
            text.configure(yscrollcommand=scrollbar.set)

            self.log_widgets[key] = text

        self.append_log("system", f"[READY] {APP_TITLE}")
        self.append_log("system", f"[OS] {get_os_label()}")
        self.append_log("system", f"[IPv4] {self.ip_var.get()}")
        self.append_log("system", "[PORT] Backend 8000 / Admin 5173 / User Front 5174")
        self.append_log("system", "[INFO] 백엔드는 backend/.venv가 있으면 해당 Python을 우선 사용합니다.")
        self.append_log("system", "[INFO] Windows에서는 py -3.12, npm.cmd, taskkill 기준으로 동작하도록 보완했습니다.")

    # --------------------------------------------------------
    # 설정 창
    # --------------------------------------------------------

    def open_tool_settings_window(self):
        win = tk.Toplevel(self.root)
        win.title("개발 도구 상태 / 설치 설정")
        win.geometry("940x420")
        win.transient(self.root)

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
            python_status, node_status, lines = self.check_developer_tools(show_popup=False, return_lines=True)

            status_box.configure(state="normal")
            status_box.delete("1.0", "end")
            status_box.insert("end", "\n".join(lines))
            status_box.configure(state="disabled")

        refresh_status()

        rows = [
            ("Python 설치 명령", "python_install_cmd"),
            ("Node.js 설치 명령", "node_install_cmd"),
            ("Homebrew 설치 명령", "homebrew_install_cmd"),
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
            text="저장 후 닫기",
            command=lambda: [self.save_current_config(show_popup=False), win.destroy()],
            style="Primary.TButton",
        ).pack(side="right")

    def open_server_settings_window(self, server_key):
        info = SERVER_INFO[server_key]

        win = tk.Toplevel(self.root)
        win.title(f"{info['label']} 설정")
        win.geometry("980x440")
        win.transient(self.root)

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
            lines.append("- 사용자 프론트는 5174, 관리자 프론트는 5173으로 고정했습니다.")

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
            messagebox.showinfo("자동 명령 갱신", "전체 서버의 설치/실행 명령을 현재 경로 기준으로 다시 생성했습니다.")

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
            self.append_log("system", f"[PATH] 프로젝트 경로 자동 설정: {root}")
        else:
            messagebox.showwarning(
                "자동 설정 실패",
                f"현재 위치 기준으로 backend/frontend/admin 폴더를 찾지 못했습니다.\n\n{root}"
            )

    def collect_config(self):
        return {key: var.get().strip() for key, var in self.vars.items()}

    def save_current_config(self, show_popup=True):
        self.config.update(self.collect_config())
        save_config(self.config)
        self.status_var.set("설정 저장 완료")
        self.append_log("system", f"[CONFIG] 설정 저장: {CONFIG_FILE}")

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
        if not hasattr(self, "share_text"):
            return

        ip = self.ip_var.get().strip()

        lines = [
            f"백엔드: {build_share_url('backend', ip)}",
            f"관리자: {build_share_url('admin', ip)}",
            f"사용자: {build_share_url('frontend', ip)}",
        ]

        self.share_text.configure(state="normal")
        self.share_text.delete("1.0", "end")
        self.share_text.insert("end", "\n".join(lines))
        self.share_text.configure(state="disabled")

    def copy_share_info(self):
        self.refresh_share_text()
        text = self.share_text.get("1.0", "end").strip()

        self.root.clipboard_clear()
        self.root.clipboard_append(text)
        self.root.update()

        self.status_var.set("공유 주소 복사 완료")
        self.append_log("system", "[COPY] 공유 주소 복사 완료")

    def open_all_local_urls(self):
        webbrowser.open(SERVER_INFO["backend"]["local_url"])
        webbrowser.open(SERVER_INFO["admin"]["local_url"])
        webbrowser.open(SERVER_INFO["frontend"]["local_url"])

    # --------------------------------------------------------
    # 로그
    # --------------------------------------------------------

    def append_log(self, log_key, message):
        widget = self.log_widgets.get(log_key) or self.log_widgets.get("system")

        if widget is None:
            return

        widget.configure(state="normal")
        widget.insert("end", message + "\n")
        widget.see("end")
        widget.configure(state="normal")

    def process_log_queue(self):
        try:
            while True:
                log_key, message = self.output_queue.get_nowait()
                self.append_log(log_key, message)
        except queue.Empty:
            pass

        self.root.after(100, self.process_log_queue)

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

        self.status_var.set(f"{title} 시작")
        self.log_notebook.select(self.log_widgets[log_key].master)

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
                    self.output_queue.put((log_key, line.rstrip("\n")))

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
                self.root.after(0, lambda: self.server_status_vars[server_key].set("중지됨"))

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

        self.status_var.set("전체 의존성 설치 시작")

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
            self.run_server(server_key)

        self.refresh_ip()
        self.status_var.set("전체 서버 실행 시작")

    def stop_server(self, server_key):
        process_key = f"{server_key}_run"
        process = self.processes.get(process_key)

        info = SERVER_INFO[server_key]

        if process and process.poll() is None:
            self.terminate_process(process_key)

        self.kill_port(info["port"], show_popup=False)
        self.server_status_vars[server_key].set("중지됨")
        self.append_log(server_key, f"[STOP] {info['port']} 포트 종료 요청 완료")
        self.status_var.set(f"{info['label']} 중지 요청 완료")

    def stop_all_servers(self):
        for server_key in ["backend", "frontend", "admin"]:
            self.stop_server(server_key)

        self.status_var.set("전체 서버 중지 요청 완료")
        messagebox.showinfo("전체 서버 중지", "8000, 5173, 5174 포트 종료 요청을 완료했습니다.")

    # --------------------------------------------------------
    # 개발 도구
    # --------------------------------------------------------

    def check_developer_tools(self, show_popup=True, return_lines=False):
        python_status = find_python_status()
        node_status = find_node_status()
        winget_status = find_winget_status()
        homebrew_status = find_homebrew_status()

        lines = [
            f"운영체제: {get_os_label()}",
            f"IPv4: {self.ip_var.get()}",
            "",
            f"Python: {'정상' if python_status['ok'] else '확인 필요'} - {python_status['message']}",
            f"Node.js/npm: {'정상' if node_status['ok'] else '확인 필요'} - {node_status['message']}",
        ]

        if winget_status is not None:
            lines.append(f"winget: {'정상' if winget_status['ok'] else '확인 필요'} - {winget_status['message']}")

        if homebrew_status is not None:
            lines.append(f"Homebrew: {'정상' if homebrew_status['ok'] else '확인 필요'} - {homebrew_status['message']}")

        self.tool_status_var.set(
            f"Python {'정상' if python_status['ok'] else '필요'} / "
            f"Node {'정상' if node_status['ok'] else '필요'}"
        )

        self.append_log("system", "[CHECK] 개발 도구 상태 확인")
        for line in lines:
            self.append_log("system", line)

        if show_popup:
            messagebox.showinfo("개발 도구 상태", "\n".join(lines))

        if return_lines:
            return python_status, node_status, lines

        return python_status, node_status

    def auto_check_tools_on_start(self):
        python_status, node_status = self.check_developer_tools(show_popup=False)

        missing = []

        if not python_status["ok"]:
            missing.append("Python")

        if not node_status["ok"]:
            missing.append("Node.js/npm")

        if not missing:
            return

        message = (
            "개발 도구 확인 결과, 다음 항목이 설치되어 있지 않거나 PATH에서 찾을 수 없습니다.\n\n"
            + "\n".join(f"- {name}" for name in missing)
            + "\n\n설치 도우미를 사용할 수 있습니다.\n"
            "설치 후에는 런처와 터미널을 다시 실행하는 것이 안전합니다."
        )

        answer = messagebox.askyesno("개발 도구 설치 안내", message + "\n\n지금 설치 도우미를 실행할까요?")

        if not answer:
            return

        if not python_status["ok"]:
            self.install_python_tool()

        if not node_status["ok"]:
            self.install_node_tool()

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

    # --------------------------------------------------------
    # 종료
    # --------------------------------------------------------

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
