from .Edge import Edge
from .vertex import Vertex

class Graph:
    def __init__(self):
        self.adjacency_list = {}  # Para almacenar los vértices y sus conexiones
        self.edge_weights = {}    # Para almacenar los pesos de las aristas

    def add_vertex(self, vertex):
        """
        Agrega un vértice al grafo si no existe.
        
        Args:
            vertex: Identificador del vértice
        """
        if vertex not in self.adjacency_list:
            self.adjacency_list[vertex] = set()

    def add_edge(self, start, end, weight=1):
        """
        Agrega una arista con peso entre dos vértices.
        
        Args:
            start: Vértice de inicio
            end: Vértice de fin
            weight: Peso de la arista (default: 1)
        """
        # Asegurarse de que ambos vértices existan
        self.add_vertex(start)
        self.add_vertex(end)
        
        # Agregar la conexión y el peso
        self.adjacency_list[start].add(end)
        self.edge_weights[(start, end)] = weight

    def vertices(self):
        """
        Retorna la lista de todos los vértices en el grafo.
        
        Returns:
            list: Lista de vértices
        """
        return list(self.adjacency_list.keys())

    def get_neighbors(self, vertex):
        """
        Obtiene los vértices vecinos de un vértice dado.
        
        Args:
            vertex: Vértice del cual obtener vecinos
            
        Returns:
            list: Lista de vértices vecinos
        """
        return list(self.adjacency_list.get(vertex, set()))

    def get_edge(self, start, end):
        """
        Obtiene la arista entre dos vértices.
        
        Args:
            start: Vértice de inicio
            end: Vértice de fin
            
        Returns:
            Edge: Objeto Edge si existe la arista, None en caso contrario
        """
        weight = self.edge_weights.get((start, end))
        if weight is not None:
            return Edge(start, end, weight)
        return None

    def has_edge(self, start, end):
        """
        Verifica si existe una arista entre dos vértices.
        
        Args:
            start: Vértice de inicio
            end: Vértice de fin
            
        Returns:
            bool: True si existe la arista, False en caso contrario
        """
        return (start, end) in self.edge_weights

    def get_edge_weight(self, start, end):
        """
        Obtiene el peso de una arista.
        
        Args:
            start: Vértice de inicio
            end: Vértice de fin
            
        Returns:
            int/float: Peso de la arista o None si no existe
        """
        return self.edge_weights.get((start, end))

    def __str__(self):
        """
        Representación en string del grafo.
        
        Returns:
            str: Representación del grafo
        """
        return f"Graph(vertices={list(self.adjacency_list.keys())}, edges={self.edge_weights})"

    def edges(self):
        edges = []
        seen = set()  # Para evitar duplicados en grafos no dirigidos
        for start in self.adjacency_list:
            for end in self.adjacency_list[start]:
                if (start, end) not in seen and (end, start) not in seen:
                    weight = self.edge_weights.get((start, end), 1)
                    edge = Edge(start, end, weight)
                    edges.append(edge)
                    seen.add((start, end))
        return edges

    def bfs(self, start):
        visited = set()
        queue = [start]
        result = []

        while queue:
            vertex = queue.pop(0)
            if vertex not in visited:
                visited.add(vertex)
                result.append(vertex)
                queue.extend(set(self.adjacency_list.get(vertex, [])) - visited)

        return result

    def dfs(self, start, visited=None):
        if visited is None:
            visited = set()
        visited.add(start)
        result = [start]

        for neighbor in self.adjacency_list.get(start, []):
            if neighbor not in visited:
                result.extend(self.dfs(neighbor, visited))

        return result

    def topological_sort(self):
        visited = set()
        stack = []

        def dfs(vertex):
            visited.add(vertex)
            for neighbor in self.adjacency_list.get(vertex, []):
                if neighbor not in visited:
                    dfs(neighbor)
            stack.append(vertex)

        for vertex in self.adjacency_list:
            if vertex not in visited:
                dfs(vertex)

        return stack[::-1] 

    def has_vertex(self, vertex):
        """
        Verifica si existe un vértice en el grafo.
        
        Args:
            vertex: Identificador del vértice a verificar
            
        Returns:
            bool: True si existe el vértice, False en caso contrario
        """
        return vertex in self.adjacency_list

    def get_vertex(self, vertex_id):
        """
        Obtiene un vértice del grafo por su identificador.
        
        Args:
            vertex_id: Identificador del vértice
            
        Returns:
            str: El identificador del vértice si existe, None en caso contrario
        """
        if self.has_vertex(vertex_id):
            return vertex_id
        return None

    def get_connections(self, vertex):
        """
        Obtiene todos los vértices conectados a un vértice dado.
        
        Args:
            vertex: Identificador del vértice
            
        Returns:
            list: Lista de identificadores de vértices conectados
        """
        if self.has_vertex(vertex):
            return list(self.adjacency_list[vertex])
        return [] 

    def kruskal_mst(self):
        """
        Calcula el árbol de expansión mínima (MST) usando el algoritmo de Kruskal.
        Returns:
            List[Tuple[str, str, float]]: Lista de aristas (u, v, peso) del MST
        """
        parent = {v: v for v in self.vertices()}
        rank = {v: 0 for v in self.vertices()}
        def find(v):
            while parent[v] != v:
                parent[v] = parent[parent[v]]
                v = parent[v]
            return v
        def union(u, v):
            ru, rv = find(u), find(v)
            if ru == rv:
                return False
            if rank[ru] < rank[rv]:
                parent[ru] = rv
            else:
                parent[rv] = ru
                if rank[ru] == rank[rv]:
                    rank[ru] += 1
            return True
        edges = [(e.start(), e.end(), e.element()) for e in self.edges()]
        edges.sort(key=lambda x: x[2])
        mst = []
        for u, v, w in edges:
            if union(u, v):
                mst.append((u, v, w))
        return mst 