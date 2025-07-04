"""
Cliente API para el dashboard de Streamlit
Permite que el dashboard consuma datos desde la API REST
"""

import requests
import json
from typing import Dict, List, Optional, Any
import streamlit as st

class APIClient:
    """Cliente para consumir la API REST del Sistema de Drones"""
    
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
        self.session = requests.Session()
    
    def _make_request(self, method: str, endpoint: str, data: Optional[Dict] = None) -> Dict:
        """Realiza una petición HTTP a la API"""
        url = f"{self.base_url}{endpoint}"
        
        try:
            if method.upper() == "GET":
                response = self.session.get(url)
            elif method.upper() == "POST":
                response = self.session.post(url, json=data)
            else:
                raise ValueError(f"Método HTTP no soportado: {method}")
            
            response.raise_for_status()
            return response.json()
            
        except requests.exceptions.ConnectionError:
            raise Exception(f"No se puede conectar a la API en {self.base_url}. Asegúrate de que la API esté ejecutándose.")
        except requests.exceptions.HTTPError as e:
            if response.status_code == 404:
                raise Exception(f"Endpoint no encontrado: {endpoint}")
            elif response.status_code == 400:
                error_data = response.json()
                raise Exception(f"Error en la petición: {error_data.get('detail', 'Error desconocido')}")
            else:
                raise Exception(f"Error HTTP {response.status_code}: {response.text}")
        except Exception as e:
            raise Exception(f"Error al comunicarse con la API: {str(e)}")
    
    def check_api_status(self) -> bool:
        """Verifica si la API está disponible"""
        try:
            response = self._make_request("GET", "/")
            return True
        except:
            return False
    
    def get_simulation_status(self) -> Dict:
        """Obtiene el estado actual de la simulación"""
        return self._make_request("GET", "/simulation/status")
    
    def initialize_simulation(self, num_nodes: int, num_edges: int, num_orders: int) -> Dict:
        """Inicializa una nueva simulación"""
        data = {
            "num_nodes": num_nodes,
            "num_edges": num_edges,
            "num_orders": num_orders
        }
        return self._make_request("POST", "/simulation/initialize", data)
    
    def reset_simulation(self) -> Dict:
        """Reinicia la simulación"""
        return self._make_request("GET", "/simulation/reset")
    
    def get_clients(self) -> List[Dict]:
        """Obtiene la lista de clientes"""
        response = self._make_request("GET", "/clients/")
        return response.get("clients", [])
    
    def get_client(self, client_id: str) -> Dict:
        """Obtiene información de un cliente específico"""
        return self._make_request("GET", f"/clients/{client_id}")
    
    def get_orders(self) -> List[Dict]:
        """Obtiene la lista de órdenes"""
        response = self._make_request("GET", "/orders/")
        return response.get("orders", [])
    
    def get_order(self, order_id: str) -> Dict:
        """Obtiene información de una orden específica"""
        return self._make_request("GET", f"/orders/orders/{order_id}")
    
    def complete_order(self, order_id: str) -> Dict:
        """Completa una orden"""
        return self._make_request("POST", f"/orders/orders/{order_id}/complete")
    
    def cancel_order(self, order_id: str) -> Dict:
        """Cancela una orden"""
        return self._make_request("POST", f"/orders/orders/{order_id}/cancel")
    
    def calculate_route(self, start_node: str, end_node: str, algorithm: str = "dijkstra") -> Dict:
        """Calcula una ruta entre dos nodos"""
        data = {
            "start_node": start_node,
            "end_node": end_node,
            "algorithm": algorithm
        }
        return self._make_request("POST", "/routes/calculate", data)
    
    def get_mst(self) -> Dict:
        """Obtiene el árbol de expansión mínima"""
        return self._make_request("GET", "/routes/mst")
    
    def generate_pdf_report(self) -> bytes:
        """Genera un reporte PDF"""
        url = f"{self.base_url}/reports/reports/pdf"
        try:
            response = self.session.get(url)
            response.raise_for_status()
            return response.content
        except Exception as e:
            raise Exception(f"Error generando PDF: {str(e)}")
    
    def get_summary(self) -> Dict:
        """Obtiene el resumen general de la simulación"""
        return self._make_request("GET", "/info/reports/summary")
    
    def get_client_visits_ranking(self) -> List[Dict]:
        """Obtiene el ranking de visitas de clientes"""
        response = self._make_request("GET", "/info/reports/visits/clients")
        return response.get("ranking", [])
    
    def get_recharge_visits_ranking(self) -> List[Dict]:
        """Obtiene el ranking de visitas de estaciones de recarga"""
        response = self._make_request("GET", "/info/reports/visits/recharges")
        return response.get("ranking", [])
    
    def get_storage_visits_ranking(self) -> List[Dict]:
        """Obtiene el ranking de visitas de almacenes"""
        response = self._make_request("GET", "/info/reports/visits/storages")
        return response.get("ranking", [])

# Instancia global del cliente API
api_client = APIClient()

def get_api_client() -> APIClient:
    """Obtiene la instancia global del cliente API"""
    return api_client

def check_api_connection() -> bool:
    """Verifica la conexión con la API y muestra mensajes apropiados"""
    try:
        if api_client.check_api_status():
            return True
        else:
            st.error("❌ No se puede conectar a la API. Asegúrate de que esté ejecutándose en http://localhost:8000")
            st.info("💡 Para ejecutar la API: python run_api_simple.py")
            return False
    except Exception as e:
        st.error(f"❌ Error de conexión con la API: {str(e)}")
        st.info("💡 Para ejecutar la API: python run_api_simple.py")
        return False

def get_simulation_data() -> Optional[Dict]:
    """Obtiene los datos de simulación desde la API"""
    try:
        status = api_client.get_simulation_status()
        if status.get("initialized"):
            return status.get("simulation_summary", {})
        else:
            return None
    except Exception as e:
        st.error(f"❌ Error obteniendo datos de simulación: {str(e)}")
        return None
