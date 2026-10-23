import urllib.request
import urllib.error
import re
import gzip
import shutil
import xml.etree.ElementTree as ET
from datetime import datetime, timedelta, timezone
from html import unescape

OUTPUT_XML = "epg_peru.xml"
OUTPUT_GZ = "epg_peru.xml.gz"
OUTPUT_DEFAULT = "epg.xml"
TIMEZONE_OFFSET = "-0500"

# Lista completa de canales peruanos según el panel XUI.one del usuario
CHANNELS_CONFIG = [
    {
        "id": "america-tv.pe",
        "name": "AMERICA TV",
        "streams": ["PERU ®| AMERICA TV SD", "PERU ®| AMERICA TV HD"],
        "icon": "https://cdn.mitvstatic.com/channels/pe_america-television_m.png",
        "source": "mitv",
        "slug": "america-television",
        "category": "Generalista",
    },
    {
        "id": "latina-tv.pe",
        "name": "LATINA TV",
        "streams": ["PERU ®| LATINA TV SD", "PERU ®| LATINA TV HD"],
        "icon": "https://cdn.mitvstatic.com/channels/pe_frecuencia-latina_m.png",
        "source": "mitv",
        "slug": "frecuencia-latina",
        "category": "Generalista",
    },
    {
        "id": "latina-noticias.pe",
        "name": "LATINA NOTICIAS",
        "streams": ["PERU ®| LATINA NOTICIAS HD"],
        "icon": "https://cdn.mitvstatic.com/channels/pe_frecuencia-latina_m.png",
        "source": "template",
        "template_key": "latina_noticias",
        "category": "Noticias",
    },
    {
        "id": "latina-clasicos.pe",
        "name": "LATINA CLASICOS",
        "streams": ["PERU ®| LATINA CLASICOS HD"],
        "icon": "https://cdn.mitvstatic.com/channels/pe_frecuencia-latina_m.png",
        "source": "template",
        "template_key": "latina_clasicos",
        "category": "Entretenimiento",
    },
    {
        "id": "atv.pe",
        "name": "ATV",
        "streams": ["PERU ®| ATV HD"],
        "icon": "https://cdn.mitvstatic.com/channels/pe_atv_m.png",
        "source": "mitv",
        "slug": "atv",
        "category": "Generalista",
    },
    {
        "id": "atv-mas.pe",
        "name": "ATV+",
        "streams": ["PERU ®| ATV+ HD"],
        "icon": "https://cdn.mitvstatic.com/channels/pe_atv-1_m.png",
        "source": "mitv",
        "slug": "atv-1",
        "category": "Noticias",
    },
    {
        "id": "atv-sur.pe",
        "name": "ATV SUR",
        "streams": ["PERU ®| ATV SUR HD"],
        "icon": "https://cdn.mitvstatic.com/channels/pe_atv-sur_m.png",
        "source": "mitv",
        "slug": "atv-sur",
        "category": "Regional",
    },
    {
        "id": "willax.pe",
        "name": "WILLAX TV",
        "streams": ["PERU ®| WILLAX SD", "PERU ®| WILLAX HD"],
        "icon": "https://cdn.mitvstatic.com/channels/pe_willax_m.png",
        "source": "mitv",
        "slug": "willax",
        "category": "Generalista",
    },
    {
        "id": "panamericana.pe",
        "name": "PANAMERICANA TV",
        "streams": ["PERU ®| PANAMERICANA SD", "PERU ®| PANAMERICANA HD"],
        "icon": "https://cdn.mitvstatic.com/channels/pe_panamericana-tv_m.png",
        "source": "mitv",
        "slug": "panamericana-tv",
        "category": "Generalista",
    },
    {
        "id": "rpp-tv.pe",
        "name": "RPP TV",
        "streams": ["PERU ®| RPP HD"],
        "icon": "https://upload.wikimedia.org/wikipedia/commons/thumb/5/59/RPP_logo.svg/512px-RPP_logo.svg.png",
        "source": "template",
        "template_key": "rpp",
        "category": "Noticias",
    },
    {
        "id": "pbo-tv.pe",
        "name": "PBO TV",
        "streams": ["PERU ®| PBO TV HD"],
        "icon": "",
        "source": "template",
        "template_key": "pbo",
        "category": "Noticias",
    },
    {
        "id": "canal-n.pe",
        "name": "CANAL N",
        "streams": ["PERU ®| CANAL N HD"],
        "icon": "",
        "source": "template",
        "template_key": "canal_n",
        "category": "Noticias",
    },
    {
        "id": "tv-peru.pe",
        "name": "TV PERU",
        "streams": ["PERU ®| TV PERU HD"],
        "icon": "https://cdn.mitvstatic.com/channels/pe_tv-peru_m.png",
        "source": "mitv",
        "slug": "tv-peru",
        "category": "Generalista",
    },
    {
        "id": "peru-magico.pe",
        "name": "PERU MAGICO",
        "streams": ["PERU ®| PERU MAGICO HD"],
        "icon": "",
        "source": "gatotv",
        "slug": "peru_magico",
        "category": "Variedades",
    },
    {
        "id": "global-tv.pe",
        "name": "GLOBAL TV",
        "streams": ["PERU ®| GLOBAL TV HD"],
        "icon": "",
        "source": "template",
        "template_key": "global_tv",
        "category": "Entretenimiento",
    },
    {
        "id": "tv-cosmos.pe",
        "name": "TV COSMOS",
        "streams": ["PERU ®| TV COSMOS HD"],
        "icon": "",
        "source": "template",
        "template_key": "regional",
        "region": "Trujillo / La Libertad",
        "category": "Regional",
    },
    {
        "id": "karibena-tv.pe",
        "name": "KARIBEÑA TV",
        "streams": ["PERU ®| KARIBEÑA"],
        "icon": "",
        "source": "template",
        "template_key": "karibena",
        "category": "Musical / Variedades",
    },
    {
        "id": "cultura24.pe",
        "name": "CULTURA 24 TV",
        "streams": ["PERU ®| CULTURA 24 TV HD"],
        "icon": "",
        "source": "template",
        "template_key": "cultura24",
        "category": "Cultural",
    },
    {
        "id": "ovacion-tv.pe",
        "name": "OVACION TV",
        "streams": ["PERU ®| OVACION TV HD"],
        "icon": "",
        "source": "template",
        "template_key": "ovacion",
        "category": "Deportes",
    },
    {
        "id": "exitosa-tv.pe",
        "name": "EXITOSA TV",
        "streams": ["PERU ®| EXITOSA TV HD"],
        "icon": "",
        "source": "template",
        "template_key": "exitosa",
        "category": "Noticias",
    },
    {
        "id": "creo-tv.pe",
        "name": "CREO TV",
        "streams": ["PERU ®| CREO TV HD"],
        "icon": "",
        "source": "template",
        "template_key": "regional",
        "region": "Perú",
        "category": "Regional",
    },
    {
        "id": "bh-tv.pe",
        "name": "BH TV (BETHEL)",
        "streams": ["PERU ®| BH TV HD"],
        "icon": "https://cdn.mitvstatic.com/channels/pe_bethel_m.png",
        "source": "mitv",
        "slug": "bethel",
        "category": "Familiar / Cultural",
    },
    {
        "id": "doble-c.pe",
        "name": "DOBLE C TV",
        "streams": ["PERU ®| DOBLE C HD"],
        "icon": "",
        "source": "template",
        "template_key": "regional",
        "region": "Perú",
        "category": "Variedades",
    },
    {
        "id": "fabulosa-tv.pe",
        "name": "FABULOSA TV",
        "streams": ["PERU ®| FABULOSA TV HD"],
        "icon": "",
        "source": "template",
        "template_key": "musical_variedades",
        "category": "Musical / Variedades",
    },
    {
        "id": "inkavision.pe",
        "name": "INKAVISION",
        "streams": ["PERU ®| INKAVISION HD"],
        "icon": "",
        "source": "template",
        "template_key": "regional",
        "region": "Perú",
        "category": "Regional",
    },
    {
        "id": "nativa-tv.pe",
        "name": "NATIVA TV",
        "streams": ["PERU ®| NATIVA HD"],
        "icon": "",
        "source": "template",
        "template_key": "nativa",
        "category": "Noticias / Deportes",
    },
    {
        "id": "antares-tv.pe",
        "name": "ANTARES TV",
        "streams": ["PERU ®| ANTARES TV HD"],
        "icon": "",
        "source": "template",
        "template_key": "regional",
        "region": "Cajamarca / Norte",
        "category": "Regional",
    },
    {
        "id": "andes-tv.pe",
        "name": "ANDES TV",
        "streams": ["PERU ®| ANDES TV HD"],
        "icon": "",
        "source": "template",
        "template_key": "regional",
        "region": "Sur Andino",
        "category": "Regional",
    },
    {
        "id": "a-uno-tv.pe",
        "name": "A UNO TV",
        "streams": ["PERU ®| A UNO TV HD"],
        "icon": "",
        "source": "template",
        "template_key": "regional",
        "region": "Norte Peruano",
        "category": "Regional",
    },
    {
        "id": "andina-rtv.pe",
        "name": "ANDINA RTV",
        "streams": ["PERU ®| ANDINA RTV HD"],
        "icon": "",
        "source": "template",
        "template_key": "regional",
        "region": "Centro / Andina",
        "category": "Regional",
    },
    {
        "id": "region-tv-callao.pe",
        "name": "REGION TV CALLAO",
        "streams": ["PERU ®| REGION TV CALLAO HD"],
        "icon": "",
        "source": "template",
        "template_key": "regional",
        "region": "Callao",
        "category": "Regional",
    },
    {
        "id": "sol-tv.pe",
        "name": "SOL TV",
        "streams": ["PERU ®| SOL TV HD"],
        "icon": "",
        "source": "template",
        "template_key": "sol_tv",
        "category": "Regional",
    },
    {
        "id": "abc-tv.pe",
        "name": "ABC TV",
        "streams": ["PERU ®| ABC TV HD"],
        "icon": "",
        "source": "template",
        "template_key": "regional",
        "region": "Perú",
        "category": "Variedades",
    },
    {
        "id": "amazonia-tv.pe",
        "name": "AMAZONIA TV",
        "streams": ["PERU ®| AMAZONIA TV HD"],
        "icon": "",
        "source": "template",
        "template_key": "regional",
        "region": "Oriente / Amazonía Peruana",
        "category": "Regional",
    },
    {
        "id": "36-huacho-tv.pe",
        "name": "36 HUACHO TV",
        "streams": ["PERU ®| 36 HUACHO TV HD"],
        "icon": "",
        "source": "template",
        "template_key": "regional",
        "region": "Huacho / Norte Chico",
        "category": "Regional",
    },
    {
        "id": "xtremo-tv.pe",
        "name": "XTREMO TV",
        "streams": ["PERU ®| XTREMO TV HD"],
        "icon": "",
        "source": "template",
        "template_key": "musical_variedades",
        "category": "Entretenimiento",
    },
    {
        "id": "lider-tv.pe",
        "name": "LIDER TV",
        "streams": ["PERU ®| LIDER TV HD"],
        "icon": "",
        "source": "template",
        "template_key": "regional",
        "region": "Perú",
        "category": "Regional",
    },
    {
        "id": "millenium-tv.pe",
        "name": "MILLENIUM TV",
        "streams": ["PERU ®| MILLENIUM TV HD"],
        "icon": "",
        "source": "template",
        "template_key": "regional",
        "region": "Perú",
        "category": "Regional",
    },
    {
        "id": "via-television.pe",
        "name": "VIA TELEVISION",
        "streams": ["PERU ®| VIA TELEVISION HD"],
        "icon": "",
        "source": "template",
        "template_key": "regional",
        "region": "Tarapoto / San Martín",
        "category": "Regional",
    },
    {
        "id": "usmptv.pe",
        "name": "USMPTV",
        "streams": ["PERU ®| USMPTV HD"],
        "icon": "",
        "source": "template",
        "template_key": "usmptv",
        "category": "Educativo / Cultural",
    },
    {
        "id": "liga-1.pe",
        "name": "LIGA 1",
        "streams": ["PERU ®| LIGA 1 SD", "PERU ®| LIGA 1 HD"],
        "icon": "",
        "source": "template",
        "template_key": "liga1",
        "category": "Deportes",
    },
    {
        "id": "liga-1-max.pe",
        "name": "LIGA 1 MAX",
        "streams": ["PERU ®| LIGA 1 MAX SD", "PERU ®| LIGA 1 MAX HD"],
        "icon": "",
        "source": "template",
        "template_key": "liga1_max",
        "category": "Deportes",
    },
    {
        "id": "movistar-deportes.pe",
        "name": "MOVISTAR DEPORTES",
        "streams": ["PERU ®| MOVISTAR DEPORTES SD", "PERU ®| MOVISTAR DEPORTES HD"],
        "icon": "",
        "source": "template",
        "template_key": "movistar_deportes",
        "category": "Deportes",
    },
]

# Plantillas horarias detalladas para canales informativos, deportivos y regionales de Perú
TEMPLATES = {
    "rpp": [
        ("00:00", "05:00", "Rotativa de la Madrugada", "Resumen informativo nocturno y noticias nacionales en vivo por RPP TV.", "Noticias"),
        ("05:00", "06:00", "La Rotativa del Aire - Primera Hora", "Las primeras informaciones del día desde todas las regiones del Perú.", "Noticias"),
        ("06:00", "08:00", "La Rotativa del Aire", "El noticiero líder de la mañana con enlaces en vivo, entrevistas y actualidad nacional.", "Noticias"),
        ("08:00", "10:00", "Ampliación de Noticias", "Análisis político, económico y entrevistas a los protagonistas de la noticia en el Perú.", "Noticias"),
        ("10:00", "12:00", "Encendidos", "Magazine matutino de servicios, salud, economía familiar y actualidad.", "Magazine"),
        ("12:00", "14:00", "La Rotativa del Aire - Edición Mediodía", "Cobertura completa de las noticias más importantes de la jornada.", "Noticias"),
        ("14:00", "16:00", "Fútbol como Cancha", "Toda la información de la Liga 1, Selección Peruana y el deporte internacional.", "Deportes"),
        ("16:00", "18:00", "Central de Informaciones", "Transmisión continua de noticias, enlaces regionales y último minuto.", "Noticias"),
        ("18:00", "19:30", "Conexión", "Actualidad nacional, tráfico, denuncias ciudadanas y análisis vespertino.", "Noticias"),
        ("19:30", "21:00", "Nada Está Dicho", "Debate político y análisis de la coyuntura nacional.", "Política"),
        ("21:00", "22:30", "Todo se Sabe", "Entrevistas a fondo e investigación periodística del acontecer peruano.", "Noticias"),
        ("22:30", "24:00", "Resumen Central RPP", "Recuento de los hechos más relevantes del día en el Perú y el mundo.", "Noticias"),
    ],
    "canal_n": [
        ("00:00", "06:00", "N Noticias - Madrugada", "Cobertura informativa continua minuto a minuto desde Lima y regiones.", "Noticias"),
        ("06:00", "08:00", "N Noticias - Edición Mañana", "Las noticias más importantes para iniciar el día bien informado.", "Noticias"),
        ("08:00", "10:00", "Primero a las 8", "Entrevistas políticas y análisis de los temas que marcan la agenda nacional.", "Política"),
        ("10:00", "12:00", "N en Directo", "Transmisiones en vivo desde el Congreso, Palacio de Gobierno y regiones.", "Noticias"),
        ("12:00", "14:00", "N Noticias - Edición Mediodía", "Resumen informativo del mediodía con enlaces en directo.", "Noticias"),
        ("14:00", "15:00", "N Deportes", "Información deportiva nacional e internacional.", "Deportes"),
        ("15:00", "18:00", "N Noticias - Edición Tarde", "Actualización informativa de la tarde y cobertura nacional.", "Noticias"),
        ("18:00", "20:00", "Cuentas Claras", "Análisis político, económico y social de la jornada en el Perú.", "Política"),
        ("20:00", "21:00", "Las Cosas como Son", "Periodismo de investigación y entrevistas centrales.", "Noticias"),
        ("21:00", "22:00", "Octavo Mandamiento", "Entrevistas de fondo y debate sobre la actualidad peruana e internacional.", "Política"),
        ("22:00", "24:00", "N Noticias - Edición Noche", "Cierre informativo con las noticias más destacadas del día.", "Noticias"),
    ],
    "pbo": [
        ("00:00", "06:00", "PBO Madrugada", "Repetición de los mejores programas y análisis de PBO.", "Variedades"),
        ("06:00", "08:30", "PBO Noticias - Mañana", "Información de primera mano, actualidad nacional y enlaces en vivo.", "Noticias"),
        ("08:30", "11:00", "Phillip Butters en Vivo", "Análisis político, entrevistas exclusivas y opinión sin censura.", "Opinión"),
        ("11:00", "13:00", "PBO Familia y Salud", "Consejos médicos, bienestar, gastronomía y entrevistas.", "Magazine"),
        ("13:00", "15:00", "Campeonísimo", "Debate deportivo, Liga 1 y selección peruana con Carlos Alberto Navarro.", "Deportes"),
        ("15:00", "18:00", "PBO Tarde Informativa", "Actualidad nacional, economía y política peruana.", "Noticias"),
        ("18:00", "20:00", "PBO Edición Central", "Resumen y análisis de los hechos políticos del día.", "Noticias"),
        ("20:00", "22:00", "PBO Debate y Opinión", "Mesa de análisis sobre la coyuntura nacional.", "Opinión"),
        ("22:00", "24:00", "Especiales PBO", "Lo mejor de la jornada en PBO TV.", "Noticias"),
    ],
    "exitosa": [
        ("00:00", "05:00", "La Hora Esotérica / Madrugada Exitosa", "Acompañamiento nocturno y resumen informativo nacional.", "Variedades"),
        ("05:00", "08:00", "Exitosa Perú", "Conexión directa con todas las regiones del país y noticias matinales.", "Noticias"),
        ("08:00", "11:00", "Hablemos Claro", "Análisis político, entrevistas y denuncias ciudadanas en vivo.", "Noticias"),
        ("11:00", "14:00", "Informamos y Opinamos", "Debate, entrevistas y cobertura en vivo desde todo el Perú.", "Noticias"),
        ("14:00", "16:00", "Exitosa Deportes", "Toda la polémica del fútbol peruano, Liga 1 y torneos internacionales.", "Deportes"),
        ("16:00", "18:00", "Contra el Tráfico", "Información al instante, actualidad y participación del público.", "Magazine"),
        ("18:00", "21:00", "Exitosa te Escucha", "Debate ciudadano, política nacional y enlaces en directo.", "Noticias"),
        ("21:00", "23:00", "Exitosa Noticias - Edición Noche", "Cierre informativo y análisis político del día.", "Noticias"),
        ("23:00", "24:00", "Resumen Exitosa", "Lo más destacado de la jornada informativa.", "Noticias"),
    ],
    "latina_noticias": [
        ("00:00", "05:30", "Latina Noticias 24/7 - Madrugada", "Cobertura continua de noticias nacionales e internacionales.", "Noticias"),
        ("05:30", "09:00", "Latina Noticias Matinal", "Información desde temprano con enlaces en vivo en Lima y provincias.", "Noticias"),
        ("09:00", "12:00", "Latina Noticias en Directo", "Seguimiento en vivo de las noticias del día y entrevistas.", "Noticias"),
        ("12:00", "14:30", "Latina Noticias Mediodía", "Resumen completo de la mañana y actualidad nacional.", "Noticias"),
        ("14:30", "18:00", "Tarde Informativa Latina", "Actualización minuto a minuto de la coyuntura peruana.", "Noticias"),
        ("18:00", "20:00", "Hora Punta", "Análisis de las noticias de la tarde y enlaces en directo.", "Noticias"),
        ("20:00", "22:30", "Latina Noticias Edición Central", "El noticiero central con reportajes a fondo e investigación.", "Noticias"),
        ("22:30", "24:00", "Buenas Nuevas, Malas Nuevas", "Análisis periodístico y resumen del cierre de jornada.", "Noticias"),
    ],
    "latina_clasicos": [
        ("00:00", "06:00", "Trasnoche de Clásicos Peruanos", "Las mejores series y programas históricos de la televisión peruana.", "Entretenimiento"),
        ("06:00", "09:00", "Clásicos Familiares de Latina", "Series y comedias clásicas para toda la familia.", "Comedia"),
        ("09:00", "12:00", "Grandes Novelas Peruanas", "Telenovelas y producciones nacionales inolvidables.", "Novelas"),
        ("12:00", "15:00", "El Especial del Humor - Clásicos", "Los mejores sketches y parodias del humor peruano.", "Comedia"),
        ("15:00", "18:00", "Tardes de Recuerdo en Latina", "Series emblemáticas que hicieron historia en el Perú.", "Series"),
        ("18:00", "21:00", "Maratón de Comedia Peruana", "Risas aseguradas con los programas clásicos más queridos.", "Comedia"),
        ("21:00", "24:00", "Estelares del Recuerdo", "Miniseries y producciones estelares de colección.", "Series"),
    ],
    "global_tv": [
        ("00:00", "06:00", "Cine de Trasnoche", "Selección de películas de acción, suspenso y aventura.", "Cine"),
        ("06:00", "09:00", "Mañanas Animadas en Global", "Dibujos animados y series infantiles clásicas.", "Infantil"),
        ("09:00", "12:00", "Series Clásicas de Acción", "Las mejores series internacionales dobladas al español.", "Series"),
        ("12:00", "14:00", "Global Noticias / Actualidad", "Información nacional e internacional y entretenimiento.", "Noticias"),
        ("14:00", "18:00", "Tardes de Cine Familiar", "Películas para disfrutar en familia por Global TV.", "Cine"),
        ("18:00", "21:00", "Series Estelares", "Aventura, ficción y entretenimiento continuo.", "Series"),
        ("21:00", "24:00", "Cine Estelar Global TV", "Grandes éxitos del cine en horario estelar.", "Cine"),
    ],
    "karibena": [
        ("00:00", "06:00", "Madrugada Cumbiambera", "La mejor cumbia peruana sin interrupciones en Karibeña TV.", "Musical"),
        ("06:00", "09:00", "Despierta con La Karibeña", "Música alegre y noticias matutinas para empezar el día.", "Musical"),
        ("09:00", "12:00", "El Súper Show de la Karibeña", "Entretenimiento, humor, concursos y los éxitos de la cumbia.", "Variedades"),
        ("12:00", "15:00", "Fiesta Karibeña de Mediodía", "Videoclips y conciertos de las mejores orquestas del Perú.", "Musical"),
        ("15:00", "18:00", "Tardes de Cumbia y Sabor", "Pedidos musicales y especiales de agrupaciones peruanas.", "Musical"),
        ("18:00", "21:00", "Habla Kausa en Karibeña", "Actualidad popular, música en vivo y diversión.", "Variedades"),
        ("21:00", "24:00", "Estelares de la Cumbia Peruana", "Grandes conciertos y éxitos bailables de la noche.", "Musical"),
    ],
    "cultura24": [
        ("00:00", "06:00", "Archivo Cultural del Perú", "Documentales sobre historia, arqueología y tradiciones peruanas.", "Cultural"),
        ("06:00", "09:00", "Perú Milenario", "Reportajes sobre las culturas preincas, el Tahuantinsuyo y patrimonio.", "Documental"),
        ("09:00", "12:00", "Agenda Cultural 24", "Exposiciones, teatro, literatura y eventos artísticos en el Perú.", "Cultural"),
        ("12:00", "15:00", "Sonidos y Danzas del Perú", "Música tradicional, folclore y expresiones artísticas regionales.", "Cultural"),
        ("15:00", "18:00", "Documentales de Biodiversidad", "Naturaleza, reservas nacionales y geografía peruana.", "Documental"),
        ("18:00", "21:00", "Conversatorios de Arte e Historia", "Entrevistas a historiadores, escritores y artistas nacionales.", "Cultural"),
        ("21:00", "24:00", "Cine Peruano e Iberoamericano", "Ciclo de cine cultural y cortometrajes premiados.", "Cine"),
    ],
    "ovacion": [
        ("00:00", "06:00", "Ovación Madrugada Deportiva", "Repetición de las mesas de debate y análisis del fútbol peruano.", "Deportes"),
        ("06:00", "09:00", "Ovación Primera Edición", "Todas las noticias deportivas del día en el Perú y el mundo.", "Deportes"),
        ("09:00", "12:00", "Negrini lo Sabe / Mañanas de Ovación", "Opinión, debate y actualidad del deporte nacional.", "Deportes"),
        ("12:00", "14:00", "La Hora de Lalo", "El clásico deportivo del mediodía con toda la información del fútbol.", "Deportes"),
        ("14:00", "17:00", "Sobremesa en Ovación", "Debate intenso sobre la Liga 1, Copa Libertadores y Selección Peruana.", "Deportes"),
        ("17:00", "20:00", "Ovación Edición Central", "Cobertura completa de entrenamientos, conferencias y partidos.", "Deportes"),
        ("20:00", "24:00", "Noche Deportiva en Ovación TV", "Resumen de la jornada deportiva y análisis táctico.", "Deportes"),
    ],
    "nativa": [
        ("00:00", "06:00", "Nativa Madrugada", "Repetición de programas periodísticos y transmisiones deportivas.", "Variedades"),
        ("06:00", "09:00", "Las Mañanas con Carlos Cornejo", "Noticias, entrevistas políticas y análisis de la realidad nacional.", "Noticias"),
        ("09:00", "12:00", "Conéctate con Mayra Alvarez", "Actualidad, entrevistas, cultura y temas ciudadanos.", "Magazine"),
        ("12:00", "15:00", "Pulso Informativo Mediodía", "Cobertura periodística desde Lima y las regiones del Perú.", "Noticias"),
        ("15:00", "18:00", "Nativa Deportes / Transmisiones", "Liga Femenina, Liga 2, Futsal Pro y polideportivo peruano.", "Deportes"),
        ("18:00", "21:00", "Al Vuelo / Edición Central", "Análisis político e investigación periodística en vivo.", "Noticias"),
        ("21:00", "24:00", "Mesa de Noche en Nativa", "Debate político y resumen de las noticias más importantes.", "Política"),
    ],
    "usmptv": [
        ("00:00", "06:00", "Franja Cultural Universitaria", "Documentales educativos, ciencia e historia del Perú.", "Educativo"),
        ("06:00", "09:00", "Aula Abierta USMP", "Programas educativos para escolares y universitarios.", "Educativo"),
        ("09:00", "12:00", "Historia y Patrimonio del Perú", "Especiales sobre historia republicana, virreinal y precolombina.", "Cultural"),
        ("12:00", "15:00", "Ciencia, Tecnología e Innovación", "Avances científicos, salud e investigación académica.", "Educativo"),
        ("15:00", "18:00", "Tiempo de Leer y Cultura", "Literatura peruana, arte y entrevistas académicas.", "Cultural"),
        ("18:00", "21:00", "Clases Magistrales USMPTV", "Conferencias y documentales de formación profesional.", "Educativo"),
        ("21:00", "24:00", "Especiales Culturales USMPTV", "Documentales de gastronomía, turismo e identidad peruana.", "Cultural"),
    ],
    "liga1": [
        ("00:00", "06:00", "Compactos Liga 1 Te Apuesto", "Repetición de los mejores partidos de la fecha del fútbol peruano.", "Deportes"),
        ("06:00", "09:00", "Goles y Resumen de la Fecha", "Todos los goles y mejores jugadas del campeonato nacional.", "Deportes"),
        ("09:00", "12:00", "Clásicos del Fútbol Peruano", "Partidos históricos de Universitario, Alianza Lima, Sporting Cristal y más.", "Deportes"),
        ("12:00", "15:00", "L1 Noticias - Mediodía", "Actualidad de los clubes peruanos, entrenamientos y conferencias.", "Deportes"),
        ("15:00", "18:00", "Transmisión / Repetición Liga 1", "Fútbol profesional peruano en alta definición.", "Deportes"),
        ("18:00", "21:00", "Debate Liga 1", "Análisis táctico, tabla de posiciones y previa de la jornada.", "Deportes"),
        ("21:00", "24:00", "Estelar Liga 1", "Repetición del partido destacado de la fecha.", "Deportes"),
    ],
    "liga1_max": [
        ("00:00", "06:00", "Maratón Liga 1 Max", "Repeticiones íntegras de los encuentros de la Liga 1 Te Apuesto.", "Deportes"),
        ("06:00", "09:00", "El Resumen de la Fecha L1 Max", "Goles, polémicas y figuras de la jornada del fútbol peruano.", "Deportes"),
        ("09:00", "12:00", "L1 Radio en Vivo", "Debate deportivo, información de los clubes y enlaces desde los entrenamientos.", "Deportes"),
        ("12:00", "14:30", "Previa y Actualidad Liga 1 Max", "Análisis previo y noticias de última hora de la Liga 1.", "Deportes"),
        ("14:30", "18:30", "Fútbol en Vivo / Partido Destacado Liga 1 Max", "Cobertura exclusiva del campeonato nacional de primera división.", "Deportes"),
        ("18:30", "21:00", "Post-Partido y Análisis L1 Max", "Declaraciones de los protagonistas, conferencias y análisis arbitral.", "Deportes"),
        ("21:00", "24:00", "Noche de Fútbol en Liga 1 Max", "Especiales y repetición de los duelos estelares de la fecha.", "Deportes"),
    ],
    "movistar_deportes": [
        ("00:00", "06:00", "Madrugada en Movistar Deportes", "Repetición de Al Ángulo y programas estelares del deporte peruano.", "Deportes"),
        ("06:00", "09:00", "Zona Mixta - Edición Mañana", "Resumen deportivo nacional e internacional.", "Deportes"),
        ("09:00", "12:00", "Vóley Peruano LNSV / Polideportivo", "Lo mejor de la Liga Nacional Superior de Voleibol y deporte peruano.", "Deportes"),
        ("12:00", "14:00", "Zona Mixta Mediodía", "Noticias en vivo de la Selección Peruana, fútbol y polideportivo.", "Deportes"),
        ("14:00", "18:00", "Especiales y Transmisiones Movistar Deportes", "Partidos clásicos, vóley nacional y eventos deportivos.", "Deportes"),
        ("18:00", "20:00", "El Vuelco / Previa Deportiva", "Debate, entrevistas y actualidad del deporte nacional.", "Deportes"),
        ("20:00", "22:00", "Después de Todo", "Análisis periodístico de la jornada deportiva con Horacio Zimmermann y equipo.", "Deportes"),
        ("22:00", "24:00", "Al Ángulo", "El programa estelar de debate y análisis del fútbol peruano.", "Deportes"),
    ],
    "sol_tv": [
        ("00:00", "06:00", "Sol TV Noticias - Edición Nocturna", "Resumen informativo del norte peruano y programación musical.", "Regional"),
        ("06:00", "09:00", "Sol TV Noticias - Edición de la Mañana", "Información en vivo desde Trujillo, La Libertad y todo el norte del Perú.", "Noticias"),
        ("09:00", "12:00", "Magazine Matutino del Norte", "Entrevistas, servicios a la comunidad, salud y cultura norteña.", "Magazine"),
        ("12:00", "14:30", "Sol TV Noticias - Edición Mediodía", "Cobertura regional desde Trujillo, Chiclayo, Piura y Cajamarca.", "Noticias"),
        ("14:30", "18:00", "Tardes de Entretenimiento en Sol TV", "Variedades, música, cultura y reportajes regionales.", "Variedades"),
        ("18:00", "20:00", "Línea Directa / Debate Regional", "Análisis de la problemática local y entrevistas a autoridades.", "Política"),
        ("20:00", "22:30", "Sol TV Noticias - Edición Central", "El noticiero central del norte del Perú.", "Noticias"),
        ("22:30", "24:00", "Deportes y Cierre Informativo Sol TV", "Actualidad deportiva regional y resumen del día.", "Deportes"),
    ],
    "musical_variedades": [
        ("00:00", "06:00", "Trasnoche Musical y Variedades", "Selección continua de éxitos musicales y videoclips.", "Musical"),
        ("06:00", "09:00", "Mañanas Musicales", "Energía, música variada y actualidad para iniciar el día.", "Musical"),
        ("09:00", "12:00", "Magazine de la Mañana", "Entretenimiento, notas curiosas, música y participación.", "Variedades"),
        ("12:00", "15:00", "Especial de Mediodía", "Los mejores éxitos latinos, cumbia, salsa y pop.", "Musical"),
        ("15:00", "18:00", "Tardes de Entretenimiento", "Programación variada, rankings musicales y espectáculos.", "Entretenimiento"),
        ("18:00", "21:00", "Hora Estelar de Variedades", "Lo más pedido del día, entrevistas y diversión familiar.", "Variedades"),
        ("21:00", "24:00", "Noches de Concierto y Éxitos", "Especiales musicales y entretenimiento nocturno.", "Musical"),
    ],
    "regional": [
        ("00:00", "06:00", "Programación Continua / Resumen Regional", "Repetición de noticieros y especiales culturales de la región.", "Regional"),
        ("06:00", "09:00", "Noticiero Matinal Regional", "Las principales noticias locales, enlaces en vivo y servicio a la comunidad.", "Noticias"),
        ("09:00", "12:00", "Magazine Familiar de la Mañana", "Entrevistas, gastronomía local, salud, cultura y emprendimiento.", "Magazine"),
        ("12:00", "14:00", "Informativo del Mediodía", "Cobertura periodística regional y nacional de primera mano.", "Noticias"),
        ("14:00", "16:00", "Música y Cultura Regional", "Folclore, música peruana y tradiciones de nuestra tierra.", "Cultural"),
        ("16:00", "18:00", "Tardes de Variedades y Entretenimiento", "Espacio juvenil, cine familiar y reportajes locales.", "Variedades"),
        ("18:00", "20:00", "Debate y Actualidad Local", "Análisis de los temas más importantes de la región con invitados.", "Política"),
        ("20:00", "22:00", "Noticiero Edición Central", "Resumen completo de las noticias del día en la región y el Perú.", "Noticias"),
        ("22:00", "24:00", "Especial Nocturno / Deportes Regionales", "Deporte local, entrevistas y cierre informativo.", "Deportes"),
    ],
}


def clean_html_text(text):
    if not text:
        return ""
    text = re.sub(r"<[^>]+>", "", text)
    text = unescape(text)
    return re.sub(r"\s+", " ", text).strip()


def fetch_url(url, timeout=12):
    req = urllib.request.Request(
        url,
        headers={
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
            "Accept-Language": "es-PE,es;q=0.9",
        },
    )
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        return resp.read().decode("utf-8", errors="replace")


def scrape_mitv_channel(slug, base_date):
    """
    Extrae la programación real de mi.tv/pe para ayer, hoy y mañana.
    Retorna lista de dicts: [{'start': datetime, 'stop': datetime, 'title': str, 'desc': str, 'category': str}]
    """
    day_configs = [
        ("ayer", base_date - timedelta(days=1)),
        ("", base_date),
        ("manana", base_date + timedelta(days=1)),
    ]

    raw_items = []
    for day_slug, day_dt in day_configs:
        if day_slug:
            url = f"https://mi.tv/pe/async/channel/{slug}/{day_slug}/-300"
        else:
            url = f"https://mi.tv/pe/async/channel/{slug}/-300"

        try:
            html = fetch_url(url)
        except Exception as e:
            print(f"  [!] Aviso mi.tv ({slug} - {day_slug or 'hoy'}): {e}")
            continue

        # Extraer cada bloque <li ...> dentro de <ul class="broadcasts ...">
        li_blocks = re.findall(r"<li[^>]*>(.*?)</li>", html, re.DOTALL)
        current_day_date = day_dt.date()
        last_hour = -1

        for block in li_blocks:
            time_m = re.search(r'<span class="time">\s*(\d{1,2}):(\d{2})\s*</span>', block)
            title_m = re.search(r"<h2>(.*?)</h2>", block, re.DOTALL)
            if not time_m or not title_m:
                continue

            hh = int(time_m.group(1))
            mm = int(time_m.group(2))
            title = clean_html_text(title_m.group(1))

            sub_m = re.search(r'<span class="sub-title">(.*?)</span>', block, re.DOTALL)
            cat = clean_html_text(sub_m.group(1)) if sub_m else "Entretenimiento"

            syn_m = re.search(r'<p class="synopsis">(.*?)</p>', block, re.DOTALL)
            desc = clean_html_text(syn_m.group(1)) if syn_m else f"Transmisión de {title}."

            # En mi.tv la guía de un día empieza ~05:00 AM y si pasa de las 00:00 corresponde a la madrugada siguiente
            if last_hour >= 18 and hh < 6:
                current_day_date = current_day_date + timedelta(days=1)
            last_hour = hh

            start_dt = datetime(
                current_day_date.year,
                current_day_date.month,
                current_day_date.day,
                hh,
                mm,
                0,
            )
            raw_items.append(
                {
                    "start": start_dt,
                    "title": title,
                    "desc": desc,
                    "category": cat,
                }
            )

    if not raw_items:
        return []

    # Ordenar por fecha/hora de inicio y eliminar duplicados del mismo minuto
    raw_items.sort(key=lambda x: x["start"])
    dedup = []
    for item in raw_items:
        if dedup and dedup[-1]["start"] == item["start"]:
            continue
        dedup.append(item)

    # Calcular hora de fin en base al siguiente programa
    programs = []
    for i, item in enumerate(dedup):
        start_dt = item["start"]
        if i + 1 < len(dedup):
            stop_dt = dedup[i + 1]["start"]
            # Si hay un salto exagerado (>6 horas), limitar a 2 horas
            if (stop_dt - start_dt) > timedelta(hours=6):
                stop_dt = start_dt + timedelta(hours=2)
        else:
            stop_dt = start_dt + timedelta(hours=2)

        if stop_dt > start_dt:
            programs.append(
                {
                    "start": start_dt,
                    "stop": stop_dt,
                    "title": item["title"],
                    "desc": item["desc"],
                    "category": item["category"],
                }
            )

    return programs


def scrape_gatotv_channel(slug, base_date):
    """
    Extrae la programación real desde gatotv.com/canal/<slug> y la proyecta para ayer, hoy y mañana.
    """
    url = f"https://www.gatotv.com/canal/{slug}"
    try:
        html = fetch_url(url)
    except Exception as e:
        print(f"  [!] Aviso GatoTV ({slug}): {e}")
        return []

    rows = re.findall(
        r'<tr class="tbl_EPG_row[^"]*">(.*?)</tr>', html, re.DOTALL
    )
    daily_slots = []
    for row in rows:
        times = re.findall(r'<time datetime="(\d{2}:\d{2})">', row)
        title_m = re.search(
            r'<div class="div_program_title_on_channel">\s*<span[^>]*>(.*?)</span>',
            row,
            re.DOTALL,
        )
        if not title_m:
            title_m = re.search(
                r'<div class="div_program_title_on_channel">.*?<span>(.*?)</span>',
                row,
                re.DOTALL,
            )
        if len(times) >= 2 and title_m:
            t_start, t_end = times[0], times[1]
            title = clean_html_text(title_m.group(1))
            daily_slots.append((t_start, t_end, title))

    if not daily_slots:
        return []

    programs = []
    for day_offset in (-1, 0, 1):
        d = (base_date + timedelta(days=day_offset)).date()
        for t_start, t_end, title in daily_slots:
            sh, sm = map(int, t_start.split(":"))
            eh, em = map(int, t_end.split(":"))
            start_dt = datetime(d.year, d.month, d.day, sh, sm, 0)
            if (eh, em) <= (sh, sm):
                stop_dt = datetime(d.year, d.month, d.day, eh, em, 0) + timedelta(days=1)
            else:
                stop_dt = datetime(d.year, d.month, d.day, eh, em, 0)

            programs.append(
                {
                    "start": start_dt,
                    "stop": stop_dt,
                    "title": title,
                    "desc": f"Programación de {title} por Perú Mágico.",
                    "category": "Variedades",
                }
            )

    return programs


def generate_template_programs(ch_conf, base_date):
    """
    Genera la parrilla de programación para ayer, hoy, mañana y pasado mañana
    para canales de noticias, deportes o regionales.
    """
    t_key = ch_conf.get("template_key", "regional")
    slots = TEMPLATES.get(t_key, TEMPLATES["regional"])
    ch_name = ch_conf["name"]
    region = ch_conf.get("region", "Perú")

    programs = []
    for day_offset in (-1, 0, 1, 2):
        d = (base_date + timedelta(days=day_offset)).date()
        for start_str, end_str, title_tpl, desc_tpl, cat in slots:
            sh, sm = map(int, start_str.split(":"))
            start_dt = datetime(d.year, d.month, d.day, sh, sm, 0)
            if end_str == "24:00":
                stop_dt = datetime(d.year, d.month, d.day, 0, 0, 0) + timedelta(days=1)
            else:
                eh, em = map(int, end_str.split(":"))
                stop_dt = datetime(d.year, d.month, d.day, eh, em, 0)

            if t_key == "regional":
                title = f"{title_tpl} - {ch_name}"
                desc = f"{desc_tpl} Señal en vivo de {ch_name} ({region})."
            else:
                title = title_tpl
                desc = desc_tpl

            programs.append(
                {
                    "start": start_dt,
                    "stop": stop_dt,
                    "title": title,
                    "desc": desc,
                    "category": cat,
                }
            )
    return programs


def format_xmltv_time(dt):
    return dt.strftime(f"%Y%m%d%H%M%S {TIMEZONE_OFFSET}")


def main():
    peru_tz = timezone(timedelta(hours=-5))
    now = datetime.now(peru_tz).replace(tzinfo=None)
    print(f"=== Generador EPG Perú (XUI.one) - Fecha base (Perú): {now.strftime('%Y-%m-%d %H:%M')} ===")

    tv = ET.Element(
        "tv",
        {
            "source-info-name": "EPG Peru AkyHay",
            "generator-info-name": "EPG_Peru_XUI_Generator",
        },
    )

    all_programs = []
    total_channels = 0

    for ch in CHANNELS_CONFIG:
        ch_id = ch["id"]
        ch_name = ch["name"]
        streams = ch["streams"]
        icon = ch.get("icon", "")

        # 1. Agregar canal principal con prefijo PERU ®| para que el Auto-Assign de XC_VM haga match al 100%
        ch_elem = ET.SubElement(tv, "channel", {"id": ch_id})
        dn_main = ET.SubElement(ch_elem, "display-name", {"lang": "es"})
        dn_main.text = f"PERU ®| {ch_name}"

        # Agregar también los nombres exactos de los streams en XUI.one / XC_VM
        for st_name in streams:
            dn_st = ET.SubElement(ch_elem, "display-name", {"lang": "es"})
            dn_st.text = st_name

        if icon:
            ET.SubElement(ch_elem, "icon", {"src": icon})

        total_channels += 1

        # 2. Obtener programación
        source = ch.get("source")
        progs = []
        if source == "mitv":
            print(f"[*] Extrayendo guía en vivo de mi.tv para: {ch_name} ({ch['slug']})...")
            progs = scrape_mitv_channel(ch["slug"], now)
        elif source == "gatotv":
            print(f"[*] Extrayendo guía en vivo de GatoTV para: {ch_name} ({ch['slug']})...")
            progs = scrape_gatotv_channel(ch["slug"], now)

        if not progs:
            if source in ("mitv", "gatotv"):
                print(f"    -> Usando parrilla de respaldo para {ch_name}")
            else:
                print(f"[*] Generando parrilla programada para: {ch_name} ({len(streams)} stream/s)...")
            progs = generate_template_programs(ch, now)

        for p in progs:
            all_programs.append((ch_id, p))

    # Agregar todos los bloques <programme> al XML
    for ch_id, p in all_programs:
        prog_elem = ET.SubElement(
            tv,
            "programme",
            {
                "start": format_xmltv_time(p["start"]),
                "stop": format_xmltv_time(p["stop"]),
                "channel": ch_id,
            },
        )
        t_el = ET.SubElement(prog_elem, "title", {"lang": "es"})
        t_el.text = p["title"]

        d_el = ET.SubElement(prog_elem, "desc", {"lang": "es"})
        d_el.text = p["desc"]

        c_el = ET.SubElement(prog_elem, "category", {"lang": "es"})
        c_el.text = p.get("category", "General")

    tree = ET.ElementTree(tv)
    if hasattr(ET, "indent"):
        ET.indent(tree, space="  ", level=0)

    tree.write(OUTPUT_XML, encoding="utf-8", xml_declaration=True)
    shutil.copyfile(OUTPUT_XML, OUTPUT_DEFAULT)

    with open(OUTPUT_XML, "rb") as f_in:
        with gzip.open(OUTPUT_GZ, "wb") as f_out:
            shutil.copyfileobj(f_in, f_out)

    print("\n========================================================")
    print(f"¡EPG Peruano generado con éxito!")
    print(f" - Canales únicos configurados : {total_channels} (cubriendo tus 50 streams SD/HD)")
    print(f" - Programas totales generados : {len(all_programs)}")
    print(f" - Archivo XML                 : {OUTPUT_XML} (y {OUTPUT_DEFAULT})")
    print(f" - Archivo comprimido GZ       : {OUTPUT_GZ}")
    print("========================================================")


if __name__ == "__main__":
    main()
