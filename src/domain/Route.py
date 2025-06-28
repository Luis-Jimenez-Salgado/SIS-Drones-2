class Route:
    def __init__(self, route_id, nodes, total_cost=0, charging_points=None):
        """
        Inicializa una ruta con un ID y una lista de nodos.
        
        Args:
            route_id: Identificador único de la ruta
            nodes: Lista de nodos que forman la ruta
            total_cost: Costo total de la ruta
            charging_points: Lista de puntos de recarga en la ruta
        """
        self.route_id = route_id
        self.nodes = nodes
        self.frequency = 1
        self.total_cost = total_cost
        self.charging_points = charging_points if charging_points else []
        self._hash = hash(tuple(nodes))
        self.node_visits = {}  # Diccionario para registrar visitas a nodos
        self._initialize_node_visits()

    def _initialize_node_visits(self):
        """Inicializa el contador de visitas para cada nodo en la ruta."""
        for node in self.nodes:
            self.node_visits[node] = self.node_visits.get(node, 0) + 1

    def calculate_total_cost(self, graph):
        """
        Calcula el costo total de la ruta usando el grafo proporcionado.
        
        Args:
            graph: Grafo que contiene los nodos y aristas
            
        Returns:
            float: Costo total de la ruta
        """
        total = 0
        for i in range(len(self.nodes) - 1):
            edge = graph.get_edge(self.nodes[i], self.nodes[i + 1])
            if edge:
                total += edge.element()
        self.total_cost = total
        return total

    def identify_charging_points(self):
        """
        Identifica los puntos de recarga en la ruta.
        """
        self.charging_points = [node for node in self.nodes if node.startswith('C')]
        return self.charging_points

    def __eq__(self, other):
        """
        Compara si dos rutas son iguales basándose en sus nodos.
        
        Args:
            other: Otra ruta para comparar
            
        Returns:
            bool: True si las rutas tienen los mismos nodos en el mismo orden
        """
        if not isinstance(other, Route):
            return False
        return self.nodes == other.nodes

    def __lt__(self, other):
        """
        Compara si esta ruta es menor que otra basándose en la frecuencia.
        
        Args:
            other: Otra ruta para comparar
            
        Returns:
            bool: True si esta ruta tiene menor frecuencia
        """
        if not isinstance(other, Route):
            return False
        return self.frequency < other.frequency

    def __gt__(self, other):
        """
        Compara si esta ruta es mayor que otra basándose en la frecuencia.
        
        Args:
            other: Otra ruta para comparar
            
        Returns:
            bool: True si esta ruta tiene mayor frecuencia
        """
        if not isinstance(other, Route):
            return False
        return self.frequency > other.frequency

    def __hash__(self):
        """
        Calcula el hash de la ruta basado en sus nodos.
        
        Returns:
            int: Hash de la ruta
        """
        return self._hash

    def __str__(self):
        """
        Representación en string de la ruta.
        
        Returns:
            str: Representación de la ruta con su frecuencia y costo
        """
        charging = f" [Recarga en: {', '.join(self.charging_points)}]" if self.charging_points else ""
        return f"{' → '.join(self.nodes)} (Freq: {self.frequency}, Costo: {self.total_cost:.2f}){charging}"

    def increment_frequency(self):
        """
        Incrementa la frecuencia de uso de la ruta y actualiza las visitas a nodos.
        """
        self.frequency += 1
        for node in self.nodes:
            self.node_visits[node] = self.node_visits.get(node, 0) + 1

    def get_frequency(self):
        """
        Obtiene la frecuencia de uso de la ruta.
        
        Returns:
            int: Frecuencia de uso
        """
        return self.frequency

    def get_node_visits(self):
        """
        Obtiene el diccionario de visitas a nodos.
        
        Returns:
            dict: Diccionario con nodos y sus visitas
        """
        return self.node_visits

    def get_most_visited_nodes(self, node_type=None):
        """
        Obtiene los nodos más visitados, opcionalmente filtrados por tipo.
        
        Args:
            node_type: Tipo de nodo a filtrar ('storage', 'charging', 'client')
            
        Returns:
            list: Lista de tuplas (nodo, visitas) ordenadas por visitas
        """
        filtered_visits = self.node_visits
        if node_type:
            filtered_visits = {node: visits for node, visits in self.node_visits.items() 
                             if node.startswith(node_type[0].upper())}
        
        return sorted(filtered_visits.items(), key=lambda x: x[1], reverse=True)

    def is_viable(self, drone_autonomy):
        """
        Verifica si la ruta es viable dado la autonomía del dron.
        
        Args:
            drone_autonomy: Autonomía máxima del dron
            
        Returns:
            bool: True si la ruta es viable
        """
        return self.total_cost <= drone_autonomy

    def __le__(self, other):
        if not isinstance(other, Route):
            return NotImplemented
        return str(self.nodes) <= str(other.nodes)

    def __ge__(self, other):
        if not isinstance(other, Route):
            return NotImplemented
        return str(self.nodes) >= str(other.nodes) 