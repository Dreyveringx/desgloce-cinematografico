from collections import OrderedDict

from app.core.script_parser import FilaDesglose, extract_character_observation


def build(escenas: list, personajes_principales: list, personajes_extras: list) -> dict:
    """
    Construye el breakdown completo.
    Retorna:
    {
        'personajes': { nombre: OrderedDict{ dia: [FilaDesglose] } },
        'extras': OrderedDict{ dia: [FilaDesglose] },
        'cambios': [ {'personaje': str, 'resumen': str, 'items': [str]} ]
    }
    """
    resultado_personajes = {}
    kbio_tracker = {}

    for personaje in personajes_principales:
        resultado_personajes[personaje] = OrderedDict()
        kbio_tracker[personaje] = {}

    for esc in escenas:
        for personaje in esc.personajes:
            if personaje not in resultado_personajes:
                continue
            dia = esc.dia_rodaje
            if dia not in resultado_personajes[personaje]:
                resultado_personajes[personaje][dia] = []
                kbio_tracker[personaje][dia] = 1

            fila = FilaDesglose(
                kbio=kbio_tracker[personaje][dia],
                capitulo=esc.capitulo,
                escena=esc.numero,
                locacion=esc.locacion,
                ext=esc.es_exterior,
                int_=esc.es_interior,
                dia=esc.es_dia,
                noche=esc.es_noche,
                observacion=extract_character_observation(
                    personaje, esc.acotacion, personajes_principales
                ),
                continuidad=esc.continuidad,
            )
            resultado_personajes[personaje][dia].append(fila)

    extras_por_dia = OrderedDict()
    for esc in escenas:
        if not esc.extras:
            continue
        dia = esc.dia_rodaje
        if dia not in extras_por_dia:
            extras_por_dia[dia] = []
        fila = FilaDesglose(
            kbio=None,
            capitulo=esc.capitulo,
            escena=esc.numero,
            locacion=esc.locacion,
            ext=esc.es_exterior,
            int_=esc.es_interior,
            dia=esc.es_dia,
            noche=esc.es_noche,
            observacion=f"{', '.join(esc.extras[:5])} — {esc.acotacion}",
        )
        extras_por_dia[dia].append(fila)

    cambios = []
    for personaje, dias in resultado_personajes.items():
        total_escenas = sum(len(f) for f in dias.values())
        cambios.append({
            'personaje': personaje,
            'resumen': f"{max(1, total_escenas // 10)} CAMBIOS",
            'items': []
        })

    return {
        'personajes': resultado_personajes,
        'extras': extras_por_dia,
        'cambios': cambios,
    }
