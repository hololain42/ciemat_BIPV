# Proyecto de Prácticas en Empresa del Máster en Energía de la UCM

Proyecto de análisis de datos para ajustar del modelo de temperatura de Ross en sistemas BIPV con módulos fotovoltaicos serigrafiados

## 📋 Requisitos Previos

- **Python 3.7 o superior** instalado en tu sistema
- Conexión a Internet (para instalar paquetes si es necesario)


Si no tienes Python instalado, descárgalo desde [python.org](https://www.python.org/downloads/)

## 🚀 Uso del programa

### Desde Visual Studio Code (VSCode)

1. **Abre el proyecto en VSCode**
   - Abre VSCode
   - Ve a `Archivo` → `Abrir carpeta...`
   - Selecciona la carpeta del proyecto

2. **Abre el archivo `run.py`**
   - En el explorador de archivos de VSCode (panel izquierdo)
   - Haz clic en `run.py`

3. **Ejecuta el archivo**
   - Haz clic en el **botón de play ▶** en la esquina superior derecha
   - O presiona `Ctrl + F5` (Windows/Linux) o `Cmd + F5` (Mac)
   - O haz clic derecho en el archivo → `Ejecutar archivo Python en la terminal`

4. **Sigue las instrucciones en la terminal integrada**
   - La terminal aparecerá en la parte inferior de VSCode
   - El programa verificará automáticamente todos los requisitos
   - Si falta algún paquete, te preguntará si quieres instalarlo (escribe `s` y presiona Enter)
   - Te pedirá el parámetro de tiempo de submuestreo
   - Ejecutará todos los scripts secuencialmente y guardará los resultados en los directorios adecuados

> **💡 Consejo**: Si VSCode te pregunta qué intérprete de Python usar, selecciona la versión más reciente (ej: Python 3.11 o superior)

### Opción 2: Desde la Terminal/Símbolo del Sistema

1. **Descarga o clona este repositorio**
   ```bash
   git clone https://github.com/hololain42/ciemat_BIPV.git
   cd ciemat_BIPV
   ```

2. **Ejecuta el script principal**
   
   **En Windows:**
   ```bash
   python run.py
   ```
   
   **En Mac/Linux:**
   ```bash
   python3 run.py
   ```
   O si tienes permisos de ejecución:
   ```bash
   ./run.py
   ```

3. **Sigue las instrucciones en pantalla**
   - El programa verificará automáticamente todos los requisitos
   - Si falta algún paquete, te preguntará si quieres instalarlo
   - Te pedirá el parámetro de tiempo de submuestreo
   - Ejecutará todos los scripts secuencialmente y guardará los resultados en los directorios adecuados

### Opción 3: Instalación Manual de Dependencias

Si prefieres instalar las dependencias manualmente antes de ejecutar:

```bash
pip install -r requirements.txt
python run.py
```

## 📦 Dependencias

El proyecto utiliza las siguientes librerías de Python:

- **chardet** ≥ 5.2.0 - Detección de codificación de archivos
- **matplotlib** ≥ 3.10.0 - Visualización de gráficos
- **numpy** ≥ 2.3.0 - Operaciones numéricas
- **pandas** ≥ 2.3.0 - Análisis de datos
- **pvlib** ≥ 0.13.0 - Modelado de sistemas fotovoltaicos
- **scikit-learn** ≥ 1.7.0 - Machine learning y análisis estadístico
- **scipy** ≥ 1.16.0 - Computación científica

Todas las dependencias se instalarán automáticamente al ejecutar `run.py`.

## 📂 Estructura del Proyecto

```
proyecto/
│
├── run.py                        # ⭐ Script principal de ejecución
├── requirements.txt              # Lista de dependencias
├── README.md                     # Este archivo
├── .gitignore                    # Archivos ignorados por Git
│
├── Produccion_anual.py           # Análisis de producción anual
├── Data.py                       # Procesamiento de datos
├── DatPlots.py                   # Generación de gráficos de datos
├── Energy and PR.py              # Cálculo de energía y Performance Ratio
├── Filter.py                     # Filtrado de datos
├── histograma_irradiacion.py    # Histogramas de irradiación
├── RossModel_fitting.py          # Ajuste del modelo Ross
├── submuestreo.py                # Submuestreo de datos
├── exportar_dataframe.py         # Exportación de dataframes
│
├── Datos Datalogger/             # 📁 Datos de entrada del datalogger
├── Excel Resultados/             # 📁 Resultados exportados en Excel
├── figuras/                      # 📁 Gráficos generados
└── __pycache__/                  # Archivos temporales de Python (auto-generados)
```

## ⚙️ Parámetros de Configuración

Durante la ejecución, el programa te solicitará:

- **Tiempo de submuestreo**: Intervalo temporal (en minutos) para el procesamiento de datos

## 🔧 Solución de Problemas

### Error: "python no se reconoce como comando"

**Windows:**
- Asegúrate de que Python esté en las variables de entorno PATH
- Intenta usar `py` en lugar de `python`

**Mac/Linux:**
- Usa `python3` en lugar de `python`

### Error: "Permission denied" (Mac/Linux)

Da permisos de ejecución al script:
```bash
chmod +x run.py
```

### Los paquetes no se instalan correctamente

Instala manualmente con:
```bash
pip install -r requirements.txt
```

Si persiste el error, actualiza pip:
```bash
python -m pip install --upgrade pip
```

### Error con scikit-learn

Si el sistema no reconoce `scikit-learn`:
```bash
pip uninstall scikit-learn
pip install scikit-learn
```

## 📊 Resultados

Los resultados del análisis se guardarán en:

- `Datos Datalogger/` - Datos de entrada del datalogger
- `Excel Resultados/` - Resultados exportados en Excel
- `figuras/`          - 📁 Gráficos generados

## 👥 Autor

Zayd Isaac Valdez Lema, Manuel Rodrigo Rivero y Nuria Martín Chivelet

## 📄 Licencia

© 2025 - Proyecto desarrollado durante prácticas en empresa en CIEMAT 
Todos los derechos reservados.

## 📞 Contacto

Para dudas o problemas con el código, contacta a [manrod22@ucm.es]

---

## 🆘 ¿Necesitas Ayuda?

Si tienes problemas ejecutando el proyecto:

1. Verifica que Python 3.7+ esté instalado
2. Asegúrate de estar en el directorio correcto del proyecto
3. Lee los mensajes de error que muestra `run.py`
4. Revisa la sección de Solución de Problemas arriba

---

**Última actualización**: Octubre 2025