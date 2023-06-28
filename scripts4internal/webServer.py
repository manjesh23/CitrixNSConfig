import logging
from flask import Flask, request

app = Flask(__name__)

@app.route('/')
def hello():
    logging.info('{:-^87}'.format('HTTP Request Header Details Start') + "\n")
    logging.info(f"HTTP Request: {request.method} {request.url}")
    logging.info(f"HTTP Headers: {request.headers}")
    logging.info(f"HTTP Body: {request.data.decode('utf-8')}")
    logging.info('{:-^87}'.format('HTTP Request Header Details End') + "\n")
    logging.info('{:-^87}'.format('HTTP Response Header Details Start') + "\n")
    response = app.make_response(f"<style>div{{background-color:#d3d3d3;border:15px solid #000;text-align:center;padding:50px;margin:20px;font-weight:700;font-size:2.5em}}</style><div>HTTP Server on port {port}<br><br>{message}</div>")
    logging.info(f"HTTP Response: {response.status_code}")
    logging.info(f"HTTP Headers: {response.headers}")
    logging.info(response)
    logging.info('{:-^87}'.format('HTTP Response Header Details End') + "\n")
    return response

if __name__ == '__main__':
    # Prompt user for port number
    port = input("Enter the LISTEN port number: ")

    # Prompt user for message
    message = input("Enter the message to display as HTML Body: ")

    # Configure logging
    logging.basicConfig(level=logging.INFO)

    # Run the Flask app on all interfaces
    from waitress import serve
    serve(app, host='0.0.0.0', port=port)
