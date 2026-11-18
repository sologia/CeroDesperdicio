"""Catálogo de ingredientes frecuentes con información nutricional.

Valores aproximados por cada 100 g (referencia: tablas USDA / INCAP).
Formato: nombre: (categoria, unidad, dias_vida, peso_unidad_g,
                  kcal, proteina, carbohidratos, grasa, fibra)
"""

from datetime import date, timedelta

CATALOGO = {
    # Frutas
    "Manzana":        ("Frutas", "unidad", 21, 180, 52, 0.3, 14, 0.2, 2.4),
    "Banano":         ("Frutas", "unidad", 6, 120, 89, 1.1, 23, 0.3, 2.6),
    "Naranja":        ("Frutas", "unidad", 14, 130, 47, 0.9, 12, 0.1, 2.4),
    "Limón":          ("Frutas", "unidad", 21, 60, 29, 1.1, 9, 0.3, 2.8),
    "Aguacate":       ("Frutas", "unidad", 5, 200, 160, 2.0, 9, 15, 6.7),
    "Mango":          ("Frutas", "unidad", 6, 200, 60, 0.8, 15, 0.4, 1.6),
    "Piña":           ("Frutas", "unidad", 5, 900, 50, 0.5, 13, 0.1, 1.4),
    "Papaya":         ("Frutas", "unidad", 5, 1000, 43, 0.5, 11, 0.3, 1.7),
    "Fresas":         ("Frutas", "paquete", 5, 250, 32, 0.7, 7.7, 0.3, 2.0),
    # Verduras
    "Tomate":         ("Verduras", "unidad", 7, 120, 18, 0.9, 3.9, 0.2, 1.2),
    "Cebolla":        ("Verduras", "unidad", 30, 110, 40, 1.1, 9.3, 0.1, 1.7),
    "Ajo":            ("Verduras", "unidad", 60, 40, 149, 6.4, 33, 0.5, 2.1),
    "Papa":           ("Verduras", "unidad", 30, 170, 77, 2.0, 17, 0.1, 2.2),
    "Zanahoria":      ("Verduras", "unidad", 21, 60, 41, 0.9, 10, 0.2, 2.8),
    "Chiltoma":       ("Verduras", "unidad", 10, 120, 20, 0.9, 4.6, 0.2, 1.7),
    "Lechuga":        ("Verduras", "unidad", 7, 300, 15, 1.4, 2.9, 0.2, 1.3),
    "Repollo":        ("Verduras", "unidad", 14, 900, 25, 1.3, 5.8, 0.1, 2.5),
    "Brócoli":        ("Verduras", "unidad", 7, 300, 34, 2.8, 7, 0.4, 2.6),
    "Pepino":         ("Verduras", "unidad", 7, 200, 15, 0.7, 3.6, 0.1, 0.5),
    "Espinaca":       ("Verduras", "paquete", 5, 200, 23, 2.9, 3.6, 0.4, 2.2),
    "Elote":          ("Verduras", "unidad", 5, 150, 86, 3.3, 19, 1.4, 2.7),
    "Plátano verde":  ("Verduras", "unidad", 7, 250, 122, 1.3, 32, 0.4, 2.3),
    # Carnes
    "Pollo":          ("Carnes", "kg", 2, 1500, 215, 18.6, 0, 15, 0),
    "Pechuga de pollo": ("Carnes", "kg", 2, 250, 165, 31, 0, 3.6, 0),
    "Carne molida":   ("Carnes", "kg", 2, 450, 250, 26, 0, 17, 0),
    "Bistec de res":  ("Carnes", "kg", 3, 200, 217, 26, 0, 12, 0),
    "Cerdo":          ("Carnes", "kg", 3, 200, 242, 27, 0, 14, 0),
    "Pescado":        ("Carnes", "kg", 2, 200, 96, 20, 0, 1.7, 0),
    "Jamón":          ("Carnes", "paquete", 7, 250, 145, 21, 1.5, 6, 0),
    "Salchichas":     ("Carnes", "paquete", 14, 400, 290, 12, 3, 25, 0),
    # Lácteos y huevos
    "Leche":          ("Lácteos", "litro", 7, 1030, 61, 3.2, 4.8, 3.3, 0),
    "Queso":          ("Lácteos", "lb", 14, 450, 350, 22, 2, 28, 0),
    "Yogur":          ("Lácteos", "unidad", 14, 200, 61, 3.5, 4.7, 3.3, 0),
    "Mantequilla":    ("Lácteos", "paquete", 60, 225, 717, 0.9, 0.1, 81, 0),
    "Crema":          ("Lácteos", "botella", 10, 450, 198, 2.4, 4.6, 19, 0),
    "Huevos":         ("Lácteos", "docena", 21, 50, 155, 13, 1.1, 11, 0),
    # Granos y cereales
    "Arroz":          ("Granos y cereales", "lb", 365, 450, 365, 7.1, 80, 0.7, 1.3),
    "Frijoles":       ("Granos y cereales", "lb", 365, 450, 333, 23, 60, 0.8, 15),
    "Pasta":          ("Granos y cereales", "paquete", 365, 400, 371, 13, 75, 1.5, 3.2),
    "Avena":          ("Granos y cereales", "bolsa", 180, 400, 389, 17, 66, 7, 11),
    "Tortillas":      ("Granos y cereales", "paquete", 5, 300, 218, 5.7, 45, 2.9, 6.3),
    # Panadería
    "Pan de molde":   ("Panadería", "paquete", 7, 500, 265, 9, 49, 3.2, 2.7),
    # Enlatados
    "Atún en lata":   ("Enlatados", "unidad", 365, 140, 116, 26, 0, 1, 0),
    "Maíz en lata":   ("Enlatados", "unidad", 365, 300, 81, 2.4, 18, 1, 2),
    # Bebidas
    "Jugo de naranja": ("Bebidas", "litro", 7, 1040, 45, 0.7, 10, 0.2, 0.2),
    # Otros
    "Aceite":         ("Otros", "botella", 365, 920, 884, 0, 0, 100, 0),
    "Azúcar":         ("Otros", "lb", 365, 450, 387, 0, 100, 0, 0),
}

NUTRIENTES = ("kcal", "proteina", "carbohidratos", "grasa", "fibra")

_GRAMOS_POR_UNIDAD = {"kg": 1000, "g": 1, "lb": 453.6, "litro": 1000, "ml": 1}


def buscar(nombre):
    """Devuelve la ficha del catálogo (sin distinguir mayúsculas) o None."""
    clave = str(nombre).strip().lower()
    # Acepta plurales simples: "manzanas" -> "manzana", "limones" -> "limón".
    candidatos = {clave, clave[:-1], clave[:-2]} if len(clave) > 3 else {clave}
    sin_tildes = str.maketrans("áéíóú", "aeiou")
    candidatos = {c.translate(sin_tildes) for c in candidatos}
    for nombre_cat, datos in CATALOGO.items():
        if nombre_cat.lower().translate(sin_tildes) in candidatos:
            return nombre_cat, datos
    return None


def por_categoria():
    grupos = {}
    for nombre, datos in CATALOGO.items():
        grupos.setdefault(datos[0], []).append(nombre)
    return grupos


def fecha_sugerida(nombre):
    ficha = buscar(nombre)
    dias = ficha[1][2] if ficha else 7
    return (date.today() + timedelta(days=dias)).isoformat()


def nutricion_100g(nombre):
    ficha = buscar(nombre)
    if not ficha:
        return None
    return dict(zip(NUTRIENTES, ficha[1][4:]))


def gramos(nombre, cantidad, unidad):
    ficha = buscar(nombre)
    if not ficha:
        return None
    peso_unidad = ficha[1][3]
    if unidad in _GRAMOS_POR_UNIDAD:
        factor = _GRAMOS_POR_UNIDAD[unidad]
    elif unidad == "docena":
        factor = 12 * peso_unidad
    else:  # unidad, bolsa, botella, paquete, caja
        factor = peso_unidad
    return float(cantidad) * factor


def nutricion_total(nombre, cantidad, unidad):
    """Nutrientes de la cantidad indicada, o None si no está en el catálogo."""
    base = nutricion_100g(nombre)
    peso = gramos(nombre, cantidad, unidad)
    if base is None or peso is None:
        return None
    return {k: v * peso / 100 for k, v in base.items()}


def texto_nutricion(n, sufijo=""):
    if not n:
        return "Sin datos nutricionales"
    return (
        f"{n['kcal']:.0f} kcal{sufijo}  ·  Proteína {n['proteina']:.1f} g  ·  "
        f"Carbs {n['carbohidratos']:.1f} g  ·  Grasa {n['grasa']:.1f} g  ·  "
        f"Fibra {n['fibra']:.1f} g"
    )
