
"""Integración de Cero Desperdicio con la API de OpenAI."""

import os
from datetime import date

from catalogo import nutricion_100g


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

    # OPENAI_BASE_URL permite usar proveedores compatibles con OpenAI,
    # incluso gratuitos: Google Gemini, Groq u Ollama (local).
    base_url = os.getenv("OPENAI_BASE_URL", "").strip() or None
    # Sin límite, una llamada colgada dejaba la app "pensando" hasta 10 min.
    return OpenAI(
        api_key=api_key, base_url=base_url, timeout=60, max_retries=0
    )


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
            "dias_para_vencer": dias,
            "nutricion_por_100g": nutricion_100g(
                getattr(alimento, "nombre", "")
            )
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

    mensaje = (
        f"Fecha actual: {date.today().isoformat()}\n"
        f"Inventario registrado: {productos}\n\n"
        f"Solicitud del usuario: {prompt}"
    )

    if os.getenv("OPENAI_BASE_URL", "").strip():
        return _consultar_compatible(cliente, modelo, mensaje)

    parametros = dict(
        model=modelo,
        instructions=_INSTRUCCIONES,
        input=mensaje,
        # En los modelos con razonamiento, este límite incluye los tokens
        # que el modelo usa para "pensar"; con poco margen la receta salía
        # cortada (solo el nombre).
        max_output_tokens=int(os.getenv("OPENAI_MAX_TOKENS", "12000")),
    )

    try:
        # Razonamiento bajo: más rápido, más barato y deja tokens al texto.
        respuesta = cliente.responses.create(
            reasoning={"effort": "low"}, **parametros
        )
    except Exception as error:
        if "reasoning" not in str(error).lower():
            raise
        # Modelos sin razonamiento (p. ej. gpt-4o) no aceptan ese parámetro.
        respuesta = cliente.responses.create(**parametros)

    texto = (getattr(respuesta, "output_text", "") or "").strip()

    if getattr(respuesta, "status", "") == "incomplete":
        aviso = (
            "\n\n(La respuesta se cortó por el límite de tokens. "
            "Subí OPENAI_MAX_TOKENS en el archivo .env.)"
        )
        return (texto + aviso) if texto else aviso.strip()

    if not texto:
        return "La IA no devolvió una respuesta. Intentá nuevamente."

    return texto


def _consultar_compatible(cliente, modelos, mensaje):
    """Gemini, Groq, Ollama y otros: usan la API de chat de OpenAI.

    OPENAI_MODEL puede traer varios modelos separados por coma: si uno
    está retirado (404), saturado (503), sin cuota (429) o tarda demasiado,
    se prueba el siguiente.
    """
    lista = [m.strip() for m in modelos.split(",") if m.strip()]
    ultimo_error = None

    for modelo in lista:
        try:
            respuesta = _chat(cliente, modelo, mensaje)
            break
        except Exception as error:
            print(f"Modelo {modelo} falló: {error}")
            ultimo_error = error
    else:
        raise ultimo_error

    opcion = respuesta.choices[0]
    texto = (opcion.message.content or "").strip()

    if opcion.finish_reason == "length":
        aviso = (
            "\n\n(La respuesta se cortó por el límite de tokens. "
            "Subí OPENAI_MAX_TOKENS en el archivo .env.)"
        )
        return (texto + aviso) if texto else aviso.strip()

    return texto or "La IA no devolvió una respuesta. Intentá nuevamente."


def _chat(cliente, modelo, mensaje):
    parametros = dict(
        model=modelo,
        messages=[
            {"role": "system", "content": _INSTRUCCIONES},
            {"role": "user", "content": mensaje},
        ],
        max_tokens=int(os.getenv("OPENAI_MAX_TOKENS", "12000")),
    )

    try:
        # Los modelos que "piensan" dejan más tokens para la receta con
        # razonamiento bajo. Los que no lo admiten dan error y se
        # reintenta sin ese parámetro.
        return cliente.chat.completions.create(
            reasoning_effort="low", **parametros
        )
    except Exception as error:
        if "reasoning" not in str(error).lower():
            raise
        return cliente.chat.completions.create(**parametros)


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

Usá EXACTAMENTE este formato de texto plano (sin Markdown, sin # ni **):

RECETA: <nombre atractivo>
Porciones: <número>   Tiempo: <minutos>
Ingredientes:
- <ingrediente> - <cantidad aproximada>
Preparación:
1. <paso>
Información nutricional por porción:
Calorías: <número> kcal | Proteína: <número> g | Carbohidratos: <número> g | Grasa: <número> g | Fibra: <número> g
Información nutricional del platillo completo:
Calorías: <número> kcal | Proteína: <número> g | Carbohidratos: <número> g | Grasa: <número> g | Fibra: <número> g
Aprovecha:
- <alimentos del inventario que ayuda a aprovechar>

Calculá la información nutricional con los datos "nutricion_por_100g" del
inventario cuando existan (son valores por 100 g); si faltan, estimalos.
Si hace falta un ingrediente que no aparece en el inventario, marcálo como
"(ingrediente adicional por conseguir)". No incluyás alimentos vencidos.
"""

    try:
        return _consultar(solicitud, disponibles)
    except Exception as error:
        # Sin clave, sin internet o sin crédito: se usan recetas locales
        # para que la función siga sirviendo.
        print(f"Error en generar_recetas: {error}")
        from recetas_locales import generar
        return (
            "Modo sin conexión: " + _mensaje_error(error) + "\n"
            "Mientras tanto, estas son recetas sugeridas con tus ingredientes:\n\n"
            + generar(disponibles)
        )


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
