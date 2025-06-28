import random
import string
from src.model.Graph import Graph
from src.domain.Client import Client
from src.domain.Order import Order
from src.domain.Route import Route
import streamlit as st
from collections import deque

class SimulationInitializer:
    def __init__(self):
        """
        Inicializa el simulador.
        """
        self.graph = None
        self.orders = []
        self.clients = []
        self.routes = []
        self.route_frequencies = {}
        self.node_types = {}
        self.DRONE_AUTONOMY = 50
        self.path_cache = {}  # Cache para rutas ya calculadas
        self._storage_nodes = []  # Cache para nodos de almacenamiento
        self._charging_nodes = []  # Cache para nodos de carga
        self._client_nodes = []  # Cache para nodos de cliente

    def get_node_letters(self, count):
        """
        Genera identificadores de nodos usando letras.
        Para los primeros 26 nodos usa A-Z
        Después usa AA, AB, AC, ..., BA, BB, etc.
        """
        if count <= 0:
            return []
            
        letters = []
        # Primero las letras simples A-Z
        alphabet = list(string.ascii_uppercase)
        
        # Añadir primero las letras simples
        letters.extend(alphabet[:min(count, 26)])
        
        if count <= 26:
            return letters
            
        # Si necesitamos más de 26, empezar con combinaciones AA, AB, etc.
        remaining = count - 26
        current_first = 0  # Índice para la primera letra
        current_second = 0  # Índice para la segunda letra
        
        while len(letters) < count:
            new_name = alphabet[current_first] + alphabet[current_second]
            letters.append(new_name)
            
            current_second += 1
            if current_second >= 26:
                current_second = 0
                current_first += 1
                if current_first >= 26:
                    # Si necesitáramos más, podríamos añadir una tercera letra aquí
                    break
                    
        return letters[:count]

    def initialize_network(self, num_nodes, num_edges=None):
        """
        Inicializa la red con la distribución correcta de nodos y sus tipos.
        """
        # Validación de entrada
        if num_nodes < 10 or num_nodes > 150:
            raise ValueError("El número de nodos debe estar entre 10 y 150")
            
        # Reiniciar todas las estructuras
        self.graph = Graph()
        self.node_types.clear()
        self.path_cache.clear()
        self._storage_nodes.clear()
        self._charging_nodes.clear()
        self._client_nodes.clear()
        
        if num_edges is None:
            num_edges = max(num_nodes - 1, int(num_nodes * 1.5))
        
        # Validar cantidad de aristas
        min_edges = num_nodes - 1
        max_edges = (num_nodes * (num_nodes - 1)) // 2
        if num_edges < min_edges:
            raise ValueError(f"El número de aristas debe ser al menos {min_edges} para garantizar conectividad")
        if num_edges > max_edges:
            raise ValueError(f"El número máximo de aristas posible es {max_edges}")
            
        num_edges = max(min_edges, min(num_edges, max_edges))

        # Calcular cantidad de cada tipo de nodo garantizando distribución exacta
        # 20% almacenamiento, 20% recarga, 60% cliente
        storage_nodes = max(1, int(num_nodes * 0.2))
        charging_nodes = max(1, int(num_nodes * 0.2))
        client_nodes = num_nodes - storage_nodes - charging_nodes
        
        # Ajustar para garantizar distribución exacta
        # Si hay residuo, asignarlo a clientes (mayor porcentaje)
        total_assigned = storage_nodes + charging_nodes + client_nodes
        if total_assigned != num_nodes:
            client_nodes += (num_nodes - total_assigned)
        
        # Verificar que tenemos al menos 1 de cada tipo
        if storage_nodes < 1 or charging_nodes < 1 or client_nodes < 1:
            # Si no hay suficientes nodos, ajustar proporciones
            if num_nodes < 5:
                storage_nodes = 1
                charging_nodes = 1
                client_nodes = num_nodes - 2
            else:
                # Recalcular con distribución mínima garantizada
                storage_nodes = max(1, int(num_nodes * 0.2))
                charging_nodes = max(1, int(num_nodes * 0.2))
                client_nodes = num_nodes - storage_nodes - charging_nodes
        
        print(f"📊 Distribución de nodos garantizada:")
        print(f"   📦 Almacenamiento: {storage_nodes} ({storage_nodes/num_nodes*100:.1f}%)")
        print(f"   🔋 Recarga: {charging_nodes} ({charging_nodes/num_nodes*100:.1f}%)")
        print(f"   👤 Cliente: {client_nodes} ({client_nodes/num_nodes*100:.1f}%)")

        # Crear todos los nodos primero
        for i in range(storage_nodes):
            node_id = f"S{i+1}"
            self.graph.add_vertex(node_id)
            self._storage_nodes.append(node_id)
            self.node_types[node_id] = "storage"

        for i in range(charging_nodes):
            node_id = f"C{i+1}"
            self.graph.add_vertex(node_id)
            self._charging_nodes.append(node_id)
            self.node_types[node_id] = "charging"

        # Crear clientes
        client_types = ["Regular", "Premium", "VIP"]
        for i in range(client_nodes):
            node_id = f"T{i+1}"
            self.graph.add_vertex(node_id)
            self._client_nodes.append(node_id)
            self.node_types[node_id] = "client"
            
            client = Client(f"CLI{i+1}", f"Cliente {i+1}", random.choice(client_types))
            client.node_id = node_id
            self.clients.append(client)

        # Crear árbol de expansión mínimo inicial para garantizar conectividad
        all_nodes = self._storage_nodes + self._charging_nodes + self._client_nodes
        edges_added = set()
        
        # Calcular peso máximo basado en el tamaño de la red
        max_weight = min(5, max(2, self.DRONE_AUTONOMY // (num_nodes // 10)))
        
        # Conectar nodos secuencialmente primero (más eficiente que aleatorio)
        for i in range(len(all_nodes)-1):
            u, v = all_nodes[i], all_nodes[i+1]
            weight = random.randint(1, max_weight)
            self.graph.add_edge(u, v, weight)
            edges_added.add((min(u, v), max(u, v)))

        # Agregar aristas adicionales de manera más eficiente
        edges_to_add = num_edges - (len(all_nodes) - 1)
        potential_edges = [(u, v) for u in all_nodes for v in all_nodes 
                         if u < v and (u, v) not in edges_added]
        
        if edges_to_add > 0:
            random.shuffle(potential_edges)
            for u, v in potential_edges[:edges_to_add]:
                weight = random.randint(1, max_weight)
                self.graph.add_edge(u, v, weight)

        # Verificar conectividad final
        if not self.is_connected():
            raise ValueError("La red generada no está conectada. Por favor, intente nuevamente.")

        return self.graph

    def get_node_type(self, node_id):
        """Get the type of a node based on its ID prefix."""
        if node_id.startswith('S'):
            return "storage"
        elif node_id.startswith('C'):
            return "charging"
        elif node_id.startswith('T'):
            return "client"
        return "unknown"

    def is_connected(self):
        if not self.graph.vertices():
            return True
        
        start = self.graph.vertices()[0]
        visited = set(self.graph.bfs(start))
        return len(visited) == len(self.graph.vertices())

    def find_path_with_charging(self, start, end):
        """
        Encuentra una ruta entre dos nodos considerando la autonomía del dron y estaciones de carga.
        Si no hay ruta completa, devuelve el camino parcial más largo posible y la batería restante.
        Returns:
            dict: {
                'path': [...],
                'completed': bool,
                'battery_left': int,
                'reason': str,
                'partial_path': [...],
                'partial_battery_left': int,
                'full_path': [...],
                'full_battery_left': int
            }
        """
        if not (start in self.graph.vertices() and end in self.graph.vertices()):
            return {'path': [], 'completed': False, 'battery_left': None, 'reason': 'Nodos no válidos', 'partial_path': [], 'partial_battery_left': None, 'full_path': [], 'full_battery_left': None}

        cache_key = f"{start}-{end}"
        if cache_key in self.path_cache:
            return self.path_cache[cache_key]

        queue = deque([(start, [start], self.DRONE_AUTONOMY, 0)])
        visited = set()  # (nodo, batería_restante)
        best_path = None
        min_recharges = float('inf')
        longest_partial = ([], self.DRONE_AUTONOMY, 0)

        while queue:
            current, path, battery, num_recharges = queue.popleft()

            # Si llegamos al destino, actualizamos el mejor camino si tiene menos recargas
            if current == end:
                if num_recharges < min_recharges:
                    best_path = (path, battery, num_recharges)
                    min_recharges = num_recharges
                continue

            # Si ya encontramos un camino y este tiene más recargas, lo ignoramos
            if num_recharges >= min_recharges:
                continue

            # Guardar el camino parcial más largo
            if len(path) > len(longest_partial[0]):
                longest_partial = (path, battery, num_recharges)

            neighbors = self.graph.get_neighbors(current)
            if battery < self.DRONE_AUTONOMY * 0.3:
                neighbors = sorted(neighbors, key=lambda x: x.startswith('C'), reverse=True)

            for neighbor in neighbors:
                edge = self.graph.get_edge(current, neighbor)
                if edge:
                    edge_cost = edge.element()
                    new_battery = battery
                    new_recharges = num_recharges
                    if current.startswith('C') or neighbor.startswith('C'):
                        new_battery = self.DRONE_AUTONOMY
                        if not current.startswith('C'):
                            new_recharges += 1
                    else:
                        new_battery -= edge_cost
                    state = (neighbor, new_battery)
                    if new_battery >= 0 and state not in visited:
                        visited.add(state)
                        new_path = path + [neighbor]
                        queue.append((neighbor, new_path, new_battery, new_recharges))

        if best_path:
            result = {
                'path': best_path[0],
                'completed': True,
                'battery_left': best_path[1],
                'reason': '',
                'partial_path': best_path[0],
                'partial_battery_left': best_path[1],
                'full_path': best_path[0],
                'full_battery_left': best_path[1]
            }
            self.path_cache[cache_key] = result
            return result
        else:
            # Devolver el camino parcial más largo
            result = {
                'path': longest_partial[0],
                'completed': False,
                'battery_left': longest_partial[1],
                'reason': 'No se pudo completar la ruta con la autonomía disponible',
                'partial_path': longest_partial[0],
                'partial_battery_left': longest_partial[1],
                'full_path': [],
                'full_battery_left': None
            }
            self.path_cache[cache_key] = result
            return result

    def generate_orders(self, num_orders):
        """
        Genera órdenes aleatorias entre nodos de manera optimizada.
        Ahora prioriza la reutilización de rutas frecuentes si existen entre el origen y destino.
        """
        if not self.graph or not self.graph.vertices():
            raise ValueError("El grafo no está inicializado")
            
        orders = []
        client_dict = {client.node_id: client for client in self.clients}
        
        # Reiniciar contadores de frecuencia
        self.route_frequencies = {}
        self.routes = []
        
        for i in range(num_orders):
            try:
                # Seleccionar origen y destino
                origin = random.choice(self._storage_nodes)
                destination = random.choice(self._client_nodes)
                
                # Buscar si ya existe una ruta frecuente entre este origen y destino
                ruta_existente = None
                for route in self.routes:
                    if route.nodes[0] == origin and route.nodes[-1] == destination:
                        ruta_existente = route
                        break
                
                if ruta_existente:
                    path = ruta_existente.nodes
                    route_key = ' → '.join(path)
                    ruta_existente.increment_frequency()
                    route = ruta_existente
                    completed = True
                else:
                    # Encontrar una ruta viable nueva
                    result = self.find_path_with_charging(origin, destination)
                    path = result['path']
                    completed = result['completed']
                    if not path or not completed:
                        continue
                    route_key = ' → '.join(path)
                    route = Route(f"Route_{len(self.routes)+1}", path)
                    self.routes.append(route)
                
                # Actualizar frecuencia de la ruta
                if route_key in self.route_frequencies:
                    self.route_frequencies[route_key] += 1
                    route.frequency = self.route_frequencies[route_key]
                else:
                    self.route_frequencies[route_key] = 1
                    route.frequency = 1
                
                # Calcular el costo total
                total_cost = sum(self.graph.get_edge(path[j], path[j+1]).element() 
                               for j in range(len(path)-1))
                
                # Obtener cliente
                client = client_dict.get(destination)
                if not client:
                    continue
                
                # Crear la orden con todos los campos necesarios
                order = Order(
                    order_id=f"ORD_{i+1}",
                    origin=origin,
                    destination=destination,
                    client_id=client.client_id,
                    client_name=client.name,
                    priority=client.client_type
                )
                
                # Asignar ruta y costo
                order.assign_route(route)
                order.route_cost = total_cost
                
                # Registrar orden
                orders.append(order)
                client.add_order(order)
                
            except Exception as e:
                st.error(f"Error generando orden {i+1}: {str(e)}")
                continue
        
        if not orders:
            raise ValueError("No se pudo generar ninguna orden válida.")
        
        # Verificar que la suma de frecuencias es igual al número de órdenes
        total_freq = sum(self.route_frequencies.values())
        if total_freq != len(orders):
            st.warning(f"Error de consistencia: Total de frecuencias ({total_freq}) ≠ Número de órdenes ({len(orders)})")
            
        return orders

    def initialize_simulation(self, num_nodes, num_edges, num_orders):
        """
        Inicializa la simulación completa.
        
        Args:
            num_nodes: Número total de nodos
            num_edges: Número de aristas
            num_orders: Número de órdenes a generar
        """
        # Reiniciar todas las estructuras
        self.graph = None
        self.orders = []
        self.clients = []
        self.routes = []
        self.route_frequencies = {}
        self.node_types = {}  # Reiniciar tipos de nodos
        
        # Paso 1: Inicializar la red
        self.initialize_network(num_nodes, num_edges)
        
        if not self.graph or not self.graph.vertices():
            raise ValueError("No se pudo inicializar la red correctamente")
            
        # Paso 2: Generar órdenes
        self.orders = self.generate_orders(num_orders)
        
        return self.graph, self.orders, self.clients

    def get_routes(self):
        return self.routes

    def get_route_frequencies(self):
        return self.route_frequencies 