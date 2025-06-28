class Vertex:
    """Lightweight vertex structure for a graph."""
    __slots__ = '_element', '_edges'

    def __init__(self, element):
        """Do not call constructor directly. Use Graph's insert_vertex(element)."""
        self._element = element
        self._edges = []

    def element(self):
        """Return element associated with this vertex."""
        return self._element

    def edges(self):
        """Return list of edges connected to this vertex."""
        return self._edges

    def add_edge(self, vertex):
        """Add an edge to this vertex."""
        if vertex not in self._edges:
            self._edges.append(vertex)

    def remove_edge(self, vertex):
        """Remove an edge from this vertex."""
        if vertex in self._edges:
            self._edges.remove(vertex)

    def __hash__(self):
        return hash(id(self))

    def __str__(self):
        return str(self._element)

    def __repr__(self):
        return f"Vertex({self._element})"
