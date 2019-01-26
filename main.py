from clients import *
import logging
from time import time
import pathlib
from cpp.um_emulator import UniversalMachine


def run_user():
    um = UniversalMachine(pathlib.Path('umix.umz').read_bytes())

    # out = open(configs['outfile'], 'wb')
    client = UserClient('EOF')
    client.run(um)


if __name__ == '__main__':
    run_user()
    # print('\ntime elapsed: %.1f' % (time() - t))