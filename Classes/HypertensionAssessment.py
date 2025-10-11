from datetime import datetime
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QFormLayout, QGroupBox,
    QLabel, QSpinBox, QDoubleSpinBox, QCheckBox, QPushButton,
    QPlainTextEdit, QHBoxLayout, QLineEdit, QScrollArea,
    QComboBox, QMessageBox,
    QFrame
)
from PyQt5.QtGui import QFont
from PyQt5.QtCore import Qt
import os
from google import genai
from google.genai import types
from Classes.MedicalReportPDFWriter import MedicalReportPDFWriter

class HypertensionAssessment(QWidget):
    def __init__(self, db_manager, user):
        super().__init__()
        self.db_manager = db_manager
        self.user = user
        self.init_ui()

    def calculate_age(self, birth_date):
        """Calcula idade a partir da data de nascimento"""
        if not birth_date:
            return 0
        today = datetime.now()
        age = today.year - birth_date.year - ((today.month, today.day) < (birth_date.month, birth_date.day))
        return age

    def init_ui(self):
        # Aplicar estilo geral (mantém o mesmo)
        self.setStyleSheet("""
            QWidget {
                font-family: 'Segoe UI', Arial, sans-serif;
                font-size: 10pt;
                background-color: #f8f9fa;
            }
            
            QGroupBox {
                font-weight: bold;
                font-size: 11pt;
                color: #2c3e50;
                border: 2px solid #bdc3c7;
                border-radius: 12px;
                margin-top: 15px;
                padding-top: 10px;
                background-color: white;
            }
            
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 15px;
                padding: 5px 10px;
                background-color: #3498db;
                color: white;
                border-radius: 8px;
                font-weight: bold;
            }
            
            QLabel {
                color: #34495e;
                font-weight: 500;
                padding: 2px;
            }
            
            QSpinBox, QDoubleSpinBox, QComboBox, QLineEdit {
                border: 2px solid #bdc3c7;
                border-radius: 6px;
                padding: 8px 12px;
                background-color: white;
                font-size: 10pt;
                min-height: 20px;
            }
            
            QSpinBox:focus, QDoubleSpinBox:focus, QComboBox:focus, QLineEdit:focus {
                border-color: #3498db;
                outline: none;
            }
            
            QSpinBox:hover, QDoubleSpinBox:hover, QComboBox:hover {
                border-color: #5dade2;
            }
            
            QCheckBox {
                spacing: 8px;
                font-weight: 500;
                color: #34495e;
            }
            
            QCheckBox::indicator {
                width: 18px;
                height: 18px;
                border: 2px solid #bdc3c7;
                border-radius: 4px;
                background-color: white;
            }
            
            QCheckBox::indicator:checked {
                background-color: #27ae60;
                border-color: #27ae60;
                image: url(data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iMTYiIGhlaWdodD0iMTYiIHZpZXdCb3g9IjAgMCAxNiAxNiIgZmlsbD0ibm9uZSIgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIj4KPHBhdGggZD0iTTEzLjMzMzMgNC42NjY2N0w2IDEyTDIuNjY2NjcgOC42NjY2N0w0LjA4IDcuMjUzMzNMNiA5LjE3MzMzTDExLjkyIDMuMjUzMzNMMTMuMzMzMyA0LjY2NjY3WiIgZmlsbD0id2hpdGUiLz4KICA8L3N2Zz4K);
            }
            
            QCheckBox::indicator:hover {
                border-color: #5dade2;
            }
            
            QPushButton {
                background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                                          stop: 0 #3498db, stop: 1 #2980b9);
                border: none;
                color: white;
                padding: 12px 24px;
                font-size: 11pt;
                font-weight: bold;
                border-radius: 8px;
                min-height: 20px;
                min-width: 120px;
            }
            
            QPushButton:hover {
                background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                                          stop: 0 #5dade2, stop: 1 #3498db);
            }
            
            QPushButton:pressed {
                background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                                          stop: 0 #2980b9, stop: 1 #21618c);
            }
            
            QPushButton:disabled {
                background: #95a5a6;
                color: #ecf0f1;
            }
            
            QPushButton#btn_salvar {
                background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                                          stop: 0 #27ae60, stop: 1 #229954);
            }
            
            QPushButton#btn_salvar:hover {
                background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                                          stop: 0 #58d68d, stop: 1 #27ae60);
            }
            
            QPushButton#btn_pdf {
                background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                                          stop: 0 #e74c3c, stop: 1 #c0392b);
            }
            
            QPushButton#btn_pdf:hover {
                background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                                          stop: 0 #ec7063, stop: 1 #e74c3c);
            }
            
            QPlainTextEdit {
                border: 2px solid #bdc3c7;
                border-radius: 8px;
                background-color: white;
                padding: 12px;
                font-family: 'Consolas', 'Monaco', monospace;
                font-size: 10pt;
                line-height: 1.4;
            }
            
            QScrollArea {
                border: none;
                background-color: #f8f9fa;
            }
            
            QScrollBar:vertical {
                border: none;
                background: #ecf0f1;
                width: 12px;
                border-radius: 6px;
            }
            
            QScrollBar::handle:vertical {
                background: #bdc3c7;
                border-radius: 6px;
                min-height: 30px;
            }
            
            QScrollBar::handle:vertical:hover {
                background: #95a5a6;
            }
            
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
                border: none;
                background: none;
                height: 0px;
            }
        """)

        # Widget de conteúdo para scroll
        content = QWidget()
        content_layout = QVBoxLayout(content)
        content_layout.setContentsMargins(25, 25, 25, 25)
        content_layout.setSpacing(20)

        # Título principal
        title_label = QLabel("🩺 Avaliação de Hipertensão")
        title_label.setFont(QFont("Segoe UI", 16, QFont.Bold))
        title_label.setStyleSheet("""
            QLabel {
                color: #2c3e50;
                padding: 15px 0px;
                border-bottom: 3px solid #3498db;
                margin-bottom: 10px;
            }
        """)
        title_label.setAlignment(Qt.AlignCenter)
        content_layout.addWidget(title_label)

        # Seleção de paciente (apenas para médicos)
        if self.user["user_type"] == "doctor":
            patient_group = QGroupBox("👤 Seleção de Paciente")
            patient_layout = QFormLayout()
            patient_layout.setSpacing(10)
            patient_layout.setFieldGrowthPolicy(QFormLayout.ExpandingFieldsGrow)

            self.patient_combo = QComboBox()
            self.patient_combo.setMinimumHeight(35)
            # Não conecta o sinal ainda - será feito após criar todos os campos
            self.load_patients()
            
            # Label personalizado para o paciente
            patient_label = QLabel("Selecionar Paciente:")
            patient_label.setStyleSheet("font-weight: bold; color: #34495e;")
            
            patient_layout.addRow(patient_label, self.patient_combo)
            patient_group.setLayout(patient_layout)
            content_layout.addWidget(patient_group)

        # --- Avaliação Ágil ---
        auto_gbox = QGroupBox("📝 Avaliação Ágil")
        auto_form = QFormLayout()
        auto_form.setSpacing(15)
        auto_form.setFieldGrowthPolicy(QFormLayout.ExpandingFieldsGrow)

        # Idade (calculada, read-only)
        self.idade = QLineEdit()
        self.idade.setReadOnly(True)
        self.idade.setStyleSheet("""
            QLineEdit[readOnly="true"] {
                background-color: #ecf0f1;
                color: #2c3e50;
                font-weight: bold;
            }
        """)
        self.idade.setMinimumHeight(35)
        self.idade.setPlaceholderText("Calculada automaticamente")
        auto_form.addRow(self.create_bold_label("Idade:"), self.idade)

        self.sexo_m = QCheckBox("Masculino")
        self.sexo_m.setStyleSheet("QCheckBox { font-weight: bold; }")
        auto_form.addRow(self.create_bold_label("Sexo:"), self.sexo_m)

        self.hist_fam = QCheckBox("Sim")
        auto_form.addRow(self.create_bold_label("Histórico familiar de hipertensão:"), self.hist_fam)

        # Medidas físicas
        measures_frame = QFrame()
        measures_layout = QHBoxLayout(measures_frame)
        measures_layout.setSpacing(10)
        
        self.altura = QDoubleSpinBox()
        self.altura.setRange(50, 250)
        self.altura.setSuffix(" cm")
        self.altura.setMinimumHeight(35)
        
        self.peso = QDoubleSpinBox()
        self.peso.setRange(10, 300)
        self.peso.setDecimals(1)
        self.peso.setSuffix(" kg")
        self.peso.setMinimumHeight(35)
        
        self.imc = QLineEdit()
        self.imc.setReadOnly(True)
        self.imc.setStyleSheet("""
            QLineEdit[readOnly="true"] {
                background-color: #ecf0f1;
                color: #2c3e50;
                font-weight: bold;
            }
        """)
        self.imc.setMinimumHeight(35)
        
        measures_layout.addWidget(QLabel("Altura:"))
        measures_layout.addWidget(self.altura)
        measures_layout.addWidget(QLabel("Peso:"))
        measures_layout.addWidget(self.peso)
        measures_layout.addWidget(QLabel("IMC:"))
        measures_layout.addWidget(self.imc)
        
        auto_form.addRow(self.create_bold_label("Medidas Físicas:"), measures_frame)
        
        self.altura.valueChanged.connect(self.calcular_imc)
        self.peso.valueChanged.connect(self.calcular_imc)

        # Hábitos alimentares e exercícios
        self.frutas = QSpinBox()
        self.frutas.setRange(0, 20)
        self.frutas.setSuffix(" porções/dia")
        self.frutas.setMinimumHeight(35)
        auto_form.addRow(self.create_bold_label("Frutas/Vegetais por dia:"), self.frutas)

        self.exercicio = QSpinBox()
        self.exercicio.setRange(0, 10000)
        self.exercicio.setSuffix(" min/semana")
        self.exercicio.setMinimumHeight(35)
        auto_form.addRow(self.create_bold_label("Exercício por semana:"), self.exercicio)

        # Vícios e estilo de vida
        self.fuma = QCheckBox("Sim")
        auto_form.addRow(self.create_bold_label("Fumante:"), self.fuma)

        self.alcool = QSpinBox()
        self.alcool.setRange(0, 100)
        self.alcool.setSuffix(" doses/semana")
        self.alcool.setMinimumHeight(35)
        auto_form.addRow(self.create_bold_label("Bebidas alcoólicas:"), self.alcool)

        self.estresse = QSpinBox()
        self.estresse.setRange(0, 10)
        self.estresse.setSuffix(" (0=baixo, 10=alto)")
        self.estresse.setMinimumHeight(35)
        auto_form.addRow(self.create_bold_label("Nível de estresse:"), self.estresse)

        self.sono = QCheckBox("Sim")
        auto_form.addRow(self.create_bold_label("Qualidade do sono ruim:"), self.sono)

        auto_gbox.setLayout(auto_form)
        content_layout.addWidget(auto_gbox)

        # --- Exames Médicos opcionais ---
        self.chk_exames = QCheckBox("🩺 Possui dados de exames médicos?")
        self.chk_exames.setStyleSheet("""
            QCheckBox {
                font-size: 12pt;
                font-weight: bold;
                color: #2c3e50;
                padding: 10px;
                background-color: white;
                border: 2px solid #3498db;
                border-radius: 8px;
            }
        """)
        self.chk_exames.stateChanged.connect(self.toggle_exames)
        content_layout.addWidget(self.chk_exames)

        self.exame_gbox = QGroupBox("🔬 Exames Médicos (Opcional)")
        exame_form = QFormLayout()
        exame_form.setSpacing(15)
        exame_form.setFieldGrowthPolicy(QFormLayout.ExpandingFieldsGrow)

        def make_spin(maxv, suffix="", decimal_places=1):
            sb = QDoubleSpinBox()
            sb.setRange(0, maxv)
            sb.setDecimals(decimal_places)
            sb.setSuffix(suffix)
            sb.setSpecialValueText("não informado")
            sb.setMinimumHeight(35)
            return sb

        # Colesterol
        cholesterol_frame = QFrame()
        cholesterol_layout = QHBoxLayout(cholesterol_frame)
        
        self.ldl = make_spin(500, " mg/dL")
        self.hdl = make_spin(200, " mg/dL")
        
        cholesterol_layout.addWidget(QLabel("LDL:"))
        cholesterol_layout.addWidget(self.ldl)
        cholesterol_layout.addWidget(QLabel("HDL:"))
        cholesterol_layout.addWidget(self.hdl)
        
        exame_form.addRow(self.create_bold_label("Colesterol:"), cholesterol_frame)

        # Outros exames de sangue
        self.trig = make_spin(1000, " mg/dL")
        exame_form.addRow(self.create_bold_label("Triglicerídeos:"), self.trig)

        glucose_frame = QFrame()
        glucose_layout = QHBoxLayout(glucose_frame)
        
        self.glic = make_spin(500, " mg/dL")
        self.hba1c = make_spin(20, " %")
        
        glucose_layout.addWidget(QLabel("Jejum:"))
        glucose_layout.addWidget(self.glic)
        glucose_layout.addWidget(QLabel("HbA1c:"))
        glucose_layout.addWidget(self.hba1c)
        
        exame_form.addRow(self.create_bold_label("Glicemia:"), glucose_frame)

        self.creat = make_spin(10, " mg/dL")
        exame_form.addRow(self.create_bold_label("Creatinina:"), self.creat)

        # Exames especiais
        self.protein = QCheckBox("Positiva")
        exame_form.addRow(self.create_bold_label("Proteinúria:"), self.protein)

        self.apneia = QCheckBox("Diagnosticada")
        exame_form.addRow(self.create_bold_label("Apneia do sono:"), self.apneia)

        self.cortisol = make_spin(100, " µg/dL")
        exame_form.addRow(self.create_bold_label("Cortisol sérico:"), self.cortisol)

        self.mutacao = QCheckBox("Presente")
        exame_form.addRow(self.create_bold_label("Mutação genética:"), self.mutacao)

        # Parâmetros físicos
        vitals_frame = QFrame()
        vitals_layout = QHBoxLayout(vitals_frame)
        
        self.bpm = make_spin(200, " bpm", 0)
        self.pm25 = make_spin(500, " µg/m³")
        
        vitals_layout.addWidget(QLabel("BPM repouso:"))
        vitals_layout.addWidget(self.bpm)
        vitals_layout.addWidget(QLabel("PM2.5:"))
        vitals_layout.addWidget(self.pm25)
        
        exame_form.addRow(self.create_bold_label("Parâmetros adicionais:"), vitals_frame)

        self.exame_gbox.setLayout(exame_form)
        content_layout.addWidget(self.exame_gbox)

        # --- Botões ---
        btns_container = QFrame()
        btns_container.setStyleSheet("""
            QFrame {
                background-color: white;
                border-radius: 12px;
                padding: 15px;
                border: 2px solid #bdc3c7;
            }
        """)
        btns = QHBoxLayout(btns_container)
        btns.setSpacing(15)

        self.btn_avaliar = QPushButton("🔍 Avaliar Hipertensão")
        self.btn_avaliar.clicked.connect(self.avaliar_hipertensao)
        self.btn_avaliar.setMinimumHeight(45)
        btns.addWidget(self.btn_avaliar)

        if self.user["user_type"] == "doctor":
            self.btn_salvar = QPushButton("💾 Salvar Relatório")
            self.btn_salvar.setObjectName("btn_salvar")
            self.btn_salvar.clicked.connect(self.salvar_relatorio)
            self.btn_salvar.setEnabled(False)
            self.btn_salvar.setMinimumHeight(45)
            btns.addWidget(self.btn_salvar)

        self.btn_pdf = QPushButton("📄 Gerar PDF")
        self.btn_pdf.setObjectName("btn_pdf")
        self.btn_pdf.clicked.connect(self.gerar_pdf)
        self.btn_pdf.setEnabled(False)
        self.btn_pdf.setMinimumHeight(45)
        btns.addWidget(self.btn_pdf)
        
        content_layout.addWidget(btns_container)

        # --- Resultado ---
        result_container = QFrame()
        result_container.setStyleSheet("""
            QFrame {
                background-color: white;
                border-radius: 12px;
                padding: 15px;
                border: 2px solid #bdc3c7;
            }
        """)
        result_layout = QVBoxLayout(result_container)
        
        lbl = QLabel("📊 Resultado da Avaliação")
        lbl.setFont(QFont("Segoe UI", 14, QFont.Bold))
        lbl.setStyleSheet("""
            QLabel {
                color: #2c3e50;
                padding: 10px 0px;
                border-bottom: 2px solid #3498db;
                margin-bottom: 15px;
            }
        """)
        result_layout.addWidget(lbl)
        
        self.result = QPlainTextEdit()
        self.result.setReadOnly(True)
        self.result.setMinimumHeight(250)
        self.result.setPlaceholderText("Os resultados da avaliação aparecerão aqui após clicar em 'Avaliar Hipertensão'...")
        result_layout.addWidget(self.result)
        
        content_layout.addWidget(result_container)

        # Scroll area
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setWidget(content)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        scroll.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)

        # Layout principal
        main = QVBoxLayout(self)
        main.setContentsMargins(0, 0, 0, 0)
        main.addWidget(scroll)

        # Oculta exames por padrão
        self.toggle_exames(0)
        self.last_assessment = None
        
        # Conecta o sinal do combo de pacientes APÓS criar todos os campos
        if self.user["user_type"] == "doctor":
            self.patient_combo.currentIndexChanged.connect(self.on_patient_changed)
        
        # Carrega dados iniciais
        self.load_initial_data()

    def create_bold_label(self, text):
        """Cria um label com estilo em negrito"""
        label = QLabel(text)
        label.setStyleSheet("font-weight: bold; color: #34495e;")
        return label

    def load_patients(self):
        """Carrega pacientes no combo box"""
        patients = self.db_manager.get_users_by_type("patient")
        self.patient_combo.clear()
        for patient in patients:
            self.patient_combo.addItem(patient["name"], patient["_id"])
    
    def on_patient_changed(self):
        """Chamado quando o paciente selecionado muda"""
        if self.user["user_type"] == "doctor":
            self.load_initial_data()
    
    def clear_form_fields(self):
        """Limpa todos os campos do formulário"""
        # Idade permanece (calculada da data de nascimento)
        
        # Campos de avaliação ágil
        self.sexo_m.setChecked(False)
        self.hist_fam.setChecked(False)
        self.altura.setValue(0)
        self.peso.setValue(0)
        self.imc.clear()
        self.frutas.setValue(0)
        self.exercicio.setValue(0)
        self.fuma.setChecked(False)
        self.alcool.setValue(0)
        self.estresse.setValue(0)
        self.sono.setChecked(False)
        
        # Campos de exames (sempre começam zerados)
        self.chk_exames.setChecked(False)
        self.ldl.setValue(0)
        self.hdl.setValue(0)
        self.trig.setValue(0)
        self.glic.setValue(0)
        self.hba1c.setValue(0)
        self.creat.setValue(0)
        self.protein.setChecked(False)
        self.apneia.setChecked(False)
        self.cortisol.setValue(0)
        self.mutacao.setChecked(False)
        self.bpm.setValue(0)
        self.pm25.setValue(0)
    
    def load_initial_data(self):
        """Carrega dados iniciais baseado no usuário ou paciente selecionado"""
        patient_id = None
        
        # Define qual paciente buscar
        if self.user["user_type"] == "patient":
            patient_id = self.user["_id"]
            patient_data = self.user
        elif self.user["user_type"] == "doctor" and hasattr(self, 'patient_combo'):
            patient_id = self.patient_combo.currentData()
            if patient_id:
                patient_data = self.db_manager.db.users.find_one({"_id": patient_id})
            else:
                return
        else:
            return
        
        # Calcula e exibe idade
        if patient_data and "birth_date" in patient_data:
            age = self.calculate_age(patient_data["birth_date"])
            self.idade.setText(f"{age} anos")
        else:
            self.idade.clear()
        
        # Busca último relatório do paciente
        if patient_id:
            last_report = self.db_manager.get_latest_patient_report(patient_id)
            
            if last_report and "report_data" in last_report:
                report_data = last_report["report_data"]
                input_data = report_data.get("input_data", {})
                
                # Verifica se existe autoavaliacao ou avaliacaoagil
                auto = input_data.get("autoavaliacao") or input_data.get("avaliacaoagil")
                
                if auto:
                    # Preenche campos de avaliação ágil
                    self.sexo_m.setChecked(auto.get("sexo_masculino", False))
                    self.hist_fam.setChecked(auto.get("historico_familiar_hipertensao", False))
                    
                    if auto.get("altura_cm"):
                        self.altura.setValue(auto["altura_cm"])
                    if auto.get("peso_kg"):
                        self.peso.setValue(auto["peso_kg"])
                    
                    self.frutas.setValue(auto.get("porcoes_frutas_vegetais_dia", 0))
                    self.exercicio.setValue(auto.get("minutos_exercicio_semana", 0))
                    self.fuma.setChecked(auto.get("fuma_atualmente", False))
                    self.alcool.setValue(auto.get("bebidas_alcoolicas_semana", 0))
                    self.estresse.setValue(auto.get("nivel_estresse_0_10", 0))
                    self.sono.setChecked(auto.get("sono_qualidade_ruim", False))
                else:
                    # Se não há dados no relatório, limpa os campos
                    self.clear_form_fields()
            else:
                # Se não há relatórios anteriores, limpa os campos
                self.clear_form_fields()
                
        # Não preenche exames médicos - eles devem ser inseridos a cada avaliação

    def calcular_imc(self):
        h = self.altura.value() / 100
        if h > 0:
            imc = self.peso.value() / (h * h)
            self.imc.setText(f"{imc:.1f}")
        else:
            self.imc.clear()

    def toggle_exames(self, estado):
        self.exame_gbox.setVisible(estado == Qt.Checked)

    def get_current_age(self):
        """Obtém idade do campo ou calcula"""
        idade_text = self.idade.text().replace(" anos", "").strip()
        try:
            return int(idade_text)
        except:
            return 0

    def avaliar_hipertensao(self):
        # Pega idade atual
        idade_atual = self.get_current_age()
        
        # Monta dados de Avaliação Agíl
        auto = {
            "idade_anos": idade_atual,
            "sexo_masculino": self.sexo_m.isChecked(),
            "historico_familiar_hipertensao": self.hist_fam.isChecked(),
            "altura_cm": self.altura.value(),
            "peso_kg": self.peso.value(),
            "imc": float(self.imc.text()) if self.imc.text() else None,
            "porcoes_frutas_vegetais_dia": self.frutas.value(),
            "minutos_exercicio_semana": self.exercicio.value(),
            "fuma_atualmente": self.fuma.isChecked(),
            "bebidas_alcoolicas_semana": self.alcool.value(),
            "nivel_estresse_0_10": self.estresse.value(),
            "sono_qualidade_ruim": self.sono.isChecked()
        }

        # Monta dados de exames (ou null)
        exames = None
        if self.chk_exames.isChecked():
            exames = {
                "colesterol_ldl_mg_dL":     None if self.ldl.value() == 0 else self.ldl.value(),
                "colesterol_hdl_mg_dL":     None if self.hdl.value() == 0 else self.hdl.value(),
                "triglicerideos_mg_dL":     None if self.trig.value() == 0 else self.trig.value(),
                "glicemia_jejum_mg_dL":     None if self.glic.value() == 0 else self.glic.value(),
                "hba1c_percent":            None if self.hba1c.value() == 0 else self.hba1c.value(),
                "creatinina_mg_dL":         None if self.creat.value() == 0 else self.creat.value(),
                "proteinuria_positiva":     self.protein.isChecked(),
                "diagnostico_apneia_sono":  self.apneia.isChecked(),
                "cortisol_serico_ug_dL":    None if self.cortisol.value() == 0 else self.cortisol.value(),
                "mutacao_genetica_hipertensao": self.mutacao.isChecked(),
                "bpm_repouso":              None if self.bpm.value() == 0 else self.bpm.value(),
                "indice_pm25":              None if self.pm25.value() == 0 else self.pm25.value()
            }

        # Assessment data
        assessment_data = {
            "avaliacaoagil": auto,
            "exames": exames,
            "timestamp": datetime.now().isoformat()
        }

        # Avaliação com IA
        resultado = self.ai_assessment(assessment_data)

        self.result.setPlainText(resultado)
        self.last_assessment = {
            "input_data": assessment_data,
            "ai_result": resultado
        }

        self.btn_pdf.setEnabled(True)
        if self.user["user_type"] == "doctor":
            self.btn_salvar.setEnabled(True)

    def simulate_ai_assessment(self, data):
        """Simula avaliação de IA - substitua pela integração real com Gemini"""
        auto = data["avaliacaoagil"]
        exames = data.get("exames")

        risk_factors = []
        score = 0

        # Análise de fatores de risco
        if auto["idade_anos"] > 40:
            risk_factors.append("Idade acima de 40 anos")
            score += 10

        if auto["sexo_masculino"]:
            risk_factors.append("Sexo masculino")
            score += 5

        if auto["historico_familiar_hipertensao"]:
            risk_factors.append("Histórico familiar de hipertensão")
            score += 15

        # Calcula IMC
        if auto["altura_cm"] > 0:
            imc = auto["peso_kg"] / ((auto["altura_cm"]/100) ** 2)
            if imc > 30:
                risk_factors.append("Obesidade (IMC > 30)")
                score += 15
            elif imc > 25:
                risk_factors.append("Sobrepeso (IMC > 25)")
                score += 10

        if auto["fuma_atualmente"]:
            risk_factors.append("Tabagismo")
            score += 20

        if auto["bebidas_alcoolicas_semana"] > 14:
            risk_factors.append("Consumo excessivo de álcool")
            score += 10

        if auto["nivel_estresse_0_10"] > 7:
            risk_factors.append("Alto nível de estresse")
            score += 10

        if auto["sono_qualidade_ruim"]:
            risk_factors.append("Qualidade de sono ruim")
            score += 5

        if auto["minutos_exercicio_semana"] < 150:
            risk_factors.append("Sedentarismo (menos de 150min/semana)")
            score += 10

        if auto["porcoes_frutas_vegetais_dia"] < 5:
            risk_factors.append("Dieta pobre em frutas e vegetais")
            score += 5

        # Análise de exames
        if exames:
            if exames.get("colesterol_ldl_mg_dL", 0) > 130:
                risk_factors.append("LDL elevado (>130 mg/dL)")
                score += 10

            if exames.get("glicemia_jejum_mg_dL", 0) > 100:
                risk_factors.append("Glicemia alterada (>100 mg/dL)")
                score += 10

            if exames.get("proteinuria_positiva", False):
                risk_factors.append("Proteinúria positiva")
                score += 15

        # Classificação de risco
        if score < 20:
            risk_level = "BAIXO"
            recommendation = "Manter hábitos saudáveis e monitoramento anual."
        elif score < 40:
            risk_level = "MODERADO"
            recommendation = "Modificações no estilo de vida e monitoramento semestral."
        elif score < 60:
            risk_level = "ALTO"
            recommendation = "Intervenção médica necessária. Monitoramento trimestral."
        else:
            risk_level = "MUITO ALTO"
            recommendation = "Intervenção médica urgente. Acompanhamento mensal."

        # Monta relatório
        report = f"""
🏥 RELATÓRIO DE AVALIAÇÃO DE RISCO DE HIPERTENSÃO

📊 PONTUAÇÃO DE RISCO: {score} pontos
🎯 NÍVEL DE RISCO: {risk_level}

⚠️ FATORES DE RISCO IDENTIFICADOS:
"""

        if risk_factors:
            for i, factor in enumerate(risk_factors, 1):
                report += f"{i}. {factor}\n"
        else:
            report += "Nenhum fator de risco significativo identificado.\n"

        report += f"""
💡 RECOMENDAÇÕES:
{recommendation}

📝 ORIENTAÇÕES GERAIS:
• Manter pressão arterial abaixo de 120/80 mmHg
• Praticar exercícios regulares (mínimo 150min/semana)
• Manter dieta rica em frutas, vegetais e pobre em sódio
• Controlar peso corporal (IMC < 25)
• Evitar tabagismo e consumo excessivo de álcool
• Gerenciar níveis de estresse
• Manter qualidade adequada do sono

⏰ Data da Avaliação: {datetime.now().strftime('%d/%m/%Y %H:%M')}

IMPORTANTE: Esta avaliação é apenas informativa. 
Consulte sempre um médico para diagnóstico e tratamento adequados.
"""

        return report
    
    def ai_assessment(self, data):
        """Avaliação de risco de hipertensão usando Gemini AI"""
        
        API_KEY = os.getenv("GEMINI_API_KEY")
        
        try:
            # Inicializa cliente Gemini
            gemini = genai.Client(
                api_key=API_KEY, 
                http_options=types.HttpOptions(api_version="v1alpha")
            )
            chat = gemini.chats.create(model="gemini-2.0-flash")
            
            # Prepara dados para análise
            auto = data["avaliacaoagil"]
            exames = data.get("exames")
            
            # Calcula IMC para incluir no prompt
            imc = None
            if auto["altura_cm"] > 0:
                imc = auto["peso_kg"] / ((auto["altura_cm"]/100) ** 2)
            
            imc_str = f"{imc:.1f}" if imc else "Não calculado"
            
            # Constrói prompt estruturado
            prompt = f"""
Você é um especialista em cardiologia e medicina preventiva. Analise os dados do paciente e forneça uma avaliação de risco de hipertensão seguindo EXATAMENTE o formato especificado abaixo.

DADOS DO PACIENTE:
=================

DADOS DEMOGRÁFICOS E ESTILO DE VIDA:
• Idade: {auto['idade_anos']} anos
• Sexo: {'Masculino' if auto['sexo_masculino'] else 'Feminino'}
• Histórico familiar de hipertensão: {'Sim' if auto['historico_familiar_hipertensao'] else 'Não'}
• Altura: {auto['altura_cm']} cm
• Peso: {auto['peso_kg']} kg
• IMC: {imc_str}
• Porções de frutas/vegetais por dia: {auto['porcoes_frutas_vegetais_dia']}
• Minutos de exercício por semana: {auto['minutos_exercicio_semana']}
• Fuma atualmente: {'Sim' if auto['fuma_atualmente'] else 'Não'}
• Bebidas alcoólicas por semana: {auto['bebidas_alcoolicas_semana']}
• Nível de estresse (0-10): {auto['nivel_estresse_0_10']}
• Qualidade do sono ruim: {'Sim' if auto['sono_qualidade_ruim'] else 'Não'}

EXAMES LABORATORIAIS:
"""

            if exames:
                prompt += f"""
• Colesterol LDL: {exames.get('colesterol_ldl_mg_dL', 'Não informado')} mg/dL
• Colesterol HDL: {exames.get('colesterol_hdl_mg_dL', 'Não informado')} mg/dL
• Triglicerídeos: {exames.get('triglicerideos_mg_dL', 'Não informado')} mg/dL
• Glicemia de jejum: {exames.get('glicemia_jejum_mg_dL', 'Não informado')} mg/dL
• HbA1c: {exames.get('hba1c_percent', 'Não informado')}%
• Creatinina: {exames.get('creatinina_mg_dL', 'Não informado')} mg/dL
• Proteinúria: {'Positiva' if exames.get('proteinuria_positiva', False) else 'Negativa'}
• Diagnóstico de apneia do sono: {'Sim' if exames.get('diagnostico_apneia_sono', False) else 'Não'}
• Cortisol sérico: {exames.get('cortisol_serico_ug_dL', 'Não informado')} μg/dL
• Mutação genética para hipertensão: {'Sim' if exames.get('mutacao_genetica_hipertensao', False) else 'Não'}
• BPM em repouso: {exames.get('bpm_repouso', 'Não informado')}
• Índice PM2.5: {exames.get('indice_pm25', 'Não informado')}
"""
            else:
                prompt += "Não foram fornecidos exames laboratoriais.\n"

            prompt += f"""

INSTRUÇÕES PARA AVALIAÇÃO:
=========================

1. Analise todos os fatores de risco para hipertensão presentes nos dados
2. Calcule uma pontuação de risco baseada em evidências científicas em uma escala de 0 a 100
3. Classifique o risco como: BAIXO, MODERADO, ALTO ou MUITO ALTO
4. Forneça recomendações específicas baseadas no perfil do paciente

FORMATO DE RESPOSTA OBRIGATÓRIO:
===============================

🏥 RELATÓRIO DE AVALIAÇÃO DE RISCO DE HIPERTENSÃO

📊 PONTUAÇÃO DE RISCO: [pontuação] pontos
🎯 NÍVEL DE RISCO: [BAIXO/MODERADO/ALTO/MUITO ALTO]

⚠️ FATORES DE RISCO IDENTIFICADOS:
[Liste numericamente cada fator de risco encontrado, um por linha]

💡 RECOMENDAÇÕES:
[Recomendações específicas baseadas no perfil do paciente]

📝 ORIENTAÇÕES GERAIS:
• Manter pressão arterial abaixo de 120/80 mmHg
• Praticar exercícios regulares (mínimo 150min/semana)
• Manter dieta rica em frutas, vegetais e pobre em sódio
• Controlar peso corporal (IMC < 25)
• Evitar tabagismo e consumo excessivo de álcool
• Gerenciar níveis de estresse
• Manter qualidade adequada do sono

⏰ Data da Avaliação: {datetime.now().strftime('%d/%m/%Y %H:%M')}

IMPORTANTE: Esta avaliação é apenas informativa. 
Consulte sempre um médico para diagnóstico e tratamento adequados.

RESPONDA APENAS COM O RELATÓRIO NO FORMATO ESPECIFICADO ACIMA.
"""

            # Envia prompt para Gemini
            response = chat.send_message(prompt)
            
            # Retorna o texto da resposta
            return response.text
            
        except Exception as e:
            # Fallback para simulação local em caso de erro
            print(f"Erro na avaliação com Gemini: {e}")
            return "Erro ao avaliar com Gemini. Contate os administradores."

    def salvar_relatorio(self):
        """Salva relatório no banco de dados (apenas médicos)"""
        if self.user["user_type"] != "doctor":
            return

        if not self.last_assessment:
            QMessageBox.warning(
                self, "Erro", "Realize uma avaliação primeiro!")
            return

        # Pega o paciente selecionado
        if self.patient_combo.currentData() is None:
            QMessageBox.warning(self, "Erro", "Selecione um paciente!")
            return

        patient_id = self.patient_combo.currentData()

        # Salva no banco
        report_id = self.db_manager.create_report(
            self.user["_id"],
            patient_id,
            self.last_assessment
        )

        if report_id:
            QMessageBox.information(
                self, "Sucesso", "Relatório realizado com sucesso!")
            self.btn_salvar.setEnabled(False)
        else:
            QMessageBox.warning(self, "Erro", "Erro ao salvar relatório!")

    def gerar_pdf(self):
        """Método para gerar PDF no estilo oficial preto e branco"""
        if not self.last_assessment:
            QMessageBox.warning(self, "Erro", "Realize uma avaliação primeiro!")
            return
        
        try:
            # Prepara dados
            data = {
                "avaliacaoagil": self.last_assessment["input_data"]["avaliacaoagil"],
                "exames": self.last_assessment["input_data"].get("exames"),
                "ai_result": self.last_assessment["ai_result"]
            }
            
            # Informações do usuário
            user_info = {
                "name": self.user["name"],
                "user_type": self.user.get("user_type", "patient")
            }
            
            # Nome do paciente
            patient_name = None
            if self.user["user_type"] == "doctor" and self.patient_combo.currentData():
                patient_name = self.patient_combo.currentText()
            
            # Gera o PDF (agora com diálogo de salvamento)
            generator = MedicalReportPDFWriter()
            filename = generator.generate_pdf(data, user_info, patient_name)
        
            # Verifica se o usuário não cancelou
            if filename:
                QMessageBox.information(
                    self, 
                    "✅ Laudo Gerado", 
                    f"Laudo médico oficial gerado com sucesso!\n\n📁 Salvo em:\n{filename}"
                )
            # Se filename for None, usuário cancelou - não mostra nada
            
        except Exception as e:
            QMessageBox.critical(
                self, 
                "❌ Erro", 
                f"Erro ao gerar laudo:\n\n{str(e)}"
            )