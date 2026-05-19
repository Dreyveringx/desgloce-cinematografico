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
                leading_spaces = len(next_line) - len(next_line.lstrip())
                if stripped and leading_spaces < 30 and len(stripped) > 2:
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
                acotacion=acotacion[:1500],
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
            esc.acotacion = re.sub(r'\s+', ' ', block).strip()[:1500]


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


def extract_character_observation(char_name: str, escena_text: str, all_char_names: list) -> str:
    """
    Genera la observación específica para UN personaje en UNA escena.
    Extrae vestuario, props, acciones y relaciones relevantes para producción.
    """
    char_upper = char_name.upper()
    text = escena_text or ""
    parts = []

    age_pattern = re.compile(
        rf'\b{re.escape(char_name)}\b\s*\((\d{{1,2}}(?:s|\s*años|\s*AÑOS)?)\)',
        re.IGNORECASE
    )
    age_match = age_pattern.search(text)
    if age_match:
        age = age_match.group(1).replace('s', ' años').strip()
        if age.isdigit():
            age = f'{age} años'
        parts.append(f'{char_upper} ({age})')
    else:
        parts.append(char_upper)

    char_mentions = [
        m.start() for m in re.finditer(rf'\b{re.escape(char_name)}\b', text, re.IGNORECASE)
    ]

    vestuario_found = []
    for pattern, label in VESTUARIO_PATTERNS:
        match = pattern.search(text)
        if match:
            match_pos = match.start()
            cerca_del_personaje = (
                any(abs(match_pos - cp) < 400 for cp in char_mentions)
                if char_mentions else True
            )
            if cerca_del_personaje or not char_mentions:
                if isinstance(label, str) and '{}' in label:
                    captured = match.group(1)[:20].strip().upper()
                    item = label.format(captured)
                else:
                    item = label
                if item not in vestuario_found:
                    vestuario_found.append(item)

    if vestuario_found:
        police = [v for v in vestuario_found if 'POLIC' in v]
        if len(police) > 1:
            vestuario_found = [v for v in vestuario_found if 'POLIC' not in v]
            vestuario_found.insert(0, 'DISFRAZ POLICÍA')
        seen = set()
        deduped = []
        for v in vestuario_found:
            key = v[:12]
            if key in seen:
                continue
            seen.add(key)
            deduped.append(v)
        vestuario_found = deduped

    if vestuario_found:
        has_sudadera = 'SUDADERA' in vestuario_found
        has_sin_camisa = 'SIN CAMISA' in vestuario_found or 'TORSO DESNUDO' in vestuario_found
        if has_sudadera and (has_sin_camisa or re.search(r'quita\s+la\s+camisa|sin\s+camisa', text, re.I)):
            vestuario_found = [v for v in vestuario_found if v not in ('SUDADERA', 'SIN CAMISA', 'TORSO DESNUDO', 'CHAQUETA')]
            vestuario_found.insert(0, 'SUDADERA / SIN CAMISA')
        parts.extend(vestuario_found[:3])

    props_found = []
    for pattern, label in PROPS_PATTERNS:
        match = pattern.search(text)
        if match:
            match_pos = match.start()
            cerca = any(abs(match_pos - cp) < 300 for cp in char_mentions) if char_mentions else True
            if cerca and label not in props_found:
                props_found.append(label)

    if props_found:
        parts.extend(props_found[:4])

    acciones_found = []
    for pattern, label in ACCIONES_PATTERNS:
        if pattern.search(text) and label not in acciones_found:
            acciones_found.append(label)

    if acciones_found:
        parts.extend(acciones_found[:3])

    otros = [
        n for n in all_char_names
        if n.upper() != char_upper and re.search(rf'\b{re.escape(n)}\b', text, re.IGNORECASE)
    ]
    if otros:
        parts.append(f'Con: {", ".join(otros[:4])}')

    acotacion_limpia = re.sub(r'\s+', ' ', text).strip()
    if len(acotacion_limpia) > 20:
        parts.append(acotacion_limpia[:1800])

    return ' · '.join(p for p in parts if p)
