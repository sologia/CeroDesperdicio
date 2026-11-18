"""Generador de recetas sin conexión (respaldo cuando la IA no está disponible).

Arma recetas a partir de plantillas simples, priorizando los alimentos que
vencen primero, y calcula la información nutricional con el catálogo.
"""

from datetime import date

import catalogo

PORCIONES = 2

# Gramos usados por ingrediente según categoría (para 2 porciones).
_GRAMOS_CATEGORIA = {
    "Carnes": 300, "Verduras": 150, "Frutas": 200, "Lácteos": 150,
    "Granos y cereales": 160, "Panadería": 120, "Enlatados": 140,
    "Bebidas": 400, "Otros": 15,
}
_GRAMOS_ESPECIALES = {
    "Huevos": 200, "Aceite": 15, "Mantequilla": 20, "Ajo": 10,
    "Limón": 30, "Azúcar": 15, "Queso": 60, "Crema": 40,
}


def _dias(alimento):
    try:
        return (date.fromisoformat(str(alimento.fecha_vencimiento)) - date.today()).days
    except (ValueError, TypeError):
        return 999


def _categoria(alimento):
    ficha = catalogo.buscar(alimento.nombre)
    return ficha[1][0] if ficha else str(alimento.categoria).strip().title()


def _gramos(alimento):
    nombre = alimento.nombre.strip().title()
    deseado = _GRAMOS_ESPECIALES.get(
        nombre, _GRAMOS_CATEGORIA.get(_categoria(alimento), 150)
    )
    disponible = catalogo.gramos(alimento.nombre, alimento.cantidad, alimento.unidad)
    return min(deseado, disponible) if disponible else deseado


def _de(alimentos, *categorias, nombres=()):
    return [
        a for a in alimentos
        if _categoria(a) in categorias or a.nombre.strip().lower() in nombres
    ]


def _plantillas(a):
    """Devuelve (nombre, ingredientes, pasos) posibles con lo disponible."""
    nombres = {x.nombre.strip().lower(): x for x in a}
    huevos = nombres.get("huevos")
    proteinas = _de(a, "Carnes", nombres=("atún en lata",))
    verduras = _de(a, "Verduras")
    frutas = _de(a, "Frutas")
    granos = [nombres[n] for n in ("arroz", "pasta", "tortillas") if n in nombres]
    lacteos = [nombres[n] for n in ("leche", "yogur") if n in nombres]
    pan = nombres.get("pan de molde")
    queso = nombres.get("queso")
    recetas = []

    if proteinas and verduras:
        p = proteinas[0]
        ing = [p] + verduras[:3] + granos[:1]
        recetas.append((f"Salteado de {p.nombre.lower()} con verduras", ing, [
            f"Corta {p.nombre.lower()} en trozos pequeños y sazona con sal y pimienta.",
            "Pica las verduras en tiras o cubos del mismo tamaño.",
            f"Dora {p.nombre.lower()} en un sartén caliente con un poco de aceite (6-8 min).",
            "Agrega las verduras y saltea a fuego alto 4-5 minutos, que queden crujientes.",
            ("Sirve acompañado de " + granos[0].nombre.lower() + " cocido.")
            if granos else "Sirve caliente.",
        ]))

    if huevos:
        ing = [huevos] + verduras[:2] + ([queso] if queso else [])
        recetas.append(("Tortilla de huevo con lo que hay", ing, [
            "Bate los huevos con una pizca de sal.",
            "Sofríe las verduras picadas 3 minutos en un sartén con aceite.",
            "Vierte los huevos, baja el fuego y tapa 5 minutos.",
            ("Agrega el queso por encima, " if queso else "") + "dobla y sirve.",
        ]))

    if len(verduras) >= 2:
        ing = verduras[:4] + proteinas[:1] + [g for g in granos if g.nombre.lower() == "arroz"][:1]
        recetas.append(("Sopa casera de aprovechamiento", ing, [
            "Pica todos los ingredientes en cubos.",
            "Sofríe cebolla/ajo (si tienes) en una olla con un poco de aceite.",
            "Agrega el resto, cubre con 1 litro de agua y sal al gusto.",
            "Cocina a fuego medio 25-30 minutos hasta que todo esté suave.",
        ]))

    acompanantes = proteinas + verduras
    for i, g in enumerate(granos):
        if not acompanantes:
            break
        principal = acompanantes[i % len(acompanantes)]
        nombre_g = g.nombre.lower()
        if nombre_g == "tortillas":
            ing = [g, principal] + ([queso] if queso else []) + verduras[:1]
            recetas.append((f"Quesadillas de {principal.nombre.lower()}" if queso
                            else f"Tacos de {principal.nombre.lower()}", ing, [
                f"Cocina {principal.nombre.lower()} en trozos pequeños con sal y especias.",
                "Calienta las tortillas en un comal.",
                "Rellena cada tortilla" + (", agrega queso" if queso else "")
                + " y dóblala; dora 1-2 minutos por lado.",
                "Sirve con salsa o limón si tienes.",
            ]))
            continue
        ing = [g, principal] + verduras[:2] + ([queso] if queso and nombre_g == "pasta" else [])
        recetas.append((f"{g.nombre.title()} con {principal.nombre.lower()}", ing, [
            f"Cocina {nombre_g} según el empaque y escurre si hace falta.",
            "Mientras tanto, saltea los demás ingredientes picados con un poco de aceite.",
            f"Mezcla todo con {nombre_g}, ajusta la sal y sirve caliente.",
        ]))

    if frutas:
        ing = frutas[:2] + lacteos[:1]
        recetas.append(("Licuado de " + " y ".join(f.nombre.lower() for f in frutas[:2]), ing, [
            "Pela y corta la fruta en trozos.",
            "Licúa con " + (lacteos[0].nombre.lower() if lacteos else "un vaso de agua") + " y hielo.",
            "Sirve frío de inmediato.",
        ]))

    if pan:
        ing = [pan] + proteinas[:1] + ([queso] if queso else []) + verduras[:2]
        recetas.append(("Sándwich completo", ing, [
            "Tuesta ligeramente el pan.",
            "Arma capas con los ingredientes en rodajas finas.",
            "Cierra, corta en diagonal y sirve.",
        ]))

    if len(verduras) + len(frutas) >= 2:
        ing = (verduras + frutas)[:4]
        recetas.append(("Ensalada fresca de la nevera", ing, [
            "Lava bien y corta todos los ingredientes.",
            "Mezcla en un bol con sal, limón y un chorrito de aceite.",
            "Sirve al momento para que no pierda frescura.",
        ]))

    if not recetas:
        ing = a[:4]
        recetas.append(("Plato de aprovechamiento rápido", ing, [
            "Lava y corta los ingredientes.",
            "Cocina primero los más duros y luego los más suaves en un sartén con aceite.",
            "Sazona al gusto y sirve.",
        ]))
    return recetas


def _formato_nutricion(n):
    if not n["kcal"]:
        return "Calorías: sin datos (ingredientes fuera del catálogo)"
    return (
        f"Calorías: {n['kcal']:.0f} kcal | Proteína: {n['proteina']:.1f} g | "
        f"Carbohidratos: {n['carbohidratos']:.1f} g | Grasa: {n['grasa']:.1f} g | "
        f"Fibra: {n['fibra']:.1f} g"
    )


def generar(alimentos, cantidad=3):
    ordenados = sorted(alimentos, key=_dias)
    vistos = set()
    salida = []

    for nombre, ingredientes, pasos in _plantillas(ordenados):
        ingredientes = [i for i in dict.fromkeys(ingredientes) if i is not None]
        clave = frozenset(id(i) for i in ingredientes)
        if clave in vistos:
            continue
        vistos.add(clave)

        total = dict.fromkeys(catalogo.NUTRIENTES, 0.0)
        lineas = []
        for ing in ingredientes:
            g = _gramos(ing)
            base = catalogo.nutricion_100g(ing.nombre)
            if base:
                for k in total:
                    total[k] += base[k] * g / 100
            lineas.append(f"- {ing.nombre} - {g:.0f} g aprox.")

        porcion = {k: v / PORCIONES for k, v in total.items()}
        urgentes = [i.nombre for i in ingredientes if 0 <= _dias(i) <= 3]

        salida += [
            f"RECETA: {nombre}",
            f"Porciones: {PORCIONES}   Tiempo: {10 + 5 * len(pasos)} minutos",
            "Ingredientes:",
            *lineas,
            "Preparación:",
            *[f"{n}. {p}" for n, p in enumerate(pasos, 1)],
            "Información nutricional por porción:",
            _formato_nutricion(porcion),
            "Información nutricional del platillo completo:",
            _formato_nutricion(total),
            "Aprovecha:",
            "- " + (", ".join(urgentes) + " (vencen pronto)" if urgentes
                    else ", ".join(i.nombre for i in ingredientes)),
            "",
        ]
        if len(vistos) >= cantidad:
            break

    return "\n".join(salida)
