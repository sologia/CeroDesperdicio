
# COLORES PRINCIPALES
FONDO = "#11131C"
PANEL = "#1B1F2D"
PANEL_SECUNDARIO = "#242A3B"
PANEL_CLARO = "#30384D"

MORADO = "#8B75F5"
MORADO_CLARO = "#AA9BFF"
AZUL = "#4C9AFF"
TURQUESA = "#40C9B5"

CORAL = "#FF777F"
AMARILLO = "#F2B85B"
EXITO = "#48C995"

BLANCO = "#FFFFFF"
TEXTO = "#E8EAF2"
GRIS = "#A1A9BC"
BORDE = "#343B50"

VERDE = EXITO
VERDE_OSCURO = PANEL
VERDE_CLARO = MORADO_CLARO

FUENTE = "Segoe UI"


def configurar_estilos(ventana):
    import tkinter as tk
    from tkinter import ttk

    ventana.configure(bg=FONDO)

    estilo = ttk.Style(ventana)
    estilo.theme_use("clam")

    estilo.configure(
        "Treeview",
        background=PANEL,
        fieldbackground=PANEL,
        foreground=TEXTO,
        rowheight=38,
        borderwidth=0,
        font=(FUENTE, 10)
    )

    estilo.map(
        "Treeview",
        background=[("selected", "#49416F")],
        foreground=[("selected", BLANCO)]
    )

    estilo.configure(
        "Treeview.Heading",
        background=PANEL_CLARO,
        foreground=BLANCO,
        font=(FUENTE, 9, "bold"),
        padding=11,
        borderwidth=0
    )

    estilo.map(
        "Treeview.Heading",
        background=[("active", MORADO)]
    )

    estilo.configure(
        "Vertical.TScrollbar",
        background=PANEL_CLARO,
        troughcolor=FONDO,
        bordercolor=FONDO,
        arrowcolor=BLANCO
    )
