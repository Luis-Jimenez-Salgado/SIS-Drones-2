"""
Controlador para endpoints de información y estadísticas
"""

from fastapi import APIRouter, HTTPException
from typing import List, Dict
import sys
import os

# Agregar el directorio raíz al path para importar módulos
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from src.shared_data import shared_data_manager

router = APIRouter()

@router.get("/reports/visits/clients")
async def get_client_visits_ranking():
    """Obtener ranking de clientes más visitados"""
    if not shared_data_manager.is_initialized():
        raise HTTPException(status_code=400, detail="Simulación no inicializada. Inicialice la simulación desde el dashboard primero.")
    try:
        node_visits = shared_data_manager.get_node_visits() or {}
        client_visits = {node: visits for node, visits in node_visits.items() if node.startswith('T')}
        sorted_clients = sorted(client_visits.items(), key=lambda x: x[1], reverse=True)
        ranking_data = [
            {"rank": i+1, "client_node": node, "visits": visits}
            for i, (node, visits) in enumerate(sorted_clients[:10])
        ]
        return {
            "ranking": ranking_data,
            "total_clients_visited": len(client_visits),
            "total_visits": sum(client_visits.values())
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error obteniendo ranking de clientes: {str(e)}")

@router.get("/reports/visits/recharges")
async def get_recharge_visits_ranking():
    """Obtener ranking de estaciones de recarga más visitadas"""
    if not shared_data_manager.is_initialized():
        raise HTTPException(status_code=400, detail="Simulación no inicializada. Inicialice la simulación desde el dashboard primero.")
    try:
        node_visits = shared_data_manager.get_node_visits() or {}
        recharge_visits = {node: visits for node, visits in node_visits.items() if node.startswith('C')}
        sorted_recharges = sorted(recharge_visits.items(), key=lambda x: x[1], reverse=True)
        ranking_data = [
            {"rank": i+1, "recharge_node": node, "visits": visits}
            for i, (node, visits) in enumerate(sorted_recharges[:10])
        ]
        return {
            "ranking": ranking_data,
            "total_recharges_visited": len(recharge_visits),
            "total_visits": sum(recharge_visits.values())
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error obteniendo ranking de recargas: {str(e)}")

@router.get("/reports/visits/storages")
async def get_storage_visits_ranking():
    """Obtener ranking de almacenes más visitados"""
    if not shared_data_manager.is_initialized():
        raise HTTPException(status_code=400, detail="Simulación no inicializada. Inicialice la simulación desde el dashboard primero.")
    try:
        node_visits = shared_data_manager.get_node_visits() or {}
        storage_visits = {node: visits for node, visits in node_visits.items() if node.startswith('S')}
        sorted_storages = sorted(storage_visits.items(), key=lambda x: x[1], reverse=True)
        ranking_data = [
            {"rank": i+1, "storage_node": node, "visits": visits}
            for i, (node, visits) in enumerate(sorted_storages[:10])
        ]
        return {
            "ranking": ranking_data,
            "total_storages_visited": len(storage_visits),
            "total_visits": sum(storage_visits.values())
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error obteniendo ranking de almacenes: {str(e)}")

@router.get("/reports/summary")
async def get_system_summary():
    """Obtener resumen general del sistema"""
    if not shared_data_manager.is_initialized():
        raise HTTPException(status_code=400, detail="Simulación no inicializada. Inicialice la simulación desde el dashboard primero.")
    try:
        summary = shared_data_manager.get_simulation_summary()
        return summary
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error obteniendo resumen del sistema: {str(e)}") 