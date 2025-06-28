import datetime

class Order:
    def __init__(self, order_id, origin, destination, client_id=None, client_name=None, priority="Normal"):
        """
        Inicializa una orden de entrega.
        
        Args:
            order_id: ID único de la orden
            origin: Nodo de origen
            destination: Nodo de destino
            client_id: ID del cliente (opcional)
            client_name: Nombre del cliente (opcional)
            priority: Prioridad de la orden ("Alta", "Normal", "Baja")
        """
        self.order_id = order_id
        self.client_id = client_id if client_id else "SYSTEM"
        self.client_name = client_name if client_name else "Sistema"
        self.origin = origin
        self.destination = destination
        self.status = "Pendiente"
        self.priority = priority
        self.creation_date = datetime.datetime.now()
        self.delivery_date = None
        self.delivered_to = None
        self.route = None
        self.route_cost = 0
        self.origin_type = self._get_node_type(origin)
        self.destination_type = self._get_node_type(destination)

    def _get_node_type(self, node_id):
        """
        Determina el tipo de nodo basado en su ID.
        
        Args:
            node_id: ID del nodo
            
        Returns:
            str: Tipo de nodo ('Almacenamiento', 'Carga', 'Cliente')
        """
        if node_id.startswith('S'):
            return 'Almacenamiento'
        elif node_id.startswith('C'):
            return 'Carga'
        elif node_id.startswith('T'):
            return 'Cliente'
        return 'Desconocido'

    def assign_route(self, route):
        """
        Asigna una ruta a la orden.
        
        Args:
            route: Objeto Route a asignar
        """
        self.route = route

    def calculate_route_cost(self):
        """
        Calcula el costo total de la ruta sumando los pesos de las aristas.
        """
        if self.route and self.route.nodes:
            total_cost = 0
            nodes = self.route.nodes
            for i in range(len(nodes) - 1):
                # Aquí deberíamos obtener el peso de la arista entre nodes[i] y nodes[i+1]
                # Este método necesitará acceso al grafo para obtener los pesos
                edge_cost = 0  # Esto se debe reemplazar con el peso real de la arista
                total_cost += edge_cost
            self.route_cost = total_cost

    def complete_delivery(self):
        """
        Marca la orden como completada y registra la fecha de entrega.
        """
        self.status = "Completada"
        self.delivery_date = datetime.datetime.now()
        self.delivered_to = self.destination

    def to_dict(self):
        """
        Convierte la orden a un diccionario para serialización.
        
        Returns:
            dict: Diccionario con los datos de la orden
        """
        return {
            'ID': self.order_id,
            'ID_Cliente': self.client_id,
            'Cliente': self.client_name,
            'Origen': self.origin,
            'Tipo_Origen': self.origin_type,
            'Destino': self.destination,
            'Tipo_Destino': self.destination_type,
            'Estado': self.status,
            'Prioridad': self.priority,
            'Fecha_Creacion': self.creation_date.strftime("%Y-%m-%d %H:%M:%S") if self.creation_date else "NULL",
            'Fecha_Entrega': self.delivery_date.strftime("%Y-%m-%d %H:%M:%S") if self.delivery_date else "NULL",
            'Entregado_en': self.delivered_to if self.delivered_to else "NULL",
            'Costo_Total': self.route_cost
        }

    def __str__(self):
        return f"Order {self.order_id} - From: {self.origin} ({self.origin_type}) To: {self.destination} ({self.destination_type}), Status: {self.status}" 