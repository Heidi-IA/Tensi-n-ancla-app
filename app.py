import ipywidgets as widgets
from IPython.display import display
import math

# --- Constantes ---
COEF_POISSON = 0.3  
MODULO_YOUNG = 30000000  
COEF_EXPANSION = 0.0000069  
GRADIENTE_FLUIDO = 0.5  
CONVERSION_PIES_METROS = 3.28084  

# --- Variables fijas ---
NIVEL_DINAMICO_METROS = 1900
NIVEL_ESTATICO_PIE = 700
TEMP_SUPERFICIE_C = 30
TEMP_MEDIA_C = 15

# --- Variables de entrada ---
nivel_dinamico_metros = widgets.FloatText(value=NIVEL_DINAMICO_METROS, description="Nivel dinámico (m):", disabled=True)
nivel_dinamico_pie = widgets.Text(value=f"{NIVEL_DINAMICO_METROS * CONVERSION_PIES_METROS:.2f}", description="Nivel dinámico (ft):", disabled=True)

profundidad_ancla_metros = widgets.FloatText(value=1000, description="Profundidad ancla (m):")
profundidad_ancla_pie = widgets.Text(description="Profundidad ancla (ft):")

temp_superficie_C = widgets.FloatText(value=TEMP_SUPERFICIE_C, description="Temp. superficie (°C):", disabled=True)
temp_media_C = widgets.FloatText(value=TEMP_MEDIA_C, description="Temp. media (°C):", disabled=True)
temp_superficie_F = widgets.Text(value=f"{(TEMP_SUPERFICIE_C * 9/5) + 32:.2f}", description="Temp. superficie (°F):", disabled=True)
temp_media_F = widgets.Text(value=f"{(TEMP_MEDIA_C * 9/5) + 32:.2f}", description="Temp. media (°F):", disabled=True)

diametro_exterior = widgets.Dropdown(
    options=[2.875, 3.5], 
    value=2.875,
    description="Diámetro exterior (in):"
)

diametro_interior = widgets.Text(description="Diámetro interior (in):")
seccion_paredes = widgets.Text(description="Sección paredes (in²):")

nivel_estatico_pie = widgets.FloatText(value=NIVEL_ESTATICO_PIE, description="Nivel estático (ft):", disabled=True)

# --- Funciones de cálculo ---
def metros_a_pies(metros):
    return metros * CONVERSION_PIES_METROS

def calcular_area(diametro_exterior):
    return (math.pi / 4) * (diametro_exterior ** 2)

def calcular_F1(area, nivel_dinamico_pie, profundidad_ancla_pie):
    return (area * nivel_dinamico_pie * GRADIENTE_FLUIDO * 
            ((COEF_POISSON * nivel_dinamico_pie / profundidad_ancla_pie) + (1 - 2 * COEF_POISSON)))

def calcular_F2(seccion_paredes):
    return MODULO_YOUNG * COEF_EXPANSION * ((TEMP_SUPERFICIE_C - TEMP_MEDIA_C) / 2) * seccion_paredes

def calcular_F3(area, diametro_exterior, diametro_interior, nivel_estatico_pie, profundidad_ancla_pie):
    A = area * GRADIENTE_FLUIDO * ((diametro_exterior**2 - diametro_interior**2) / (diametro_exterior**2)) * nivel_estatico_pie
    B = (COEF_POISSON * nivel_estatico_pie / profundidad_ancla_pie) + (1 - 2 * COEF_POISSON)
    return A * B

def calcular_estiramiento(profundidad_ancla_pie, tension_total):
    return 0.22 * (profundidad_ancla_pie / 1000) * (tension_total / 1000)

# --- Funciones de actualización ---
def actualizar_profundidad_ancla_pie(*args):
    profundidad_ancla_pie.value = f"{metros_a_pies(profundidad_ancla_metros.value):.2f}"

def actualizar_diametros(*args):
    if diametro_exterior.value == 2.875:
        diametro_interior.value = "2.441"
        seccion_paredes.value = "1.812"
    elif diametro_exterior.value == 3.5:
        diametro_interior.value = "2.992"
        seccion_paredes.value = "2.59"

def actualizar_tension_total(*args):
    actualizar_diametros()  

    area_value = calcular_area(diametro_exterior.value)
    F1 = calcular_F1(area_value, float(nivel_dinamico_pie.value), float(profundidad_ancla_pie.value))

    # Validar `seccion_paredes.value`
    if seccion_paredes.value.strip():
        F2 = calcular_F2(float(seccion_paredes.value))
    else:
        print("Advertencia: `seccion_paredes` está vacío, asignando valor por defecto.")
        F2 = 0  

    F3 = calcular_F3(area_value, diametro_exterior.value, float(diametro_interior.value), nivel_estatico_pie.value, float(profundidad_ancla_pie.value))

    tension_total = F1 + F2 - F3

    # Actualizar los widgets
    area_widget.value = f"{area_value:.2f}"
    F1_widget.value = f"{F1:.2f}"
    F2_widget.value = f"{F2:.2f}"
    F3_widget.value = f"{F3:.2f}"
    tension_total_widget.value = f"{tension_total:.2f}"
    estiramiento_widget.value = f"{calcular_estiramiento(float(profundidad_ancla_pie.value), tension_total):.4f}"

    # Actualizar frase final
    profundidad_ancla = profundidad_ancla_metros.value
    estiramiento = calcular_estiramiento(float(profundidad_ancla_pie.value), tension_total)
    frase_final_widget.value = (f"Fijar ancla en {profundidad_ancla:.2f} m "
                                f"con {tension_total:.2f} lbs y "
                                f"{estiramiento:.4f} in de estiramiento.")

# --- Vincular actualizaciones ---
profundidad_ancla_metros.observe(actualizar_profundidad_ancla_pie, 'value')
diametro_exterior.observe(actualizar_diametros, 'value')

for var in [profundidad_ancla_metros]:
    var.observe(actualizar_tension_total, 'value')

# --- Mostrar widgets ---
display(nivel_dinamico_metros, nivel_dinamico_pie)
display(profundidad_ancla_metros, profundidad_ancla_pie)
display(temp_superficie_C, temp_superficie_F)
display(temp_media_C, temp_media_F)
display(diametro_exterior, diametro_interior, seccion_paredes)
display(nivel_estatico_pie)

area_widget = widgets.Text(description="Área (in²):")
F1_widget = widgets.Text(description="F1 (lbs):")
F2_widget = widgets.Text(description="F2 (lbs):")
F3_widget = widgets.Text(description="F3 (lbs):")
tension_total_widget = widgets.Text(description="Tensión Total (lbs):")
estiramiento_widget = widgets.Text(description="Estiramiento E (in):")
frase_final_widget = widgets.Text(description="Frase final:", disabled=True)

display(area_widget, F1_widget, F2_widget, F3_widget, tension_total_widget, estiramiento_widget)
display(frase_final_widget)
