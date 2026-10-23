from src.models import DiagnosticoResultado, SintomaDetalle, Enfermedad

class InferenceEngine:
    def __init__(self, tree_engine):
        self.tree_engine = tree_engine
        self.sintomas_evaluados = []

    def agregar_sintoma_detalle(self, id_sintoma, nombre, duracion, intensidad, es_constante):
        detalle = SintomaDetalle(id_sintoma, nombre, duracion, intensidad, es_constante)
        self.sintomas_evaluados.append(detalle)

    def calcular_diagnosticos(self):
        resultados = []
        if not self.sintomas_evaluados:
            return resultados

        # --- EVALUACIÓN DE BANDERAS ROJAS / URGENCIA CRÍTICA ---
        for s in self.sintomas_evaluados:
            if (s.id in ["SINT-15", "SINT-04"]) and s.intensidad >= 8:
                enf_emergencia = Enfermedad(
                    id_enfermedad="EMERG-911",
                    nombre="Orientación Sintomática de Emergencia",
                    sintomas_clave=[s.id],
                    nivel_riesgo="CRÍTICO / URGENTE",
                    recomendaciones="Presenta signos de alarma graves. No intente automedicarse ni espere.",
                    canalizacion="Urgencias Hospitalarias / Llamada inmediata al 911",
                    banderas_rojas="Múltiples signos de falla respiratoria o cardiovascular aguda detectados."
                )
                return [DiagnosticoResultado(enf_emergencia, [f"Severidad elevada en {s.nombre}"], es_alerta_critica=True)]

        # --- EVALUACIÓN Y COINCIDENCIA DE SÍNDROMES ---
        for enf in self.tree_engine.enfermedades.values():
            coincidencias = 0
            factores_alerta = []

            for s_id in enf.sintomas_clave:
                s_reportado = next((s for s in self.sintomas_evaluados if s.id == s_id), None)
                if s_reportado:
                    coincidencias += 1
                    if s_reportado.intensidad >= 8:
                        factores_alerta.append(f"Alta intensidad en {s_reportado.nombre}")

            if coincidencias > 0:
                resultados.append((coincidencias, DiagnosticoResultado(enf, factores_alerta)))

        # Ordenar por mayor número de síntomas coincidentes
        resultados.sort(key=lambda x: x[0], reverse=True)
        return [r[1] for r in resultados]