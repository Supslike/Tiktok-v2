# MAIN IMPORTS
from threading import Thread
from flask import Flask, render_template

# Flask app
app = Flask('Naoki v2')

# Main page where bot's avatar is used
@app.route('/')
def home():
  bot_status = True
  bot_name = "Naoki"
  bot_description = "Your reliable tiktok downloader is now online!"
  return render_template('index.html', bot_name=bot_name, bot_description=bot_description, bot_online=bot_status)

# Run
def run():
  app.run(host='0.0.0.0',port=0000)

# Runs flask in background
def keep_alive():
  Thread(target=run).start()