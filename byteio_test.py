from clients import run
from byteio import *
from cpp.um_emulator import UniversalMachine

from pathlib import Path
import io
import sys

def test_io_smoke():
    um = UniversalMachine(Path('umix.umz').read_bytes())
    
    run(um, umin=TextByteReader(io.StringIO()), umout=TextByteWriter(io.StringIO()))
    assert um.state == UniversalMachine.State.WAITING

    output = io.StringIO('')
    run(um, umin=TextByteReader(io.StringIO('guest\nexit\n')), 
            umout=ForkByteWriter(TextByteWriter(output), TextByteWriter(sys.stdout)))
    assert um.state == UniversalMachine.State.HALT
    assert 'logged in as guest' in output.getvalue()


def test_io_sequential():
    input = SequentialByteReader(TextByteReader(io.StringIO('hello ')),
                                 TextByteReader(io.StringIO('world')),
                                 TextByteReader(io.StringIO('!\n')))
    outstring = io.StringIO()
    output = TextByteWriter(outstring)
    while True:
        c = input.readbyte()
        if c is None: break
        output.writebyte(c)
    assert outstring.getvalue() == 'hello world!\n'

if __name__ == '__main__':
    test_io_smoke()
