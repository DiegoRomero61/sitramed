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
        self.root.geometry("1000x720")
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

    def _crear_interfaz(self):
        header = tk.Frame(self.root, bg="#1E3A8A", height=60)
        header.pack(fill=tk.X, side=tk.TOP)
        lbl_titulo = tk.Label(header, text="SITRAMED | Asistente Local de Triaje Sintomático", 
                              font=("Segoe UI", 15, "bold"), fg="white", bg="#1E3A8A")
        lbl_titulo.pack(pady=15, padx=20, side=tk.LEFT)

        main_container = tk.Frame(self.root, bg="#F0F4F8")
        main_container.pack(fill=tk.BOTH, expand=True, padx=15, pady=15)

        # --- COLUMNA DERECHA: Reporte Clínico ---
        col_derecha = tk.LabelFrame(main_container, text=" Ficha de Orientación ", font=("Segoe UI", 10, "bold"), 
                                    bg="white", fg="#1E293B", padx=15, pady=15, width=380)
        col_derecha.pack(side=tk.RIGHT, fill=tk.Y, padx=(10, 0))
        col_derecha.pack_propagate(False)

        self.lbl_riesgo = tk.Label(col_derecha, text="Nivel de Riesgo: --", font=("Segoe UI", 10, "bold"), bg="white", fg="#334155")
        self.lbl_riesgo.pack(anchor="w", pady=(5, 5))

        self.lbl_canalizacion = tk.Label(col_derecha, text="Canalización: --", font=("Segoe UI", 9, "bold"), fg="#2563EB", bg="white")
        self.lbl_canalizacion.pack(anchor="w", pady=2)

        tk.Label(col_derecha, text="Recomendaciones y Cuidados:", font=("Segoe UI", 9, "bold"), bg="white", fg="#1E293B").pack(anchor="w", pady=(10, 2))
        self.txt_recom = tk.Text(col_derecha, font=("Segoe UI", 8), wrap=tk.WORD, bg="#F8FAFC", relief=tk.FLAT, height=6)
        self.txt_recom.pack(fill=tk.X, pady=(0, 5))

        tk.Label(col_derecha, text="🚨 Signos de Alerta / Banderas Rojas:", font=("Segoe UI", 9, "bold"), bg="white", fg="#DC2626").pack(anchor="w", pady=(5, 2))
        self.txt_flags = tk.Text(col_derecha, font=("Segoe UI", 8), wrap=tk.WORD, bg="#FEF2F2", fg="#991B1B", relief=tk.FLAT, height=6)
        self.txt_flags.pack(fill=tk.BOTH, expand=True, pady=(0, 10))

        self.btn_descargar = tk.Button(col_derecha, text="📥 Descargar Ficha en PDF", font=("Segoe UI", 9, "bold"),
                                       bg="#2563EB", fg="white", relief=tk.FLAT, state=tk.DISABLED,
                                       command=self._descargar_informe_pdf)
        self.btn_descargar.pack(fill=tk.X, ipady=7)

        # --- COLUMNA IZQUIERDA: Interacción / Conversación ---
        col_izquierda = tk.LabelFrame(main_container, text=" Registro de Consulta ", font=("Segoe UI", 10, "bold"), 
                                      bg="white", fg="#1E293B", padx=15, pady=15)
        col_izquierda.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        frame_paciente = tk.Frame(col_izquierda, bg="white")
        frame_paciente.pack(fill=tk.X, pady=(0, 10))

        tk.Label(frame_paciente, text="Nombre Paciente:", bg="white", font=("Segoe UI", 9, "bold"), fg="#475569").grid(row=0, column=0, sticky="w")
        self.entry_nombre = tk.Entry(frame_paciente, font=("Segoe UI", 9), width=22, relief=tk.SOLID, bd=1)
        self.entry_nombre.insert(0, "Jose Diego Romero")
        self.entry_nombre.grid(row=0, column=1, padx=5, pady=2)

        tk.Label(frame_paciente, text="Edad:", bg="white", font=("Segoe UI", 9, "bold"), fg="#475569").grid(row=0, column=2, sticky="w", padx=(10, 0))
        self.entry_edad = tk.Entry(frame_paciente, font=("Segoe UI", 9), width=5, relief=tk.SOLID, bd=1)
        self.entry_edad.insert(0, "22")
        self.entry_edad.grid(row=0, column=3, padx=5, pady=2)

        frame_chat_container = tk.Frame(col_izquierda, bg="#F1F5F9", bd=1, relief=tk.SOLID)
        frame_chat_container.pack(fill=tk.BOTH, expand=True, pady=10)

        self.txt_chat = tk.Text(frame_chat_container, state=tk.DISABLED, wrap=tk.WORD, font=("Segoe UI", 10),
                                bg="#F1F5F9", relief=tk.FLAT, padx=10, pady=10)
        self.txt_chat.pack(fill=tk.BOTH, expand=True)

        self.txt_chat.tag_config("bienvenida", font=("Segoe UI", 14, "bold"), foreground="#1E3A8A", justify="center")
        self.txt_chat.tag_config("sub_bienvenida", font=("Segoe UI", 9), foreground="#64748B", justify="center")
        self.txt_chat.tag_config("bot_msg", font=("Segoe UI", 9, "bold"), foreground="#1E293B", background="#E2E8F0", lmargin1=10, lmargin2=15, rmargin=50, spacing1=4, spacing3=4)
        self.txt_chat.tag_config("user_msg", font=("Segoe UI", 9, "bold"), foreground="white", background="#2563EB", justify="right", rmargin=10, lmargin1=100, spacing1=4, spacing3=4)

        frame_input = tk.Frame(col_izquierda, bg="white")
        frame_input.pack(fill=tk.X, pady=(5, 0))

        self.entry_usuario = tk.Entry(frame_input, font=("Segoe UI", 10), relief=tk.SOLID, bd=1)
        self.entry_usuario.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 5), ipady=6)
        self.entry_usuario.bind("<Return>", lambda event: self._procesar_entrada())

        btn_enviar = tk.Button(frame_input, text="Enviar", font=("Segoe UI", 9, "bold"), bg="#2563EB", fg="white", 
                               relief=tk.FLAT, padx=12, command=self._procesar_entrada)
        btn_enviar.pack(side=tk.LEFT, padx=(0, 5))

        btn_finalizar = tk.Button(frame_input, text="Finalizar Consulta", font=("Segoe UI", 9, "bold"), bg="#DC2626", fg="white", 
                                  relief=tk.FLAT, padx=12, command=self._finalizar_consulta)
        btn_finalizar.pack(side=tk.RIGHT)

        self._mostrar_saludo_inicial()

    def _mostrar_saludo_inicial(self):
        self.txt_chat.config(state=tk.NORMAL)
        self.txt_chat.delete("1.0", tk.END)
        self.txt_chat.insert(tk.END, "\n¿Qué síntomas sientes hoy?\n", "bienvenida")
        self.txt_chat.insert(tk.END, "Describe libremente lo que te pasa (ej. 'tengo tos y fiebre'):\n\n", "sub_bienvenida")
        self.txt_chat.see(tk.END)
        self.txt_chat.config(state=tk.DISABLED)

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
            messagebox.showinfo("Consulta Finalizada", "Esta consulta ya ha sido cerrada. Reinicia para evaluar un nuevo caso.")
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
            self._agregar_mensaje_sistema("No logré identificar síntomas claros. Por favor describe tu molestia nuevamente.")
        else:
            self.sintomas_pendientes_preguntas.extend(detectados)
            for s in detectados:
                self.sintomas_registrados_ids.add(s["id"])
            self._iniciar_siguiente_pregunta()

    def _iniciar_siguiente_pregunta(self):
        if self.sintomas_pendientes_preguntas:
            self.sintoma_actual_evaluando = self.sintomas_pendientes_preguntas.pop(0)
            tipo_preg = self.sintoma_actual_evaluando.get("tipo_preguntas", "normales")

            if tipo_preg == "directo":
                self.engine.agregar_sintoma_detalle(
                    id_sintoma=self.sintoma_actual_evaluando["id"],
                    nombre=self.sintoma_actual_evaluando["nombre"],
                    duracion=1,
                    intensidad=5,
                    es_constante=True
                )
                self._agregar_mensaje_sistema(f"Registrado síntoma de atención inmediata: '{self.sintoma_actual_evaluando['nombre']}'. Generando canalización...")
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
            self._actualizar_diagnostico_ui()
            self._agregar_mensaje_sistema("Evaluación sintomática actualizada. Puedes agregar más malestares o presionar 'Finalizar Consulta'.")

    def _guardar_detalle_sintoma(self, respuesta):
        tipo_preg = self.sintoma_actual_evaluando.get("tipo_preguntas", "normales")

        if self.estado_pregunta == "dias":
            try:
                self.temp_dias = int(respuesta)
            except ValueError:
                self.temp_dias = 1

            if tipo_preg == "solo_duracion":
                self.engine.agregar_sintoma_detalle(
                    id_sintoma=self.sintoma_actual_evaluando["id"],
                    nombre=self.sintoma_actual_evaluando["nombre"],
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
                duracion=dias_final,
                intensidad=self.temp_intensidad,
                es_constante=True
            )
            self._iniciar_siguiente_pregunta()

    def _actualizar_diagnostico_ui(self):
        resultados = self.engine.calcular_diagnosticos()
        
        if not resultados:
            self.lbl_riesgo.config(text="Nivel de Riesgo: Bajo / No determinado")
            self.lbl_canalizacion.config(text="Canalización: Monitoreo o Consulta General")
            self.txt_recom.delete("1.0", tk.END)
            self.txt_recom.insert(tk.END, "Información sintomática insuficiente. Se recomienda monitorear la evolución o consultar a un profesional de la salud.")
            self.txt_flags.delete("1.0", tk.END)
            self.txt_flags.insert(tk.END, "Sin banderas rojas inmediatas detectadas.")
            self.btn_descargar.config(state=tk.DISABLED)
            return

        top = resultados[0]
        
        self.lbl_riesgo.config(text=f"Nivel de Riesgo: {top.enfermedad.nivel_riesgo}")
        self.lbl_canalizacion.config(text=f"Canalización Sugerida: {top.enfermedad.canalizacion}")
        
        self.txt_recom.delete("1.0", tk.END)
        self.txt_recom.insert(tk.END, top.enfermedad.recomendaciones)

        self.txt_flags.delete("1.0", tk.END)
        self.txt_flags.insert(tk.END, top.enfermedad.banderas_rojas)

        self.btn_descargar.config(state=tk.NORMAL)

        nom = self.entry_nombre.get().strip() or "Paciente"
        try:
            ed = int(self.entry_edad.get())
        except ValueError:
            ed = 22

        self.db.guardar_consulta(nom, ed, top.enfermedad.nivel_riesgo, 100, top.enfermedad.canalizacion)

    def _finalizar_consulta(self):
        self.consulta_finalizada = True
        self._actualizar_diagnostico_ui()
        self._agregar_mensaje_sistema("La consulta ha sido cerrada formalmente. Puedes descargar la Ficha de Orientación en PDF en el panel derecho.")

    def _descargar_informe_pdf(self):
        resultados = self.engine.calcular_diagnosticos()
        if not resultados:
            messagebox.showwarning("Atención", "No se puede generar informe para información sintomática insuficiente.")
            return

        top = resultados[0]
        nombre = self.entry_nombre.get().strip() or "Paciente Anónimo"
        edad = self.entry_edad.get().strip() or "N/A"
        fecha_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

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
            c.rect(0, height - 80, width, 80, fill=True, stroke=False)
            
            c.setFillColorRGB(1, 1, 1)
            c.setFont("Helvetica-Bold", 15)
            c.drawString(40, height - 40, "SITRAMED - FICHA DE ORIENTACIÓN SINTOMÁTICA")
            c.setFont("Helvetica", 9)
            c.drawString(40, height - 58, f"Fecha de Consulta: {fecha_str} | Protocolo de Triaje ICOM")

            # DATOS DEL PACIENTE
            c.setFillColorRGB(0.1, 0.1, 0.1)
            c.setFont("Helvetica-Bold", 11)
            c.drawString(40, height - 110, "1. DATOS DEL PACIENTE")
            
            c.setFont("Helvetica", 10)
            c.drawString(50, height - 128, f"Nombre Completo: {nombre}")
            c.drawString(320, height - 128, f"Edad: {edad} años")

            # ANAMNESIS
            c.setFont("Helvetica-Bold", 11)
            c.drawString(40, height - 155, "2. SÍNTOMAS REGISTRADOS (ANAMNESIS)")

            y = height - 175
            c.setFont("Helvetica", 9)
            for idx, s in enumerate(self.engine.sintomas_evaluados, 1):
                c.drawString(50, y, f"• [{idx}] {s.nombre} — Duración: {s.duracion_dias} día(s) | Intensidad: {s.intensidad}/10")
                y -= 16

            # EVALUACIÓN Y CANALIZACIÓN
            y -= 10
            c.setFont("Helvetica-Bold", 11)
            c.drawString(40, y, "3. NIVEL DE RIESGO Y CANALIZACIÓN MÉDICA")
            
            y -= 20
            c.setFont("Helvetica", 10)
            c.drawString(50, y, f"Nivel de Riesgo Clínico: {top.enfermedad.nivel_riesgo}")
            
            y -= 18
            c.setFont("Helvetica-Bold", 10)
            c.setFillColorRGB(0.14, 0.38, 0.92)
            c.drawString(50, y, f"Canalización Sugerida: {top.enfermedad.canalizacion}")

            # RECOMENDACIONES
            c.setFillColorRGB(0.1, 0.1, 0.1)
            y -= 25
            c.setFont("Helvetica-Bold", 11)
            c.drawString(40, y, "4. RECOMENDACIONES Y CUIDADOS GENERALES")
            
            y -= 18
            c.setFont("Helvetica", 9)
            recom_lineas = [top.enfermedad.recomendaciones[i:i+85] for i in range(0, len(top.enfermedad.recomendaciones), 85)]
            for line in recom_lineas:
                c.drawString(50, y, line)
                y -= 14

            # BANDERAS ROJAS / SIGNOS DE ALERTA
            y -= 10
            c.setFillColorRGB(0.8, 0.1, 0.1)
            c.setFont("Helvetica-Bold", 11)
            c.drawString(40, y, "5. SIGNOS DE ALERTA (BANDERAS ROJAS)")
            
            y -= 18
            c.setFillColorRGB(0.2, 0.2, 0.2)
            c.setFont("Helvetica", 9)
            flags_lineas = [top.enfermedad.banderas_rojas[i:i+85] for i in range(0, len(top.enfermedad.banderas_rojas), 85)]
            for line in flags_lineas:
                c.drawString(50, y, line)
                y -= 14

            # AVISO LEGAL
            c.setFillColorRGB(0.7, 0.1, 0.1)
            c.setFont("Helvetica-Bold", 8)
            c.drawString(40, 45, "AVISO DE EXENCIÓN DE RESPONSABILIDAD MÉDICA:")
            c.setFillColorRGB(0.3, 0.3, 0.3)
            c.setFont("Helvetica", 7)
            c.drawString(40, 33, "Este documento es una ficha de orientación preliminar generada por un prototipo de software académico (SITRAMED).")
            c.drawString(40, 23, "No constituye un diagnóstico ni una prescripción formal. Ante cualquier duda o persistencia, acuda a consulta médica.")

            c.save()
            messagebox.showinfo("Éxito", f"Ficha de Orientación en PDF guardada exitosamente en:\n{ruta_archivo}")

        except Exception as e:
            messagebox.showerror("Error", f"No se pudo generar la ficha en PDF: {str(e)}")