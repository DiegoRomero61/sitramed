from src.models import ResultadoInferencia, SintomaDetalle, CuadroClinico

class InferenceEngine:
    def __init__(self, tree_engine):
        self.tree_engine = tree_engine
        self.sintomas_evaluados = []

    def agregar_sintoma_detalle(self, id_sintoma, nombre, peso_base=1, duracion=1, intensidad=5, es_constante=True):
        detalle = SintomaDetalle(id_sintoma, nombre, peso_base, duracion, intensidad, es_constante)
        self.sintomas_evaluados.append(detalle)

    def calcular_orientacion(self):
        if not self.sintomas_evaluados:
            return [ResultadoInferencia(datos_insuficientes=True, mensaje_sistema="No se registraron síntomas para evaluar.")]

        ids_reportados = []
        for s in self.sintomas_evaluados:
            if s.id not in ids_reportados:
                ids_reportados.append(s.id)

        set_reportados = set(ids_reportados)
        num_sintomas = len(set_reportados)

        # --- 1. EVALUACIÓN DE BANDERAS ROJAS CRÍTICAS DE ENTRADA ---
        for s in self.sintomas_evaluados:
            if (s.id in ["SINT-15", "SINT-04", "SINT-16", "SINT-28"]) and s.intensidad >= 8:
                emergencia_cuadro = CuadroClinico(
                    id_cuadro="EMERG-911",
                    nombre="Alerta Clínica de Emergencia",
                    sintomas_clave=[s.id],
                    recomendaciones="Presenta signos de alarma críticos. Guarde reposo absoluto, no se automedique y solicite asistencia médica inmediata.",
                    canalizacion="Servicios de Urgencias Médicas Inmediato / Llamada al 911",
                    banderas_rojas="Múltiples marcas de severidad respiratoria, cardiovascular o anafiláctica detectadas."
                )
                return [ResultadoInferencia(cuadro_clinico=emergencia_cuadro, ics=100.0, es_alerta_critica=True)]

        # --- 2. COINCIDENCIA EXACTA DIRECTA (1 o más síntomas que matcheen un cuadro específico) ---
        for cuadro in self.tree_engine.cuadros_clinicos.values():
            if set(cuadro.sintomas_clave) == set_reportados:
                return [ResultadoInferencia(cuadro_clinico=cuadro, ics=100.0)]

        # --- 3. MANEJO DE MÚLTIPLES SÍNTOMAS SIN CUADRO COMBINADO ---
        
        # SI SON 3 O MÁS SÍNTOMAS Y NO HAY MATCHER EXACTO -> Muestra información ambigua / confusa
        if num_sintomas >= 3:
            return [ResultadoInferencia(
                datos_insuficientes=True, 
                mensaje_sistema="Se ha ingresado una combinación de múltiples síntomas (3 o más) que no coincide con un cuadro único en la base de conocimiento. La información resulta ambigua o heterogénea; se recomienda acudir a valoración presencial con un Médico General."
            )]

        # SI SON EXACTAMENTE 2 SÍNTOMAS Y NO HAY UN CUADRO COMBINADO -> Acumular los 2 cuadros mono-sintomáticos
        if num_sintomas == 2:
            cuadros_individuales = []
            for id_s in ids_reportados:
                for cuadro in self.tree_engine.cuadros_clinicos.values():
                    if cuadro.sintomas_clave == [id_s]:
                        cuadros_individuales.append(cuadro)
                        break

            if len(cuadros_individuales) == 2:
                c1, c2 = cuadros_individuales[0], cuadros_individuales[1]
                
                # Combinar nombres, canalizaciones y recomendaciones
                nombre_comb = f"{c1.nombre} + {c2.nombre}"
                canal_comb = f"{c1.canalizacion} / {c2.canalizacion}"
                recom_comb = f"• [{c1.nombre}]: {c1.recomendaciones}\n\n• [{c2.nombre}]: {c2.recomendaciones}"
                flags_comb = f"• [{c1.nombre}]: {c1.banderas_rojas}\n\n• [{c2.nombre}]: {c2.banderas_rojas}"

                cuadro_acumulado = CuadroClinico(
                    id_cuadro="ENF-COMBINADA",
                    nombre=nombre_comb,
                    sintomas_clave=ids_reportados,
                    recomendaciones=recom_comb,
                    canalizacion=canal_comb,
                    banderas_rojas=flags_comb
                )
                return [ResultadoInferencia(cuadro_clinico=cuadro_acumulado, ics=100.0)]

        # --- 4. BÚSQUEDA SECUNDARIA POR MAYOR COINCIDENCIA (Fallback) ---
        candidatos = []
        for cuadro in self.tree_engine.cuadros_clinicos.values():
            sintomas_clave_set = set(cuadro.sintomas_clave)
            coincidencias = set_reportados.intersection(sintomas_clave_set)
            
            if coincidencias:
                num_coincidencias = len(coincidencias)
                tamano_cuadro = len(sintomas_clave_set)
                cobertura_usuario = num_coincidencias / len(set_reportados)
                especificidad = num_coincidencias / tamano_cuadro

                candidatos.append({
                    "cuadro": cuadro,
                    "cobertura_usuario": cobertura_usuario,
                    "especificidad": especificidad,
                    "tamano_cuadro": tamano_cuadro
                })

        if not candidatos:
            return [ResultadoInferencia(
                datos_insuficientes=True, 
                mensaje_sistema="Los datos ingresados no coinciden con ningún cuadro sintomático registrado."
            )]

        candidatos.sort(
            key=lambda c: (c["cobertura_usuario"], c["especificidad"], -c["tamano_cuadro"]), 
            reverse=True
        )

        mejor_opcion = candidatos[0]["cuadro"]
        ics_valor = round(candidatos[0]["especificidad"] * 100.0, 2)

        return [ResultadoInferencia(cuadro_clinico=mejor_opcion, ics=ics_valor)]
