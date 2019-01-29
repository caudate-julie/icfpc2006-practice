import io
from typing import List
from abc import abstractmethod

class ByteReader:

    # returns one byte from stream or None if EOF
    def readbyte():
        return None


class TextByteReader(ByteReader):
    # stream is fileobject, opened for reading as text
    def __init__(self, stream, *, encoding='ascii', errors='strict'):
        self.stream = stream
        self.encoding = encoding
        self.errors = errors
        self.buffer = bytearray()
    
    def readbyte(self):
        if len(self.buffer) > 0:
            return self.buffer.pop(0)

        c = self.stream.read(1)
        if len(c) == 0:
            return None
        assert len(c) == 1
        c = c.encode(encoding=self.encoding, errors=self.errors)
        self.buffer = c[1:]
        return c[0]


class ForkByteReader(ByteReader):
    def __init__(self, reader: ByteReader, writers):
        self.reader = reader
        self.writers = writers
    
    def readbyte(self):
        byte = self.reader.readbyte()
        if byte is None:
            return None

        for writer in self.writers:
            writer.writebyte(byte)
        return byte


class SequentialByteReader(ByteReader):
    def __init__(self, *readers):
        self.readers = list(readers)
    
    def readbyte(self):
        while len(self.readers) > 0:
            c = self.readers[0].readbyte()
            if c is None:
                self.readers.pop(0)
                continue
            return c
        return None

# ------------------------------------------------- #

class ByteWriter:

    def writebyte():
        pass


class TextByteWriter(ByteWriter):
    # stream is fileobject, opened for writing as text
    def __init__(self, stream, *, encoding='ascii', errors='strict'):
        self.stream = stream
        self.encoding = encoding
        self.errors = errors
    
    def writebyte(self, byte):
        b = bytes([byte]).decode(encoding=self.encoding, errors=self.errors)
        self.stream.write(b)
        self.stream.flush()


class ByteByteWriter(ByteWriter):
    # stream is fileobject, opened for reading as binary
    def __init__(self, stream):
        self.stream = stream
    
    def writebyte(self, byte):
        self.stream.write(byte)
        self.stream.flush()


class ForkByteWriter(ByteWriter):
    def __init__(self, *bytewriters):
        self.bytewriters = bytewriters
    
    def writebyte(self, byte):
        for stream in self.bytewriters:
            stream.writebyte(byte)


__all__ = ['ByteReader', 
           'ByteWriter',
           'TextByteReader',
           'TextByteWriter',
           'ForkByteWriter',
           'ForkByteReader',
           'SequentialByteReader',
           'ByteByteWriter']