from byteio import *
from clients import run
from cpp.um_emulator import UniversalMachine

from pathlib import Path
from time import time
import sys
import io
import socketserver

um = None

class Handler(socketserver.StreamRequestHandler):
    def handle(self):
        um = UniversalMachine(Path('umix.umz').read_bytes())
        with Path('logs/telnet.out').open('wb') as f:
            print(f'client address: {self.client_address[0]}')
            request = b''
            while True:
                line = self.rfile.readline()
                if line.strip() == b'': break
                request += line
            
            response = proxy(request, ByteWriter(f))
            self.wfile.write(response)
            print('response sent')
            self.wfile.close()


def um_initialize():
    global um
    um = UniversalMachine(Path('umix.umz').read_bytes())
    run(um, umin = ByteReader(io.BytesIO(b'guest\nmail\n')), umout=BaseWriter())


# assumes um is already running
def proxy(request, logwriter: BaseWriter):
    if um == None:
        um_initialize()
    local_um = UniversalMachine(um)
    connstring = b'telnet 127.0.0.1 80\n'

    run(local_um, umin = ByteReader(io.BytesIO(connstring + request)), umout=logwriter)

    outstream = io.BytesIO()
    run(local_um,
        umin=ForkReader(ByteReader(io.BytesIO(b'\n')), [logwriter]),
        umout=ForkWriter(logwriter, ByteWriter(outstream)))

    response = outstream.getvalue()
    assert response.endswith(b'% '), (request, response)
    return response[:-2]


if __name__ == '__main__':
    import hintcheck
    hintcheck.hintcheck_all_functions()
    HOST, PORT = 'localhost', 5017
    # with socketserver.ThreadingTCPServer((HOST, PORT), Handler) as server:
    #     print('listening...')
    #     server.serve_forever()

    t = time()
    connstring = b'guest\nmail\ntelnet 127.0.0.1 80\n'
    um = UniversalMachine(Path('umix.umz').read_bytes())

    run(um, 
        umin=ByteReader(io.BytesIO(connstring)),
        umout=BaseWriter())
    print(f'runtime: {time()-t:.4}')
    t = time()
    um2 = UniversalMachine(um)
    print(f'copytime: {time()-t:.4}')
    

    # with Path('logs/telnet.out').open('wb') as f:
    #     logwriter = ByteWriter(f)
    #     response = proxy(request, logwriter)
    #     print('\n\nRESPONSE:\n', response)