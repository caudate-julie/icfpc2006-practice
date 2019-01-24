from clients import *
import logging
from time import time
from cpp.um_emulator import UniversalMachine


UMFILE = 'codex.umz'

def run_UM(sequence, configs):
    um = UniversalMachine()
    um.load(UMFILE)

    out = open(configs['outfile'], 'wb')
    for T, P in sequence:
        assert T in clientlist, 'Unknown input mode'
        client = clientlist[T](P)
        client.setmode(configs['mode'])
        client.run(um)
        print(type(client.output))
        print(len(client.output))

        out.write(client.output)
        if um.halted:
            break
    print(um.error_message)
    out.close()


if __name__ == '__main__':
    configs = { 
                'mode' : '',
                'outfile' : 'default.out'
              }

    sequence = [('f', 'start.in')]
    t = time()
    run_UM(sequence, configs)
    print('\ntime elapsed: %.1f' % (time() - t))