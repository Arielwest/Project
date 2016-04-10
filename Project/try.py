import wmi

conn = wmi.WMI('192.168.2.55', user='34v7', password='')
conn.Win32_Process.Create(CommandLine='calc.exe')
