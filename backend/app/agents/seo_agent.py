# Sprint 8: Agente SEO — genera artículos de blog semanales
# TODO: Implementar en Sprint 8

SEO_SYSTEM_PROMPT = """
Eres el agente SEO de Hacienda La Carmelita, una finca turística premium de 100 hectáreas
en Lérida, Tolima, Colombia. La finca es parte del legado arrocero del Tolima.
Tu objetivo: generar artículos de blog que posicionen a haciendalacarmelita.com en Google.
"""

TEMAS_SEO = [
    {"kw": "finca para 16 personas tolima", "secondary": ["finca lérida", "alquiler finca Colombia"]},
    {"kw": "cabalgata tolima colombia", "secondary": ["turismo ecuestre", "caballos tolima"]},
    {"kw": "agritourism colombia arroz", "secondary": ["farm tourism colombia", "tolima rice farming"]},
    {"kw": "finca privada colombia familia", "secondary": ["turismo rural colombia", "finca exclusiva"]},
    {"kw": "hacienda arrocera tolima", "secondary": ["historia arroz colombia", "rio magdalena finca"]},
]


async def generar_articulo_seo(tema: dict):
    """Genera artículo de blog optimizado para Google."""
    raise NotImplementedError("TODO: Sprint 8")
