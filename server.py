"""
Local Web Server for DAA File Compression Studio.

Launches a lightweight HTTP server serving the interactive web application
and automatically opens the default web browser. Requires zero external dependencies.
"""

import http.server
import socketserver
import webbrowser
import os
import sys

PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
WEB_DIR = os.path.join(PROJECT_ROOT, "web")
PORT = 8000


class CompressionWebHandler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=WEB_DIR, **kwargs)

    def end_headers(self):
        # Enable caching-free live development
        self.send_header("Cache-Control", "no-cache, no-store, must-revalidate")
        self.send_header("Pragma", "no-cache")
        self.send_header("Expires", "0")
        super().end_headers()


def launch_web_server(port: int = PORT, open_browser: bool = True):
    # Allow port reuse to prevent 'Address already in use' errors on quick restarts
    socketserver.TCPServer.allow_reuse_address = True

    try:
        with socketserver.TCPServer(("", port), CompressionWebHandler) as httpd:
            url = f"http://localhost:{port}"
            print("\n" + "=" * 70)
            print("      DAA LOSSLESS FILE COMPRESSION STUDIO - WEB INTERFACE")
            print("=" * 70)
            print(f"🚀 Web Application running live at: {url}")
            print("👉 Open your browser to test Huffman, RLE, and LZW interactive tools.")
            print("🛑 Press Ctrl+C in this terminal to stop the server.")
            print("=" * 70 + "\n")

            if open_browser:
                try:
                    webbrowser.open(url)
                except Exception:
                    pass

            httpd.serve_forever()
    except OSError as e:
        if "Address already in use" in str(e):
            next_port = port + 1
            if next_port == 8001:  # Port 8001 is reserved for the FastAPI compression backend
                next_port = 8002
            print(f"\n[Notice] Port {port} is currently in use. Trying port {next_port}...")
            launch_web_server(port=next_port, open_browser=open_browser)
        else:
            raise e
    except KeyboardInterrupt:
        print("\nWeb server stopped cleanly. Goodbye!")


if __name__ == "__main__":
    launch_web_server()
