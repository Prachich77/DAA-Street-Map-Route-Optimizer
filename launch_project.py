"""One-click local launcher. Place beside main.py."""
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
import subprocess
import sys
import webbrowser

BASE = Path(__file__).resolve().parent

def main():
    if not (BASE / "main.py").is_file():
        print("ERROR: Put launch_project.py and START_PROJECT.bat beside main.py.")
        return 1
    print("Generating the route report. Please wait...")
    result = subprocess.run([sys.executable, str(BASE / "main.py"), "--no-browser"], cwd=BASE)
    if result.returncode != 0:
        print("Project generation failed. Read the error above; no old report was opened.")
        return result.returncode
    report = BASE / "results" / "street_map.html"
    if not report.is_file():
        print("ERROR: results/street_map.html was not generated.")
        return 1
    handler = partial(SimpleHTTPRequestHandler, directory=str(BASE / "results"))
    # Request a free local port, avoiding conflicts with an earlier demo server.
    with ThreadingHTTPServer(("127.0.0.1", 0), handler) as server:
        url = f"http://127.0.0.1:{server.server_port}/street_map.html"
        print("Open:", url)
        print("Keep this window open during your presentation.")
        print("Press Ctrl+C to stop the server.")
        if not webbrowser.open(url):
            print("Browser did not open automatically. Copy the address above.")
        try:
            server.serve_forever()
        except KeyboardInterrupt:
            print("\nDemo server stopped.")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
