import io
from typing import List, Optional
from abc import abstractmethod

class BaseReader:

    # returns one byte from stream or None if EOF
    def readbyte(self) -> Optional[int]:
        return None


class TextReader(BaseReader):
    # stream is fileobject, opened for reading as text
    def __init__(self, stream, *, encoding='ascii', errors='strict'):
        assert stream.readable()
        self.stream = stream
        self.encoding = encoding
        self.errors = errors
        self.buffer = bytearray()
    
    def readbyte(self) -> Optional[int]:
        if len(self.buffer) > 0:
            return self.buffer.pop(0)

        c = self.stream.read(1)
        if len(c) == 0:
            return None
        assert len(c) == 1
        c = c.encode(encoding=self.encoding, errors=self.errors)
        self.buffer = c[1:]
        return c[0]


class ByteReader(BaseReader):
    # stream is fileobject, opened for reading as binary
    def __init__(self, stream):
        assert stream.readable()
        self.stream = stream
    
    def readbyte(self) -> Optional[int]:
        c = self.stream.read(1)
        if len(c) == 0:
            return None
        assert len(c) == 1
        return c[0]


class ForkReader(BaseReader):
    def __init__(self, reader: BaseReader, writers):
        self.reader = reader
        self.writers = writers
    
    def readbyte(self) -> Optional[int]:
        byte = self.reader.readbyte()
        if byte is None:
            return None

        for writer in self.writers:
            writer.writebyte(byte)
        return byte


class SequentialReader(BaseReader):
    def __init__(self, *readers):
        self.readers = list(readers)
    
    def readbyte(self) -> Optional[int]:
        while len(self.readers) > 0:
            c = self.readers[0].readbyte()
            if c is None:
                self.readers.pop(0)
                continue
            return c
        return None

# ------------------------------------------------- #

class BaseWriter:

    def writebyte(self, byte: int):
        pass


class TextWriter(BaseWriter):
    # stream is fileobject, opened for writing as text
    def __init__(self, stream, *, encoding='ascii', errors='strict'):
        assert stream.writable()
        self.stream = stream
        self.encoding = encoding
        self.errors = errors
    
    def writebyte(self, byte: int):
        b = bytes([byte]).decode(encoding=self.encoding, errors=self.errors)
        self.stream.write(b)
        self.stream.flush()


class ByteWriter(BaseWriter):
    # stream is fileobject, opened for writing as binary
    def __init__(self, stream):
        assert stream.writable()
        self.stream = stream
    
    def writebyte(self, byte: int):
        self.stream.write(bytes([byte]))
        self.stream.flush()


class ForkWriter(BaseWriter):
    def __init__(self, *writers):
        self.writers = writers
    
    def writebyte(self, byte: int):
        for stream in self.writers:
            stream.writebyte(byte)


__all__ = ['BaseReader', 
           'BaseWriter',
           'TextReader',
           'TextWriter',
           'ForkWriter',
           'ForkReader',
           'SequentialReader',
           'ByteReader',
           'ByteWriter']