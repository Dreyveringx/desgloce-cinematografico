import re
from dataclasses import dataclass, field
from typing import Optional

# Regex para cabeceras de escena (formato Hollywood estándar)
SCENE_HEADER_RE = re.compile(
    r'^[ \t]*(\d+[A-Z]?)[ \t]+(EXT|INT|INSERT)\.[ \t]+(.+?)[ \t]*[-\u2013][ \t]*'
    r'(NOCHE|D\u00cdA|DIA|CONTINUO|AMANECER|ATARDECER|MA\u00d1ANA|TARDE|MADRUGADA|M\u00c1S TARDE|MAS TARDE)',
    re.IGNORECASE | re.MULTILINE
)

DIALOGUE_NAME_RE = re.compile(
    r'^\s{18,38}([A-Z\u00c1\u00c9\u00cd\u00d3\u00da\u00d1][A-Z\u00c1\u00c9\u00cd\u00d3\u00da\u00d1\s\.]{1,28})'
    r'(\s*\([^)]*\))?\s*$',
    re.MULTILINE
)

EXCLUDE_WORDS = {
    'CORTE A', 'FADE OUT', 'FADE IN', 'SMASH CUT', 'CORTE', 'INSERT',
    'CONTINUA', 'CONTINUACION', 'FIN', 'APOLOS', 'SOBRE NEGRO',
    'TEXTO EN PANTALLA', 'CREDITOS EN PANTALLA', 'CLIP', 'V.O', 'O.S',
    'V.O.', 'O.S.', 'POLISH', 'ABRIL', 'ENERO', 'FEBRERO', 'MARZO',
    'MAYO', 'JUNIO', 'JULIO', 'AGOSTO', 'SEPTIEMBRE', 'OCTUBRE',
    'NOVIEMBRE', 'DICIEMBRE', 'MAS TARDE', 'MÁS TARDE', 'TIEMPO DESPUES'
}

EXTRAS_KEYWORDS = {
    'MUJERES', 'HOMBRES', 'CLIENTES', 'CLIENTAS', 'EXTRAS', 'MATONES',
    'TRANSEUNTES', 'GENTE', 'PERSONAS', 'TIPOS', 'TRABAJADORES',
    'MESEROS', 'GUARDIAS', 'POLICIAS', 'POLICIA', 'INVITADOS',
    'ASISTENTES', 'EMPLEADOS', 'CHICAS', 'CHICOS', 'SEÑORAS', 'SEÑORES',
    'NIÑOS', 'JOVENES', 'HOMBRE', 'MUJER', 'CLIENTE', 'EXTRA',
    'AMIGOS', 'AMIGAS', 'PAREJAS', 'SEGURIDAD'
}


@dataclass
class Escena:
    numero: str
    capitulo: int
    locacion: str
    es_exterior: bool
    es_interior: bool
    es_dia: bool
    es_noche: bool
    es_continuo: bool
    momento_raw: str
    personajes: list = field(default_factory=list)
    extras: list = field(default_factory=list)
    acotacion: str = ""
    dia_rodaje: str = "DIA 1"
    kbio: int = 1
    continuidad: str = ""


@dataclass
class FilaDesglose:
    kbio: Optional[int]
    capitulo: int
    escena: str
    locacion: str
    ext: bool
    int_: bool
    dia: bool
    noche: bool
    observacion: str
    continuidad: str = ""


def parse_scenes(text: str) -> list:
    """Parsea el texto del guion y retorna lista de Escena."""
    lines = text.split('\n')
    escenas = []
    i = 0

    while i < len(lines):
        line = lines[i]
        match = SCENE_HEADER_RE.match(line)
        if match:
            numero = match.group(1).strip()
            tipo = match.group(2).upper()
            locacion = match.group(3).strip()
            momento = match.group(4).strip().upper()

            if tipo == 'INSERT':
                if 'EXT' in locacion.upper():
                    es_ext = True
                    es_int = False
                else:
                    es_ext = False
                    es_int = True
            else:
                es_ext = (tipo == 'EXT')
                es_int = (tipo == 'INT')

            momento_norm = momento.replace('Á', 'A').replace('É', 'E').replace('Í', 'I').replace('Ó', 'O').replace('Ú', 'U')
            es_dia = momento_norm in ('DIA', 'DÍA', 'AMANECER', 'MANANA', 'MAÑANA', 'ATARDECER', 'TARDE', 'MAS TARDE')
            es_noche = momento_norm in ('NOCHE', 'MADRUGADA')
            es_continuo = momento_norm == 'CONTINUO'

            acotacion_lines = []
            i += 1
            while i < len(lines):
                next_line = lines[i]
                if SCENE_HEADER_RE.match(next_line):
                    break
                stripped = next_line.strip()
                if not stripped:
                    i += 1
                    continue
                if re.match(r'^APOLOS\s+\d+\s*$', stripped, re.IGNORECASE):
                    i += 1
                    continue
                if re.match(r'^APOLOS\s*$', stripped, re.IGNORECASE):
                    i += 1
                    continue
                acotacion_lines.append(stripped)
                i += 1

            acotacion = ' '.join(acotacion_lines)

            esc = Escena(
                numero=numero,
                capitulo=1,
                locacion=locacion,
                es_exterior=es_ext,
                es_interior=es_int,
                es_dia=es_dia,
                es_noche=es_noche,
                es_continuo=es_continuo,
                momento_raw=momento,
                acotacion=acotacion,
            )
            escenas.append(esc)
        else:
            i += 1

    return escenas


def _assign_characters_from_scene_blocks(text: str, escenas: list, personajes_principales: list, personajes_extras: list) -> None:
    """Asigna personajes escaneando el bloque completo de cada escena en el guion."""
    lines = text.split('\n')
    header_rows = []
    for i, line in enumerate(lines):
        if SCENE_HEADER_RE.match(line):
            header_rows.append(i)

    for idx, esc in enumerate(escenas):
        if idx >= len(header_rows):
            break
        start = header_rows[idx] + 1
        end = header_rows[idx + 1] if idx + 1 < len(header_rows) else len(lines)
        block = '\n'.join(lines[start:end])
        for char in personajes_principales:
            if re.search(rf'\b{re.escape(char)}\b', block, re.IGNORECASE):
                if char not in esc.personajes:
                    esc.personajes.append(char)
        for extra in personajes_extras:
            if re.search(rf'\b{re.escape(extra)}\b', block, re.IGNORECASE):
                if extra not in esc.extras:
                    esc.extras.append(extra)
        if block.strip() and len(block) > len(esc.acotacion):
            block_clean = re.sub(r'\bAPOLOS\s+\d+\b', '', block, flags=re.IGNORECASE)
            block_clean = re.sub(r'\s+', ' ', block_clean).strip()
            esc.acotacion = block_clean


def detect_characters(text: str, escenas: list) -> tuple:
    """Detecta personajes y extras. Retorna (personajes_principales, extras)."""
    name_count = {}
    for match in DIALOGUE_NAME_RE.finditer(text):
        name = match.group(1).strip()
        name = re.sub(r'\s*\(.*?\)\s*$', '', name).strip()
        if not name or len(name) < 2:
            continue
        if any(excl in name.upper() for excl in EXCLUDE_WORDS):
            continue
        if re.match(r'^[\d\s\*\-\.]+$', name):
            continue
        name_count[name] = name_count.get(name, 0) + 1

    personajes_principales = []
    personajes_extras = []

    for name, count in sorted(name_count.items(), key=lambda x: -x[1]):
        name_upper = name.upper().strip()
        is_extra = any(kw in name_upper for kw in EXTRAS_KEYWORDS)
        if is_extra:
            personajes_extras.append(name)
        elif count >= 2:
            personajes_principales.append(name)
        else:
            personajes_extras.append(name)

    _assign_characters_from_scene_blocks(text, escenas, personajes_principales, personajes_extras)

    return personajes_principales, personajes_extras


def assign_shooting_days(escenas: list) -> list:
    """Asigna 'dia_rodaje' a cada escena."""
    if not escenas:
        return escenas

    dia_num = 1
    dia_especial_num = 1
    prev_moment = None
    special_day_keywords = re.compile(
        r'(han\s+pasado|paso\s+de\s+tiempo|semanas?\s+despu[eé]s|'
        r'meses?\s+despu[eé]s|a[ñn]os?\s+despu[eé]s|tiempo\s+despu[eé]s|'
        r'al\s+d[ií]a\s+siguiente|flashback|tiempo\s+atr[aá]s)',
        re.IGNORECASE
    )

    for esc in escenas:
        acotacion_lower = esc.acotacion.lower()
        momento = esc.momento_raw.upper().replace('Á', 'A').replace('É', 'E').replace('Í', 'I').replace('Ó', 'O').replace('Ú', 'U')

        if special_day_keywords.search(acotacion_lower):
            dia_especial_num += 1
            esc.dia_rodaje = f"DIA X{dia_especial_num} PASO DEL TIEMPO"
            prev_moment = momento
            continue

        if momento == 'CONTINUO':
            esc.dia_rodaje = f"DIA {dia_num}"
            continue

        if prev_moment and prev_moment in ('NOCHE', 'MADRUGADA') and momento in ('DIA', 'MANANA', 'MAÑANA', 'AMANECER'):
            dia_num += 1

        esc.dia_rodaje = f"DIA {dia_num}"
        prev_moment = momento

    return escenas


def calculate_kbio(escenas: list, personajes: list) -> None:
    """Calcula el KBIO (cambio de vestuario) por personaje por día."""
    costume_change_re = re.compile(
        r'(vestido\s+de|uniforme\s+de|ropa\s+interior|traje\s+de|pijama|'
        r'ba[ñn]ador|K\d+\b|disfraz\s+de|casco)',
        re.IGNORECASE
    )

    for personaje in personajes:
        kbio_por_dia = {}
        for esc in escenas:
            if personaje not in esc.personajes:
                continue
            dia = esc.dia_rodaje
            if dia not in kbio_por_dia:
                kbio_por_dia[dia] = 1
            else:
                if costume_change_re.search(esc.acotacion):
                    kbio_por_dia[dia] += 1
            esc.kbio = kbio_por_dia[dia]


# Patrones de vestuario a detectar en el texto
VESTUARIO_PATTERNS = [
    (re.compile(r'viste\s+de\s+([a-záéíóúñ\s]+)', re.I), 'DISFRAZ {}'),
    (re.compile(r'vestido[s]?\s+de\s+([a-záéíóúñ\s]+)', re.I), 'DISFRAZ {}'),
    (re.compile(r'vestida\s+en\s+([a-záéíóúñ\s]+)', re.I), 'VISTE {}'),
    (re.compile(r'uniforme\s+de\s+([a-záéíóúñ\s]+)', re.I), 'UNIFORME {}'),
    (re.compile(r'traje\s+de\s+([a-záéíóúñ\s]+)', re.I), 'TRAJE {}'),
    (re.compile(r'vestidos?\s+de\s+polic', re.I), 'DISFRAZ POLICÍA'),
    (re.compile(r'\ben\s+b[oó]xers?\b.{0,40}billete', re.I), 'BÓXER CON BILLETES'),
    (re.compile(r'\ben\s+b[oó]xers?\b', re.I), 'BÓXER'),
    (re.compile(r'\ben\s+pijama\b', re.I), 'PIJAMA'),
    (re.compile(r'\bpijama\b', re.I), 'PIJAMA'),
    (re.compile(r'\bsudadera\b', re.I), 'SUDADERA'),
    (re.compile(r'boxer[s]?\b', re.I), 'BÓXER'),
    (re.compile(r'sin\s+camisa', re.I), 'SIN CAMISA'),
    (re.compile(r'se\s+abre?\s+la\s+camisa', re.I), 'TORSO DESNUDO'),
    (re.compile(r'se\s+quita\s+la\s+camisa', re.I), 'TORSO DESNUDO'),
    (re.compile(r'torso\s+desnudo', re.I), 'TORSO DESNUDO'),
    (re.compile(r'ropa\s+interior', re.I), 'ROPA INTERIOR'),
    (re.compile(r'ba[ñn]ador', re.I), 'BAÑADOR'),
    (re.compile(r'disfraz\b', re.I), 'DISFRAZ'),
    (re.compile(r'chaleco', re.I), 'CHALECO'),
    (re.compile(r'chaqueta', re.I), 'CHAQUETA'),
    (re.compile(r'casco\b', re.I), 'CASCO MOTO'),
    (re.compile(r'gorra\b', re.I), 'GORRA'),
    (re.compile(r'esposas\b', re.I), 'ESPOSAS'),
    (re.compile(r'rodillera', re.I), 'RODILLERA'),
]

PROPS_PATTERNS = [
    (re.compile(r'meg[aá]fono', re.I), 'megáfono'),
    (re.compile(r'micr[oó]fono', re.I), 'micrófono'),
    (re.compile(r'jeringa', re.I), 'jeringa'),
    (re.compile(r'sobre\b.{0,30}billete', re.I), 'sobre con billetes'),
    (re.compile(r'\bbillete', re.I), 'billetes'),
    (re.compile(r'copa\b.{0,20}aguardiente|aguardiente', re.I), 'copa aguardiente'),
    (re.compile(r'vaso[s]?\b', re.I), 'vasos'),
    (re.compile(r'arma\b', re.I), 'arma'),
    (re.compile(r'pistola\b', re.I), 'pistola'),
    (re.compile(r'celular\b', re.I), 'celular'),
    (re.compile(r'documento', re.I), 'documento'),
    (re.compile(r'anillo\b', re.I), 'anillo'),
    (re.compile(r'maletín\b|maleta\b', re.I), 'maletín'),
    (re.compile(r'rodillera', re.I), 'rodillera bajo pantalón'),
    (re.compile(r'cuchillo\b', re.I), 'cuchillo'),
    (re.compile(r'botella\b', re.I), 'botella'),
]

ACCIONES_PATTERNS = [
    (re.compile(r'cojea|cojeando', re.I), 'COJEA'),
    (re.compile(r'baila|bailando', re.I), 'BAILA'),
    (re.compile(r'llora|llorando', re.I), 'LLORA'),
    (re.compile(r'golpea|golpe', re.I), 'GOLPEA'),
    (re.compile(r'abraza|abrazo', re.I), 'ABRAZA'),
    (re.compile(r'besa|besando', re.I), 'BESA'),
    (re.compile(r'desnudo|desnuda', re.I), 'DESNUDO'),
    (re.compile(r'sangra|sangrando|sangre', re.I), 'SANGRA'),
    (re.compile(r'golpeado|herido|lastimado', re.I), 'HERIDO'),
    (re.compile(r'\bcae\b|cayendo\b', re.I), 'CAE'),
    (re.compile(r'dispara|disparo', re.I), 'DISPARA'),
    (re.compile(r'\bcorre\b|corriendo\b', re.I), 'CORRE'),
    (re.compile(r'duerme|durmiendo', re.I), 'DUERME'),
    (re.compile(r'fuma|fumando', re.I), 'FUMA'),
    (re.compile(r'toma\b.{0,15}trago|bebe\b', re.I), 'BEBE'),
    (re.compile(r'se\s+abre?\s+la\s+camisa', re.I), 'TORSO DESNUDO'),
    (re.compile(r'aprieta\s+los\s+dientes', re.I), 'APRIETA LOS DIENTES'),
    (re.compile(r'se\s+toca\s+la\s+rodilla', re.I), 'SE TOCA LA RODILLA'),
    (re.compile(r'susurra.{0,20}o[ií]do', re.I), 'SUSURRA AL OÍDO'),
]


def _is_dialogue_or_cast(sentence: str, char_name: str) -> bool:
    """Filtra listas de elenco y líneas de diálogo del personaje."""
    s = sentence.strip()
    if re.match(r'^Son\s+', s, re.IGNORECASE):
        return True
    if re.match(r'^[A-ZÁÉÍÓÚÑ][A-ZÁÉÍÓÚÑ\s]{1,28}$', s):
        return True
    m = re.match(rf'^{re.escape(char_name)}\s+(.+)$', s, re.IGNORECASE)
    if not m:
        return False
    rest = m.group(1).strip()
    if re.match(
        r'^(Nos|Les|No\s+me|Lo\s+siento|Ay,|Si\s|Sí\s|Ya\s|Que\s|Curado|Después|Aguanta|Sin\s+salvo)',
        rest,
        re.IGNORECASE,
    ):
        return True
    letters = [c for c in rest if c.isalpha()]
    if letters and len(rest) < 1500:
        upper_ratio = sum(c.isupper() for c in letters) / len(letters)
        if upper_ratio > 0.72:
            return True
    return False


def _sentence_mentions_char(sentence: str, char_name: str) -> bool:
    if re.search(rf'\b{re.escape(char_name)}\b', sentence, re.IGNORECASE):
        return True
    if re.search(rf'\bde\s+{re.escape(char_name)}\b', sentence, re.IGNORECASE):
        return True
    if re.search(rf'\bdel\s+{re.escape(char_name)}\b', sentence, re.IGNORECASE):
        return True
    return False


def _extract_costume_context(text: str) -> str:
    """Frase breve de contexto (estilo Excel manual), no etiquetas."""
    context_patterns = [
        r'(?:cuatro|tres|varios)\s+hombres?\s+fornidos\s+vestidos?\s+de\s+polic\w+',
        r'(?:cuatro|tres|varios)\s+hombres?\s+vestidos?\s+de\s+polic\w+',
        r'hombres?\s+fornidos\s+vestidos?\s+de\s+polic\w+',
        r'uniformes?\s+de\s+param[eé]dic\w+',
        r'vestidos?\s+de\s+oficial(?:es)?\s+de\s+la\s+marina',
        r'vestidos?\s+de\s+cura',
        r'en\s+pijama',
        r'con\s+sudadera',
        r'bata\s+de\s+paciente',
    ]
    for pat in context_patterns:
        m = re.search(pat, text, re.IGNORECASE)
        if m:
            phrase = re.sub(r'\s+', ' ', m.group(0)).strip()
            if len(phrase) > 12:
                return phrase[0].upper() + phrase[1:]
    props_snippet = re.search(
        r'gorras?,?\s+chalecos?,?\s+esposas?,?\s+bolillos?',
        text,
        re.IGNORECASE,
    )
    if props_snippet:
        return props_snippet.group(0)
    return ''


def _is_set_dressing_for_char(sentence: str, char_name: str, full_text: str) -> bool:
    """Acotación de lugar/vestuario aunque no nombre al personaje en esa frase."""
    if not re.search(rf'\b{re.escape(char_name)}\b', full_text, re.IGNORECASE):
        return False
    if re.search(rf'\bropa\s+de\s+{re.escape(char_name)}\b', sentence, re.IGNORECASE):
        return True
    if re.search(
        r'\b(penthouse|apartamento|yacen sobre la cama|botas de cuero|desperdigada)\b',
        sentence,
        re.IGNORECASE,
    ):
        return True
    return False


def extract_character_observation(char_name: str, escena_text: str, all_char_names: list) -> str:
    """
    Observación estilo desglose manual: prosa breve del guion (sin etiquetas ·).
    Típico: 80–350 caracteres, como el Excel de referencia Apolos.
    """
    MAX_LEN = 300
    char_upper = char_name.upper()
    text = escena_text or ""
    text = re.sub(r'\bAPOLOS\s+\d+\b', '', text)
    text = re.sub(r'\s{3,}', ' ', text)

    age_re = re.compile(rf'\b{re.escape(char_name)}\b\s*\((\d{{1,2}})\)', re.IGNORECASE)
    age_match = age_re.search(text)
    if age_match:
        opener = f'{char_upper} ({age_match.group(1)} AÑOS)'
    else:
        opener = char_upper

    context = _extract_costume_context(text)
    if context and context.lower() not in opener.lower():
        opener = f'{opener}, {context}'

    max_frases = 2 if len(opener) < 20 and ',' not in opener else 3

    oraciones_raw = re.split(r'(?<=[.!?])\s+|\n{2,}', text)
    candidatas = []
    seen = set()
    for raw in oraciones_raw:
        frase = re.sub(r'\s+', ' ', raw).strip()
        if len(frase) < 15 or frase in seen:
            continue
        if re.match(r'^APOLOS\s*$', frase, re.IGNORECASE):
            continue
        relevante = _sentence_mentions_char(frase, char_name) or _is_set_dressing_for_char(
            frase, char_name, text
        )
        if not relevante:
            pos = text.lower().find(frase.lower())
            if pos > 0 and re.search(
                r'\b(toma un sobre|cuenta|se va|se pone|se quita|sostiene)\b', frase, re.IGNORECASE
            ):
                ventana = text[max(0, pos - 350):pos]
                if re.search(rf'\b{re.escape(char_name)}\b', ventana, re.IGNORECASE):
                    relevante = True
        if not relevante:
            continue
        if _is_dialogue_or_cast(frase, char_name):
            continue
        if re.match(r'^Un camerino\b', frase, re.IGNORECASE) and not re.search(
            rf'\b{re.escape(char_name)}\b', frase, re.IGNORECASE
        ):
            continue
        seen.add(frase)
        pos = text.lower().find(frase.lower())
        candidatas.append((pos if pos >= 0 else 99999, frase))

    candidatas.sort(key=lambda x: x[0])

    cuerpo = ''
    n_frases = 0
    for _, frase in candidatas:
        if n_frases >= max_frases:
            break
        sep = '. ' if cuerpo or not opener.endswith('.') else ' '
        if len(opener) + len(cuerpo) + len(sep) + len(frase) > MAX_LEN:
            if not cuerpo:
                espacio = MAX_LEN - len(opener) - len(sep) - 3
                if espacio > 35:
                    cuerpo += sep + frase[:espacio].rstrip() + '...'
                    n_frases += 1
            break
        cuerpo += sep + frase
        n_frases += 1

    resultado = (opener + cuerpo).strip()
    resultado = re.sub(r'\s+', ' ', resultado)
    resultado = re.sub(r'\.{2,}', '.', resultado)
    if len(resultado) > MAX_LEN:
        resultado = resultado[: MAX_LEN - 3].rstrip() + '...'
    return resultado
