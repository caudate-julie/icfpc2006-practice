import clients
from cpp.um_emulator import UniversalMachine

from time import time
from collections import defaultdict
import logging
import pathlib
import re
import sys



if __name__ == '__main__':
    # with Path('logs/guest.out').open('w') as f:
    #     logwriter = TextWriter(f)
    #     umin = ForkReader(TextReader(sys.stdin), [logwriter])
    #     umout = ForkWriter(TextWriter(sys.stdout), logwriter)
        
    #     um = UniversalMachine(Path('umix.umz').read_bytes())
    #     run(um, umin=umin, umout=umout)
    run_user()
    collect_score()
