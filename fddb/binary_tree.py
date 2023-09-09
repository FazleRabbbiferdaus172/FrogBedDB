from .logical import LogicalBase, ValueRef


class BinaryNode:
    pass


class BinaryNodeRef(ValueRef):
    pass


class BinaryTree(LogicalBase):
    def _get(self, node, key):
        while node is not None:
            if key < node.key:
                node = self._follow(node.left_ref)
            elif node.key < key:
                node = self._follow(node.right_ref)
            else:
                return self._follow(node.value_ref)
        raise KeyError
