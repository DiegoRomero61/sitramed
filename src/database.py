import sqlite3
import os
from datetime import datetime

class DatabaseManager:
    def __init__(self, db_path="data/historial.db"):
        self.db_path = db_path
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        self._crear_tablas()

    def _obtener_conexion(self):
        return sqlite3.connect(self.db_path)

    def _crear_tablas(self):
        with self._obtener_conexion() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS consultas (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    nombre_paciente TEXT NOT NULL,
                    edad INTEGER NOT NULL,
                    fecha DATETIME NOT NULL,
                    ics_porcentaje REAL NOT NULL,
                    canalizacion TEXT NOT NULL
                )
            """)
            conn.commit()

    def guardar_consulta(self, nombre, edad, ics_porcentaje, canalizacion):
        try:
            fecha_actual = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            with self._obtener_conexion() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT INTO consultas (nombre_paciente, edad, fecha, ics_porcentaje, canalizacion)
                    VALUES (?, ?, ?, ?, ?)
                """, (nombre, edad, fecha_actual, ics_porcentaje, canalizacion))
                conn.commit()
        except sqlite3.Error as e:
            print(f"Error al guardar en base de datos SQLite: {e}")
