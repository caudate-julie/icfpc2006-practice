from abc import abstractmethod
from cpp.um_emulator import UniversalMachine
from pathlib import Path
import sys
import io

class UMClient:
    def __init__(self, outfile, first):
        self.outfile = Path('logs') / (outfile + '.out')
        if first and self.outfile.exists():
            self.outfile.write_text('')
        self.echo = True

    def run(self, um: UniversalMachine):
        self.setup(um)
        f = open(self.outfile, 'a')
        instream = []

        while True:
            out = um.run().decode('ascii')
            f.write(out)

            if self.echo:
                print(out, end='', flush=True)

            if um.state == UniversalMachine.State.HALT:
                break

            # if um.state == UniversalMachine.State.ERROR:
            #     # TODO
            #     print(um.error_message)
            #     break

            if um.state == UniversalMachine.State.IDLE:
                continue

            assert um.state == UniversalMachine.State.WAITING

            if len(instream) == 0:
                instream = self.input()
                if instream == None: 
                    break    
                
                f.write(instream)
                instream = list(instream)
            um.write_input(ord(instream.pop(0)))

        f.close()

    @abstractmethod
    def setup(self, um):
        raise NotImplementedError()
    
    @abstractmethod
    def input(self):
        raise NotImplementedError()    


class FileClient(UMClient):
    infile: str

    def __init__(self, infile, outfile=None, first=False):
        if outfile == None: outfile = infile
        UMClient.__init__(self, outfile, first)
        self.instream = io.StringIO((Path('logs') / (infile + '.in')).read_text())

    def setup(self, um: UniversalMachine):
        um.output_buffer_limit = 1 if self.echo else None
        um.command_limit = None

    def input(self):
        c = self.instream.read(1)
        if len(c) == 0:
            return None
        return c


class UserClient(UMClient):

    def __init__(self, eof, outfile=None, first=False):
        if outfile == None:
            outfile = 'default'
        UMClient.__init__(self, outfile, first)
        self.eof = eof
        self.inputlog = Path('logs') / 'input.in'
        if self.inputlog.exists():
            self.inputlog.unlink()

    def setup(self, um: UniversalMachine):
        um.output_buffer_limit = 1
        um.command_limit = None

    def input(self):
        instream = sys.stdin.readline()
        if instream.strip() == self.eof:
            return None

        with self.inputlog.open(mode='a') as f:
            f.write(instream)

        return instream


if __name__ == '__main__':
    um = UniversalMachine(Path('umix.umz').read_bytes())
    client = UserClient('EOU', first=True)
    client.run(um)

    um = UniversalMachine(Path('umix.umz').read_bytes())
    client = FileClient('input')
    client.run(um)