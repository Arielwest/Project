from Constants import *
from flask import Flask, render_template, request, redirect, url_for
from itertools import izip
import webbrowser
from Server import Server
from threading import Thread
from ClientInterface import Computer
from Process import Process

app = Flask(__name__)
server = Server()


@app.route('/', methods=['GET', 'POST'])
def show_main_form():
    if (not server.running) and (not server.starting):
        start_thread = Thread(target=server.start)
        start_thread.setDaemon(True)
        start_thread.start()
        return render_template("Loading.html")
    elif server.starting:
        return render_template("Loading.html")
    elif server.running:
        if request.method == 'POST':
            ip = request.form['Ip']
            mac = request.form['Mac']
            active = request.form['Status'] == "online" or request.form['Status'] == u'online'
            if request.form['Action'] == "More":
                url = url_for("view_computer", mac=mac, ip=ip)
                return redirect(url)
            else:
                if not active:
                    server.wake_up(Computer(mac, ip, False))
                else:
                    server.shutdown(Computer(mac, ip, True))
        computers_dict = server.make_computers_dictionary()
        computers = [dict(IP=ip,MAC=mac, STATUS=state, INDEX=index, CONNECTED=connected) for ip, mac, state, index, connected in izip(computers_dict['IP'], computers_dict['MAC'], computers_dict['STATUS'], computers_dict['INDEX'], computers_dict['CONNECTED'])]
        return render_template("MainPage.html", computers=computers)


@app.route('/view_computer?mac=<mac>&ip=<ip>', methods=['GET', 'POST'])
def view_computer(mac, ip):
    message = ""
    if request.method == 'POST':
        ip = request.form['Ip']
        mac = request.form['Mac']
        name = request.form['Host']
        function = request.form['Action'].lower().replace(' ', '_')
        print function
        print request.form["ProcessName"]
        if function == "open_process":
            message = server.open_process(Computer(mac, ip), request.form["ProcessName"])
        else:
            return redirect(url_for(function, mac=mac, ip=ip, name=name))
    computer_data = server.computer_data(Computer(mac, ip))
    return render_template("InfoPage.html", computer=computer_data, message=message)


@app.route('/view_files?mac=<mac>&ip=<ip>', methods=['GET', 'POST'])
def show_files(mac, ip):
    if request.method == 'POST':
        ip = request.form['Ip']
        mac = request.form['Mac']
        function = request.form['Action']
        pass
    elif request.method == 'GET':
        computer_data = server.computer_data(Computer(mac, ip))
        return render_template("FilesPage.html", computer=computer_data)


@app.route('/view_processes?mac=<mac>&ip=<ip>&name=<name>', methods=['GET', 'POST'])
def show_processes(mac, ip, name):
    message = ""
    computer = Computer(mac, ip)
    if request.method == 'POST':
        process_name = request.form['name']
        pid = request.form['pid']
        parent_id = request.form['parent_id']
        function = request.form['Action']
        if function == "Terminate":
            message = server.terminate_process(computer, Process(process_name, pid, parent_id))
        elif function == "Back":
            return redirect(url_for("view_computer", mac=mac, ip=ip))
    process_list = server.get_processes_data(computer)
    return render_template("ProcessesPage.html", process_list=process_list, mac=mac, ip=ip, name=name, message=message)


def main():
    webbrowser.open(FLASK_URL)
    app.run(host="0.0.0.0")

if __name__ == "__main__":
    main()
