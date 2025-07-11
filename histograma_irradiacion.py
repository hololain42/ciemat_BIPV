import pandas as pd
import matplotlib.pyplot as plt


def generar_histograma_irradiacion(df, tiempo_submuestreo, meses, titulo, mostrar_grafico, col_irradiancia='Celula Calibrada Arriba'):
    """
    Genera un histograma de irradiación mensual [kWh/m2]
    
    Parámetros:
    - df: DataFrame con los datos
    - tiempo_submuestreo: tiempo en minutos entre mediciones
    - col_irradiancia: nombre de la columna con datos de irradiancia
    - mostrar_grafico: si True, muestra el gráfico; si False, solo lo genera
    
    Retorna:
    - fig: objeto Figure de matplotlib para poder guardarlo
    - irradiancia_completa: lista con los valores mensuales
    """

    # Crear una copia temporal del index solo para este cálculo (sin modificar el original)
    # Asegurar que el índice esté en formato datetime
    if not isinstance(df.index, pd.DatetimeIndex):
        temp_index = pd.to_datetime(df.index)
    else:
        temp_index = df.index  # Ya está en formato datetime

    # Calcular la irradiancia total mensual SIN modificar el DataFrame original
    irradiancia_mensual = df.groupby(temp_index.month)[col_irradiancia].sum()

    # Pasamos a kWh/m2
    irradiancia_mensual = irradiancia_mensual * (tiempo_submuestreo/60) * (1/1000)

    # Crear el gráfico
    fig = plt.figure(figsize=(10, 6))
    fig.canvas.manager.set_window_title('Irradiación célula calibrada arriba')

    # Definimos objeto ax para distinguir entre figuras
    ax = fig.add_subplot(111)

    # Asegurar que tenemos datos para todos los meses (llenar con 0 si faltan)
    irradiancia_completa = []
    for mes in range(1, len(meses)+1):
        if mes in irradiancia_mensual.index:
            irradiancia_completa.append(irradiancia_mensual[mes])
        else:
            irradiancia_completa.append(0)

    # Crear el gráfico de barras
    barras = ax.bar(range(1, len(meses)+1), irradiancia_completa, color='#FF6B35', edgecolor='white', linewidth=0.5)

    
    ax.text(0.05, 0.95, 'Orientación del plano: \n' + r'$\alpha = -97^\circ$' + '\n' + r'$\beta = 90^\circ$', 
        transform=ax.transAxes, 
        fontsize=12, 
        ha='left', 
        va='top', 
        bbox=dict(facecolor='white', alpha=0.7, edgecolor='gray'))
    
    ax.set_xlabel('Mes', fontsize=12)
    ax.set_ylabel('Irradiación sobre plano [kWh/m²]', fontsize=12)
    ax.set_title(titulo, fontsize=14, fontweight='bold')
    ax.set_xticks(range(1, len(meses)+1))
    ax.set_xticklabels(meses)
    ax.grid(True, alpha=0.3, axis='y')

    # Ajustar el rango del eje Y para que empiece en 0
    max_val = max(irradiancia_completa)
    if max_val > 0:
        ax.set_ylim(0, max_val * 1.25)
    else:
        ax.set_ylim(0, 1)

    # Opcional: añadir valores sobre las barras
    for i, v in enumerate(irradiancia_completa):
        ax.text(i+1, v + max(irradiancia_completa)*0.01, f'{v:.1f}', 
                ha='center', va='bottom', fontsize=9)

    plt.tight_layout()
    
    # Mostrar el gráfico solo si se solicita
    if mostrar_grafico:
        plt.show()
    
    """
    # Mostrar los valores calculados
    print("Irradiancia mensual (kWh/m²):")
    for i, mes in enumerate(meses):
        print(f"{mes}: {irradiancia_completa[i]:.2f}")
    """
    
    return fig, irradiancia_completa


