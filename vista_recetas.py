"""Pantalla de recetas: selección de ingredientes y recetas en tarjetas."""

import threading
import tkinter as tk
from datetime import date
from tkinter import messagebox, ttk

import catalogo
from asistente_ia import generar_recetas
from estilos import *

COLORES_NUTRIENTES = (
    ("Calorías", "kcal", AMARILLO),
    ("Proteína", "g", TURQUESA),
    ("Carbohidratos", "g", AZUL),
    ("Grasa", "g", CORAL),
    ("Fibra", "g", EXITO),
)


# ======================================================
# LECTURA DEL TEXTO DE LA IA
# ======================================================

def _nutrientes(linea):
    """'Calorías: 540 kcal | Proteína: 52 g' -> {'Calorías': '540', ...}"""
    datos = {}
    for parte in linea.split("|"):
        if ":" not in parte:
            continue
        clave, valor = parte.split(":", 1)
        numero = "".join(c for c in valor if c.isdigit() or c in ".,")
        datos[clave.strip().capitalize()] = numero.strip(".,") or "—"
    return datos


def interpretar(texto):
    """Convierte el texto con formato 'RECETA: ...' en una lista de dicts.

    Devuelve (aviso, recetas). 'aviso' es el texto previo a la primera
    receta (por ejemplo, el mensaje de modo sin conexión).
    """
    aviso, recetas, actual, seccion = [], [], None, None

    for bruta in texto.splitlines():
        linea = bruta.strip().replace("**", "").lstrip("#").strip()
        if not linea:
            continue
        minus = linea.lower()

        if minus.startswith("receta:"):
            actual = {
                "nombre": linea.split(":", 1)[1].strip(), "meta": "",
                "ingredientes": [], "pasos": [], "porcion": {},
                "total": {}, "aprovecha": [], "texto": [linea],
            }
            recetas.append(actual)
            seccion = None
            continue

        if actual is None:
            aviso.append(linea)
            continue

        actual["texto"].append(linea)
        if minus.startswith("porciones"):
            actual["meta"] = linea
        elif minus.startswith("ingredientes"):
            seccion = "ingredientes"
        elif minus.startswith("preparaci"):
            seccion = "pasos"
        elif "nutricional" in minus and "porci" in minus:
            seccion = "porcion"
        elif "nutricional" in minus:
            seccion = "total"
        elif minus.startswith("aprovecha"):
            seccion = "aprovecha"
        elif minus.startswith("calor") and seccion in ("porcion", "total"):
            actual[seccion] = _nutrientes(linea)
        elif seccion in ("ingredientes", "aprovecha"):
            actual[seccion].append(linea.lstrip("-•* ").strip())
        elif seccion == "pasos":
            paso = linea.lstrip("-•* ")
            if paso[:1].isdigit() and "." in paso[:4]:
                paso = paso.split(".", 1)[1].strip()
            actual["pasos"].append(paso)

    return "\n".join(aviso), recetas


def _meta(receta):
    """'Porciones: 2   Tiempo: 30 minutos' -> ('2', '30 min')"""
    texto = receta["meta"].lower()
    porciones = tiempo = ""
    if "porciones" in texto:
        porciones = "".join(
            c for c in texto.split("porciones", 1)[1].split("tiempo")[0]
            if c.isdigit()
        )
    if "tiempo" in texto:
        tiempo = texto.split("tiempo", 1)[1].strip(" :")
        tiempo = tiempo.replace("minutos", "min").replace("aprox.", "").strip()
        if tiempo.isdigit():
            tiempo += " min"
    return porciones, tiempo


# ======================================================
# PANTALLA
# ======================================================

class VistaRecetas:

    def __init__(self, app):
        self.app = app
        self.contenido = app.contenido
        self.disponibles = [
            a for a in app.inventario if float(getattr(a, "cantidad", 0)) > 0
        ]
        # Los vencidos quedan desmarcados: no se recomienda cocinarlos.
        self.usar = {
            id(a): not ((d := self._dias(a)) is not None and d < 0)
            for a in self.disponibles
        }
        self.chips = {}
        self._acomodar = lambda *a: None
        self.ultimo_texto = ""
        self.construir()

    # ---------- utilidades ----------

    @staticmethod
    def _dias(alimento):
        try:
            return (date.fromisoformat(str(alimento.fecha_vencimiento))
                    - date.today()).days
        except (ValueError, TypeError):
            return None

    def _chip(self, padre, texto, fondo, color=BLANCO, tam=9):
        return tk.Label(
            padre, text=texto, bg=fondo, fg=color, padx=10, pady=4,
            font=(FUENTE, tam)
        )

    # ---------- construcción ----------

    def construir(self):
        app = self.app
        app.encabezado(
            "Recetas inteligentes",
            "Elige lo que quieres usar y la IA te propone platillos con su "
            "información nutricional."
        )

        # Toda la página (resumen, selector y recetas) se desplaza junta.
        self._zona_desplazable()

        tarjetas = tk.Frame(self.interior, bg=FONDO)
        tarjetas.pack(fill="x")
        proximos = sum(
            1 for a in self.disponibles
            if (d := self._dias(a)) is not None and 0 <= d <= 3
        )
        calorias = sum(
            (catalogo.nutricion_total(a.nombre, a.cantidad, a.unidad) or {})
            .get("kcal", 0) for a in self.disponibles
        )
        app.tarjeta(tarjetas, "Ingredientes disponibles", len(self.disponibles), TURQUESA)
        app.tarjeta(tarjetas, "Vencen en 3 días o menos", proximos, AMARILLO)
        app.tarjeta(tarjetas, "Calorías en tu refri", f"{calorias:,.0f}", MORADO_CLARO)

        self._selector()

        self.estado = tk.Label(
            self.interior, text="", bg=FONDO, fg=GRIS, font=(FUENTE, 10),
            anchor="w"
        )
        self.estado.pack(fill="x", padx=5, pady=(14, 6))
        self.resultados = tk.Frame(self.interior, bg=FONDO)
        self.resultados.pack(fill="both", expand=True, padx=5, pady=(0, 20))
        self._estado_vacio()

    def _selector(self):
        panel = self.app.panel(self.interior, 14)
        panel.pack(fill="x", padx=5, pady=(14, 0))

        cabecera = tk.Frame(panel, bg=PANEL)
        cabecera.pack(fill="x")
        tk.Label(
            cabecera, text="¿CON QUÉ QUIERES COCINAR?", bg=PANEL, fg=GRIS,
            font=(FUENTE, 8, "bold")
        ).pack(side="left")
        for texto, valor in (("Ninguno", False), ("Todos", True)):
            enlace = tk.Label(
                cabecera, text=texto, bg=PANEL, fg=MORADO_CLARO,
                cursor="hand2", font=(FUENTE, 8, "underline")
            )
            enlace.pack(side="right", padx=6)
            enlace.bind("<Button-1>", lambda e, v=valor: self._marcar_todos(v))

        cuerpo = tk.Frame(panel, bg=PANEL)
        cuerpo.pack(fill="x", pady=(8, 0))

        self.boton_generar = self.app.boton(
            cuerpo, "✦  Generar recetas", self.generar, color=MORADO
        )
        self.boton_generar.config(font=(FUENTE, 11, "bold"), padx=22, pady=14)
        self.boton_generar.pack(side="right", padx=(12, 0))

        grilla = tk.Frame(cuerpo, bg=PANEL, height=40)
        grilla.pack(side="left", fill="x", expand=True)
        grilla.pack_propagate(False)

        if not self.disponibles:
            tk.Label(
                grilla,
                text="Tu inventario está vacío. Agrega alimentos desde "
                     "«Inventario → Desde mi refri».",
                bg=PANEL, fg=GRIS, font=(FUENTE, 10)
            ).pack(anchor="w")
            return

        orden = sorted(
            self.disponibles,
            key=lambda a: 999 if self._dias(a) is None else self._dias(a)
        )
        for a in orden:
            chip = tk.Label(grilla, font=(FUENTE, 9), padx=12, pady=6,
                            cursor="hand2")
            chip.bind("<Button-1>", lambda e, al=a: self._alternar(al))
            self.chips[id(a)] = (chip, a)
            self._pintar_chip(a)

        def acomodar(evento=None):
            """Coloca los chips en filas que se ajustan al ancho disponible."""
            ancho = max(grilla.winfo_width(), 200)
            x = y = alto_fila = 0
            for chip, _ in self.chips.values():
                w, h = chip.winfo_reqwidth(), chip.winfo_reqheight()
                if x and x + w > ancho:
                    x, y = 0, y + alto_fila + 6
                chip.place(x=x, y=y)
                x += w + 6
                alto_fila = max(alto_fila, h)
            alto = y + alto_fila
            if int(grilla.cget("height")) != alto:
                grilla.configure(height=alto)

        self._acomodar = acomodar
        grilla.bind("<Configure>", acomodar)
        grilla.after_idle(acomodar)

    def _pintar_chip(self, alimento):
        chip, _ = self.chips[id(alimento)]
        activo = self.usar[id(alimento)]
        dias = self._dias(alimento)
        vencido = dias is not None and dias < 0
        if vencido:
            aviso = "  ⚠ vencido"
        elif dias is not None and dias <= 3:
            aviso = "  ⏳"
        else:
            aviso = ""
        chip.config(
            text=("✓ " if activo else "") + alimento.nombre + aviso,
            bg=MORADO if activo else PANEL_SECUNDARIO,
            fg=BLANCO if activo else (CORAL if vencido else GRIS)
        )

    def _alternar(self, alimento):
        self.usar[id(alimento)] = not self.usar[id(alimento)]
        self._pintar_chip(alimento)
        self._acomodar()

    def _marcar_todos(self, valor):
        for clave, (_, alimento) in self.chips.items():
            self.usar[clave] = valor
            self._pintar_chip(alimento)
        self._acomodar()

    def _zona_desplazable(self):
        marco = tk.Frame(self.contenido, bg=FONDO)
        marco.pack(fill="both", expand=True, padx=(25, 8), pady=(0, 8))

        self.lienzo = tk.Canvas(marco, bg=FONDO, highlightthickness=0)
        barra = ttk.Scrollbar(marco, orient="vertical", command=self.lienzo.yview)
        self.interior = tk.Frame(self.lienzo, bg=FONDO)
        ventana_id = self.lienzo.create_window((0, 0), window=self.interior,
                                               anchor="nw")
        self.interior.bind(
            "<Configure>",
            lambda e: self.lienzo.configure(scrollregion=self.lienzo.bbox("all"))
        )
        # El contenido siempre ocupa todo el ancho disponible.
        self.lienzo.bind(
            "<Configure>",
            lambda e: self.lienzo.itemconfigure(ventana_id, width=e.width)
        )
        self.lienzo.configure(yscrollcommand=barra.set)
        barra.pack(side="right", fill="y")
        self.lienzo.pack(side="left", fill="both", expand=True)

        def rueda(evento):
            try:
                self.lienzo.yview_scroll(int(-evento.delta / 120), "units")
            except tk.TclError:
                pass

        self.lienzo.bind("<Enter>", lambda e: self.lienzo.bind_all("<MouseWheel>", rueda))
        self.lienzo.bind("<Leave>", lambda e: self.lienzo.unbind_all("<MouseWheel>"))

    def _limpiar_resultados(self):
        for w in self.resultados.winfo_children():
            w.destroy()

    def _ir_a_resultados(self):
        """Desplaza la página para que se vean las recetas."""
        self.interior.update_idletasks()
        alto = max(1, self.interior.winfo_height())
        self.lienzo.yview_moveto(self.estado.winfo_y() / alto)

    def _estado_vacio(self):
        self._limpiar_resultados()
        caja = tk.Frame(self.resultados, bg=FONDO)
        caja.pack(expand=True, pady=40)
        tk.Label(caja, text="🍳", bg=FONDO, font=(FUENTE, 40)).pack()
        tk.Label(
            caja, text="¿Qué cocinamos hoy?", bg=FONDO, fg=BLANCO,
            font=(FUENTE, 16, "bold")
        ).pack(pady=(6, 2))
        tk.Label(
            caja,
            text="Marca los ingredientes de arriba y presiona «Generar recetas».\n"
                 "Los que vencen pronto (⏳) aparecen primero.",
            bg=FONDO, fg=GRIS, font=(FUENTE, 10), justify="center"
        ).pack()

    # ---------- generación ----------

    def generar(self):
        elegidos = [a for a in self.disponibles if self.usar[id(a)]]
        if not elegidos:
            messagebox.showinfo(
                "Sin ingredientes",
                "Selecciona al menos un ingrediente para cocinar."
                if self.disponibles else
                "Agrega alimentos a tu inventario antes de generar recetas."
            )
            return

        self.boton_generar.config(state="disabled", text="Cocinando…")
        self._limpiar_resultados()
        caja = tk.Frame(self.resultados, bg=FONDO)
        caja.pack(expand=True, pady=50)
        animacion = tk.Label(caja, text="", bg=FONDO, fg=MORADO_CLARO,
                             font=(FUENTE, 30))
        animacion.pack()
        tk.Label(
            caja, text=f"Pensando recetas con {len(elegidos)} ingrediente(s)…",
            bg=FONDO, fg=GRIS, font=(FUENTE, 11)
        ).pack(pady=(6, 0))
        self.estado.config(text="")

        respuesta = []

        def trabajo():
            try:
                respuesta.append(generar_recetas(elegidos))
            except Exception as error:
                respuesta.append(f"No se pudieron generar las recetas: {error}")

        cuadros = "🥕🍅🧅🥦🍗🧀🍚🥚"

        def esperar(paso=0):
            if not self.lienzo.winfo_exists():
                return
            if not respuesta:
                if animacion.winfo_exists():
                    animacion.config(text=cuadros[paso % len(cuadros)])
                self.lienzo.after(250, lambda: esperar(paso + 1))
                return
            self.boton_generar.config(state="normal", text="✦  Generar otras")
            self.mostrar(respuesta[0])

        threading.Thread(target=trabajo, daemon=True).start()
        self._ir_a_resultados()
        esperar()

    # ---------- resultados ----------

    def mostrar(self, texto):
        self.ultimo_texto = texto
        self._limpiar_resultados()
        aviso, recetas = interpretar(texto)

        if aviso:
            sin_conexion = aviso.lower().startswith("modo sin conexi")
            banda = tk.Frame(self.resultados, bg="#3A3122" if sin_conexion else PANEL,
                             padx=14, pady=10)
            banda.pack(fill="x", pady=(0, 10))
            tk.Label(
                banda, text=("⚠  " if sin_conexion else "ℹ  ") + aviso,
                bg=banda["bg"], fg=AMARILLO if sin_conexion else TEXTO,
                font=(FUENTE, 9), justify="left", anchor="w", wraplength=900
            ).pack(fill="x")

        if not recetas:
            # La IA no respetó el formato: se muestra el texto tal cual.
            caja = self.app.panel(self.resultados, 16)
            caja.pack(fill="x")
            tk.Label(
                caja, text=texto if not aviso else "", bg=PANEL, fg=TEXTO,
                font=(FUENTE, 10), justify="left", anchor="w", wraplength=900
            ).pack(fill="x")
            self.estado.config(text="")
            return

        self.estado.config(
            text=f"●  {len(recetas)} receta(s) listas", fg=EXITO
        )
        for numero, receta in enumerate(recetas, 1):
            self._tarjeta_receta(numero, receta)
        self._ir_a_resultados()

    def _tarjeta_receta(self, numero, receta):
        exterior = tk.Frame(self.resultados, bg=MORADO)
        exterior.pack(fill="x", pady=(0, 16))
        tarjeta = tk.Frame(exterior, bg=PANEL, padx=22, pady=18)
        tarjeta.pack(fill="x", padx=(5, 0))  # franja de color a la izquierda

        # Título y datos rápidos
        cabecera = tk.Frame(tarjeta, bg=PANEL)
        cabecera.pack(fill="x")
        tk.Label(
            cabecera, text=f"RECETA {numero}", bg=PANEL, fg=MORADO_CLARO,
            font=(FUENTE, 8, "bold")
        ).pack(anchor="w")
        fila_titulo = tk.Frame(cabecera, bg=PANEL)
        fila_titulo.pack(fill="x")
        tk.Label(
            fila_titulo, text=receta["nombre"], bg=PANEL, fg=BLANCO,
            font=(FUENTE, 16, "bold"), anchor="w", justify="left",
            wraplength=700
        ).pack(side="left")

        copiar = tk.Label(
            fila_titulo, text="📋 Copiar", bg=PANEL_CLARO, fg=BLANCO,
            padx=10, pady=4, cursor="hand2", font=(FUENTE, 9)
        )
        copiar.pack(side="right")
        copiar.bind("<Button-1>", lambda e: self._copiar(receta, copiar))

        porciones, tiempo = _meta(receta)
        chips = tk.Frame(cabecera, bg=PANEL)
        chips.pack(anchor="w", pady=(8, 0))
        if porciones:
            self._chip(chips, f"👥  {porciones} porciones", PANEL_SECUNDARIO).pack(side="left", padx=(0, 6))
        if tiempo:
            self._chip(chips, f"⏱  {tiempo}", PANEL_SECUNDARIO).pack(side="left", padx=(0, 6))
        self._chip(chips, f"🧾  {len(receta['ingredientes'])} ingredientes",
                   PANEL_SECUNDARIO).pack(side="left")

        # Nutrición por porción
        if receta["porcion"]:
            self._bloque_nutricion(tarjeta, receta)

        # Ingredientes | Preparación
        cuerpo = tk.Frame(tarjeta, bg=PANEL)
        cuerpo.pack(fill="x", pady=(14, 0))
        cuerpo.columnconfigure(0, weight=2, uniform="col")
        cuerpo.columnconfigure(1, weight=3, uniform="col")

        izquierda = tk.Frame(cuerpo, bg=PANEL_SECUNDARIO, padx=14, pady=12)
        izquierda.grid(row=0, column=0, sticky="nsew", padx=(0, 10))
        tk.Label(izquierda, text="INGREDIENTES", bg=PANEL_SECUNDARIO,
                 fg=TURQUESA, font=(FUENTE, 8, "bold")).pack(anchor="w", pady=(0, 6))
        for ing in receta["ingredientes"]:
            adicional = "por conseguir" in ing.lower() or "adicional" in ing.lower()
            tk.Label(
                izquierda, text=("＋ " if adicional else "•  ") + ing,
                bg=PANEL_SECUNDARIO, fg=AMARILLO if adicional else TEXTO,
                font=(FUENTE, 10), anchor="w", justify="left", wraplength=300
            ).pack(fill="x", pady=1)

        derecha = tk.Frame(cuerpo, bg=PANEL_SECUNDARIO, padx=14, pady=12)
        derecha.grid(row=0, column=1, sticky="nsew")
        tk.Label(derecha, text="PREPARACIÓN", bg=PANEL_SECUNDARIO,
                 fg=TURQUESA, font=(FUENTE, 8, "bold")).pack(anchor="w", pady=(0, 6))
        for n, paso in enumerate(receta["pasos"], 1):
            fila = tk.Frame(derecha, bg=PANEL_SECUNDARIO)
            fila.pack(fill="x", pady=3)
            tk.Label(
                fila, text=str(n), bg=MORADO, fg=BLANCO, width=2,
                font=(FUENTE, 9, "bold")
            ).pack(side="left", anchor="n", padx=(0, 10))
            tk.Label(
                fila, text=paso, bg=PANEL_SECUNDARIO, fg=TEXTO,
                font=(FUENTE, 10), anchor="w", justify="left", wraplength=470
            ).pack(side="left", fill="x", expand=True)

        # Qué aprovecha
        if receta["aprovecha"]:
            pie = tk.Frame(tarjeta, bg=PANEL)
            pie.pack(fill="x", pady=(14, 0))
            tk.Label(pie, text="♻  Aprovecha:", bg=PANEL, fg=EXITO,
                     font=(FUENTE, 9, "bold")).pack(side="left", padx=(0, 8))
            for item in receta["aprovecha"][:6]:
                self._chip(pie, item, "#1F3B33", EXITO, 9).pack(side="left", padx=2)

    def _bloque_nutricion(self, padre, receta):
        caja = tk.Frame(padre, bg=PANEL)
        caja.pack(fill="x", pady=(14, 0))
        tk.Label(caja, text="INFORMACIÓN NUTRICIONAL POR PORCIÓN", bg=PANEL,
                 fg=GRIS, font=(FUENTE, 8, "bold")).pack(anchor="w", pady=(0, 6))
        fila = tk.Frame(caja, bg=PANEL)
        fila.pack(fill="x")
        for i, (nombre, unidad, color) in enumerate(COLORES_NUTRIENTES):
            fila.columnconfigure(i, weight=1, uniform="nut")
            celda = tk.Frame(fila, bg=PANEL_SECUNDARIO, padx=10, pady=8)
            celda.grid(row=0, column=i, sticky="nsew", padx=(0 if i == 0 else 6, 0))
            tk.Frame(celda, bg=color, height=3).pack(fill="x", pady=(0, 6))
            valor = receta["porcion"].get(nombre, "—")
            tk.Label(celda, text=f"{valor} {unidad}" if valor != "—" else "—",
                     bg=PANEL_SECUNDARIO, fg=color,
                     font=(FUENTE, 14, "bold")).pack(anchor="w")
            tk.Label(celda, text=nombre, bg=PANEL_SECUNDARIO, fg=GRIS,
                     font=(FUENTE, 8)).pack(anchor="w")

        total = receta["total"]
        if total:
            partes = [f"{total.get(n, '—')} {u}  {n.lower()}"
                      for n, u, _ in COLORES_NUTRIENTES if n in total]
            tk.Label(
                caja, text="Platillo completo:  " + "   ·   ".join(partes),
                bg=PANEL, fg=GRIS, font=(FUENTE, 9), anchor="w"
            ).pack(fill="x", pady=(6, 0))

    def _copiar(self, receta, etiqueta):
        self.app.ventana.clipboard_clear()
        self.app.ventana.clipboard_append("\n".join(receta["texto"]))
        etiqueta.config(text="✓ Copiada", bg=EXITO)
        etiqueta.after(
            1500,
            lambda: etiqueta.winfo_exists()
            and etiqueta.config(text="📋 Copiar", bg=PANEL_CLARO)
        )
