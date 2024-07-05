import os
from flask import Flask, render_template

app = Flask(__name__, static_folder='botsigs')

# Define the directory where botsigs are stored
bot_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'botsigs')

index_file_path = os.path.join(bot_dir, 'BotSignatureMapping.json')

@app.route('/BotSignatureMapping.json')
def get_bot_signature_mapping():
    return render_template('BotSignatureMapping.json')

if __name__ == '__main__':
    app.run(host='10.110.23.30', port=80, debug=True)
