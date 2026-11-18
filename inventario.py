from datetime import date
import math


class Alimento:
    def __init__(
        self,
        codigo,
        nombre,
        cantidad,
        unidad,
        fecha_vencimiento,
        categoria,
        cantidad_aprovechada=0,
        cantidad_desperdiciada=0,
        puntos_rescate=0
    ):
        self.codigo = codigo
        self.nombre = nombre
        self.cantidad = cantidad
        self.unidad = unidad
        self.fecha_vencimiento = fecha_vencimiento
        self.categoria = categoria
        self.cantidad_aprovechada = cantidad_aprovechada
        self.cantidad_desperdiciada = cantidad_desperdiciada
        self.puntos_rescate = puntos_rescate

    def mostrar_informacion(self):
        print(
            f"[{self.codigo}] {self.nombre} | "
            f"{self.categoria} | "
            f"{self.cantidad:g} {self.unidad} | "
            f"vence: {self.fecha_vencimiento}"
        )


def generar_codigo(inventario):
    codigos = []

    for alimento in inventario:
        try:
            codigos.append(int(alimento.codigo))
        except (TypeError, ValueError):
            continue

    return max(codigos, default=0) + 1


def leer_fecha(mensaje):
    while True:
        texto = input(mensaje).strip()

        try:
            return date.fromisoformat(texto).isoformat()
        except ValueError:
            print("Fecha incorrecta. Utiliza AAAA-MM-DD.")


def leer_cantidad(mensaje, maximo=None):
    while True:
        try:
            cantidad = float(input(mensaje).replace(",", "."))

            if not math.isfinite(cantidad) or cantidad <= 0:
                print("La cantidad debe ser positiva y finita.")

            elif maximo is not None and cantidad > maximo:
                print(
                    f"No puedes superar la cantidad disponible ({maximo:g})."
                )

            else:
                return cantidad

        except ValueError:
            print("Introduce un número válido.")


def leer_codigo(mensaje):
    while True:
        try:
            codigo = int(input(mensaje))

            if codigo > 0:
                return codigo

            print("El código debe ser mayor que cero.")

        except ValueError:
            print("Introduce un código numérico.")


def leer_texto(mensaje):
    while True:
        texto = input(mensaje).strip()

        if texto:
            return texto

        print("Este campo no puede quedar vacío.")


def localizar_alimento(inventario, codigo):
    for alimento in inventario:
        if str(alimento.codigo) == str(codigo):
            return alimento

    return None


def registrar_alimento(inventario):
    print("\n--- REGISTRAR ALIMENTO ---")

    codigo = generar_codigo(inventario)
    nombre = leer_texto("Nombre: ")
    categoria = leer_texto("Categoría: ")
    cantidad = leer_cantidad("Cantidad: ")

    unidades = (
        "unidad", "kg", "g", "lb", "litro",
        "ml", "bolsa", "botella", "paquete",
        "caja", "docena"
    )

    print("Unidades disponibles:", ", ".join(unidades))

    while True:
        unidad = leer_texto("Unidad: ").lower()

        if unidad in unidades:
            break

        print("Selecciona una unidad de la lista.")

    vencimiento = leer_fecha("Vencimiento (AAAA-MM-DD): ")

    alimento = Alimento(
        codigo,
        nombre,
        cantidad,
        unidad,
        vencimiento,
        categoria
    )

    inventario.append(alimento)

    print(f"Alimento registrado con código {codigo}.")
    return True


def mostrar_inventario(inventario):
    print("\n--- INVENTARIO ---")

    if not inventario:
        print("No hay alimentos registrados.")
        return

    for alimento in inventario:
        alimento.mostrar_informacion()


def modificar_alimento(inventario):
    print("\n--- MODIFICAR ALIMENTO ---")

    codigo = leer_codigo("Código del alimento: ")
    alimento = localizar_alimento(inventario, codigo)

    if alimento is None:
        print("No se encontró ese alimento.")
        return False

    print("Ingresa los nuevos datos (el código no cambia).")

    alimento.nombre = leer_texto("Nombre: ")
    alimento.categoria = leer_texto("Categoría: ")
    alimento.cantidad = leer_cantidad("Cantidad disponible: ")

    unidades = (
        "unidad", "kg", "g", "lb", "litro",
        "ml", "bolsa", "botella", "paquete",
        "caja", "docena"
    )

    print("Unidades disponibles:", ", ".join(unidades))

    while True:
        unidad = leer_texto("Unidad: ").lower()

        if unidad in unidades:
            alimento.unidad = unidad
            break

        print("Selecciona una unidad de la lista.")

    alimento.fecha_vencimiento = leer_fecha(
        "Vencimiento (AAAA-MM-DD): "
    )

    print("Alimento modificado.")
    return True


def eliminar_alimento(inventario):
    print("\n--- ELIMINAR ALIMENTO ---")

    codigo = leer_codigo("Código del alimento: ")
    alimento = localizar_alimento(inventario, codigo)

    if alimento is None:
        print("No se encontró ese alimento.")
        return False

    confirmacion = input(
        f"¿Eliminar {alimento.nombre}? (s/n): "
    ).strip().lower()

    if confirmacion != "s":
        print("Operación cancelada.")
        return False

    inventario.remove(alimento)

    print("Alimento eliminado.")
    return True