from cpp.um_emulator import UniversalMachine
from byteio import *

from abc import abstractmethod
from pathlib import Path
from typing import Optional
import sys
import io


def run(um: UniversalMachine, *, umin: ByteReader, umout: ByteWriter):
    while True:
        # if um.state == UniversalMachine.State.ERROR:
        #     # TODO
        #     print(um.error_message)
        #     return

        if um.state == UniversalMachine.State.IDLE:
            out = um.run()
            for byte in out:
                umout.writebyte(byte)
            continue

        if um.state == UniversalMachine.State.HALT:
            return

        assert um.state == UniversalMachine.State.WAITING

        c = umin.readbyte()
        if c is None: return
        um.write_input(c)


if __name__ == '__main__':
    with Path('logs/default.out').open('w') as f:
        logwriter = TextByteWriter(f)
        umin = ForkByteReader(TextByteReader(sys.stdin), [logwriter])
        umout = ForkByteWriter(TextByteWriter(sys.stdout), logwriter)
        
        um = UniversalMachine(Path('umix.umz').read_bytes())
        run(um, umin=umin, umout=umout)
