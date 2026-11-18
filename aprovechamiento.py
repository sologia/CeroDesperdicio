from datetime import date

from inventario import (
    leer_codigo,
    leer_cantidad,
    localizar_alimento
)

class Nodo:
    def __init__(self, alimento):
        self.alimento = alimento
        self.izquierda = None
        self.derecha = None

class ArbolVencimientos:
    def __init__(self):
        self.raiz = None

    def insertar(self, alimento):
        self.raiz = self._insertar(
            self.raiz,
            alimento
        )

    def _insertar(self, nodo, alimento):
        if nodo is None:
            return Nodo(alimento)

        clave = (
            alimento.fecha_vencimiento,
            alimento.codigo
        )

        clave_nodo = (
            nodo.alimento.fecha_vencimiento,
            nodo.alimento.codigo
        )

        if clave < clave_nodo:
            nodo.izquierda = self._insertar(
                nodo.izquierda,
                alimento
            )

        elif clave > clave_nodo:
            nodo.derecha = self._insertar(
                nodo.derecha,
                alimento
            )

        return nodo

    def recorrido_inorden(self):
        resultado = []

        def visitar(nodo):
            if nodo is not None:
                visitar(nodo.izquierda)
                resultado.append(nodo.alimento)
                visitar(nodo.derecha)

        visitar(self.raiz)

        return resultado

def construir_arbol(inventario):
    arbol = ArbolVencimientos()

    for alimento in inventario:
        arbol.insertar(alimento)

    return arbol

def consultar_vencimientos(inventario):
    print("\n--- VENCIMIENTOS POR CATEGORIA ---")

    if not inventario:
        print("No hay alimentos registrados.")
        return

    categorias = sorted(
        {a.categoria for a in inventario},
        key=str.casefold
    )

    print("0. Todas las categorias")

    for i, categoria in enumerate(categorias, start=1):
        print(f"{i}. {categoria}")

    try:
        opcion = int(input("Selecciona categoria: "))

        if opcion < 0 or opcion > len(categorias):
            print("Categoria no valida.")
            return

    except ValueError:
        print("Opcion no valida.")
        return

    print("\n1. Proximos 7 dias o vencidos")
    print("2. Todos los productos, ordenados por fecha")

    modo = input("Selecciona vista: ").strip()

    if modo not in ("1", "2"):
        print("Opcion no valida.")
        return

    arbol = construir_arbol(inventario)
    hoy = date.today()
    encontrados = 0

    for alimento in arbol.recorrido_inorden():

        if opcion and alimento.categoria != categorias[opcion - 1]:
            continue

        if alimento.cantidad <= 0:
            continue

        dias = (
            date.fromisoformat(alimento.fecha_vencimiento)
            - hoy
        ).days

        if modo == "1" and dias > 7:
            continue

        if dias < 0:
            estado = f"VENCIDO hace {-dias} dias"

        elif dias == 0:
            estado = "VENCE HOY"

        elif dias <= 7:
            estado = f"VENCE en {dias} dias"

        else:
            estado = f"Faltan {dias} dias"

        print(
            f"{alimento.categoria} | "
            f"{alimento.nombre} | "
            f"{alimento.fecha_vencimiento} | "
            f"{estado}"
        )

        encontrados += 1

    if not encontrados:
        print("No hay productos para ese filtro.")

class GrafoRecetas:
    def __init__(self):
        self.adyacencia = {}
        self.recetas = {}

    def agregar_receta(self, nombre, ingredientes):
        self.recetas[nombre] = ingredientes

        nodo_receta = "receta:" + nombre

        self.adyacencia.setdefault(
            nodo_receta,
            set()
        )

        for ingrediente in ingredientes:
            nodo_ing = "ingrediente:" + ingrediente

            self.adyacencia.setdefault(
                nodo_ing,
                set()
            ).add(nodo_receta)

            self.adyacencia[nodo_receta].add(
                nodo_ing
            )

    def recetas_posibles(self, disponibles):
        resultado = []

        for receta, ingredientes in self.recetas.items():
            if all(
                ingrediente in disponibles
                for ingrediente in ingredientes
            ):
                resultado.append(receta)

        return resultado

    def recetas_relacionadas(self, ingrediente):
        vecinos = self.adyacencia.get(
            "ingrediente:" + ingrediente,
            set()
        )

        return sorted(
            nodo.removeprefix("receta:")
            for nodo in vecinos
        )


def crear_grafo_recetas():
    grafo = GrafoRecetas()

    grafo.agregar_receta(
        "Ensalada",
        ["tomate", "cebolla"]
    )

    grafo.agregar_receta(
        "Sopa de pollo",
        ["pollo", "cebolla", "zanahoria"]
    )

    grafo.agregar_receta(
        "Arroz con pollo",
        ["arroz", "pollo", "cebolla"]
    )

    grafo.agregar_receta(
        "Pizza sencilla",
        ["queso", "tomate"]
    )

    return grafo


def consultar_recetas(inventario):
    print("\n--- RECETAS ---")

    grafo = crear_grafo_recetas()
    hoy = date.today()

    disponibles = {
        alimento.nombre.casefold().strip()
        for alimento in inventario
        if (
            alimento.cantidad > 0
            and date.fromisoformat(
                alimento.fecha_vencimiento
            ) >= hoy
        )
    }

    print(
        "Ingredientes disponibles:",
        ", ".join(sorted(disponibles)) or "ninguno"
    )

    posibles = grafo.recetas_posibles(disponibles)

    if posibles:
        print("\nRecetas posibles:")

        for receta in posibles:
            print("- " + receta)

    else:
        print(
            "No hay recetas completas con los ingredientes registrados."
        )

    print("\nRelaciones del grafo:")

    ingredientes = {
        ingrediente
        for lista in grafo.recetas.values()
        for ingrediente in lista
    }

    for ingrediente in sorted(ingredientes):
        relacionadas = grafo.recetas_relacionadas(
            ingrediente
        )

        print(
            f"{ingrediente} -> "
            f"{', '.join(relacionadas)}"
        )

    print(
        "\nNota: las recetas son demostrativas; "
        "no verifican cantidades por porcion."
    )


def registrar_movimiento(inventario):
    print("\n--- APROVECHAMIENTO / DESCARTE ---")

    codigo = leer_codigo("Codigo: ")

    alimento = localizar_alimento(
        inventario,
        codigo
    )

    if alimento is None:
        print("Alimento no encontrado.")
        return False

    if alimento.cantidad <= 0:
        print("No queda cantidad disponible.")
        return False

    print("1. Aprovechado")
    print("2. Descartado")

    opcion = input("Opcion: ").strip()

    if opcion not in ("1", "2"):
        print("Opcion no valida.")
        return False

    dias = (
        date.fromisoformat(alimento.fecha_vencimiento)
        - date.today()
    ).days

    if opcion == "1" and dias < 0:
        print(
            "No se puede registrar como aprovechado "
            "un alimento vencido."
        )
        return False

    cantidad = leer_cantidad(
        f"Cantidad (maximo {alimento.cantidad:g} "
        f"{alimento.unidad}): ",
        maximo=alimento.cantidad
    )

    alimento.cantidad -= cantidad

    if opcion == "1":
        alimento.cantidad_aprovechada += cantidad

        if 0 <= dias <= 7:
            alimento.puntos_rescate += cantidad * 10

        print("Aprovechamiento registrado.")

    else:
        alimento.cantidad_desperdiciada += cantidad
        print("Descarte registrado.")

    return True

def mostrar_estadisticas(inventario):
    print("\n--- ESTADISTICAS ---")

    total = len(inventario)

    aprovechado = sum(
        a.cantidad_aprovechada
        for a in inventario
    )

    descartado = sum(
        a.cantidad_desperdiciada
        for a in inventario
    )

    puntos = sum(
        a.puntos_rescate
        for a in inventario
    )

    print("Productos registrados:", total)

    print(
        f"Cantidad aprovechada "
        f"(unidades mixtas): {aprovechado:g}"
    )

    print(
        f"Cantidad descartada "
        f"(unidades mixtas): {descartado:g}"
    )

    print(
        f"Indice de Rescate (puntos): {puntos:g}"
    )

    print(
        "Nota: las cantidades mezclan unidades; "
        "deben interpretarse por producto."
    )