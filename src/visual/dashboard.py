import streamlit as st
import matplotlib.pyplot as plt
import networkx as nx
from src.model.Graph import Graph
from src.sim.SimulationInitializer import SimulationInitializer
from src.visual.NetworkXAdapter import NetworkXAdapter
from src.visual.AVLVisualizer import AVLVisualizer
from src.tda.AVL import AVL
from src.domain.Route import Route
from src.domain.Order import Order
import pandas as pd
import json
from src.model.algorithms import DijkstraAlgorithm
from src.shared_data import shared_data_manager
from datetime import datetime

# Must be the first Streamlit command
st.set_page_config(
    page_title="Sistema de Entrega con Drones",
    page_icon="🚁",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Apply custom CSS for dark theme
st.markdown("""
    <style>
    /* Fondo principal */
    .stApp {
        background-color: #0E1117;
        color: #FAFAFA;
    }
    
    /* Estilo para botones */
    .stButton>button {
        background-color: #262730;
        color: #FAFAFA;
        border: 1px solid #4B4B4B;
        border-radius: 4px;
        padding: 0.5rem 1rem;
        transition: all 0.2s;
    }
    .stButton>button:hover {
        border-color: #6B6B6B;
        background-color: #363840;
    }
    
    /* Estilo para sliders */
    .stSlider>div>div {
        background-color: #262730;
    }
    .stSlider>div>div>div>div {
        background-color: #4B4B4B;
    }
    
    /* Estilo para tabs */
    .stTabs>div>div>div {
        background-color: #262730;
        color: #FAFAFA;
        border-radius: 4px;
    }
    .stTabs>div>div>div:hover {
        background-color: #363840;
    }
    
    /* Estilo para selectbox */
    .stSelectbox>div>div {
        background-color: #262730;
        color: #FAFAFA;
        border: 1px solid #4B4B4B;
    }
    
    /* Estilo para expander */
    .streamlit-expanderHeader {
        background-color: #262730;
        color: #FAFAFA;
    }
    
    /* Estilo para dataframe */
    .stDataFrame {
        background-color: #262730;
    }
    .stDataFrame table {
        background-color: #262730;
    }
    .stDataFrame th {
        background-color: #363840;
        color: #FAFAFA;
    }
    .stDataFrame td {
        color: #FAFAFA;
    }
    
    /* Estilo para métricas */
    .stMetric>div {
        background-color: #262730;
        border: 1px solid #4B4B4B;
        border-radius: 4px;
        padding: 1rem;
    }
    
    /* Estilo para widgets en general */
    .stWidgetLabel {
        color: #FAFAFA !important;
    }
    
    /* Estilo para tooltips */
    .stTooltipIcon {
        color: #FAFAFA;
    }
    
    /* Estilo para markdown */
    .stMarkdown {
        color: #FAFAFA;
    }
    </style>
    """, unsafe_allow_html=True)

# Intentar importar plotly, si no está disponible usar alternativa más simple
try:
    import plotly.express as px
    HAS_PLOTLY = True
except ImportError:
    HAS_PLOTLY = False

def update_shared_data():
    """Actualizar datos compartidos con la API"""
    try:
        session_data = {
            'graph': st.session_state.get('graph'),
            'orders': st.session_state.get('orders', []),
            'clients': st.session_state.get('clients', []),
            'routes': st.session_state.get('routes', []),
            'node_visits': st.session_state.get('node_visits', {}),
            'route_counter': st.session_state.get('route_counter', 0),
            'order_counter': st.session_state.get('order_counter', 0)
        }
        
        # Debug: mostrar información de los datos
        print(f"🔄 Actualizando datos compartidos:")
        print(f"   - Grafo: {'Sí' if session_data['graph'] else 'No'}")
        print(f"   - Clientes: {len(session_data['clients'])}")
        print(f"   - Órdenes: {len(session_data['orders'])}")
        print(f"   - Rutas: {len(session_data['routes'])}")
        print(f"   - Inicializado: {session_data['graph'] is not None}")
        
        shared_data_manager.update_from_dashboard(session_data)
        print("✅ Datos compartidos actualizados exitosamente")
        
    except Exception as e:
        print(f"❌ Error actualizando datos compartidos: {str(e)}")
        st.error(f"Error actualizando datos compartidos: {str(e)}")

def run_simulation_tab():
    st.header('⚙️ Inicializar Simulación')
    
    col1, col2 = st.columns([3, 1])
    
    with col1:
        # Sliders según especificación
        num_nodes = st.slider('Número de Nodos', 10, 150, 15, help="Elegir entre 10 y 150 nodos")
        num_edges = st.slider('Número de Aristas', 10, 300, 20, help="Elegir entre 10 y 300 aristas")
        num_orders = st.slider('Número de Órdenes', 10, 300, 14, help="Elegir entre 10 y 300 órdenes")
        
        # Validaciones según especificación
        min_edges_required = num_nodes - 1
        if num_edges < min_edges_required:
            st.error(f'❌ El número de aristas debe ser al menos {min_edges_required} para garantizar conectividad')
            return
        
        if num_nodes > 150:
            st.error('❌ El número de nodos no debe superar 150')
            return
        
        # Campo informativo con distribución de nodos según especificación
        st.subheader('📊 Distribución de Nodos')
        
        # Calcular distribución exacta
        storage_nodes = max(1, int(num_nodes * 0.2))
        charging_nodes = max(1, int(num_nodes * 0.2))
        client_nodes = num_nodes - storage_nodes - charging_nodes
        
        # Mostrar información detallada
        col_info1, col_info2, col_info3 = st.columns(3)
        
        with col_info1:
            st.metric(
                label="📦 Almacenamiento",
                value=storage_nodes,
                delta=f"{int((storage_nodes/num_nodes)*100)}%"
            )
        
        with col_info2:
            st.metric(
                label="🔋 Recarga",
                value=charging_nodes,
                delta=f"{int((charging_nodes/num_nodes)*100)}%"
            )
        
        with col_info3:
            st.metric(
                label="👤 Clientes",
                value=client_nodes,
                delta=f"{int((client_nodes/num_nodes)*100)}%"
            )
        
        # Información adicional
        st.info(f"""
        **Configuración de la Red:**
        - **Total de nodos:** {num_nodes}
        - **Aristas mínimas requeridas:** {min_edges_required}
        - **Aristas configuradas:** {num_edges}
        - **Órdenes a generar:** {num_orders}
        
        **Distribución de roles:**
        - 📦 Almacenamiento: {storage_nodes} nodos ({int((storage_nodes/num_nodes)*100)}%)
        - 🔋 Recarga: {charging_nodes} nodos ({int((charging_nodes/num_nodes)*100)}%)
        - 👤 Clientes: {client_nodes} nodos ({int((client_nodes/num_nodes)*100)}%)
        """)
        
        # Advertencia para configuraciones pequeñas
        if num_nodes < 15:
            st.warning('⚠️ La simulación puede no ser funcional con menos de 15 nodos debido a restricciones de conectividad y roles. Se recomienda usar al menos 15 nodos.')
    
    with col2:
        # Botón según especificación
        if st.button('📊 Start Simulation', use_container_width=True, type='primary'):
            with st.spinner('Inicializando simulación...'):
                try:
                    # Siempre crear una nueva instancia al iniciar la simulación
                    st.session_state.simulation_initializer = SimulationInitializer()
                    st.session_state.avl_tree = AVL()
                    st.session_state.routes = []
                    st.session_state.route_counter = 0
                    st.session_state.order_counter = 0
                    st.session_state.node_visits = {}
                    st.session_state.orders = []
                    st.session_state.clients = []
                    st.session_state.graph = None
                    st.session_state.network_adapter = None
                    
                    # Limpiar el visualizador de mapa y posiciones de nodos para nueva simulación
                    if 'map_visualizer' in st.session_state:
                        del st.session_state.map_visualizer
                    if 'node_positions' in st.session_state:
                        del st.session_state.node_positions
                    
                    # Inicializar simulación con parámetros validados
                    graph, orders, clients = st.session_state.simulation_initializer.initialize_simulation(
                        num_nodes, num_edges, num_orders
                    )
                    
                    if not graph or not graph.vertices():
                        raise ValueError("La inicialización de la red falló")
                    
                    st.session_state.graph = graph
                    st.session_state.orders = orders.copy() if orders else []
                    st.session_state.clients = clients.copy() if clients else []
                    st.session_state.routes = st.session_state.simulation_initializer.routes.copy()
                    st.session_state.order_counter = len(st.session_state.orders)
                    st.session_state.route_counter = len(st.session_state.routes)
                    
                    st.session_state.network_adapter = NetworkXAdapter(st.session_state.graph)
                    st.session_state.network_adapter.convert_to_networkx()
                
                    # Actualizar datos compartidos con la API
                    update_shared_data()
                
                    # Mostrar resumen de la simulación inicializada
                    st.success('✅ Simulación inicializada exitosamente!')
                    
                    # Mostrar estadísticas de la simulación creada
                    actual_nodes = len(graph.vertices())
                    actual_edges = len([edge for edge in graph.edges()])
                    actual_orders = len(orders) if orders else 0
                    actual_clients = len(clients) if clients else 0
                    
                    st.info(f"""
                    **Simulación Creada:**
                    - ✅ Nodos generados: {actual_nodes}
                    - ✅ Aristas creadas: {actual_edges}
                    - ✅ Órdenes generadas: {actual_orders}
                    - ✅ Clientes creados: {actual_clients}
                    - ✅ Red conectada: {'Sí' if st.session_state.simulation_initializer.is_connected() else 'No'}
                    """)
                    
                    st.rerun()
                except Exception as e:
                    st.error(f"❌ Error al inicializar la simulación: {str(e)}")
                    return

def explore_network_tab():
    st.header('🌍 Explorar Red Geográfica')
    
    if not st.session_state.graph:
        st.warning('Por favor, ejecute la simulación primero para explorar la red.')
        return
    
    if 'node_visits' not in st.session_state:
        st.session_state.node_visits = {}

    nodes = list(st.session_state.graph.vertices())
    storage_nodes = [n for n in nodes if n.startswith('S')]
    client_nodes = [n for n in nodes if n.startswith('T')]
    
    # Inicializar el visualizador de mapa solo una vez
    if 'map_visualizer' not in st.session_state:
        from src.visual.map_visualizer import MapVisualizer
        st.session_state.map_visualizer = MapVisualizer()
        
        # Generar posiciones de nodos una sola vez y guardarlas en session_state
        st.session_state.node_positions = st.session_state.map_visualizer.generate_node_positions(nodes, 'random')
    
    map_viz = st.session_state.map_visualizer
    
    # Usar las posiciones fijas de los nodos
    folium_map = map_viz.create_map(st.session_state.graph, st.session_state.node_positions)
    
    # 🧭 Componentes según especificación
    st.subheader('🧭 Configuración de Ruta')
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("#### 📦 Nodo Origen (Almacenamiento)")
        start_node = st.selectbox(
            'Seleccionar nodo origen',
            storage_nodes,
            key='origin',
            help="Solo se permiten nodos de almacenamiento como origen"
        )
    
    with col2:
        st.markdown("#### 👤 Nodo Destino (Cliente)")
        end_node = st.selectbox(
            'Seleccionar nodo destino',
            client_nodes,
            key='dest',
            help="Solo se permiten nodos cliente como destino"
        )
    
    with col3:
        st.markdown("#### 🚁 Algoritmo")
        st.info("**Dijkstra** - Algoritmo de caminos más cortos")
        algorithm = 'Dijkstra'  # Algoritmo fijo

    if 'current_path' not in st.session_state:
        st.session_state.current_path = None
        st.session_state.current_cost = 0
        st.session_state.path_calculated = False
        st.session_state.flight_summary = None

    # Botones de acción según especificación
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button('✈️ Calculate Route', use_container_width=True, type='primary'):
            # Validación: Solo permitir rutas de Almacenamiento → Cliente
            if not start_node.startswith('S') or not end_node.startswith('T'):
                st.error('❌ Solo se permiten rutas de Almacenamiento (S) → Cliente (T)')
                return
            
            # Usar algoritmo Dijkstra (fijo)
            dijkstra = DijkstraAlgorithm(st.session_state.graph)
            path, total_cost, info = dijkstra.find_shortest_path(start_node, end_node)
            completed = info.get('autonomy_respected', False)
            charging_points = info.get('charging_stations', [])
            reason = '' if completed else 'No se respeta la autonomía o no hay ruta.'
            segments = []
            valid_path = completed
            current_autonomy = dijkstra.MAX_AUTONOMY
            
            if path:
                for i in range(len(path)-1):
                    edge = st.session_state.graph.get_edge(path[i], path[i+1])
                    if edge:
                        edge_cost = edge.element()
                        if path[i].startswith('C') or path[i+1].startswith('C'):
                            charging_node = path[i] if path[i].startswith('C') else path[i+1]
                            if charging_node not in charging_points:
                                charging_points.append(charging_node)
                            current_autonomy = dijkstra.MAX_AUTONOMY
                            segments.append(f"🔋 Recargando en {charging_node} (Energía restaurada a {current_autonomy})")
                        current_autonomy -= edge_cost
                        segments.append(f"{path[i]} → {path[i+1]} (Costo: {edge_cost}, Energía: {current_autonomy})")
                    else:
                        valid_path = False
                        st.error(f"❌ No hay conexión directa entre {path[i]} y {path[i+1]}")
                        break

                # Resaltar la ruta en el mapa
                map_viz.highlight_path(path)
                st.session_state.current_path = path
                st.session_state.current_cost = total_cost
                st.session_state.path_calculated = completed
                
                # Crear resumen de vuelo con cálculo mejorado de batería
                # Calcular uso real de batería considerando recargas
                MAX_AUTONOMY = 50
                total_battery_used = 0
                current_battery = MAX_AUTONOMY
                
                for i in range(len(path) - 1):
                    edge = st.session_state.graph.get_edge(path[i], path[i+1])
                    if edge:
                        edge_cost = edge.element()
                        # Si el siguiente nodo es de recarga, restaurar batería
                        if path[i+1].startswith('C'):
                            current_battery = MAX_AUTONOMY
                        # Consumir batería del segmento actual
                        current_battery -= edge_cost
                        total_battery_used += edge_cost
                
                # Calcular porcentaje de uso de batería
                if total_battery_used > 0:
                    battery_usage = min((total_battery_used / MAX_AUTONOMY) * 100, 100)
                else:
                    battery_usage = 0
                
                st.session_state.flight_summary = {
                    'route': ' → '.join(path),
                    'total_cost': total_cost,
                    'battery_usage': battery_usage,
                    'total_battery_used': total_battery_used,
                    'charging_stations': charging_points,
                    'segments': segments,
                    'completed': completed,
                    'algorithm': algorithm
                }
                
                st.success(f"✅ Ruta calculada con {algorithm}")
                
            else:
                st.error(f"❌ No se encontró ninguna ruta posible: {reason}")
                st.session_state.path_calculated = False

    with col2:
        if st.button('🌲 Show MST (Kruskal)', use_container_width=True):
            try:
                # Mostrar el MST en el mapa
                mst_info = map_viz.show_mst(st.session_state.graph)
                st.success(f'🌲 MST (Kruskal) mostrado en el mapa (líneas discontinuas)')
                if mst_info:
                    st.info(f"📊 Información del MST:")
                    st.info(f"   • Nodos conectados: {len(mst_info['nodes'])}")
                    st.info(f"   • Conexiones: {len(mst_info['edges'])}")
                    st.info(f"   • Costo total: {mst_info['total_cost']}")
                    st.info(f"   • Cobertura: {mst_info['coverage_percentage']:.1f}%")
            except Exception as e:
                st.error(f'Error al mostrar el MST: {str(e)}')
    
    with col3:
        if st.button('🗺️ Limpiar Mapa', use_container_width=True):
            # Limpiar el mapa y restaurar rutas normales
            map_viz.clear_map(st.session_state.graph)
            st.session_state.current_path = None
            st.session_state.path_calculated = False
            st.session_state.flight_summary = None
            st.success('🗺️ Mapa limpiado - Rutas normales restauradas')

    # Mostrar el mapa principal
    st.subheader('🗺️ Mapa de la Red')
    
    # Agregar información de la ruta actual al mapa si existe
    if st.session_state.current_path and st.session_state.flight_summary:
        map_viz.add_route_summary(
            st.session_state.current_path, 
            st.session_state.current_cost, 
            st.session_state.flight_summary['battery_usage']
        )
    
    # Mostrar el mapa
    st.components.v1.html(map_viz.get_map_html(), height=600, scrolling=True)
    
    # Cuadro informativo: resumen de vuelo (según especificación)
    if st.session_state.flight_summary:
        st.subheader('📊 Resumen de Vuelo')
        
        summary = st.session_state.flight_summary
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown(f"""
            **🚁 Algoritmo:** {summary['algorithm']}  
            **📍 Ruta:** {summary['route']}  
            **💰 Costo Total:** {summary['total_cost']:.2f} unidades  
            **🔋 Energía Consumida:** {summary['total_battery_used']:.1f} / 50 unidades  
            **🔋 Uso de Batería:** {summary['battery_usage']:.1f}%  
            **📦 Nodos:** {len(st.session_state.current_path)}
            """)
        
        with col2:
            if summary['charging_stations']:
                st.markdown(f"""
                **⚡ Estaciones de Recarga:** {len(summary['charging_stations'])}  
                **🔋 Puntos de Recarga:** {', '.join(summary['charging_stations'])}  
                **✅ Estado:** {'Completada' if summary['completed'] else 'Parcial'}  
                **🚁 Autonomía Máxima:** 50 unidades
                **🔄 Recargas Realizadas:** {len(summary['charging_stations'])}
                """)
            else:
                st.markdown(f"""
                **⚡ Estaciones de Recarga:** No requeridas  
                **✅ Estado:** {'Completada' if summary['completed'] else 'Parcial'}  
                **🚁 Autonomía Máxima:** 50 unidades
                **🔄 Recargas Realizadas:** 0
                """)
        
        # Detalles de la ruta
        with st.expander("📍 Detalles de la Ruta", expanded=True):
            if summary['completed']:
                st.success(f"✅ Ruta completada exitosamente")
                if summary['charging_stations']:
                    st.warning(f"🔋 La ruta requiere {len(summary['charging_stations'])} paradas de carga: {', '.join(summary['charging_stations'])}")
            else:
                st.error(f"❌ Ruta parcial - No se respeta la autonomía completa")
            
            st.write("**Análisis detallado de la ruta:**")
            for segment in summary['segments']:
                st.write(f"• {segment}")

    # Botón para completar entrega (según especificación)
    if st.session_state.path_calculated:
        st.subheader('📦 Completar Entrega')
        
        if st.button('✅ Complete Delivery and Create Order', use_container_width=True, type='primary'):
            try:
                path = st.session_state.current_path
                total_cost = st.session_state.current_cost
                
                # Registrar visitas a nodos
                for node in path:
                    st.session_state.node_visits[node] = st.session_state.node_visits.get(node, 0) + 1
                
                # Crear o actualizar ruta
                st.session_state.route_counter += 1
                route_id = f"Ruta_{st.session_state.route_counter}"
                
                existing_route = None
                route_nodes_tuple = tuple(path)
                
                for r in st.session_state.routes:
                    if tuple(r.nodes) == route_nodes_tuple:
                        existing_route = r
                        break
                
                if existing_route:
                    route = existing_route
                    route.increment_frequency()
                else:
                    route = Route(route_id, path)
                    route.frequency = 1
                    st.session_state.routes.append(route)
                
                # Crear orden
                st.session_state.order_counter += 1
                order_id = f"ORD_{st.session_state.order_counter}"
                
                client_node = end_node  # Ya validamos que es un cliente
                client_num = client_node[1:]
                client = next((c for c in st.session_state.clients if c.client_id == f"CLI{client_num}"), None)
                
                if client:
                    order = Order(
                        order_id=order_id,
                        origin=start_node,
                        destination=end_node,
                        client_id=client.client_id,
                        client_name=client.name,
                        priority=client.client_type
                    )
                    client.add_order(order)
                    
                    order.assign_route(route)
                    order.route_cost = total_cost
                    order.status = "Completado"
                    
                    st.session_state.orders.append(order)
                
                # Actualizar datos compartidos con la API
                update_shared_data()
                
                st.success("✅ Entrega completada y orden creada exitosamente!")
                st.session_state.path_calculated = False
                st.session_state.flight_summary = None
                
                st.rerun()
            except Exception as e:
                st.error(f"❌ Error al completar la entrega: {str(e)}")

    # Información adicional del sistema
    if st.session_state.graph:
        st.subheader('📊 Información del Sistema')
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Total Nodos", len(nodes))
        
        with col2:
            st.metric("Nodos Almacenamiento", len(storage_nodes))
        
        with col3:
            charging_nodes = [n for n in nodes if n.startswith('C')]
            st.metric("Nodos Recarga", len(charging_nodes))
        
        with col4:
            st.metric("Nodos Cliente", len(client_nodes))

def clients_orders_tab():
    st.header('👥 Clientes y Órdenes')
    
    if not st.session_state.graph:
        st.warning('Por favor, ejecute la simulación primero para ver clientes y órdenes.')
        return
    
    # Botón para refrescar información
    if st.button('🔄 Refrescar Información', use_container_width=True):
        from src.shared_data import shared_data_manager
        # Recargar clientes y órdenes desde el archivo compartido
        st.session_state.clients = []
        st.session_state.orders = []
        data = shared_data_manager._load_data()
        if data:
            # Cargar clientes - filtrar solo campos válidos
            if 'clients' in data:
                from src.domain.Client import Client
                for client_data in data['clients']:
                    # Solo usar campos que acepta el constructor de Client
                    valid_client_data = {
                        'client_id': client_data.get('client_id'),
                        'name': client_data.get('name'),
                        'client_type': client_data.get('client_type'),
                        'node_id': client_data.get('node_id')  # Agregar node_id
                    }
                    st.session_state.clients.append(Client(**valid_client_data))
            # Cargar órdenes - filtrar solo campos válidos
            if 'orders' in data:
                from src.domain.Order import Order
                from src.domain.Route import Route
                for order_data in data['orders']:
                    # Solo usar campos que acepta el constructor de Order
                    valid_order_data = {
                        'order_id': order_data.get('order_id'),
                        'origin': order_data.get('origin'),
                        'destination': order_data.get('destination'),
                        'client_id': order_data.get('client_id'),
                        'client_name': order_data.get('client_name'),
                        'priority': order_data.get('priority', 'Normal')
                    }
                    order = Order(**valid_order_data)
                    # Establecer campos adicionales si existen
                    if 'status' in order_data:
                        order.status = order_data['status']
                    if 'route_cost' in order_data:
                        order.route_cost = order_data['route_cost']
                    if 'creation_date' in order_data and order_data['creation_date']:
                        from datetime import datetime
                        order.creation_date = datetime.fromisoformat(order_data['creation_date'])
                    if 'delivery_date' in order_data and order_data['delivery_date']:
                        from datetime import datetime
                        order.delivery_date = datetime.fromisoformat(order_data['delivery_date'])
                    
                    # Restaurar la ruta si existe
                    if 'route_info' in order_data and order_data['route_info']:
                        route_info = order_data['route_info']
                        route = Route(route_info['route_id'], route_info['nodes'])
                        route.frequency = route_info['frequency']
                        order.assign_route(route)
                    
                    st.session_state.orders.append(order)
        st.success('✅ Información recargada desde la API/archivo compartido.')
        st.rerun()
    
    st.subheader('📋 Clientes')
    if st.session_state.clients:
        clients_json = []
        for client in st.session_state.clients:
            total_orders = len([order for order in st.session_state.orders if order.client_id == client.client_id])
            client_data = {
                "ID": client.client_id,
                "Nombre": client.name,
                "Tipo": client.client_type,
                "Total Órdenes": total_orders,
                "Nodo": client.node_id if hasattr(client, 'node_id') else 'N/A'
            }
            clients_json.append(client_data)
        st.json(clients_json)
    else:
        st.info('No hay clientes disponibles.')
    
    st.subheader('📦 Órdenes')
    if st.session_state.orders:
        orders_json = []
        for order in st.session_state.orders:
            if not hasattr(order, 'total_cost') or not order.total_cost:
                total_cost = 0
                if hasattr(order, 'route') and order.route:
                    for i in range(len(order.route.nodes)-1):
                        edge = st.session_state.graph.get_edge(order.route.nodes[i], order.route.nodes[i+1])
                        if edge:
                            total_cost += edge.element()
                    order.total_cost = total_cost
            
            order_data = {
                "ID Orden": order.order_id,
                "ID Cliente": order.client_id if hasattr(order, 'client_id') else None,
                "Nombre Cliente": order.client_name if hasattr(order, 'client_name') else None,
                "Origen": order.origin,
                "Destino": order.destination,
                "Estado": order.status if hasattr(order, 'status') else "Pendiente",
                "Prioridad": order.priority if hasattr(order, 'priority') else "Normal",
                "Fecha Creación": order.creation_date.strftime("%Y-%m-%d %H:%M:%S") if hasattr(order, 'creation_date') and order.creation_date else None,
                "Fecha Entrega": order.delivery_date.strftime("%Y-%m-%d %H:%M:%S") if hasattr(order, 'delivery_date') and order.delivery_date else None,
                "Costo Total": order.total_cost if hasattr(order, 'total_cost') else total_cost,
                "Ruta": ' → '.join(order.route.nodes) if hasattr(order, 'route') and order.route else 'No asignada'
            }
            orders_json.append(order_data)
        st.json(orders_json)
    else:
        st.info('No hay órdenes disponibles.')

def route_analytics_tab():
    st.header('📋 Análisis de Rutas')
    
    if not st.session_state.routes:
        st.info('No hay rutas registradas aún. Use la pestaña "Explorar Red" para crear rutas.')
        return

    try:
        # Ordenar rutas por frecuencia (descendente) y luego por recorrido (lexicográfico)
        sorted_routes = sorted(st.session_state.routes, 
                             key=lambda x: (-x.frequency, ' → '.join(x.nodes)))

        # Crear árbol AVL
        avl_tree = AVL()
        for route in sorted_routes:
            avl_tree.insert(route)
        
        # Sección 1: Gráfico del árbol AVL
        st.subheader('🌳 Árbol AVL de Frecuencias de Rutas')
        st.info("Visualización de la estructura AVL balanceada con etiquetas 'A → B → C\\nFreq: X'")
        
        avl_visualizer = AVLVisualizer(avl_tree)
        fig = avl_visualizer.visualize()
        st.pyplot(fig)
        plt.close()

        # Sección 2: Lista de rutas más frecuentes
        st.subheader('🔄 Rutas Más Frecuentes')
        st.info("Rutas ordenadas por frecuencia de uso (descendente) y luego por recorrido (lexicográfico)")
        
        routes_data = []
        for route in sorted_routes:
            routes_data.append({
                'Ruta': ' → '.join(route.nodes),
                'Frecuencia': route.frequency,
                'Nodos': len(route.nodes),
                'Origen': route.nodes[0],
                'Destino': route.nodes[-1]
            })
        
        df_routes = pd.DataFrame(routes_data)
        st.dataframe(
            df_routes,
            column_config={
                "Ruta": "Secuencia de Nodos",
                "Frecuencia": st.column_config.NumberColumn("Frecuencia de Uso", format="%d"),
                "Nodos": "Cantidad de Nodos",
                "Origen": "Nodo Origen",
                "Destino": "Nodo Destino"
            },
            hide_index=True
        )

        # Sección 3: Estadísticas de rutas
        st.subheader('📈 Estadísticas de Rutas')
        col1, col2, col3 = st.columns(3)
        
        with col1:
            total_routes = len(st.session_state.routes)
            st.metric("Total de Rutas Únicas", total_routes)
        
        with col2:
            total_frequency = sum(route.frequency for route in st.session_state.routes)
            st.metric("Total de Viajes Realizados", total_frequency)
        
        with col3:
            avg_frequency = total_frequency / total_routes if total_routes > 0 else 0
            st.metric("Promedio de Uso por Ruta", f"{avg_frequency:.2f}")

        # Sección 4: Botón de generación de PDF
        st.subheader('📄 Generar Informe PDF')
        st.info("Descarga un reporte completo con: rutas frecuentes, clientes recurrentes, nodos utilizados y gráficas")
        
        if st.button('📄 Generar Informe PDF', use_container_width=True, type='primary'):
            try:
                from src.visual.report_generator import ReportGenerator
                
                # Crear generador de reportes
                report_gen = ReportGenerator()
                
                # Generar el reporte
                output_path = f"reporte_rutas_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
                report_path = report_gen.generate_report(
                    graph=st.session_state.graph,
                    orders=st.session_state.orders,
                    clients=st.session_state.clients,
                    routes=st.session_state.routes,
                    output_path=output_path
                )
                
                # Leer el archivo generado
                with open(report_path, "rb") as pdf_file:
                    pdf_bytes = pdf_file.read()
                
                # Descargar el PDF
                st.download_button(
                    label="📥 Descargar Reporte PDF",
                    data=pdf_bytes,
                    file_name=output_path,
                    mime="application/pdf",
                    use_container_width=True
                )
                
                st.success(f"✅ Reporte PDF generado exitosamente: {output_path}")
                st.info("📊 El reporte incluye:")
                st.info("   • Rutas frecuentes y su análisis")
                st.info("   • Clientes más recurrentes")
                st.info("   • Nodos más utilizados")
                st.info("   • Gráficas de torta y barras")
                st.info("   • Estadísticas completas del sistema")
                
            except Exception as e:
                st.error(f"❌ Error al generar el reporte PDF: {str(e)}")
                st.error("Asegúrate de que todas las dependencias estén instaladas (reportlab, matplotlib)")
        
    except Exception as e:
        st.error(f"Error al procesar las rutas: {str(e)}")
        return

def general_statistics_tab():
    st.header('📈 Estadísticas Generales')
    
    if not st.session_state.graph:
        st.warning('Por favor, ejecute la simulación primero para ver las estadísticas.')
        return
    
    # Título para la sección de nodos más visitados
    st.subheader('📊 Nodos Más Visitados por Rol')
    
    # Obtener y filtrar nodos por tipo
    nodes = list(st.session_state.graph.vertices())
    storage_nodes = [n for n in nodes if n.startswith('S')]
    charging_nodes = [n for n in nodes if n.startswith('C')]
    client_nodes = [n for n in nodes if n.startswith('T')]
    
    # Crear tres columnas para los gráficos
    col1, col2, col3 = st.columns(3)

    # Función auxiliar para crear gráficos de barras
    def create_bar_chart(data, title, color):
        if data:
            df = pd.DataFrame({
                'Node': [node for node, _ in data],
                'Visits': [visits for _, visits in data]
            })
            fig = plt.figure(figsize=(8, 5))
            plt.bar(df['Node'], df['Visits'], color=color)
            plt.xticks(rotation=45)
            plt.title(title)
            plt.tight_layout()
            return fig
        return None

    # Agregar visitas de todas las rutas por tipo de nodo
    def aggregate_visits_by_type(node_type_prefix):
        visits = {}
        for route in getattr(st.session_state, 'routes', []):
            for node, count in route.get_node_visits().items():
                if node.startswith(node_type_prefix):
                    visits[node] = visits.get(node, 0) + count
        # Ordenar por visitas descendente
        return sorted(visits.items(), key=lambda x: x[1], reverse=True)

    with col1:
        st.markdown("👥 Clientes Más Visitados")
        client_visits = aggregate_visits_by_type('T')
        if client_visits:
            fig = create_bar_chart(client_visits[:5], 'Top 5 Clientes Más Visitados', '#66B2FF')
            if fig:
                st.pyplot(fig)
                plt.close()
        else:
            st.info('No hay visitas registradas a clientes.')

    with col2:
        st.markdown("🔋 Estaciones de Recarga Más Visitadas")
        charging_visits = aggregate_visits_by_type('C')
        if charging_visits:
            fig = create_bar_chart(charging_visits[:5], 'Top 5 Estaciones de Recarga Más Visitadas', '#66B2FF')
            if fig:
                st.pyplot(fig)
                plt.close()
        else:
            st.info('No hay visitas registradas a estaciones de recarga.')

    with col3:
        st.markdown("📦 Almacenes Más Visitados")
        storage_visits = aggregate_visits_by_type('S')
        if storage_visits:
            fig = create_bar_chart(storage_visits[:5], 'Top 5 Almacenes Más Visitados', '#66B2FF')
            if fig:
                st.pyplot(fig)
                plt.close()
        else:
            st.info('No hay visitas registradas a almacenes.')

    # Distribución de roles de nodos
    st.subheader('🔄 Gráfico de Torta: Distribución de Roles de Nodos')
    
    # Contar nodos por tipo
    node_types = {
        "Almacenamiento": len(storage_nodes),
        "Recarga": len(charging_nodes),
        "Cliente": len(client_nodes)
    }
    
    fig = plt.figure(figsize=(10, 6))
    plt.pie(
        list(node_types.values()),
        labels=list(node_types.keys()),
        colors=['#FF9999', '#66B2FF', '#99FF99'],
        autopct='%1.1f%%',
        startangle=90
    )
    plt.title('Distribución de Nodos por Rol')
    st.pyplot(fig)
    plt.close()
    
    # Estadísticas adicionales en columnas
    st.subheader('📊 Estadísticas Adicionales')
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Total de Nodos", len(nodes))
        st.metric("Nodos de Almacenamiento", len(storage_nodes))
    
    with col2:
        st.metric("Nodos de Recarga", len(charging_nodes))
        st.metric("Nodos Cliente", len(client_nodes))
    
    with col3:
        total_edges = sum(1 for _ in st.session_state.graph.edges())
        st.metric("Total de Conexiones", total_edges)
        avg_connections = total_edges / len(nodes) if len(nodes) > 0 else 0
        st.metric("Promedio de Conexiones", f"{avg_connections:.2f}")
    
    # Estadísticas de órdenes
    st.subheader('📦 Estadísticas de Órdenes')
    if st.session_state.orders:
        col1, col2, col3 = st.columns(3)
        
        with col1:
            total_orders = len(st.session_state.orders)
            st.metric('Total de Órdenes', total_orders)
        
        with col2:
            avg_cost = sum(order.route_cost for order in st.session_state.orders) / total_orders if total_orders > 0 else 0
            st.metric('Costo Promedio', f"{avg_cost:.2f}")
        
        with col3:
            priorities = [order.priority for order in st.session_state.orders]
            most_common = max(set(priorities), key=priorities.count) if priorities else "N/A"
            st.metric('Prioridad Más Común', most_common)
    else:
        st.info('No hay datos de órdenes disponibles.')

def tabs_container():
    tabs = st.tabs([
        "⚙️ Inicializar Simulación",
        "🗺️ Explorar Red",
        "👥 Clientes y Órdenes",
        "📋 Análisis de Rutas",
        "📈 Estadísticas"
    ])
    
    with tabs[0]:
        run_simulation_tab()
    with tabs[1]:
        explore_network_tab()
    with tabs[2]:
        clients_orders_tab()
    with tabs[3]:
        route_analytics_tab()
    with tabs[4]:
        general_statistics_tab()

def run_dashboard():
    # Main title
    st.title('🚁 Sistema de Entrega con Drones')
    
    # Initialize session state variables if they don't exist
    if 'graph' not in st.session_state:
        st.session_state.graph = None
    if 'simulation_initializer' not in st.session_state:
        st.session_state.simulation_initializer = None
    if 'network_adapter' not in st.session_state:
        st.session_state.network_adapter = None
    if 'routes' not in st.session_state:
        st.session_state.routes = []
    if 'orders' not in st.session_state:
        st.session_state.orders = []
    if 'clients' not in st.session_state:
        st.session_state.clients = []
    if 'route_counter' not in st.session_state:
        st.session_state.route_counter = 0
    if 'order_counter' not in st.session_state:
        st.session_state.order_counter = 0
    
    # Show tabs
    tabs_container()

if __name__ == "__main__":
    run_dashboard() 