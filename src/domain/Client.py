class Client:
    def __init__(self, client_id, name, client_type, node_id=None):
        """
        Inicializa un cliente.
        
        Args:
            client_id: ID único del cliente (e.g., 'C1', 'C2', etc.)
            name: Nombre del cliente
            client_type: Tipo de cliente (e.g., 'Regular', 'Premium', etc.)
            node_id: ID del nodo asociado al cliente (opcional)
        """
        self.client_id = client_id
        self.name = name
        self.client_type = client_type
        self.node_id = node_id
        self.orders = []  # Lista de órdenes del cliente

    def add_order(self, order):
        """
        Agrega una orden al cliente.
        
        Args:
            order: Objeto Order a agregar
        """
        self.orders.append(order)

    def get_total_orders(self):
        """
        Obtiene el número total de órdenes del cliente.
        
        Returns:
            int: Número total de órdenes
        """
        return len(self.orders)

    def get_completed_orders(self):
        """
        Obtiene el número de órdenes completadas.
        
        Returns:
            int: Número de órdenes completadas
        """
        return len([order for order in self.orders if order.status == "Completada"])

    def get_pending_orders(self):
        """
        Obtiene el número de órdenes pendientes.
        
        Returns:
            int: Número de órdenes pendientes
        """
        return len([order for order in self.orders if order.status == "Pendiente"])

    def to_dict(self):
        """
        Convierte el cliente a un diccionario para serialización.
        
        Returns:
            dict: Diccionario con los datos del cliente
        """
        completed_orders = self.get_completed_orders()
        return {
            'ID': self.client_id,
            'Nombre': self.name,
            'Tipo': self.client_type,
            'Total_Ordenes': self.get_total_orders(),
            'Ordenes_Completadas': completed_orders,
            'Ordenes_Pendientes': self.get_pending_orders()
        }

    def __str__(self):
        return f"Client {self.client_id} - {self.name} ({self.client_type})" 