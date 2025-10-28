import os
import re
from datetime import datetime
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QFormLayout, QGroupBox,
    QLabel, QSpinBox, QDoubleSpinBox, QCheckBox, QPushButton,
    QPlainTextEdit, QHBoxLayout, QLineEdit, QScrollArea,
    QMessageBox, QFrame, QDialog, QProgressBar
)
from PyQt5.QtGui import QFont, QIntValidator
from PyQt5.QtCore import Qt, QThread, QObject, pyqtSignal
from google import genai
from google.genai import types
from Classes.MedicalReportPDFWriter import MedicalReportPDFWriter

# --- HELPER CLASSES PARA POPUP E THREADING ---

class LoadingDialog(QDialog):
    """
    Popup de carregamento modal para operações demoradas.
    """
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Processando...")
        self.setModal(True)
        # Impede o usuário de fechar o diálogo
        self.setWindowFlags(Qt.Dialog | Qt.CustomizeWindowHint | Qt.WindowTitleHint) 
        
        layout = QVBoxLayout(self)
        layout.setSpacing(15)
        layout.setContentsMargins(20, 20, 20, 20)
        
        self.msg_label = QLabel("Enviando dados para análise da IA...")
        self.msg_label.setFont(QFont("Segoe UI", 12))
        self.msg_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.msg_label)
        
        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 0) # Modo indeterminado
        self.progress_bar.setMinimumHeight(15)
        layout.addWidget(self.progress_bar)
        
        self.gemini_label = QLabel("powered by google gemini")
        self.gemini_label.setStyleSheet("font-size: 8pt; color: #7f8c8d;")
        self.gemini_label.setAlignment(Qt.AlignRight)
        layout.addWidget(self.gemini_label)
        
        self.setMinimumWidth(350)

class AssessmentWorker(QObject):
    """
    Worker para executar a avaliação da IA em uma thread separada.
    """
    finished = pyqtSignal(str) # Emite o resultado (string)

    def __init__(self, assessment_data, ai_function):
        super().__init__()
        self.assessment_data = assessment_data
        self.ai_function = ai_function

    def run(self):
        """Executa a tarefa demorada"""
        try:
            resultado = self.ai_function(self.assessment_data)
            self.finished.emit(resultado)
        except Exception as e:
            print(f"Erro no worker de avaliação: {e}")
            self.finished.emit(f"Erro ao processar avaliação: {e}")


# --- CLASSE PARA FORMATAÇÃO E VALIDAÇÃO DE CPF ---

class CPFLineEdit(QLineEdit):
    """
    QLineEdit personalizado com formatação automática de CPF
    e validação em tempo real.
    """
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setPlaceholderText("Digite o CPF (apenas números)")
        self.setMaxLength(14)  # 11 dígitos + 3 separadores
        self.textChanged.connect(self.format_cpf)
        self.setStyleSheet("""
            QLineEdit {
                border: 2px solid #bdc3c7;
                border-radius: 6px;
                padding: 8px 12px;
                background-color: white;
                font-size: 11pt;
                min-height: 20px;
                font-weight: 500;
            }
            QLineEdit:focus {
                border-color: #3498db;
                outline: none;
            }
            QLineEdit[valid="true"] {
                border-color: #27ae60;
                background-color: #eafaf1;
            }
            QLineEdit[valid="false"] {
                border-color: #e74c3c;
                background-color: #fadbd8;
            }
        """)
    
    def format_cpf(self):
        """Formata o CPF automaticamente enquanto o usuário digita"""
        # Remove tudo que não é número
        text = re.sub(r'\D', '', self.text())
        
        # Limita a 11 dígitos
        if len(text) > 11:
            text = text[:11]
        
        # Formata o CPF
        formatted = ""
        if len(text) <= 3:
            formatted = text
        elif len(text) <= 6:
            formatted = f"{text[:3]}.{text[3:]}"
        elif len(text) <= 9:
            formatted = f"{text[:3]}.{text[3:6]}.{text[6:]}"
        else:
            formatted = f"{text[:3]}.{text[3:6]}.{text[6:9]}-{text[9:]}"
        
        # Atualiza o texto sem reemitir o sinal
        self.blockSignals(True)
        cursor_pos = self.cursorPosition()
        old_length = len(self.text())
        self.setText(formatted)
        
        # Ajusta a posição do cursor
        new_length = len(formatted)
        if new_length > old_length:
            cursor_pos += (new_length - old_length)
        self.setCursorPosition(min(cursor_pos, new_length))
        self.blockSignals(False)
        
        # Atualiza o estilo baseado na validade
        self.update_validity_style()
    
    def get_raw_cpf(self):
        """Retorna o CPF sem formatação (apenas números)"""
        return re.sub(r'\D', '', self.text())
    
    def is_valid_cpf(self, cpf):
        """Valida o CPF usando o algoritmo oficial"""
        # Remove caracteres não numéricos
        cpf = re.sub(r'\D', '', cpf)
        
        # Verifica se tem 11 dígitos
        if len(cpf) != 11:
            return False
        
        # Verifica se todos os dígitos são iguais
        if cpf == cpf[0] * 11:
            return False
        
        # Valida primeiro dígito verificador
        soma = sum(int(cpf[i]) * (10 - i) for i in range(9))
        digito1 = (soma * 10 % 11) % 10
        if digito1 != int(cpf[9]):
            return False
        
        # Valida segundo dígito verificador
        soma = sum(int(cpf[i]) * (11 - i) for i in range(10))
        digito2 = (soma * 10 % 11) % 10
        if digito2 != int(cpf[10]):
            return False
        
        return True
    
    def update_validity_style(self):
        """Atualiza o estilo visual baseado na validade do CPF"""
        cpf = self.get_raw_cpf()
        
        if len(cpf) == 0:
            self.setProperty("valid", "")
        elif len(cpf) == 11:
            if self.is_valid_cpf(cpf):
                self.setProperty("valid", "true")
            else:
                self.setProperty("valid", "false")
        else:
            self.setProperty("valid", "")
        
        # Força atualização do estilo
        self.style().unpolish(self)
        self.style().polish(self)
    
    def is_complete_and_valid(self):
        """Verifica se o CPF está completo e válido"""
        cpf = self.get_raw_cpf()
        return len(cpf) == 11 and self.is_valid_cpf(cpf)


# --- CLASSE PRINCIPAL DA TELA ---

class HypertensionAssessment(QWidget):
    def __init__(self, db_manager, user):
        super().__init__()
        self.db_manager = db_manager
        self.user = user
        
        # Estado
        self.selected_patient_id = None
        self.last_assessment = None
        self.last_assessment_report_id = None
        self.current_assessment_data = None

        #flags
        self.flag_avaliar_concluida = False
        self.flag_salvar_concluido = False
        
        # Para o threading
        self.thread = None
        self.worker = None
        self.loading_dialog = None
        
        self.init_ui()

    def calculate_age(self, birth_date):
        """Calcula idade a partir da data de nascimento"""
        if not birth_date:
            return 0
        today = datetime.now()
        age = today.year - birth_date.year - ((today.month, today.day) < (birth_date.month, birth_date.day))
        return age

    def init_ui(self):
        # Aplicar estilo geral
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

        # --- SELEÇÃO DE PACIENTE (Req 1) ---
        if self.user["user_type"] == "doctor":
            patient_group = QGroupBox("👤 Seleção de Paciente")
            patient_layout = QFormLayout()
            patient_layout.setSpacing(15)
            patient_layout.setFieldGrowthPolicy(QFormLayout.ExpandingFieldsGrow)
            
            # Layout de busca (CPF + Botão)
            search_layout = QHBoxLayout()
            search_layout.setSpacing(10)
            
            # Usa o CPFLineEdit personalizado
            self.cpf_input = CPFLineEdit()
            self.cpf_input.setMinimumHeight(35)
            self.cpf_input.returnPressed.connect(self.search_patient_by_cpf)  # Enter para buscar
            search_layout.addWidget(self.cpf_input, 3)
            
            self.search_patient_btn = QPushButton("🔍 Buscar")
            self.search_patient_btn.setMinimumHeight(35)
            self.search_patient_btn.clicked.connect(self.search_patient_by_cpf)
            search_layout.addWidget(self.search_patient_btn, 1)
            
            patient_layout.addRow(self.create_bold_label("Buscar por CPF:"), search_layout)
            
            # Label de validação do CPF
            self.cpf_validation_label = QLabel("")
            self.cpf_validation_label.setStyleSheet("font-size: 9pt; font-style: italic;")
            self.cpf_validation_label.setWordWrap(True)
            patient_layout.addRow("", self.cpf_validation_label)
            
            # Conecta mudanças no CPF para atualizar mensagem de validação
            self.cpf_input.textChanged.connect(self.update_cpf_validation_message)
            
            # Label para nome do paciente com ícone de status
            patient_info_frame = QFrame()
            patient_info_frame.setStyleSheet("""
                QFrame {
                    background-color: #f8f9fa;
                    border: 2px solid #e8e8e8;
                    border-radius: 8px;
                    padding: 10px;
                }
            """)
            patient_info_layout = QHBoxLayout(patient_info_frame)
            patient_info_layout.setContentsMargins(10, 10, 10, 10)
            
            self.patient_status_icon = QLabel("⚪")
            self.patient_status_icon.setFont(QFont("Segoe UI", 14))
            patient_info_layout.addWidget(self.patient_status_icon)
            
            self.patient_name_label = QLabel("Nenhum paciente selecionado")
            self.patient_name_label.setStyleSheet("font-weight: bold; color: #7f8c8d; font-size: 11pt;")
            self.patient_name_label.setWordWrap(True)
            patient_info_layout.addWidget(self.patient_name_label, 1)
            
            patient_layout.addRow(self.create_bold_label("Paciente:"), patient_info_frame)
            
            patient_group.setLayout(patient_layout)
            content_layout.addWidget(patient_group)

        # --- SUBDIVISÃO 1: DADOS DEMOGRÁFICOS (Req 2) ---
        demo_gbox = QGroupBox("ℹ️ Dados Demográficos")
        demo_form = QFormLayout()
        demo_form.setSpacing(15)
        demo_form.setFieldGrowthPolicy(QFormLayout.ExpandingFieldsGrow)
        
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
        self.idade.setPlaceholderText("Selecione um paciente")
        demo_form.addRow(self.create_bold_label("Idade:"), self.idade)

        self.sexo_m = QCheckBox("Masculino")
        self.sexo_m.setStyleSheet("QCheckBox { font-weight: bold; }")
        demo_form.addRow(self.create_bold_label("Sexo:"), self.sexo_m)

        self.hist_fam = QCheckBox("Sim")
        demo_form.addRow(self.create_bold_label("Histórico familiar de hipertensão:"), self.hist_fam)
        
        demo_gbox.setLayout(demo_form)
        content_layout.addWidget(demo_gbox)
        
        # --- SUBDIVISÃO 2: MEDIDAS FÍSICAS (Req 2) ---
        measures_gbox = QGroupBox("📏 Medidas Físicas")
        measures_form = QFormLayout()
        measures_form.setSpacing(15)
        measures_form.setFieldGrowthPolicy(QFormLayout.ExpandingFieldsGrow)

        measures_frame = QFrame()
        measures_layout = QHBoxLayout(measures_frame)
        measures_layout.setSpacing(10)
        measures_layout.setContentsMargins(0,0,0,0)
        
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
        
        measures_form.addRow(measures_frame)
        
        self.altura.valueChanged.connect(self.calcular_imc)
        self.peso.valueChanged.connect(self.calcular_imc)
        
        measures_gbox.setLayout(measures_form)
        content_layout.addWidget(measures_gbox)

        # --- SUBDIVISÃO 3: ESTILO DE VIDA E HÁBITOS (Req 2) ---
        habits_gbox = QGroupBox("🥗 Estilo de Vida e Hábitos")
        habits_form = QFormLayout()
        habits_form.setSpacing(15)
        habits_form.setFieldGrowthPolicy(QFormLayout.ExpandingFieldsGrow)

        self.frutas = QSpinBox()
        self.frutas.setRange(0, 20)
        self.frutas.setSuffix(" porções/dia")
        self.frutas.setMinimumHeight(35)
        habits_form.addRow(self.create_bold_label("Frutas/Vegetais por dia:"), self.frutas)

        self.exercicio = QSpinBox()
        self.exercicio.setRange(0, 10000)
        self.exercicio.setSuffix(" min/semana")
        self.exercicio.setMinimumHeight(35)
        habits_form.addRow(self.create_bold_label("Exercício por semana:"), self.exercicio)

        self.fuma = QCheckBox("Sim")
        habits_form.addRow(self.create_bold_label("Fumante:"), self.fuma)

        self.alcool = QSpinBox()
        self.alcool.setRange(0, 100)
        self.alcool.setSuffix(" doses/semana")
        self.alcool.setMinimumHeight(35)
        habits_form.addRow(self.create_bold_label("Bebidas alcoólicas:"), self.alcool)

        self.estresse = QSpinBox()
        self.estresse.setRange(0, 10)
        self.estresse.setSuffix(" (0=baixo, 10=alto)")
        self.estresse.setMinimumHeight(35)
        habits_form.addRow(self.create_bold_label("Nível de estresse:"), self.estresse)

        self.sono = QCheckBox("Sim")
        habits_form.addRow(self.create_bold_label("Qualidade do sono ruim:"), self.sono)

        habits_gbox.setLayout(habits_form)
        content_layout.addWidget(habits_gbox)

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
        cholesterol_layout.setContentsMargins(0,0,0,0)
        
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
        glucose_layout.setContentsMargins(0,0,0,0)
        
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
        vitals_layout.setContentsMargins(0,0,0,0)
        
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
            self.btn_salvar.setMinimumHeight(45)
            btns.addWidget(self.btn_salvar)

        self.btn_pdf = QPushButton("📄 Gerar PDF")
        self.btn_pdf.setObjectName("btn_pdf")
        self.btn_pdf.clicked.connect(self.gerar_pdf)
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
        
        # Carrega dados iniciais (apenas se for paciente)
        if self.user["user_type"] == "patient":
            self.load_initial_data()

    def create_bold_label(self, text):
        """Cria um label com estilo em negrito"""
        label = QLabel(text)
        label.setStyleSheet("font-weight: bold; color: #34495e;")
        return label

    def update_cpf_validation_message(self):
        """Atualiza a mensagem de validação do CPF em tempo real"""
        if self.user["user_type"] != "doctor":
            return
            
        cpf = self.cpf_input.get_raw_cpf()
        
        if len(cpf) == 0:
            self.cpf_validation_label.setText("")
            self.cpf_validation_label.setStyleSheet("font-size: 9pt;")
        elif len(cpf) < 11:
            self.cpf_validation_label.setText(f"⏳ Digite mais {11 - len(cpf)} dígito(s)")
            self.cpf_validation_label.setStyleSheet("font-size: 9pt; color: #f39c12; font-style: italic;")
        elif self.cpf_input.is_complete_and_valid():
            self.cpf_validation_label.setText("✅ CPF válido - Pressione Enter ou clique em Buscar")
            self.cpf_validation_label.setStyleSheet("font-size: 9pt; color: #27ae60; font-weight: bold;")
        else:
            self.cpf_validation_label.setText("❌ CPF inválido - Verifique os números digitados")
            self.cpf_validation_label.setStyleSheet("font-size: 9pt; color: #e74c3c; font-weight: bold;")

    def search_patient_by_cpf(self):
        """Busca paciente por CPF no banco de dados"""
        if not self.cpf_input.is_complete_and_valid():
            QMessageBox.warning(
                self, 
                "CPF Inválido", 
                "Por favor, digite um CPF válido antes de buscar.\n\nO CPF deve conter 11 dígitos e passar pela validação."
            )
            self.cpf_input.setFocus()
            return

        cpf = self.cpf_input.text()

        # Busca apenas pacientes ATIVOS pelo CPF
        patient = self.db_manager.get_user_by_cpf(cpf, user_type='patient')
        
        if patient:
            self.selected_patient_id = patient['id']
            self.patient_name_label.setText(f"{patient['name']}")
            self.patient_name_label.setStyleSheet("font-weight: bold; color: #27ae60; font-size: 11pt;")
            self.patient_status_icon.setText("✅")
            
            # Reseta os botões, dados e flags
            self.last_assessment = None
            self.last_assessment_report_id = None
            self.flag_avaliar_concluida = False
            self.flag_salvar_concluido = False
            
            self.result.clear()
            
            # Carrega os dados do paciente encontrado
            self.load_initial_data()
            
            # Feedback visual de sucesso
            QMessageBox.information(
                self,
                "✅ Paciente Encontrado",
                f"Paciente {patient['name']} encontrado com sucesso!\n\nCPF: {self.cpf_input.text()}"
            )
        else:
            self.selected_patient_id = None
            self.patient_name_label.setText("Paciente não encontrado ou inativo")
            self.patient_name_label.setStyleSheet("font-weight: bold; color: #e74c3c; font-size: 11pt;")
            self.patient_status_icon.setText("❌")
            self.clear_form_fields()
            self.idade.clear()
            
            QMessageBox.warning(
                self,
                "❌ Paciente Não Encontrado",
                f"Não foi encontrado nenhum paciente ativo com o CPF:\n{self.cpf_input.text()}\n\nVerifique se:\n• O CPF está correto\n• O paciente está cadastrado no sistema\n• O cadastro do paciente está ativo"
            )
         
    def clear_form_fields(self):
        """Limpa todos os campos do formulário"""
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
        patient_data = None
        
        # Define qual paciente buscar
        if self.user["user_type"] == "patient":
            patient_id = self.user["id"]
            patient_data = self.user
        
        elif self.user["user_type"] == "doctor":
            patient_id = self.selected_patient_id
            if patient_id:
                patient_data = self.db_manager.get_user_by_id(patient_id)
            else:
                self.clear_form_fields()
                self.idade.clear()
                return
        else:
            return
        
        # Calcula e exibe idade
        if patient_data and "birth_date" in patient_data and patient_data["birth_date"]:
            age = self.calculate_age(patient_data["birth_date"])
            self.idade.setText(f"{age} anos")
        else:
            self.idade.setText("Idade N/A")
        
        # Busca último relatório do paciente
        if patient_id:
            self.clear_form_fields() 
            
            last_report = self.db_manager.get_latest_patient_report(patient_id)
            
            if last_report and "report_data" in last_report:
                report_data = last_report["report_data"]
                input_data = report_data.get("input_data", {})
                
                # 'avaliacaoagil' ou 'autoavaliacao'
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
        if self.user["user_type"] == "doctor" and self.selected_patient_id is None:
            QMessageBox.warning(self, "Ação Necessária", "Você deve buscar e selecionar um paciente ativo pelo CPF antes de avaliar.")
            return

        idade_atual = self.get_current_age()
        if idade_atual == 0:
            QMessageBox.warning(self, "Dados Incompletos", "Não foi possível determinar a idade do paciente.")
            return
            
        # Monta dados de Avaliação Ágil
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

        # Armazena dados para o worker
        self.current_assessment_data = {
            "avaliacaoagil": auto,
            "exames": exames,
            "timestamp": datetime.now().isoformat()
        }

        # Inicia popup e thread
        self.loading_dialog = LoadingDialog(self)
        
        # Configura a thread e o worker
        self.thread = QThread(self)
        self.worker = AssessmentWorker(self.current_assessment_data, self.ai_assessment)
        self.worker.moveToThread(self.thread)
        
        # Conecta os sinais
        self.thread.started.connect(self.worker.run)
        self.worker.finished.connect(self.on_assessment_finished)
        self.worker.finished.connect(self.thread.quit)
        self.worker.finished.connect(self.worker.deleteLater)
        self.thread.finished.connect(self.thread.deleteLater)
        
        # Inicia a thread
        self.thread.start()
        
        # Exibe o diálogo de carregamento
        self.loading_dialog.exec_()
    
    def on_assessment_finished(self, resultado):
        """Chamado quando a thread de avaliação termina"""
        # Fecha o popup
        if self.loading_dialog:
            self.loading_dialog.accept()
            
        # Lida com o resultado
        if "Erro" in resultado:
            QMessageBox.critical(self, "Erro na Avaliação", resultado)
            self.flag_avaliar_concluida = False
            self.flag_salvar_concluido = False
            return

        self.result.setPlainText(resultado)
        
        # Armazena o último resultado
        self.last_assessment = {
            "input_data": self.current_assessment_data,
            "ai_result": resultado
        }
        
        # Reseta o ID do relatório salvo
        self.last_assessment_report_id = None
        
        self.flag_avaliar_concluida = True
        self.flag_salvar_concluido = False
             
             
    def ai_assessment(self, data):
        """Avaliação de risco de hipertensão usando Gemini AI"""
        
        API_KEY = os.getenv("GEMINI_API_KEY")
        if not API_KEY:
             return "Erro: GEMINI_API_KEY não configurada no ambiente."

        try:
            gemini = genai.Client(
                api_key=API_KEY, 
                http_options=types.HttpOptions(api_version="v1alpha")
            )
            chat = gemini.chats.create(model="gemini-2.0-flash")
            
            auto = data["avaliacaoagil"]
            exames = data.get("exames")
            
            imc = None
            if auto["altura_cm"] > 0 and auto["peso_kg"] > 0:
                imc = auto["peso_kg"] / ((auto["altura_cm"]/100) ** 2)
            
            imc_str = f"{imc:.1f}" if imc else "Não calculado"
            
            # Constrói prompt estruturado
            prompt = f"""
Você é um especialista em cardiologia e medicina preventiva. Analise os dados do paciente e forneça uma avaliação de risco de hipertensão seguindo EXATAMENTE o formato especificado abaixo.

DADOS DO PACIENTE:
=================

DADOS DEMOGRÁFICOS E ESTILO de VIDA:
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
• Colesterol LDL: {exames.get('colesterol_ldl_mg_dL', 'Não informado') or 'Não informado'} mg/dL
• Colesterol HDL: {exames.get('colesterol_hdl_mg_dL', 'Não informado') or 'Não informado'} mg/dL
• Triglicerídeos: {exames.get('triglicerideos_mg_dL', 'Não informado') or 'Não informado'} mg/dL
• Glicemia de jejum: {exames.get('glicemia_jejum_mg_dL', 'Não informado') or 'Não informado'} mg/dL
• HbA1c: {exames.get('hba1c_percent', 'Não informado') or 'Não informado'}%
• Creatinina: {exames.get('creatinina_mg_dL', 'Não informado') or 'Não informado'} mg/dL
• Proteinúria: {'Positiva' if exames.get('proteinuria_positiva', False) else 'Negativa'}
• Diagnóstico de apneia do sono: {'Sim' if exames.get('diagnostico_apneia_sono', False) else 'Não'}
• Cortisol sérico: {exames.get('cortisol_serico_ug_dL', 'Não informado') or 'Não informado'} μg/dL
• Mutação genética para hipertensão: {'Sim' if exames.get('mutacao_genetica_hipertensao', False) else 'Não'}
• BPM em repouso: {exames.get('bpm_repouso', 'Não informado') or 'Não informado'}
• Índice PM2.5: {exames.get('indice_pm25', 'Não informado') or 'Não informado'}
"""
            else:
                prompt += "Não foram fornecidos exames laboratoriais.\n"

            prompt += f"""

INSTRUÇÕES PARA AVALIAÇÃO:
=========================
1. Analise todos os fatores de risco para hipertensão presentes nos dados.
2. Calcule uma pontuação de risco (0-100) e classifique (BAIXO, MODERADO, ALTO, MUITO ALTO).
3. Forneça recomendações específicas.

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

            response = chat.send_message(prompt)
            return response.text
            
        except Exception as e:
            print(f"Erro na avaliação com Gemini: {e}")
            return f"Erro ao avaliar com Gemini: {str(e)}"

    def salvar_relatorio(self):
        """Salva relatório no banco de dados (apenas médicos)"""
        if self.user["user_type"] != "doctor":
            return

        if not self.flag_avaliar_concluida:
            QMessageBox.warning(
                self, "Ação Necessária", "Você deve gerar um relatório (clicando em 'Avaliar Hipertensão') antes de salvar.")
            return

        if self.selected_patient_id is None:
            QMessageBox.warning(self, "Erro", "Nenhum paciente selecionado!")
            return

        patient_id = self.selected_patient_id

        # Salva no banco
        report_id = self.db_manager.create_report(
            self.user["id"],
            patient_id,
            self.last_assessment
        )

        if report_id:
            QMessageBox.information(
                self, "Sucesso", "Relatório salvo com sucesso!")
            self.last_assessment_report_id = report_id
            self.flag_salvar_concluido = True
        else:
            QMessageBox.warning(self, "Erro", "Erro ao salvar relatório!")
            self.flag_salvar_concluido = False


    def gerar_pdf(self):
        """Método para gerar PDF no estilo oficial preto e branco"""
        
        if self.user["user_type"] == "doctor" and not self.flag_salvar_concluido:
            QMessageBox.warning(
                self, "Ação Necessária", "Você deve salvar o relatório (clicando em 'Salvar Relatório') antes de gerar o PDF.")
            return
            
        if not self.flag_avaliar_concluida:
            QMessageBox.warning(self, "Erro", "Realize uma avaliação primeiro!")
            return
        
        try:
            data = {
                "avaliacaoagil": self.last_assessment["input_data"]["avaliacaoagil"],
                "exames": self.last_assessment["input_data"].get("exames"),
                "ai_result": self.last_assessment["ai_result"]
            }
            
            user_info = {
                "name": self.user["name"],
                "user_type": self.user.get("user_type", "patient")
            }
            
            # Pega nome do paciente do label
            patient_name = None
            if self.user["user_type"] == "doctor" and self.selected_patient_id:
                patient_name = self.patient_name_label.text()
            elif self.user["user_type"] == "patient":
                patient_name = self.user["name"]
            
            # Gera o PDF
            generator = MedicalReportPDFWriter()
            filename = generator.generate_pdf(data, user_info, patient_name)
        
            if filename:
                QMessageBox.information(
                    self, 
                    "✅ Laudo Gerado", 
                    f"Laudo médico oficial gerado com sucesso!\n\n📁 Salvo em:\n{filename}"
                )
            
        except Exception as e:
            QMessageBox.critical(
                self, 
                "❌ Erro", 
                f"Erro ao gerar laudo:\n\n{str(e)}"
            )