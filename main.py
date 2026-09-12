"""Tathvyn - Root Entry Point Wrapper.

Delegates execution to backend/main.py with working directory anchored in backend/.
Allows running commands seamlessly from either repository root or backend/.
"""

import os
import subprocess
import sys
from pathlib import Path

if __name__ == "__main__":
    root_dir = Path(__file__).resolve().parent
    backend_dir = root_dir / "backend"
    backend_main = backend_dir / "main.py"

    backend_venv_py = backend_dir / ".venv" / "Scripts" / "python.exe"
    python_bin = str(backend_venv_py) if backend_venv_py.is_file() else sys.executable

    env = os.environ.copy()
    src_dir = str(backend_dir / "src")
    env["PYTHONPATH"] = f"{src_dir}{os.pathsep}{env.get('PYTHONPATH', '')}".rstrip(os.pathsep)

    cmd = [python_bin, str(backend_main)] + sys.argv[1:]
    res = subprocess.run(cmd, cwd=backend_dir, env=env)
    sys.exit(res.returncode)
