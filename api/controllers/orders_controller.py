"""
Controlador para endpoints de órdenes
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
async def get_orders():
    """Obtener lista de todas las órdenes"""
    if not shared_data_manager.is_initialized():
        raise HTTPException(status_code=404, detail="No hay órdenes disponibles. Inicialice la simulación desde el dashboard primero.")
    
    try:
        orders = shared_data_manager.get_orders()
        if not orders:
            raise HTTPException(status_code=404, detail="No hay órdenes disponibles. Inicialice la simulación desde el dashboard primero.")
        
        return {
            "orders": orders,
            "total_count": len(orders)
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error obteniendo órdenes: {str(e)}")

@router.get("/orders/{order_id}")
async def get_order(order_id: str):
    """Obtener información de una orden específica"""
    if not shared_data_manager.is_initialized():
        raise HTTPException(status_code=404, detail="No hay órdenes disponibles. Inicialice la simulación desde el dashboard primero.")
    
    try:
        # Buscar la orden por ID
        order = shared_data_manager.get_order_by_id(order_id)
        
        if not order:
            raise HTTPException(status_code=404, detail=f"Orden con ID '{order_id}' no encontrada")
        
        return order
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error obteniendo orden: {str(e)}")

@router.post("/orders/orders/{order_id}/cancel")
async def cancel_order(order_id: str):
    """Cancelar una orden específica"""
    if not shared_data_manager.is_initialized():
        raise HTTPException(status_code=404, detail="No hay órdenes disponibles. Inicialice la simulación desde el dashboard primero.")
    try:
        order = shared_data_manager.get_order_by_id(order_id)
        if not order:
            raise HTTPException(status_code=404, detail=f"Orden con ID '{order_id}' no encontrada")
        if order.get('status', 'Pendiente') == 'Cancelada':
            raise HTTPException(status_code=400, detail=f"La orden '{order_id}' ya está cancelada")
        # Actualizar estado en el JSON
        updated = shared_data_manager.set_order_status(order_id, 'Cancelada')
        if not updated:
            raise HTTPException(status_code=500, detail=f"No se pudo cancelar la orden '{order_id}'")
        return {
            "message": f"Orden '{order_id}' cancelada exitosamente",
            "order_id": order_id,
            "status": "Cancelada"
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error cancelando orden: {str(e)}")

@router.post("/orders/orders/{order_id}/complete")
async def complete_order(order_id: str):
    """Completar una orden específica"""
    if not shared_data_manager.is_initialized():
        raise HTTPException(status_code=404, detail="No hay órdenes disponibles. Inicialice la simulación desde el dashboard primero.")
    try:
        order = shared_data_manager.get_order_by_id(order_id)
        if not order:
            raise HTTPException(status_code=404, detail=f"Orden con ID '{order_id}' no encontrada")
        if order.get('status', 'Pendiente') == 'Completada':
            raise HTTPException(status_code=400, detail=f"La orden '{order_id}' ya está completada")
        # Actualizar estado en el JSON
        updated = shared_data_manager.set_order_status(order_id, 'Completada')
        if not updated:
            raise HTTPException(status_code=500, detail=f"No se pudo completar la orden '{order_id}'")
        return {
            "message": f"Orden '{order_id}' completada exitosamente",
            "order_id": order_id,
            "status": "Completada"
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error completando orden: {str(e)}") 