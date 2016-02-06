from Constants import *
from flask import Flask
from threading import Thread
import webbrowser
import sys

app = Flask(__name__)


@app.route("/")
def login():
    return "Hello"


def main():
    app_thread = Thread(target=app.run)
    app_thread.start()
    app_thread.join()
    webbrowser.open(FLASK_URL)

if __name__ == "__main__":
    main()
