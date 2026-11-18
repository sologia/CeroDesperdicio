
import tkinter as tk
from tkinter import ttk, messagebox
from datetime import date
import calendar
import threading

from inventario import Alimento, localizar_alimento, generar_codigo
from gestion import (
    cargar_datos,
    guardar_datos,
    busqueda_lineal,
    ordenar_por_codigo,
    ordenar_por_vencimiento
)
from asistente_ia import consultar_ia, generar_recetas
from estilos import *


class Aplicacion:

    def __init__(self, ventana):
        self.ventana = ventana
        self.ventana.title("Cero Desperdicio")
        self.ventana.minsize(1050, 680)
        try:
            self.ventana.state("zoomed")
        except tk.TclError:
            self.ventana.attributes("-zoomed", True)

        configurar_estilos(ventana)

        try:
            self.inventario = cargar_datos()
        except Exception as error:
            self.inventario = []
            messagebox.showwarning("Aviso", str(error))

        self.menu_actual = "Inicio"
        self.botones_menu = {}

        self.contenedor = tk.Frame(ventana, bg=FONDO)
        self.contenedor.pack(fill="both", expand=True)

        self.crear_menu()

        self.contenido = tk.Frame(
            self.contenedor,
            bg=FONDO
        )
        self.contenido.pack(side="right", fill="both", expand=True)

        self.seleccionar_menu("Inicio", self.mostrar_inicio)
        self.ventana.protocol("WM_DELETE_WINDOW", self.cerrar)

    # ==================================================
    # ELEMENTOS GENERALES
    # ==================================================

    def crear_menu(self):
        self.menu = tk.Frame(
            self.contenedor,
            bg=PANEL,
            width=245
        )
        self.menu.pack(side="left", fill="y")
        self.menu.pack_propagate(False)

        tk.Label(
            self.menu,
            text="✦",
            bg=PANEL,
            fg=AMARILLO,
            font=("Segoe UI", 34, "bold")
        ).pack(anchor="w", padx=24, pady=(28, 0))

        tk.Label(
            self.menu,
            text="CERO DESPERDICIO",
            bg=PANEL,
            fg=BLANCO,
            font=("Segoe UI", 15, "bold")
        ).pack(anchor="w", padx=22, pady=(0, 5))

        tk.Label(
            self.menu,
            text="Aprovecha más. Desperdicia menos.",
            bg=PANEL,
            fg=GRIS,
            font=("Segoe UI", 8)
        ).pack(anchor="w", padx=22, pady=(0, 35))

        opciones = [
            ("Inicio", "⌂", self.mostrar_inicio),
            ("Inventario", "▣", self.mostrar_inventario),
            ("Buscar alimentos", "⌕", self.buscar_alimentos),
            ("Vencimientos", "◷", self.mostrar_vencimientos),
            ("Recetas con IA", "♨", self.mostrar_recetas),
            ("Estadísticas", "▤", self.mostrar_estadisticas),
            ("Asistente IA", "✦", self.mostrar_asistente)
        ]

        for nombre, icono, comando in opciones:
            boton = tk.Button(
                self.menu,
                text=f"  {icono}    {nombre}",
                command=lambda n=nombre, c=comando:
                    self.seleccionar_menu(n, c),
                bg=PANEL,
                fg=GRIS,
                activebackground=PANEL_CLARO,
                activeforeground=BLANCO,
                font=("Segoe UI", 10),
                relief="flat",
                bd=0,
                anchor="w",
                padx=18,
                pady=14,
                cursor="hand2"
            )

            boton.pack(fill="x", padx=12, pady=3)
            self.botones_menu[nombre] = boton

            boton.bind(
                "<Enter>",
                lambda e, b=boton, n=nombre:
                    self.animar_boton(b, n, True)
            )

            boton.bind(
                "<Leave>",
                lambda e, b=boton, n=nombre:
                    self.animar_boton(b, n, False)
            )

    def seleccionar_menu(self, nombre, comando):
        self.menu_actual = nombre

        for opcion, boton in self.botones_menu.items():
            if opcion == nombre:
                boton.configure(
                    bg="#49416F",
                    fg=BLANCO,
                    font=("Segoe UI", 10, "bold")
                )
            else:
                boton.configure(
                    bg=PANEL,
                    fg=GRIS,
                    font=("Segoe UI", 10)
                )

        comando()

    def animar_boton(self, boton, nombre, entrando):
        if nombre == self.menu_actual:
            boton.configure(bg="#49416F", fg=BLANCO)
        elif entrando:
            boton.configure(bg=PANEL_CLARO, fg=BLANCO)
        else:
            boton.configure(bg=PANEL, fg=GRIS)

    def limpiar(self):
        for elemento in self.contenido.winfo_children():
            elemento.destroy()

    def encabezado(self, titulo, descripcion=""):
        tk.Label(
            self.contenido,
            text=titulo,
            bg=FONDO,
            fg=BLANCO,
            font=("Segoe UI", 24, "bold")
        ).pack(anchor="w", padx=30, pady=(25, 4))

        if descripcion:
            tk.Label(
                self.contenido,
                text=descripcion,
                bg=FONDO,
                fg=GRIS,
                font=("Segoe UI", 10)
            ).pack(anchor="w", padx=32, pady=(0, 20))

    def boton(self, padre, texto, comando, color=MORADO):
        return tk.Button(
            padre,
            text=texto,
            command=comando,
            bg=color,
            fg=BLANCO,
            activebackground=MORADO_CLARO,
            activeforeground=BLANCO,
            font=("Segoe UI", 9, "bold"),
            relief="flat",
            bd=0,
            padx=16,
            pady=10,
            cursor="hand2"
        )

    def tarjeta(self, padre, titulo, valor, color=MORADO):
        marco = tk.Frame(
            padre,
            bg=PANEL,
            padx=16,
            pady=15,
            highlightbackground=BORDE,
            highlightthickness=1
        )
        marco.pack(side="left", expand=True, fill="both", padx=5)

        tk.Label(
            marco,
            text=titulo.upper(),
            bg=PANEL,
            fg=GRIS,
            font=("Segoe UI", 8, "bold")
        ).pack(anchor="w")

        tk.Label(
            marco,
            text=str(valor),
            bg=PANEL,
            fg=color,
            font=("Segoe UI", 21, "bold")
        ).pack(anchor="w", pady=(8, 0))

        return marco

    def panel(self, padre, padding=16):
        return tk.Frame(
            padre,
            bg=PANEL,
            padx=padding,
            pady=padding,
            highlightbackground=BORDE,
            highlightthickness=1
        )

    def crear_tabla(self, padre, columnas, encabezados, anchos=None):
        marco = tk.Frame(padre, bg=PANEL)
        tabla = ttk.Treeview(
            marco,
            columns=columnas,
            show="headings"
        )

        for i, columna in enumerate(columnas):
            tabla.heading(columna, text=encabezados[i])
            ancho = anchos[i] if anchos else 130
            tabla.column(columna, width=ancho, anchor="center")

        barra = ttk.Scrollbar(
            marco,
            orient="vertical",
            command=tabla.yview
        )
        tabla.configure(yscrollcommand=barra.set)

        tabla.pack(side="left", fill="both", expand=True)
        barra.pack(side="right", fill="y")

        return marco, tabla

    # ==================================================
    # INICIO
    # ==================================================

    def mostrar_inicio(self):
        self.limpiar()

        self.encabezado(
            "Panel principal",
            "Controla tus alimentos y descubre cómo reducir el desperdicio."
        )

        tarjetas = tk.Frame(self.contenido, bg=FONDO)
        tarjetas.pack(fill="x", padx=25, pady=10)

        disponibles = sum(
            float(getattr(a, "cantidad", 0))
            for a in self.inventario
        )

        aprovechados = sum(
            float(getattr(a, "cantidad_aprovechada", 0))
            for a in self.inventario
        )

        self.tarjeta(
            tarjetas,
            "Alimentos registrados",
            len(self.inventario),
            MORADO
        )

        self.tarjeta(
            tarjetas,
            "Unidades disponibles",
            f"{disponibles:g}",
            AZUL
        )

        self.tarjeta(
            tarjetas,
            "Unidades aprovechadas",
            f"{aprovechados:g}",
            EXITO
        )

        acciones = self.panel(self.contenido, 22)
        acciones.pack(fill="x", padx=30, pady=25)

        tk.Label(
            acciones,
            text="¿Qué deseas hacer?",
            bg=PANEL,
            fg=BLANCO,
            font=("Segoe UI", 15, "bold")
        ).pack(anchor="w", pady=(0, 15))

        self.boton(
            acciones,
            "+ Registrar alimento",
            self.formulario_alimento
        ).pack(anchor="w", pady=4)

        self.boton(
            acciones,
            "Consultar vencimientos",
            lambda: self.seleccionar_menu(
                "Vencimientos", self.mostrar_vencimientos
            ),
            color=PANEL_CLARO
        ).pack(anchor="w", pady=4)

        self.boton(
            acciones,
            "Generar recetas con IA",
            lambda: self.seleccionar_menu(
                "Recetas con IA", self.mostrar_recetas
            ),
            color=PANEL_CLARO
        ).pack(anchor="w", pady=4)

    # ==================================================
    # INVENTARIO
    # ==================================================

    def mostrar_inventario(self):
        self.limpiar()

        self.encabezado(
            "Mi inventario",
            "Administra todos los alimentos registrados."
        )

        resumen = tk.Frame(self.contenido, bg=FONDO)
        resumen.pack(fill="x", padx=25, pady=5)

        self.tarjeta(
            resumen,
            "Productos",
            len(self.inventario),
            MORADO
        )

        self.tarjeta(
            resumen,
            "Cantidad total",
            f"{sum(float(a.cantidad) for a in self.inventario):g}",
            AZUL
        )

        self.tarjeta(
            resumen,
            "Categorías",
            len(set(a.categoria for a in self.inventario)),
            TURQUESA
        )

        herramientas = self.panel(self.contenido, 14)
        herramientas.pack(fill="x", padx=30, pady=15)

        tk.Label(
            herramientas,
            text="GESTIÓN DE ALIMENTOS",
            bg=PANEL,
            fg=GRIS,
            font=("Segoe UI", 8, "bold")
        ).pack(anchor="w", pady=(0, 10))

        fila = tk.Frame(herramientas, bg=PANEL)
        fila.pack(fill="x")

        self.boton(
            fila,
            "+ Agregar alimento",
            self.formulario_alimento
        ).pack(side="left", padx=(0, 8))

        self.boton(
            fila,
            "Editar seleccionado",
            self.modificar_seleccionado,
            color=PANEL_CLARO
        ).pack(side="left", padx=8)

        self.boton(
            fila,
            "Eliminar",
            self.eliminar_seleccionado,
            color=CORAL
        ).pack(side="left", padx=8)

        self.filtro_categoria = tk.StringVar(value="Todas")

        categorias = sorted(set(
            a.categoria for a in self.inventario
        ))

        filtro = ttk.Combobox(
            fila,
            textvariable=self.filtro_categoria,
            values=["Todas"] + categorias,
            state="readonly",
            width=18
        )
        filtro.pack(side="right", padx=5)
        filtro.bind(
            "<<ComboboxSelected>>",
            lambda e: self.filtrar_inventario()
        )

        tk.Label(
            fila,
            text="Categoría:",
            bg=PANEL,
            fg=GRIS
        ).pack(side="right", padx=5)

        marco, self.tabla = self.crear_tabla(
            self.contenido,
            ("codigo", "nombre", "cantidad", "unidad", "fecha", "categoria"),
            ("Código", "Alimento", "Cantidad", "Unidad", "Vencimiento", "Categoría"),
            (85, 180, 100, 90, 130, 120)
        )
        marco.pack(fill="both", expand=True, padx=30, pady=(0, 25))

        self.actualizar_tabla()

    def actualizar_tabla(self, lista=None):
        for fila in self.tabla.get_children():
            self.tabla.delete(fila)

        alimentos = self.inventario if lista is None else lista

        for a in alimentos:
            self.tabla.insert(
                "",
                "end",
                values=(
                    a.codigo,
                    a.nombre,
                    a.cantidad,
                    a.unidad,
                    a.fecha_vencimiento,
                    a.categoria
                )
            )

    def filtrar_inventario(self):
        categoria = self.filtro_categoria.get()

        if categoria == "Todas":
            self.actualizar_tabla()
        else:
            self.actualizar_tabla([
                a for a in self.inventario
                if a.categoria == categoria
            ])

    def formulario_alimento(self, alimento=None):
        ventana = tk.Toplevel(self.ventana)
        ventana.title("Editar alimento" if alimento else "Registrar alimento")
        ventana.configure(bg=FONDO)
        ventana.resizable(False, False)
        ventana.transient(self.ventana)
        ventana.grab_set()

        # Centrar el formulario respecto a la ventana principal.
        ancho, alto = 600, 760
        ventana.update_idletasks()
        x = self.ventana.winfo_rootx() + max(0, (self.ventana.winfo_width() - ancho) // 2)
        y = self.ventana.winfo_rooty() + max(0, (self.ventana.winfo_height() - alto) // 2)
        ventana.geometry(f"{ancho}x{alto}+{x}+{y}")

        estilo = ttk.Style(ventana)
        estilo.theme_use("clam")
        estilo.configure(
            "Formulario.TCombobox",
            fieldbackground=PANEL_SECUNDARIO,
            background=PANEL_CLARO,
            foreground=BLANCO,
            arrowcolor=MORADO_CLARO,
            bordercolor=BORDE,
            lightcolor=PANEL_SECUNDARIO,
            darkcolor=PANEL_SECUNDARIO,
            padding=10,
            font=("Segoe UI", 10)
        )
        estilo.map(
            "Formulario.TCombobox",
            fieldbackground=[("readonly", PANEL_SECUNDARIO)],
            foreground=[("readonly", BLANCO)],
            selectbackground=[("readonly", PANEL_SECUNDARIO)],
            selectforeground=[("readonly", BLANCO)]
        )
        ventana.option_add("*TCombobox*Listbox.background", PANEL_SECUNDARIO)
        ventana.option_add("*TCombobox*Listbox.foreground", BLANCO)
        ventana.option_add("*TCombobox*Listbox.selectBackground", MORADO)
        ventana.option_add("*TCombobox*Listbox.selectForeground", BLANCO)

        # Encabezado del formulario.
        cabecera = tk.Frame(ventana, bg=PANEL, height=112)
        cabecera.pack(fill="x")
        cabecera.pack_propagate(False)
        tk.Label(
            cabecera, text="✦", bg=PANEL, fg=MORADO_CLARO,
            font=("Segoe UI", 25, "bold")
        ).pack(pady=(13, 0))
        tk.Label(
            cabecera,
            text="Editar alimento" if alimento else "Agregar alimento",
            bg=PANEL, fg=BLANCO, font=("Segoe UI", 19, "bold")
        ).pack()
        tk.Label(
            cabecera,
            text="Registra los detalles para organizar y aprovechar mejor tus alimentos",
            bg=PANEL, fg=GRIS, font=("Segoe UI", 9)
        ).pack(pady=(3, 10))

        cuerpo = tk.Frame(ventana, bg=FONDO)
        cuerpo.pack(fill="both", expand=True, padx=38, pady=(17, 8))

        def etiqueta(texto, ayuda=None):
            tk.Label(
                cuerpo, text=texto.upper(), bg=FONDO, fg=GRIS,
                font=("Segoe UI", 8, "bold")
            ).pack(anchor="w", pady=(11, 5))
            if ayuda:
                tk.Label(
                    cuerpo, text=ayuda, bg=FONDO, fg=GRIS,
                    font=("Segoe UI", 8)
                ).pack(anchor="w", pady=(0, 4))

        def entrada(valor=""):
            campo = tk.Entry(
                cuerpo, bg=PANEL_SECUNDARIO, fg=BLANCO,
                insertbackground=BLANCO, relief="flat",
                font=("Segoe UI", 11), highlightthickness=1,
                highlightbackground=BORDE, highlightcolor=MORADO
            )
            campo.pack(fill="x", ipady=9)
            if valor != "":
                campo.insert(0, str(valor))
            return campo

        # Código: se presenta como identificador, nunca como campo editable.
        etiqueta("Código de registro", "Este código se genera automáticamente.")
        codigo = alimento.codigo if alimento else generar_codigo(self.inventario)
        bloque_codigo = tk.Frame(
            cuerpo, bg="#252238", highlightthickness=1,
            highlightbackground="#514879"
        )
        bloque_codigo.pack(fill="x")
        tk.Label(
            bloque_codigo, text="ID", bg="#252238", fg=MORADO_CLARO,
            font=("Segoe UI", 9, "bold")
        ).pack(side="left", padx=(15, 10), pady=12)
        tk.Label(
            bloque_codigo, text=str(codigo), bg="#252238", fg=BLANCO,
            font=("Segoe UI", 14, "bold")
        ).pack(side="left", pady=12)
        tk.Label(
            bloque_codigo, text="GENERADO POR EL SISTEMA", bg="#252238",
            fg=TURQUESA, font=("Segoe UI", 7, "bold")
        ).pack(side="right", padx=14)

        etiqueta("Nombre del alimento")
        campo_nombre = entrada(alimento.nombre if alimento else "")

        etiqueta("Cantidad y unidad")
        fila_cantidad = tk.Frame(cuerpo, bg=FONDO)
        fila_cantidad.pack(fill="x")
        campo_cantidad = tk.Entry(
            fila_cantidad, bg=PANEL_SECUNDARIO, fg=BLANCO,
            insertbackground=BLANCO, relief="flat",
            font=("Segoe UI", 11), highlightthickness=1,
            highlightbackground=BORDE, highlightcolor=MORADO
        )
        campo_cantidad.pack(side="left", fill="x", expand=True, ipady=9)
        if alimento:
            campo_cantidad.insert(0, str(alimento.cantidad))

        unidades = [
            "unidad", "kg", "g", "lb", "litro", "ml",
            "bolsa", "botella", "paquete", "caja", "docena"
        ]
        unidad_var = tk.StringVar(value=alimento.unidad if alimento else "unidad")
        selector_unidad = ttk.Combobox(
            fila_cantidad, textvariable=unidad_var, values=unidades,
            state="readonly", style="Formulario.TCombobox", width=13
        )
        selector_unidad.pack(side="left", padx=(10, 0), ipady=3)

        etiqueta("Fecha de vencimiento", "Selecciona el día en el calendario integrado.")
        fila_fecha = tk.Frame(cuerpo, bg=FONDO)
        fila_fecha.pack(fill="x")
        fecha_var = tk.StringVar(
            value=alimento.fecha_vencimiento if alimento else date.today().isoformat()
        )
        campo_fecha = tk.Entry(
            fila_fecha, textvariable=fecha_var, state="readonly",
            readonlybackground=PANEL_SECUNDARIO, fg=BLANCO,
            relief="flat", font=("Segoe UI", 11),
            highlightthickness=1, highlightbackground=BORDE
        )
        campo_fecha.pack(side="left", fill="x", expand=True, ipady=9)

        calendario_panel = tk.Frame(
            cuerpo, bg=PANEL, highlightthickness=1,
            highlightbackground=BORDE, padx=12, pady=10
        )
        calendario_visible = [False]
        fecha_calendario = [date.fromisoformat(fecha_var.get())]
        calendario_cabecera = tk.Frame(calendario_panel, bg=PANEL)
        calendario_cabecera.pack(fill="x")
        calendario_dias = tk.Frame(calendario_panel, bg=PANEL)
        calendario_dias.pack()

        def dibujar_calendario():
            for widget in calendario_cabecera.winfo_children():
                widget.destroy()
            for widget in calendario_dias.winfo_children():
                widget.destroy()

            actual = fecha_calendario[0]
            tk.Button(
                calendario_cabecera, text="‹", width=3,
                command=lambda: mover_mes(-1), bg=PANEL_CLARO,
                fg=BLANCO, activebackground=MORADO, relief="flat",
                cursor="hand2"
            ).pack(side="left")
            tk.Label(
                calendario_cabecera,
                text=f"{calendar.month_name[actual.month].title()} {actual.year}",
                bg=PANEL, fg=BLANCO, font=("Segoe UI", 11, "bold")
            ).pack(side="left", expand=True)
            tk.Button(
                calendario_cabecera, text="›", width=3,
                command=lambda: mover_mes(1), bg=PANEL_CLARO,
                fg=BLANCO, activebackground=MORADO, relief="flat",
                cursor="hand2"
            ).pack(side="right")

            for col, nombre_dia in enumerate(("L", "M", "X", "J", "V", "S", "D")):
                tk.Label(
                    calendario_dias, text=nombre_dia, width=5,
                    bg=PANEL, fg=MORADO_CLARO,
                    font=("Segoe UI", 8, "bold")
                ).grid(row=0, column=col, pady=(8, 5))

            for fila, semana in enumerate(
                calendar.monthcalendar(actual.year, actual.month), start=1
            ):
                for col, numero in enumerate(semana):
                    if numero == 0:
                        tk.Label(
                            calendario_dias, text="", width=5, bg=PANEL
                        ).grid(row=fila, column=col, padx=1, pady=1)
                        continue
                    elegido = (
                        actual.year == date.fromisoformat(fecha_var.get()).year
                        and actual.month == date.fromisoformat(fecha_var.get()).month
                        and numero == date.fromisoformat(fecha_var.get()).day
                    )
                    tk.Button(
                        calendario_dias, text=str(numero), width=4,
                        command=lambda d=numero: seleccionar_fecha(d),
                        bg=MORADO if elegido else PANEL_SECUNDARIO,
                        fg=BLANCO, activebackground=MORADO_CLARO,
                        relief="flat", font=("Segoe UI", 8), cursor="hand2"
                    ).grid(row=fila, column=col, padx=2, pady=2, ipady=3)

        def mover_mes(delta):
            actual = fecha_calendario[0]
            indice = actual.month - 1 + delta
            anio = actual.year + indice // 12
            mes = indice % 12 + 1
            fecha_calendario[0] = date(anio, mes, 1)
            dibujar_calendario()

        def seleccionar_fecha(dia):
            actual = fecha_calendario[0]
            fecha_var.set(date(actual.year, actual.month, dia).isoformat())
            calendario_panel.pack_forget()
            calendario_visible[0] = False
            boton_calendario.configure(text="▦  Elegir fecha")

        def alternar_calendario():
            if calendario_visible[0]:
                calendario_panel.pack_forget()
                calendario_visible[0] = False
                boton_calendario.configure(text="▦  Elegir fecha")
            else:
                actual = date.fromisoformat(fecha_var.get())
                fecha_calendario[0] = date(actual.year, actual.month, 1)
                dibujar_calendario()
                calendario_panel.pack(fill="x", pady=(8, 0))
                calendario_visible[0] = True
                boton_calendario.configure(text="✕  Ocultar calendario")

        boton_calendario = self.boton(
            fila_fecha, "▦  Elegir fecha", alternar_calendario,
            color=PANEL_CLARO
        )
        boton_calendario.pack(side="left", padx=(10, 0))

        etiqueta("Categoría")
        categorias = [
            "Frutas", "Verduras", "Carnes", "Lácteos",
            "Granos y cereales", "Bebidas", "Panadería",
            "Enlatados", "Otros"
        ]
        categoria_var = tk.StringVar(
            value=alimento.categoria if alimento else "Otros"
        )
        selector_categoria = ttk.Combobox(
            cuerpo, textvariable=categoria_var, values=categorias,
            state="readonly", style="Formulario.TCombobox"
        )
        selector_categoria.pack(fill="x", ipady=3)

        pie = tk.Frame(ventana, bg=FONDO)
        pie.pack(fill="x", padx=38, pady=(8, 22))

        def guardar():
            try:
                nombre = campo_nombre.get().strip()
                cantidad_texto = campo_cantidad.get().strip().replace(",", ".")
                if not nombre:
                    raise ValueError("Escribe el nombre del alimento.")
                try:
                    cantidad = float(cantidad_texto)
                except ValueError:
                    raise ValueError("Introduce una cantidad numérica válida.")
                if not (0 < cantidad < float("inf")):
                    raise ValueError("La cantidad debe ser mayor que cero.")

                fecha = date.fromisoformat(fecha_var.get()).isoformat()
                unidad = unidad_var.get()
                categoria = categoria_var.get()
                if alimento:
                    alimento.nombre = nombre
                    alimento.cantidad = cantidad
                    alimento.unidad = unidad
                    alimento.fecha_vencimiento = fecha
                    alimento.categoria = categoria
                else:
                    nuevo_codigo = generar_codigo(self.inventario)
                    self.inventario.append(
                        Alimento(nuevo_codigo, nombre, cantidad, unidad, fecha, categoria)
                    )

                guardar_datos(self.inventario)
                ventana.destroy()
                self.mostrar_inventario()
                messagebox.showinfo(
                    "Guardado", "El alimento se guardó correctamente."
                )
            except ValueError as error:
                messagebox.showerror(
                    "Datos incorrectos", str(error), parent=ventana
                )
            except Exception as error:
                messagebox.showerror("Error", str(error), parent=ventana)

        self.boton(pie, "Guardar alimento", guardar).pack(side="right")
        self.boton(
            pie, "Cancelar", ventana.destroy, color=PANEL_CLARO
        ).pack(side="right", padx=(0, 10))
        campo_nombre.focus_set()

    def obtener_seleccion(self):
        seleccion = self.tabla.selection()

        if not seleccion:
            messagebox.showwarning(
                "Selecciona un alimento",
                "Primero selecciona una fila de la tabla."
            )
            return None

        codigo = self.tabla.item(seleccion[0], "values")[0]
        return localizar_alimento(self.inventario, codigo)

    def modificar_seleccionado(self):
        alimento = self.obtener_seleccion()

        if alimento:
            self.formulario_alimento(alimento)

    def eliminar_seleccionado(self):
        alimento = self.obtener_seleccion()

        if alimento and messagebox.askyesno(
            "Confirmar eliminación",
            f"¿Eliminar {alimento.nombre} del inventario?"
        ):
            self.inventario.remove(alimento)
            guardar_datos(self.inventario)
            self.mostrar_inventario()

    # ==================================================
    # BUSCAR ALIMENTOS
    # ==================================================

    def buscar_alimentos(self):
        self.limpiar()
        self.encabezado(
            "Buscar alimentos",
            "Busca por nombre o código y ordena los resultados sin salir de esta pantalla."
        )

        panel = self.panel(self.contenido, 18)
        panel.pack(fill="x", padx=30, pady=10)

        tk.Label(
            panel, text="BÚSQUEDA DE PRODUCTOS", bg=PANEL,
            fg=GRIS, font=("Segoe UI", 8, "bold")
        ).pack(anchor="w")

        fila = tk.Frame(panel, bg=PANEL)
        fila.pack(fill="x", pady=(9, 0))
        entrada = tk.Entry(
            fila, bg=PANEL_SECUNDARIO, fg=BLANCO,
            insertbackground=BLANCO, relief="flat",
            font=("Segoe UI", 12)
        )
        entrada.pack(side="left", fill="x", expand=True, ipady=10)

        marco, tabla = self.crear_tabla(
            self.contenido,
            ("codigo", "nombre", "cantidad", "unidad", "fecha", "categoria"),
            ("Código", "Alimento", "Cantidad", "Unidad", "Vencimiento", "Categoría"),
            (95, 220, 110, 100, 145, 160)
        )
        marco.pack(fill="both", expand=True, padx=30, pady=(10, 5))

        contador = tk.Label(
            self.contenido, text="Resultados: 0",
            bg=FONDO, fg=GRIS, font=("Segoe UI", 9)
        )
        contador.pack(anchor="w", padx=32, pady=(0, 5))

        controles_orden = self.panel(self.contenido, 12)
        controles_orden.pack(fill="x", padx=30, pady=(5, 18))
        tk.Label(
            controles_orden, text="ORDENAR RESULTADOS", bg=PANEL,
            fg=GRIS, font=("Segoe UI", 8, "bold")
        ).pack(anchor="w", pady=(0, 8))
        botones_orden = tk.Frame(controles_orden, bg=PANEL)
        botones_orden.pack(anchor="w")

        resultados_actuales = list(self.inventario)

        def pintar_resultados(lista):
            for item in tabla.get_children():
                tabla.delete(item)
            for a in lista:
                tabla.insert(
                    "", "end",
                    values=(
                        a.codigo, a.nombre, a.cantidad,
                        a.unidad, a.fecha_vencimiento, a.categoria
                    )
                )
            contador.config(text=f"Resultados encontrados: {len(lista)}")

        def ejecutar_busqueda(event=None):
            nonlocal resultados_actuales
            texto = entrada.get().strip()
            resultados_actuales = (
                busqueda_lineal(self.inventario, texto)
                if texto else list(self.inventario)
            )
            pintar_resultados(resultados_actuales)

        def ordenar_codigo():
            nonlocal resultados_actuales
            resultados_actuales = sorted(
                resultados_actuales,
                key=lambda a: str(a.codigo).casefold()
            )
            pintar_resultados(resultados_actuales)

        def ordenar_vencimiento():
            nonlocal resultados_actuales
            def clave_fecha(a):
                try:
                    return (0, date.fromisoformat(str(a.fecha_vencimiento)))
                except (ValueError, TypeError, AttributeError):
                    return (1, date.max)
            resultados_actuales = sorted(resultados_actuales, key=clave_fecha)
            pintar_resultados(resultados_actuales)

        entrada.bind("<KeyRelease>", ejecutar_busqueda)
        self.boton(
            fila, "Buscar", ejecutar_busqueda
        ).pack(side="left", padx=(10, 0))
        self.boton(
            fila, "Limpiar", lambda: (entrada.delete(0, "end"), ejecutar_busqueda()),
            color=PANEL_CLARO
        ).pack(side="left", padx=(8, 0))

        self.boton(
            botones_orden, "Código: A–Z", ordenar_codigo,
            color=PANEL_CLARO
        ).pack(side="left", padx=(0, 8))
        self.boton(
            botones_orden, "Próximos a vencer", ordenar_vencimiento,
            color=PANEL_CLARO
        ).pack(side="left", padx=(0, 8))
        self.boton(
            botones_orden, "Restablecer orden", ejecutar_busqueda,
            color=PANEL_CLARO
        ).pack(side="left")

        ejecutar_busqueda()

    def mostrar_resultados(self, alimentos, titulo):
        # Se conserva por compatibilidad con otras llamadas del proyecto.
        self.limpiar()
        self.encabezado(titulo)
        marco, tabla = self.crear_tabla(
            self.contenido,
            ("codigo", "nombre", "cantidad", "fecha"),
            ("Código", "Alimento", "Cantidad", "Vencimiento")
        )
        marco.pack(fill="both", expand=True, padx=30, pady=20)
        for a in alimentos:
            tabla.insert(
                "", "end",
                values=(a.codigo, a.nombre, a.cantidad, a.fecha_vencimiento)
            )

    # ==================================================
    # VENCIMIENTOS
    # ==================================================

    def mostrar_vencimientos(self):
        self.limpiar()

        self.encabezado(
            "Control de vencimientos",
            "Identifica qué alimentos necesitan atención."
        )

        hoy = date.today()
        vencidos = []
        proximos = []
        buen_estado = []
        sin_fecha = []

        for a in self.inventario:
            try:
                fecha = date.fromisoformat(a.fecha_vencimiento)
                dias = (fecha - hoy).days

                if dias < 0:
                    vencidos.append((a, dias))
                elif dias <= 7:
                    proximos.append((a, dias))
                else:
                    buen_estado.append((a, dias))

            except (ValueError, TypeError, AttributeError):
                sin_fecha.append(a)

        tarjetas = tk.Frame(self.contenido, bg=FONDO)
        tarjetas.pack(fill="x", padx=25, pady=5)

        self.tarjeta(tarjetas, "Vencidos", len(vencidos), CORAL)
        self.tarjeta(tarjetas, "Próximos (7 días)", len(proximos), AMARILLO)
        self.tarjeta(tarjetas, "En buen estado", len(buen_estado), EXITO)

        panel = self.panel(self.contenido, 15)
        panel.pack(fill="both", expand=True, padx=30, pady=15)

        tk.Label(
            panel,
            text="Estado de los alimentos",
            bg=PANEL,
            fg=BLANCO,
            font=("Segoe UI", 14, "bold")
        ).pack(anchor="w", pady=(0, 12))

        filtros = tk.Frame(panel, bg=PANEL)
        filtros.pack(fill="x", pady=(0, 12))

        marco, tabla = self.crear_tabla(
            panel,
            ("nombre", "cantidad", "fecha", "estado", "dias"),
            ("Alimento", "Cantidad", "Vencimiento", "Estado", "Días restantes"),
            (180, 100, 140, 150, 120)
        )
        marco.pack(fill="both", expand=True)

        tabla.tag_configure("vencido", foreground=CORAL)
        tabla.tag_configure("urgente", foreground=AMARILLO)
        tabla.tag_configure("normal", foreground=EXITO)

        def cargar_lista(tipo):
            for fila in tabla.get_children():
                tabla.delete(fila)

            if tipo == "Vencidos":
                lista = vencidos
            elif tipo == "Próximos":
                lista = proximos
            elif tipo == "Buen estado":
                lista = buen_estado
            elif tipo == "Sin fecha":
                lista = sin_fecha
            else:
                lista = (
                    vencidos + proximos + buen_estado
                )

            for elemento in lista:
                if isinstance(elemento, tuple):
                    a, dias = elemento

                    if dias < 0:
                        estado = "VENCIDO"
                        tag = "vencido"
                    elif dias <= 7:
                        estado = "PRÓXIMO"
                        tag = "urgente"
                    else:
                        estado = "BUEN ESTADO"
                        tag = "normal"

                    dias_texto = str(dias)
                else:
                    a = elemento
                    estado = "SIN FECHA VÁLIDA"
                    tag = "vencido"
                    dias_texto = "-"

                tabla.insert(
                    "",
                    "end",
                    values=(
                        a.nombre,
                        f"{a.cantidad} {a.unidad}",
                        a.fecha_vencimiento,
                        estado,
                        dias_texto
                    ),
                    tags=(tag,)
                )

        for nombre, color in [
            ("Todos", MORADO),
            ("Vencidos", CORAL),
            ("Próximos", AMARILLO),
            ("Buen estado", EXITO),
            ("Sin fecha", PANEL_CLARO)
        ]:
            self.boton(
                filtros,
                nombre,
                lambda n=nombre: cargar_lista(n),
                color=color
            ).pack(side="left", padx=(0, 7))

        cargar_lista("Todos")

    # ==================================================
    # RECETAS GENERADAS POR IA
    # ==================================================

    def mostrar_recetas(self):
        self.limpiar()

        self.encabezado(
            "Recetas inteligentes",
            "Recetas creadas por IA utilizando los alimentos de tu inventario."
        )

        disponibles = [
            a for a in self.inventario
            if float(getattr(a, "cantidad", 0)) > 0
        ]

        panel = self.panel(self.contenido, 20)
        panel.pack(fill="x", padx=30, pady=5)

        tk.Label(
            panel,
            text="✦  GENERADOR INTELIGENTE DE RECETAS",
            bg=PANEL,
            fg=MORADO_CLARO,
            font=("Segoe UI", 12, "bold")
        ).pack(anchor="w")

        tk.Label(
            panel,
            text=(
                "La IA analizará tus alimentos disponibles, "
                "priorizará los próximos a vencer y creará recetas "
                "con ingredientes reales de tu inventario."
            ),
            bg=PANEL,
            fg=GRIS,
            font=("Segoe UI", 9),
            wraplength=850,
            justify="left"
        ).pack(anchor="w", pady=(8, 15))

        tarjetas = tk.Frame(self.contenido, bg=FONDO)
        tarjetas.pack(fill="x", padx=25, pady=10)

        self.tarjeta(
            tarjetas,
            "Alimentos disponibles",
            len(disponibles),
            TURQUESA
        )

        proximos = 0
        for a in disponibles:
            try:
                dias = (
                    date.fromisoformat(a.fecha_vencimiento) - date.today()
                ).days

                if 0 <= dias <= 7:
                    proximos += 1
            except (ValueError, TypeError, AttributeError):
                pass

        self.tarjeta(
            tarjetas,
            "Próximos a vencer",
            proximos,
            AMARILLO
        )

        zona = self.panel(self.contenido, 18)
        zona.pack(fill="both", expand=True, padx=30, pady=15)

        tk.Label(
            zona,
            text="Tus recomendaciones",
            bg=PANEL,
            fg=BLANCO,
            font=("Segoe UI", 14, "bold")
        ).pack(anchor="w")

        resultado = tk.Text(
            zona,
            bg=PANEL_SECUNDARIO,
            fg=TEXTO,
            insertbackground=BLANCO,
            font=("Segoe UI", 10),
            wrap="word",
            relief="flat",
            padx=16,
            pady=14,
            spacing1=5,
            spacing3=7
        )
        resultado.pack(fill="both", expand=True, pady=12)

        resultado.insert(
            "end",
            "Aquí aparecerán las recetas creadas por la inteligencia artificial.\n\n"
            "Presiona «Generar recetas» para analizar tu inventario."
        )
        resultado.config(state="disabled")

        resultado.tag_configure(
            "titulo",
            foreground=MORADO_CLARO,
            font=("Segoe UI", 13, "bold"),
            spacing1=12,
            spacing3=7
        )

        resultado.tag_configure(
            "subtitulo",
            foreground=TURQUESA,
            font=("Segoe UI", 10, "bold")
        )

        estado = tk.Label(
            zona,
            text="●  Esperando solicitud",
            bg=PANEL,
            fg=GRIS,
            font=("Segoe UI", 9)
        )
        estado.pack(anchor="w")

        def mostrar_resultado(texto):
            resultado.config(state="normal")
            resultado.delete("1.0", "end")

            for linea in texto.splitlines():
                limpia = linea.strip()

                if not limpia:
                    resultado.insert("end", "\n")
                elif limpia.upper().startswith("RECETA:"):
                    resultado.insert("end", limpia + "\n", "titulo")
                elif limpia.endswith(":"):
                    resultado.insert("end", limpia + "\n", "subtitulo")
                else:
                    resultado.insert("end", limpia + "\n")

            resultado.config(state="disabled")
            estado.config(
                text="●  Recetas generadas",
                fg=EXITO
            )

        def generar():
            if not disponibles:
                messagebox.showinfo(
                    "Inventario vacío",
                    "Registra alimentos con cantidad disponible "
                    "antes de generar recetas."
                )
                return

            boton_generar.config(state="disabled")
            estado.config(
                text="●  La IA está analizando tu inventario...",
                fg=AMARILLO
            )

            resultado.config(state="normal")
            resultado.delete("1.0", "end")
            resultado.insert(
                "end",
                "Analizando alimentos y preparando recetas...\n"
            )
            resultado.config(state="disabled")

            def trabajo():
                try:
                    respuesta = generar_recetas(self.inventario)
                except Exception as error:
                    respuesta = f"No se pudieron generar las recetas: {error}"

                self.ventana.after(
                    0,
                    lambda: terminar(respuesta)
                )

            def terminar(respuesta):
                if not self.ventana.winfo_exists():
                    return

                mostrar_resultado(respuesta)
                boton_generar.config(state="normal")

            threading.Thread(
                target=trabajo,
                daemon=True
            ).start()

        boton_generar = self.boton(
            zona,
            "✦  Generar recetas con IA",
            generar
        )
        boton_generar.pack(anchor="w")

    # ==================================================
    # ESTADÍSTICAS
    # ==================================================

    def mostrar_estadisticas(self):
        self.limpiar()

        self.encabezado(
            "Panel de estadísticas",
            "Analiza el aprovechamiento y el desperdicio de tus alimentos."
        )

        registrados = len(self.inventario)

        disponibles = sum(
            float(getattr(a, "cantidad", 0))
            for a in self.inventario
        )

        aprovechados = sum(
            float(getattr(a, "cantidad_aprovechada", 0))
            for a in self.inventario
        )

        desperdiciados = sum(
            float(getattr(a, "cantidad_desperdiciada", 0))
            for a in self.inventario
        )

        puntos = sum(
            float(getattr(a, "puntos_rescate", 0))
            for a in self.inventario
        )

        total = aprovechados + desperdiciados

        porcentaje = (
            aprovechados / total * 100
            if total > 0 else 0
        )

        tarjetas = tk.Frame(self.contenido, bg=FONDO)
        tarjetas.pack(fill="x", padx=25, pady=10)

        self.tarjeta(tarjetas, "Registrados", registrados, MORADO)
        self.tarjeta(tarjetas, "Disponibles", f"{disponibles:g}", AZUL)
        self.tarjeta(tarjetas, "Aprovechados", f"{aprovechados:g}", EXITO)
        self.tarjeta(tarjetas, "Desperdiciados", f"{desperdiciados:g}", CORAL)
        self.tarjeta(tarjetas, "Puntos de rescate", f"{puntos:g}", AMARILLO)

        progreso = self.panel(self.contenido, 20)
        progreso.pack(fill="x", padx=30, pady=15)

        tk.Label(
            progreso,
            text="Nivel de aprovechamiento",
            bg=PANEL,
            fg=BLANCO,
            font=("Segoe UI", 13, "bold")
        ).pack(anchor="w")

        tk.Label(
            progreso,
            text=f"{porcentaje:.1f}%",
            bg=PANEL,
            fg=MORADO_CLARO,
            font=("Segoe UI", 22, "bold")
        ).pack(anchor="w", pady=5)

        barra = tk.Frame(progreso, bg=PANEL_CLARO, height=14)
        barra.pack(fill="x", pady=8)
        barra.pack_propagate(False)

        valor = tk.Frame(barra, bg=EXITO)
        valor.pack(
            side="left",
            fill="y",
            expand=False
        )

        def actualizar_barra(event=None):
            valor.configure(
                width=int(barra.winfo_width() * min(porcentaje, 100) / 100)
            )

        barra.bind("<Configure>", actualizar_barra)

        tabla_panel = self.panel(self.contenido, 12)
        tabla_panel.pack(
            fill="both",
            expand=True,
            padx=30,
            pady=10
        )

        tk.Label(
            tabla_panel,
            text="Rendimiento por alimento",
            bg=PANEL,
            fg=BLANCO,
            font=("Segoe UI", 13, "bold")
        ).pack(anchor="w", pady=(0, 10))

        marco, tabla = self.crear_tabla(
            tabla_panel,
            ("nombre", "disponible", "aprovechado", "desperdiciado", "puntos"),
            ("Alimento", "Disponible", "Aprovechado", "Desperdiciado", "Puntos")
        )
        marco.pack(fill="both", expand=True)

        for a in self.inventario:
            tabla.insert(
                "",
                "end",
                values=(
                    a.nombre,
                    a.cantidad,
                    getattr(a, "cantidad_aprovechada", 0),
                    getattr(a, "cantidad_desperdiciada", 0),
                    getattr(a, "puntos_rescate", 0)
                )
            )

    # ==================================================
    # ASISTENTE IA
    # ==================================================

    def mostrar_asistente(self):
        self.limpiar()

        self.encabezado(
            "Asistente inteligente",
            "Consulta, pregunta y recibe recomendaciones basadas en tu inventario."
        )

        principal = tk.Frame(self.contenido, bg=FONDO)
        principal.pack(fill="both", expand=True, padx=30, pady=(0, 20))

        cabecera = self.panel(principal, 15)
        cabecera.pack(fill="x")

        tk.Label(
            cabecera,
            text="✦  CERO DESPERDICIO AI",
            bg=PANEL,
            fg=MORADO_CLARO,
            font=("Segoe UI", 12, "bold")
        ).pack(anchor="w")

        tk.Label(
            cabecera,
            text="Asistente conectado a los alimentos de tu inventario.",
            bg=PANEL,
            fg=GRIS,
            font=("Segoe UI", 9)
        ).pack(anchor="w", pady=(4, 0))

        area = tk.Frame(principal, bg=FONDO)
        area.pack(fill="both", expand=True, pady=12)

        lienzo = tk.Canvas(
            area,
            bg=FONDO,
            highlightthickness=0
        )

        scroll = ttk.Scrollbar(
            area,
            orient="vertical",
            command=lienzo.yview
        )

        mensajes = tk.Frame(lienzo, bg=FONDO)

        ventana_mensajes = lienzo.create_window(
            (0, 0),
            window=mensajes,
            anchor="nw"
        )

        mensajes.bind(
            "<Configure>",
            lambda e: lienzo.configure(
                scrollregion=lienzo.bbox("all")
            )
        )

        lienzo.bind(
            "<Configure>",
            lambda e: lienzo.itemconfigure(
                ventana_mensajes,
                width=e.width
            )
        )

        lienzo.configure(yscrollcommand=scroll.set)
        lienzo.pack(side="left", fill="both", expand=True)
        scroll.pack(side="right", fill="y")

        def agregar_mensaje(texto, usuario=False):
            contenedor = tk.Frame(mensajes, bg=FONDO)
            contenedor.pack(fill="x", padx=8, pady=7)

            color = "#49416F" if usuario else PANEL
            burbuja = tk.Frame(contenedor, bg=color, padx=15, pady=12)

            burbuja.pack(
                side="right" if usuario else "left",
                padx=(75, 0) if usuario else (0, 75)
            )

            tk.Label(
                burbuja,
                text="TÚ" if usuario else "CERO DESPERDICIO AI",
                bg=color,
                fg=MORADO_CLARO if usuario else TURQUESA,
                font=("Segoe UI", 8, "bold")
            ).pack(anchor="w")

            tk.Label(
                burbuja,
                text=texto,
                bg=color,
                fg=BLANCO,
                font=("Segoe UI", 10),
                justify="left",
                wraplength=620
            ).pack(anchor="w", pady=(5, 0))

            lienzo.update_idletasks()
            lienzo.yview_moveto(1)

        agregar_mensaje(
            "¡Hola! Soy tu asistente inteligente. "
            "Puedo ayudarte a aprovechar alimentos, recomendar "
            "recetas y reducir desperdicios. ¿Qué necesitas?",
            False
        )

        estado = tk.Label(
            principal,
            text="●  Listo para ayudarte",
            bg=FONDO,
            fg=EXITO,
            font=("Segoe UI", 9)
        )
        estado.pack(anchor="w", pady=(0, 8))

        entrada_panel = self.panel(principal, 12)
        entrada_panel.pack(fill="x")

        pregunta = tk.Entry(
            entrada_panel,
            bg=PANEL_SECUNDARIO,
            fg=BLANCO,
            insertbackground=BLANCO,
            relief="flat",
            font=("Segoe UI", 11)
        )
        pregunta.pack(
            side="left",
            fill="x",
            expand=True,
            ipady=10,
            padx=(0, 10)
        )

        boton_enviar = self.boton(
            entrada_panel,
            "Enviar  ➤",
            lambda: enviar()
        )
        boton_enviar.pack(side="right")

        def terminar_consulta(respuesta):
            if not self.ventana.winfo_exists():
                return

            agregar_mensaje(respuesta, False)
            estado.config(
                text="●  Listo para ayudarte",
                fg=EXITO
            )

            pregunta.config(state="normal")
            boton_enviar.config(state="normal")
            pregunta.focus_set()

        def consultar_en_hilo(texto):
            try:
                respuesta = consultar_ia(texto, self.inventario)
            except Exception as error:
                respuesta = f"Error al consultar la IA: {error}"

            try:
                self.ventana.after(
                    0,
                    lambda: terminar_consulta(respuesta)
                )
            except tk.TclError:
                pass

        def enviar():
            texto = pregunta.get().strip()

            if not texto:
                return

            pregunta.delete(0, "end")
            agregar_mensaje(texto, True)

            estado.config(
                text="●  La IA está preparando tu respuesta...",
                fg=AMARILLO
            )

            pregunta.config(state="disabled")
            boton_enviar.config(state="disabled")

            threading.Thread(
                target=consultar_en_hilo,
                args=(texto,),
                daemon=True
            ).start()

        pregunta.bind("<Return>", lambda e: enviar())
        pregunta.focus_set()

    # ==================================================
    # CERRAR APLICACIÓN
    # ==================================================

    def cerrar(self):
        try:
            guardar_datos(self.inventario)
        except Exception as error:
            messagebox.showerror("Error al guardar", str(error))
            return

        self.ventana.destroy()


def iniciar_interfaz():
    ventana = tk.Tk()
    Aplicacion(ventana)
    ventana.mainloop()
