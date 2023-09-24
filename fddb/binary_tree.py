from .logical import LogicalBase, ValueRef
import pickle

class BinaryNode:
    def store_refs(self, storage):
        self.value_ref.store(storage)
        self.left_ref.store(storage)
        self.right_ref.store(storage)


class BinaryNodeRef(ValueRef):

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


class BinaryTree(LogicalBase):

    def __init__(self, storage):
        super().__init__(storage)
        self.node_ref_class = BinaryNodeRef

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
            new_node = BinaryNode(self.node_ref_class(), key, value_ref, self.node_ref_calss(), 1)
        elif key < node.key:
            new_node = BinaryNode.from_node(
                node,
                left_ref=self._insert(
                    self.follow(node.left_ref), key, value_ref
                )
            )
        else:
            new_node = BinaryNode.from_node(node, value_ref=value_ref)
        return self.node_ref_class(referent=new_node)
