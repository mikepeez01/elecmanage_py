# Sistema de Gestión y Automatización Energética

## 📋 Descripción del Proyecto

Sistema automatizado desarrollado en Python para la gestión energética y asesoramiento en el mercado eléctrico español. El proyecto integra múltiples fuentes de datos para proporcionar análisis, informes y herramientas de apoyo a la toma de decisiones en el sector energético.

### Funcionalidades Principales

- **Compilación y procesamiento de facturas** eléctricas (XML/PDF)
- **Consolidación de curvas de carga** de múltiples proveedores
- **Análisis de contratos** y condiciones de suministro
- **Seguimiento de regulación** y componentes tarifarios
- **Informes de mercado** con precios spot y futuros
- **Verificación automática** de facturación
- **Generación de informes** personalizados por cliente

## 🏗️ Arquitectura del Sistema

El proyecto está organizado en una estructura modular que facilita el mantenimiento y la escalabilidad:

├── src/ # Módulos y librerías Python
├── notebooks/ # Notebooks Jupyter para análisis
│ └── elec/ # Notebooks específicos de electricidad
├── data/ # Datos de entrada (no incluidos)
│ ├── raw/ # Datos brutos
│ ├── processed/ # Datos procesados
│ ├── customers/ # Información de clientes
│ └──
└── outputs/ # Resultados y informes generados
├── market_report/ # Informes de mercado
├── load_compilation/ # Compilación de cargas
└── invoice/ # Gestión de facturas


## 🛠️ Tecnologías Utilizadas

- **Python 3.x** - Lenguaje principal de desarrollo
- **Jupyter Notebooks** - Análisis interactivo y documentación
- **Papermill** - Automatización y parametrización de notebooks
- **Pandas** - Manipulación y análisis de datos
- **Matplotlib/Plotly** - Visualización de datos
- **SQLite** - Base de datos para facturas procesadas

## 📂 Configuración de Rutas

El archivo `config.yaml` contiene todas las rutas relevantes del proyecto, facilitando la organización y acceso a los diferentes recursos. La estructura está diseñada para soportar múltiples clientes y subproyectos de forma independiente.

## 🚀 Instalación y Configuración

### Prerrequisitos

- Python 3.12 o superior
- pip (gestor de paquetes de Python)

### Instalación de Dependencias

pip install -e .

### Estructura de Datos Esperada

Por motivos de confidencialidad, este repositorio **no incluye datos reales de clientes**. Para el funcionamiento del sistema, se requiere la siguiente estructura de datos:

#### Datos de Entrada (`data/`)
- **Facturas:** Archivos XML o PDF de facturas eléctricas
- **Curvas de carga:** Archivos en formato xlsx, csv, html o parquet
- **Contratos:** Información contractual en plantillas Excel estandarizadas
- **Regulación:** Archivos con peajes, cargos e impuestos vigentes
- **Puntos de suministro:** Archivo maestro con información de CUPS y tarifas (`data/customers/elec_data_clientes_elec.xlsx`)

#### Datos Procesados (`data/processed/`)
- Base de datos de facturas (`facturas_elec.db`)
- Curvas consolidadas (`elec_load.parquet`)
- Precios spot y futuros (`spot.parquet`, `futuros_elec.parquet`)

## 📊 Uso del Sistema

### Ejecución de Notebooks

Los notebooks se ejecutan mediante Papermill para garantizar reproducibilidad.

## ⚡ Subproyectos

### 1. Invoice Compilation
- Procesamiento automático de facturas XML y PDF
- Estandarización de datos de facturación
- Base de datos centralizada de información

### 2. Load Compilation
- Consolidación de curvas de carga horarias y cuarto-horarias
- Integración de datos de múltiples proveedores
- Análisis de consumo por cliente y tarifa

### 3. Market Report
- Informes periódicos del mercado eléctrico
- Análisis de precios spot y futuros
- Gráficos y visualizaciones de tendencias

### 4. Verification Project
- Verificación automática de facturación
- Detección de anomalías y discrepancias
- Informes de control y seguimiento

### Generación de Informes

Los informes se generan automáticamente en la carpeta `outputs/` organizados por:
- Tipo de informe
- Cliente
- Fecha de generación

## 📈 Outputs del Sistema

### Informes Generados
- **Seguimiento de facturación** por cliente
- **Archivo de curvas de carga** consolidadas
- **Verificaciones automáticas** de facturación en formato pdf
- **Gráficos analíticos** de consumo y precios

### Formatos de Salida
- Excel (.xlsx)
- PDF para informes finales
- HTML para visualizaciones interactivas
- Parquet para grandes volúmenes de datos

## 🔒 Consideraciones de Privacidad

Este proyecto maneja información sensible de clientes y datos comerciales. Por este motivo:

- **No se incluyen datos reales** en el repositorio público
- La estructura está preparada para datos que cumplan los formatos especificados
- Se recomienda implementar medidas adicionales de seguridad en entornos productivos

## 🤝 Contribución

Para contribuir al proyecto:

1. Fork del repositorio
2. Crear una rama para la nueva funcionalidad
3. Realizar commits con mensajes descriptivos
4. Enviar pull request con descripción detallada


## 📧 Contacto

Mikel Pérez Yárnoz
mikelperezy01@gmail.com
+34 664 187 473

---

**Nota:** Este sistema ha sido desarrollado específicamente para el mercado eléctrico español y está adaptado a la regulación vigente. Para su uso en otros mercados, se requeriría adaptación de los módulos regulatorios.




