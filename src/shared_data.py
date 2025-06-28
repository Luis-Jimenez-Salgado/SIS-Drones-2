"""
Módulo para compartir datos entre el Dashboard y la API
Permite que ambos componentes accedan a la misma información de simulación
"""

import threading
import json
import os
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict
from datetime import datetime
from .tda.Map import Map

@dataclass
class SharedSimulationData:
    """Estructura de datos compartidos para la simulación"""
    graph: Any = None
    orders: List = None
    clients: List = None
    routes: List = None
    node_visits: Dict = None
    route_counter: int = 0
    order_counter: int = 0
    initialized: bool = False
    
    def __post_init__(self):
        if self.orders is None:
            self.orders = []
        if self.clients is None:
            self.clients = []
        if self.routes is None:
            self.routes = []
        if self.node_visits is None:
            self.node_visits = {}

class SharedDataManager:
    """Gestor de datos compartidos entre Dashboard y API usando archivos JSON y Maps para acceso O(1)"""
    
    def __init__(self, data_file="shared_simulation_data.json"):
        self._data_file = data_file
        self._lock = threading.Lock()
        self._data = SharedSimulationData()
        # Maps para acceso O(1) a clientes y órdenes
        self._clients_map = Map()
        self._orders_map = Map()
    
    def _convert_datetime_to_string(self, obj):
        """Convertir objetos datetime a strings para serialización JSON"""
        if isinstance(obj, datetime):
            return obj.isoformat()
        elif isinstance(obj, dict):
            return {key: self._convert_datetime_to_string(value) for key, value in obj.items()}
        elif isinstance(obj, list):
            return [self._convert_datetime_to_string(item) for item in obj]
        else:
            return obj
    
    def _update_maps(self, clients_data: List, orders_data: List):
        """Actualizar los Maps internos con los nuevos datos"""
        # Limpiar Maps existentes
        for key in self._clients_map.keys():
            self._clients_map.remove(key)
        for key in self._orders_map.keys():
            self._orders_map.remove(key)
        
        # Poblar Maps con nuevos datos
        for client in clients_data:
            self._clients_map.put(client['client_id'], client)
        
        for order in orders_data:
            self._orders_map.put(order['order_id'], order)
    
    def update_from_dashboard(self, session_state_data: Dict[str, Any]):
        """Actualizar datos desde el dashboard"""
        print("🔄 Iniciando actualización de datos compartidos...")
        try:
            with self._lock:
                # Extraer datos básicos que se pueden serializar
                clients_data = []
                for client in session_state_data.get('clients', []):
                    client_dict = {
                        'client_id': client.client_id,
                        'name': client.name,
                        'client_type': client.client_type,
                        'node_id': getattr(client, 'node_id', 'N/A'),
                        'created_at': getattr(client, 'created_at', None)
                    }
                    clients_data.append(client_dict)
                
                orders_data = []
                for order in session_state_data.get('orders', []):
                    # Obtener información de la ruta si existe
                    route_info = None
                    if hasattr(order, 'route') and order.route:
                        route_info = {
                            'route_id': order.route.route_id,
                            'nodes': order.route.nodes,
                            'frequency': order.route.frequency
                        }
                    
                    order_dict = {
                        'order_id': order.order_id,
                        'origin': order.origin,
                        'destination': order.destination,
                        'client_id': order.client_id,
                        'client_name': order.client_name,
                        'status': getattr(order, 'status', 'Pendiente'),
                        'priority': getattr(order, 'priority', 'Normal'),
                        'route_cost': getattr(order, 'route_cost', 0),
                        'creation_date': getattr(order, 'creation_date', None),
                        'delivery_date': getattr(order, 'delivery_date', None),
                        'route_info': route_info  # Agregar información de la ruta
                    }
                    orders_data.append(order_dict)
                
                routes_data = []
                for route in session_state_data.get('routes', []):
                    try:
                        route_dict = {
                            'route_id': route.route_id,
                            'nodes': route.nodes,
                            'frequency': route.frequency,
                            'node_visits': dict(route.get_node_visits())  # Convertir a dict
                        }
                        routes_data.append(route_dict)
                    except Exception as e:
                        print(f"⚠️  Error serializando ruta {getattr(route, 'route_id', 'unknown')}: {e}")
                        # Agregar ruta básica sin node_visits
                        route_dict = {
                            'route_id': getattr(route, 'route_id', 'unknown'),
                            'nodes': getattr(route, 'nodes', []),
                            'frequency': getattr(route, 'frequency', 1),
                            'node_visits': {}
                        }
                        routes_data.append(route_dict)
                
                # Serializar información del grafo
                graph_data = None
                if session_state_data.get('graph'):
                    graph = session_state_data['graph']
                    try:
                        graph_data = {
                            'vertices': list(graph.vertices()),
                            'edges': []
                        }
                        for edge in graph.edges():
                            # Solo serializar datos básicos, no métodos
                            graph_data['edges'].append({
                                'start': str(edge.start),
                                'end': str(edge.end),
                                'weight': float(edge.element())
                            })
                    except Exception as e:
                        print(f"⚠️  Error serializando grafo: {e}")
                        graph_data = None
                
                # Crear estructura de datos completa
                data_dict = {
                    'initialized': session_state_data.get('graph') is not None,
                    'route_counter': session_state_data.get('route_counter', 0),
                    'order_counter': session_state_data.get('order_counter', 0),
                    'node_visits': session_state_data.get('node_visits', {}),
                    'clients': clients_data,
                    'orders': orders_data,
                    'routes': routes_data,
                    'graph': graph_data,  # Agregar datos del grafo
                    'last_updated': datetime.now().isoformat()
                }
                
                # Convertir objetos datetime a strings
                data_dict = self._convert_datetime_to_string(data_dict)
                
                # Guardar en archivo JSON
                with open(self._data_file, 'w', encoding='utf-8') as f:
                    json.dump(data_dict, f, indent=2, ensure_ascii=False)
                
                # Actualizar Maps internos para acceso O(1)
                self._update_maps(clients_data, orders_data)
                
                print(f"✅ Datos guardados exitosamente en {self._data_file}")
                print(f"📊 Resumen: {len(clients_data)} clientes, {len(orders_data)} órdenes, {len(routes_data)} rutas")
                print(f"🗺️ Maps actualizados: {self._clients_map.size()} clientes, {self._orders_map.size()} órdenes")
                if graph_data:
                    print(f"🌐 Grafo: {len(graph_data['vertices'])} nodos, {len(graph_data['edges'])} aristas")
                
        except Exception as e:
            import traceback
            print(f"❌ Error guardando datos compartidos: {e}")
            traceback.print_exc()
    
    def _load_data(self):
        """Cargar datos desde archivo JSON"""
        try:
            if os.path.exists(self._data_file):
                print(f"📖 Leyendo archivo: {self._data_file}")
                with open(self._data_file, 'r', encoding='utf-8') as f:
                    data_dict = json.load(f)
                    print(f"✅ Datos cargados: initialized={data_dict.get('initialized')}, clients={len(data_dict.get('clients', []))}")
                    
                    # Actualizar Maps con datos cargados
                    clients_data = data_dict.get('clients', [])
                    orders_data = data_dict.get('orders', [])
                    self._update_maps(clients_data, orders_data)
                    
                    return data_dict
            else:
                print(f"❌ Archivo no encontrado: {self._data_file}")
            return None
        except Exception as e:
            print(f"❌ Error cargando datos compartidos: {e}")
            import traceback
            traceback.print_exc()
            return None
    
    def is_initialized(self) -> bool:
        """Verificar si la simulación está inicializada"""
        data = self._load_data()
        return data.get('initialized', False) if data else False
    
    def get_clients(self) -> List:
        """Obtener lista de clientes"""
        data = self._load_data()
        if data and 'clients' in data:
            return data['clients']
        return []
    
    def get_orders(self) -> List:
        """Obtener lista de órdenes"""
        data = self._load_data()
        if data and 'orders' in data:
            return data['orders']
        return []
    
    def get_routes(self) -> List:
        """Obtener lista de rutas"""
        data = self._load_data()
        if data and 'routes' in data:
            return data['routes']
        return []
    
    def get_graph(self):
        """Obtener el grafo reconstruido desde los datos serializados"""
        data = self._load_data()
        if not data or 'graph' not in data or not data['graph']:
            return None
        
        try:
            from src.model.Graph import Graph
            from src.model.Edge import Edge
            
            graph = Graph()
            graph_data = data['graph']
            
            # Agregar vértices
            for vertex in graph_data['vertices']:
                graph.add_vertex(vertex)
            
            # Agregar aristas
            for edge_data in graph_data['edges']:
                graph.add_edge(edge_data['start'], edge_data['end'], edge_data['weight'])
            
            print(f"✅ Grafo reconstruido: {len(graph_data['vertices'])} nodos, {len(graph_data['edges'])} aristas")
            return graph
            
        except Exception as e:
            print(f"❌ Error reconstruyendo grafo: {e}")
            return None
    
    def get_nodes_from_routes(self) -> List:
        """Obtener lista de nodos únicos desde las rutas"""
        routes = self.get_routes()
        nodes = set()
        for route in routes:
            if 'nodes' in route:
                nodes.update(route['nodes'])
        return list(nodes)
    
    def get_node_visits(self) -> Dict:
        """Obtener visitas a nodos"""
        data = self._load_data()
        if data and 'node_visits' in data:
            return data['node_visits']
        return {}
    
    def get_client_by_id(self, client_id: str):
        """Obtener cliente por ID usando Map para acceso O(1)"""
        # Intentar obtener desde Map primero
        client = self._clients_map.get(client_id)
        if client:
            return client
        
        # Fallback a búsqueda en lista si Map no tiene datos
        clients = self.get_clients()
        for client in clients:
            if client['client_id'] == client_id:
                return client
        return None
    
    def get_order_by_id(self, order_id: str):
        """Obtener orden por ID usando Map para acceso O(1)"""
        # Intentar obtener desde Map primero
        order = self._orders_map.get(order_id)
        if order:
            return order
        
        # Fallback a búsqueda en lista si Map no tiene datos
        orders = self.get_orders()
        for order in orders:
            if order['order_id'] == order_id:
                return order
        return None
    
    def get_orders_by_client(self, client_id: str) -> List:
        """Obtener órdenes de un cliente específico"""
        orders = self.get_orders()
        return [order for order in orders if order['client_id'] == client_id]
    
    def get_simulation_summary(self) -> Dict:
        """Obtener resumen de la simulación"""
        data = self._load_data()
        
        if not data or not data.get('initialized', False):
            return {"initialized": False, "message": "Simulación no inicializada"}
        
        clients = data.get('clients', [])
        orders = data.get('orders', [])
        routes = data.get('routes', [])
        node_visits = data.get('node_visits', {})
        
        # Contar nodos por tipo basado en las visitas
        storage_nodes = [n for n in node_visits.keys() if n.startswith('S')]
        charging_nodes = [n for n in node_visits.keys() if n.startswith('C')]
        client_nodes = [n for n in node_visits.keys() if n.startswith('T')]
        
        total_nodes = len(set(list(node_visits.keys())))
        
        return {
            "initialized": True,
            "simulation_summary": {
                "total_nodes": total_nodes,
                "storage_nodes": len(storage_nodes),
                "charging_nodes": len(charging_nodes),
                "client_nodes": len(client_nodes),
                "total_orders": len(orders),
                "total_clients": len(clients),
                "total_routes": len(routes)
            },
            "node_distribution": {
                "storage_percentage": (len(storage_nodes) / total_nodes * 100) if total_nodes > 0 else 0,
                "charging_percentage": (len(charging_nodes) / total_nodes * 100) if total_nodes > 0 else 0,
                "client_percentage": (len(client_nodes) / total_nodes * 100) if total_nodes > 0 else 0
            }
        }

    def set_order_status(self, order_id: str, new_status: str) -> bool:
        """Actualiza el estado de una orden y guarda el cambio en el archivo JSON. Retorna True si se modificó."""
        with self._lock:
            data = self._load_data()
            if not data or 'orders' not in data:
                return False
            modified = False
            for order in data['orders']:
                if order['order_id'] == order_id:
                    if order.get('status', 'Pendiente') != new_status:
                        order['status'] = new_status
                        if new_status == 'Completada':
                            order['delivery_date'] = datetime.now().isoformat()
                        modified = True
                    break
            if modified:
                # Guardar cambios
                with open(self._data_file, 'w', encoding='utf-8') as f:
                    json.dump(data, f, indent=2, ensure_ascii=False)
                
                # Actualizar Map correspondiente
                if self._orders_map.contains(order_id):
                    order_data = self._orders_map.get(order_id)
                    order_data['status'] = new_status
                    if new_status == 'Completada':
                        order_data['delivery_date'] = datetime.now().isoformat()
                    self._orders_map.put(order_id, order_data)
            return modified

    def force_node_visits_example(self):
        """Forzar node_visits con datos de ejemplo para pruebas de la API"""
        data = self._load_data() or {}
        # Ejemplo: 3 almacenes, 3 recargas, 9 clientes
        node_visits = {
            'S1': 5, 'S2': 3, 'S3': 2,
            'C1': 7, 'C2': 4, 'C3': 1,
            'T1': 10, 'T2': 8, 'T3': 6, 'T4': 5, 'T5': 4, 'T6': 3, 'T7': 2, 'T8': 1, 'T9': 1
        }
        data['node_visits'] = node_visits
        data['initialized'] = True  # Marcar como inicializado para que la API funcione
        with open(self._data_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        print('✅ node_visits de ejemplo guardado en shared_simulation_data.json')
        print('✅ Simulación marcada como inicializada')

# Instancia global del gestor de datos compartidos
shared_data_manager = SharedDataManager() 