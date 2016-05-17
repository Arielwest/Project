# region ---------------------------- ABOUT ----------------------------
"""
##################################################################
# Created By: Ariel Westfried                                    #
# Date: 01/01/2016                                               #
# Name: Project - GuiEngine                                      #
# Version: 1.0                                                   #
# Windows Tested Versions: Win 7 32-bit                          #
# Python Tested Versions: 2.6 32-bit                             #
# Python Environment  : PyCharm                                  #
##################################################################
"""
# endregion

# region ---------------------------- IMPORTS ----------------------------
from Constants import *
from flask import Flask, render_template, request, redirect, url_for, safe_join, send_from_directory
from itertools import izip
import webbrowser
from Server import Server
from threading import Thread
from ClientInterface import Computer
from Process import Process
# endregion

# region ---------------------------- FLASK METHODS ----------------------------

app = Flask(__name__)
server = Server()


def unicode_to_list(unicode):
    return [item[2:-1] for item in unicode[1:-1].split(', ')]


# handles MAinPage.html
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
            if request.form['Action'] == "More":
                ip = request.form['Ip']
                mac = request.form['Mac']
                url = url_for("view_computer", mac=mac, ip=ip)
                return redirect(url)
            elif request.form['Action'] == "Remote Desktop":
                computers = request.form.getlist('check')
                computer_list = [Computer(comp.split('_')[0], comp.split('_')[1]) for comp in computers]
                server.remote_desktop(computer_list)
            elif request.form['Action'] == "Add Computer Manually":
                return redirect(url_for('add_computer'))
            else:
                action = request.form['Action']
                if action == 'WakeOnLAN':
                    action = 'wake up'
                else:
                    action = 'shutdown'
                computer_list = request.form.getlist('check')
                return redirect(url_for('wake_on_lan', computer_list=str(computer_list), action=action))
        computers_dict = server.make_computers_dictionary()
        computers = [dict(IP=ip,MAC=mac, STATUS=state, INDEX=index, CONNECTED=connected) for ip, mac, state, index, connected in izip(computers_dict['IP'], computers_dict['MAC'], computers_dict['STATUS'], computers_dict['INDEX'], computers_dict['CONNECTED'])]
        return render_template("MainPage.html", computers=computers)


# handles AddPage.html
@app.route('/add_computer', methods=['GET', 'POST'])
def add_computer():
    message = ""
    if request.method == 'POST':
        ip = request.form['Ip']
        mac = request.form['Mac']
        message = server.and_computer(Computer(mac, ip, False))
    return render_template('AddPage.html', message=message)


# handles Downloading
@app.route('/download_file?mac=<mac>&ip=<ip>&directory=<path:directory>&item=<item>', methods=['GET'])
def download_file(mac, ip, directory, item):
    file_to_send = server.download(Computer(mac, ip), safe_join(directory, item))
    return send_from_directory(DOWNLOAD_UPLOAD, file_to_send)


# handles InfoPage.html
@app.route('/view_computer?mac=<mac>&ip=<ip>', methods=['GET', 'POST'])
def view_computer(mac, ip):
    message = ""
    if request.method == 'POST':
        ip = request.form['Ip']
        mac = request.form['Mac']
        name = request.form['Host']
        function = request.form['Action'].lower().replace(' ', '_')
        if function == "open_process":
            message = server.open_process(Computer(mac, ip), request.form["ProcessName"])
        elif function == 'show_files':
            return redirect(url_for(function, mac=mac, ip=ip, name=name, path=str(EMPTY_PATH)))
        else:
            return redirect(url_for(function, mac=mac, ip=ip, name=name))
    computer_data = server.computer_data(Computer(mac, ip))
    return render_template("InfoPage.html", computer=computer_data, message=message)


# handles FilesPage.html
@app.route('/view_files?mac=<mac>&ip=<ip>&name=<name>&path=<path:path>', methods=['GET', 'POST'])
def show_files(mac, ip, name, path):
    message = ""
    if request.method == 'POST':
        action = request.form['Action']
        if action == 'Open':
            if path == EMPTY_PATH:
                path = ""
            else:
                path += '\\'
            return redirect(url_for('show_files', mac=mac, ip=ip, name=name, path=path + request.form['FileName']))
        elif action == 'Create':
            message = server.create_file(Computer(mac, ip), path, request.form['FileName'])
        else:
            message = server.delete_file(Computer(mac, ip), safe_join(path, request.form['FileName']))
    directory = server.get_file(Computer(mac, ip), path)
    if "ERROR" in directory['ITEMS']:
        message = directory['ITEMS']
        directory['ITEMS'] = []
    return render_template("FilesPage.html", directory=directory, mac=mac, ip=ip, name=name, message=message)


# handles ProcessesPage.html
@app.route('/view_processes?mac=<mac>&ip=<ip>&name=<name>', methods=['GET', 'POST'])
def show_processes(mac, ip, name):
    message = ""
    computer = Computer(mac, ip)
    if request.method == 'POST':
        process_list = request.form.getlist('check')
        function = request.form['Action']
        if function == "Terminate":
            new_list = []
            for process in process_list:
                process_name, pid, parent_pid = process.split(u'_')
                new_list.append(Process(process_name, pid, parent_pid))
            process_list = new_list
            message = server.terminate_process(computer, process_list)
        elif function == "Back":
            return redirect(url_for("view_computer", mac=mac, ip=ip))
    process_list = server.get_processes_data(computer)
    return render_template("ProcessesPage.html", process_list=process_list, mac=mac, ip=ip, name=name, message=message)


# handles WakeOnLan.html
@app.route('/wake_on_lan?computer_list=<computer_list>&action=<action>', methods=['GET', 'POST'])
def wake_on_lan(computer_list, action):
    message = ""
    if request.method == 'POST':
        active = action == 'shutdown'
        if 'now' in request.form['Go']:
            for part in unicode_to_list(computer_list):
                mac, ip = part.split('_')
                server.do_action_now(Computer(mac, ip, active), action)
            return redirect(url_for('show_main_form'))
        else:
            hour = request.form['hour']
            minute = request.form['minute']
            second = request.form['second']
            try:
                for part in [item[1:-1] for item in computer_list[1:-1].split(', ')]:
                    mac, ip = part.split('_')
                    server.do_action(Computer(mac, ip, active), hour, minute, second, action)
            except:
                message = "Error: Time wasn't inserted correctly."
            else:
                return redirect(url_for('show_main_form'))
    names = [str(item.split('_')[1]) for item in unicode_to_list(computer_list)]
    return render_template("WakeOnLan.html", computer_list=computer_list, action=action, message=message, names=names)


# Shows one folder up
@app.route('/go_back?mac=<mac>&ip=<ip>&name=<name>&path=<path:path>')
def back(mac, ip, name, path):
    new_path = '\\'.join(path.split('\\')[:-1])
    if not new_path:
        new_path = EMPTY_PATH
    return redirect(url_for('show_files', mac=mac, ip=ip, name=name, path=new_path))
# endregion

# region ---------------------------- MAIN ----------------------------


def main():
    webbrowser.open(FLASK_URL)
    app.run(host="0.0.0.0", debug=False)

if __name__ == "__main__":
    main()
# endregion

