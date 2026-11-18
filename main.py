from inventario import (
    registrar_alimento,
    mostrar_inventario,
    modificar_alimento,
    eliminar_alimento
)

from gestion import (
    cargar_datos,
    guardar_datos,
    menu_busquedas,
    ordenar_por_vencimiento
)

from aprovechamiento import (
    consultar_vencimientos,
    consultar_recetas,
    registrar_movimiento,
    mostrar_estadisticas
)

from interfaz import iniciar_interfaz

if __name__ == "__main__":
    iniciar_interfaz()

def guardar_si_hubo_cambios(inventario, hubo_cambios):
    if hubo_cambios and not guardar_datos(inventario):
        print("ADVERTENCIA: el cambio esta solo en memoria; no pudo guardarse.")

def menu_inventario(inventario):
    while True:
        print("\n--- INVENTARIO ---")
        print("1. Registrar")
        print("2. Mostrar productos")
        print("3. Buscar por nombre o codigo")
        print("4. Modificar")
        print("5. Eliminar")
        print("6. Ordenar por vencimiento")
        print("0. Volver")

        op = input("Opcion: ").strip()

        if op == "1":
            guardar_si_hubo_cambios(
                inventario,
                registrar_alimento(inventario)
            )

        elif op == "2":
            mostrar_inventario(inventario)

        elif op == "3":
            menu_busquedas(inventario)

        elif op == "4":
            guardar_si_hubo_cambios(
                inventario,
                modificar_alimento(inventario)
            )

        elif op == "5":
            guardar_si_hubo_cambios(
                inventario,
                eliminar_alimento(inventario)
            )

        elif op == "6":
            for alimento in ordenar_por_vencimiento(inventario):
                alimento.mostrar_informacion()

        elif op == "0":
            return

        else:
            print("Opcion no valida.")

def menu_aprovechamiento(inventario):
    while True:
        print("\n--- APROVECHAMIENTO ---")
        print("1. Registrar alimento aprovechado o descartado")
        print("2. Ver estadisticas e Indice de Rescate")
        print("0. Volver")

        op = input("Opcion: ").strip()

        if op == "1":
            guardar_si_hubo_cambios(
                inventario,
                registrar_movimiento(inventario)
            )

        elif op == "2":
            mostrar_estadisticas(inventario)

        elif op == "0":
            return

        else:
            print("Opcion no valida.")

def iniciar_programa():
    try:
        inventario = cargar_datos()

    except RuntimeError as error:
        print(error)
        print("No se abrira el inventario para evitar sobrescribir datos.")
        return

    while True:
        print("\n========== CERO DESPERDICIO ==========")
        print("1. Inventario")
        print("2. Vencimientos por categoria")
        print("3. Recetas con ingredientes")
        print("4. Aprovechamiento y estadisticas")
        print("0. Salir")
        print("======================================")

        op = input("Opcion: ").strip()

        if op == "1":
            menu_inventario(inventario)

        elif op == "2":
            consultar_vencimientos(inventario)

        elif op == "3":
            consultar_recetas(inventario)

        elif op == "4":
            menu_aprovechamiento(inventario)

        elif op == "0":
            print("Hasta luego.")
            return

        else:
            print("Opcion no valida.")

if __name__ == "__main__":
    iniciar_programa()