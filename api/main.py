"""
API RESTful para el Sistema Logístico de Drones
FastAPI con documentación automática y endpoints completos
"""

from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
import uvicorn
from typing import List, Dict, Optional
import json
import os
from datetime import datetime

# Importar controladores
from .controllers.clients_controller import router as clients_router
from .controllers.orders_controller import router as orders_router
from .controllers.reports_controller import router as reports_router
from .controllers.info_controller import router as info_router

# Crear aplicación FastAPI
app = FastAPI(
    title="Sistema Logístico de Drones API",
    description="API RESTful para gestión de drones autónomos, rutas y órdenes",
    version="2.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Configurar CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # En producción, especificar dominios específicos
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    """Endpoint raíz con información de la API"""
    return {
        "message": "🚁 Sistema Logístico de Drones API",
        "version": "2.0.0",
        "status": "active",
        "documentation": "/docs",
        "endpoints": {
            "clients": "/clients/*",
            "orders": "/orders/*",
            "reports": "/reports/*",
            "info": "/info/*"
        }
    }

@app.get("/health")
async def health_check():
    """Verificar el estado de salud de la API"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "version": "2.0.0"
    }

# Incluir rutas de los controladores
app.include_router(clients_router, prefix="/clients", tags=["Clients"])
app.include_router(orders_router, prefix="/orders", tags=["Orders"])
app.include_router(reports_router, prefix="/reports", tags=["Reports"])
app.include_router(info_router, prefix="/info", tags=["Information"])

if __name__ == "__main__":
    uvicorn.run(
        "api.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    ) 