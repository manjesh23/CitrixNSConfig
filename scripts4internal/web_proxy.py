import http.server
import socketserver
import urllib.request
from urllib.parse import urlparse

PORT = 8080

class Proxy(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        # Parse the requested URL
        parsed_url = urlparse(self.path)
        # Build the full URL
        full_url = parsed_url.geturl()

        try:
            # Forward the request to the actual server
            with urllib.request.urlopen(full_url) as response:
                # Send response headers to the client
                self.send_response(response.getcode())
                for header in response.getheaders():
                    self.send_header(header[0], header[1])
                self.end_headers()
                
                # Send the content to the client
                self.wfile.write(response.read())

        except Exception as e:
            self.send_error(500, f"Error: {e}")

    def do_POST(self):
        # Handle POST requests by forwarding them like GET requests
        content_length = int(self.headers['Content-Length'])
        post_data = self.rfile.read(content_length)

        parsed_url = urlparse(self.path)
        full_url = parsed_url.geturl()

        try:
            req = urllib.request.Request(full_url, data=post_data)
            req.add_header('Content-Type', self.headers['Content-Type'])

            with urllib.request.urlopen(req) as response:
                self.send_response(response.getcode())
                for header in response.getheaders():
                    self.send_header(header[0], header[1])
                self.end_headers()
                
                self.wfile.write(response.read())

        except Exception as e:
            self.send_error(500, f"Error: {e}")

if __name__ == "__main__":
    with socketserver.TCPServer(("", PORT), Proxy) as httpd:
        print(f"Serving at port {PORT}")
        httpd.serve_forever()
