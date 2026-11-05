"""
Módulo: models.py
Descripción: Clases y modelos Orientados a Objetos (POO) para SITRAMED.
Alineado con el enfoque determinista, Índice de Coincidencia Sintomática (ICS)
y lectura directa de banderas rojas por cuadro clínico.
"""

class SintomaDetalle:
    def __init__(self, id_sintoma, nombre, peso_base=1, duracion_dias=1, intensidad=5, es_constante=True):
        self.id = id_sintoma
        self.nombre = nombre
        self.peso_base = peso_base
        self.duracion_dias = duracion_dias
        self.intensidad = intensidad
        self.es_constante = es_constante

    def calcular_multiplicador_severidad(self):
        factor_intensidad = self.intensidad / 5.0
        factor_duracion = 1.2 if self.duracion_dias > 3 else 1.0
        factor_frecuencia = 1.1 if self.es_constante else 0.9
        return round(self.peso_base * factor_intensidad * factor_duracion * factor_frecuencia, 2)


class CuadroClinico:
    """
    Representa un cuadro/categoría clínica sintomática dentro de la base de conocimiento.
    Se eliminó el nivel de riesgo visual para alinearse con la rigurosidad académica.
    """
    def __init__(self, id_cuadro, nombre, sintomas_clave, recomendaciones, canalizacion, banderas_rojas=""):
        self.id = id_cuadro
        self.nombre = nombre
        self.sintomas_clave = sintomas_clave  # Lista de IDs de síntomas (SINT-XX)
        self.recomendaciones = recomendaciones  # Cuidados no farmacológicos
        self.canalizacion = canalizacion  # Especialidad recomendada
        self.banderas_rojas = banderas_rojas  # Criterios de alarma y factores por edad


class ResultadoInferencia:
    """
    Estructura de salida determinista del motor de orientación.
    """
    def __init__(self, cuadro_clinico=None, ics=0.0, es_alerta_critica=False, datos_insuficientes=False, mensaje_sistema=""):
        self.cuadro_clinico = cuadro_clinico
        self.ics = round(ics, 2)  # Índice de Coincidencia Sintomática (%)
        self.es_alerta_critica = es_alerta_critica  # Interrupción inmediata por bandera roja
        self.datos_insuficientes = datos_insuficientes  # Caso TC-03: Descarte por falta de datos
        self.mensaje_sistema = mensaje_sistema

    def obtener_canalizacion(self):
        if self.es_alerta_critica:
            return "Urgencias Hospitalarias Inmediatas / 911"
        if self.datos_insuficientes:
            return "Consulta Presencial con Médico General (Datos Insuficientes)"
        if self.cuadro_clinico:
            return self.cuadro_clinico.canalizacion
        return "Consulta Médica General Preventiva"
