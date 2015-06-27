import socket
__author__ = 'martin'

DEBUG = True
PORT = 1337 # CHANGE TO POLOPORT
POLO_BINDING_PORT = 1390

MARCOPORT = 1338

MULTICAST_ADDR = '224.0.0.112'
MULTICAST_ADDRS = ['224.0.0.112', '224.0.0.113']

BINDING_MULTICAST_ADDRS = ['224.0.0.112', '224.0.0.113']
HOPS = 1
IFACE = 'eth0'

TIMEOUT = 1000.0
FRAME_SIZE = 4096
CONF_DIR = '/etc/marcopolo/'
SERVICES_DIR = 'polo/services/'


LOGGING_LEVEL = 'DEBUG'
LOGGING_FORMAT = '%(asctime)s:%(levelname)s:%(message)s'
LOGGING_DIR = '/var/log/marcopolo/'
PIDFILE_POLO = '/var/run/marcopolo/polod.pid'
PIDFILE_MARCO = '/var/run/marcopolo/marcod.pid'

RETRIES = -10

POLO_USER_DIR = ".polo"

POLO_PARAMS = {"hostname":socket.gethostname()}

VERIFY_REGEXP = '^([\d\w]+):([\d\w]+)$'