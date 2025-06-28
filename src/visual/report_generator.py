from reportlab.lib.pagesizes import letter, A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT
import matplotlib.pyplot as plt
import pandas as pd
import io
import os
import json
from datetime import datetime

class ReportGenerator:
    def __init__(self):
        self.styles = getSampleStyleSheet()
        self._setup_custom_styles()
    
    def _setup_custom_styles(self):
        """Configura estilos personalizados para el reporte"""
        self.title_style = ParagraphStyle(
            'CustomTitle',
            parent=self.styles['Heading1'],
            fontSize=24,
            spaceAfter=30,
            alignment=TA_CENTER,
            textColor=colors.darkblue
        )
        
        self.heading_style = ParagraphStyle(
            'CustomHeading',
            parent=self.styles['Heading2'],
            fontSize=16,
            spaceAfter=12,
            textColor=colors.darkblue
        )
        
        self.normal_style = ParagraphStyle(
            'CustomNormal',
            parent=self.styles['Normal'],
            fontSize=10,
            spaceAfter=6
        )
    
    def _get_field(self, obj, field, default='N/A'):
        if isinstance(obj, dict):
            return obj.get(field, default)
        return getattr(obj, field, default)
    
    def generate_report(self, graph, orders, clients, routes, output_path="reporte_drones.pdf"):
        """
        Genera un reporte PDF con exactamente lo solicitado.
        
        Args:
            graph: Grafo del sistema (puede ser None)
            orders: Lista de órdenes
            clients: Lista de clientes
            routes: Lista de rutas
            output_path: Ruta donde guardar el PDF
        """
        doc = SimpleDocTemplate(output_path, pagesize=A4)
        story = []
        
        # Título principal
        story.append(Paragraph("🚁 Sistema Logístico de Drones", self.title_style))
        story.append(Paragraph(f"Reporte Generado: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}", self.styles['Normal']))
        story.append(Spacer(1, 20))
        
        # 1. Tabla de clientes con Info(ID,Nombre,Type,total_orders)
        story.extend(self._generate_client_table(clients, orders))
        
        # 2. Todas las órdenes en formato JSON
        story.extend(self._generate_orders_json(orders))
        
        # 3. Distribución de nodos (piechart)
        story.extend(self._generate_node_distribution_chart(graph, routes))
        
        # 4. Gráfico de barras de Clientes más visitados
        story.extend(self._generate_most_visited_clients_chart(clients, orders))
        
        # 5. Gráfico de barras de Estaciones de Recarga
        story.extend(self._generate_charging_stations_chart(graph, routes))
        
        # 6. Gráfico de barras de Almacenamiento
        story.extend(self._generate_storage_stations_chart(graph, routes))
        
        # Construir PDF
        doc.build(story)
        return output_path
    
    def _generate_client_table(self, clients, orders):
        """Genera tabla de clientes con Info(ID,Nombre,Type,total_orders)"""
        story = []
        story.append(Paragraph("👥 Tabla de Clientes", self.heading_style))
        
        if not clients:
            story.append(Paragraph("No hay clientes disponibles.", self.normal_style))
            return story
        
        # Crear diccionario para contar órdenes por cliente
        client_orders_count = {}
        if orders:
            for order in orders:
                client_id = self._get_field(order, 'client_id', None)
                if client_id:
                    client_orders_count[client_id] = client_orders_count.get(client_id, 0) + 1
        
        # Crear tabla de clientes
        client_data = [
            ['ID', 'Nombre', 'Type', 'Total Órdenes']
        ]
        
        for client in clients:
            client_id = self._get_field(client, 'client_id', 'N/A')
            total_orders = client_orders_count.get(client_id, 0)
            
            client_data.append([
                client_id,
                self._get_field(client, 'name', 'N/A'),
                self._get_field(client, 'client_type', 'Regular'),
                str(total_orders)
            ])
        
        client_table = Table(client_data, colWidths=[1*inch, 2*inch, 1*inch, 1*inch])
        client_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 10),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        
        story.append(client_table)
        story.append(Spacer(1, 20))
        
        return story
    
    def _generate_orders_json(self, orders):
        """Genera todas las órdenes en formato JSON como en la página"""
        story = []
        story.append(Paragraph("📦 Todas las Órdenes (JSON)", self.heading_style))
        
        if not orders:
            story.append(Paragraph("No hay órdenes disponibles.", self.normal_style))
            return story
        
        # Convertir órdenes a formato JSON
        orders_json = []
        for order in orders:
            order_dict = {
                'order_id': self._get_field(order, 'order_id', 'N/A'),
                'origin': self._get_field(order, 'origin', 'N/A'),
                'destination': self._get_field(order, 'destination', 'N/A'),
                'client_id': self._get_field(order, 'client_id', 'N/A'),
                'client_name': self._get_field(order, 'client_name', 'N/A'),
                'status': self._get_field(order, 'status', 'Pendiente'),
                'priority': self._get_field(order, 'priority', 'Normal'),
                'route_cost': self._get_field(order, 'route_cost', 0)
            }
            orders_json.append(order_dict)
        
        # Crear texto JSON formateado
        json_text = json.dumps(orders_json, indent=2, ensure_ascii=False)
        
        # Dividir JSON en líneas para el PDF
        json_lines = json_text.split('\n')
        for line in json_lines:
            story.append(Paragraph(line, self.normal_style))
        
        story.append(Spacer(1, 20))
        return story
    
    def _generate_node_distribution_chart(self, graph, routes):
        """Genera gráfico de distribución de nodos (piechart)"""
        story = []
        story.append(Paragraph("📊 Distribución de Nodos", self.heading_style))
        
        # Obtener nodos desde el grafo o desde las rutas
        nodes = []
        if graph:
            nodes = list(graph.vertices())
        elif routes:
            # Extraer nodos únicos desde las rutas
            nodes_set = set()
            for route in routes:
                if hasattr(route, 'nodes'):
                    nodes_set.update(route.nodes)
                elif isinstance(route, dict) and 'nodes' in route:
                    nodes_set.update(route['nodes'])
            nodes = list(nodes_set)
        
        if not nodes:
            story.append(Paragraph("No hay datos de nodos disponibles.", self.normal_style))
            return story
        
        storage_nodes = [n for n in nodes if n.startswith('S')]
        charging_nodes = [n for n in nodes if n.startswith('C')]
        client_nodes = [n for n in nodes if n.startswith('T')]
        
        # Crear gráfico de pie
        fig, ax = plt.subplots(figsize=(8, 6))
        labels = ['Almacenamiento', 'Recarga', 'Cliente']
        sizes = [len(storage_nodes), len(charging_nodes), len(client_nodes)]
        colors_pie = ['#FF9999', '#66B2FF', '#99FF99']
        
        ax.pie(sizes, labels=labels, colors=colors_pie, autopct='%1.1f%%', startangle=90)
        ax.set_title('Distribución de Nodos por Tipo')
        
        # Guardar gráfico temporalmente
        img_buffer = io.BytesIO()
        plt.savefig(img_buffer, format='png', dpi=300, bbox_inches='tight')
        img_buffer.seek(0)
        plt.close()
        
        # Agregar imagen al reporte
        story.append(Image(img_buffer, width=4*inch, height=3*inch))
        story.append(Spacer(1, 20))
        
        return story
    
    def _generate_most_visited_clients_chart(self, clients, orders):
        """Genera gráfico de barras de Clientes más visitados"""
        story = []
        story.append(Paragraph("👥 Clientes Más Visitados", self.heading_style))
        
        if not clients or not orders:
            story.append(Paragraph("No hay datos suficientes para generar el gráfico.", self.normal_style))
            return story
        
        # Contar visitas por cliente
        client_visits = {}
        for order in orders:
            client_id = self._get_field(order, 'client_id', None)
            if client_id:
                client_visits[client_id] = client_visits.get(client_id, 0) + 1
        
        if not client_visits:
            story.append(Paragraph("No hay datos de visitas disponibles.", self.normal_style))
            return story
        
        # Obtener top 10 clientes más visitados
        sorted_clients = sorted(client_visits.items(), key=lambda x: x[1], reverse=True)[:10]
        
        # Crear gráfico de barras
        fig, ax = plt.subplots(figsize=(10, 6))
        client_names = [f"Cliente {client_id}" for client_id, _ in sorted_clients]
        visit_counts = [count for _, count in sorted_clients]
        
        bars = ax.bar(client_names, visit_counts, color='#4ECDC4')
        ax.set_title('Clientes Más Visitados')
        ax.set_ylabel('Número de Visitas')
        ax.set_xlabel('Clientes')
        
        # Rotar etiquetas del eje X para mejor legibilidad
        plt.xticks(rotation=45, ha='right')
        
        # Agregar valores en las barras
        for bar, count in zip(bars, visit_counts):
            ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.1, 
                   str(count), ha='center', va='bottom')
        
        plt.tight_layout()
                
        # Guardar gráfico temporalmente
        img_buffer = io.BytesIO()
        plt.savefig(img_buffer, format='png', dpi=300, bbox_inches='tight')
        img_buffer.seek(0)
        plt.close()
        
        # Agregar imagen al reporte
        story.append(Image(img_buffer, width=5*inch, height=3*inch))
        story.append(Spacer(1, 20))
        
        return story
    
    def _generate_charging_stations_chart(self, graph, routes):
        """Genera gráfico de barras de Estaciones de Recarga"""
        story = []
        story.append(Paragraph("🔋 Estaciones de Recarga", self.heading_style))
        nodes = []
        if graph:
            nodes = list(graph.vertices())
        elif routes:
            nodes_set = set()
            for route in routes:
                if hasattr(route, 'nodes'):
                    nodes_set.update(route.nodes)
                elif isinstance(route, dict) and 'nodes' in route:
                    nodes_set.update(route['nodes'])
            nodes = list(nodes_set)
        if not nodes:
            story.append(Paragraph("No hay datos de nodos disponibles.", self.normal_style))
            return story
        charging_nodes = [n for n in nodes if n.startswith('C')]
        if not charging_nodes:
            story.append(Paragraph("No hay estaciones de recarga disponibles.", self.normal_style))
            return story
        charging_usage = {}
        for node in charging_nodes:
            usage = int(node[1:]) if len(node) > 1 and node[1:].isdigit() else 1
            charging_usage[node] = usage
        fig, ax = plt.subplots(figsize=(10, 6))
        station_names = list(charging_usage.keys())
        usage_counts = list(charging_usage.values())
        bars = ax.bar(station_names, usage_counts, color='#FF6B6B')
        ax.set_title('Uso de Estaciones de Recarga')
        ax.set_ylabel('Número de Usos')
        ax.set_xlabel('Estaciones de Recarga')
        for bar, count in zip(bars, usage_counts):
            ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.1, str(count), ha='center', va='bottom')
        plt.tight_layout()
        img_buffer = io.BytesIO()
        plt.savefig(img_buffer, format='png', dpi=300, bbox_inches='tight')
        img_buffer.seek(0)
        plt.close()
        story.append(Image(img_buffer, width=5*inch, height=3*inch))
        story.append(Spacer(1, 20))
        return story
    
    def _generate_storage_stations_chart(self, graph, routes):
        """Genera gráfico de barras de Almacenamiento"""
        story = []
        story.append(Paragraph("📦 Almacenamiento", self.heading_style))
        nodes = []
        if graph:
            nodes = list(graph.vertices())
        elif routes:
            nodes_set = set()
            for route in routes:
                if hasattr(route, 'nodes'):
                    nodes_set.update(route.nodes)
                elif isinstance(route, dict) and 'nodes' in route:
                    nodes_set.update(route['nodes'])
            nodes = list(nodes_set)
        if not nodes:
            story.append(Paragraph("No hay datos de nodos disponibles.", self.normal_style))
            return story
        storage_nodes = [n for n in nodes if n.startswith('S')]
        if not storage_nodes:
            story.append(Paragraph("No hay nodos de almacenamiento disponibles.", self.normal_style))
            return story
        storage_usage = {}
        for node in storage_nodes:
            usage = int(node[1:]) if len(node) > 1 and node[1:].isdigit() else 1
            storage_usage[node] = usage
        fig, ax = plt.subplots(figsize=(10, 6))
        storage_names = list(storage_usage.keys())
        usage_counts = list(storage_usage.values())
        bars = ax.bar(storage_names, usage_counts, color='#45B7D1')
        ax.set_title('Uso de Nodos de Almacenamiento')
        ax.set_ylabel('Número de Usos')
        ax.set_xlabel('Nodos de Almacenamiento')
        for bar, count in zip(bars, usage_counts):
            ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.1, str(count), ha='center', va='bottom')
        plt.tight_layout()
        img_buffer = io.BytesIO()
        plt.savefig(img_buffer, format='png', dpi=300, bbox_inches='tight')
        img_buffer.seek(0)
        plt.close()
        story.append(Image(img_buffer, width=5*inch, height=3*inch))
        story.append(Spacer(1, 20))
        return story 