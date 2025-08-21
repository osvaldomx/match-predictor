# Predicción de Resultados de la Liga MX con MLOps

<p align="center">
  <a href="https://github.com/tu_usuario/match-predictor/actions/workflows/ci.yml">
    <img src="https://github.com/tu_usuario/match-predictor/actions/workflows/ci.yml/badge.svg" alt="CI Pipeline Status">
  </a>
  <a href="https://github.com/psf/black">
    <img src="https://img.shields.io/badge/code%20style-black-000000.svg" alt="Code style: black">
  </a>
  <a href="#">
    <img src="https://img.shields.io/badge/python-3.11-blue.svg" alt="Python Version">
  </a>
  <a href="./LICENSE">
    <img src="https://img.shields.io/badge/License-GPLv3-blue.svg" alt="License: GPL-3.0">
  </a>
</p>

Este repositorio contiene un proyecto completo de Machine Learning Operations (MLOps) para predecir los resultados de los partidos de la Liga MX. El sistema se construye sobre un pipeline automatizado que abarca desde la extracción de datos mediante web scraping hasta el despliegue de un modelo interpretable como una API en un contenedor Docker.

---
## 🏗️ Estado del Proyecto

Este proyecto se está desarrollando de forma iterativa. El estado actual de cada fase es:

* **Fase 0: Configuración y Estructura:** ✅ `Completado`
* **Fase 1: Pipeline de Datos (Web Scraping):** ⏳ `En Progreso`
* **Fase 2: Análisis Exploratorio de Datos (EDA):** 📋 `Pendiente`
* **Fase 3: Entrenamiento y Optimización de Modelos:** 📋 `Pendiente`
* **Fase 4: Despliegue de API:** 📋 `Pendiente`

---
## 💻 Stack Tecnológico

* **Lenguaje:** Python 3.11
* **Gestión de Dependencias:** Poetry
* **Extracción de Datos:** Requests, BeautifulSoup4
* **Análisis y ML:** Pandas, Scikit-learn, XGBoost, SHAP
* **Framework de API:** FastAPI
* **Contenerización:** Docker
* **MLOps Tools:** MLflow, DVC
* **Pruebas y Calidad:** Pytest, Ruff, Black

---
## 🚀 Cómo Empezar

Sigue estos pasos para configurar el entorno de desarrollo en tu máquina local.

### Prerrequisitos
* Git
* Python 3.11+
* Poetry
* DVC

### Instalación

1.  **Clonar el Repositorio:**
    ```bash
    git clone [https://github.com/tu_usuario/match-predictor.git](https://github.com/tu_usuario/match-predictor.git)
    cd match-predictor
    ```

2.  **Crear y Activar el Entorno Virtual:**
    ```bash
    python -m venv venv
    source venv/bin/activate  # En Windows: venv\Scripts\activate
    ```

3.  **Configurar Poetry e Instalar Dependencias:**
    Este comando le indica a Poetry que use el entorno virtual que acabas de activar.
    ```bash
    poetry config virtualenvs.create false --local
    poetry install
    ```

4.  **Inicializar DVC:**
    Configura tu almacenamiento remoto de DVC (ej. Google Drive, S3, etc.).
    ```bash
    dvc init
    dvc remote add -d myremote gdrive://ID_DE_TU_CARPETA
    ```
---
## 📈 Uso

*(Esta sección se completará a medida que se desarrollen los pipelines de datos y entrenamiento).*

---
## 🧪 Pruebas

Para ejecutar el conjunto de pruebas unitarias y de integración, asegúrate de tener el entorno activado y ejecuta:
```bash
pytest
```
---
## 📜 Licencia
Este proyecto está bajo la Licencia MIT. Ver el archivo `LICENSE` para más detalles.