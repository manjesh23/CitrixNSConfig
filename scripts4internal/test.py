from flask import Flask

app = Flask(__name__)

@app.route('/')
def home():
    return 'Hello, this is the homepage!'

@app.route('/page#<page_number>')
def dynamic_page(page_number):
    return f'You are on page #{page_number}'

if __name__ == '__main__':
    app.run(debug=True)
