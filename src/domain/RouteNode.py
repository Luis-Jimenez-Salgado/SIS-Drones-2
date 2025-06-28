class RouteNode:
    def __init__(self, route, frequency=1):
        """
        Inicializa un nodo de ruta.
        
        Args:
            route (list): Lista de nodos que forman la ruta
            frequency (int): Frecuencia de uso de la ruta
        """
        self.route = route  # Lista de nodos en la ruta
        self.frequency = frequency
        self.left = None
        self.right = None
        self.height = 1
        
    def __str__(self):
        """
        Representación en string del nodo.
        
        Returns:
            str: Ruta en formato 'nodo1 → nodo2 → ... → nodoN (Freq: n)'
        """
        route_str = " → ".join(self.route)
        return f"{route_str} (Freq: {self.frequency})"
        
    def __lt__(self, other):
        """
        Compara dos nodos de ruta.
        La comparación se hace por la representación en string de la ruta.
        
        Args:
            other: Otro nodo de ruta para comparar
            
        Returns:
            bool: True si este nodo es menor que el otro
        """
        return str(self) < str(other)
        
    def __eq__(self, other):
        """
        Compara si dos nodos de ruta son iguales.
        Son iguales si tienen la misma secuencia de nodos.
        
        Args:
            other: Otro nodo de ruta para comparar
            
        Returns:
            bool: True si los nodos son iguales
        """
        if not isinstance(other, RouteNode):
            return False
        return self.route == other.route 