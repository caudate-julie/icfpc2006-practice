from abc import abstractmethod
from cpp.um_import import UniversalMachine
import io

class UMClient:
    def __init__(self):
        self.output = b''
        self.mode = []

    @abstractmethod
    def run(self, um: UniversalMachine):
        raise NotImplementedError()

    @abstractmethod
    def setmode(self, modeversion):
        raise NotImplementedError()


class FileClient(UMClient):
    filename: str

    def __init__(self, filename):
        UMClient.__init__(self)
        self.filename = filename

    def setmode(self, modeversion):
        self.mode = [UniversalMachine.mode.echoinput]
        if modeversion == 'verbal':
            self.mode.append(UniversalMachine.mode.echo)

    def run(self, um):
        f = open(self.filename, 'rb')
        instream = f.read()
        um.setmode(self.mode)
        um.run(instream)
        self.output = um.read_output()
        f.close()


class UserClient(UMClient):

    def __init__(self, eof):
        UMClient.__init__(self)
        self.eof = eof

    def setmode(self, modeversion):
        self.mode = []

    def run(self, um):
        outstream = []
        instream = ''
        um.setmode(self.mode)
        while True:
            um.run(instream)
            outstream.append(um.read_output())
            if not um.is_waiting: 
                break

            instream = input(outstream[-1])
            if instream == self.eof:
                break

            outstream.append(instream)
        output = ''.join(outstream)



clientlist= { 'u' : UserClient,
              'f' : FileClient,
            }


if __name__ == '__main__':
    um = UniversalMachine()
    um.load('codex.umz')
    f = UserClient('EOU')
    f.run(um)
#    print(um.read_output())
    
