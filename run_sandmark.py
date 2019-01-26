import logging
from time import time
from pathlib import Path
from cpp.um_emulator import UniversalMachine


def main():
    um = UniversalMachine(Path('sandmark.umz').read_bytes())
    um.output_buffer_limit = 1
    t = time()
    while um.state != UniversalMachine.State.HALT:
        assert um.state == UniversalMachine.State.IDLE
        output = um.run()
        print(output.decode('ascii'), end='', flush=True)
    print(f'\ntime elapsed:{time() - t:.4}')
    


if __name__ == '__main__':
    main()