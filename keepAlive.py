from flask import Flask
from threading import Thread
import logging

# 關閉 Flask 的預設日誌
log = logging.getLogger('werkzeug')
log.setLevel(logging.ERROR)

app = Flask('')

@app.route('/')
def home():
    return "Bot is alive!"

@app.route('/health')
def health_check():
    return 'OK'

def run():
    app.run(host='0.0.0.0', port=8080)

def keep_alive():
    t = Thread(target=run)
    t.start()