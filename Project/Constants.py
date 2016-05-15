# region ---------------------------- ABOUT ----------------------------
"""
##################################################################
# Created By: Ariel Westfried                                    #
# Date: 01/01/2016                                               #
# Name: Project - Constants                                      #
# Version: 1.0                                                   #
# Windows Tested Versions: Win 7 32-bit                          #
# Python Tested Versions: 2.6 32-bit                             #
# Python Environment  : PyCharm                                  #
##################################################################
"""
# endregion

# region ---------------------------- Constants ----------------------------
MODULES_TO_INSTALL = ["flask", "wmi", "pywin32", "scapy", "pywinrm"]    # The modules needed for the program to run
SERVER_PORT = 6070                                                      # The port where the server listens
BROADCAST_PORT = 6071                                                   # The port used for the broadcast communication
SERVER_ANNOUNCE_MESSAGE = "I'm the network manager server."             # The message used to identify the server
BUFFER_SIZE = 1024                                                      # The buffer size of the socket communication
IP_REGULAR_EXPRESSION = r"^(?:[0-9]{1,3}\.){3}[0-9]{1,3}$"              # The regex for a valid ip
FLASK_URL = "http://127.0.0.1:5000/"                                    # The url where the server sits
DATABASE_NAME = r"Database.db"                                          # Name of the database file
MAC_LENGTH = 12                                                         # Length of mac address
WAKE_ON_LAN_PORT = 9                                                    # The port used for wake on lan protocol
NET_SCAN_WAIT = 60                                                      # Time to wait between network scans
ANNOUNCE_SLEEP_TIME = 10                                                # Time to wait between broadcast announcements
PROCESS_ENUMERATE_SLEEP = 60                                            # Time to wait between updating process list
EMPTY_PATH = 'Drives'                                                   # First path when looking for folders
END_LINE = '\r\n'                                                       # End of line
BROKEN_END_LINE = '\\r\\n'                                              # End of line with an error
MAC_REGULAR_EXPRESSION = b"^([0-9A-Fa-f]{2}[:-]){5}([0-9A-Fa-f]{2})$"   # Regex for a valid mac address
PROCESS_PARTS_SEPARATOR = "#"                                           # Separator used between process when in string
FILE_SEPARATOR = '#'                                                    # Separator used between file names in string
IN_PACK_SEPARATOR = '#'                                                 # Separator for key exchange communication
FRAGMENTS_SEPARATOR = '@'                                               # Separates between a packet and its serial number
DOWNLOAD_UPLOAD = 'C:\\ServerFiles\\'                                   # Directory where to save downloaded files
