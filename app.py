from flask import Flask, request, render_template_string
import math

app = Flask(__name__)

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

def metros_a_pies(metros: float) -> float:
    return metros * CONVERSION_PIES_METROS

def calcular_area(diametro_exterior: float) -> float:
    return (math.pi / 4) * (diametro_exterior ** 2)

def diametro_interior_y_seccion(diametro_exterior: float) -> tuple[float, float]:
    # Mapeo según tus widgets
    if abs(diametro_exterior - 2.875) < 1e-6:
        return 2.441, 1.812
    if abs(diametro_exterior - 3.5) < 1e-6:
        return 2.992, 2.59
    # fallback razonable
    return diametro_exterior * 0.85, 0.0

def calcular_F1(area: float, nivel_dinamico_ft: float, profundidad_ancla_ft: float) -> float:
    return (area * nivel_dinamico_ft * GRADIENTE_FLUIDO *
            ((COEF_POISSON * nivel_dinamico_ft / profundidad_ancla_ft) + (1 - 2 * COEF_POISSON)))

def calcular_F2(seccion_paredes: float) -> float:
    return MODULO_YOUNG * COEF_EXPANSION * ((TEMP_SUPERFICIE_C - TEMP_MEDIA_C) / 2) * seccion_paredes

def calcular_F3(area: float, diametro_exterior: float, diametro_interior: float,
                nivel_estatico_ft: float, profundidad_ancla_ft: float) -> float:
    A = area * GRADIENTE_FLUIDO * ((diametro_exterior**2 - diametro_interior**2) / (diametro_exterior**2)) * nivel_estatico_ft
    B = (COEF_POISSON * nivel_estatico_ft / profundidad_ancla_ft) + (1 - 2 * COEF_POISSON)
    return A * B

def calcular_estiramiento(profundidad_ancla_ft: float, tension_total: float) -> float:
    return 0.22 * (profundidad_ancla_ft / 1000) * (tension_total / 1000)

TEMPLATE = """
<!doctype html>
<html lang="es">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>Tensi-n-ancla</title>
  <style>
    body { font-family: Arial, sans-serif; max-width: 980px; margin: 40px auto; padding: 0 16px; }
    .card { border: 1px solid #ddd; border-radius: 12px; padding: 16px; margin-bottom: 16px; }
    label { display:block; margin-top: 10px; font-weight: 600; }
    input, select { width: 100%; padding: 10px; border-radius: 10px; border: 1px solid #ccc; margin-top: 6px; }
    .row { display: grid; grid-template-columns: 1fr 1fr; gap: 12px; }
    .btn { margin-top: 14px; padding: 10px 14px; border: 0; border-radius: 10px; cursor:pointer; }
    .btn-primary { background: #1f6feb; color: white; }
    table { width: 100%; border-collapse: collapse; }
    td { padding: 8px; border-bottom: 1px solid #eee; }
    .muted { color: #666; font-size: 0.95em; }
    .big { font-size: 1.05em; }
    .ok { font-weight: 700; }
  </style>
</head>
<body>

  <h1>Tensi-n-ancla</h1>
  <p class="muted">Cálculo de la tensión necesaria para fijar ancla y estiramiento de la sarta.</p>

  <div class="card">
    <form method="post">
      <div class="row">
        <div>
          <label>Nivel dinámico (m)</label>
          <input value="{{nivel_dinamico_m}}" disabled>
        </div>
        <div>
          <label>Nivel dinámico (ft)</label>
          <input value="{{nivel_dinamico_ft}}" disabled>
        </div>
      </div>

      <div class="row">
        <div>
          <label>Profundidad ancla (m)</label>
          <input name="prof_m" type="number" step="0.01" value="{{prof_m}}" required>
        </div>
        <div>
          <label>Profundidad ancla (ft)</label>
          <input value="{{prof_ft}}" disabled>
        </div>
      </div>

      <div class="row">
        <div>
          <label>Temp. superficie (°C)</label>
          <input value="{{temp_sup_c}}" disabled>
        </div>
        <div>
          <label>Temp. superficie (°F)</label>
          <input value="{{temp_sup_f}}" disabled>
        </div>
      </div>

      <div class="row">
        <div>
          <label>Temp. media (°C)</label>
          <input value="{{temp_med_c}}" disabled>
        </div>
        <div>
          <label>Temp. media (°F)</label>
          <input value="{{temp_med_f}}" disabled>
        </div>
      </div>

      <div class="row">
        <div>
          <label>Diámetro exterior (in)</label>
          <select name="de">
            <option value="2.875" {% if de==2.875 %}selected{% endif %}>2.875</option>
            <option value="3.5" {% if de==3.5 %}selected{% endif %}>3.5</option>
          </select>
        </div>
        <div>
          <label>Nivel estático (ft)</label>
          <input value="{{nivel_est_ft}}" disabled>
        </div>
      </div>

      <button class="btn btn-primary" type="submit">Calcular</button>
    </form>
  </div>

  {% if result %}
  <div class="card">
    <h2>Resultados</h2>
    <table>
      <tr><td>Diámetro interior (in)</td><td>{{di}}</td></tr>
      <tr><td>Sección paredes (in²)</td><td>{{sp}}</td></tr>
      <tr><td>Área (in²)</td><td>{{area}}</td></tr>
      <tr><td>F1 (lbs)</td><td>{{F1}}</td></tr>
      <tr><td>F2 (lbs)</td><td>{{F2}}</td></tr>
      <tr><td>F3 (lbs)</td><td>{{F3}}</td></tr>
      <tr><td class="ok">Tensión Total (lbs)</td><td class="ok">{{TT}}</td></tr>
      <tr><td>Estiramiento E (in)</td><td>{{E}}</td></tr>
    </table>
    <p class="big"><strong>{{frase}}</strong></p>
  </div>
  {% endif %}

</body>
</html>
"""

@app.route("/", methods=["GET", "POST"])
def index():
    nivel_dinamico_m = NIVEL_DINAMICO_METROS
    nivel_dinamico_ft = metros_a_pies(nivel_dinamico_m)

    prof_m = 1000.0
    de = 2.875

    if request.method == "POST":
        prof_m = float(request.form.get("prof_m", prof_m))
        de = float(request.form.get("de", de))

    prof_ft = metros_a_pies(prof_m)

    temp_sup_f = (TEMP_SUPERFICIE_C * 9/5) + 32
    temp_med_f = (TEMP_MEDIA_C * 9/5) + 32

    di, sp = diametro_interior_y_seccion(de)

    result = None
    ctx = dict(
        nivel_dinamico_m=f"{nivel_dinamico_m:.2f}",
        nivel_dinamico_ft=f"{nivel_dinamico_ft:.2f}",
        prof_m=f"{prof_m:.2f}",
        prof_ft=f"{prof_ft:.2f}",
        temp_sup_c=f"{TEMP_SUPERFICIE_C:.2f}",
        temp_med_c=f"{TEMP_MEDIA_C:.2f}",
        temp_sup_f=f"{temp_sup_f:.2f}",
        temp_med_f=f"{temp_med_f:.2f}",
        de=de,
        di=f"{di:.3f}",
        sp=f"{sp:.3f}",
        nivel_est_ft=f"{NIVEL_ESTATICO_PIE:.2f}",
        result=False
    )

    if request.method == "POST":
        area = calcular_area(de)
        F1 = calcular_F1(area, nivel_dinamico_ft, prof_ft)
        F2 = calcular_F2(sp)
        F3 = calcular_F3(area, de, di, NIVEL_ESTATICO_PIE, prof_ft)
        TT = F1 + F2 - F3
        E = calcular_estiramiento(prof_ft, TT)

        frase = f"Fijar ancla en {prof_m:.2f} m con {TT:.2f} lbs y {E:.4f} in de estiramiento."

        ctx.update(dict(
            area=f"{area:.2f}",
            F1=f"{F1:.2f}",
            F2=f"{F2:.2f}",
            F3=f"{F3:.2f}",
            TT=f"{TT:.2f}",
            E=f"{E:.4f}",
            frase=frase,
            result=True
        ))

    return render_template_string(TEMPLATE, **ctx)
