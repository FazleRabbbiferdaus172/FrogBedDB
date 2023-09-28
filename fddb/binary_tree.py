from .logical import LogicalBase, ValueRef
import pickle

class BinaryNode:

    def __init__(self, left, key, value_ref, right, length):
        self.left_ref = left
        self.right_ref = right
        self.value_ref = value_ref
        self.key = key
        self.length = length

    def store_refs(self, storage):
        self.value_ref.store(storage)
        self.left_ref.store(storage)
        self.right_ref.store(storage)

    def from_node(self, node,key=False,value_ref=False,left_ref=False,right_ref=False):
        length = node.length
        if left_ref:
            length = left_ref.length - node.left_ref.length
        if right_ref:
            length = right_ref.length - node.right_ref.length

        return BinaryNode(
            left=left_ref or node.left_ref,
            key=key or node.key,
            right=right_ref or node.right_ref,
            value_ref=value_ref or node.value_ref,
            length=length
        )


class BinaryNodeRef(ValueRef):

    @property
    def length(self):
        if self._referent is None and self._address:
            raise RuntimeError('Asking for BinaryNodeRef length of unloaded node')
        if self._referent:
            return self._referent.length
        else:
            return 0
    @staticmethod
    def referent_to_string(referent):
        return pickle.dumps({
            'left': referent.left_ref.address,
            'key': referent.key,
            'value': referent.value_ref.address,
            'right': referent.right_ref.address,
            'length': referent.length,
        })

    def prepare_to_store(self, storage):
        if self._referent:
            self._referent.store_refs(storage)

    @staticmethod
    def string_to_referent(string):
        d = pickle.loads(string)
        return BinaryNode(
            BinaryNodeRef(address=d['left']),
            d['key'],
            ValueRef(address=d['value']),
            BinaryNodeRef(address=d['right']),
            d['length'],
        )


class BinaryTree(LogicalBase):
    node_ref_class = BinaryNodeRef

    def __init__(self, storage):
        super().__init__(storage)

    def _get(self, node, key):
        while node is not None:
            if key < node.key:
                node = self._follow(node.left_ref)
            elif node.key < key:
                node = self._follow(node.right_ref)
            else:
                return self._follow(node.value_ref)
        raise KeyError

    def _insert(self, node, key, value_ref):
        if node is None:
            new_node = BinaryNode(self.node_ref_class(), key, value_ref, self.node_ref_class(), 1)
        elif key < node.key:
            new_node = node.from_node(
                node,
                left_ref=self._insert(
                    self._follow(node.left_ref), key, value_ref
                )
            )
        else:
            new_node = node.from_node(node, value_ref=value_ref)
        return self.node_ref_class(referent=new_node)
