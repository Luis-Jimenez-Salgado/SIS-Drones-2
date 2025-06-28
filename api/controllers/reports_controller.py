"""
Controlador para endpoints de informes
"""

from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse
import sys
import os
from datetime import datetime

# Agregar el directorio raíz al path para importar módulos
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from src.shared_data import shared_data_manager
from src.visual.report_generator import ReportGenerator

router = APIRouter()

@router.get("/reports/pdf")
async def generate_pdf_report():
    """Generar informe PDF con datos de la simulación"""
    if not shared_data_manager.is_initialized():
        raise HTTPException(status_code=400, detail="Simulación no inicializada. Inicialice la simulación desde el dashboard primero.")
    
    try:
        # Obtener datos de la simulación
        graph = shared_data_manager.get_graph()  # Ahora reconstruye el grafo real
        clients = shared_data_manager.get_clients()
        orders = shared_data_manager.get_orders()
        routes = shared_data_manager.get_routes()
        
        # Crear generador de informes
        report_generator = ReportGenerator()
        
        # Generar PDF usando exactamente la misma llamada que el dashboard
        output_path = f"reporte_api_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
        pdf_filename = report_generator.generate_report(
            graph=graph,
            orders=orders,
            clients=clients,
            routes=routes,
            output_path=output_path
        )
        
        if pdf_filename and os.path.exists(pdf_filename):
            return FileResponse(
                pdf_filename,
                media_type='application/pdf',
                filename='informe_drones.pdf'
            )
        else:
            raise HTTPException(status_code=500, detail="Error generando el archivo PDF")
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generando informe PDF: {str(e)}") 