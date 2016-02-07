from Constants import *
from flask import Flask, render_template, request
from threading import Thread
import webbrowser
import sys

app = Flask(__name__)


@app.route('/', methods=['GET', 'POST'])
def show_main_form():
    return "Nothing, yet"


def main():
    app_thread = Thread(target=app.run)
    app_thread.start()
    app_thread.join()
    webbrowser.open(FLASK_URL)

if __name__ == "__main__":
    main()
