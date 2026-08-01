from __future__ import annotations

import socket
import subprocess
import time
from pathlib import Path
from urllib.request import urlopen

from .contracts import STARTUP_TIMEOUT_SECONDS


def allocate_port() -> int:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.bind(("127.0.0.1", 0))
        return int(sock.getsockname()[1])


class StreamlitProcess:
    def __init__(self, root: Path, log_path: Path) -> None:
        self.root = root
        self.log_path = log_path
        self.port = allocate_port()
        self.process: subprocess.Popen | None = None
        self._log_handle = None

    @property
    def base_url(self) -> str:
        return f"http://127.0.0.1:{self.port}"

    def __enter__(self) -> "StreamlitProcess":
        self.log_path.parent.mkdir(parents=True, exist_ok=True)
        self._log_handle = self.log_path.open("w", encoding="utf-8")
        self.process = subprocess.Popen(
            [
                "python",
                "-m",
                "streamlit",
                "run",
                "app.py",
                "--server.headless=true",
                f"--server.port={self.port}",
                "--browser.gatherUsageStats=false",
            ],
            cwd=self.root,
            stdout=self._log_handle,
            stderr=subprocess.STDOUT,
            text=True,
        )
        deadline = time.monotonic() + STARTUP_TIMEOUT_SECONDS
        while time.monotonic() < deadline:
            if self.process.poll() is not None:
                raise RuntimeError("Streamlit exited before becoming ready.")
            try:
                with urlopen(f"{self.base_url}/_stcore/health", timeout=2) as response:
                    if response.status == 200:
                        return self
            except OSError:
                time.sleep(0.5)
        raise TimeoutError("Streamlit did not become ready within the governed timeout.")

    def __exit__(self, exc_type, exc, tb) -> None:
        if self.process is not None and self.process.poll() is None:
            self.process.terminate()
            try:
                self.process.wait(timeout=10)
            except subprocess.TimeoutExpired:
                self.process.kill()
                self.process.wait(timeout=5)
        if self._log_handle is not None:
            self._log_handle.close()
