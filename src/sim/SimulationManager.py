from src.model.Graph import Graph
from src.domain.Client import Client
from src.domain.Order import Order
from src.domain.Route import Route
from src.sim.SimulationInitializer import SimulationInitializer
from src.tda.AVL import AVL
from typing import List, Dict, Optional, Any
import random
from datetime import datetime

class SimulationManager:
    """Singleton para manejar el estado global de la simulación"""
    
    _instance = None
    _initialized = False
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(SimulationManager, cls).__new__(cls)
        return cls._instance
    
    def __init__(self):
        if not self._initialized:
            self.graph = None
            self.clients = []
            self.orders = []
            self.routes = []
            self.route_frequencies = AVL()
            self.simulation_initializer = SimulationInitializer()
            self._initialized = True
    
    def is_initialized(self) -> bool:
        """Verifica si la simulación ha sido inicializada"""
        return self.graph is not None and len(self.clients) > 0
    
    def initialize_simulation(self, num_nodes: int = 15, num_edges: int = 20, num_orders: int = 10) -> Dict[str, Any]:
        """Inicializa una nueva simulación con los parámetros especificados"""
        try:
            # Crear nueva simulación
            self.graph = self.simulation_initializer.create_random_graph(num_nodes, num_edges)
            
            # Generar clientes basados en los nodos del grafo
            self.clients = self._generate_clients_from_graph()
            
            # Generar órdenes
            self.orders = self._generate_orders(num_orders)
            
            # Limpiar rutas anteriores
            self.routes = []
            self.route_frequencies = AVL()
            
            return {
                "success": True,
                "message": f"Simulación inicializada con {num_nodes} nodos, {num_edges} aristas y {num_orders} órdenes",
                "stats": {
                    "nodes": num_nodes,
                    "edges": num_edges,
                    "orders": num_orders,
                    "clients": len(self.clients)
                }
            }
            
        except Exception as e:
            return {
                "success": False,
                "message": f"Error al inicializar simulación: {str(e)}"
            }
    
    def _generate_clients_from_graph(self) -> List[Client]:
        """Genera clientes basados en los nodos del grafo"""
        clients = []
        nodes = list(self.graph.vertices())
        
        # Filtrar nodos de cliente (no almacenamiento ni recarga)
        client_nodes = [node for node in nodes if not node.startswith('S') and not node.startswith('C')]
        
        for i, node in enumerate(client_nodes):
            client = Client(
                client_id=f"CLIENT_{i+1:03d}",
                name=f"Cliente {i+1}",
                client_type="Regular",
                node_id=node
            )
            clients.append(client)
        
        return clients
    
    def _generate_orders(self, num_orders: int) -> List[Order]:
        """Genera órdenes aleatorias"""
        orders = []
        nodes = list(self.graph.vertices())
        
        # Nodos de almacenamiento (origen)
        storage_nodes = [node for node in nodes if node.startswith('S')]
        # Nodos de cliente (destino)
        client_nodes = [node for node in nodes if not node.startswith('S') and not node.startswith('C')]
        
        if not storage_nodes or not client_nodes:
            # Si no hay nodos de almacenamiento o cliente, usar cualquier nodo
            storage_nodes = nodes[:len(nodes)//2]
            client_nodes = nodes[len(nodes)//2:]
        
        for i in range(num_orders):
            origin = random.choice(storage_nodes)
            destination = random.choice(client_nodes)
            
            # Encontrar cliente correspondiente al nodo destino
            client = next((c for c in self.clients if c.node_id == destination), None)
            client_id = client.client_id if client else f"CLIENT_{i+1:03d}"
            client_name = client.name if client else f"Cliente {i+1}"
            
            order = Order(
                order_id=f"ORDER_{i+1:03d}",
                client_id=client_id,
                client_name=client_name,
                origin=origin,
                destination=destination,
                status="Pendiente",
                priority=random.choice(["Baja", "Normal", "Alta"]),
                created_at=datetime.now()
            )
            orders.append(order)
        
        return orders
    
    def get_graph(self) -> Graph:
        """Obtiene el grafo actual"""
        return self.graph
    
    def get_clients(self) -> List[Client]:
        """Obtiene la lista de clientes"""
        return self.clients
    
    def get_orders(self) -> List[Order]:
        """Obtiene la lista de órdenes"""
        return self.orders
    
    def get_routes(self) -> List[Route]:
        """Obtiene la lista de rutas calculadas"""
        return self.routes
    
    def add_route(self, route: Route):
        """Agrega una nueva ruta y actualiza frecuencias"""
        self.routes.append(route)
        
        # Actualizar frecuencias en el AVL
        route_key = f"{route.origin} -> {route.destination}"
        current_freq = self.route_frequencies.search(route_key)
        if current_freq is None:
            self.route_frequencies.insert(route_key, 1)
        else:
            self.route_frequencies.insert(route_key, current_freq + 1)
    
    def get_route_frequencies(self) -> Dict[str, int]:
        """Obtiene las frecuencias de rutas como diccionario"""
        frequencies = {}
        self._collect_frequencies(self.route_frequencies.root, frequencies)
        return frequencies
    
    def _collect_frequencies(self, node, frequencies):
        """Recolecta frecuencias del árbol AVL"""
        if node is not None:
            frequencies[node.key] = node.value
            self._collect_frequencies(node.left, frequencies)
            self._collect_frequencies(node.right, frequencies)
    
    def calculate_route(self, origin: str, destination: str, algorithm: str = "dijkstra") -> Dict[str, Any]:
        """Calcula una ruta entre dos nodos"""
        if not self.graph:
            return {"success": False, "message": "No hay grafo disponible"}
        
        try:
            if algorithm.lower() == "dijkstra":
                path, cost = self.graph.dijkstra_shortest_path(origin, destination)
            elif algorithm.lower() == "floyd_warshall":
                path, cost = self.graph.floyd_warshall_shortest_path(origin, destination)
            else:
                return {"success": False, "message": "Algoritmo no soportado"}
            
            if path is None:
                return {"success": False, "message": "No se encontró ruta entre los nodos"}
            
            # Crear objeto Route
            route = Route(
                route_id=f"ROUTE_{len(self.routes)+1:03d}",
                origin=origin,
                destination=destination,
                path=path,
                cost=cost,
                algorithm=algorithm,
                created_at=datetime.now()
            )
            
            # Agregar a la lista de rutas
            self.add_route(route)
            
            return {
                "success": True,
                "route": {
                    "route_id": route.route_id,
                    "origin": route.origin,
                    "destination": route.destination,
                    "path": route.path,
                    "cost": route.cost,
                    "algorithm": route.algorithm,
                    "created_at": route.created_at.isoformat()
                }
            }
            
        except Exception as e:
            return {"success": False, "message": f"Error al calcular ruta: {str(e)}"}
    
    def get_minimum_spanning_tree(self) -> Dict[str, Any]:
        """Obtiene el árbol de expansión mínima"""
        if not self.graph:
            return {"success": False, "message": "No hay grafo disponible"}
        
        try:
            mst_edges = self.graph.kruskal_mst()
            return {
                "success": True,
                "mst_edges": [(edge.endpoints()[0], edge.endpoints()[1], edge.element()) for edge in mst_edges]
            }
        except Exception as e:
            return {"success": False, "message": f"Error al calcular MST: {str(e)}"}
    
    def complete_order(self, order_id: str) -> Dict[str, Any]:
        """Marca una orden como completada"""
        order = next((o for o in self.orders if o.order_id == order_id), None)
        if not order:
            return {"success": False, "message": "Orden no encontrada"}
        
        order.status = "Completada"
        order.completed_at = datetime.now()
        
        return {"success": True, "message": f"Orden {order_id} marcada como completada"}
    
    def cancel_order(self, order_id: str) -> Dict[str, Any]:
        """Cancela una orden"""
        order = next((o for o in self.orders if o.order_id == order_id), None)
        if not order:
            return {"success": False, "message": "Orden no encontrada"}
        
        order.status = "Cancelada"
        order.cancelled_at = datetime.now()
        
        return {"success": True, "message": f"Orden {order_id} cancelada"}
    
    def get_statistics(self) -> Dict[str, Any]:
        """Obtiene estadísticas generales de la simulación"""
        if not self.is_initialized():
            return {"success": False, "message": "Simulación no inicializada"}
        
        nodes = list(self.graph.vertices())
        storage_nodes = [n for n in nodes if n.startswith('S')]
        recharge_nodes = [n for n in nodes if n.startswith('C')]
        client_nodes = [n for n in nodes if not n.startswith('S') and not n.startswith('C')]
        
        completed_orders = [o for o in self.orders if o.status == "Completada"]
        pending_orders = [o for o in self.orders if o.status == "Pendiente"]
        cancelled_orders = [o for o in self.orders if o.status == "Cancelada"]
        
        return {
            "success": True,
            "statistics": {
                "total_nodes": len(nodes),
                "storage_nodes": len(storage_nodes),
                "recharge_nodes": len(recharge_nodes),
                "client_nodes": len(client_nodes),
                "total_edges": len(self.graph.edges()),
                "total_clients": len(self.clients),
                "total_orders": len(self.orders),
                "completed_orders": len(completed_orders),
                "pending_orders": len(pending_orders),
                "cancelled_orders": len(cancelled_orders),
                "total_routes": len(self.routes)
            }
        }
    
    def reset_simulation(self):
        """Reinicia la simulación"""
        self.graph = None
        self.clients = []
        self.orders = []
        self.routes = []
        self.route_frequencies = AVL()

# Instancia global del SimulationManager
simulation_manager = SimulationManager() 