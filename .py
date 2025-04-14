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
