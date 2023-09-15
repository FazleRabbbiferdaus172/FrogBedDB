import os
import portalocker


class Storage:
    SUPERBLOCK_SIZE = 4096

    def __init__(self, f):
        self._f = f
        self.locked = False
        self._ensure_superblock()

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

    def commit_root_address(self, root_address):
        self.lock()
        self._f.flush()
        self._seek_superblock()
        self._write_integer(root_address)
        self._f.flush()
        self.unlock()

    def _get_all_contents(self):
        return self._f.read()
