"""
Algoritmos de optimización para el sistema de drones.
Incluye Dijkstra para rutas más cortas y Kruskal para árbol de expansión mínima.
"""

import heapq
from typing import Dict, List, Tuple, Optional, Set
from .Graph import Graph
from .Edge import Edge


class DijkstraAlgorithm:
    """
    Implementación del algoritmo de Dijkstra para encontrar el camino más corto
    entre dos nodos en un grafo ponderado.
    """
    
    def __init__(self, graph: Graph):
        """
        Inicializa el algoritmo con un grafo.
        
        Args:
            graph: Grafo sobre el cual ejecutar el algoritmo
        """
        self.graph = graph
        self.MAX_AUTONOMY = 50  # Autonomía máxima del dron
    
    def find_shortest_path(self, start: str, end: str, 
                          consider_charging: bool = True) -> Tuple[List[str], float, Dict]:
        """
        Encuentra el camino más corto entre dos nodos.
        
        Args:
            start: Nodo de inicio
            end: Nodo de destino
            consider_charging: Si considerar estaciones de recarga
            
        Returns:
            Tuple con (camino, costo_total, información_adicional)
        """
        if not self.graph.has_vertex(start) or not self.graph.has_vertex(end):
            return [], float('inf'), {}
        
        # Inicialización
        distances = {vertex: float('inf') for vertex in self.graph.vertices()}
        distances[start] = 0
        previous = {vertex: None for vertex in self.graph.vertices()}
        visited = set()
        
        # Cola de prioridad: (distancia, nodo)
        pq = [(0, start)]
        
        while pq:
            current_distance, current_vertex = heapq.heappop(pq)
            
            if current_vertex in visited:
                continue
                
            visited.add(current_vertex)
            
            # Si llegamos al destino, terminamos
            if current_vertex == end:
                break
            
            # Explorar vecinos
            for neighbor in self.graph.get_neighbors(current_vertex):
                if neighbor in visited:
                    continue
                
                edge_weight = self.graph.get_edge_weight(current_vertex, neighbor)
                if edge_weight is None:
                    continue
                
                # Verificar autonomía si es necesario
                if consider_charging and not self._can_reach_with_autonomy(
                    current_vertex, neighbor, current_distance):
                    continue
                
                new_distance = current_distance + edge_weight
                
                if new_distance < distances[neighbor]:
                    distances[neighbor] = new_distance
                    previous[neighbor] = current_vertex
                    heapq.heappush(pq, (new_distance, neighbor))
        
        # Reconstruir el camino
        path = self._reconstruct_path(previous, start, end)
        total_cost = distances[end] if distances[end] != float('inf') else float('inf')
        
        # Información adicional
        info = {
            'total_cost': total_cost,
            'charging_stations': self._get_charging_stations_in_path(path) if path else [],
            'autonomy_respected': self._check_autonomy_respect(path, total_cost),
            'path_length': len(path) if path else 0
        }
        
        return path, total_cost, info
    
    def _can_reach_with_autonomy(self, current: str, neighbor: str, 
                                current_distance: float) -> bool:
        """
        Verifica si el dron puede llegar al vecino respetando la autonomía.
        
        Args:
            current: Nodo actual
            neighbor: Nodo vecino
            current_distance: Distancia acumulada hasta el nodo actual
            
        Returns:
            bool: True si puede llegar respetando autonomía
        """
        edge_weight = self.graph.get_edge_weight(current, neighbor)
        if edge_weight is None:
            return False
        
        # Si el vecino es una estación de recarga, siempre se puede llegar
        if neighbor.startswith('C'):
            return True
        
        # Verificar si la autonomía es suficiente
        return edge_weight <= self.MAX_AUTONOMY
    
    def _reconstruct_path(self, previous: Dict[str, Optional[str]], 
                         start: str, end: str) -> List[str]:
        """
        Reconstruye el camino desde el diccionario de nodos anteriores.
        
        Args:
            previous: Diccionario de nodos anteriores
            start: Nodo de inicio
            end: Nodo de destino
            
        Returns:
            Lista de nodos que forman el camino
        """
        if previous[end] is None and end != start:
            return []  # No hay camino
        
        path = []
        current = end
        
        while current is not None:
            path.append(current)
            current = previous[current]
        
        return path[::-1]  # Invertir para obtener el orden correcto
    
    def _get_charging_stations_in_path(self, path: List[str]) -> List[str]:
        """
        Obtiene las estaciones de recarga en el camino.
        
        Args:
            path: Lista de nodos del camino
            
        Returns:
            Lista de estaciones de recarga en el camino
        """
        return [node for node in path if node.startswith('C')]
    
    def _check_autonomy_respect(self, path: List[str], total_cost: float) -> bool:
        """
        Verifica si el camino respeta la autonomía del dron.
        
        Args:
            path: Lista de nodos del camino
            total_cost: Costo total del camino
            
        Returns:
            bool: True si respeta la autonomía
        """
        if not path:
            return False
        
        # Si hay estaciones de recarga en el camino, se puede completar
        charging_stations = self._get_charging_stations_in_path(path)
        if charging_stations:
            return True
        
        # Si no hay estaciones de recarga, verificar que el costo total
        # no exceda la autonomía
        return total_cost <= self.MAX_AUTONOMY


class KruskalMST:
    """
    Implementación del algoritmo de Kruskal para encontrar el árbol de expansión mínima.
    """
    
    def __init__(self, graph: Graph):
        """
        Inicializa el algoritmo con un grafo.
        
        Args:
            graph: Grafo sobre el cual ejecutar el algoritmo
        """
        self.graph = graph
    
    def find_mst(self) -> Tuple[List[Edge], float]:
        """
        Encuentra el árbol de expansión mínima usando Kruskal.
        
        Returns:
            Tuple con (lista_de_aristas_del_mst, costo_total)
        """
        # Obtener todas las aristas del grafo
        edges = self.graph.edges()
        
        # Ordenar aristas por peso
        edges.sort(key=lambda edge: edge.element())
        
        # Estructura Union-Find para detectar ciclos
        parent = {vertex: vertex for vertex in self.graph.vertices()}
        rank = {vertex: 0 for vertex in self.graph.vertices()}
        
        mst_edges = []
        total_cost = 0
        
        for edge in edges:
            start, end = edge.endpoints()
            
            # Verificar si agregar esta arista crearía un ciclo
            if self._find(parent, start) != self._find(parent, end):
                mst_edges.append(edge)
                total_cost += edge.element()
                self._union(parent, rank, start, end)
        
        return mst_edges, total_cost
    
    def _find(self, parent: Dict[str, str], vertex: str) -> str:
        """
        Encuentra la raíz del conjunto al que pertenece un vértice.
        
        Args:
            parent: Diccionario de padres
            vertex: Vértice a buscar
            
        Returns:
            Raíz del conjunto
        """
        if parent[vertex] != vertex:
            parent[vertex] = self._find(parent, parent[vertex])
        return parent[vertex]
    
    def _union(self, parent: Dict[str, str], rank: Dict[str, int], 
               x: str, y: str) -> None:
        """
        Une dos conjuntos usando union by rank.
        
        Args:
            parent: Diccionario de padres
            rank: Diccionario de rangos
            x: Primer vértice
            y: Segundo vértice
        """
        root_x = self._find(parent, x)
        root_y = self._find(parent, y)
        
        if root_x == root_y:
            return
        
        if rank[root_x] < rank[root_y]:
            parent[root_x] = root_y
        elif rank[root_x] > rank[root_y]:
            parent[root_y] = root_x
        else:
            parent[root_y] = root_x
            rank[root_x] += 1
    
    def get_mst_nodes(self, mst_edges: List[Edge]) -> Set[str]:
        """
        Obtiene todos los nodos que forman parte del MST.
        
        Args:
            mst_edges: Lista de aristas del MST
            
        Returns:
            Conjunto de nodos del MST
        """
        nodes = set()
        for edge in mst_edges:
            start, end = edge.endpoints()
            nodes.add(start)
            nodes.add(end)
        return nodes


class RouteOptimizer:
    """
    Clase principal para optimización de rutas que integra Dijkstra y Kruskal.
    """
    
    def __init__(self, graph: Graph):
        """
        Inicializa el optimizador de rutas.
        
        Args:
            graph: Grafo del sistema
        """
        self.graph = graph
        self.dijkstra = DijkstraAlgorithm(graph)
        self.kruskal = KruskalMST(graph)
    
    def optimize_route(self, start: str, end: str, 
                      algorithm: str = "dijkstra") -> Dict:
        """
        Optimiza una ruta entre dos nodos.
        
        Args:
            start: Nodo de inicio
            end: Nodo de destino
            algorithm: Algoritmo a usar ("dijkstra" o "mst")
            
        Returns:
            Diccionario con información de la ruta optimizada
        """
        if algorithm.lower() == "dijkstra":
            path, cost, info = self.dijkstra.find_shortest_path(start, end)
            return {
                'algorithm': 'Dijkstra',
                'path': path,
                'total_cost': cost,
                'charging_stations': info['charging_stations'],
                'autonomy_respected': info['autonomy_respected'],
                'path_length': info['path_length']
            }
        elif algorithm.lower() == "mst":
            mst_edges, total_cost = self.kruskal.find_mst()
            mst_nodes = self.kruskal.get_mst_nodes(mst_edges)
            
            # Para MST, verificamos si ambos nodos están conectados
            if start in mst_nodes and end in mst_nodes:
                # Usar Dijkstra en el MST para encontrar el camino
                # (Esto requeriría crear un subgrafo del MST)
                return {
                    'algorithm': 'MST',
                    'mst_edges': mst_edges,
                    'mst_nodes': list(mst_nodes),
                    'total_mst_cost': total_cost,
                    'note': 'MST conecta todos los nodos, use Dijkstra para ruta específica'
                }
            else:
                return {
                    'algorithm': 'MST',
                    'error': 'Los nodos no están conectados en el MST'
                }
        else:
            return {
                'error': f'Algoritmo "{algorithm}" no soportado'
            }
    
    def get_mst_visualization_data(self) -> Dict:
        """
        Obtiene datos del MST para visualización.
        
        Returns:
            Diccionario con datos del MST
        """
        mst_edges, total_cost = self.kruskal.find_mst()
        mst_nodes = self.kruskal.get_mst_nodes(mst_edges)
        
        return {
            'edges': mst_edges,
            'nodes': list(mst_nodes),
            'total_cost': total_cost,
            'edge_count': len(mst_edges),
            'node_count': len(mst_nodes)
        } 