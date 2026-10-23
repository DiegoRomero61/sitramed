class SintomaDetalle:
    def __init__(self, id_sintoma, nombre, duracion_dias=1, intensidad=5, es_constante=True):
        self.id = id_sintoma
        self.nombre = nombre
        self.duracion_dias = duracion_dias
        self.intensidad = intensidad
        self.es_constante = es_constante

    def calcular_multiplicador_severidad(self):
        factor_intensidad = self.intensidad / 5.0
        factor_duracion = 1.2 if self.duracion_dias > 3 else 1.0
        factor_frecuencia = 1.1 if self.es_constante else 0.9
        return round(factor_intensidad * factor_duracion * factor_frecuencia, 2)

class Enfermedad:
    def __init__(self, id_enfermedad, nombre, sintomas_clave, nivel_riesgo, recomendaciones, canalizacion, banderas_rojas=""):
        self.id = id_enfermedad
        self.nombre = nombre
        self.sintomas_clave = sintomas_clave
        self.nivel_riesgo = nivel_riesgo
        self.recomendaciones = recomendaciones
        self.canalizacion = canalizacion
        self.banderas_rojas = banderas_rojas

class DiagnosticoResultado:
    def __init__(self, enfermedad, factores_riesgo, es_alerta_critica=False):
        self.enfermedad = enfermedad
        self.factores_riesgo = factores_riesgo
        self.es_alerta_critica = es_alerta_critica