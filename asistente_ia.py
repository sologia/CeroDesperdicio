
"""Integración de Cero Desperdicio con la API de OpenAI."""

import os
from datetime import date


def _cargar_configuracion():
    try:
        from dotenv import load_dotenv
        load_dotenv()
    except ImportError:
        pass


def _obtener_cliente():
    _cargar_configuracion()
    api_key = os.getenv("OPENAI_API_KEY", "").strip()

    if not api_key:
        raise RuntimeError(
            "No se encontró OPENAI_API_KEY. Configurá tu clave en el archivo .env."
        )

    try:
        from openai import OpenAI
    except ImportError as error:
        raise RuntimeError(
            "No está instalado OpenAI. Ejecutá: pip install openai python-dotenv"
        ) from error

    return OpenAI(api_key=api_key)


def _obtener_inventario(inventario):
    hoy = date.today()
    productos = []

    for alimento in inventario:
        try:
            vencimiento = date.fromisoformat(
                str(alimento.fecha_vencimiento)
            )
            dias = (vencimiento - hoy).days
        except (ValueError, TypeError, AttributeError):
            dias = None

        productos.append({
            "codigo": str(getattr(alimento, "codigo", "")),
            "nombre": str(getattr(alimento, "nombre", "Sin nombre")),
            "cantidad": getattr(alimento, "cantidad", 0),
            "unidad": str(getattr(alimento, "unidad", "")),
            "categoria": str(getattr(alimento, "categoria", "Otros")),
            "fecha_vencimiento": str(
                getattr(alimento, "fecha_vencimiento", "Sin fecha")
            ),
            "dias_para_vencer": dias
        })

    return productos


_INSTRUCCIONES = """
Sos el asistente de Cero Desperdicio, una aplicación académica para organizar
alimentos, aprovechar mejor los productos y reducir el desperdicio.

Respondé siempre en español, con tono amable, claro y práctico.
Usá el inventario recibido como fuente de verdad: no inventés productos,
cantidades, fechas ni categorías. Podés sugerir ingredientes adicionales,
pero indicá claramente que el usuario tendría que conseguirlos.

Priorizá alimentos próximos a vencer que todavía no estén vencidos.
Nunca recomendés consumir alimentos vencidos. La fecha de vencimiento por sí
sola no permite garantizar que un alimento sea seguro; recomendá seguir las
normas de inocuidad y las indicaciones del fabricante.

No afirmés que modificaste, guardaste o eliminaste datos del inventario.
Si la pregunta no tiene relación con alimentos, recetas, conservación o
reducción del desperdicio, explicá brevemente el propósito del asistente.
"""


def _consultar(prompt, inventario):
    cliente = _obtener_cliente()
    modelo = os.getenv("OPENAI_MODEL", "gpt-5.5").strip() or "gpt-5.5"
    productos = _obtener_inventario(inventario)

    respuesta = cliente.responses.create(
        model=modelo,
        instructions=_INSTRUCCIONES,
        input=(
            f"Fecha actual: {date.today().isoformat()}\n"
            f"Inventario registrado: {productos}\n\n"
            f"Solicitud del usuario: {prompt}"
        ),
        max_output_tokens=1200
    )

    texto = getattr(respuesta, "output_text", "")

    if not texto or not texto.strip():
        return "La IA no devolvió una respuesta. Intentá nuevamente."

    return texto.strip()


def consultar_ia(pregunta, inventario):
    """Responde preguntas usando el inventario actual."""

    if not pregunta or not pregunta.strip():
        return "Escribí una pregunta para poder ayudarte."

    try:
        return _consultar(pregunta.strip(), inventario)
    except Exception as error:
        print(f"Error en consultar_ia: {error}")
        return _mensaje_error(error)


def generar_recetas(inventario):
    """Genera recetas utilizando alimentos disponibles."""

    if not inventario:
        return (
            "Tu inventario está vacío. Registrá algunos alimentos "
            "para generar recetas."
        )

    disponibles = []
    hoy = date.today()

    for alimento in inventario:
        try:
            cantidad = float(getattr(alimento, "cantidad", 0))
        except (ValueError, TypeError):
            cantidad = 0

        if cantidad <= 0:
            continue

        try:
            vencimiento = date.fromisoformat(
                str(alimento.fecha_vencimiento)
            )
            dias = (vencimiento - hoy).days
        except (ValueError, TypeError, AttributeError):
            dias = None

        if dias is not None and dias < 0:
            continue

        disponibles.append(alimento)

    if not disponibles:
        return (
            "No encontré alimentos disponibles y no vencidos "
            "para preparar recetas. Revisá las cantidades y fechas."
        )

    solicitud = """
Generá 3 recetas prácticas usando principalmente los alimentos disponibles
que aparecen en el inventario. Priorizá los que vencen primero.

Para cada receta incluí:
1. Nombre atractivo.
2. Ingredientes y cantidades aproximadas, sin inventar existencias.
3. Preparación paso a paso.
4. Tiempo aproximado.
5. Qué alimentos del inventario ayuda a aprovechar.

Si hace falta un ingrediente que no aparece en el inventario, marcálo como
"Ingrediente adicional por conseguir". No incluyás alimentos vencidos.
Usá un formato ordenado, fácil de leer y adecuado para cocinar en casa.
"""

    try:
        return _consultar(solicitud, disponibles)
    except Exception as error:
        print(f"Error en generar_recetas: {error}")
        return _mensaje_error(error)


def _mensaje_error(error):
    mensaje = str(error).lower()

    if isinstance(error, RuntimeError):
        return str(error)

    if (
        "authentication" in mensaje
        or "api key" in mensaje
        or "unauthorized" in mensaje
    ):
        return (
            "La API rechazó la clave. Revisá que OPENAI_API_KEY "
            "esté bien escrita y corresponda a una clave activa."
        )

    if (
        "rate limit" in mensaje
        or "quota" in mensaje
        or "billing" in mensaje
    ):
        return (
            "La cuenta de API alcanzó un límite o no tiene crédito "
            "disponible. Revisá el uso y la facturación."
        )

    if "connection" in mensaje or "timeout" in mensaje:
        return (
            "No pude conectar con OpenAI. Revisá tu conexión "
            "a Internet e intentá otra vez."
        )

    return (
        "No se pudo completar la solicitud a la IA. Revisá la API Key, "
        "el modelo y la conexión. Detalle técnico: " + str(error)
    )
