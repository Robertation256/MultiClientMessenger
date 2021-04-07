import os

#---------------Server Socket-----------------
PORT_NUMBER = 5000
IP_ADDRESS = "localhost"

#---------------Path-----------------
ROOT = os.path.normpath(os.getcwd())
TEMPLATE_PATH = ROOT+"\\templates"
STATIC_FILE_PATH = ROOT + "\\static"


#---------------Secret Keys-----------------
APP_SECRET = "defaultS"     #Your app secret, has to to be 8 byte long



#---------------Sleep Cycle-----------------
SHORT_CONNECTION_SLEEP_CYCLE = 1
LONG_CONNECTION_SLEEP_CYCLE = 2
DEAD_CLIENT_KILL_CYCLE = 10


#---------------Timeout-----------------
USER_TIMEOUT = 60


