import json
import os
from src.models import CuadroClinico

class TreeEngine:
    def __init__(self, json_path="data/base_conocimiento.json"):
        self.json_path = json_path
        self.sintomas_secundarios = {}
        self.cuadros_clinicos = {}

    def cargar_conocimiento(self):
        if not os.path.exists(self.json_path):
            raise FileNotFoundError(f"No se encontró la base de conocimiento en: {self.json_path}")

        with open(self.json_path, "r", encoding="utf-8") as f:
            data = json.load(f)

        for s in data.get("sintomas_secundarios", []):
            self.sintomas_secundarios[s["id"]] = s

        for e in data.get("enfermedades", []):
            # Carga directa y obligatoria del texto de banderas rojas del JSON
            texto_flags = e.get("banderas_rojas", "").strip()
            if not texto_flags:
                texto_flags = "Consulte a un profesional médico si los síntomas empeoran o persisten."

            self.cuadros_clinicos[e["id"]] = CuadroClinico(
                id_cuadro=e["id"],
                nombre=e["nombre"],
                sintomas_clave=e["sintomas_clave"],
                recomendaciones=e["recomendaciones"],
                canalizacion=e["canalizacion"],
                banderas_rojas=texto_flags
            )
