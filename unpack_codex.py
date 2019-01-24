import logging
from time import time
from pathlib import Path
from cpp.um_emulator import UniversalMachine


# codex.umz (packed) + password -> umix.um (unpacked)
def main():
    um = UniversalMachine()
    um.load('codex.umz')

    password = rb'(\b.bb)(\v.vv)06FHPVboundvarHRAkp'
    um.setmode([])
    um.run(password)
    outstream = um.read_output()
    assert um.halted
    
    end_of_preamble = b'follows colon:'
    m = outstream.find(end_of_preamble) + len(end_of_preamble)
    assert not m == -1
    print(outstream[:m])
    
    Path('umix.umz').write_bytes(outstream[m:])


if __name__ == '__main__':
    main()