from clients import *
from cpp.um_emulator import UniversalMachine

from time import time
from collections import defaultdict
import logging
import pathlib
import re


def run_user():
    um = UniversalMachine(pathlib.Path('umix.umz').read_bytes())
    client = UserClient('EOF')
    client.run(um)

def run(clientlist):
    um = UniversalMachine(pathlib.Path('umix.umz').read_bytes())
    for client in clientlist:
        client.run(um)


# all lines that match score pattern are collected in logs/score.txt and summed up
def collect_score():
    # PUZZL.TSK=100@1001|14370747643c6d2db0a40ecb4b0bb65
    # | 1 |     |2|
    # problem   score
    regex = re.compile(r'(\w*?)\.\w*?=(\d*)@\d*\|\w*')
    score = 0
    scorelines = defaultdict(set)
    for p in Path('logs').glob('*.out'):
        with p.open() as f:
            for line in f:
                m = regex.match(line)
                if m is None:
                    continue
                if line in scorelines[m[1]]:
                    continue
                scorelines[m[1]].add(line)
                score += int(m[2])

    with Path('logs/score.txt').open('w') as f:
        f.write(f'Total score: {score}\n')
        for task in scorelines.keys():
            f.write('\n' + task + '\n')
            for line in scorelines[task]:
                f.write(line)


if __name__ == '__main__':
    clientlist = [UserClient('EOU')]
    run(clientlist)
    collect_score()
