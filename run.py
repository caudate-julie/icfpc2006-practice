import clients
from cpp.um_emulator import UniversalMachine
from byteio import *

import io
import argparse
import sys
import re
from collections import defaultdict
from pathlib import Path

def run_user():
    um = UniversalMachine(Path('umix.umz').read_bytes())
    with Path('logs/default.out').open('wb') as f, \
         Path('logs/input.in').open('wb') as g:
        logwriter = ByteWriter(f)
        clients.run(um,
            umin=ForkReader(TextReader(sys.stdin), [logwriter, ByteWriter(g)]),
            umout=ForkWriter(TextWriter(sys.stdout), logwriter))


def run_file(filename):
    path = Path('logs')
    um = UniversalMachine(Path('umix.umz').read_bytes())
    with (path / 'input.in').open('w') as keyboard, \
         (path / (filename + '.in')).open('r') as infile, \
         (path / (filename + '.out')).open('wb') as outfile:
        logwriter = ByteWriter(outfile)
        conswriter = TextWriter(sys.stdout)
        doublewriter = ForkWriter(logwriter, conswriter)
        # run file
        clients.run(um,
                    umin=ForkReader(TextReader(infile), [doublewriter]),
                    umout=doublewriter)
        clients.run(um,
                    umin=ForkReader(TextReader(sys.stdin),
                                    [logwriter, TextWriter(keyboard)]),
                    umout=doublewriter)


def run_compiled(umcode: bytearray)
    um = UniversalMachine(umcode)
    output = io.StringIO()
    clients.run(um,
            umin=BaseReader(),
            umout=TextWriter(output))
    return output.getvalue()


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
    # usage:
    # run
    # run -s
    # run smb
    # run smb -s
    # run -s --no-run
    parser = argparse.ArgumentParser()
    parser.add_argument('name', nargs='?')
    parser.add_argument('-s', '--score', action='store_true', help='calculate score')
    parser.add_argument('--no-run', action='store_true', help='UM is not executed')
    args = parser.parse_args()

    if not args.no_run:
        if args.name is None:
            run_user()
        else:
            run_file(args.name)
    if args.score:
        collect_score()


