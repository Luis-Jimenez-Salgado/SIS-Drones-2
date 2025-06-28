#!/usr/bin/env python3
"""
Script para instalar dependencias del proyecto SIS-Drones-2
Instala automáticamente todas las dependencias de requirements.txt
"""

import subprocess
import sys
import os
from pathlib import Path

def run_command(command, description):
    """Ejecuta un comando y maneja errores"""
    print(f"🔄 {description}...")
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        print(f"✅ {description} completado exitosamente")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Error en {description}: {e}")
        print(f"Error output: {e.stderr}")
        return False

def check_python_version():
    """Verifica que la versión de Python sea compatible"""
    version = sys.version_info
    print(f"🐍 Python {version.major}.{version.minor}.{version.micro}")
    
    if version.major < 3 or (version.major == 3 and version.minor < 8):
        print("❌ Se requiere Python 3.8 o superior")
        return False
    
    print("✅ Versión de Python compatible")
    return True

def install_dependencies():
    """Instala las dependencias del proyecto"""
    print("🚀 Iniciando instalación de dependencias...")
    print("=" * 50)
    
    # Verificar versión de Python
    if not check_python_version():
        return False
    
    # Verificar que requirements.txt existe
    requirements_file = Path("requirements.txt")
    if not requirements_file.exists():
        print("❌ Archivo requirements.txt no encontrado")
        return False
    
    print(f"📦 Archivo requirements.txt encontrado")
    
    # Actualizar pip
    if not run_command(f"{sys.executable} -m pip install --upgrade pip", "Actualizando pip"):
        print("⚠️  No se pudo actualizar pip, continuando...")
    
    # Instalar dependencias
    if not run_command(f"{sys.executable} -m pip install -r requirements.txt", "Instalando dependencias"):
        return False
    
    # Verificar instalación de dependencias críticas
    critical_packages = [
        "streamlit",
        "fastapi", 
        "uvicorn",
        "folium",
        "reportlab"
    ]
    
    print("\n🔍 Verificando instalación de dependencias críticas...")
    for package in critical_packages:
        try:
            __import__(package)
            print(f"✅ {package} instalado correctamente")
        except ImportError:
            print(f"❌ {package} no se pudo importar")
            return False
    
    print("\n🎉 ¡Todas las dependencias han sido instaladas exitosamente!")
    return True

def main():
    """Función principal"""
    print("=" * 60)
    print("🔧 INSTALADOR DE DEPENDENCIAS - SIS-Drones-2")
    print("=" * 60)
    
    # Cambiar al directorio del proyecto si es necesario
    script_dir = Path(__file__).parent
    if script_dir != Path.cwd():
        print(f"📁 Cambiando al directorio: {script_dir}")
        os.chdir(script_dir)
    
    if install_dependencies():
        print("\n" + "=" * 60)
        print("✅ INSTALACIÓN COMPLETADA")
        print("=" * 60)
        print("\n📋 Comandos para ejecutar el proyecto:")
        print("1. Para ejecutar el Dashboard:")
        print("   streamlit run main.py")
        print("\n2. Para ejecutar la API:")
        print("   uvicorn api.main:app --reload --host 0.0.0.0 --port 8000")
        print("\n3. Para ejecutar ambos (en terminales separadas):")
        print("   Terminal 1: streamlit run main.py")
        print("   Terminal 2: uvicorn api.main:app --reload --host 0.0.0.0 --port 8000")
        print("\n🌐 URLs de acceso:")
        print("   Dashboard: http://localhost:8501")
        print("   API: http://localhost:8000")
        print("   Documentación API: http://localhost:8000/docs")
        return 0
    else:
        print("\n" + "=" * 60)
        print("❌ INSTALACIÓN FALLIDA")
        print("=" * 60)
        print("\n💡 Soluciones posibles:")
        print("1. Verificar conexión a internet")
        print("2. Actualizar pip: python -m pip install --upgrade pip")
        print("3. Usar entorno virtual: python -m venv venv")
        print("4. Activar entorno virtual:")
        print("   - Windows: venv\\Scripts\\activate")
        print("   - Linux/Mac: source venv/bin/activate")
        return 1

if __name__ == "__main__":
    sys.exit(main()) 