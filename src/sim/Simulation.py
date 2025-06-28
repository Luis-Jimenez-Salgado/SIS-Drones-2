class Simulation:
    def __init__(self, graph):
        self.graph = graph
        self.orders = []

    def initialize(self, num_nodes, num_orders):
        # Inicializar nodos
        for i in range(num_nodes):
            self.graph.add_edge(f'Node_{i}', f'Node_{(i+1) % num_nodes}')

        # Inicializar órdenes
        for j in range(num_orders):
            self.orders.append(f'Order_{j}')

        print(f'Initialized with {num_nodes} nodes and {num_orders} orders.')

    def run(self):
        # Ejecutar la simulación
        print('Running simulation...')
        for order in self.orders:
            # Simular procesamiento de cada orden
            print(f'Processing {order}')
        print('Simulation complete.')

    def generate_statistics(self):
        # Generar estadísticas de la simulación
        print('Generating statistics...')
        num_nodes = len(self.graph.adjacency_list)
        num_orders = len(self.orders)
        print(f'Total nodes: {num_nodes}')
        print(f'Total orders: {num_orders}')
        # Aquí se pueden agregar más estadísticas
        print('Statistics generation complete.') 