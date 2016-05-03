import heapq

class PriorityQueueSet(object):

    """
    Combined priority queue and set data structure.

    Acts like a priority queue, except that its items are guaranteed to be
    unique. Provides O(1) membership test, O(log N) insertion and O(log N)
    removal of the smallest item.

    Important: the items of this data structure must be both comparable and
    hashable (i.e. must implement __cmp__ and __hash__). This is true of
    Python's built-in objects, but you should implement those methods if you
    want to use the data structure for custom objects.

    @ifjorissen note: originally lifted from: http://stackoverflow.com/questions/407734/a-generic-priority-queue-for-python
    and augmented to have a couple extra functions and to accept an alternative ordering for the heap 
    """

    def __init__(self, items=[], key=lambda x:x):
        """
        Create a new PriorityQueueSet.

        Arguments:
            items (list): An initial item list - it can be unsorted and
                non-unique. The data structure will be created in O(N).
        """
        self.key = key
        self.set = dict(((key(item), item), True) for item in items)

        self.heap = list(self.set.keys())
        heapq.heapify(self.heap)

    def has_item(self, item):
        """Check if ``item`` exists in the queue."""
        return (self.key(item), item) in self.set

    def empty(self):
        """Check if the queue is empty. If it is, return True, else False."""
        if not self.set:
            return True
        else:
            return False

    def get(self):
        """Remove and return the smallest item from the queue."""
        smallest = heapq.heappop(self.heap)
        del self.set[smallest]
        return smallest[1]


    def remove(self, item):
        """removes an item if it is in the queue"""
        if item in self.set:
            self.heap.remove(item)
            heapq.heapify(self.heap)
            item_key = (self.key(item), item)
            del self.set[item_key]

    def put(self, item):
        """Add ``item`` to the queue if doesn't already exist."""
        if item not in self.set:
            data = (self.key(item), item)
            self.set[data] = True
            heapq.heappush(self.heap, data)

    def __repr__(self):
        return str(self.heap)