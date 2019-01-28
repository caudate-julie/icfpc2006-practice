from clients import *
import logging
from time import time
import pathlib
from cpp.um_emulator import UniversalMachine


def run_user():
    um = UniversalMachine(pathlib.Path('umix.umz').read_bytes())
    client = UserClient('EOF')
    client.run(um)

def run(clientlist):
    um = UniversalMachine(pathlib.Path('umix.umz').read_bytes())
    for client in clientlist:
        client.run(um)

def collect_score():
    pass

if __name__ == '__main__':
    clientlist = [UserClient('EOU', first=True)]
    run(clientlist)
