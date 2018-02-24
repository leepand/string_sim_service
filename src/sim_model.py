"""BK-tree data structure to allow fast querying of "close" matches.
For example usage, see README.rst.
This code is licensed under a permissive MIT license -- see LICENSE.txt.
The pybktree project lives on GitHub here:
https://github.com/Jetsetter/pybktree
"""
import jellyfish
from collections import deque
from operator import itemgetter
import re

__all__ = ['edit_distance', 'BKTree']

__version__ = '1.1'

_getitem0 = itemgetter(0)

def resub_string(string,resub_list=None):
    if resub_list:
        for str_sub in resub_list:
            pat=safe_unicode(str_sub)
            string=re.sub(pat, '', safe_unicode(string))
            return string
    else:
        return safe_unicode(string)
def safe_unicode(text):
    """
    Attempts to convert a string to unicode format
    """
    # convert to text to be "Safe"!
    if isinstance(text,unicode):
        return text
    else:
        return text.decode('utf-8') 

def edit_distance(x, y, resub_del_list=None):
    """Calculate the hamming distance (number of bits different) between the
    two integers given.
    >>> [hamming_distance(x, 15) for x in [0, 8, 10, 12, 14, 15]]
    [4, 3, 2, 2, 1, 0]
    """
    y=resub_string(safe_unicode(y),resub_del_list)
    x=resub_string(safe_unicode(x),resub_del_list)
    return 1-jellyfish.jaro_winkler(x, y)#bin(x ^ y).count('1')


class BKTree(object):
    """BK-tree data structure that allows fast querying of matches that are
    "close" given a function to calculate a distance metric (e.g., Hamming
    distance or Levenshtein distance).
    Each node in the tree (including the root node) is a two-tuple of
    (item, children_dict), where children_dict is a dict whose keys are
    non-negative distances of the child to the current item and whose values
    are nodes.
    """
    def __init__(self, distance_func, items=[], resub_del_list=None):
        """Initialize a BKTree instance with given distance function
        (which takes two items as parameters and returns a non-negative
        distance integer). "items" is an optional list of items to add
        on initialization.
        >>> tree = BKTree(hamming_distance)
        >>> list(tree)
        []
        >>> tree.distance_func is hamming_distance
        True
        >>> tree = BKTree(hamming_distance, [])
        >>> list(tree)
        []
        >>> tree = BKTree(hamming_distance, [0, 4, 5])
        >>> sorted(tree)
        [0, 4, 5]
        """
        self.distance_func = distance_func
        self.tree = None
        self.resub_del_list=resub_del_list
        _add = self.add
        for item in items:
            _add(item)

    def add(self, item):
        """Add given item to this tree.
        >>> tree = BKTree(hamming_distance)
        >>> list(tree)
        []
        >>> tree.add(4)
        >>> sorted(tree)
        [4]
        >>> tree.add(15)
        >>> sorted(tree)
        [4, 15]
        """
        node = self.tree
        if node is None:
            self.tree = (item, {})
            return

        # Slight speed optimization -- avoid lookups inside the loop
        _distance_func = self.distance_func
        _resub_del_list=self.resub_del_list
        while True:
            parent, children = node
            #print parent, children
            distance = _distance_func(item, parent, _resub_del_list)
            node = children.get(distance)
            if node is None:
                children[distance] = (item, {})
                break

    def find(self, item, n):
        """Find items in this tree whose distance is less than or equal to n
        from given item, and return list of (distance, item) tuples ordered by
        distance.
        >>> tree = BKTree(hamming_distance)
        >>> tree.find(13, 1)
        []
        >>> tree.add(0)
        >>> tree.find(1, 1)
        [(1, 0)]
        >>> for item in [0, 4, 5, 14, 15]:
        ...     tree.add(item)
        >>> sorted(tree)
        [0, 0, 4, 5, 14, 15]
        >>> sorted(tree.find(13, 1))
        [(1, 5), (1, 15)]
        >>> sorted(tree.find(13, 2))
        [(1, 5), (1, 15), (2, 4), (2, 14)]
        >>> sorted(tree.find(0, 1000)) == [(hamming_distance(x, 0), x) for x in tree]
        True
        """
        if self.tree is None:
            return []

        candidates = deque([self.tree])
        found = []

        # Slight speed optimization -- avoid lookups inside the loop
        _candidates_popleft = candidates.popleft
        _candidates_extend = candidates.extend
        _found_append = found.append
        _distance_func = self.distance_func

        while candidates:
            candidate, children = _candidates_popleft()
            distance = _distance_func(candidate, item, self.resub_del_list)
            if distance <= n:
                _found_append((distance, candidate))

            if children:
                lower = distance - n
                upper = distance + n
                _candidates_extend(c for d, c in children.items() if lower <= d <= upper)

        found.sort(key=_getitem0)
        return found

    def __iter__(self):
        """Return iterator over all items in this tree; items are yielded in
        arbitrary order.
        >>> tree = BKTree(hamming_distance)
        >>> list(tree)
        []
        >>> tree = BKTree(hamming_distance, [1, 2, 3, 4, 5])
        >>> sorted(tree)
        [1, 2, 3, 4, 5]
        """
        if self.tree is None:
            return

        candidates = deque([self.tree])

        # Slight speed optimization -- avoid lookups inside the loop
        _candidates_popleft = candidates.popleft
        _candidates_extend = candidates.extend

        while candidates:
            candidate, children = _candidates_popleft()
            yield candidate
            _candidates_extend(children.values())

    def __repr__(self):
        """Return a string representation of this BK-tree with a little bit of info.
        >>> BKTree(hamming_distance)
        <BKTree using hamming_distance with no top-level nodes>
        >>> BKTree(hamming_distance, [0, 4, 8, 14, 15])
        <BKTree using hamming_distance with 3 top-level nodes>
        """
        return '<{} using {} with {} top-level nodes>'.format(
            self.__class__.__name__,
            self.distance_func.__name__,
            len(self.tree[1]) if self.tree is not None else 'no',
        )


#if __name__ == '__main__':
#    import doctest
#    doctest.testmod()