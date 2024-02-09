from flask import Flask, request

app = Flask(__name__)

@app.route('/host')
def hello_world():
    # Check if the 'Authorization' header is present
    if 'Authorization' in request.headers:
        # Check if the value of the 'Authorization' header is correct (Base64 encoded 'admin:admin')
        if request.headers['Authorization'] == 'Basic YWRtaW46YWRtaW4=':
            return 'Hello, World! - Authorized'
        else:
            return 'Unauthorized', 401  # Return 401 Unauthorized if the header value is incorrect
    else:
        return 'Unauthorized', 401  # Return 401 Unauthorized if the 'Authorization' header is not present

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000)
