import sqlite3
import os

class DatabaseManager:
    def __init__(self, db_path="data/historial.db"):
        self.db_path = db_path
        self._crear_tablas()

    def _conectar(self):
        return sqlite3.connect(self.db_path)

    def _crear_tablas(self):
        """Crea las tablas de pacientes e historial de diagnósticos si no existen."""
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        with self._conectar() as conn:
            cursor = conn.cursor()
            
            # Tabla de Pacientes
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS pacientes (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    nombre TEXT NOT NULL,
                    edad INTEGER NOT NULL,
                    fecha_registro TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')

            # Tabla de Historial de Diagnósticos / Triaje
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS historial_diagnosticos (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    paciente_id INTEGER,
                    diagnostico_sugerido TEXT NOT NULL,
                    porcentaje_certidumbre REAL NOT NULL,
                    especialidad_canalizada TEXT NOT NULL,
                    fecha_consulta TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (paciente_id) REFERENCES pacientes (id)
                )
            ''')
            conn.commit()

    def guardar_consulta(self, nombre_paciente, edad, diagnostico, certidumbre, canalizacion):
        """Registra un paciente y su resultado en la base de datos."""
        with self._conectar() as conn:
            cursor = conn.cursor()
            # Insertar paciente
            cursor.execute(
                "INSERT INTO pacientes (nombre, edad) VALUES (?, ?)", 
                (nombre_paciente, edad)
            )
            paciente_id = cursor.lastrowid

            # Insertar historial de la consulta
            cursor.execute('''
                INSERT INTO historial_diagnosticos 
                (paciente_id, diagnostico_sugerido, porcentaje_certidumbre, especialidad_canalizada)
                VALUES (?, ?, ?, ?)
            ''', (paciente_id, diagnostico, certidumbre, canalizacion))
            
            conn.commit()
            return paciente_id