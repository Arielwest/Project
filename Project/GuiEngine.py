from Constants import *
from ComputerDatabase import ComputerDatabase
from flask import Flask, render_template, request, url_for
from itertools import izip
import webbrowser

import WakeOnLan

app = Flask(__name__)


@app.route('/', methods=['GET', 'POST'])
def show_main_form():
    if request.method == 'POST':
        if request.form['Action'] == "Info":
            pass
        else:
            ip = request.form['Ip']
            mac = request.form['Mac']
            status = request.form['Status']
            if status == "offline":
                WakeOnLan.wake_on_lan(mac)
                ComputerDatabase().update_state(mac)
            else:
                WakeOnLan.shutdown(ip)
                ComputerDatabase().update_state(ip)
    computers_dict = ComputerDatabase().make_dictionary()
    computers = [dict(IP=ip, MAC=mac, STATUS=state, INDEX=index) for ip, mac, state, index in izip(computers_dict['IP'], computers_dict['MAC'], computers_dict['STATUS'], computers_dict['INDEX'])]
    return render_template("MainPage.htm", computers=computers)


def main():
    webbrowser.open(FLASK_URL)
    app.run()

if __name__ == "__main__":
    main()
