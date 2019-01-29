from cpp.um_emulator import UniversalMachine

from abc import abstractmethod
from pathlib import Path
from typing import Optional
import sys
import io

# Abstract baseclass for Clients
# self.outfile : fileobject, opened for writing as binary
# self.echo : echoes to stdin if True
class UMClient:
    def __init__(self):
        self.echo = True

    def run(self, um: UniversalMachine, outfile):
        self.setup(um)
        instream = bytearray()

        while True:
            # if um.state == UniversalMachine.State.ERROR:
            #     # TODO
            #     print(um.error_message)
            #     break

            if um.state == UniversalMachine.State.IDLE:
                out = um.run()
                outfile.write(out)

                if self.echo:
                    print(out.decode('ascii'), end='', flush=True)
                continue

            if um.state == UniversalMachine.State.HALT:
                break

            assert um.state == UniversalMachine.State.WAITING

            if len(instream) == 0:
                instream = self.input()
                if instream == None: 
                    break
                
                outfile.write(instream)
            um.write_input(instream.pop(0))

    @abstractmethod
    def setup(self, um):
        raise NotImplementedError()
    
    @abstractmethod
    def input(self) -> Optional[bytearray]:
        raise NotImplementedError()    


# Reads input for UM from file
class FileClient(UMClient):

    def __init__(self, infile):
        super().__init__()
        self.instream = io.BytesIO(infile.read_bytes())

    def setup(self, um: UniversalMachine):
        um.output_buffer_limit = 1 if self.echo else None
        um.command_limit = None

    def input(self) -> Optional[bytearray]:
        c = self.instream.read(1)
        if len(c) == 0:
            return None
        return bytearray(c)


class UserClient(UMClient):
    def __init__(self, eof):
        super().__init__()
        self.eof = eof
        self.inputlog = Path('logs') / 'input.in'
        if self.inputlog.exists():
            self.inputlog.unlink()

    def setup(self, um: UniversalMachine):
        um.output_buffer_limit = 1
        um.command_limit = None

    def input(self) -> Optional[bytearray]:
        instream = sys.stdin.readline()
        if instream.strip() == self.eof:
            return None

        with self.inputlog.open(mode='a') as f:
            f.write(instream)

        return bytearray(instream.encode('ascii'))


if __name__ == '__main__':
    with Path('logs/default.out').open('wb') as f:
        um = UniversalMachine(Path('umix.umz').read_bytes())
        client = UserClient('EOU')
        client.run(um, f)

        um = UniversalMachine(Path('umix.umz').read_bytes())
        client = FileClient(Path('logs/input.in'))
        client.run(um, f)