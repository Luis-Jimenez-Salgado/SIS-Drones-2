# 🚁 Sistema Logístico de Drones Fase 2

Sistema logístico autónomo con drones que incluye visualización geoespacial, optimización de rutas, API RESTful y generación de informes.

## 🎯 Características Principales

- **🌍 Visualización Geoespacial**: Mapa interactivo con Folium
- **🛣️ Optimización de Rutas**: Algoritmos Dijkstra y MST (Kruskal)
- **🌐 API RESTful**: Endpoints para clientes, órdenes y reportes
- **📊 Dashboard Interactivo**: Interfaz Streamlit con 5 pestañas
- **📄 Generación de PDF**: Informes automáticos desde app y API
- **⚡ Rendimiento Optimizado**: Acceso O(1) con hash maps
- **📈 Análisis Estadístico**: Estadísticas avanzadas y visualizaciones

## 🚀 Instalación Rápida

### 1. Instalar Dependencias
```bash
# Opción 1: Script automático (recomendado)
py install_dependencies.py

# Opción 2: Instalación manual
py -m pip install -r requirements.txt
```

### 2. Ejecutar el Sistema

#### Opción A: Script Automático (Recomendado)
```bash
# Ejecutar Dashboard y API simultáneamente
py run_system.py both

# Solo Dashboard
py run_system.py dashboard

# Solo API
py run_system.py api
```

#### Opción B: Comandos Manuales
```bash
# Terminal 1: Dashboard
streamlit run main.py

# Terminal 2: API
uvicorn api.main:app --reload --host 0.0.0.0 --port 8000
```

## 🌐 URLs de Acceso

- **Dashboard**: http://localhost:8501
- **API**: http://localhost:8000
- **Documentación API**: http://localhost:8000/docs

## 📋 Estructura del Proyecto

```
SIS-Drones-2/
├── api/                    # API RESTful
│   ├── main.py            # Entrada principal de la API
│   └── controllers/       # Controladores de endpoints
├── src/
│   ├── domain/           # Entidades del dominio
│   ├── model/            # Modelos de datos y algoritmos
│   ├── sim/              # Simulación y gestión
│   ├── tda/              # Estructuras de datos (AVL, Map)
│   ├── visual/           # Visualización y dashboard
│   └── shared_data.py    # Datos compartidos entre componentes
├── main.py               # Entrada principal del dashboard
├── install_dependencies.py # Script de instalación
├── run_system.py         # Script de ejecución
└── requirements.txt      # Dependencias del proyecto
```

## 🔧 Funcionalidades del Dashboard

### 📊 Pestaña 1: Run Simulation
- Configuración de parámetros de simulación
- Generación de grafos aleatorios
- Validación de parámetros

### 🌍 Pestaña 2: Explore Network
- Visualización en mapa real (Temuco)
- Cálculo de rutas con algoritmos de optimización
- Visualización de MST (Kruskal)
- Animación de recorridos

### 👥 Pestaña 3: Clients & Orders
- Lista de clientes con detalles
- Gestión de órdenes
- Información de rutas asociadas

### 📈 Pestaña 4: Route Analytics
- Análisis de rutas frecuentes
- Visualización de árbol AVL
- Generación de informes PDF

### 📊 Pestaña 5: General Statistics
- Estadísticas visuales
- Distribución de nodos por tipo
- Gráficos interactivos

## 🌐 Endpoints de la API

### Clientes
- `GET /clients/` - Lista de clientes
- `GET /clients/{client_id}` - Cliente por ID

### Órdenes
- `GET /orders/` - Lista de órdenes
- `GET /orders/orders/{order_id}` - Orden por ID
- `POST /orders/orders/{order_id}/cancel` - Cancelar orden
- `POST /orders/orders/{order_id}/complete` - Completar orden

### Informes
- `GET /reports/reports/pdf` - Generar PDF
- `GET /info/reports/visits/clients` - Ranking clientes
- `GET /info/reports/visits/recharges` - Ranking recarga
- `GET /info/reports/visits/storages` - Ranking almacenamiento
- `GET /info/reports/summary` - Resumen general

## ⚡ Optimizaciones de Rendimiento

### Hash Maps (Map)
- Acceso O(1) a clientes y órdenes por ID
- Implementación propia en `src/tda/Map.py`
- Sincronización automática con datos JSON

### Estructuras de Datos
- **AVL Tree**: Para estadísticas de rutas
- **Graph**: Para modelado de red de transporte
- **Hash Maps**: Para acceso rápido a entidades

## 🧪 Pruebas y Validación

### Casos de Prueba
- Simulación con 15-150 nodos
- Cálculo de rutas con autonomía (50 unidades)
- Generación de informes PDF
- Endpoints de API

### Validaciones
- Conectividad de grafos garantizada
- Respeto a límites de autonomía
- Distribución correcta de roles (20%📦, 20%🔋, 60%👤)

## 🛠️ Solución de Problemas

### Error: "streamlit no encontrado"
```bash
py install_dependencies.py
```

### Error: "uvicorn no encontrado"
```bash
py install_dependencies.py
```

### Problemas de puertos ocupados
```bash
# Cambiar puerto del dashboard
streamlit run main.py --server.port 8502

# Cambiar puerto de la API
uvicorn api.main:app --port 8001
```

### Problemas de dependencias
```bash
# Actualizar pip
py -m pip install --upgrade pip

# Reinstalar dependencias
py install_dependencies.py
```

## 📊 Parámetros de Simulación

- **Nodos**: 10-150 (20% almacenamiento, 20% recarga, 60% clientes)
- **Aristas**: 10-300
- **Órdenes**: 10-500
- **Autonomía**: 50 unidades de costo
- **Recarga**: Forzada cuando se excede autonomía

## 🤝 Contribución

1. Fork el proyecto
2. Crea una rama para tu feature (`git checkout -b feature/AmazingFeature`)
3. Commit tus cambios (`git commit -m 'Add some AmazingFeature'`)
4. Push a la rama (`git push origin feature/AmazingFeature`)
5. Abre un Pull Request

## 📄 Licencia

Este proyecto está bajo la Licencia MIT. Ver el archivo `LICENSE` para más detalles.

## 📞 Soporte

Para soporte técnico o preguntas sobre el proyecto:
- Revisar la documentación de la API en http://localhost:8000/docs
- Consultar los logs de ejecución
- Verificar la configuración de dependencias

---

**Desarrollado para INFO 1126 - Programación 3**