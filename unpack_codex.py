import logging
from time import time
from pathlib import Path
from cpp.um_emulator import UniversalMachine


# codex.umz (packed) + password -> umix.umz (unpacked)
def main():
    um = UniversalMachine(Path('codex.umz').read_bytes())

    password = rb'(\b.bb)(\v.vv)06FHPVboundvarHRAkp'
    output = um.run()
    for c in password:
        assert um.state == UniversalMachine.State.WAITING, um.state
        um.write_input(c)
        output += um.run()
    
    assert um.state == UniversalMachine.State.HALT
    
    end_of_preamble = b'follows colon:'
    m = output.find(end_of_preamble) + len(end_of_preamble)
    assert m != -1
    print(output[:m].decode('ascii'))
    
    Path('umix.umz').write_bytes(output[m:])


if __name__ == '__main__':
    main()