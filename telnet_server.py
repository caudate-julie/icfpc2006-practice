from byteio import *
from clients import run
from cpp.um_emulator import UniversalMachine

from pathlib import Path
import sys
import io
import socketserver
import threading
import logging


file_lock = threading.Lock()

class Handler(socketserver.StreamRequestHandler):
    def handle(self):
        request = []
        while True:
            line = self.rfile.readline()
            if line.strip() == b'':
                break
            request.append(line)

        request = b''.join(request)
        response = proxy(request, BaseWriter())
        self.wfile.write(response)

        with file_lock:
            with Path('logs/default.out').open('ab') as f:
                f.write(request + response)

        request_header = request[:request.find(b' HTTP')].decode('ascii')
        response_header = response[response.find(b' ')+1:response.find(b'\n')].decode('ascii')
        logging.info(f'{request_header} | {response_header} | {len(response)} bytes')

        self.wfile.close()


um = None
um_lock = threading.Lock()

def get_um_copy():
    global um
    with um_lock:
    
        if um is None:
            logging.info('loading um...')
            um = UniversalMachine(Path('umix.umz').read_bytes())
            b = b'guest\nmail\ntelnet 127.0.0.1 80\n'
            run(um, umin = ByteReader(io.BytesIO(b)), umout=BaseWriter())
            logging.info('done')
        return UniversalMachine(um)


def proxy(request, logwriter: BaseWriter):
    local_um = get_um_copy()

    run(local_um, umin = ByteReader(io.BytesIO(request)), umout=logwriter)

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

    logging.basicConfig(format='%(asctime)s : %(message)s',
                        level=logging.INFO,
                        datefmt='%m-%d %H:%M:%S',)

    HOST, PORT = 'localhost', 5017
    with socketserver.ThreadingTCPServer((HOST, PORT), Handler) as server:
        Path('logs/default.out').write_bytes(b'')
        logging.info('listening...')
        server.serve_forever()
