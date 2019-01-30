import clients
from cpp.um_emulator import UniversalMachine

from time import time
from collections import defaultdict
import logging
import pathlib
import re
import sys


def run_user():
    um = UniversalMachine(pathlib.Path('umix.umz').read_bytes())
    with Path('logs/default.out').open('wb') as f, \
          Path('logs/input.in').open('wb') as g:
        logwriter = ByteWriter(f)
        run(um,
            umin=ForkReader(TextReader(sys.stdin), [logwriter, ByteWriter(g)]),
            umout=ForkWriter(TextWriter(sys.stdout), logwriter))


def run_files(filenames, outfile):

run howie



# all lines that match score pattern are collected in logs/score.txt and summed up
def collect_score():
    # PUZZL.TSK=100@1001|14370747643c6d2db0a40ecb4b0bb65
    # | 1 |     |2|
    # problem   score
    regex = re.compile(r'(\w*?)\.\w*?=(\d*)@\d*\|\w*')
    score = 0
    scorelines = defaultdict(set)
    for p in Path('logs').glob('*.out'):
        with p.open('rb') as f:
            for line in f:
                
                line = line.decode('ascii', errors='ignore').strip()
                m = regex.search(line)
                if m is None:
                    continue
                if m[0] in scorelines[m[1]]:
                    continue
                scorelines[m[1]].add(m[0])
                score += int(m[2])

    with Path('logs/score.txt').open('w') as f:
        f.write(f'Total score: {score}\n')
        for task in scorelines.keys():
            f.write('\n' + task + '\n')
            for line in scorelines[task]:
                f.write(line + '\n')
    print(f'Total score: {score}. Result written to logs/score.txt')


if __name__ == '__main__':
    # with Path('logs/guest.out').open('w') as f:
    #     logwriter = TextWriter(f)
    #     umin = ForkReader(TextReader(sys.stdin), [logwriter])
    #     umout = ForkWriter(TextWriter(sys.stdout), logwriter)
        
    #     um = UniversalMachine(Path('umix.umz').read_bytes())
    #     run(um, umin=umin, umout=umout)
    run_user()
    collect_score()
