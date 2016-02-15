from Constants import *
from ComputerDatabase import ComputerDatabase
from flask import Flask, render_template, request
from itertools import izip
from threading import Thread,Timer
import webbrowser
import sys

app = Flask(__name__)


@app.route('/')
@app.route('/<name>')
def show_main_form(name=None):
    computers_dict = ComputerDatabase().make_dictionary()
    computers = [dict(IP = ip, MAC = mac, STATUS = state) for ip, mac, state in izip(computers_dict['IP'], computers_dict['MAC'], computers_dict['STATUS'])]
    return render_template("MainPage.htm", computers=computers)


def main():
  #  app_thread = Thread(target=app.run)
  #   app_thread.start()
  #  app_thread.join()
    #webbrowser.open(FLASK_URL, autoraise=True)
    webbrowser.open(FLASK_URL)
    app.run()

if __name__ == "__main__":
   main()



