from run import run
from byteio import *
from cpp.um_emulator import UniversalMachine

from pathlib import Path
import io
import sys
import pytest

def test_io_smoke():
    um = UniversalMachine(Path('umix.umz').read_bytes())
    
    run(um, umin=BaseReader(), umout=BaseWriter())
    assert um.state == UniversalMachine.State.WAITING

    output = io.StringIO('')
    run(um, umin=TextReader(io.StringIO('guest\nexit\n')), 
            umout=ForkWriter(TextWriter(output), TextWriter(sys.stdout)))
    assert um.state == UniversalMachine.State.HALT
    assert 'logged in as guest' in output.getvalue()


def test_io_sequential():
    input = SequentialReader(TextReader(io.StringIO('hello ')),
                                 TextReader(io.StringIO('world')),
                                 TextReader(io.StringIO('!\n')))
    outstring = io.StringIO()
    output = TextWriter(outstring)
    while True:
        c = input.readbyte()
        if c is None: break
        output.writebyte(c)
    assert outstring.getvalue() == 'hello world!\n'


if __name__ == '__main__':
    test_io_smoke()
