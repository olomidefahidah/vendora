class Node:
    def __init__(self, data):
        self.data = data
        self.next = None


class LinkedList:
    """Small singly linked list used for products, cart items, users, and sales."""

    def __init__(self):
        self.head = None
        self._size = 0

    def append(self, item):
        node = Node(item)
        if self.head is None:
            self.head = node
        else:
            current = self.head
            while current.next is not None:
                current = current.next
            current.next = node
        self._size += 1

    def clear(self):
        self.head = None
        self._size = 0

    def find(self, predicate):
        current = self.head
        while current is not None:
            if predicate(current.data):
                return current.data
            current = current.next
        return None

    def remove_if(self, predicate):
        current = self.head
        previous = None
        while current is not None:
            if predicate(current.data):
                if previous is None:
                    self.head = current.next
                else:
                    previous.next = current.next
                self._size -= 1
                return current.data
            previous = current
            current = current.next
        return None

    def to_list(self):
        return [item for item in self]

    def __iter__(self):
        current = self.head
        while current is not None:
            yield current.data
            current = current.next

    def __len__(self):
        return self._size
