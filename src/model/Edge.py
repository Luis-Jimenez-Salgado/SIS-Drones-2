"""Edge module for graph operations."""

class Edge:
    """Edge structure for a graph."""
    def __init__(self, start, end, weight=1):
        """
        Inicializa una arista con vértices de inicio y fin, y un peso opcional.
        
        Args:
            start: Vértice de inicio
            end: Vértice de fin
            weight: Peso de la arista (default: 1)
        """
        self._start = start
        self._end = end
        self._weight = weight
        self.energy_cost = weight  # El costo energético es igual al peso por defecto

    def start(self):
        """
        Obtiene el vértice de inicio.
        
        Returns:
            Vértice de inicio
        """
        return self._start

    def end(self):
        """
        Obtiene el vértice de fin.
        
        Returns:
            Vértice de fin
        """
        return self._end

    def element(self):
        """
        Obtiene el peso de la arista.
        
        Returns:
            int/float: Peso de la arista
        """
        return self._weight

    def endpoints(self):
        """
        Obtiene los vértices que conecta la arista.
        
        Returns:
            tuple: (vértice_inicio, vértice_fin)
        """
        return (self._start, self._end)

    def opposite(self, vertex):
        """
        Obtiene el vértice opuesto al dado en la arista.
        
        Args:
            vertex: Vértice del cual obtener el opuesto
            
        Returns:
            Vértice opuesto o None si el vértice dado no es parte de la arista
        """
        if vertex == self._start:
            return self._end
        elif vertex == self._end:
            return self._start
        return None

    def get_energy_cost(self):
        """Return energy cost for this edge."""
        return self.energy_cost

    def __eq__(self, other):
        """Check if two edges are equal."""
        if not isinstance(other, Edge):
            return False
        return (self._start == other._start and 
                self._end == other._end and 
                self._weight == other._weight)

    def __hash__(self):
        """Allow edge to be a map/set key."""
        return hash((self._start, self._end, self._weight))

    def __str__(self):
        """
        Representación en string de la arista.
        
        Returns:
            str: Representación de la arista
        """
        return f"Edge({self._start} -> {self._end}, weight={self._weight})"

    def __repr__(self):
        """Official string representation."""
        return f"Edge({self._start}, {self._end}, {self._weight})"

    def is_viable(self, drone_autonomy):
        """Check if the drone can traverse this edge with its current autonomy."""
        return self.energy_cost <= drone_autonomy 