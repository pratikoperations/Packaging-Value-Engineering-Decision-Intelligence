from __future__ import annotations

import os
import signal
import socket
import subprocess
import sys
import time
import urllib.request
from dataclasses import dataclass
from pathlib import Path

from .contracts import STARTUP_TIMEOUT_SECONDS


def allocate_port() -> int:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.bind(("127.0.0.1", 0))
        return int(sock.getsockname()[1])


@dataclass
class StreamlitProcess:
    root: Path
    artifact_dir: Path
    port: int | None = None
    process: subprocess.Popen[str] | None = None

    def start(self) -> str:
        self.port = self.port or allocate_port()
        self.artifact_dir.mkdir(parents=True, exist_ok=True)
        stdout_path = self.artifact_dir / "streamlit-stdout.log"
        stderr_path = self.artifact_dir / "streamlit-stderr.log"
        self._stdout = stdout_path.open("w", encoding="utf-8")
        self._stderr = stderr_path.open("w", encoding="utf-8")
        command = [
            sys.executable, "-m", "streamlit", "run", "app.py",
            "--server.headless=true", "--server.address=127.0.0.1",
            f"--server.port={self.port}", "--browser.gatherUsageStats=false",
        ]
        kwargs: dict[str, object] = {
            "cwd": str(self.root), "stdout": self._stdout, "stderr": self._stderr,
            "text": True,
        }
        if os.name == "posix":
            kwargs["start_new_session"] = True
        self.process = subprocess.Popen(command, **kwargs)  # type: ignore[arg-type]
        deadline = time.monotonic() + STARTUP_TIMEOUT_SECONDS
        health = f"http://127.0.0.1:{self.port}/_stcore/health"
        while time.monotonic() < deadline:
            if self.process.poll() is not None:
                raise RuntimeError("Streamlit exited before readiness.")
            try:
                with urllib.request.urlopen(health, timeout=1) as response:
                    if response.status == 200:
                        return f"http://127.0.0.1:{self.port}"
            except OSError:
                time.sleep(0.5)
        raise TimeoutError("Streamlit did not become ready within 60 seconds.")

    def stop(self) -> None:
        try:
            if self.process and self.process.poll() is None:
                if os.name == "posix":
                    os.killpg(os.getpgid(self.process.pid), signal.SIGTERM)
                else:
                    self.process.terminate()
                try:
                    self.process.wait(timeout=10)
                except subprocess.TimeoutExpired:
                    if os.name == "posix":
                        os.killpg(os.getpgid(self.process.pid), signal.SIGKILL)
                    else:
                        self.process.kill()
                    self.process.wait(timeout=5)
        finally:
            for stream_name in ("_stdout", "_stderr"):
                stream = getattr(self, stream_name, None)
                if stream:
                    stream.close()

    def __enter__(self) -> "StreamlitProcess":
        self.start()
        return self

    def __exit__(self, *_exc: object) -> None:
        self.stop()
