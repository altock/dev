from snakebite.client import Client
from constants import NAMENODE_PORT

client = Client('localhost', NAMENODE_PORT)
for x in client.ls(['/']):
    print x
