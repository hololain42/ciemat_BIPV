"""
Este archivo instala cualquier paquete faltante y ejecuta el programa secuencialmente
"""

import sys
import os
import subprocess
import importlib.util
from pathlib import Path


def print_header(message):
    """Imprime un encabezado visual para separar secciones."""
    print("\n" + "=" * 70)
    print(f"  {message}")
    print("=" * 70)


def print_step(step_num, message):
    """Imprime un paso del proceso."""
    print(f"\n[{step_num}] {message}")


def print_success(message):
    """Imprime un mensaje de éxito."""
    print(f"✓ {message}")


def print_error(message):
    """Imprime un mensaje de error."""
    print(f"✗ ERROR: {message}")


def print_warning(message):
    """Imprime una advertencia."""
    print(f"⚠ ADVERTENCIA: {message}")


def check_python_version(min_version=(3, 7)):
    """Verifica que la versión de Python sea compatible."""
    print_step(1, "Verificando versión de Python...")
    current_version = sys.version_info[:2]
    
    if current_version >= min_version:
        print_success(f"Python {current_version[0]}.{current_version[1]} detectado (mínimo requerido: {min_version[0]}.{min_version[1]})")
        return True
    else:
        print_error(f"Se requiere Python {min_version[0]}.{min_version[1]} o superior. Versión actual: {current_version[0]}.{current_version[1]}")
        return False


def check_requirements_file():
    """Verifica que existe el archivo requirements.txt."""
    print_step(2, "Buscando archivo de requisitos...")
    
    if not os.path.exists("requirements.txt"):
        print_warning("No se encontró requirements.txt. Continuando sin verificar dependencias.")
        return True
    
    print_success("Archivo requirements.txt encontrado")
    return True


def check_installed_packages():
    """Verifica e instala los paquetes necesarios."""
    print_step(3, "Verificando paquetes instalados...")
    
    if not os.path.exists("requirements.txt"):
        return True
    
    try:
        # Leer requirements.txt
        with open("requirements.txt", "r") as f:
            requirements = [line.strip() for line in f if line.strip() and not line.startswith("#")]
        
        missing_packages = []
        
        # Mapeo de nombres especiales
        PACKAGE_MAP = {
            "scikit-learn": "sklearn",
        }
        
        # Verificar cada paquete
        for req in requirements:
            # Extraer nombre del paquete (antes de ==, >=, etc.)
            package_name = req.split("==")[0].split(">=")[0].split("<=")[0].split("~=")[0].strip()
            
            # Obtener el nombre correcto para importar
            import_name = PACKAGE_MAP.get(package_name, package_name.replace("-", "_"))
            
            # Intentar importar el paquete
            spec = importlib.util.find_spec(import_name)
            
            if spec is None:
                missing_packages.append(req)
                print(f"  ✗ {package_name} - NO INSTALADO")
            else:
                print(f"  ✓ {package_name} - Instalado")
        
        if missing_packages:
            print_warning(f"Faltan {len(missing_packages)} paquete(s)")
            print("\n¿Deseas instalar los paquetes faltantes automáticamente? (s/n): ", end="")
            
            respuesta = input().strip().lower()
            
            if respuesta in ["s", "si", "sí", "y", "yes"]:
                print("\nInstalando paquetes faltantes...")
                try:
                    subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
                    print_success("Paquetes instalados correctamente")
                    return True
                except subprocess.CalledProcessError:
                    print_error("Error al instalar paquetes. Instálalos manualmente con: pip install -r requirements.txt")
                    return False
            else:
                print_error("No se pueden ejecutar los scripts sin los paquetes necesarios")
                print("Instala los paquetes manualmente con: pip install -r requirements.txt")
                return False
        else:
            print_success("Todos los paquetes están instalados")
            return True
            
    except Exception as e:
        print_error(f"Error al verificar paquetes: {e}")
        return False


def execute_script(script_name):
    """Ejecuta un script de Python y maneja errores."""
    print_header(f"EJECUTANDO SCRIPT: {script_name}")
    
    try:
        # Ejecutar el script como módulo
        result = subprocess.run(
            [sys.executable, str(script_name)],
            capture_output=False,
            text=True,
            check=True
        )
        
        print_success(f"{script_name} completado exitosamente")
        return True
        
    except subprocess.CalledProcessError as e:
        print_error(f"Error al ejecutar {script_name}")
        print(f"Código de salida: {e.returncode}")
        return False
    except Exception as e:
        print_error(f"Error inesperado al ejecutar {script_name}: {e}")
        return False



def main():
    """Función principal del launcher."""
    print_header("INICIANDO EJECUCIÓN DEL PROGRAMA")
    
    SCRIPT_FILES = [
        "Produccion_anual.py",
    ]
    
    # Verificaciones previas
    if not check_python_version(min_version=(3, 7)):
        sys.exit(1)
    
    if not check_requirements_file():
        sys.exit(1)
    
    if not check_installed_packages():
        sys.exit(1)
    
    print_header("TODAS LAS VERIFICACIONES COMPLETADAS ✓")

    # Solicitar parámetro de tiempo de submuestreo
    print("\n" + "-" * 70)
    print("CONFIGURACIÓN DE PARÁMETROS")
    print("-" * 70)
    
    while True:
        try:
            tiempo_submuestreo = input("\nIntroduce el tiempo de submuestreo (en minutos): ").strip()
            tiempo_submuestreo = int(tiempo_submuestreo)
            
            if tiempo_submuestreo > 0:
                print_success(f"Tiempo de submuestreo configurado: {tiempo_submuestreo} minutos")
                break
            else:
                print_error("El tiempo debe ser un número positivo")
        except ValueError:
            print_error("Por favor, introduce un número válido")
    
    # Guardar el parámetro para que los scripts lo puedan usar
    os.environ['TIEMPO_SUBMUESTREO'] = str(tiempo_submuestreo)

    
    # Ejecutar scripts secuencialmente    
    for script in SCRIPT_FILES:
        if not execute_script(script):
            print_header("EJECUCIÓN INTERRUMPIDA POR ERROR")
            sys.exit(1)
    
    # Éxito
    print_header("¡PROCESO COMPLETADO EXITOSAMENTE! ✓")
    print("\nTodos los scripts se ejecutaron correctamente.")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n")
        print_header("EJECUCIÓN CANCELADA POR EL USUARIO")
        sys.exit(1)
    except Exception as e:
        print("\n\n")
        print_error(f"Error inesperado: {e}")
        sys.exit(1)