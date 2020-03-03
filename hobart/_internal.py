class EdgeMap:
    """
    A quick two-level dictionary where the two keys are interchangeable (i.e.
    a symmetric graph).
    """

    def __init__(self):
        # Store indicies into self.values here, to make it easier to get inds
        # or values.
        self.d = {}
        self.values = []

    def _order(self, u, v):
        if u < v:
            return u, v
        else:
            return v, u

    def add(self, u, v, val):
        low, high = self._order(u, v)
        if low not in self.d:
            self.d[low] = {}
        self.values.append(val)
        self.d[low][high] = len(self.values) - 1

    def contains(self, u, v):
        low, high = self._order(u, v)
        if low in self.d and high in self.d[low]:
            return True
        return False

    def index(self, u, v):
        low, high = self._order(u, v)
        try:
            return self.d[low][high]
        except KeyError:
            return None


class Graph:
    """
    A little utility class to build a symmetric graph and calculate Euler Paths.
    """

    def __init__(self, size):
        self.size = size
        self.d = {}

    def __len__(self):
        return len(self.d)

    def add_edge(self, u, v):
        assert u >= 0 and u < self.size
        assert v >= 0 and v < self.size
        if u not in self.d:
            self.d[u] = set()
        if v not in self.d:
            self.d[v] = set()
        self.d[u].add(v)
        self.d[v].add(u)

    def remove_edge(self, u, v):
        if u in self.d and v in self.d[u]:
            self.d[u].remove(v)
        if v in self.d and u in self.d[v]:
            self.d[v].remove(u)  # pragma: no cover
        if v in self.d and len(self.d[v]) == 0:
            del self.d[v]
        if u in self.d and len(self.d[u]) == 0:
            del self.d[u]

    def pop_euler_path(self, allow_multiple_connected_components=True):
        # Based on code from Przemek Drochomirecki, Krakow, 5 Nov 2006
        # http://code.activestate.com/recipes/498243-finding-eulerian-path-in-undirected-graph/
        # Under PSF License
        # NB: MUTATES d

        # Count the number of vertices with odd degree.
        odd = [x for x in self.d if len(self.d[x]) & 1]
        odd.append(list(self.d.keys())[0])
        if not allow_multiple_connected_components and len(odd) > 3:
            return None  # pragma: no cover
        stack = [odd[0]]
        path = []

        # Main algorithm.
        while stack:
            v = stack[-1]
            if v in self.d:
                u = self.d[v].pop()
                stack.append(u)
                self.remove_edge(u, v)
            else:
                path.append(stack.pop())
        return path
