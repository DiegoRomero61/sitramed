import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import os
from datetime import datetime
from src.tree_engine import TreeEngine
from src.inference_engine import InferenceEngine
from src.database import DatabaseManager

class SitramedUI:
    def __init__(self, root):
        self.root = root
        self.root.title("SITRAMED - Asistente Local de Triaje Sintomático")
        self.root.geometry("1020x750")
        self.root.configure(bg="#F0F4F8")

        # Inicialización de motores
        self.tree = TreeEngine()
        self.tree.cargar_conocimiento()
        self.engine = InferenceEngine(self.tree)
        self.db = DatabaseManager()

        self.catalogo = list(self.tree.sintomas_secundarios.values())
        self.sintomas_registrados_ids = set()
        self.sintomas_pendientes_preguntas = []
        self.sintoma_actual_evaluando = None
        self.consulta_finalizada = False

        self._crear_interfaz()
        self.root.after(200, self._mostrar_disclaimer_inicial)

    def _mostrar_disclaimer_inicial(self):
        titulo_aviso = "SITRAMED | AVISO LEGAL Y EXENCIÓN DE RESPONSABILIDAD MÉDICA"
        mensaje_aviso = (
            "INFORMACIÓN IMPORTANTE PARA EL USUARIO:\n\n"
            "1. NO ES UN DIAGNÓSTICO MÉDICO:\n"
            "Este software (SITRAMED) es un prototipo académico diseñado exclusivamente "
            "como herramienta de ORIENTACIÓN PRELIMINAR Y TRIAGEMENTO SINTOMÁTICO. "
            "En ningún caso sustituye la consulta, valoración, diagnóstico o tratamiento de un "
            "profesional de la salud capacitado.\n\n"
            "2. ORIENTACIÓN DE AUTOCUIDADO NO FARMACOLÓGICO:\n"
            "Las recomendaciones brindadas consisten únicamente en medidas generales de "
            "autocuidado (p. ej., descanso, hidratación y compresas) y no prescriben "
            "fármacos de ninguna clase.\n\n"
            "3. FUENTES OFICIALES Y DOCUMENTADAS:\n"
            "La base de conocimiento de este sistema se encuentra fundamentada en protocolos "
            "y literatura médica internacional de libre acceso (Guías de Práctica Clínica CENETEC, "
            "Organización Mundial de la Salud - OMS, Mayo Clinic y GINA).\n\n"
            "4. EN CASO DE EMERGENCIA CRÍTICA:\n"
            "Si presenta dolor opresivo en el pecho, dificultad severa para respirar o sangrado incontrolable, "
            "acuda inmediatamente a un servicio de urgencias o llame al 911.\n\n"
            "Al hacer clic en 'Aceptar', usted reconoce y comprende los alcances de este prototipo."
        )
        messagebox.showwarning(titulo_aviso, mensaje_aviso)

    def _crear_interfaz(self):
        header = tk.Frame(self.root, bg="#1E3A8A", height=55)
        header.pack(fill=tk.X, side=tk.TOP)
        lbl_titulo = tk.Label(header, text="SITRAMED | Asistente Local de Triaje Sintomático", 
                              font=("Segoe UI", 14, "bold"), fg="white", bg="#1E3A8A")
        lbl_titulo.pack(pady=12, padx=20, side=tk.LEFT)

        main_container = tk.Frame(self.root, bg="#F0F4F8")
        main_container.pack(fill=tk.BOTH, expand=True, padx=12, pady=10)

        # --- COLUMNA DERECHA: Ficha de Orientación ---
        col_derecha = tk.LabelFrame(main_container, text=" Ficha de Orientación Sintomática ", font=("Segoe UI", 10, "bold"), 
                                    bg="white", fg="#1E293B", padx=12, pady=10, width=420)
        col_derecha.pack(side=tk.RIGHT, fill=tk.Y, padx=(10, 0))
        col_derecha.pack_propagate(False)

        # CANALIZACIÓN PROMOVIDA COMO ENCABEZADO PRINCIPAL (Letras azules, grande y destacado)
        self.lbl_canalizacion = tk.Label(col_derecha, text="Canalización Sugerida: --", 
                                         font=("Segoe UI", 11, "bold"), fg="#2563EB", bg="white", 
                                         wraplength=380, justify="left")
        self.lbl_canalizacion.pack(anchor="w", pady=(2, 6))

        # 1. Recomendaciones y Autocuidado
        tk.Label(col_derecha, text="Recomendaciones y Autocuidado General:", font=("Segoe UI", 8, "bold"), bg="white", fg="#1E293B").pack(anchor="w", pady=(4, 2))
        self.txt_recom = tk.Text(col_derecha, font=("Segoe UI", 8), wrap=tk.WORD, bg="#F8FAFC", relief=tk.FLAT, height=4)
        self.txt_recom.pack(fill=tk.X, pady=(0, 4))

        # --- CONTENEDOR 50/50 PARA BANDERAS ROJAS Y DIRECTORIO MÉDICO ---
        frame_split = tk.Frame(col_derecha, bg="white")
        frame_split.pack(fill=tk.BOTH, expand=True, pady=(2, 6))

        # 2. Signos de Alerta / Banderas Rojas
        frame_flags = tk.Frame(frame_split, bg="white")
        frame_flags.pack(fill=tk.BOTH, expand=True, pady=(0, 4))
        
        tk.Label(frame_flags, text="🚨 Signos de Alerta / Banderas Rojas (Factores Edad):", font=("Segoe UI", 8, "bold"), bg="white", fg="#DC2626").pack(anchor="w", pady=(0, 2))
        self.txt_flags = tk.Text(frame_flags, font=("Segoe UI", 8), wrap=tk.WORD, bg="#FEF2F2", fg="#991B1B", relief=tk.FLAT)
        self.txt_flags.pack(fill=tk.BOTH, expand=True)

        # 3. Centros de Atención Referenciados (ZMG)
        frame_medicos = tk.Frame(frame_split, bg="white")
        frame_medicos.pack(fill=tk.BOTH, expand=True, pady=(4, 0))
        
        tk.Label(frame_medicos, text="📍 Centros de Atención Referenciados (ZMG):", font=("Segoe UI", 8, "bold"), bg="white", fg="#047857").pack(anchor="w", pady=(0, 2))
        self.txt_medicos = tk.Text(frame_medicos, font=("Segoe UI", 8), wrap=tk.WORD, bg="#ECFDF5", fg="#065F46", relief=tk.FLAT)
        self.txt_medicos.pack(fill=tk.BOTH, expand=True)

        # Botón PDF
        self.btn_descargar = tk.Button(col_derecha, text="📥 Descargar Ficha en PDF", font=("Segoe UI", 9, "bold"),
                                       bg="#2563EB", fg="white", relief=tk.FLAT, state=tk.DISABLED,
                                       command=self._descargar_informe_pdf)
        self.btn_descargar.pack(fill=tk.X, ipady=6)

        # --- COLUMNA IZQUIERDA: Conversación ---
        col_izquierda = tk.LabelFrame(main_container, text=" Registro de Consulta ", font=("Segoe UI", 10, "bold"), 
                                      bg="white", fg="#1E293B", padx=12, pady=10)
        col_izquierda.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        frame_paciente = tk.Frame(col_izquierda, bg="white")
        frame_paciente.pack(fill=tk.X, pady=(0, 8))

        tk.Label(frame_paciente, text="Nombre Paciente:", bg="white", font=("Segoe UI", 9, "bold"), fg="#475569").grid(row=0, column=0, sticky="w")
        self.entry_nombre = tk.Entry(frame_paciente, font=("Segoe UI", 9), width=20, relief=tk.SOLID, bd=1)
        self.entry_nombre.insert(0, "Jose Diego Romero Mata")
        self.entry_nombre.grid(row=0, column=1, padx=4, pady=2)

        tk.Label(frame_paciente, text="Edad:", bg="white", font=("Segoe UI", 9, "bold"), fg="#475569").grid(row=0, column=2, sticky="w", padx=(8, 0))
        self.entry_edad = tk.Entry(frame_paciente, font=("Segoe UI", 9), width=4, relief=tk.SOLID, bd=1)
        self.entry_edad.insert(0, "22")
        self.entry_edad.grid(row=0, column=3, padx=4, pady=2)

        btn_reiniciar = tk.Button(frame_paciente, text="🔄 Nueva Consulta", font=("Segoe UI", 8, "bold"), 
                                  bg="#059669", fg="white", relief=tk.FLAT, padx=6, command=self._reiniciar_consulta)
        btn_reiniciar.grid(row=0, column=4, padx=(10, 0), sticky="e")

        frame_chat_container = tk.Frame(col_izquierda, bg="#F1F5F9", bd=1, relief=tk.SOLID)
        frame_chat_container.pack(fill=tk.BOTH, expand=True, pady=8)

        self.txt_chat = tk.Text(frame_chat_container, state=tk.DISABLED, wrap=tk.WORD, font=("Segoe UI", 9),
                                bg="#F1F5F9", relief=tk.FLAT, padx=8, pady=8)
        self.txt_chat.pack(fill=tk.BOTH, expand=True)

        self.txt_chat.tag_config("bienvenida", font=("Segoe UI", 12, "bold"), foreground="#1E3A8A", justify="center")
        self.txt_chat.tag_config("sub_bienvenida", font=("Segoe UI", 8), foreground="#64748B", justify="center")
        self.txt_chat.tag_config("bot_msg", font=("Segoe UI", 9, "bold"), foreground="#1E293B", background="#E2E8F0", lmargin1=8, lmargin2=12, rmargin=40, spacing1=3, spacing3=3)
        self.txt_chat.tag_config("user_msg", font=("Segoe UI", 9, "bold"), foreground="white", background="#2563EB", justify="right", rmargin=8, lmargin1=80, spacing1=3, spacing3=3)

        frame_input = tk.Frame(col_izquierda, bg="white")
        frame_input.pack(fill=tk.X, pady=(4, 0))

        self.entry_usuario = tk.Entry(frame_input, font=("Segoe UI", 9), relief=tk.SOLID, bd=1)
        self.entry_usuario.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 4), ipady=5)
        self.entry_usuario.bind("<Return>", lambda event: self._procesar_entrada())

        btn_enviar = tk.Button(frame_input, text="Enviar", font=("Segoe UI", 9, "bold"), bg="#2563EB", fg="white", 
                               relief=tk.FLAT, padx=10, command=self._procesar_entrada)
        btn_enviar.pack(side=tk.LEFT, padx=(0, 4))

        btn_finalizar = tk.Button(frame_input, text="Finalizar Consulta", font=("Segoe UI", 9, "bold"), bg="#DC2626", fg="white", 
                                  relief=tk.FLAT, padx=10, command=self._finalizar_consulta)
        btn_finalizar.pack(side=tk.RIGHT)

        self._mostrar_saludo_inicial()

    def _mostrar_saludo_inicial(self):
        self.txt_chat.config(state=tk.NORMAL)
        self.txt_chat.delete("1.0", tk.END)
        self.txt_chat.insert(tk.END, "\n¿Qué síntomas o molestias sientes hoy?\n", "bienvenida")
        self.txt_chat.insert(tk.END, "Describe libremente lo que te pasa (ej. 'tengo dolor de cabeza y fiebre'):\n\n", "sub_bienvenida")
        self.txt_chat.see(tk.END)
        self.txt_chat.config(state=tk.DISABLED)

    def _obtener_medicos_zmg(self, canalizacion_str, es_urgencia=False):
        """Devuelve un directorio de centros médicos locales de Guadalajara según la especialidad canalizada."""
        if es_urgencia or "Urgencias" in canalizacion_str or "911" in canalizacion_str:
            return (
                "1. Hospital Civil de Guadalajara 'Fray Antonio Alcalde'\n"
                "   📍 C. Hospital 278, Col. El Retiro, GDL | 📞 (33) 3883 4000\n\n"
                "2. Cruz Roja Mexicana Delegación Guadalajara\n"
                "   📍 Av. San Luis Potosí 540, Col. Santuario, GDL | 📞 (33) 3614 5610\n\n"
                "3. UMF / HGZ No. 14 IMSS (Servicio de Urgencias)\n"
                "   📍 Av. 16 de Septiembre 868, Centro, GDL | 📞 (33) 3613 0184"
            )
        elif "Otorrinolaringología" in canalizacion_str or "Audiología" in canalizacion_str:
            return (
                "1. Instituto de Otrología y Neurotología ZMG\n"
                "   📍 Av. Hidalgo 1450, Col. Ladrón de Guevara, GDL | 📞 (33) 3615 2020\n\n"
                "2. UMAE Hospital de Especialidades CMNO IMSS\n"
                "   📍 Av. Belisario Domínguez 1000, Col. Independencia, GDL\n\n"
                "3. Hospital Civil 'Dr. Juan I. Menchaca' (Consultas ORL)\n"
                "   📍 C. Salvador Quevedo y Zubieta 750, Col. Independencia, GDL"
            )
        elif "Gastroenterología" in canalizacion_str or "Hepatología" in canalizacion_str:
            return (
                "1. Servicio de Gastroenterología Hospital Civil Nuevo\n"
                "   📍 C. Salvador Quevedo y Zubieta 750, Col. Independencia, GDL\n\n"
                "2. UMAE Centro Médico Nacional de Occidente (CMNO IMSS)\n"
                "   📍 Av. Belisario Domínguez 1000, Col. Independencia, GDL\n\n"
                "3. UMF No. 51 IMSS Guadalajara\n"
                "   📍 Av. Profesora María Reyes 1184, Col. El Ginés, GDL"
            )
        elif "Neumología" in canalizacion_str:
            return (
                "1. Instituto de Neumología y Cirugía del Tórax de GDL\n"
                "   📍 Av. México 2580, Col. Ladrón de Guevara, GDL | 📞 (33) 3616 1212\n\n"
                "2. UMAE Hospital de Especialidades CMNO IMSS (Neumología)\n"
                "   📍 Av. Belisario Domínguez 1000, Col. Independencia, GDL\n\n"
                "3. Hospital Civil de Guadalajara 'Fray Antonio Alcalde'\n"
                "   📍 C. Hospital 278, Col. El Retiro, GDL"
            )
        elif "Oftalmología" in canalizacion_str:
            return (
                "1. Instituto de Oftalmología y Ciencias Visuales ZMG\n"
                "   📍 Av. Revolución 1500, Col. Universitaria, GDL | 📞 (33) 3619 8080\n\n"
                "2. Hospital de Oftalmología Santa Lucía\n"
                "   📍 Av. Hidalgo 1420, Col. Ladrón de Guevara, GDL | 📞 (33) 3615 3030\n\n"
                "3. Clínica Oftalmológica Hospital Civil Viejo\n"
                "   📍 C. Coronel Calderón 777, Col. El Retiro, GDL"
            )
        elif "Neurología" in canalizacion_str:
            return (
                "1. Instituto de Neurociencias de Guadalajara (UdeG)\n"
                "   📍 C. Francisco de Quevedo 180, Col. Arcos Vallarta, GDL\n\n"
                "2. UMAE Hospital de Especialidades CMNO IMSS (Neurología)\n"
                "   📍 Av. Belisario Domínguez 1000, Col. Independencia, GDL\n\n"
                "3. Hospital Civil Fray Antonio Alcalde (Torre de Especialidades)\n"
                "   📍 C. Hospital 278, Col. El Retiro, GDL"
            )
        elif any(k in canalizacion_str for k in ["Traumatología", "Ortopedia", "Reumatología"]):
            return (
                "1. Hospital de Traumatología y Ortopedia HGO IMSS\n"
                "   📍 Av. Circunvalación Agustín Yáñez 1988, Col. Moderna, GDL\n\n"
                "2. Hospital Civil 'Fray Antonio Alcalde' (Ortopedia y Trauma)\n"
                "   📍 C. Hospital 278, Col. El Retiro, GDL | 📞 (33) 3883 4000\n\n"
                "3. Cruz Verde Ruiz Sánchez (Traumatología de Urgencias)\n"
                "   📍 C. Medrano 2000, Col. San Antonio, GDL"
            )
        elif "Odontología" in canalizacion_str:
            return (
                "1. Clínica Odontológica CUCEI / CUCS (UdeG)\n"
                "   📍 Av. Sierra Nevada 950, Col. Independencia, GDL\n\n"
                "2. Servicio de Cirugía Maxilofacial Hospital Civil Viejo\n"
                "   📍 C. Hospital 278, Col. El Retiro, GDL\n\n"
                "3. UMF No. 2 IMSS (Consultorio Dental)\n"
                "   📍 Av. Javier Mina 614, Col. Oblatos, GDL"
            )
        elif "Dermatología" in canalizacion_str:
            return (
                "1. Instituto Dermatológico 'Dr. José Barba Rubio'\n"
                "   📍 Av. Federalismo Norte 3102, Zapopan | 📞 (33) 3030 4500\n\n"
                "2. Clínica de Dermatología Hospital Civil Fray Antonio Alcalde\n"
                "   📍 C. Hospital 278, Col. El Retiro, GDL\n\n"
                "3. UMAE CMNO IMSS (Dermatología Médica)\n"
                "   📍 Av. Belisario Domínguez 1000, Col. Independencia, GDL"
            )
        elif "Urología" in canalizacion_str or "Ginecología" in canalizacion_str or "Sexología" in canalizacion_str:
            return (
                "1. UMAE Hospital de Ginecobstetricia CMNO IMSS\n"
                "   📍 Av. Belisario Domínguez 1000, Col. Independencia, GDL\n\n"
                "2. Servicio de Urología Hospital Civil Fray Antonio Alcalde\n"
                "   📍 C. Hospital 278, Col. El Retiro, GDL\n\n"
                "3. UMF No. 3 IMSS (Atención Integral/Medicina Familiar)\n"
                "   📍 Av. Belisario Domínguez 492, Col. San Juan de Dios, GDL"
            )
        elif "Psicología" in canalizacion_str or "Psiquiatría" in canalizacion_str:
            return (
                "1. SALME - Instituto Jalisciense de Salud Mental\n"
                "   📍 Av. Zoquipan 1000, Zapopan | 📞 (33) 3833 0000\n\n"
                "2. Centro de Evaluación Psicológica (UdeG CUCS)\n"
                "   📍 C. Sierra Nevada 950, Col. Independencia, GDL\n\n"
                "3. Hospital Psiquiátrico 'El Zapote' (Línea SALME: 800 227 4747)\n"
                "   📍 Tlajomulco de Zúñiga, ZMG"
            )
        else:
            return (
                "1. UMF No. 2 IMSS Guadalajara (Medicina Familiar)\n"
                "   📍 Av. Javier Mina 614, Col. Oblatos, GDL\n\n"
                "2. Hospital Civil de Guadalajara 'Dr. Juan I. Menchaca'\n"
                "   📍 C. Salvador Quevedo y Zubieta 750, Col. Independencia, GDL\n\n"
                "3. Cruz Verde Del Rosario (Consulta General ZMG)\n"
                "   📍 Av. Michelena 180, Col. Rincón de la Agua, GDL"
            )

    def _reiniciar_consulta(self):
        self.engine = InferenceEngine(self.tree)
        self.sintomas_registrados_ids.clear()
        self.sintomas_pendientes_preguntas.clear()
        self.sintoma_actual_evaluando = None
        self.consulta_finalizada = False

        self.entry_usuario.delete(0, tk.END)
        self.lbl_canalizacion.config(text="Canalización Sugerida: --")
        self.txt_recom.delete("1.0", tk.END)
        self.txt_flags.delete("1.0", tk.END)
        self.txt_medicos.delete("1.0", tk.END)
        self.btn_descargar.config(state=tk.DISABLED)

        self._mostrar_saludo_inicial()
        messagebox.showinfo("Nueva Consulta", "El sistema ha sido reiniciado. Puede ingresar los síntomas de un nuevo paciente.")

    def _agregar_mensaje_sistema(self, mensaje):
        self.txt_chat.config(state=tk.NORMAL)
        self.txt_chat.insert(tk.END, f"\n SITRAMED: {mensaje} \n", "bot_msg")
        self.txt_chat.see(tk.END)
        self.txt_chat.config(state=tk.DISABLED)

    def _agregar_mensaje_usuario(self, mensaje):
        self.txt_chat.config(state=tk.NORMAL)
        self.txt_chat.insert(tk.END, f"\n TÚ: {mensaje} \n", "user_msg")
        self.txt_chat.see(tk.END)
        self.txt_chat.config(state=tk.DISABLED)

    def _procesar_entrada(self):
        if self.consulta_finalizada:
            messagebox.showinfo("Consulta Finalizada", "Esta consulta ya ha sido cerrada. Haz clic en 'Nueva Consulta' para evaluar otro caso.")
            return

        texto = self.entry_usuario.get().strip()
        if not texto:
            return

        self._agregar_mensaje_usuario(texto)
        self.entry_usuario.delete(0, tk.END)

        if texto.lower() in ["finalizar", "terminar", "salir", "fin"]:
            self._finalizar_consulta()
            return

        if self.sintoma_actual_evaluando:
            self._guardar_detalle_sintoma(texto)
            return

        texto_norm = texto.lower()
        detectados = []
        for s in self.catalogo:
            for kw in s.get("keywords", []):
                if kw.lower() in texto_norm:
                    if s not in detectados and s["id"] not in self.sintomas_registrados_ids:
                        detectados.append(s)
                    break

        if not detectados:
            self._agregar_mensaje_sistema("No logré identificar síntomas mapeados en el catálogo. Intenta describirlos con otras palabras (ej. 'dolor de muela', 'fiebre', 'tos').")
        else:
            self.sintomas_pendientes_preguntas.extend(detectados)
            for s in detectados:
                self.sintomas_registrados_ids.add(s["id"])
            self._iniciar_siguiente_pregunta()

    def _iniciar_siguiente_pregunta(self):
        if self.sintomas_pendientes_preguntas:
            self.sintoma_actual_evaluando = self.sintomas_pendientes_preguntas.pop(0)
            tipo_preg = self.sintoma_actual_evaluando.get("tipo_preguntas", "normales")
            peso_b = self.sintoma_actual_evaluando.get("peso_base", 1)

            if tipo_preg == "directo":
                self.engine.agregar_sintoma_detalle(
                    id_sintoma=self.sintoma_actual_evaluando["id"],
                    nombre=self.sintoma_actual_evaluando["nombre"],
                    peso_base=peso_b,
                    duracion=1,
                    intensidad=5,
                    es_constante=True
                )
                self._agregar_mensaje_sistema(f"Registrado síntoma primario: '{self.sintoma_actual_evaluando['nombre']}'. Actualizando orientación...")
                self._iniciar_siguiente_pregunta()

            elif tipo_preg == "solo_intensidad":
                self.estado_pregunta = "intensidad"
                self._agregar_mensaje_sistema(f"Sobre '{self.sintoma_actual_evaluando['nombre']}': Del 1 al 10, ¿qué tan fuerte es la molestia?")

            elif tipo_preg == "solo_duracion":
                self.estado_pregunta = "dias"
                self._agregar_mensaje_sistema(f"Sobre '{self.sintoma_actual_evaluando['nombre']}': ¿Hace cuántos días comenzó?")

            else:
                self.estado_pregunta = "dias"
                self._agregar_mensaje_sistema(f"Sobre '{self.sintoma_actual_evaluando['nombre']}': ¿Hace cuántos días comenzó esta molestia?")

        else:
            self.sintoma_actual_evaluando = None
            self._actualizar_orientacion_ui()
            self._agregar_mensaje_sistema("Evaluación sintomática actualizada. Puedes agregar más malestares o presionar 'Finalizar Consulta'.")

    def _guardar_detalle_sintoma(self, respuesta):
        tipo_preg = self.sintoma_actual_evaluando.get("tipo_preguntas", "normales")
        peso_b = self.sintoma_actual_evaluando.get("peso_base", 1)

        if self.estado_pregunta == "dias":
            try:
                self.temp_dias = int(respuesta)
            except ValueError:
                self.temp_dias = 1

            if tipo_preg == "solo_duracion":
                self.engine.agregar_sintoma_detalle(
                    id_sintoma=self.sintoma_actual_evaluando["id"],
                    nombre=self.sintoma_actual_evaluando["nombre"],
                    peso_base=peso_b,
                    duracion=self.temp_dias,
                    intensidad=5,
                    es_constante=True
                )
                self._iniciar_siguiente_pregunta()
            else:
                self.estado_pregunta = "intensidad"
                self._agregar_mensaje_sistema(f"En una escala del 1 al 10, ¿qué tan fuerte es la molestia de '{self.sintoma_actual_evaluando['nombre']}'?")

        elif self.estado_pregunta == "intensidad":
            try:
                self.temp_intensidad = int(respuesta)
            except ValueError:
                self.temp_intensidad = 5

            dias_final = getattr(self, "temp_dias", 1) if tipo_preg != "solo_intensidad" else 1

            self.engine.agregar_sintoma_detalle(
                id_sintoma=self.sintoma_actual_evaluando["id"],
                nombre=self.sintoma_actual_evaluando["nombre"],
                peso_base=peso_b,
                duracion=dias_final,
                intensidad=self.temp_intensidad,
                es_constante=True
            )
            self._iniciar_siguiente_pregunta()

    def _actualizar_orientacion_ui(self):
        resultados = self.engine.calcular_orientacion()
        
        if not resultados or resultados[0].datos_insuficientes:
            msj_error = resultados[0].mensaje_sistema if resultados else "No se identificó un cuadro específico."
            
            self.lbl_canalizacion.config(text="Canalización Sugerida: Consulta con Médico General")
            self.txt_recom.delete("1.0", tk.END)
            self.txt_recom.insert(tk.END, msj_error)
            
            self.txt_flags.delete("1.0", tk.END)
            self.txt_flags.insert(tk.END, "Si los síntomas persisten, empeoran o se combinan con malestar general, acuda a consulta médica presencial.")
            
            self.txt_medicos.delete("1.0", tk.END)
            self.txt_medicos.insert(tk.END, self._obtener_medicos_zmg("Médico General"))

            self.btn_descargar.config(state=tk.DISABLED)
            return

        top = resultados[0]
        canalizacion_str = top.obtener_canalizacion()

        self.lbl_canalizacion.config(text=f"Canalización Sugerida: {canalizacion_str}")
        
        self.txt_recom.delete("1.0", tk.END)
        self.txt_recom.insert(tk.END, top.cuadro_clinico.recomendaciones)

        self.txt_flags.delete("1.0", tk.END)
        self.txt_flags.insert(tk.END, top.cuadro_clinico.banderas_rojas)

        self.txt_medicos.delete("1.0", tk.END)
        self.txt_medicos.insert(tk.END, self._obtener_medicos_zmg(canalizacion_str, top.es_alerta_critica))

        self.btn_descargar.config(state=tk.NORMAL)

        nom = self.entry_nombre.get().strip() or "Paciente"
        try:
            ed = int(self.entry_edad.get())
        except ValueError:
            ed = 22

        self.db.guardar_consulta(nom, ed, top.ics, canalizacion_str)

    def _finalizar_consulta(self):
        self.consulta_finalizada = True
        self._actualizar_orientacion_ui()
        self._agregar_mensaje_sistema("La consulta ha finalizado. Puedes descargar la Ficha de Orientación Sintomática en PDF en el panel derecho.")

    def _descargar_informe_pdf(self):
        resultados = self.engine.calcular_orientacion()
        if not resultados or resultados[0].datos_insuficientes:
            messagebox.showwarning("Atención", "No se puede generar la ficha PDF por datos sintomáticos ambiguos o insuficientes.")
            return

        top = resultados[0]
        nombre = self.entry_nombre.get().strip() or "Paciente Anónimo"
        edad = self.entry_edad.get().strip() or "N/A"
        fecha_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        canalizacion_str = top.obtener_canalizacion()

        ruta_archivo = filedialog.asksaveasfilename(
            defaultextension=".pdf",
            filetypes=[("Documentos PDF", "*.pdf"), ("Todos los archivos", "*.*")],
            initialfile=f"Ficha_Orientacion_SITRAMED_{nombre.replace(' ', '_')}.pdf",
            title="Guardar Ficha de Orientación PDF"
        )

        if not ruta_archivo:
            return

        try:
            from reportlab.lib.pagesizes import letter
            from reportlab.pdfgen import canvas
            
            c = canvas.Canvas(ruta_archivo, pagesize=letter)
            width, height = letter

            # ENCABEZADO INSTITUCIONAL
            c.setFillColorRGB(0.11, 0.22, 0.54)
            c.rect(0, height - 70, width, 70, fill=True, stroke=False)
            
            c.setFillColorRGB(1, 1, 1)
            c.setFont("Helvetica-Bold", 14)
            c.drawString(35, height - 35, "SITRAMED - FICHA DE ORIENTACIÓN SINTOMÁTICA")
            c.setFont("Helvetica", 9)
            c.drawString(35, height - 52, f"Fecha de Consulta: {fecha_str} | Protocolo Determinista ICOM")

            # DATOS DEL PACIENTE
            c.setFillColorRGB(0.1, 0.1, 0.1)
            c.setFont("Helvetica-Bold", 10)
            c.drawString(35, height - 90, "1. DATOS DEL PACIENTE")
            
            c.setFont("Helvetica", 9)
            c.drawString(45, height - 105, f"Nombre Completo: {nombre}")
            c.drawString(320, height - 105, f"Edad: {edad} años")

            # ANAMNESIS
            c.setFont("Helvetica-Bold", 10)
            c.drawString(35, height - 125, "2. SÍNTOMAS REGISTRADOS (ANAMNESIS)")

            y = height - 140
            c.setFont("Helvetica", 8)
            for idx, s in enumerate(self.engine.sintomas_evaluados, 1):
                c.drawString(45, y, f"• [{idx}] {s.nombre} — Duración: {s.duracion_dias} día(s) | Intensidad: {s.intensidad}/10")
                y -= 13

            # EVALUACIÓN DETERMINISTA Y CANALIZACIÓN
            y -= 5
            c.setFont("Helvetica-Bold", 10)
            c.drawString(35, y, "3. CANALIZACIÓN MÉDICA SUGERIDA")
            
            y -= 16
            c.setFont("Helvetica-Bold", 10)
            c.setFillColorRGB(0.14, 0.38, 0.92)
            c.drawString(45, y, f"Canalización Sugerida: {canalizacion_str}")

            # RECOMENDACIONES
            c.setFillColorRGB(0.1, 0.1, 0.1)
            y -= 22
            c.setFont("Helvetica-Bold", 10)
            c.drawString(35, y, "4. RECOMENDACIONES Y CUIDADOS GENERALES (NO FARMACOLÓGICOS)")
            
            y -= 15
            c.setFont("Helvetica", 8)
            recom_texto = top.cuadro_clinico.recomendaciones
            for line_bloque in recom_texto.split('\n'):
                if line_bloque.strip():
                    sub_lineas = [line_bloque[i:i+90] for i in range(0, len(line_bloque), 90)]
                    for sub in sub_lineas:
                        c.drawString(45, y, sub)
                        y -= 11
                else:
                    y -= 4

            # BANDERAS ROJAS / SIGNOS DE ALERTA
            y -= 8
            c.setFillColorRGB(0.8, 0.1, 0.1)
            c.setFont("Helvetica-Bold", 10)
            c.drawString(35, y, "5. SIGNOS DE ALERTA Y FACTORES POR EDAD (BANDERAS ROJAS)")
            
            y -= 15
            c.setFillColorRGB(0.2, 0.2, 0.2)
            c.setFont("Helvetica", 8)
            flags_texto = top.cuadro_clinico.banderas_rojas
            for line_bloque in flags_texto.split('\n'):
                if line_bloque.strip():
                    sub_lineas = [line_bloque[i:i+90] for i in range(0, len(line_bloque), 90)]
                    for sub in sub_lineas:
                        c.drawString(45, y, sub)
                        y -= 11
                else:
                    y -= 4

            # DIRECTORIO LOCAL GUADALAJARA
            y -= 8
            c.setFillColorRGB(0.02, 0.47, 0.34)
            c.setFont("Helvetica-Bold", 10)
            c.drawString(35, y, "6. CENTROS DE ATENCIÓN REFERENCIADOS (ZMG GUADALAJARA)")
            
            y -= 15
            c.setFillColorRGB(0.1, 0.1, 0.1)
            c.setFont("Helvetica", 8)
            medicos_texto = self._obtener_medicos_zmg(canalizacion_str, top.es_alerta_critica)
            for line_med in medicos_texto.split('\n'):
                if line_med.strip():
                    c.drawString(45, y, line_med.strip())
                    y -= 11
                else:
                    y -= 4

            # AVISO LEGAL
            c.setFillColorRGB(0.7, 0.1, 0.1)
            c.setFont("Helvetica-Bold", 8)
            c.drawString(35, 38, "AVISO DE EXENCIÓN DE RESPONSABILIDAD MÉDICA:")
            c.setFillColorRGB(0.3, 0.3, 0.3)
            c.setFont("Helvetica", 7)
            c.drawString(35, 27, "Este documento es una ficha de orientación preliminar generada por un prototipo de software académico (SITRAMED).")
            c.drawString(35, 18, "No constituye un diagnóstico ni una prescripción formal. Ante cualquier duda o persistencia, acuda a consulta médica.")

            c.save()
            messagebox.showinfo("Éxito", f"Ficha de Orientación en PDF guardada exitosamente en:\n{ruta_archivo}")

        except Exception as e:
            messagebox.showerror("Error", f"No se pudo generar la ficha en PDF: {str(e)}")
