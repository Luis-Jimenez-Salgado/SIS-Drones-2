"""
Controlador para endpoints de clientes
"""

from fastapi import APIRouter, HTTPException
from typing import List, Dict, Optional
import sys
import os

# Agregar el directorio raíz al path para importar módulos
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from src.shared_data import shared_data_manager

router = APIRouter()

@router.get("/")
async def get_clients():
    """Obtener lista de todos los clientes"""
    if not shared_data_manager.is_initialized():
        raise HTTPException(status_code=404, detail="No hay clientes disponibles. Inicialice la simulación desde el dashboard primero.")
    
    try:
        clients = shared_data_manager.get_clients()
        if not clients:
            raise HTTPException(status_code=404, detail="No hay clientes disponibles. Inicialice la simulación desde el dashboard primero.")
        
        return {
            "clients": clients,
            "total_count": len(clients)
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error obteniendo clientes: {str(e)}")

@router.get("/{client_id}")
async def get_client(client_id: str):
    """Obtener información de un cliente específico"""
    if not shared_data_manager.is_initialized():
        raise HTTPException(status_code=404, detail="No hay clientes disponibles. Inicialice la simulación desde el dashboard primero.")
    
    try:
        # Buscar el cliente por ID
        client = shared_data_manager.get_client_by_id(client_id)
        
        if not client:
            raise HTTPException(status_code=404, detail=f"Cliente con ID '{client_id}' no encontrado")
        
        return client
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error obteniendo cliente: {str(e)}") 