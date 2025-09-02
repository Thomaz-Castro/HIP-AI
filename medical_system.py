import sys
import json
import hashlib
from datetime import datetime, date
from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QFormLayout, QGroupBox,
    QLabel, QSpinBox, QDoubleSpinBox, QCheckBox, QPushButton,
    QPlainTextEdit, QHBoxLayout, QLineEdit, QScrollArea, QStackedWidget,
    QComboBox, QTableWidget, QTableWidgetItem, QHeaderView, QMessageBox,
    QTabWidget, QTextEdit, QDateEdit, QDialog
)
from PyQt5.QtGui import QFont, QPixmap
from PyQt5.QtCore import Qt, QDate
from fpdf import FPDF
import pymongo
from pymongo import MongoClient
from bson.objectid import ObjectId
import os
from dotenv import load_dotenv

# Carrega variáveis de ambiente
load_dotenv()

class DatabaseManager:
    def __init__(self):
        # Configure sua string de conexão do MongoDB Atlas aqui
        # Formato: mongodb+srv://<username>:<password>@<cluster>.mongodb.net/<database>?retryWrites=true&w=majority
        self.connection_string = os.getenv("MONGODB_URI", "mongodb+srv://usuario:senha@cluster.mongodb.net/medical_system?retryWrites=true&w=majority")
        self.client = None
        self.db = None
        self.connect()
    
    def connect(self):
        try:
            self.client = MongoClient(self.connection_string)
            self.db = self.client.medical_system
            # Testa a conexão
            self.client.admin.command('ismaster')
            print("Conectado ao MongoDB Atlas com sucesso!")
            self.create_indexes()
            self.create_admin_user()
        except Exception as e:
            print(f"Erro ao conectar ao MongoDB: {e}")
            return False
        return True
    
    def create_indexes(self):
        """Cria índices únicos para email"""
        try:
            self.db.users.create_index("email", unique=True)
        except:
            pass
    
    def create_admin_user(self):
        """Cria usuário administrador padrão se não existir"""
        admin_exists = self.db.users.find_one({"email": "admin@sistema.com"})
        if not admin_exists:
            admin_user = {
                "name": "Administrador",
                "email": "admin@sistema.com",
                "password": self.hash_password("admin123"),
                "user_type": "admin",
                "created_at": datetime.now()
            }
            self.db.users.insert_one(admin_user)
            print("Usuário administrador criado: admin@sistema.com / admin123")
    
    def hash_password(self, password):
        return hashlib.sha256(password.encode()).hexdigest()
    
    def authenticate(self, email, password):
        user = self.db.users.find_one({"email": email})
        if user and user["password"] == self.hash_password(password):
            return user
        return None
    
    def create_user(self, name, email, password, user_type, additional_data=None):
        try:
            user_data = {
                "name": name,
                "email": email,
                "password": self.hash_password(password),
                "user_type": user_type,
                "created_at": datetime.now()
            }
            if additional_data:
                for key, value in additional_data.items():
                    if isinstance(value, date) and not isinstance(value, datetime):
                        additional_data[key] = datetime.combine(value, datetime.min.time())
                user_data.update(additional_data)

            
            result = self.db.users.insert_one(user_data)
            return result.inserted_id
        except pymongo.errors.DuplicateKeyError:
            return None
    
    def get_users_by_type(self, user_type):
        return list(self.db.users.find({"user_type": user_type}))
    
    def update_user(self, user_id, data):
        try:
            result = self.db.users.update_one(
                {"_id": ObjectId(user_id)},
                {"$set": data}
            )
            return result.modified_count > 0
        except:
            return False
    
    def delete_user(self, user_id):
        try:
            result = self.db.users.delete_one({"_id": ObjectId(user_id)})
            return result.deleted_count > 0
        except:
            return False
    
    def create_report(self, doctor_id, patient_id, report_data):
        try:
            report = {
                "doctor_id": ObjectId(doctor_id),
                "patient_id": ObjectId(patient_id),
                "report_data": report_data,
                "created_at": datetime.now()
            }
            result = self.db.reports.insert_one(report)
            return result.inserted_id
        except:
            return None
    
    def get_patient_reports(self, patient_id):
        return list(self.db.reports.find({"patient_id": ObjectId(patient_id)}))
    
    def get_all_reports(self):
        pipeline = [
            {
                "$lookup": {
                    "from": "users",
                    "localField": "doctor_id",
                    "foreignField": "_id",
                    "as": "doctor"
                }
            },
            {
                "$lookup": {
                    "from": "users",
                    "localField": "patient_id",
                    "foreignField": "_id",
                    "as": "patient"
                }
            },
            {
                "$unwind": "$doctor"
            },
            {
                "$unwind": "$patient"
            }
        ]
        return list(self.db.reports.aggregate(pipeline))

class LoginWindow(QDialog):
    def __init__(self, db_manager):
        super().__init__()
        self.db_manager = db_manager
        self.user = None
        self.main_window = None
        self.init_ui()
    
    def init_ui(self):
        self.setWindowTitle("Sistema Médico - Login")
        self.setGeometry(300, 300, 400, 300)
        self.setStyleSheet("""
            QWidget { 
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white;
            }
            QGroupBox {
                background: rgba(255, 255, 255, 0.1);
                border: 1px solid rgba(255, 255, 255, 0.2);
                border-radius: 10px;
                padding: 20px;
                margin: 20px;
                color: black;
            }
            QLineEdit {
                padding: 10px;
                border: none;
                border-radius: 5px;
                background: rgba(255, 255, 255, 0.9);
                color: black;
                font-size: 14px;
            }
            QPushButton {
                padding: 12px 24px;
                background: #4CAF50;
                color: white;
                border: none;
                border-radius: 5px;
                font-size: 14px;
                font-weight: bold;
            }
            QPushButton:hover {
                background: #45a049;
            }
            QLabel {
                font-size: 16px;
                font-weight: bold;
                color: black;
            }
        """)
        
        layout = QVBoxLayout()
        
        # Título
        title = QLabel("🏥 Sistema Médico")
        title.setAlignment(Qt.AlignCenter)
        title.setFont(QFont("", 24, QFont.Bold))
        layout.addWidget(title)
        
        # Formulário de login
        login_group = QGroupBox("Login")
        form_layout = QFormLayout()
        
        self.email_input = QLineEdit()
        self.email_input.setPlaceholderText("seu.email@exemplo.com")
        form_layout.addRow("Email:", self.email_input)
        
        self.password_input = QLineEdit()
        self.password_input.setEchoMode(QLineEdit.Password)
        self.password_input.setPlaceholderText("sua senha")
        form_layout.addRow("Senha:", self.password_input)
        
        login_group.setLayout(form_layout)
        layout.addWidget(login_group)
        
        # Botão de login
        self.login_btn = QPushButton("Entrar")
        self.login_btn.clicked.connect(self.login)
        layout.addWidget(self.login_btn)
        
        # Info do admin
        info_label = QLabel("👨‍💼 Admin padrão: admin@sistema.com / admin123")
        info_label.setAlignment(Qt.AlignCenter)
        info_label.setStyleSheet("font-size: 12px; margin-top: 20px;")
        layout.addWidget(info_label)
        
        self.setLayout(layout)
        
        # Enter para login
        self.password_input.returnPressed.connect(self.login)
    
    def login(self):
        email = self.email_input.text().strip()
        password = self.password_input.text()
        
        print(f"Tentando login com: {email}")
        
        if not email or not password:
            QMessageBox.warning(self, "Erro", "Preencha email e senha!")
            return
        
        user = self.db_manager.authenticate(email, password)
        if user:
            print(f"Login bem sucedido para: {user['name']} ({user['user_type']})")
            self.user = user
            # Fecha o diálogo de login e abre a janela principal
            self.accept()
        else:
            print("Login falhou - credenciais inválidas")
            QMessageBox.warning(self, "Erro", "Email ou senha inválidos!")
            self.password_input.clear()
    
    def accept(self):
        print("LoginWindow.accept() chamado")
        # Não chama super().accept() ainda
        # Abre a janela principal primeiro
        if self.user:
            print(f"Abrindo janela principal para: {self.user['name']}")
            self.hide()  # Esconde o login
            self.main_window = MainWindow(self.db_manager, self.user)
            self.main_window.login_window = self
            self.main_window.show()
            print("Janela principal aberta")
            # Só aceita o diálogo depois que a janela principal estiver visível
            QDialog.accept(self)
        else:
            print("Erro: usuário não definido")

class HypertensionAssessment(QWidget):
    def __init__(self, db_manager, user):
        super().__init__()
        self.db_manager = db_manager
        self.user = user
        self.init_ui()
    
    def init_ui(self):
        # Widget de conteúdo para scroll
        content = QWidget()
        content_layout = QVBoxLayout(content)
        content_layout.setContentsMargins(20,20,20,20)
        content_layout.setSpacing(15)
        
        # Seleção de paciente (apenas para médicos)
        if self.user["user_type"] == "doctor":
            patient_group = QGroupBox("👤 Selecionar Paciente")
            patient_layout = QFormLayout()
            
            self.patient_combo = QComboBox()
            self.load_patients()
            patient_layout.addRow("Paciente:", self.patient_combo)
            
            patient_group.setLayout(patient_layout)
            content_layout.addWidget(patient_group)

        # --- Autoavaliação ---
        auto_gbox = QGroupBox("📝 Autoavaliação")
        auto_form = QFormLayout()
        self.idade = QSpinBox(); self.idade.setRange(0, 120); self.idade.setSuffix(" anos")
        auto_form.addRow("Idade (anos):", self.idade)
        self.sexo_m = QCheckBox("Masculino?"); auto_form.addRow("Sexo masculino:", self.sexo_m)
        self.hist_fam = QCheckBox(); auto_form.addRow("Histórico familiar hipertensão:", self.hist_fam)
        self.altura = QDoubleSpinBox(); self.altura.setRange(0,300); self.altura.setSuffix(" cm")
        auto_form.addRow("Altura (cm):", self.altura)
        self.peso = QDoubleSpinBox(); self.peso.setRange(0,500); self.peso.setDecimals(1); self.peso.setSuffix(" kg")
        auto_form.addRow("Peso (kg):", self.peso)
        self.imc = QLineEdit(); self.imc.setReadOnly(True); auto_form.addRow("IMC (calculado):", self.imc)
        self.altura.valueChanged.connect(self.calcular_imc)
        self.peso.valueChanged.connect(self.calcular_imc)
        self.frutas = QSpinBox(); self.frutas.setRange(0, 20); auto_form.addRow("Porções frutas/vegetais dia:", self.frutas)
        self.exercicio = QSpinBox(); self.exercicio.setRange(0,10000); self.exercicio.setSuffix(" min")
        auto_form.addRow("Minutos exercício semana:", self.exercicio)
        self.fuma = QCheckBox(); auto_form.addRow("Fuma atualmente:", self.fuma)
        self.alcool = QSpinBox(); self.alcool.setRange(0,100); self.alcool.setSuffix(" doses")
        auto_form.addRow("Bebidas alcoólicas semana:", self.alcool)
        self.estresse = QSpinBox(); self.estresse.setRange(0,10); auto_form.addRow("Nível estresse (0-10):", self.estresse)
        self.sono = QCheckBox(); auto_form.addRow("Sono qualidade ruim:", self.sono)
        auto_gbox.setLayout(auto_form)
        content_layout.addWidget(auto_gbox)

        # --- Exames Médicos opcionais ---
        self.chk_exames = QCheckBox("Possui dados de exame médico?")
        self.chk_exames.stateChanged.connect(self.toggle_exames)
        content_layout.addWidget(self.chk_exames)

        self.exame_gbox = QGroupBox("🩺 Exames Médicos (opcional)")
        exame_form = QFormLayout()
        def make_spin(maxv, suffix=""):
            sb = QDoubleSpinBox(); sb.setRange(0, maxv); sb.setDecimals(1); sb.setSuffix(suffix)
            sb.setSpecialValueText("nulo"); return sb
        self.ldl    = make_spin(500, " mg/dL"); exame_form.addRow("Colesterol LDL (mg/dL):", self.ldl)
        self.hdl    = make_spin(200, " mg/dL"); exame_form.addRow("Colesterol HDL (mg/dL):", self.hdl)
        self.trig   = make_spin(1000, " mg/dL"); exame_form.addRow("Triglicerídeos (mg/dL):", self.trig)
        self.glic   = make_spin(500, " mg/dL"); exame_form.addRow("Glicemia jejum (mg/dL):", self.glic)
        self.hba1c  = make_spin(20, " %");     exame_form.addRow("HbA1c (%):", self.hba1c)
        self.creat  = make_spin(10, " mg/dL"); exame_form.addRow("Creatinina (mg/dL):", self.creat)
        self.protein= QCheckBox();          exame_form.addRow("Proteinúria positiva:", self.protein)
        self.apneia = QCheckBox();          exame_form.addRow("Diagnóstico apneia sono:", self.apneia)
        self.cortisol = make_spin(100, " µg/dL"); exame_form.addRow("Cortisol sérico (µg/dL):", self.cortisol)
        self.mutacao = QCheckBox();             exame_form.addRow("Mutação genética hipertensão:", self.mutacao)
        self.bpm     = make_spin(200, " bpm");   exame_form.addRow("BPM repouso:", self.bpm)
        self.pm25    = make_spin(500, " µg/m³"); exame_form.addRow("Índice PM2.5:", self.pm25)
        self.exame_gbox.setLayout(exame_form)
        content_layout.addWidget(self.exame_gbox)

        # --- Botões ---
        btns = QHBoxLayout()
        self.btn_avaliar = QPushButton("Avaliar Hipertensão")
        self.btn_avaliar.clicked.connect(self.avaliar_hipertensao)
        btns.addWidget(self.btn_avaliar)
        
        if self.user["user_type"] == "doctor":
            self.btn_salvar = QPushButton("Salvar Relatório")
            self.btn_salvar.clicked.connect(self.salvar_relatorio)
            self.btn_salvar.setEnabled(False)
            btns.addWidget(self.btn_salvar)
        
        self.btn_pdf = QPushButton("Gerar PDF")
        self.btn_pdf.clicked.connect(self.gerar_pdf)
        self.btn_pdf.setEnabled(False)
        btns.addWidget(self.btn_pdf)
        content_layout.addLayout(btns)

        # --- Resultado ---
        lbl = QLabel("🖥️ Resultado da Avaliação:"); lbl.setFont(QFont("",12,QFont.Bold))
        content_layout.addWidget(lbl)
        self.result = QPlainTextEdit(); self.result.setReadOnly(True)
        self.result.setStyleSheet("background: #EFEFEF;")
        self.result.setMinimumHeight(200)
        content_layout.addWidget(self.result)

        # Scroll area
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setWidget(content)

        # Layout principal
        main = QVBoxLayout(self)
        main.addWidget(scroll)

        # Oculta exames por padrão
        self.toggle_exames(0)
        self.last_assessment = None
    
    def load_patients(self):
        """Carrega pacientes no combo box"""
        patients = self.db_manager.get_users_by_type("patient")
        self.patient_combo.clear()
        for patient in patients:
            self.patient_combo.addItem(patient["name"], patient["_id"])
    
    def calcular_imc(self):
        h = self.altura.value() / 100
        if h > 0:
            imc = self.peso.value() / (h * h)
            self.imc.setText(f"{imc:.1f}")
        else:
            self.imc.clear()

    def toggle_exames(self, estado):
        self.exame_gbox.setVisible(estado == Qt.Checked)
    
    def avaliar_hipertensao(self):
        # Monta dados de autoavaliação
        auto = {
            "idade_anos": self.idade.value(),
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
                "colesterol_ldl_mg_dL":     None if self.ldl.value()==0 else self.ldl.value(),
                "colesterol_hdl_mg_dL":     None if self.hdl.value()==0 else self.hdl.value(),
                "triglicerideos_mg_dL":     None if self.trig.value()==0 else self.trig.value(),
                "glicemia_jejum_mg_dL":     None if self.glic.value()==0 else self.glic.value(),
                "hba1c_percent":            None if self.hba1c.value()==0 else self.hba1c.value(),
                "creatinina_mg_dL":         None if self.creat.value()==0 else self.creat.value(),
                "proteinuria_positiva":     self.protein.isChecked(),
                "diagnostico_apneia_sono":  self.apneia.isChecked(),
                "cortisol_serico_ug_dL":    None if self.cortisol.value()==0 else self.cortisol.value(),
                "mutacao_genetica_hipertensao": self.mutacao.isChecked(),
                "bpm_repouso":              None if self.bpm.value()==0 else self.bpm.value(),
                "indice_pm25":              None if self.pm25.value()==0 else self.pm25.value()
            }
        
        # Assessment data
        assessment_data = {
            "autoavaliacao": auto,
            "exames": exames,
            "timestamp": datetime.now().isoformat()
        }
        
        # Simula avaliação de IA (substitua pela integração real com Gemini)
        resultado = self.simulate_ai_assessment(assessment_data)
        
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
        auto = data["autoavaliacao"]
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
    
    def salvar_relatorio(self):
        """Salva relatório no banco de dados (apenas médicos)"""
        if self.user["user_type"] != "doctor":
            return
        
        if not self.last_assessment:
            QMessageBox.warning(self, "Erro", "Realize uma avaliação primeiro!")
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
            QMessageBox.information(self, "Sucesso", "Relatório salvo com sucesso!")
            self.btn_salvar.setEnabled(False)
        else:
            QMessageBox.warning(self, "Erro", "Erro ao salvar relatório!")
    
    def gerar_pdf(self):
        if not self.last_assessment:
            QMessageBox.warning(self, "Erro", "Realize uma avaliação primeiro!")
            return
        
        # Cria PDF
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Arial", size=10)
        
        # Título
        pdf.set_font("Arial", 'B', 16)
        pdf.cell(0, 10, 'RELATÓRIO DE AVALIAÇÃO DE HIPERTENSÃO', 0, 1, 'C')
        pdf.ln(5)
        
        # Dados do usuário
        pdf.set_font("Arial", 'B', 12)
        if self.user["user_type"] == "doctor" and self.patient_combo.currentData():
            patient_name = self.patient_combo.currentText()
            pdf.cell(0, 8, f'Paciente: {patient_name}', 0, 1)
            pdf.cell(0, 8, f'Médico: {self.user["name"]}', 0, 1)
        else:
            pdf.cell(0, 8, f'Usuário: {self.user["name"]}', 0, 1)
        
        pdf.cell(0, 8, f'Data: {datetime.now().strftime("%d/%m/%Y %H:%M")}', 0, 1)
        pdf.ln(5)
        
        # Dados enviados
        pdf.set_font("Arial", 'B', 12)
        pdf.cell(0, 8, 'DADOS DA AVALIAÇÃO:', 0, 1)
        pdf.set_font("Arial", size=8)
        
        input_text = json.dumps(self.last_assessment["input_data"], 
                               ensure_ascii=False, indent=2)
        # Limita o tamanho do texto para caber no PDF
        if len(input_text) > 2000:
            input_text = input_text[:2000] + "..."
        
        pdf.multi_cell(0, 4, input_text.encode('latin-1', 'replace').decode('latin-1'))
        pdf.ln(5)
        
        # Resultado da IA
        pdf.set_font("Arial", 'B', 12)
        pdf.cell(0, 8, 'RESULTADO DA AVALIAÇÃO:', 0, 1)
        pdf.set_font("Arial", size=10)
        
        # Converte resultado para latin-1 para compatibilidade com PDF
        result_text = self.last_assessment["ai_result"]
        result_text = result_text.encode('latin-1', 'replace').decode('latin-1')
        pdf.multi_cell(0, 6, result_text)
        
        # Salva arquivo
        filename = f"avaliacao_hipertensao_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
        pdf.output(filename)
        QMessageBox.information(self, "PDF Gerado", f"Arquivo salvo como: {filename}")

class UserManagement(QWidget):
    def __init__(self, db_manager, user):
        super().__init__()
        self.db_manager = db_manager
        self.user = user
        self.init_ui()
    
    def init_ui(self):
        layout = QVBoxLayout()
        
        # Tabs para diferentes tipos de usuários
        self.tabs = QTabWidget()
        
        if self.user["user_type"] == "admin":
            self.doctors_tab = self.create_users_tab("doctor", "Médicos")
            self.patients_tab = self.create_users_tab("patient", "Pacientes")
            self.tabs.addTab(self.doctors_tab, "👨‍⚕️ Médicos")
            self.tabs.addTab(self.patients_tab, "👤 Pacientes")
        
        layout.addWidget(self.tabs)
        self.setLayout(layout)
        
        self.refresh_all_tables()
    
    def create_users_tab(self, user_type, title):
        widget = QWidget()
        layout = QVBoxLayout()
        
        # Botões de ação
        btn_layout = QHBoxLayout()
        add_btn = QPushButton(f"➕ Adicionar {title[:-1]}")
        add_btn.clicked.connect(lambda: self.add_user(user_type))
        edit_btn = QPushButton(f"✏️ Editar {title[:-1]}")
        edit_btn.clicked.connect(lambda: self.edit_user(user_type))
        delete_btn = QPushButton(f"🗑️ Excluir {title[:-1]}")
        delete_btn.clicked.connect(lambda: self.delete_user(user_type))
        
        btn_layout.addWidget(add_btn)
        btn_layout.addWidget(edit_btn)
        btn_layout.addWidget(delete_btn)
        btn_layout.addStretch()
        
        layout.addLayout(btn_layout)
        
        # Tabela de usuários
        table = QTableWidget()
        table.setColumnCount(4)
        table.setHorizontalHeaderLabels(["ID", "Nome", "Email", "Data Criação"])
        table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        table.setSelectionBehavior(QTableWidget.SelectRows)
        
        layout.addWidget(table)
        widget.setLayout(layout)
        
        # Armazena referência da tabela
        setattr(self, f"{user_type}_table", table)
        
        return widget
    
    def refresh_all_tables(self):
        if self.user["user_type"] == "admin":
            self.refresh_table("doctor")
            self.refresh_table("patient")
    
    def refresh_table(self, user_type):
        table = getattr(self, f"{user_type}_table")
        users = self.db_manager.get_users_by_type(user_type)
        
        table.setRowCount(len(users))
        for i, user in enumerate(users):
            table.setItem(i, 0, QTableWidgetItem(str(user["_id"])))
            table.setItem(i, 1, QTableWidgetItem(user["name"]))
            table.setItem(i, 2, QTableWidgetItem(user["email"]))
            table.setItem(i, 3, QTableWidgetItem(user["created_at"].strftime("%d/%m/%Y")))
    
    def add_user(self, user_type):
        dialog = UserDialog(self.db_manager, user_type)
        if dialog.exec_():
            self.refresh_table(user_type)
    
    def edit_user(self, user_type):
        table = getattr(self, f"{user_type}_table")
        current_row = table.currentRow()
        if current_row < 0:
            QMessageBox.warning(self, "Erro", "Selecione um usuário para editar!")
            return
        
        user_id = table.item(current_row, 0).text()
        dialog = UserDialog(self.db_manager, user_type, user_id)
        if dialog.exec_():
            self.refresh_table(user_type)
    
    def delete_user(self, user_type):
        table = getattr(self, f"{user_type}_table")
        current_row = table.currentRow()
        if current_row < 0:
            QMessageBox.warning(self, "Erro", "Selecione um usuário para excluir!")
            return
        
        user_id = table.item(current_row, 0).text()
        user_name = table.item(current_row, 1).text()
        
        reply = QMessageBox.question(
            self, "Confirmar Exclusão", 
            f"Deseja realmente excluir o usuário '{user_name}'?",
            QMessageBox.Yes | QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            if self.db_manager.delete_user(user_id):
                QMessageBox.information(self, "Sucesso", "Usuário excluído com sucesso!")
                self.refresh_table(user_type)
            else:
                QMessageBox.warning(self, "Erro", "Erro ao excluir usuário!")

class UserDialog(QDialog):
    def __init__(self, db_manager, user_type, user_id=None):
        super().__init__()
        self.db_manager = db_manager
        self.user_type = user_type
        self.user_id = user_id
        self.init_ui()
        
        if user_id:
            self.load_user_data()
    
    def init_ui(self):
        self.setWindowTitle(f"{'Editar' if self.user_id else 'Adicionar'} {self.user_type.title()}")
        self.setModal(True)
        self.resize(400, 300)
        
        layout = QVBoxLayout()
        
        # Formulário
        form_layout = QFormLayout()
        
        self.name_input = QLineEdit()
        form_layout.addRow("Nome:", self.name_input)
        
        self.email_input = QLineEdit()
        form_layout.addRow("Email:", self.email_input)
        
        self.password_input = QLineEdit()
        self.password_input.setEchoMode(QLineEdit.Password)
        if self.user_id:
            self.password_input.setPlaceholderText("Deixe em branco para manter senha atual")
        form_layout.addRow("Senha:", self.password_input)
        
        # Campos específicos para médicos
        if self.user_type == "doctor":
            self.crm_input = QLineEdit()
            form_layout.addRow("CRM:", self.crm_input)
            
            self.specialty_input = QLineEdit()
            form_layout.addRow("Especialidade:", self.specialty_input)
        
        # Campos específicos para pacientes
        elif self.user_type == "patient":
            self.birth_date_input = QDateEdit()
            self.birth_date_input.setDate(QDate.currentDate())
            self.birth_date_input.setCalendarPopup(True)
            form_layout.addRow("Data Nascimento:", self.birth_date_input)
            
            self.phone_input = QLineEdit()
            form_layout.addRow("Telefone:", self.phone_input)
        
        layout.addLayout(form_layout)
        
        # Botões
        btn_layout = QHBoxLayout()
        save_btn = QPushButton("Salvar")
        save_btn.clicked.connect(self.save_user)
        cancel_btn = QPushButton("Cancelar")
        cancel_btn.clicked.connect(self.close)
        
        btn_layout.addWidget(save_btn)
        btn_layout.addWidget(cancel_btn)
        
        layout.addLayout(btn_layout)
        self.setLayout(layout)
    
    def load_user_data(self):
        """Carrega dados do usuário para edição"""
        from bson import ObjectId
        user = self.db_manager.db.users.find_one({"_id": ObjectId(self.user_id)})
        if user:
            self.name_input.setText(user["name"])
            self.email_input.setText(user["email"])
            
            if self.user_type == "doctor":
                self.crm_input.setText(user.get("crm", ""))
                self.specialty_input.setText(user.get("specialty", ""))
            elif self.user_type == "patient":
                if "birth_date" in user:
                    self.birth_date_input.setDate(user["birth_date"])
                self.phone_input.setText(user.get("phone", ""))
    
    def save_user(self):
        name = self.name_input.text().strip()
        email = self.email_input.text().strip()
        password = self.password_input.text()
        
        if not name or not email:
            QMessageBox.warning(self, "Erro", "Nome e email são obrigatórios!")
            return
        
        if not self.user_id and not password:
            QMessageBox.warning(self, "Erro", "Senha é obrigatória para novos usuários!")
            return
        
        # Dados específicos
        additional_data = {}
        if self.user_type == "doctor":
            additional_data["crm"] = self.crm_input.text().strip()
            additional_data["specialty"] = self.specialty_input.text().strip()
        elif self.user_type == "patient":
            additional_data["birth_date"] = self.birth_date_input.date().toPyDate()
            additional_data["phone"] = self.phone_input.text().strip()
        
        if self.user_id:
            # Editar usuário existente
            update_data = {"name": name, "email": email}
            if password:
                update_data["password"] = self.db_manager.hash_password(password)
            update_data.update(additional_data)
            
            if self.db_manager.update_user(self.user_id, update_data):
                QMessageBox.information(self, "Sucesso", "Usuário atualizado com sucesso!")
                self.accept()
            else:
                QMessageBox.warning(self, "Erro", "Erro ao atualizar usuário!")
        else:
            # Criar novo usuário
            user_id = self.db_manager.create_user(name, email, password, self.user_type, additional_data)
            if user_id:
                QMessageBox.information(self, "Sucesso", "Usuário criado com sucesso!")
                self.accept()
            else:
                QMessageBox.warning(self, "Erro", "Erro ao criar usuário! Verifique se o email já não está em uso.")

class ReportsView(QWidget):
    def __init__(self, db_manager, user):
        super().__init__()
        self.db_manager = db_manager
        self.user = user
        self.init_ui()
    
    def init_ui(self):
        layout = QVBoxLayout()
        
        # Botão de atualizar
        refresh_btn = QPushButton("🔄 Atualizar Relatórios")
        refresh_btn.clicked.connect(self.load_reports)
        layout.addWidget(refresh_btn)
        
        # Tabela de relatórios
        self.table = QTableWidget()
        if self.user["user_type"] == "patient":
            self.table.setColumnCount(3)
            self.table.setHorizontalHeaderLabels(["Médico", "Data", "Ações"])
        else:
            self.table.setColumnCount(4)
            self.table.setHorizontalHeaderLabels(["Paciente", "Médico", "Data", "Ações"])
        
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        layout.addWidget(self.table)
        
        self.setLayout(layout)
        self.load_reports()
    
    def load_reports(self):
        if self.user["user_type"] == "patient":
            reports = self.db_manager.get_patient_reports(self.user["_id"])
            self.table.setRowCount(len(reports))
            
            for i, report in enumerate(reports):
                # Busca dados do médico
                doctor = self.db_manager.db.users.find_one({"_id": report["doctor_id"]})
                doctor_name = doctor["name"] if doctor else "N/A"
                
                self.table.setItem(i, 0, QTableWidgetItem(doctor_name))
                self.table.setItem(i, 1, QTableWidgetItem(report["created_at"].strftime("%d/%m/%Y %H:%M")))
                
                # Botão para visualizar
                view_btn = QPushButton("👁️ Visualizar")
                view_btn.clicked.connect(lambda checked, r=report: self.view_report(r))
                self.table.setCellWidget(i, 2, view_btn)
        
        else:  # admin ou doctor
            reports = self.db_manager.get_all_reports()
            self.table.setRowCount(len(reports))
            
            for i, report in enumerate(reports):
                self.table.setItem(i, 0, QTableWidgetItem(report["patient"]["name"]))
                self.table.setItem(i, 1, QTableWidgetItem(report["doctor"]["name"]))
                self.table.setItem(i, 2, QTableWidgetItem(report["created_at"].strftime("%d/%m/%Y %H:%M")))
                
                # Botão para visualizar
                view_btn = QPushButton("👁️ Visualizar")
                view_btn.clicked.connect(lambda checked, r=report: self.view_report(r))
                self.table.setCellWidget(i, 3, view_btn)
    
    def view_report(self, report):
        dialog = ReportViewDialog(report)
        dialog.exec_()

class ReportViewDialog(QDialog):
    def __init__(self, report):
        super().__init__()
        self.report = report
        self.init_ui()
    
    def init_ui(self):
        self.setWindowTitle("Visualizar Relatório")
        self.setModal(True)
        self.resize(800, 600)
        
        layout = QVBoxLayout()
        
        # Informações do relatório
        info_layout = QFormLayout()
        
        # Verifica se o relatório tem dados de paciente/médico embedded
        if "patient" in self.report:
            info_layout.addRow("Paciente:", QLabel(self.report["patient"]["name"]))
            info_layout.addRow("Médico:", QLabel(self.report["doctor"]["name"]))
        
        info_layout.addRow("Data:", QLabel(self.report["created_at"].strftime("%d/%m/%Y %H:%M")))
        
        layout.addLayout(info_layout)
        
        # Dados da avaliação
        data_text = QTextEdit()
        data_text.setReadOnly(True)
        
        # Formata os dados para exibição
        report_data = self.report["report_data"]
        content = f"""
📊 DADOS DA AVALIAÇÃO:
{json.dumps(report_data.get('input_data', {}), ensure_ascii=False, indent=2)}

🤖 RESULTADO DA IA:
{report_data.get('ai_result', 'N/A')}
"""
        
        data_text.setPlainText(content)
        layout.addWidget(data_text)
        
        # Botão fechar
        close_btn = QPushButton("Fechar")
        close_btn.clicked.connect(self.accept)
        layout.addWidget(close_btn)
        
        self.setLayout(layout)

class PatientProfile(QWidget):
    def __init__(self, db_manager, user):
        super().__init__()
        self.db_manager = db_manager
        self.user = user
        self.init_ui()
    
    def init_ui(self):
        layout = QVBoxLayout()
        
        # Informações do perfil
        profile_group = QGroupBox("👤 Meu Perfil")
        form_layout = QFormLayout()
        
        self.name_input = QLineEdit(self.user["name"])
        form_layout.addRow("Nome:", self.name_input)
        
        self.email_input = QLineEdit(self.user["email"])
        form_layout.addRow("Email:", self.email_input)
        
        self.phone_input = QLineEdit(self.user.get("phone", ""))
        form_layout.addRow("Telefone:", self.phone_input)
        
        self.birth_date_input = QDateEdit()
        if "birth_date" in self.user:
            self.birth_date_input.setDate(self.user["birth_date"])
        self.birth_date_input.setCalendarPopup(True)
        form_layout.addRow("Data Nascimento:", self.birth_date_input)
        
        profile_group.setLayout(form_layout)
        layout.addWidget(profile_group)
        
        # Alterar senha
        password_group = QGroupBox("🔒 Alterar Senha")
        password_layout = QFormLayout()
        
        self.old_password_input = QLineEdit()
        self.old_password_input.setEchoMode(QLineEdit.Password)
        password_layout.addRow("Senha Atual:", self.old_password_input)
        
        self.new_password_input = QLineEdit()
        self.new_password_input.setEchoMode(QLineEdit.Password)
        password_layout.addRow("Nova Senha:", self.new_password_input)
        
        self.confirm_password_input = QLineEdit()
        self.confirm_password_input.setEchoMode(QLineEdit.Password)
        password_layout.addRow("Confirmar Senha:", self.confirm_password_input)
        
        password_group.setLayout(password_layout)
        layout.addWidget(password_group)
        
        # Botões
        btn_layout = QHBoxLayout()
        
        save_profile_btn = QPushButton("💾 Salvar Perfil")
        save_profile_btn.clicked.connect(self.save_profile)
        btn_layout.addWidget(save_profile_btn)
        
        save_password_btn = QPushButton("🔐 Alterar Senha")
        save_password_btn.clicked.connect(self.change_password)
        btn_layout.addWidget(save_password_btn)
        
        layout.addLayout(btn_layout)
        layout.addStretch()
        
        self.setLayout(layout)
    
    def save_profile(self):
        name = self.name_input.text().strip()
        email = self.email_input.text().strip()
        phone = self.phone_input.text().strip()
        birth_date = self.birth_date_input.date().toPyDate()
        
        if not name or not email:
            QMessageBox.warning(self, "Erro", "Nome e email são obrigatórios!")
            return
        
        update_data = {
            "name": name,
            "email": email,
            "phone": phone,
            "birth_date": birth_date
        }
        
        if self.db_manager.update_user(str(self.user["_id"]), update_data):
            # Atualiza dados locais
            self.user.update(update_data)
            QMessageBox.information(self, "Sucesso", "Perfil atualizado com sucesso!")
        else:
            QMessageBox.warning(self, "Erro", "Erro ao atualizar perfil!")
    
    def change_password(self):
        old_password = self.old_password_input.text()
        new_password = self.new_password_input.text()
        confirm_password = self.confirm_password_input.text()
        
        if not old_password or not new_password or not confirm_password:
            QMessageBox.warning(self, "Erro", "Preencha todos os campos!")
            return
        
        if new_password != confirm_password:
            QMessageBox.warning(self, "Erro", "Nova senha e confirmação não coincidem!")
            return
        
        # Verifica senha atual
        if self.user["password"] != self.db_manager.hash_password(old_password):
            QMessageBox.warning(self, "Erro", "Senha atual incorreta!")
            return
        
        # Atualiza senha
        update_data = {"password": self.db_manager.hash_password(new_password)}
        if self.db_manager.update_user(str(self.user["_id"]), update_data):
            self.user["password"] = update_data["password"]
            QMessageBox.information(self, "Sucesso", "Senha alterada com sucesso!")
            self.old_password_input.clear()
            self.new_password_input.clear()
            self.confirm_password_input.clear()
        else:
            QMessageBox.warning(self, "Erro", "Erro ao alterar senha!")

class MainWindow(QWidget):
    def __init__(self, db_manager, user):
        super().__init__()
        self.db_manager = db_manager
        self.user = user
        self.login_window = None
        self.init_ui()
    
    def init_ui(self):
        self.setWindowTitle(f"Sistema Médico - {self.user['name']} ({self.user['user_type'].title()})")
        self.setGeometry(100, 100, 1200, 800)
        
        # CSS melhorado
        self.setStyleSheet("""
            QWidget { 
                background: #F5F5F5; 
                font-family: 'Segoe UI', sans-serif;
            }
            QGroupBox { 
                border: 2px solid #E0E0E0; 
                border-radius: 8px; 
                margin-top: 15px;
                padding-top: 10px;
                background: white;
            }
            QGroupBox::title { 
                subcontrol-origin: margin; 
                subcontrol-position: top left; 
                padding: 0 10px; 
                font-weight: bold;
                color: #333;
                background: #F5F5F5;
            }
            QLabel, QSpinBox, QDoubleSpinBox, QLineEdit, QPlainTextEdit, QComboBox {
                font-size: 13px;
                padding: 5px;
            }
            QPushButton {
                padding: 10px 20px; 
                font-size: 13px;
                border-radius: 6px;
                border: none;
                font-weight: bold;
            }
            QPushButton:hover { opacity: 0.8; }
            QTabWidget::pane { border: 1px solid #C0C0C0; background: white; }
            QTabBar::tab { 
                background: #E0E0E0; 
                padding: 10px 15px; 
                margin-right: 2px;
                border-top-left-radius: 6px;
                border-top-right-radius: 6px;
            }
            QTabBar::tab:selected { background: white; border-bottom: none; }
            QTableWidget { 
                gridline-color: #E0E0E0; 
                background: white;
                selection-background-color: #E3F2FD;
            }
            QHeaderView::section { 
                background: #F0F0F0; 
                padding: 8px; 
                border: none;
                font-weight: bold;
            }
        """)
        
        layout = QVBoxLayout()
        
        # Header
        header = QLabel(f"🏥 Sistema Médico - Bem-vindo, {self.user['name']}!")
        header.setStyleSheet("""
            font-size: 18px; 
            font-weight: bold; 
            color: #2C3E50;
            padding: 15px;
            background: white;
            border-radius: 8px;
            margin-bottom: 10px;
        """)
        layout.addWidget(header)
        
        # Tabs principais
        self.tabs = QTabWidget()
        
        # Diferentes abas baseadas no tipo de usuário
        if self.user["user_type"] == "admin":
            self.tabs.addTab(UserManagement(self.db_manager, self.user), "👥 Gerenciar Usuários")
            self.tabs.addTab(ReportsView(self.db_manager, self.user), "📊 Todos os Relatórios")
        
        elif self.user["user_type"] == "doctor":
            self.tabs.addTab(HypertensionAssessment(self.db_manager, self.user), "🩺 Nova Avaliação")
            self.tabs.addTab(ReportsView(self.db_manager, self.user), "📋 Meus Relatórios")
        
        elif self.user["user_type"] == "patient":
            self.tabs.addTab(PatientProfile(self.db_manager, self.user), "👤 Meu Perfil")
            self.tabs.addTab(ReportsView(self.db_manager, self.user), "📋 Meus Relatórios")
        
        layout.addWidget(self.tabs)
        
        # Botão logout
        logout_btn = QPushButton("🚪 Sair")
        logout_btn.setStyleSheet("background: #E74C3C; color: white;")
        logout_btn.clicked.connect(self.logout)
        layout.addWidget(logout_btn)
        
        self.setLayout(layout)
    
    def logout(self):
        self.close()
        # Volta à tela de login ou cria uma nova
        if self.login_window:
            self.login_window.email_input.clear()
            self.login_window.password_input.clear()
            self.login_window.show()
        else:
            login_window = LoginWindow(self.db_manager)
            login_window.exec_()

def main():
    app = QApplication(sys.argv)
    
    try:
        print("Iniciando Sistema Médico...")
        
        # Inicializa banco de dados
        print("Conectando ao MongoDB...")
        db_manager = DatabaseManager()
        if not db_manager.client:
            QMessageBox.critical(None, "Erro", "Não foi possível conectar ao MongoDB!")
            return
        
        print("Conexão MongoDB OK")
        
        # Mostra tela de login
        print("Abrindo tela de login...")
        login_window = LoginWindow(db_manager)
        login_result = login_window.exec_()
        
        print(f"Resultado do login: {login_result}")
        
        if login_result == QDialog.Accepted and login_window.user:
            print("Login aceito, executando aplicação principal...")
            # Login bem sucedido, a janela principal já foi aberta
            # Agora executa o loop principal da aplicação
            app.exec_()
            print("Aplicação encerrada normalmente")
        else:
            print("Login cancelado ou falhou")
        
    except Exception as e:
        QMessageBox.critical(None, "Erro Crítico", f"Erro inesperado: {str(e)}")
        print(f"Erro crítico: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        print("Sistema encerrado.")

if __name__ == "__main__":
    main()