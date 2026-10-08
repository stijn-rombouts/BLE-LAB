#!/usr/bin/env python3
"""
Simple HTTP Web Server to display the live Matplotlib temperature plot
Access via browser at http://<RPi-IP>:8080
"""

import http.server
import socketserver
import os

PORT = 8080

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))

def get_plot_path():
    candidates = [
        os.path.join(SCRIPT_DIR, 'temperature_plot.png'),
        os.path.abspath('temperature_plot.png'),
        '/root/temperature_plot.png',
    ]
    for path in candidates:
        if os.path.isfile(path):
            return path
    return candidates[0]

HTML_CONTENT = """<!DOCTYPE html>
<html>
<head>
    <title>RPi 3B+ BLE BMP280 Live Plot</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            background-color: #f4f6f9;
            text-align: center;
            padding: 20px;
        }
        h1 { color: #2c3e50; }
        .card {
            background: white;
            padding: 20px;
            border-radius: 12px;
            display: inline-block;
            box-shadow: 0 4px 15px rgba(0,0,0,0.1);
        }
        img {
            max-width: 100%;
            height: auto;
            border-radius: 8px;
        }
        .footer {
            margin-top: 15px;
            color: #7f8c8d;
            font-size: 0.9em;
        }
    </style>
    <script>
        function refreshImage() {
            var img = document.getElementById('plot-img');
            img.src = '/temperature_plot.png?t=' + new Date().getTime();
        }
        setInterval(refreshImage, 2000);
    </script>
</head>
<body>
    <div class="card">
        <h1>Raspberry Pi 3B+ - BLE Telemetry Dashboard</h1>
        <p>Live BMP280 Temperature Graph (Auto-refreshes every 2s)</p>
        <img id="plot-img" src="/temperature_plot.png" alt="Live Temperature Plot">
        <div class="footer">Connected to Pico W over Bluetooth LE</div>
    </div>
</body>
</html>
"""

class CustomHandler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        # Disable caching for image and html
        if self.path == '/' or self.path == '/index.html':
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.send_header('Cache-Control', 'no-cache, no-store, must-revalidate')
            self.end_headers()
            self.wfile.write(HTML_CONTENT.encode('utf-8'))
        elif 'temperature_plot.png' in self.path:
            plot_file = get_plot_path()
            if os.path.isfile(plot_file):
                try:
                    with open(plot_file, 'rb') as f:
                        content = f.read()
                    self.send_response(200)
                    self.send_header('Content-type', 'image/png')
                    self.send_header('Cache-Control', 'no-cache, no-store, must-revalidate')
                    self.send_header('Content-Length', str(len(content)))
                    self.end_headers()
                    self.wfile.write(content)
                except Exception as e:
                    self.send_error(500, f"Error reading plot file: {e}")
            else:
                self.send_error(404, f"Plot file not generated yet at {plot_file}")
        else:
            super().do_GET()

class ReuseTCPServer(socketserver.TCPServer):
    allow_reuse_address = True

def run_server():
    with ReuseTCPServer(("", PORT), CustomHandler) as httpd:
        print(f"Web Dashboard serving live plot at http://0.0.0.0:{PORT}")
        httpd.serve_forever()

if __name__ == "__main__":
    run_server()
