import json
import webbrowser
import mimetypes
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import unquote

import os
import shutil
import subprocess
import sys

BASE = Path(__file__).resolve().parent
DATA = BASE / "Ringkasan_Saham"
HTML = "IRIS.html"  # nama file IRIS
PORT = 8000
EXT = (".xlsx", ".xls", ".csv")


WATCHLIST = BASE / "Watchlist.xlsx"


class Handler(SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=str(BASE), **kwargs)

    def _kirim(self, isi: bytes, tipe: str, cache: str = "no-store"):
        self.send_response(200)
        self.send_header("Content-Type", tipe)
        self.send_header("Content-Length", str(len(isi)))
        self.send_header("Cache-Control", cache)
        self.end_headers()
        self.wfile.write(isi)

    def do_GET(self):
        path = self.path.split("?")[0]
        if path in ("/", "/index.html"):
            self._kirim((BASE / HTML).read_bytes(), "text/html; charset=utf-8")

        elif path == "/api/files":
            nama = sorted(
                f.name for f in DATA.glob("*")
                if f.suffix.lower() in EXT and not f.name.startswith("~$")
            ) if DATA.is_dir() else []
            self._kirim(json.dumps(nama).encode(), "application/json")

        elif path.startswith("/files/"):
            f = DATA / Path(unquote(path[len("/files/"):])).name  # .name mencegah keluar folder
            if f.is_file():
                self._kirim(f.read_bytes(), "application/octet-stream")
            else:
                self.send_error(404)

        elif path.startswith("/images/"):
            f = BASE / "images" / Path(unquote(path[len("/images/"):])).name
            if f.is_file():
                self._kirim(f.read_bytes(), mimetypes.guess_type(f.name)[0] or "application/octet-stream", cache="public, max-age=3600")
            else:
                self.send_error(404)
                
        elif path == "/favicon.ico":
            f = BASE / "images" / "white.png"
            if f.is_file():
                self._kirim(f.read_bytes(), "image/png")
            else:
                self.send_error(404)

        elif path == "/api/watchlist":
            if WATCHLIST.is_file():
                self._kirim(WATCHLIST.read_bytes(), "application/octet-stream")
            else:
                self.send_error(404)
        
        else:
            self.send_error(404)

    def log_message(self, *args):
        pass  # tidak perlu log tiap permintaan


def buka_edge(url: str) -> bool:
    """Buka url khusus di Microsoft Edge. Return False kalau Edge tidak ditemukan."""
    if sys.platform.startswith("win"):
        kandidat = [
            shutil.which("msedge"),
            r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
            r"C:\Program Files\Microsoft\Edge\Application\msedge.exe",
        ]
        for k in kandidat:
            if k and os.path.exists(k):
                subprocess.Popen([k, url])
                return True
    elif sys.platform == "darwin":
        return subprocess.run(["open", "-a", "Microsoft Edge", url]).returncode == 0
    else:
        for nama in ("microsoft-edge", "microsoft-edge-stable", "msedge"):
            p = shutil.which(nama)
            if p:
                subprocess.Popen([p, url])
                return True
    return False


if __name__ == "__main__":
    DATA.mkdir(exist_ok=True)
    server = ThreadingHTTPServer(("127.0.0.1", PORT), Handler)  # hanya bisa diakses dari komputer ini
    url = f"http://localhost:{PORT}"
    print(f"IRIS berjalan di {url}  (Ctrl+C untuk berhenti)")
    print(f"Folder data: {DATA}")
    if not buka_edge(url):
        print(f"Microsoft Edge tidak ditemukan. Buka manual di Edge: {url}")
    try:
        server.serve_forever()  # baris ini yang menjaga server tetap hidup
    except KeyboardInterrupt:
        print("\nIRIS dihentikan.")