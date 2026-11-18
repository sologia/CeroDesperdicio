
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
from asistente_ia import consultar_ia
from vista_recetas import VistaRecetas
import catalogo
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
        boton = self._boton_base(padre, texto, comando, color)
        boton.bind("<Enter>", lambda e: boton.config(bg=MORADO_CLARO)
                   if str(boton["state"]) != "disabled" else None)
        boton.bind("<Leave>", lambda e: boton.config(bg=color))
        return boton

    def _boton_base(self, padre, texto, comando, color):
        return tk.Button(
            padre,
            text=texto,
            command=comando,
            bg=color,
            fg=BLANCO,
            disabledforeground="#D9D3FF",
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
            "🧊  Seleccionar lo que hay en mi refri",
            self.seleccion_rapida,
            color=TURQUESA
        ).pack(anchor="w", pady=4)

        self.boton(
            acciones,
            "+ Registrar alimento manualmente",
            self.formulario_alimento,
            color=PANEL_CLARO
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
            "🧊  Desde mi refri",
            self.seleccion_rapida,
            color=TURQUESA
        ).pack(side="left", padx=(0, 8))

        self.boton(
            fila,
            "+ Agregar manual",
            self.formulario_alimento
        ).pack(side="left", padx=8)

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
            ("codigo", "nombre", "cantidad", "unidad", "fecha", "categoria",
             "kcal", "proteina"),
            ("Código", "Alimento", "Cantidad", "Unidad", "Vencimiento",
             "Categoría", "Calorías", "Proteína"),
            (75, 170, 85, 85, 120, 130, 100, 100)
        )
        self.tabla.bind("<<TreeviewSelect>>", self.mostrar_nutricion_seleccion)

        self.etiqueta_nutricion = tk.Label(
            self.contenido,
            text="Selecciona un alimento para ver su información nutricional.    "
                 "Rojo = vencido  ·  Amarillo = vence en 3 días o menos",
            bg=FONDO, fg=GRIS, font=("Segoe UI", 9), anchor="w"
        )
        marco.pack(fill="both", expand=True, padx=30, pady=(0, 25))
        self.etiqueta_nutricion.pack(fill="x", padx=32, pady=(0, 12),
                                     before=marco)

        self.actualizar_tabla()

    def actualizar_tabla(self, lista=None):
        for fila in self.tabla.get_children():
            self.tabla.delete(fila)

        alimentos = self.inventario if lista is None else lista

        # Filas alternadas y color según vencimiento.
        self.tabla.tag_configure("par", background=PANEL)
        self.tabla.tag_configure("impar", background="#202536")
        self.tabla.tag_configure("vencido", foreground=CORAL)
        self.tabla.tag_configure("pronto", foreground=AMARILLO)

        for i, a in enumerate(alimentos):
            n = catalogo.nutricion_total(a.nombre, a.cantidad, a.unidad)
            try:
                dias = (date.fromisoformat(str(a.fecha_vencimiento))
                        - date.today()).days
            except (ValueError, TypeError):
                dias = None
            etiquetas = ["par" if i % 2 == 0 else "impar"]
            if dias is not None and dias < 0:
                etiquetas.append("vencido")
            elif dias is not None and dias <= 3:
                etiquetas.append("pronto")
            self.tabla.insert(
                "",
                "end",
                tags=tuple(etiquetas),
                values=(
                    a.codigo,
                    a.nombre,
                    f"{float(a.cantidad):g}",
                    a.unidad,
                    a.fecha_vencimiento,
                    a.categoria,
                    f"{n['kcal']:.0f} kcal" if n else "—",
                    f"{n['proteina']:.1f} g" if n else "—"
                )
            )

    def mostrar_nutricion_seleccion(self, event=None):
        alimento = self.obtener_seleccion() if self.tabla.selection() else None
        if not alimento:
            return
        base = catalogo.nutricion_100g(alimento.nombre)
        total = catalogo.nutricion_total(
            alimento.nombre, alimento.cantidad, alimento.unidad
        )
        if not base:
            texto = f"{alimento.nombre}: sin datos nutricionales en el catálogo."
        else:
            texto = (
                f"{alimento.nombre}  —  Por 100 g: {catalogo.texto_nutricion(base)}"
                f"\nTotal en inventario ({float(alimento.cantidad):g} "
                f"{alimento.unidad}): {catalogo.texto_nutricion(total)}"
            )
        self.etiqueta_nutricion.config(text=texto, fg=TEXTO, justify="left")

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
        ancho, alto = 620, 830
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

        etiqueta("Nombre del alimento", "Elige de la lista o escribe uno nuevo.")
        nombre_var = tk.StringVar(value=alimento.nombre if alimento else "")
        campo_nombre = ttk.Combobox(
            cuerpo, textvariable=nombre_var,
            values=sorted(catalogo.CATALOGO), style="Formulario.TCombobox"
        )
        campo_nombre.pack(fill="x", ipady=3)
        info_nutricion = tk.Label(
            cuerpo, text="", bg=FONDO, fg=TURQUESA,
            font=("Segoe UI", 8), anchor="w", justify="left"
        )
        info_nutricion.pack(fill="x", pady=(4, 0))

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
        def fecha_valida(texto):
            try:
                return date.fromisoformat(str(texto))
            except (ValueError, TypeError):
                return date.today()

        fecha_var = tk.StringVar(
            value=fecha_valida(
                alimento.fecha_vencimiento if alimento else None
            ).isoformat()
        )
        campo_fecha = tk.Entry(
            fila_fecha, textvariable=fecha_var, state="readonly",
            readonlybackground=PANEL_SECUNDARIO, fg=BLANCO,
            relief="flat", font=("Segoe UI", 11),
            highlightthickness=1, highlightbackground=BORDE
        )
        campo_fecha.pack(side="left", fill="x", expand=True, ipady=9)

        # Calendario en ventana emergente: antes se dibujaba al final del
        # formulario (que no cambia de tamaño) y quedaba cortado / sin poder
        # hacer clic en los días.
        meses = (
            "", "Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio", "Julio",
            "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre"
        )

        def abrir_calendario():
            popup = tk.Toplevel(ventana)
            popup.title("Fecha de vencimiento")
            popup.configure(bg=PANEL, padx=12, pady=10)
            popup.resizable(False, False)
            popup.transient(ventana)
            popup.geometry(
                f"+{fila_fecha.winfo_rootx()}"
                f"+{fila_fecha.winfo_rooty() + fila_fecha.winfo_height() + 4}"
            )
            mes_visible = [fecha_valida(fecha_var.get()).replace(day=1)]
            cab = tk.Frame(popup, bg=PANEL)
            cab.pack(fill="x")
            dias = tk.Frame(popup, bg=PANEL)
            dias.pack(pady=(6, 0))

            def cerrar_popup():
                popup.grab_release()
                popup.destroy()
                ventana.grab_set()

            def mover(delta):
                actual = mes_visible[0]
                indice = actual.month - 1 + delta
                mes_visible[0] = date(actual.year + indice // 12, indice % 12 + 1, 1)
                dibujar()

            def elegir(dia):
                actual = mes_visible[0]
                fecha_var.set(date(actual.year, actual.month, dia).isoformat())
                cerrar_popup()

            def dibujar():
                for w in cab.winfo_children() + dias.winfo_children():
                    w.destroy()
                actual = mes_visible[0]
                elegida = fecha_valida(fecha_var.get())
                hoy = date.today()
                for texto, delta, lado in (("‹", -1, "left"), ("›", 1, "right")):
                    tk.Button(
                        cab, text=texto, width=3, command=lambda d=delta: mover(d),
                        bg=PANEL_CLARO, fg=BLANCO, activebackground=MORADO,
                        relief="flat", cursor="hand2"
                    ).pack(side=lado)
                tk.Label(
                    cab, text=f"{meses[actual.month]} {actual.year}",
                    bg=PANEL, fg=BLANCO, font=("Segoe UI", 11, "bold")
                ).pack(side="left", expand=True)
                for col, nombre_dia in enumerate("LMXJVSD"):
                    tk.Label(
                        dias, text=nombre_dia, width=4, bg=PANEL,
                        fg=MORADO_CLARO, font=("Segoe UI", 8, "bold")
                    ).grid(row=0, column=col, pady=(4, 4))
                for fila, semana in enumerate(
                    calendar.monthcalendar(actual.year, actual.month), start=1
                ):
                    for col, numero in enumerate(semana):
                        if numero == 0:
                            continue
                        dia = date(actual.year, actual.month, numero)
                        color = (
                            MORADO if dia == elegida
                            else PANEL_CLARO if dia == hoy
                            else PANEL_SECUNDARIO
                        )
                        tk.Button(
                            dias, text=str(numero), width=4,
                            command=lambda d=numero: elegir(d),
                            bg=color, fg=CORAL if dia < hoy else BLANCO,
                            activebackground=MORADO_CLARO, relief="flat",
                            font=("Segoe UI", 9), cursor="hand2"
                        ).grid(row=fila, column=col, padx=2, pady=2, ipady=3)

            popup.protocol("WM_DELETE_WINDOW", cerrar_popup)
            popup.bind("<Escape>", lambda e: cerrar_popup())
            dibujar()
            popup.grab_set()
            popup.focus_set()

        boton_calendario = self.boton(
            fila_fecha, "▦  Elegir fecha", abrir_calendario,
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

        def al_cambiar_nombre(*_):
            base = catalogo.nutricion_100g(nombre_var.get())
            info_nutricion.config(
                text=("Por 100 g: " + catalogo.texto_nutricion(base))
                if base else ""
            )

        def al_elegir_catalogo(event=None):
            ficha = catalogo.buscar(nombre_var.get())
            if not ficha:
                return
            categoria_var.set(ficha[1][0])
            unidad_var.set(ficha[1][1])
            if not campo_cantidad.get().strip():
                campo_cantidad.insert(0, "1")
            if not alimento:
                fecha_var.set(catalogo.fecha_sugerida(ficha[0]))

        nombre_var.trace_add("write", al_cambiar_nombre)
        campo_nombre.bind("<<ComboboxSelected>>", al_elegir_catalogo)
        al_cambiar_nombre()

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

                self.guardar()
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

    def seleccion_rapida(self):
        """Ventana con ingredientes predefinidos para marcar con un clic."""
        ventana = tk.Toplevel(self.ventana)
        ventana.title("¿Qué hay en tu refri?")
        ventana.configure(bg=FONDO)
        ventana.transient(self.ventana)
        ventana.grab_set()
        ancho, alto = 1060, 740
        ventana.update_idletasks()
        x = self.ventana.winfo_rootx() + max(0, (self.ventana.winfo_width() - ancho) // 2)
        y = self.ventana.winfo_rooty() + max(0, (self.ventana.winfo_height() - alto) // 2)
        ventana.geometry(f"{ancho}x{alto}+{x}+{y}")

        seleccionados = {}  # nombre -> tk.StringVar con la cantidad
        chips = {}
        en_inventario = {a.nombre.lower() for a in self.inventario}

        cabecera = tk.Frame(ventana, bg=PANEL, padx=26, pady=16)
        cabecera.pack(fill="x")
        tk.Label(
            cabecera, text="🧊  ¿Qué hay en tu refrigerador?",
            bg=PANEL, fg=BLANCO, font=("Segoe UI", 18, "bold")
        ).pack(anchor="w")
        tk.Label(
            cabecera,
            text="Toca los ingredientes que tienes y ajusta la cantidad a la "
                 "derecha. La fecha de vencimiento se sugiere sola.",
            bg=PANEL, fg=GRIS, font=("Segoe UI", 9)
        ).pack(anchor="w", pady=(2, 10))

        busqueda_var = tk.StringVar()
        tk.Entry(
            cabecera, textvariable=busqueda_var, bg=PANEL_SECUNDARIO,
            fg=BLANCO, insertbackground=BLANCO, relief="flat",
            font=("Segoe UI", 11), highlightthickness=1,
            highlightbackground=BORDE, highlightcolor=MORADO
        ).pack(fill="x", ipady=8)

        # Zona desplazable con los ingredientes agrupados por categoría.
        zona = tk.Frame(ventana, bg=FONDO)
        zona.pack(fill="both", expand=True, padx=20, pady=10)

        # Panel derecho: lo seleccionado con su cantidad.
        lateral = tk.Frame(
            zona, bg=PANEL, width=300, padx=12, pady=10,
            highlightthickness=1, highlightbackground=BORDE
        )
        lateral.pack(side="right", fill="y", padx=(10, 0))
        lateral.pack_propagate(False)
        tk.Label(
            lateral, text="TU SELECCIÓN", bg=PANEL, fg=GRIS,
            font=("Segoe UI", 8, "bold")
        ).pack(anchor="w")
        lista_sel = tk.Frame(lateral, bg=PANEL)
        lista_sel.pack(fill="both", expand=True, pady=(6, 0))

        lienzo = tk.Canvas(zona, bg=FONDO, highlightthickness=0)
        barra = ttk.Scrollbar(zona, orient="vertical", command=lienzo.yview)
        interior = tk.Frame(lienzo, bg=FONDO)
        interior.bind(
            "<Configure>",
            lambda e: lienzo.configure(scrollregion=lienzo.bbox("all"))
        )
        lienzo.create_window((0, 0), window=interior, anchor="nw")
        lienzo.configure(yscrollcommand=barra.set)
        lienzo.pack(side="left", fill="both", expand=True)
        barra.pack(side="right", fill="y")
        ventana.bind(
            "<MouseWheel>",
            lambda e: lienzo.yview_scroll(int(-e.delta / 120), "units")
        )

        pie = tk.Frame(ventana, bg=PANEL, padx=22, pady=12)
        pie.pack(fill="x", side="bottom")
        info = tk.Label(
            pie, text="Toca un ingrediente para ver su información nutricional.",
            bg=PANEL, fg=GRIS, font=("Segoe UI", 9), anchor="w", justify="left"
        )
        info.pack(side="left", fill="x", expand=True)

        def pintar(nombre):
            chip = chips[nombre]
            activo = nombre in seleccionados
            chip.config(
                bg=MORADO if activo else PANEL_SECUNDARIO,
                fg=BLANCO if activo else TEXTO,
                text=("✓ " if activo else "") + nombre
            )

        def leer_cantidad(var):
            try:
                valor = float(var.get().replace(",", "."))
                return valor if 0 < valor < float("inf") else None
            except ValueError:
                return None

        def cambiar(var, delta):
            actual = leer_cantidad(var) or 0
            nuevo = max(0.5 if actual <= 1 else 1, actual + delta)
            var.set(f"{nuevo:g}")

        def dibujar_seleccion():
            for w in lista_sel.winfo_children():
                w.destroy()
            if not seleccionados:
                tk.Label(
                    lista_sel, text="Aún no eliges nada.", bg=PANEL,
                    fg=GRIS, font=("Segoe UI", 9)
                ).pack(anchor="w")
            for nombre, var in seleccionados.items():
                unidad = catalogo.CATALOGO[nombre][1]
                fila = tk.Frame(lista_sel, bg=PANEL)
                fila.pack(fill="x", pady=3)
                tk.Label(
                    fila, text=nombre, bg=PANEL, fg=BLANCO, anchor="w",
                    font=("Segoe UI", 9, "bold"), width=13
                ).pack(side="left")
                for texto, delta in (("−", -1), (None, 0), ("+", 1)):
                    if texto is None:
                        tk.Entry(
                            fila, textvariable=var, width=5, justify="center",
                            bg=PANEL_SECUNDARIO, fg=BLANCO, relief="flat",
                            insertbackground=BLANCO, font=("Segoe UI", 10)
                        ).pack(side="left", ipady=3, padx=2)
                        continue
                    tk.Button(
                        fila, text=texto, width=2, bg=PANEL_CLARO, fg=BLANCO,
                        activebackground=MORADO, relief="flat", cursor="hand2",
                        command=lambda v=var, d=delta: cambiar(v, d)
                    ).pack(side="left")
                tk.Label(
                    fila, text=unidad, bg=PANEL, fg=GRIS,
                    font=("Segoe UI", 8)
                ).pack(side="left", padx=(4, 0))
            boton_agregar.config(
                text=f"Agregar {len(seleccionados)} ingrediente(s)"
            )

        def alternar(nombre):
            if nombre in seleccionados:
                del seleccionados[nombre]
            else:
                seleccionados[nombre] = tk.StringVar(value="1")
            pintar(nombre)
            dibujar_seleccion()
            base = catalogo.nutricion_100g(nombre)
            info.config(
                text=f"{nombre} (por 100 g)\n{catalogo.texto_nutricion(base)}",
                fg=TEXTO
            )

        def dibujar(*_):
            for w in interior.winfo_children():
                w.destroy()
            chips.clear()
            filtro = busqueda_var.get().strip().lower()
            for categoria, nombres in catalogo.por_categoria().items():
                visibles = [n for n in nombres if filtro in n.lower()]
                if not visibles:
                    continue
                tk.Label(
                    interior, text=categoria.upper(), bg=FONDO,
                    fg=MORADO_CLARO, font=("Segoe UI", 9, "bold")
                ).pack(anchor="w", pady=(12, 6))
                grilla = tk.Frame(interior, bg=FONDO)
                grilla.pack(anchor="w")
                for i, nombre in enumerate(visibles):
                    chip = tk.Label(
                        grilla, width=17, pady=8, cursor="hand2",
                        font=("Segoe UI", 10), relief="flat",
                        highlightthickness=1,
                        highlightbackground=(
                            TURQUESA if nombre.lower() in en_inventario
                            else BORDE
                        )
                    )
                    chip.grid(row=i // 4, column=i % 4, padx=4, pady=4)
                    chip.bind("<Button-1>", lambda e, n=nombre: alternar(n))
                    chips[nombre] = chip
                    pintar(nombre)
            tk.Label(
                interior, text="Borde turquesa = ya está en tu inventario.",
                bg=FONDO, fg=GRIS, font=("Segoe UI", 8)
            ).pack(anchor="w", pady=(14, 4))

        def agregar():
            if not seleccionados:
                messagebox.showinfo(
                    "Nada seleccionado",
                    "Toca al menos un ingrediente.", parent=ventana
                )
                return
            invalidos = [n for n, v in seleccionados.items()
                         if leer_cantidad(v) is None]
            if invalidos:
                messagebox.showerror(
                    "Cantidad incorrecta",
                    "Revisa la cantidad de: " + ", ".join(invalidos)
                    + ".\nDebe ser un número mayor que cero.",
                    parent=ventana
                )
                return
            for nombre in sorted(seleccionados):
                cantidad = leer_cantidad(seleccionados[nombre])
                categoria, unidad = catalogo.CATALOGO[nombre][:2]
                existente = next(
                    (a for a in self.inventario
                     if a.nombre.lower() == nombre.lower() and a.unidad == unidad),
                    None
                )
                if existente:
                    existente.cantidad = float(existente.cantidad) + cantidad
                else:
                    self.inventario.append(Alimento(
                        generar_codigo(self.inventario), nombre, cantidad, unidad,
                        catalogo.fecha_sugerida(nombre), categoria
                    ))
            self.guardar()
            total = len(seleccionados)
            ventana.destroy()
            self.seleccionar_menu("Inventario", self.mostrar_inventario)
            messagebox.showinfo(
                "Listo", f"Se agregaron {total} ingrediente(s) a tu inventario."
            )

        boton_agregar = self.boton(pie, "Agregar 0 ingrediente(s)", agregar,
                                   color=EXITO)
        boton_agregar.pack(side="right")
        self.boton(pie, "Cancelar", ventana.destroy,
                   color=PANEL_CLARO).pack(side="right", padx=8)

        busqueda_var.trace_add("write", dibujar)
        dibujar()
        dibujar_seleccion()

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
            self.guardar()
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
        self.vista_recetas = VistaRecetas(self)

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
            if not pregunta.winfo_exists():
                return

            agregar_mensaje(respuesta, False)
            estado.config(
                text="●  Listo para ayudarte",
                fg=EXITO
            )

            pregunta.config(state="normal")
            boton_enviar.config(state="normal")
            pregunta.focus_set()

        def consultar_en_hilo(texto, buzon):
            try:
                buzon.append(consultar_ia(texto, self.inventario))
            except Exception as error:
                buzon.append(f"Error al consultar la IA: {error}")

        def esperar_respuesta(buzon):
            if not pregunta.winfo_exists():
                return
            if buzon:
                terminar_consulta(buzon[0])
            else:
                pregunta.after(200, lambda: esperar_respuesta(buzon))

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

            buzon = []
            threading.Thread(
                target=consultar_en_hilo,
                args=(texto, buzon),
                daemon=True
            ).start()
            esperar_respuesta(buzon)

        pregunta.bind("<Return>", lambda e: enviar())
        pregunta.focus_set()

    # ==================================================
    # CERRAR APLICACIÓN
    # ==================================================

    def guardar(self):
        """Guarda el inventario y avisa si falla (antes fallaba en silencio)."""
        if guardar_datos(self.inventario):
            return True
        messagebox.showerror(
            "Error al guardar",
            "No se pudo guardar el inventario en datos/inventario.dat. "
            "Los cambios siguen en memoria."
        )
        return False

    def cerrar(self):
        if not self.guardar() and not messagebox.askyesno(
            "Salir sin guardar", "¿Cerrar de todas formas y perder los cambios?"
        ):
            return

        self.ventana.destroy()


def iniciar_interfaz():
    ventana = tk.Tk()
    Aplicacion(ventana)
    ventana.mainloop()
