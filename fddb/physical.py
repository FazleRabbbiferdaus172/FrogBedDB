import os
import portalocker
import struct


class Storage:
    SUPERBLOCK_SIZE = 4096
    INTEGER_FORMAT = "!Q"
    INTEGER_LENGHT = 8

    def __init__(self, f):
        self._f = f
        self.locked = False
        self._ensure_superblock()

    @property
    def closed(self):
        return self._f.closed

    def _seek_end(self):
        self._f.seek(0, os.SEEK_END)

    def _ensure_superblock(self):
        self.lock()
        self._seek_end()
        end_address = self._f.tell()
        if end_address < self.SUPERBLOCK_SIZE:
            self._f.write(b'\x00' * (self.SUPERBLOCK_SIZE - end_address))
        self.unlock()

    def unlock(self):
        if self.locked:
            self._f.flush()
            portalocker.unlock(self._f)
            self.locked = False

    def lock(self):
        if not self.locked:
            portalocker.lock(self._f, portalocker.LOCK_EX)
            self.locked = True
            return True
        else:
            return False

    def _seek_superblock(self):
        self._f.seek(0)

    def commit_root_address(self, root_address):
        self.lock()
        self._f.flush()
        self._seek_superblock()
        self._write_integer(root_address)
        self._f.flush()
        self.unlock()

    def _integer_to_formatted_byte(self, value):
        return struct.pack(self.INTEGER_FORMAT, value)

    def _write_integer(self, value):
        self.lock()
        self._f.write(self._integer_to_formatted_byte(value))

    def _write_data_length(self, data):
        self._write_integer(len(data))

    def write(self, data):
        self.lock()
        self._seek_end()
        address = self._f.tell()
        self._write_data_length(data)
        self._f.write(data)
        return address

    def read(self, address=0):
        self._seek_end()
        self._f.flush()
        # read the lenght of the data
        self._f.seek(address)
        formated_lenght_bytes = self._f.read(self.INTEGER_LENGHT)
        lenght_value = struct.unpack(self.INTEGER_FORMAT, formated_lenght_bytes)[0]
        # start reading after the lenght of data info end till the lenght of data
        return self._f.read(lenght_value)

    def _get_all_contents(self):
        self._seek_end()
        self._f.flush()
        self._f.seek(0)
        return self._f.read()

    def get_root_address(self):
        self._seek_superblock()
        formated_lenght_bytes = self._f.read(self.INTEGER_LENGHT)
        integer = struct.unpack(self.INTEGER_FORMAT, formated_lenght_bytes)[0]
        return integer

    def close(self):
        self.unlock()
        self._f.close()