


````markdown
# Proyecto de Análisis de Datos y Modelado Híbrido

Este repositorio contiene el código fuente para el análisis econométrico y modelado predictivo de series temporales y datos de panel. El proyecto combina técnicas estadísticas clásicas con algoritmos de Machine Learning y Deep Learning.

## 📋 Características del Proyecto

El flujo de trabajo incluye:
1.  **Diagnóstico Econométrico:** Análisis de Efectos Fijos (Fixed Effects) para identificar variables significativas en datos de panel.
2.  **Preprocesamiento Avanzado:** Imputación iterativa (`IterativeImputer`) y escalado adaptativo.
3.  **Modelado Comparativo:**
    * **Random Forest:** Para capturar no-linealidades tabulares.
    * **XGBoost:** Optimizado con un *Wrapper* personalizado para estabilidad en diferentes arquitecturas.
    * **LSTM (Deep Learning):** Redes recurrentes para capturar dependencias secuenciales complejas.
    * **Ridge:** Modelo de regularización aplicado a una propuesta de modelos híbrido.
4.  **Validación Robusta:** Uso de `TimeSeriesSplit` para respetar la temporalidad de los datos durante el entrenamiento.

## ⚙️ Instalación y Configuración

Este proyecto fue desarrollado utilizando **Python 3.9**. Para garantizar la reproducibilidad de los resultados, se recomienda crear un entorno virtual limpio.

### 1. Clonar el repositorio
```bash
git clone <URL_DE_TU_REPOSITORIO>
cd <NOMBRE_DE_LA_CARPETA>
````

### 2\. Crear entorno virtual (Recomendado)

Se recomienda usar **Conda** para gestionar las dependencias de sistema, especialmente en macOS:

```bash
conda create -n proyecto_ds python=3.9
conda activate proyecto_ds
```

### 3\. Instalar dependencias

El archivo `requirements.txt` incluye **Marcadores de Entorno** inteligentes. Detectará automáticamente tu sistema operativo e instalará las versiones correctas (incluyendo aceleración GPU si estás en Mac).

```bash
pip install -r requirements.txt
```

-----

## 🛠️ Notas Técnicas Importantes

### 🍎 Compatibilidad con Apple Silicon (M1/M2/M3)

Este proyecto fue desarrollado nativamente en arquitectura ARM64 (Mac).

  * **TensorFlow:** El instalador configurará automáticamente `tensorflow-metal` si detecta un chip Apple Silicon para habilitar la aceleración por GPU. En Windows/Linux, instalará la versión estándar de CPU/GPU compatible.
  * **Advertencias:** Es normal ver advertencias de `TensorFlow` en la consola relacionadas con optimizadores "Plugin" en Mac; estas no afectan el rendimiento del modelo.

### 🛡️ Wrapper de XGBoost (`SafeXGBRegressor`)

Debido a actualizaciones recientes en `scikit-learn` (v1.6+), se implementó una clase personalizada `SafeXGBRegressor` dentro del código.

  * **Propósito:** Actúa como un puente de compatibilidad entre la API moderna de Scikit-Learn y XGBoost.
  * **Funcionamiento:** Permite la optimización de hiperparámetros (Grid/Random Search) sin conflictos de versiones, asegurando que el código sea ejecutable tanto en entornos antiguos como modernos sin modificaciones manuales.

## 🚀 Uso

1.  Asegúrese de tener el archivo de datos `Data_final.csv` en la raíz del proyecto o accesible vía URL (el código maneja ambas opciones).
2.  Ejecute el Notebook principal o el script de Python.
3.  Los resultados mostrarán las métricas comparativas (MAE, RMSE, R2) para todos los modelos evaluados.

## 📦 Requerimientos Principales

  * Python 3.9
  * TensorFlow \>= 2.16
  * Scikit-Learn \>= 1.0
  * XGBoost 2.1.4
  * Pandas, Numpy, Matplotlib, Seaborn

<!-- end list -->
