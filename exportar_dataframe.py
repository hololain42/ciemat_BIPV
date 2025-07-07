#%%
import pandas as pd

#%%

### VOLCAMOS LOS DATOS FILTRADOS A UN .xlsx GENERAL PARA NO TENER QUE APLICAR LOS FILTROS CADA VEZ QUE CORREMOS EL PROGRAMA ###
### Para ahorrar memoria, también seleccionamos los datos, de forma que no copiaremos columnas como la del Inversor Huawei, 
# ya que no mide nada de este proyecto (está conectado a otras células distintas) o los canales que son sumas de voltajes

# Como ya están filtrados, es muy posible que los datos no coincidan exactamente en su Datetime
# Por ejemplo, habrá huecos en una fila si se han filtrado los datos de Green pero no los de Antracia y Terracota
# Esta función maneja esos casos correctamente, dejando en blanco esos huecos.

def combinar_dataframes_con_fechas_distintas(df_antracita, df_green, df_terracota, filename):
    """
    Combina los dataframes incluso si tienen fechas diferentes y lo exporta a un fichero .xlsx
    Preserva las columnas comunes aunque algunos dataframes estén filtrados

    Parámetros:
        df_antracita, df_green, df_terracota (DataFrame): Dataframes de pandas de cada célula
        filename (str): Nombre del archivo de salida

    Devuelve:
        df_final (DataFrame): DataFrame de pandas combinado en el orden específico que le hemos impuesto

    """
    
    # Copiar dataframes para no modificar los originales

    df_antracita_copy = preparar_para_merge(df_antracita, 'Antracita')
    df_green_copy     = preparar_para_merge(df_green, 'Green')
    df_terracota_copy = preparar_para_merge(df_terracota, 'Terracota')
    
    # Definir columnas comunes a los tres dataframes
    columnas_comunes = [
        'Temp (C) Ambiente',
        'Piranometro Referencia',
        'Celula Calibrada Abajo',
        'Celula Calibrada Arriba',
        'Celula Calibrada Izquierda',
        'Temp (C) Celula Calibrada Abajo',
        'Temp (C) Celula Calibrada Arriba'
    ]

    # Verificar en qué dataframes están las columnas comunes (para debugging)
    for df, nombre in [(df_antracita_copy, 'Antracita'), (df_green_copy, 'Green'), (df_terracota_copy, 'Terracota')]:
        columnas_comunes_presentes = [col for col in columnas_comunes if col in df.columns]


    # Merge de los DataFrames completo (outer join) para incluir todas las fechas
    # Combinamos paso a paso, ya que pd.merge solo acepta 2 dataframes a la vez

    # Primero los DataFrames de Antracita y Green
    df_temp = pd.merge(df_antracita_copy, df_green_copy, on='Datetime', how='outer', suffixes=('', '_green'))
    
    # Luego combinamos el resultado con Terracota
    df_combinado = pd.merge(df_temp, df_terracota_copy, on='Datetime', how='outer', suffixes=('', '_terracota'))
    
    # Identificar columnas duplicadas (que tienen suffixes)
    columnas_con_suffix = [col for col in df_combinado.columns if col.endswith(('_green', '_terracota'))]
    
    # Para cada columna con suffix, verificar si es una columna común
    for col_suffix in columnas_con_suffix:
        # Obtener el nombre base de la columna (sin suffix)
        if col_suffix.endswith('_green'):
            col_base = col_suffix.replace('_green', '')
        elif col_suffix.endswith('_terracota'):
            col_base = col_suffix.replace('_terracota', '')
        
        # Si la columna base es una columna común, llenar los valores NaN con los valores de la columna con suffix
        if col_base in columnas_comunes and col_base in df_combinado.columns:
            # Combinar valores: usar la columna base, pero llenar NaN con valores de la columna con suffix
            df_combinado[col_base] = df_combinado[col_base].fillna(df_combinado[col_suffix])

    # Eliminar columnas duplicadas si las hay
    # Esto elimina columnas que terminan en '_green' o '_terracota' (duplicadas)
    df_combinado = df_combinado.loc[:, ~df_combinado.columns.str.endswith(('_green', '_terracota'))]

    # Añadimos un orden específico (de esta forma ignoramos las columnas del Datalogger que no nos interesan)
    orden_columnas = [
        'Datetime',
        'Temp (C) Ambiente',
        'Piranometro Referencia',
        'Vm 1 (V) Antracita',
        'Vm 2 (V) Antracita', 
        'Vm 3 (V) Antracita', 
        'Vm 4 (V) Antracita', 
        'Vm 1 (V) Green',
        'Vm 2 (V) Green',
        'Vm 3 (V) Green',
        'Vm 4 (V) Green',
        'Vm 1 (V) Terracota',
        'Vm 2 (V) Terracota',
        'Vm 3 (V) Terracota',
        'Vm 4 (V) Terracota',
        'Im 1 (A) Antracita',
        'Im 2 (A) Antracita',
        'Im 3 (A) Antracita',
        'Im 4 (A) Antracita',
        'Im 1 (A) Green',
        'Im 2 (A) Green',
        'Im 3 (A) Green',
        'Im 4 (A) Green',
        'Im 1 (A) Terracota',
        'Im 2 (A) Terracota',
        'Im 3 (A) Terracota',
        'Im 4 (A) Terracota',
        'Corriente entrada (A) Antracita',
        'Corriente entrada (A) Green',
        'Corriente entrada (A) Terracota',
        'Potencia AC salida (W) Antracita',
        'Potencia AC salida (W) Green',
        'Potencia AC salida (W) Terracota',
        'Celula Calibrada Abajo',
        'Celula Calibrada Arriba',
        'Celula Calibrada Izquierda',
        'Temp (C) Celula Calibrada Abajo',
        'Temp (C) Celula Calibrada Arriba',
        'Temp 1 (C) Antracita',
        'Temp 2 (C) Antracita',
        'Temp 3 (C) Antracita',
        'Temp 4 (C) Antracita',
        'Temp 1 (C) Green',
        'Temp 2 (C) Green',
        'Temp 3 (C) Green',
        'Temp 4 (C) Green',
        'Temp 1 (C) Terracota',
        'Temp 2 (C) Terracota',
        'Temp 3 (C) Terracota',
        'Temp 4 (C) Terracota',
        'Potencia entrada (W) Antracita',
        'Potencia entrada (W) Green',
        'Potencia entrada (W) Terracota'
    ]
    
    # Seleccionar solo las columnas que existen
    columnas_disponibles = [col for col in orden_columnas if col in df_combinado.columns]
    
    # Mostrar columnas que existen pero no están en el orden (para debugging)
    columnas_no_incluidas = [col for col in df_combinado.columns if col not in orden_columnas]
    if columnas_no_incluidas:
        print(f"Columnas disponibles en el DataFrame pero NO incluidas: {columnas_no_incluidas}")
    
    df_final = df_combinado[columnas_disponibles]
    
    # Ordenar por fecha
    df_final = df_final.sort_values('Datetime').reset_index(drop=True)
    
    # Exportar
    df_final.to_excel(filename, index=False, sheet_name='Datos_Combinados')
    
    print(f"Creado el archivo de datos filtrados: {filename}")
    print(f"Número de filas: {len(df_final)}")
    
    return df_final


# Función auxiliar para que los DataFrames tengan la columna Datetime correcta, asociada a su index
def preparar_para_merge(df, nombre=''):

    """
    Prepara un dataframe para el merge, asegurando que tenga la columna Datetime
    """
    if df.empty:
        print(f"DataFrame {nombre} está vacío después del filtrado")
        return df

    df = df.reset_index()
    # Si el índice original no tenía nombre, Pandas lo llama 'index'
    if 'index' in df.columns:
        df.rename(columns={'index': 'Datetime'}, inplace=True)

    # Verificación segura por si el índice sí tenía otro nombre
    elif df.columns[0] != 'Datetime':
        df.rename(columns={df.columns[0]: 'Datetime'}, inplace=True)

    df['Datetime'] = pd.to_datetime(df['Datetime'])  # Asegurar formato datetime
    
    return df


#%%