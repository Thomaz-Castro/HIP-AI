from PyQt5.QtWidgets import (
    QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QTextEdit, QDialog, QGroupBox, QGridLayout,
    QScrollArea, QWidget, QFrame
)
from PyQt5.QtGui import QFont
from PyQt5.QtCore import Qt

class ReportViewDialog(QDialog):
    def __init__(self, report):
        super().__init__()
        self.report = report
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("📋 Visualizar Relatório Médico")
        self.setModal(True)
        self.resize(1000, 800)
        
        # Estilo moderno
        self.setStyleSheet("""
            QDialog {
                background-color: #f5f7fa;
            }
            
            QGroupBox {
                font-weight: bold;
                font-size: 11pt;
                color: #2c3e50;
                border: 2px solid #bdc3c7;
                border-radius: 10px;
                margin-top: 12px;
                padding-top: 10px;
                background-color: white;
            }
            
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 15px;
                padding: 5px 15px;
                background-color: #3498db;
                color: white;
                border-radius: 6px;
            }
            
            QLabel {
                color: #34495e;
                font-size: 10pt;
            }
            
            QLabel[class="header"] {
                font-size: 18pt;
                font-weight: bold;
                color: #2c3e50;
                padding: 15px;
                background-color: white;
                border-radius: 10px;
            }
            
            QLabel[class="field-label"] {
                font-weight: bold;
                color: #7f8c8d;
                font-size: 9pt;
            }
            
            QLabel[class="field-value"] {
                color: #2c3e50;
                font-size: 10pt;
                font-weight: 500;
                padding: 5px;
                background-color: #ecf0f1;
                border-radius: 4px;
            }
            
            QTextEdit {
                border: 2px solid #bdc3c7;
                border-radius: 8px;
                background-color: white;
                padding: 15px;
                font-family: 'Segoe UI', Arial;
                font-size: 10pt;
                line-height: 1.6;
            }
            
            QPushButton {
                background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                                          stop: 0 #3498db, stop: 1 #2980b9);
                border: none;
                color: white;
                padding: 12px 30px;
                font-size: 11pt;
                font-weight: bold;
                border-radius: 8px;
                min-width: 100px;
            }
            
            QPushButton:hover {
                background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                                          stop: 0 #5dade2, stop: 1 #3498db);
            }
            
            QPushButton:pressed {
                background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                                          stop: 0 #2980b9, stop: 1 #21618c);
            }
            
            QScrollArea {
                border: none;
                background-color: transparent;
            }
            
            QFrame[class="separator"] {
                background-color: #bdc3c7;
                max-height: 2px;
                margin: 10px 0px;
            }
        """)

        # Layout principal
        main_layout = QVBoxLayout(self)
        main_layout.setSpacing(15)
        main_layout.setContentsMargins(20, 20, 20, 20)

        # Cabeçalho
        header = QLabel("📋 RELATÓRIO DE AVALIAÇÃO DE HIPERTENSÃO")
        header.setProperty("class", "header")
        header.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(header)

        # Área de scroll para o conteúdo
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        
        content_widget = QWidget()
        content_layout = QVBoxLayout(content_widget)
        content_layout.setSpacing(15)

        # Informações gerais
        info_group = self.create_info_section()
        content_layout.addWidget(info_group)

        # Dados da avaliação ágil
        report_data = self.report["report_data"]
        input_data = report_data.get("input_data", {})
        
        auto = input_data.get("autoavaliacao") or input_data.get("avaliacaoagil")
        if auto:
            auto_group = self.create_avaliacao_section(auto)
            content_layout.addWidget(auto_group)

        # Exames médicos
        exames = input_data.get("exames")
        if exames:
            exames_group = self.create_exames_section(exames)
            content_layout.addWidget(exames_group)

        # Resultado da IA
        ai_result = report_data.get("ai_result", "")
        if ai_result:
            result_group = self.create_result_section(ai_result)
            content_layout.addWidget(result_group)

        scroll.setWidget(content_widget)
        main_layout.addWidget(scroll)

        # Botão fechar
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()
        
        close_btn = QPushButton("✖ Fechar")
        close_btn.clicked.connect(self.accept)
        close_btn.setMinimumHeight(45)
        btn_layout.addWidget(close_btn)
        
        btn_layout.addStretch()
        main_layout.addLayout(btn_layout)

    def create_info_section(self):
        """Cria seção de informações gerais"""
        group = QGroupBox("ℹ️ Informações do Relatório")
        layout = QGridLayout()
        layout.setSpacing(15)
        layout.setColumnStretch(1, 1)
        layout.setColumnStretch(3, 1)
        
        row = 0
        
        # Paciente
        if "patient" in self.report:
            layout.addWidget(self.create_field_label("Paciente:"), row, 0)
            layout.addWidget(self.create_field_value(self.report["patient"]["name"]), row, 1)
            row += 1
            
        # Médico
        if "doctor" in self.report:
            layout.addWidget(self.create_field_label("Médico Responsável:"), row, 0)
            layout.addWidget(self.create_field_value(self.report["doctor"]["name"]), row, 1)
            row += 1
        
        # Data
        layout.addWidget(self.create_field_label("Data da Avaliação:"), row, 0)
        layout.addWidget(self.create_field_value(
            self.report["created_at"].strftime("%d/%m/%Y às %H:%M")
        ), row, 1)
        
        group.setLayout(layout)
        return group

    def create_avaliacao_section(self, auto):
        """Cria seção de dados da avaliação ágil"""
        group = QGroupBox("📝 Dados da Avaliação Ágil")
        layout = QGridLayout()
        layout.setSpacing(12)
        layout.setColumnStretch(1, 1)
        layout.setColumnStretch(3, 1)
        
        # Linha 0
        layout.addWidget(self.create_field_label("Idade:"), 0, 0)
        layout.addWidget(self.create_field_value(f"{auto.get('idade_anos', 'N/A')} anos"), 0, 1)
        
        layout.addWidget(self.create_field_label("Sexo:"), 0, 2)
        layout.addWidget(self.create_field_value(
            "Masculino" if auto.get('sexo_masculino') else "Feminino"
        ), 0, 3)
        
        # Linha 1
        layout.addWidget(self.create_field_label("Histórico Familiar:"), 1, 0)
        layout.addWidget(self.create_field_value(
            "Sim" if auto.get('historico_familiar_hipertensao') else "Não"
        ), 1, 1)
        
        layout.addWidget(self.create_field_label("IMC:"), 1, 2)
        imc_val = auto.get('imc')
        layout.addWidget(self.create_field_value(
            f"{imc_val:.1f}" if imc_val else "N/A"
        ), 1, 3)
        
        # Linha 2
        layout.addWidget(self.create_field_label("Altura:"), 2, 0)
        layout.addWidget(self.create_field_value(f"{auto.get('altura_cm', 'N/A')} cm"), 2, 1)
        
        layout.addWidget(self.create_field_label("Peso:"), 2, 2)
        layout.addWidget(self.create_field_value(f"{auto.get('peso_kg', 'N/A')} kg"), 2, 3)
        
        # Linha 3
        layout.addWidget(self.create_field_label("Frutas/Vegetais por dia:"), 3, 0)
        layout.addWidget(self.create_field_value(
            f"{auto.get('porcoes_frutas_vegetais_dia', 0)} porções"
        ), 3, 1)
        
        layout.addWidget(self.create_field_label("Exercício por semana:"), 3, 2)
        layout.addWidget(self.create_field_value(
            f"{auto.get('minutos_exercicio_semana', 0)} minutos"
        ), 3, 3)
        
        # Linha 4
        layout.addWidget(self.create_field_label("Fumante:"), 4, 0)
        layout.addWidget(self.create_field_value(
            "Sim" if auto.get('fuma_atualmente') else "Não"
        ), 4, 1)
        
        layout.addWidget(self.create_field_label("Bebidas/semana:"), 4, 2)
        layout.addWidget(self.create_field_value(
            f"{auto.get('bebidas_alcoolicas_semana', 0)} doses"
        ), 4, 3)
        
        # Linha 5
        layout.addWidget(self.create_field_label("Nível de Estresse:"), 5, 0)
        layout.addWidget(self.create_field_value(
            f"{auto.get('nivel_estresse_0_10', 0)}/10"
        ), 5, 1)
        
        layout.addWidget(self.create_field_label("Qualidade do Sono:"), 5, 2)
        layout.addWidget(self.create_field_value(
            "Ruim" if auto.get('sono_qualidade_ruim') else "Boa"
        ), 5, 3)
        
        group.setLayout(layout)
        return group

    def create_exames_section(self, exames):
        """Cria seção de exames médicos"""
        group = QGroupBox("🔬 Exames Laboratoriais")
        layout = QGridLayout()
        layout.setSpacing(12)
        layout.setColumnStretch(1, 1)
        layout.setColumnStretch(3, 1)
        
        # Linha 0 - Colesterol
        layout.addWidget(self.create_field_label("Colesterol LDL:"), 0, 0)
        ldl = exames.get('colesterol_ldl_mg_dL')
        layout.addWidget(self.create_field_value(
            f"{ldl} mg/dL" if ldl else "Não informado"
        ), 0, 1)
        
        layout.addWidget(self.create_field_label("Colesterol HDL:"), 0, 2)
        hdl = exames.get('colesterol_hdl_mg_dL')
        layout.addWidget(self.create_field_value(
            f"{hdl} mg/dL" if hdl else "Não informado"
        ), 0, 3)
        
        # Linha 1 - Triglicerídeos e Glicemia
        layout.addWidget(self.create_field_label("Triglicerídeos:"), 1, 0)
        trig = exames.get('triglicerideos_mg_dL')
        layout.addWidget(self.create_field_value(
            f"{trig} mg/dL" if trig else "Não informado"
        ), 1, 1)
        
        layout.addWidget(self.create_field_label("Glicemia de Jejum:"), 1, 2)
        glic = exames.get('glicemia_jejum_mg_dL')
        layout.addWidget(self.create_field_value(
            f"{glic} mg/dL" if glic else "Não informado"
        ), 1, 3)
        
        # Linha 2 - HbA1c e Creatinina
        layout.addWidget(self.create_field_label("HbA1c:"), 2, 0)
        hba1c = exames.get('hba1c_percent')
        layout.addWidget(self.create_field_value(
            f"{hba1c}%" if hba1c else "Não informado"
        ), 2, 1)
        
        layout.addWidget(self.create_field_label("Creatinina:"), 2, 2)
        creat = exames.get('creatinina_mg_dL')
        layout.addWidget(self.create_field_value(
            f"{creat} mg/dL" if creat else "Não informado"
        ), 2, 3)
        
        # Linha 3 - Proteinúria e Apneia
        layout.addWidget(self.create_field_label("Proteinúria:"), 3, 0)
        layout.addWidget(self.create_field_value(
            "Positiva" if exames.get('proteinuria_positiva') else "Negativa"
        ), 3, 1)
        
        layout.addWidget(self.create_field_label("Apneia do Sono:"), 3, 2)
        layout.addWidget(self.create_field_value(
            "Diagnosticada" if exames.get('diagnostico_apneia_sono') else "Não"
        ), 3, 3)
        
        # Linha 4 - Cortisol e Mutação
        layout.addWidget(self.create_field_label("Cortisol Sérico:"), 4, 0)
        cortisol = exames.get('cortisol_serico_ug_dL')
        layout.addWidget(self.create_field_value(
            f"{cortisol} μg/dL" if cortisol else "Não informado"
        ), 4, 1)
        
        layout.addWidget(self.create_field_label("Mutação Genética:"), 4, 2)
        layout.addWidget(self.create_field_value(
            "Presente" if exames.get('mutacao_genetica_hipertensao') else "Não detectada"
        ), 4, 3)
        
        # Linha 5 - BPM e PM2.5
        layout.addWidget(self.create_field_label("BPM em Repouso:"), 5, 0)
        bpm = exames.get('bpm_repouso')
        layout.addWidget(self.create_field_value(
            f"{bpm} bpm" if bpm else "Não informado"
        ), 5, 1)
        
        layout.addWidget(self.create_field_label("Índice PM2.5:"), 5, 2)
        pm25 = exames.get('indice_pm25')
        layout.addWidget(self.create_field_value(
            f"{pm25} μg/m³" if pm25 else "Não informado"
        ), 5, 3)
        
        group.setLayout(layout)
        return group

    def create_result_section(self, ai_result):
        """Cria seção de resultado da IA"""
        group = QGroupBox("🤖 Resultado da Avaliação por IA")
        layout = QVBoxLayout()
        
        result_text = QTextEdit()
        result_text.setReadOnly(True)
        result_text.setPlainText(ai_result)
        result_text.setMinimumHeight(300)
        
        layout.addWidget(result_text)
        group.setLayout(layout)
        return group

    def create_field_label(self, text):
        """Cria um label para campo"""
        label = QLabel(text)
        label.setProperty("class", "field-label")
        return label

    def create_field_value(self, text):
        """Cria um label para valor do campo"""
        label = QLabel(str(text))
        label.setProperty("class", "field-value")
        label.setWordWrap(True)
        return label