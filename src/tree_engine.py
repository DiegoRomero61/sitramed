import json
import os
from src.models import Enfermedad

class TreeEngine:
    def __init__(self, json_path="data/base_conocimiento.json"):
        self.json_path = json_path
        self.sintomas_secundarios = {}
        self.enfermedades = {}

    def cargar_conocimiento(self):
        if not os.path.exists(self.json_path):
            raise FileNotFoundError(f"No se encontró el archivo de base de conocimiento en: {self.json_path}")

        with open(self.json_path, "r", encoding="utf-8") as f:
            data = json.load(f)

        for s in data.get("sintomas_secundarios", []):
            self.sintomas_secundarios[s["id"]] = s

        for e in data.get("enfermedades", []):
            self.enfermedades[e["id"]] = Enfermedad(
                id_enfermedad=e["id"],
                nombre=e["nombre"],
                sintomas_clave=e["sintomas_clave"],
                nivel_riesgo=e["nivel_riesgo"],
                recomendaciones=e["recomendaciones"],
                canalizacion=e["canalizacion"],
                banderas_rojas=e.get("banderas_rojas", "Consulte a un médico si los síntomas empeoran o persisten.")
            )