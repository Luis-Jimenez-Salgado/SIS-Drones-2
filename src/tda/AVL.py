class AVLNode:
    def __init__(self, key):
        self.key = key
        self.height = 1
        self.left = None
        self.right = None
        self.frequency = key.frequency if hasattr(key, 'frequency') else 1

    def __str__(self):
        return f"{str(self.key)} (freq: {self.frequency})"

class AVL:
    def __init__(self):
        self.root = None
        self._size = 0

    def __len__(self):
        return self._size

    def insert(self, key):
        """Insert a key into the AVL tree."""
        def _insert(node, key):
            # If node is None, create a new node
            if not node:
                self._size += 1
                return AVLNode(key)
            
            # If key already exists, update frequency
            if str(key) == str(node.key):
                # Increment frequency only once
                node.key.frequency += 1
                node.frequency = node.key.frequency
                return node
            
            # Insert into corresponding subtree
            if str(key) < str(node.key):
                node.left = _insert(node.left, key)
            else:
                node.right = _insert(node.right, key)

            # Update height and balance
            self._update_height(node)
            return self._balance(node)

        self.root = _insert(self.root, key)

    def delete(self, key):
        def _delete(node, key):
            if not node:
                return node
            elif str(key) < str(node.key):
                node.left = _delete(node.left, key)
            elif str(key) > str(node.key):
                node.right = _delete(node.right, key)
            else:
                self._size -= 1
                if not node.left:
                    return node.right
                elif not node.right:
                    return node.left

                temp = self._get_min(node.right)
                node.key = temp.key
                node.frequency = temp.frequency
                node.right = _delete(node.right, temp.key)

            self._update_height(node)
            return self._balance(node)

        self.root = _delete(self.root, key)

    def find(self, key):
        """Find a key in the AVL tree."""
        def _find(node, key):
            if not node:
                return None
            if str(key) == str(node.key):
                return node
            elif str(key) < str(node.key):
                return _find(node.left, key)
            else:
                return _find(node.right, key)

        return _find(self.root, key)

    def _get_min(self, node):
        current = node
        while current.left:
            current = current.left
        return current

    def _height(self, node):
        """Get the height of a node."""
        return node.height if node else 0

    def _update_height(self, node):
        """Update the height of a node."""
        node.height = max(self._height(node.left), self._height(node.right)) + 1

    def _balance_factor(self, node):
        """Calculate the balance factor of a node."""
        return self._height(node.left) - self._height(node.right)

    def _balance(self, node):
        """Balance the tree at a given node."""
        balance = self._balance_factor(node)
        
        # Caso izquierda-izquierda
        if balance > 1 and self._balance_factor(node.left) >= 0:
            return self._rotate_right(node)
            
        # Caso izquierda-derecha
        if balance > 1 and self._balance_factor(node.left) < 0:
            node.left = self._rotate_left(node.left)
            return self._rotate_right(node)
            
        # Caso derecha-derecha
        if balance < -1 and self._balance_factor(node.right) <= 0:
            return self._rotate_left(node)
            
        # Caso derecha-izquierda
        if balance < -1 and self._balance_factor(node.right) > 0:
            node.right = self._rotate_right(node.right)
            return self._rotate_left(node)
            
        return node

    def _rotate_left(self, z):
        """Perform a left rotation."""
        y = z.right
        T2 = y.left
        
        y.left = z
        z.right = T2
        
        self._update_height(z)
        self._update_height(y)
        
        return y

    def _rotate_right(self, z):
        """Perform a right rotation."""
        y = z.left
        T3 = y.right
        
        y.right = z
        z.left = T3
        
        self._update_height(z)
        self._update_height(y)
        
        return y 