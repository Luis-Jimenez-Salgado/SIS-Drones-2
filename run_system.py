#!/usr/bin/env python3
"""
Script para ejecutar el Sistema Logístico de Drones
Permite ejecutar el Dashboard, la API, o ambos simultáneamente
"""

import subprocess
import sys
import time
import os
import signal
import threading
from pathlib import Path

def run_dashboard():
    """Ejecuta el dashboard Streamlit"""
    print("🚀 Iniciando Dashboard Streamlit...")
    print("📊 URL: http://localhost:8501")
    try:
        subprocess.run(["streamlit", "run", "main.py"], check=True)
    except KeyboardInterrupt:
        print("\n🛑 Dashboard detenido por el usuario")
    except FileNotFoundError:
        print("❌ Error: streamlit no encontrado. Ejecuta: py install_dependencies.py")
    except Exception as e:
        print(f"❌ Error ejecutando dashboard: {e}")

def run_api():
    """Ejecuta la API FastAPI"""
    print("🚀 Iniciando API FastAPI...")
    print("🌐 URL: http://localhost:8000")
    print("📚 Documentación: http://localhost:8000/docs")
    try:
        subprocess.run([
            "uvicorn", "api.main:app", 
            "--reload", 
            "--host", "0.0.0.0", 
            "--port", "8000"
        ], check=True)
    except KeyboardInterrupt:
        print("\n🛑 API detenida por el usuario")
    except FileNotFoundError:
        print("❌ Error: uvicorn no encontrado. Ejecuta: py install_dependencies.py")
    except Exception as e:
        print(f"❌ Error ejecutando API: {e}")

def run_both():
    """Ejecuta tanto el dashboard como la API en procesos separados"""
    print("🚀 Iniciando sistema completo...")
    print("📊 Dashboard: http://localhost:8501")
    print("🌐 API: http://localhost:8000")
    print("📚 Documentación API: http://localhost:8000/docs")
    print("\n💡 Presiona Ctrl+C para detener ambos servicios")
    
    # Iniciar API en un hilo separado
    api_thread = threading.Thread(target=run_api, daemon=True)
    api_thread.start()
    
    # Esperar un momento para que la API inicie
    time.sleep(3)
    
    # Iniciar dashboard en el hilo principal
    try:
        run_dashboard()
    except KeyboardInterrupt:
        print("\n🛑 Deteniendo sistema completo...")

def check_dependencies():
    """Verifica que las dependencias estén instaladas"""
    try:
        import streamlit
        import fastapi
        import uvicorn
        import folium
        print("✅ Dependencias verificadas")
        return True
    except ImportError as e:
        print(f"❌ Dependencias faltantes: {e}")
        print("💡 Ejecuta: py install_dependencies.py")
        return False

def show_help():
    """Muestra la ayuda del script"""
    print("=" * 60)
    print("🚁 SISTEMA LOGÍSTICO DE DRONES - EJECUTOR")
    print("=" * 60)
    print("\n📋 Uso:")
    print("  py run_system.py [opción]")
    print("\n🔧 Opciones:")
    print("  dashboard  - Ejecuta solo el Dashboard")
    print("  api        - Ejecuta solo la API")
    print("  both       - Ejecuta Dashboard y API (recomendado)")
    print("  help       - Muestra esta ayuda")
    print("\n🌐 URLs de acceso:")
    print("  Dashboard: http://localhost:8501")
    print("  API: http://localhost:8000")
    print("  Documentación API: http://localhost:8000/docs")
    print("\n💡 Ejemplos:")
    print("  py run_system.py both")
    print("  py run_system.py dashboard")
    print("  py run_system.py api")

def main():
    """Función principal"""
    # Verificar argumentos
    if len(sys.argv) < 2:
        show_help()
        return
    
    option = sys.argv[1].lower()
    
    # Verificar dependencias
    if not check_dependencies():
        return 1
    
    # Ejecutar según la opción
    if option == "dashboard":
        run_dashboard()
    elif option == "api":
        run_api()
    elif option == "both":
        run_both()
    elif option == "help":
        show_help()
    else:
        print(f"❌ Opción desconocida: {option}")
        show_help()
        return 1
    
    return 0

if __name__ == "__main__":
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        print("\n🛑 Sistema detenido por el usuario")
        sys.exit(0) 