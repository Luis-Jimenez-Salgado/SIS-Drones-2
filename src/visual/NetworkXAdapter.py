import networkx as nx
import matplotlib.pyplot as plt

class NetworkXAdapter:
    def __init__(self, graph):
        self.graph = graph
        self.nx_graph = nx.Graph()
        self.node_colors = {}
        self.highlighted_path = None
        self.node_positions = None  # Para mantener las posiciones consistentes

    def convert_to_networkx(self):
        self.nx_graph.clear()
        
        # Agregar nodos con sus tipos
        for vertex in self.graph.vertices():
            if vertex.startswith('S'):  # Storage nodes
                self.node_colors[vertex] = '#3498db'  # Azul
            elif vertex.startswith('C'):  # Charging nodes
                self.node_colors[vertex] = '#f1c40f'  # Amarillo
            elif vertex.startswith('T'):  # Target/Client nodes
                self.node_colors[vertex] = '#2ecc71'  # Verde
            self.nx_graph.add_node(vertex)
        
        # Agregar aristas con pesos
        for start in self.graph.vertices():
            for end in self.graph.get_neighbors(start):
                weight = self.graph.get_edge_weight(start, end)
                self.nx_graph.add_edge(start, end, weight=weight)

        # Calcular posiciones solo si no existen
        if self.node_positions is None:
            # Usar un layout determinista con seed fijo
            self.node_positions = nx.spring_layout(
                self.nx_graph,
                k=2.0,  # Aumentar la separación entre nodos
                iterations=50,
                seed=42  # Seed fijo para consistencia
            )

    def highlight_path(self, path):
        """
        Guarda una ruta para resaltarla en rojo en la próxima visualización.
        
        Args:
            path: Lista de nodos que forman la ruta
        """
        self.highlighted_path = path

    def clear_path(self):
        """
        Limpia la ruta resaltada.
        """
        self.highlighted_path = None

    def draw_graph(self):
        if not self.nx_graph:
            return None
            
        # Crear nueva figura
        plt.figure(figsize=(15, 10))
        
        # Dibujar aristas normales
        nx.draw_networkx_edges(self.nx_graph, self.node_positions,
                             edge_color='gray',
                             alpha=0.5,
                             width=1)
        
        # Dibujar aristas destacadas si hay una ruta seleccionada
        if self.highlighted_path:
            path_edges = list(zip(self.highlighted_path[:-1], self.highlighted_path[1:]))
            nx.draw_networkx_edges(self.nx_graph, self.node_positions,
                                 edgelist=path_edges,
                                 edge_color='red',
                                 width=2)
        
        # Dibujar nodos por tipo en orden específico
        for node_prefix in ['S', 'C', 'T']:  # Dibujar en orden: Storage, Charging, Targets
            nodes = [n for n in self.nx_graph.nodes() if n.startswith(node_prefix)]
            if nodes:
                nx.draw_networkx_nodes(self.nx_graph, self.node_positions,
                                     nodelist=nodes,
                                     node_color=[self.node_colors[n] for n in nodes],
                                     node_size=1000,
                                     edgecolors='white',
                                     linewidths=2)
        
        # Dibujar etiquetas de nodos
        nx.draw_networkx_labels(self.nx_graph, self.node_positions,
                              font_size=12,
                              font_weight='bold',
                              font_color='black')
        
        # Dibujar pesos de aristas
        edge_labels = nx.get_edge_attributes(self.nx_graph, 'weight')
        nx.draw_networkx_edge_labels(self.nx_graph, self.node_positions,
                                   edge_labels=edge_labels,
                                   font_size=8)
        
        plt.title("Red de Entrega de Drones", pad=20, fontsize=16)
        plt.axis('off')
        
        return plt.gcf() 