import networkx as nx
import matplotlib.pyplot as plt

class AVLVisualizer:
    def __init__(self, tree=None):
        self.G = nx.Graph()
        self.pos = {}
        self.labels = {}
        self.tree = tree

    def _create_node_label(self, node):
        """
        Creates node label in format 'A → B → C\nFreq: X'
        """
        if not node or not node.key:
            return ""
        
        # Route is stored in the nodes attribute of Route object (node.key)
        route_nodes = node.key.nodes
        if not route_nodes:
            return ""
        
        # Create route string: A → B → C
        route = " → ".join(str(n) for n in route_nodes)
        
        # Get frequency
        frequency = getattr(node.key, 'frequency', 0)
        
        # Truncate long routes to prevent overlapping
        if len(route) > 30:
            # Show first and last nodes with ellipsis
            nodes_list = [str(n) for n in route_nodes]
            if len(nodes_list) > 3:
                route = f"{nodes_list[0]} → ... → {nodes_list[-1]}"
            else:
                route = route[:30] + "..."
        
        # Return formatted label: A → B → C\nFreq: X
        return f"{route}\nFreq: {frequency}"

    def visualize(self):
        """
        Wrapper method that calls draw_tree for compatibility.
        """
        return self.draw_tree()

    def draw_tree(self):
        """
        Visualizes the AVL tree using networkx.
        
        Returns:
            matplotlib.figure.Figure: The generated figure
        """
        self.G.clear()
        self.pos.clear()
        self.labels.clear()
        
        if not self.tree:
            return plt.figure()  # Return empty figure if no tree
            
        def _build_graph(node, x=0, y=0, layer=1):
            if not node:
                return
                
            # Create current node
            node_id = id(node)
            self.G.add_node(node_id)
            self.pos[node_id] = (x, y)
            self.labels[node_id] = self._create_node_label(node)
        
            # Process left child
            if node.left:
                left_id = id(node.left)
                self.G.add_edge(node_id, left_id)
                _build_graph(node.left, x-2/layer, y-1, layer+1)
                
            # Process right child
            if node.right:
                right_id = id(node.right)
                self.G.add_edge(node_id, right_id)
                _build_graph(node.right, x+2/layer, y-1, layer+1)
        
        _build_graph(self.tree.root if self.tree else None)
        
        if not self.G.nodes():
            return plt.figure()  # Return empty figure if no nodes
            
        # Create figure with dark theme
        plt.style.use('dark_background')
        fig = plt.figure(figsize=(15, 10))
        fig.patch.set_facecolor('#0E1117')
        ax = plt.gca()
        ax.set_facecolor('#0E1117')
        
        # Draw nodes with dark theme colors
        nx.draw_networkx_nodes(self.G, self.pos,
                             node_color='#262730',  # Dark node color
                             node_size=3000,
                             node_shape='o',
                             edgecolors='#4B4B4B',  # Dark border color
                             linewidths=2)
        
        # Draw edges with dark theme colors
        nx.draw_networkx_edges(self.G, self.pos,
                             edge_color='#4B4B4B',  # Dark edge color
                             width=1,
                             arrows=True,
                             arrowsize=20)
        
        # Draw labels with smaller font size for better readability
        nx.draw_networkx_labels(self.G, self.pos,
                              self.labels,
                              font_size=8,  # Reduced from 10 to 8
                              font_weight='bold',
                              font_color='#FAFAFA')  # Light text color
        
        plt.title("Árbol AVL de Frecuencias de Rutas - Estructura Balanceada", 
                 pad=20, fontsize=16, color='#FAFAFA')
        plt.axis('off')
        
        return fig 