class ValueRef:
    def __init__(self, referent=None, address=0):
        self._referent = referent
        self._address = address

    @property
    def address(self):
        return self._address

    def prepare_to_store(self, storage):
        pass

    def referent_to_string(self, value):
        return value.encode('utf-8')

    def string_to_referent(self, value):
        return  value.decode('utf-8')

    def get(self, storage):
        if not self._referent and self._address:
            self._referent = self.string_to_referent(storage.read(self._address))
        return self._referent

    def store(self, storage):
        if self._referent is not None and not self._address:
            self.prepare_to_store(storage)
            self._address = storage.write(self.referent_to_string(self._referent))

class LogicalBase:

    def __init__(self, storage):
        self._storage = storage
        self.node_ref_class = None

    def get(self, key):
        if not self._storage.locked:
            self._refresh_tree_ref()
        return self._get(self._follow(self._tree_ref), key)

    def set(self, key, value):
        if self._storage.lock():
            self._refresh_tree_ref()
        self._tree_ref = self._insert(
            self._follow(self._tree_ref), key, self.value_ref_calss(value)
        )

    def _refresh_tree_ref(self):
        self._tree_ref = self.node_ref_class(
            address=self._storage.get_root_address()
        )

    def _follow(self, ref):
        value = ref.get(self._storage)
        return value
