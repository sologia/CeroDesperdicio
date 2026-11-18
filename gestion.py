import os
import pickle
from inventario import Alimento

CARPETA_DATOS = os.path.join(
    os.path.dirname(__file__),
    "datos"
)

RUTA_ARCHIVO = os.path.join(
    CARPETA_DATOS,
    "inventario.dat"
)

def cargar_datos():
    if not os.path.exists(RUTA_ARCHIVO):
        return []

    try:
        with open(RUTA_ARCHIVO, "rb") as archivo:
            datos = pickle.load(archivo)

        if not isinstance(datos, list) or not all(
            isinstance(a, Alimento) for a in datos
        ):
            raise ValueError("Formato de inventario invalido")

        for alimento in datos:
            for campo in (
                "cantidad_aprovechada",
                "cantidad_desperdiciada",
                "puntos_rescate"
            ):
                if not hasattr(alimento, campo):
                    setattr(alimento, campo, 0)

        return datos

    except (
        OSError,
        EOFError,
        pickle.UnpicklingError,
        ValueError,
        AttributeError,
        ImportError
    ) as error:
        raise RuntimeError(
            f"No se pudo abrir el inventario: {error}"
        ) from error

def guardar_datos(inventario):
    try:
        os.makedirs(CARPETA_DATOS, exist_ok=True)

        temporal = RUTA_ARCHIVO + ".tmp"

        with open(temporal, "wb") as archivo:
            pickle.dump(inventario, archivo)

        os.replace(temporal, RUTA_ARCHIVO)

        return True

    except (OSError, pickle.PickleError) as error:
        print(f"Error al guardar: {error}")
        return False

def busqueda_lineal(inventario, texto):
    return [
        alimento
        for alimento in inventario
        if texto.casefold() in alimento.nombre.casefold()
    ]

def ordenar_por_codigo(inventario):
    return sorted(
        inventario,
        key=lambda alimento: alimento.codigo
    )

def busqueda_binaria(inventario, codigo):
    ordenados = ordenar_por_codigo(inventario)

    izquierda = 0
    derecha = len(ordenados) - 1

    while izquierda <= derecha:
        medio = (izquierda + derecha) // 2

        if ordenados[medio].codigo == codigo:
            return ordenados[medio]

        elif ordenados[medio].codigo < codigo:
            izquierda = medio + 1

        else:
            derecha = medio - 1

    return None

def ordenar_por_vencimiento(inventario):
    resultado = inventario[:]

    for i in range(1, len(resultado)):
        actual = resultado[i]
        j = i - 1

        while (
            j >= 0
            and (
                resultado[j].fecha_vencimiento,
                resultado[j].codigo
            ) > (
                actual.fecha_vencimiento,
                actual.codigo
            )
        ):
            resultado[j + 1] = resultado[j]
            j -= 1

        resultado[j + 1] = actual

    return resultado

def menu_busquedas(inventario):
    print("\n--- BUSQUEDAS ---")
    print("1. Buscar por nombre (lineal)")
    print("2. Buscar por codigo (binaria)")

    opcion = input("Opcion: ").strip()

    if opcion == "1":
        nombre = input("Nombre: ").strip()
        encontrados = busqueda_lineal(inventario, nombre)

        for alimento in encontrados:
            alimento.mostrar_informacion()

        if not encontrados:
            print("No se encontraron productos.")

    elif opcion == "2":
        try:
            codigo = int(input("Codigo: "))

            alimento = busqueda_binaria(
                inventario,
                codigo
            )

            if alimento:
                alimento.mostrar_informacion()
            else:
                print("No se encontro ese codigo.")

        except ValueError:
            print("Codigo incorrecto.")

    else:
        print("Opcion incorrecta.")