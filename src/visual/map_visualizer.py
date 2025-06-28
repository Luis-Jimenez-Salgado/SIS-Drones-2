import folium
import random
import math
from typing import List, Dict, Tuple, Optional
import streamlit as st

class MapVisualizer:
    def __init__(self):
        """
        Inicializa el visualizador de mapas con coordenadas de Temuco, Chile.
        """
        # Coordenadas exactas de Temuco, Chile
        self.temuco_center = [-38.7385268, -72.5900592]
        self.map = None
        self.node_positions = {}
        self.normal_edges = []  # Lista para almacenar las rutas normales
        self.mst_mode = False   # Flag para indicar si estamos en modo MST
        
        # Mejores colores para los nodos
        self.node_colors = {
            'storage': 'darkblue',     # Azul oscuro para almacenes
            'charging': 'orange',      # Naranja para puntos de carga
            'client': 'darkgreen'      # Verde oscuro para clientes
        }
        
        # Mejores iconos para los nodos
        self.node_icons = {
            'storage': '🏭',           # Icono de fábrica para almacenes
            'charging': '⚡',          # Icono de rayo para puntos de carga
            'client': '🏠'             # Icono de casa para clientes
        }
        
        # Iconos HTML personalizados para mejor visualización
        self.node_html_icons = {
            'storage': '🏭',           # Emoji de fábrica
            'charging': '⚡',          # Emoji de rayo
            'client': '🏠'             # Emoji de casa
        }
        
        # Diseños HTML personalizados para cada tipo de nodo
        self.node_html_designs = {
            'storage': {
                'icon': '🏭',
                'bg_color': '#1E3A8A',  # Azul oscuro
                'border_color': '#3B82F6',
                'label': 'ALMACÉN'
            },
            'charging': {
                'icon': '⚡',
                'bg_color': '#F59E0B',  # Naranja
                'border_color': '#FBBF24',
                'label': 'RECARGA'
            },
            'client': {
                'icon': '🏠',
                'bg_color': '#059669',  # Verde
                'border_color': '#10B981',
                'label': 'CLIENTE'
            }
        }
        
        # Colores para las rutas
        self.route_colors = {
            'normal': '#FF4444',       # Rojo brillante para rutas normales
            'charging': '#FF8800',     # Naranja para segmentos con recarga
            'mst': '#9932CC',          # Púrpura para MST
            'animation': '#FF0000'     # Rojo para animación
        }
    
    def generate_node_positions(self, nodes: List[str], graph_type: str = 'random') -> Dict[str, Tuple[float, float]]:
        """
        Genera posiciones geográficas para los nodos.
        
        Args:
            nodes: Lista de nodos
            graph_type: Tipo de grafo ('random', 'grid', 'circular')
            
        Returns:
            Diccionario con posiciones (lat, lon) para cada nodo
        """
        positions = {}
        
        if graph_type == 'random':
            # Coordenadas exactas de Temuco, Chile
            base_lat, base_lon = -38.7385268, -72.5900592
            
            for i, node in enumerate(nodes):
                # Generar posiciones aleatorias más cercanas al centro
                lat_offset = random.uniform(-0.01, 0.01)  # ~1km en cada dirección
                lon_offset = random.uniform(-0.01, 0.01)
                
                lat = base_lat + lat_offset
                lon = base_lon + lon_offset
                
                positions[node] = (lat, lon)
        
        elif graph_type == 'grid':
            # Organizar en una cuadrícula
            n = len(nodes)
            cols = int(n ** 0.5) + 1
            rows = (n + cols - 1) // cols
            
            base_lat, base_lon = -38.7385268, -72.5900592
            lat_step = 0.02
            lon_step = 0.02
            
            for i, node in enumerate(nodes):
                row = i // cols
                col = i % cols
                lat = base_lat + row * lat_step
                lon = base_lon + col * lon_step
                positions[node] = (lat, lon)
        
        elif graph_type == 'circular':
            # Organizar en círculo
            base_lat, base_lon = -38.7385268, -72.5900592
            radius = 0.03  # Radio del círculo
            
            for i, node in enumerate(nodes):
                angle = 2 * 3.14159 * i / len(nodes)
                lat = base_lat + radius * (1 - abs(angle - 3.14159) / 3.14159)
                lon = base_lon + radius * (angle - 3.14159) / 3.14159
                positions[node] = (lat, lon)
        
        return positions
    
    def create_map(self, graph, node_positions: Optional[Dict[str, Tuple[float, float]]] = None) -> folium.Map:
        """
        Crea un mapa interactivo con los nodos y conexiones.
        
        Args:
            graph: Grafo del sistema
            node_positions: Posiciones de los nodos (opcional)
            
        Returns:
            Mapa de Folium
        """
        if not graph:
            return None
        
        nodes = list(graph.vertices())
        
        # Usar las posiciones proporcionadas o generar nuevas
        if node_positions is not None:
            self.node_positions = node_positions
        elif not hasattr(self, 'node_positions') or not self.node_positions:
            self.node_positions = self.generate_node_positions(nodes, 'random')
        
        # Centro fijo y zoom adecuado
        center_lat, center_lon = -38.7385268, -72.5900592
        self.map = folium.Map(
            location=[center_lat, center_lon],
            zoom_start=15,
            tiles='OpenStreetMap'
        )
        
        # Reinicializar estado
        self.normal_edges = []
        self.mst_mode = False
        
        # Agregar etiqueta de algoritmo
        self._add_algorithm_label()
        
        # Agregar nodos y conexiones
        self._add_nodes_to_map(graph)
        self._add_edges_to_map(graph)
        
        return self.map
    
    def _add_algorithm_label(self):
        """Agrega una etiqueta que indica el uso del algoritmo de Dijkstra."""
        if self.map:
            # Crear HTML para la etiqueta
            algorithm_html = """
            <div style="position: fixed; 
                        top: 10px; 
                        right: 10px; 
                        background-color: rgba(0, 0, 0, 0.8); 
                        color: white; 
                        padding: 10px; 
                        border-radius: 5px; 
                        font-family: Arial, sans-serif; 
                        font-size: 12px; 
                        z-index: 1000;
                        border: 2px solid #FF4444;">
                <strong>🚁 Algoritmo de Dijkstra</strong><br>
                Optimización de rutas para drones
            </div>
            """
            
            # Agregar la etiqueta al mapa
            self.map.get_root().html.add_child(folium.Element(algorithm_html))
    
    def _add_nodes_to_map(self, graph):
        """Agrega los nodos al mapa con iconos y colores mejorados."""
        for node in graph.vertices():
            if node not in self.node_positions:
                continue
                
            lat, lon = self.node_positions[node]
            node_type = self._get_node_type(node)
            
            # Crear texto del popup con información mejorada del nodo
            popup_text = f"""
            <div style="font-family: Arial, sans-serif; min-width: 200px;">
                <h4 style="color: {self.node_colors[node_type]}; margin: 0 0 10px 0;">
                    {self.node_html_icons[node_type]} {node}
                </h4>
                <p style="margin: 5px 0;"><strong>Tipo:</strong> {node_type.title()}</p>
                <p style="margin: 5px 0;"><strong>Coordenadas:</strong><br>
                {lat:.4f}, {lon:.4f}</p>
                <hr style="margin: 10px 0;">
                <p style="margin: 5px 0; font-size: 11px; color: #666;">
                    🚁 Punto de la red logística
                </p>
            </div>
            """
            
            # Crear icono HTML personalizado
            design = self.node_html_designs[node_type]
            icon_html = f"""
            <div style="
                background: linear-gradient(135deg, {design['bg_color']}, {design['border_color']});
                border: 3px solid white;
                border-radius: 50%;
                width: 45px;
                height: 45px;
                display: flex;
                flex-direction: column;
                align-items: center;
                justify-content: center;
                font-size: 18px;
                box-shadow: 0 4px 8px rgba(0,0,0,0.3);
                color: white;
                font-weight: bold;
                text-shadow: 1px 1px 2px rgba(0,0,0,0.5);
            ">
                <div style="font-size: 20px; margin-bottom: 2px;">{design['icon']}</div>
                <div style="font-size: 8px; font-weight: bold; letter-spacing: 0.5px;">{design['label']}</div>
            </div>
            """
            
            # Agregar marcador con icono HTML personalizado
            folium.Marker(
                location=[lat, lon],
                popup=folium.Popup(popup_text, max_width=250),
                icon=folium.DivIcon(
                    html=icon_html,
                    icon_size=(45, 45),
                    icon_anchor=(22, 22)
                ),
                tooltip=f"{design['icon']} {node} ({design['label']})"
            ).add_to(self.map)
    
    def _add_edges_to_map(self, graph):
        """Agrega las conexiones entre nodos al mapa con mejor visualización."""
        self.normal_edges = []  # Limpiar lista de rutas normales
        
        for edge in graph.edges():
            u, v = edge.endpoints()
            if u in self.node_positions and v in self.node_positions:
                lat1, lon1 = self.node_positions[u]
                lat2, lon2 = self.node_positions[v]
                
                # Obtener el peso de la arista
                edge_weight = edge.element()
                
                # Color azul para todas las aristas
                color = '#1976D2'  # Azul Google/Material
                weight_normalized = 3  # Grosor medio
                
                # Crear tooltip con información del peso
                tooltip_text = f"{u} ↔ {v}<br><b>Peso:</b> {edge_weight}"
                
                # Crear la línea y almacenar referencia
                line = folium.PolyLine(
                    locations=[[lat1, lon1], [lat2, lon2]],
                    weight=weight_normalized,
                    color=color,
                    opacity=0.8,
                    popup=f"<b>Conexión:</b> {u} ↔ {v}<br><b>Peso:</b> {edge_weight}",
                    tooltip=tooltip_text
                )
                
                line.add_to(self.map)
                self.normal_edges.append(line)  # Almacenar referencia
    
    def highlight_path(self, path: List[str], color: str = None, weight: int = 6):
        """
        Resalta una ruta específica en el mapa con mejor visualización.
        
        Args:
            path: Lista de nodos que forman la ruta
            color: Color de la ruta (opcional)
            weight: Grosor de la línea
        """
        if not self.map or not path:
            return
        
        # Usar color por defecto si no se especifica
        if color is None:
            color = self.route_colors['normal']
        
        # Crear coordenadas de la ruta
        route_coords = []
        for node in path:
            if node in self.node_positions:
                route_coords.append(self.node_positions[node])
        
        if len(route_coords) < 2:
            return
        
        # Agregar ruta al mapa con mejor estilo
        folium.PolyLine(
            locations=route_coords,
            weight=weight,
            color=color,
            opacity=0.9,
            popup=f"<b>Ruta Dijkstra:</b><br>{' → '.join(path)}",
            tooltip="Ruta optimizada con Dijkstra"
        ).add_to(self.map)
        
        # Agregar flechas de dirección en la ruta
        for i in range(len(route_coords) - 1):
            # Calcular punto medio del segmento
            mid_lat = (route_coords[i][0] + route_coords[i+1][0]) / 2
            mid_lon = (route_coords[i][1] + route_coords[i+1][1]) / 2
            
            # Agregar marcador de flecha
            folium.RegularPolygonMarker(
                location=[mid_lat, mid_lon],
                number_of_sides=3,
                radius=3,
                color=color,
                fill=True,
                fill_color=color,
                fill_opacity=0.8,
                popup=f"Segmento: {path[i]} → {path[i+1]}"
            ).add_to(self.map)
    
    def hide_normal_edges(self):
        """Oculta las rutas normales del mapa."""
        if self.map and self.normal_edges:
            for edge in self.normal_edges:
                if edge in self.map._children.values():
                    self.map._children.pop(edge.get_name(), None)
            self.mst_mode = True
    
    def show_normal_edges(self):
        """Muestra las rutas normales del mapa."""
        if self.map and self.normal_edges:
            for edge in self.normal_edges:
                edge.add_to(self.map)
            self.mst_mode = False
    
    def clear_mst_info(self):
        """Limpia la información del MST del mapa."""
        if self.map:
            # Buscar y eliminar elementos HTML del MST
            for child_name, child in list(self.map._children.items()):
                if hasattr(child, '_name') and 'mst' in str(child._name).lower():
                    self.map._children.pop(child_name, None)
    
    def show_mst(self, graph, color: str = None, weight: int = 6):
        """
        Muestra el árbol de expansión mínima en el mapa con mejor visualización.
        Oculta las rutas normales cuando se muestra el MST.
        
        Args:
            graph: Grafo del sistema
            color: Color del MST (opcional)
            weight: Grosor de las líneas
        """
        if not self.map:
            return
        
        # Usar color por defecto si no se especifica
        if color is None:
            color = self.route_colors['mst']
        
        try:
            # Ocultar rutas normales primero
            self.hide_normal_edges()
            
            # Limpiar información previa del MST
            self.clear_mst_info()
            
            # Obtener MST usando Kruskal
            mst_edges = graph.kruskal_mst()
            
            total_cost = 0
            mst_nodes = set()
            
            for u, v, weight_value in mst_edges:
                if u in self.node_positions and v in self.node_positions:
                    lat1, lon1 = self.node_positions[u]
                    lat2, lon2 = self.node_positions[v]
                    
                    # Agregar nodos al conjunto
                    mst_nodes.add(u)
                    mst_nodes.add(v)
                    total_cost += weight_value
                    
                    # Crear línea discontinua para MST con mejor estilo y más gruesa
                    folium.PolyLine(
                        locations=[[lat1, lon1], [lat2, lon2]],
                        weight=weight,
                        color=color,
                        opacity=0.9,
                        dash_array='20, 15',  # Línea discontinua más pronunciada
                        popup=f"<b>🌲 MST Kruskal:</b><br>{u} → {v}<br><b>Peso:</b> {weight_value}",
                        tooltip=f"MST: {u} → {v}"
                    ).add_to(self.map)
            
            # Agregar información de cobertura mínima al mapa con mejor estilo
            coverage_info = f"""
            <div style="position: fixed; 
                        bottom: 10px; 
                        left: 10px; 
                        background-color: rgba(153, 50, 204, 0.9); 
                        color: white; 
                        padding: 15px; 
                        border-radius: 8px; 
                        box-shadow: 0 4px 8px rgba(0,0,0,0.3);
                        font-family: Arial, sans-serif; 
                        font-size: 12px; 
                        z-index: 1000;
                        border: 2px solid white;">
                <h4 style="margin: 0 0 10px 0;">🌲 Árbol de Expansión Mínima (Kruskal)</h4>
                <p style="margin: 5px 0;"><strong>Nodos conectados:</strong> {len(mst_nodes)}</p>
                <p style="margin: 5px 0;"><strong>Conexiones:</strong> {len(mst_edges)}</p>
                <p style="margin: 5px 0;"><strong>Costo total:</strong> {total_cost}</p>
                <p style="margin: 5px 0;"><strong>Cobertura:</strong> {len(mst_nodes)}/{len(graph.vertices())} nodos</p>
            </div>
            """
            
            # Agregar al mapa
            self.map.get_root().html.add_child(folium.Element(coverage_info))
            
            return {
                'edges': mst_edges,
                'nodes': list(mst_nodes),
                'total_cost': total_cost,
                'coverage_percentage': (len(mst_nodes) / len(graph.vertices())) * 100
            }
            
        except Exception as e:
            st.error(f"❌ Error al calcular MST: {str(e)}")
            return None
    
    def add_route_summary(self, path: List[str], total_cost: float, battery_usage: float):
        """
        Agrega un resumen de la ruta al mapa con mejor estilo.
        
        Args:
            path: Ruta calculada
            total_cost: Costo total de la ruta
            battery_usage: Uso de batería
        """
        if not self.map or not path:
            return
        
        # Crear HTML para el resumen con mejor estilo
        summary_html = f"""
        <div style="position: fixed; 
                    bottom: 10px; 
                    right: 10px; 
                    background-color: rgba(255, 68, 68, 0.9); 
                    color: white; 
                    padding: 15px; 
                    border-radius: 8px; 
                    box-shadow: 0 4px 8px rgba(0,0,0,0.3);
                    font-family: Arial, sans-serif; 
                    font-size: 12px; 
                    z-index: 1000;
                    border: 2px solid white;
                    max-width: 300px;">
            <h4 style="margin: 0 0 10px 0;">📊 Resumen de Ruta Dijkstra</h4>
            <p style="margin: 5px 0;"><strong>Ruta:</strong><br>{' → '.join(path)}</p>
            <p style="margin: 5px 0;"><strong>Costo Total:</strong> {total_cost:.2f}</p>
            <p style="margin: 5px 0;"><strong>Uso de Batería:</strong> {battery_usage:.1f}%</p>
            <p style="margin: 5px 0;"><strong>Nodos:</strong> {len(path)}</p>
            <p style="margin: 5px 0;"><strong>Autonomía:</strong> 50 unidades</p>
        </div>
        """
        
        # Agregar al mapa
        self.map.get_root().html.add_child(folium.Element(summary_html))
    
    def _get_node_type(self, node: str) -> str:
        """Determina el tipo de nodo basado en su ID."""
        if node.startswith('S'):
            return 'storage'
        elif node.startswith('C'):
            return 'charging'
        elif node.startswith('T'):
            return 'client'
        return 'unknown'
    
    def save_map(self, filename: str = "mapa_drones.html"):
        """
        Guarda el mapa como archivo HTML.
        
        Args:
            filename: Nombre del archivo
        """
        if self.map:
            self.map.save(filename)
            return filename
        return None
    
    def get_map_html(self) -> str:
        """
        Obtiene el HTML del mapa como string.
        
        Returns:
            HTML del mapa
        """
        if self.map:
            return self.map._repr_html_()
        return ""
    
    def add_charging_stations_highlight(self, charging_nodes: List[str]):
        """
        Resalta las estaciones de recarga en el mapa.
        
        Args:
            charging_nodes: Lista de nodos de recarga
        """
        if not self.map:
            return
        
        for node in charging_nodes:
            if node in self.node_positions:
                lat, lon = self.node_positions[node]
                
                # Agregar círculo de resalte
                folium.CircleMarker(
                    location=[lat, lon],
                    radius=15,
                    color='orange',
                    fill=True,
                    fill_color='orange',
                    fill_opacity=0.3,
                    weight=2,
                    popup=f"⚡ Estación de Recarga: {node}",
                    tooltip="Estación de recarga activa"
                ).add_to(self.map)
    
    def add_autonomy_radius(self, center_node: str, autonomy: float, color: str = 'orange'):
        """
        Agrega un círculo de autonomía alrededor de un nodo.
        
        Args:
            center_node: Nodo central
            autonomy: Radio de autonomía
            color: Color del círculo
        """
        if not self.map or center_node not in self.node_positions:
            return
        
        lat, lon = self.node_positions[center_node]
        
        # Convertir autonomía a grados (aproximadamente)
        autonomy_degrees = autonomy * 0.001  # Factor de conversión
        
        folium.Circle(
            location=[lat, lon],
            radius=autonomy_degrees * 111000,  # Convertir a metros
            color=color,
            fill=True,
            fill_color=color,
            fill_opacity=0.1,
            weight=2,
            popup=f"🚁 Radio de autonomía: {autonomy} unidades",
            tooltip="Radio de autonomía del dron"
        ).add_to(self.map)
    
    def animate_route(self, path: List[str], color: str = None, weight: int = 6, 
                     animation_duration: int = 2000):
        """
        Anima una ruta en el mapa con mejor visualización.
        
        Args:
            path: Lista de nodos que forman la ruta
            color: Color de la ruta (opcional)
            weight: Grosor de la línea
            animation_duration: Duración de la animación en ms
        """
        if not self.map or not path:
            return
        
        # Usar color por defecto si no se especifica
        if color is None:
            color = self.route_colors['animation']
        
        # Crear coordenadas de la ruta
        route_coords = []
        for node in path:
            if node in self.node_positions:
                route_coords.append(self.node_positions[node])
        
        if len(route_coords) < 2:
            return
        
        # Agregar ruta animada al mapa
        folium.PolyLine(
            locations=route_coords,
            weight=weight,
            color=color,
            opacity=0.9,
            popup=f"<b>🎬 Ruta Animada:</b><br>{' → '.join(path)}",
            tooltip="Ruta en animación"
        ).add_to(self.map)
        
        # Agregar marcador de dron que se mueve
        for i, (lat, lon) in enumerate(route_coords):
            # Crear marcador de dron
            folium.Marker(
                location=[lat, lon],
                icon=folium.Icon(
                    color='red',
                    icon='plane',
                    prefix='fa'
                ),
                popup=f"🚁 Dron en {path[i]}",
                tooltip=f"Dron en {path[i]}"
        ).add_to(self.map) 
        
        # Agregar información de animación
        animation_info = f"""
        <div style="position: fixed; 
                    top: 50px; 
                    right: 10px; 
                    background-color: rgba(255, 0, 0, 0.9); 
                    color: white; 
                    padding: 10px; 
                    border-radius: 5px; 
                    box-shadow: 0 2px 4px rgba(0,0,0,0.3);
                    font-family: Arial, sans-serif; 
                    font-size: 11px; 
                    z-index: 1000;">
            <strong>🎬 Animación de Ruta</strong><br>
            Duración: {animation_duration}ms
        </div>
        """
        
        # Agregar al mapa
        self.map.get_root().html.add_child(folium.Element(animation_info))
    
    def clear_map(self, graph):
        """
        Limpia el mapa y restaura las rutas normales.
        
        Args:
            graph: Grafo del sistema
        """
        if self.map:
            # Limpiar información del MST
            self.clear_mst_info()
            
            # Restaurar rutas normales
            self.show_normal_edges()
            
            # Recrear el mapa base
            self.create_map(graph, self.node_positions) 