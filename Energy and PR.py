#%%
from Filter import *

'''
Definimos el PR como el ratio o cociente entre la energía AC finalmente otorgada y la 
energía teórica entregada por el sistema. Esto, principalmente, evalúa todas las
pérdidas del sistema en general (temperatura, suciedad, sombreado, cableado, inversor, 
etc.). 

    PR = E_AC / Energía teórica ideal

    PR = E_AC / (P_nominal * Hi * n)

donde P_nominal = Potencia nominal instalada en condiciones estándar (STC).
      Hi = Irradiación solar recibida en el plano de los módulos (kWh/m2).
      n = Factor de corrección por tempertura.
      E_AC = Energía AC medida a la salida del microinversor.


    - DATOS NOMINALES DE LOS PANELES INSTALADOS EN LA AZOTEA -
        Se usarán los del documento a la fecha más reciente
        que, en este caso, es el del pedido de compra u orden
        de las células instaladas.

1.- 4 paneles Antracita (color azulado) en serie:

    Pnominal o Pg = 69.77 Wp (+/- 5%)
    Isc = 8.06 A
    Voc = 10.67 V
    Temp Coeff power = -0.32 %/K


2.- 4 paneles Green (color verdozo) en serie:

    Pnominal o Pg = 66.24 Wp (+/. 5%)
    Isc = 7.65 A
    Voc = 10.67 V
    Temp Coeff power = -0.32 %/K

3.- 4 paneles Terracota (color terroso/rojo) en serie:

    Pnominal o Pg = 59.17 Wp (+/. 5%)
    Isc = 6.83 A
    Voc = 9.06 V
    Temp Coeff power = -0.32 %/K


La ecuación de corrección que se está utilizando está definida como: 

    P_corregida = P_nominal* [1+(n)*(T-T_ref)]

    donde n = Coeficiente de temperatura para potencia del panel
          T_ref = Temperatura de referencia (Comunmente 25°C a menos que indique otra cosa)


'''
#%%


### CÁLCULO DE IRRADIACIÓN SOLAR MEDIANTE REGISTRO DE PIRANÓMETRO ###
tiempo_hora = 2/60 

#Irradiaciacion_Antracita =  Antracita_filtered["Piranometro Referencia"] * tiempo_hora / 1000
#Irradiaciacion_Green     =  Green_filtered["Piranometro Referencia"]     * tiempo_hora / 1000
#Irradiaciacion_Terracota =  Terracota_filtered["Piranometro Referencia"] * tiempo_hora / 1000
#
#Irradiaciacion_Antracita_mensual = Irradiaciacion_Antracita.resample('ME').sum()
#Irradiaciacion_Green_mensual     = Irradiaciacion_Green.resample('ME').sum()   
#Irradiaciacion_Terracota_mensual = Irradiaciacion_Terracota.resample('ME').sum()


Irradiacion = DataFrame_Irradiancia_Submuestreado["Canal 106-Canal_106_Gpyr_[W/m2] "] * tiempo_hora / 1000
Irradianción_mensual = Irradiacion.resample('ME').sum()

### CORRECCIÓN DE POTENCIA PARA CELULAS ANTRACITA ###

Pnominal_Antracita = 69.77/1000
TCPower_Antracita  = -0.32/100

Potencia_nominal_DC_corregida_Antracita_1 = Pnominal_Antracita*(1+(TCPower_Antracita)*(Antracita_filtered["Temp 1 (C) Antracita"]-25))
Potencia_nominal_DC_corregida_Antracita_2 = Pnominal_Antracita*(1+(TCPower_Antracita)*(Antracita_filtered["Temp 2 (C) Antracita"]-25))
Potencia_nominal_DC_corregida_Antracita_3 = Pnominal_Antracita*(1+(TCPower_Antracita)*(Antracita_filtered["Temp 3 (C) Antracita"]-25))
Potencia_nominal_DC_corregida_Antracita_4 = Pnominal_Antracita*(1+(TCPower_Antracita)*(Antracita_filtered["Temp 4 (C) Antracita"]-25))

Potencia_nominal_DC_corregida_Antracita = Potencia_nominal_DC_corregida_Antracita_1 + Potencia_nominal_DC_corregida_Antracita_2 + Potencia_nominal_DC_corregida_Antracita_3 + Potencia_nominal_DC_corregida_Antracita_4
Potencia_nominal_DC_Antracita = 4*Pnominal_Antracita

### CORRECCIÓN DE POTENCIA PARA CELULAS GREEN ###

Pnominal_Green = 66.24/1000
TCPower_Green  = -0.32/100

Potencia_nominal_DC_corregida_Green_1 = Pnominal_Green*(1+(TCPower_Green)*(Green_filtered["Temp 1 (C) Green"]-25))
Potencia_nominal_DC_corregida_Green_2 = Pnominal_Green*(1+(TCPower_Green)*(Green_filtered["Temp 2 (C) Green"]-25))
Potencia_nominal_DC_corregida_Green_3 = Pnominal_Green*(1+(TCPower_Green)*(Green_filtered["Temp 3 (C) Green"]-25))
Potencia_nominal_DC_corregida_Green_4 = Pnominal_Green*(1+(TCPower_Green)*(Green_filtered["Temp 4 (C) Green"]-25))

Potencia_nominal_DC_corregida_Green = Potencia_nominal_DC_corregida_Green_1 + Potencia_nominal_DC_corregida_Green_2 + Potencia_nominal_DC_corregida_Green_3 + Potencia_nominal_DC_corregida_Green_4
Potencia_nominal_DC_Green = 4*Pnominal_Green


### CORRECCIÓN DE POTENCIA PARA CELULAS TERRACOTA ###

Pnominal_Terracota = 59.17/1000
TCPower_Terracota  = -0.32/100

Potencia_nominal_DC_corregida_Terracota_1 = Pnominal_Terracota*(1+(TCPower_Terracota)*(Terracota_filtered["Temp 1 (C) Terracota"]-25))
Potencia_nominal_DC_corregida_Terracota_2 = Pnominal_Terracota*(1+(TCPower_Terracota)*(Terracota_filtered["Temp 2 (C) Terracota"]-25))
Potencia_nominal_DC_corregida_Terracota_3 = Pnominal_Terracota*(1+(TCPower_Terracota)*(Terracota_filtered["Temp 3 (C) Terracota"]-25))
Potencia_nominal_DC_corregida_Terracota_4 = Pnominal_Terracota*(1+(TCPower_Terracota)*(Terracota_filtered["Temp 4 (C) Terracota"]-25))

Potencia_nominal_DC_corregida_Terracota = Potencia_nominal_DC_corregida_Terracota_1 + Potencia_nominal_DC_corregida_Terracota_2 + Potencia_nominal_DC_corregida_Terracota_3 + Potencia_nominal_DC_corregida_Terracota_4
Potencia_nominal_DC_Terracota = 4*Pnominal_Terracota


                ##### CÁCULO DE ENERGÍA CORREGIDA Y ENERGÍA NOMINAL #####

Energia_nominal_Antracita_mensual = Irradianción_mensual * Potencia_nominal_DC_Antracita
Energia_nominal_Green_mensual     = Irradianción_mensual * Potencia_nominal_DC_Green
Energia_nominal_Terracota_mensual = Irradianción_mensual * Potencia_nominal_DC_Terracota


Energia_nominal_corregida_Antracita = Potencia_nominal_DC_corregida_Antracita*Irradiacion
Energia_nominal_corregida_Green = Potencia_nominal_DC_corregida_Green*Irradiacion
Energia_nominal_corregida_Terracota = Potencia_nominal_DC_corregida_Terracota*Irradiacion


Energia_nominal_corregida_Antracita_mensual = Energia_nominal_corregida_Antracita.resample('ME').sum()
Energia_nominal_corregida_Green_mensual = Energia_nominal_corregida_Green.resample('ME').sum()
Energia_nominal_corregida_Terracota_mensual = Energia_nominal_corregida_Terracota.resample('ME').sum()

############ ENERGÍA DC DE LOS ARRAYS ############

Energia_DC_Antracita = Antracita_filtered["Potencia entrada (W) Antracita"] * tiempo_hora / 1000
Energia_DC_Green     = Green_filtered["Potencia entrada (W) Green"]         * tiempo_hora / 1000
Energia_DC_Terracota = Terracota_filtered["Potencia entrada (W) Terracota"] * tiempo_hora / 1000

Energia_DC_Antracita_mensual = Energia_DC_Antracita.resample('ME').sum()
Energia_DC_Green_mensual     = Energia_DC_Green.resample('ME').sum()
Energia_DC_Terracota_mensual = Energia_DC_Terracota.resample('ME').sum()


############ ENERGÍA AC (SALIDA DEL INVERSOR) DE LOS ARRAYS ############

Energia_AC_Antracita = Antracita_filtered["Potencia AC salida (W) Antracita"] * tiempo_hora / 1000
Energia_AC_Green     = Green_filtered["Potencia AC salida (W) Green"]         * tiempo_hora / 1000
Energia_AC_Terracota = Terracota_filtered["Potencia AC salida (W) Terracota"] * tiempo_hora / 1000

Energia_AC_Antracita_mensual = Energia_AC_Antracita.resample('ME').sum()
Energia_AC_Green_mensual = Energia_AC_Green.resample('ME').sum()
Energia_AC_Terracota_mensual = Energia_AC_Terracota.resample('ME').sum()


##### CÁLCULO DE PERFOMANCE RATIO (PR) #####

PR_antracita = Energia_AC_Antracita_mensual / Energia_nominal_Antracita_mensual
PR_green   = Energia_AC_Green_mensual / Energia_nominal_Green_mensual
PR_terracota = Energia_AC_Terracota_mensual / Energia_nominal_Terracota_mensual 


##### CÁLCULO DE PERFOMANCE RATIO (PR) CORREGIDO #####

PR_antracita_T = Energia_AC_Antracita_mensual / Energia_nominal_corregida_Antracita_mensual 
PR_green_T     = Energia_AC_Green_mensual / Energia_nominal_corregida_Green_mensual
PR_terracota_T = Energia_AC_Terracota_mensual / Energia_nominal_corregida_Terracota_mensual

### Cálculo de pérdidas por temperatura L_T ####

L_t_antracita = 1 - (PR_antracita/PR_antracita_T)
L_t_green = 1 - (PR_green/PR_green_T)
L_t_terracota = 1 - (PR_terracota/PR_terracota_T)

# %%
