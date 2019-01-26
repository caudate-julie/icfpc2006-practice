from abc import abstractmethod
from cpp.um_emulator import UniversalMachine
import sys
import io

class UMClient:
    def __init__(self):
        self.outfile = 'default.out'

    @abstractmethod
    def run(self, um: UniversalMachine):
        raise NotImplementedError()


class FileClient(UMClient):
    filename: str

    def __init__(self, filename):
        UMClient.__init__(self)
        self.filename = filename

    def run(self, um):
        f = open(self.filename, 'rb')
        instream = f.read()
        um.run(instream)
        self.output = um.read_output()
        f.close()


class UserClient(UMClient):

    def __init__(self, eof):
        UMClient.__init__(self)
        self.eof = eof

    def run(self, um: UniversalMachine):
        f = open(self.outfile, 'w')
        instream = []

        while True:
            out = um.run().decode('ascii')
            f.write(out)
            print(out, end='', flush=True)

            if um.state == UniversalMachine.State.HALT:
                break

            # if um.state == UniversalMachine.State.ERROR:
            #     # TODO
            #     print(um.error_message)
            #     break

            assert um.state == UniversalMachine.State.WAITING # todo: output limit

            if len(instream) == 0:
                instream = sys.stdin.readline()
                if instream.strip() == self.eof:
                    break
                f.write(instream)
                instream = list(instream)

            um.write_input(ord(instream.pop(0)))
        f.close()


if __name__ == '__main__':
    um = UniversalMachine()
    um.load('codex.umz')
    f = UserClient('EOU')
    f.run(um)
#    print(um.read_output())
    
