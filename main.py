import sys
import json
import hashlib
from datetime import datetime
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QFormLayout, 
    QGroupBox, QLabel, QLineEdit, QPushButton, QStackedWidget, QListWidget, 
    QTextEdit, QSpinBox, QDoubleSpinBox, QCheckBox, QPlainTextEdit, QScrollArea,
    QMessageBox, QComboBox, QTableWidget, QTableWidgetItem, QHeaderView, QTabWidget,
    QDialog, QDialogButtonBox
)
from PyQt5.QtGui import QFont, QIcon
from PyQt5.QtCore import Qt, QTimer
from fpdf import FPDF
import sqlite3
from google import genai
from google.genai import types

class DatabaseManager:
    def __init__(self, db_path="hypertension_system.db"):
        self.db_path = db_path
        self.init_database()

    def init_database(self):
        """Inicializa o banco de dados com todas as tabelas necessárias"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Tabela de usuários
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS usuarios (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                tipo TEXT NOT NULL CHECK(tipo IN ('admin', 'medico', 'paciente')),
                nome TEXT NOT NULL,
                email TEXT,
                telefone TEXT,
                crm TEXT, -- Para médicos
                especialidade TEXT, -- Para médicos
                data_nascimento DATE, -- Para pacientes
                data_criacao TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                ativo BOOLEAN DEFAULT 1
            )
        ''')
        
        # Tabela de pacientes (dados clínicos adicionais)
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS pacientes_dados (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                usuario_id INTEGER,
                altura_cm REAL,
                peso_kg REAL,
                historico_familiar_hipertensao BOOLEAN,
                observacoes TEXT,
                FOREIGN KEY (usuario_id) REFERENCES usuarios (id)
            )
        ''')
        
        # Tabela de avaliações/relatórios
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS avaliacoes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                paciente_id INTEGER,
                medico_id INTEGER,
                data_avaliacao TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                dados_autoavaliacao TEXT, -- JSON
                dados_exames TEXT, -- JSON
                resultado_ia TEXT,
                observacoes_medico TEXT,
                status TEXT DEFAULT 'pendente' CHECK(status IN ('pendente', 'revisado', 'finalizado')),
                FOREIGN KEY (paciente_id) REFERENCES usuarios (id),
                FOREIGN KEY (medico_id) REFERENCES usuarios (id)
            )
        ''')
        
        # Criar usuário admin padrão se não existir
        cursor.execute("SELECT COUNT(*) FROM usuarios WHERE tipo = 'admin'")
        if cursor.fetchone()[0] == 0:
            admin_password = self.hash_password("admin123")
            cursor.execute('''
                INSERT INTO usuarios (username, password_hash, tipo, nome, email)
                VALUES (?, ?, 'admin', 'Administrador', 'admin@sistema.com')
            ''', ("admin", admin_password))
        
        conn.commit()
        conn.close()
    
    def hash_password(self, password):
        """Hash da senha usando SHA-256"""
        return hashlib.sha256(password.encode()).hexdigest()
    
    def authenticate_user(self, username, password):
        """Autentica usuário e retorna dados se válido"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        password_hash = self.hash_password(password)
        cursor.execute('''
            SELECT id, username, tipo, nome, email, ativo
            FROM usuarios 
            WHERE username = ? AND password_hash = ? AND ativo = 1
        ''', (username, password_hash))
        
        result = cursor.fetchone()
        conn.close()
        
        if result:
            return {
                'id': result[0],
                'username': result[1],
                'tipo': result[2],
                'nome': result[3],
                'email': result[4],
                'ativo': result[5]
            }
        return None
    
    def create_user(self, username, password, tipo, nome, email="", telefone="", crm="", especialidade="", data_nascimento=""):
        """Cria novo usuário"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            password_hash = self.hash_password(password)
            cursor.execute('''
                INSERT INTO usuarios (username, password_hash, tipo, nome, email, telefone, crm, especialidade, data_nascimento)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (username, password_hash, tipo, nome, email, telefone, crm, especialidade, data_nascimento))
            
            user_id = cursor.lastrowid
            
            # Se for paciente, criar registro adicional
            if tipo == 'paciente':
                cursor.execute('''
                    INSERT INTO pacientes_dados (usuario_id) VALUES (?)
                ''', (user_id,))
            
            conn.commit()
            return user_id
        except sqlite3.IntegrityError:
            return None
        finally:
            conn.close()
    
    def get_users_by_type(self, tipo):
        """Retorna usuários por tipo"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT id, username, nome, email, telefone, crm, especialidade, data_nascimento, ativo
            FROM usuarios 
            WHERE tipo = ?
            ORDER BY nome
        ''', (tipo,))
        
        results = cursor.fetchall()
        conn.close()
        return results
    
    def save_avaliacao(self, paciente_id, medico_id, dados_auto, dados_exames, resultado_ia, observacoes=""):
        """Salva uma avaliação"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO avaliacoes (paciente_id, medico_id, dados_autoavaliacao, dados_exames, resultado_ia, observacoes_medico)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (paciente_id, medico_id, json.dumps(dados_auto), json.dumps(dados_exames), resultado_ia, observacoes))
        
        avaliacao_id = cursor.lastrowid
        conn.commit()
        conn.close()
        return avaliacao_id
    
    def get_avaliacoes_paciente(self, paciente_id):
        """Retorna avaliações de um paciente"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT a.id, a.data_avaliacao, u.nome as medico_nome, a.status, 
                   a.dados_autoavaliacao, a.dados_exames, a.resultado_ia, a.observacoes_medico
            FROM avaliacoes a
            LEFT JOIN usuarios u ON a.medico_id = u.id
            WHERE a.paciente_id = ?
            ORDER BY a.data_avaliacao DESC
        ''', (paciente_id,))
        
        results = cursor.fetchall()
        conn.close()
        return results
    
    def get_all_avaliacoes(self):
        """Retorna todas as avaliações (para admin/médico)"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT a.id, a.data_avaliacao, up.nome as paciente_nome, um.nome as medico_nome, a.status
            FROM avaliacoes a
            LEFT JOIN usuarios up ON a.paciente_id = up.id
            LEFT JOIN usuarios um ON a.medico_id = um.id
            ORDER BY a.data_avaliacao DESC
        ''')
        
        results = cursor.fetchall()
        conn.close()
        return results

class LoginWindow(QWidget):
    def __init__(self, db_manager, on_login_success):
        super().__init__()
        self.db_manager = db_manager
        self.on_login_success = on_login_success
        self.init_ui()
    
    def init_ui(self):
        self.setWindowTitle("🏥 Sistema de Hipertensão - Login")
        self.setFixedSize(400, 300)
        self.setStyleSheet("""
            QWidget {
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            }
            QGroupBox {
                background: white;
                border-radius: 10px;
                padding: 20px;
                margin: 20px;
            }
            QLineEdit {
                padding: 10px;
                border: 2px solid #ddd;
                border-radius: 5px;
                font-size: 14px;
            }
            QLineEdit:focus {
                border-color: #667eea;
            }
            QPushButton {
                background: #667eea;
                color: white;
                border: none;
                padding: 12px;
                border-radius: 5px;
                font-size: 14px;
                font-weight: bold;
            }
            QPushButton:hover {
                background: #5a6fd8;
            }
        """)
        
        layout = QVBoxLayout()
        
        # Grupo de login
        login_group = QGroupBox()
        form_layout = QFormLayout()
        
        title = QLabel("🏥 Sistema de Hipertensão")
        title.setAlignment(Qt.AlignCenter)
        title.setFont(QFont("", 18, QFont.Bold))
        title.setStyleSheet("color: #333; margin-bottom: 20px;")
        
        self.username_edit = QLineEdit()
        self.username_edit.setPlaceholderText("Nome de usuário")
        
        self.password_edit = QLineEdit()
        self.password_edit.setPlaceholderText("Senha")
        self.password_edit.setEchoMode(QLineEdit.Password)
        self.password_edit.returnPressed.connect(self.login)
        
        self.login_btn = QPushButton("Entrar")
        self.login_btn.clicked.connect(self.login)
        
        form_layout.addRow(title)
        form_layout.addRow("Usuário:", self.username_edit)
        form_layout.addRow("Senha:", self.password_edit)
        form_layout.addRow("", self.login_btn)
        
        # Info de login padrão
        info_label = QLabel("Login padrão:\nAdmin: admin / admin123")
        info_label.setStyleSheet("color: #666; font-size: 12px; margin-top: 10px;")
        info_label.setAlignment(Qt.AlignCenter)
        form_layout.addRow(info_label)
        
        login_group.setLayout(form_layout)
        layout.addWidget(login_group)
        
        self.setLayout(layout)
    
    def login(self):
        username = self.username_edit.text().strip()
        password = self.password_edit.text()
        
        if not username or not password:
            QMessageBox.warning(self, "Erro", "Por favor, preencha todos os campos.")
            return
        
        user = self.db_manager.authenticate_user(username, password)
        if user:
            self.on_login_success(user)
        else:
            QMessageBox.warning(self, "Erro", "Usuário ou senha inválidos.")
            self.password_edit.clear()

class HypertensionEvaluationWidget(QWidget):
    def __init__(self, db_manager, current_user):
        super().__init__()
        self.db_manager = db_manager
        self.current_user = current_user
        self.last_payload = None
        self.init_ui()
        self.init_gemini()
    
    def init_gemini(self):
        """Inicializa a API do Gemini"""
        API_KEY = "AIzaSyAmraGN6apiXmyQTcgKaj-BaM_Zzro6IHk"  # Substitua pela sua chave
        try:
            self.gemini = genai.Client(api_key=API_KEY, http_options=types.HttpOptions(api_version="v1alpha"))
            self.chat = self.gemini.chats.create(model="gemini-2.0-flash")
        except Exception as e:
            print("Erro ao inicializar Gemini:", e)
            self.chat = None
    
    def init_ui(self):
        self.setStyleSheet("""
            QWidget { background: #FAFAFA; }
            QGroupBox { 
                border: 1px solid #CCCCCC; 
                border-radius: 5px; 
                margin-top: 10px;
                padding: 10px;
            }
            QGroupBox::title { 
                subcontrol-origin: margin; 
                subcontrol-position: top left; 
                padding: 0 5px; 
                font-weight: bold;
                color: #333;
            }
            QLabel, QSpinBox, QDoubleSpinBox, QLineEdit, QPlainTextEdit {
                font-size: 14px;
            }
            QPushButton {
                padding: 8px 16px; 
                font-size: 14px;
                border-radius: 5px;
                border: none;
            }
            QPushButton#avaliar { background-color: #4CAF50; color: white; }
            QPushButton#avaliar:hover { background-color: #45a049; }
            QPushButton#pdf { background-color: #2196F3; color: white; }
            QPushButton#pdf:hover { background-color: #1976D2; }
        """)

        # Widget de conteúdo para scroll
        content = QWidget()
        content_layout = QVBoxLayout(content)
        content_layout.setContentsMargins(20,20,20,20)
        content_layout.setSpacing(15)

        # Título
        title = QLabel("💓 Avaliação de Risco de Hipertensão")
        title.setFont(QFont("", 16, QFont.Bold))
        title.setStyleSheet("color: #333; margin-bottom: 10px;")
        content_layout.addWidget(title)

        # Seleção de paciente (para médicos)
        if self.current_user['tipo'] == 'medico':
            paciente_group = QGroupBox("👤 Seleção de Paciente")
            paciente_layout = QFormLayout()
            
            self.paciente_combo = QComboBox()
            self.load_pacientes()
            paciente_layout.addRow("Paciente:", self.paciente_combo)
            
            paciente_group.setLayout(paciente_layout)
            content_layout.addWidget(paciente_group)

        # --- Autoavaliação ---
        auto_gbox = QGroupBox("📝 Autoavaliação")
        auto_form = QFormLayout()
        self.idade = QSpinBox(); self.idade.setRange(0, 120); self.idade.setSuffix(" anos")
        auto_form.addRow("Idade:", self.idade)
        self.sexo_m = QCheckBox("Masculino"); auto_form.addRow("Sexo:", self.sexo_m)
        self.hist_fam = QCheckBox(); auto_form.addRow("Histórico familiar de hipertensão:", self.hist_fam)
        self.altura = QDoubleSpinBox(); self.altura.setRange(0,300); self.altura.setSuffix(" cm")
        auto_form.addRow("Altura:", self.altura)
        self.peso = QDoubleSpinBox(); self.peso.setRange(0,500); self.peso.setDecimals(1); self.peso.setSuffix(" kg")
        auto_form.addRow("Peso:", self.peso)
        self.imc = QLineEdit(); self.imc.setReadOnly(True); auto_form.addRow("IMC (calculado):", self.imc)
        self.altura.valueChanged.connect(self.calcular_imc)
        self.peso.valueChanged.connect(self.calcular_imc)
        self.frutas = QSpinBox(); self.frutas.setRange(0, 20); auto_form.addRow("Porções de frutas/vegetais por dia:", self.frutas)
        self.exercicio = QSpinBox(); self.exercicio.setRange(0,10000); self.exercicio.setSuffix(" min")
        auto_form.addRow("Minutos de exercício por semana:", self.exercicio)
        self.fuma = QCheckBox(); auto_form.addRow("Fuma atualmente:", self.fuma)
        self.alcool = QSpinBox(); self.alcool.setRange(0,100); self.alcool.setSuffix(" doses")
        auto_form.addRow("Bebidas alcoólicas por semana:", self.alcool)
        self.estresse = QSpinBox(); self.estresse.setRange(0,10); auto_form.addRow("Nível de estresse (0-10):", self.estresse)
        self.sono = QCheckBox(); auto_form.addRow("Sono de qualidade ruim:", self.sono)
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
            sb.setSpecialValueText("não informado"); return sb
        self.ldl = make_spin(500, " mg/dL"); exame_form.addRow("Colesterol LDL:", self.ldl)
        self.hdl = make_spin(200, " mg/dL"); exame_form.addRow("Colesterol HDL:", self.hdl)
        self.trig = make_spin(1000, " mg/dL"); exame_form.addRow("Triglicerídeos:", self.trig)
        self.glic = make_spin(500, " mg/dL"); exame_form.addRow("Glicemia em jejum:", self.glic)
        self.hba1c = make_spin(20, " %"); exame_form.addRow("HbA1c:", self.hba1c)
        self.creat = make_spin(10, " mg/dL"); exame_form.addRow("Creatinina:", self.creat)
        self.protein = QCheckBox(); exame_form.addRow("Proteinúria positiva:", self.protein)
        self.apneia = QCheckBox(); exame_form.addRow("Diagnóstico de apneia do sono:", self.apneia)
        self.cortisol = make_spin(100, " µg/dL"); exame_form.addRow("Cortisol sérico:", self.cortisol)
        self.mutacao = QCheckBox(); exame_form.addRow("Mutação genética para hipertensão:", self.mutacao)
        self.bpm = make_spin(200, " bpm"); exame_form.addRow("BPM em repouso:", self.bpm)
        self.pm25 = make_spin(500, " µg/m³"); exame_form.addRow("Índice PM2.5:", self.pm25)
        self.exame_gbox.setLayout(exame_form)
        content_layout.addWidget(self.exame_gbox)

        # --- Observações do médico ---
        if self.current_user['tipo'] == 'medico':
            obs_group = QGroupBox("📝 Observações do Médico")
            obs_layout = QVBoxLayout()
            self.observacoes_medico = QPlainTextEdit()
            self.observacoes_medico.setPlaceholderText("Digite suas observações sobre a avaliação...")
            obs_layout.addWidget(self.observacoes_medico)
            obs_group.setLayout(obs_layout)
            content_layout.addWidget(obs_group)

        # --- Botões ---
        btns = QHBoxLayout()
        self.btn_avaliar = QPushButton("🔍 Avaliar com IA")
        self.btn_avaliar.setObjectName("avaliar")
        self.btn_avaliar.clicked.connect(self.enviar_para_ia)
        btns.addWidget(self.btn_avaliar)
        
        self.btn_pdf = QPushButton("📄 Gerar PDF")
        self.btn_pdf.setObjectName("pdf")
        self.btn_pdf.clicked.connect(self.gerar_pdf)
        self.btn_pdf.setEnabled(False)
        btns.addWidget(self.btn_pdf)
        
        if self.current_user['tipo'] == 'medico':
            self.btn_salvar = QPushButton("💾 Salvar Avaliação")
            self.btn_salvar.clicked.connect(self.salvar_avaliacao)
            self.btn_salvar.setEnabled(False)
            btns.addWidget(self.btn_salvar)
        
        content_layout.addLayout(btns)

        # --- Resultado da IA ---
        result_group = QGroupBox("🤖 Resultado da Análise de IA")
        result_layout = QVBoxLayout()
        self.result = QPlainTextEdit()
        self.result.setReadOnly(True)
        self.result.setStyleSheet("background: #EFEFEF; border: 1px solid #ccc; border-radius: 5px; padding: 10px;")
        self.result.setMinimumHeight(200)
        result_layout.addWidget(self.result)
        result_group.setLayout(result_layout)
        content_layout.addWidget(result_group)

        # Scroll area
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setWidget(content)

        # Layout principal
        main = QVBoxLayout(self)
        main.addWidget(scroll)

        # Oculta exames por padrão
        self.toggle_exames(0)

    def load_pacientes(self):
        """Carrega lista de pacientes para médicos"""
        if self.current_user['tipo'] == 'medico':
            pacientes = self.db_manager.get_users_by_type('paciente')
            self.paciente_combo.clear()
            for paciente in pacientes:
                self.paciente_combo.addItem(f"{paciente[2]} ({paciente[1]})", paciente[0])

    def calcular_imc(self):
        h = self.altura.value() / 100
        if h > 0:
            imc = self.peso.value() / (h * h)
            self.imc.setText(f"{imc:.1f}")
        else:
            self.imc.clear()

    def toggle_exames(self, estado):
        self.exame_gbox.setVisible(estado == Qt.Checked)

    def enviar_para_ia(self):
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
                "colesterol_ldl_mg_dL": None if self.ldl.value()==0 else self.ldl.value(),
                "colesterol_hdl_mg_dL": None if self.hdl.value()==0 else self.hdl.value(),
                "triglicerideos_mg_dL": None if self.trig.value()==0 else self.trig.value(),
                "glicemia_jejum_mg_dL": None if self.glic.value()==0 else self.glic.value(),
                "hba1c_percent": None if self.hba1c.value()==0 else self.hba1c.value(),
                "creatinina_mg_dL": None if self.creat.value()==0 else self.creat.value(),
                "proteinuria_positiva": self.protein.isChecked(),
                "diagnostico_apneia_sono": self.apneia.isChecked(),
                "cortisol_serico_ug_dL": None if self.cortisol.value()==0 else self.cortisol.value(),
                "mutacao_genetica_hipertensao": self.mutacao.isChecked(),
                "bpm_repouso": None if self.bpm.value()==0 else self.bpm.value(),
                "indice_pm25": None if self.pm25.value()==0 else self.pm25.value()
            }
        
        # Payload final
        payload = {"autoavaliacao": auto, "exames": exames}
        self.last_payload = payload

        # Monta prompt
        prompt = (
            "Você é um especialista em cardiologia. Analise este JSON com dados de um paciente e forneça um "
            "diagnóstico completo sobre o risco de hipertensão em português brasileiro. "
            "Inclua: 1) Avaliação do risco atual, 2) Fatores de risco identificados, "
            "3) Recomendações específicas, 4) Necessidade de acompanhamento médico. "
            "Seja detalhado mas acessível:\n\n"
            f"```json\n{json.dumps(payload, ensure_ascii=False, indent=2)}\n```"
        )
        
        if not self.chat:
            self.result.setPlainText("Erro: IA indisponível. Verifique a chave da API do Gemini.")
            return
        
        self.btn_avaliar.setText("Analisando...")
        self.btn_avaliar.setEnabled(False)
        
        try:
            resp = self.chat.send_message(prompt)
            texto = resp.text
            self.result.setPlainText(texto)
            self.btn_pdf.setEnabled(True)
            if hasattr(self, 'btn_salvar'):
                self.btn_salvar.setEnabled(True)
        except Exception as e:
            texto = f"Erro ao chamar IA: {e}"
            self.result.setPlainText(texto)
        finally:
            self.btn_avaliar.setText("🔍 Avaliar com IA")
            self.btn_avaliar.setEnabled(True)

    def salvar_avaliacao(self):
        """Salva a avaliação no banco de dados"""
        if self.current_user['tipo'] != 'medico':
            return
        
        paciente_id = self.paciente_combo.currentData()
        if not paciente_id:
            QMessageBox.warning(self, "Erro", "Selecione um paciente.")
            return
        
        if not self.last_payload:
            QMessageBox.warning(self, "Erro", "Execute a avaliação primeiro.")
            return
        
        observacoes = self.observacoes_medico.toPlainText() if hasattr(self, 'observacoes_medico') else ""
        
        try:
            avaliacao_id = self.db_manager.save_avaliacao(
                paciente_id=paciente_id,
                medico_id=self.current_user['id'],
                dados_auto=self.last_payload['autoavaliacao'],
                dados_exames=self.last_payload['exames'],
                resultado_ia=self.result.toPlainText(),
                observacoes=observacoes
            )
            
            QMessageBox.information(self, "Sucesso", f"Avaliação salva com ID: {avaliacao_id}")
            self.btn_salvar.setEnabled(False)
        except Exception as e:
            QMessageBox.critical(self, "Erro", f"Erro ao salvar avaliação: {e}")

    def gerar_pdf(self):
        if not self.last_payload:
            QMessageBox.warning(self, "Erro", "Execute a avaliação primeiro.")
            return
        
        try:
            pdf = FPDF()
            pdf.add_page()
            pdf.set_font("Arial", size=12)
            
            # Cabeçalho
            pdf.set_font("Arial", 'B', 16)
            pdf.cell(0, 10, "RELATORIO DE AVALIACAO DE HIPERTENSAO", 0, 1, 'C')
            pdf.ln(10)
            
            # Informações do paciente
            pdf.set_font("Arial", 'B', 12)
            if self.current_user['tipo'] == 'medico' and hasattr(self, 'paciente_combo'):
                paciente_nome = self.paciente_combo.currentText()
                pdf.cell(0, 8, f"Paciente: {paciente_nome}", 0, 1)
            else:
                pdf.cell(0, 8, f"Paciente: {self.current_user['nome']}", 0, 1)
            
            if self.current_user['tipo'] == 'medico':
                pdf.cell(0, 8, f"Medico: {self.current_user['nome']}", 0, 1)
            
            pdf.cell(0, 8, f"Data: {datetime.now().strftime('%d/%m/%Y %H:%M')}", 0, 1)
            pdf.ln(5)
            
            # Dados da avaliação
            pdf.set_font("Arial", 'B', 12)
            pdf.cell(0, 8, "DADOS DA AVALIACAO:", 0, 1)
            pdf.set_font("Arial", size=10)
            
            auto_data = self.last_payload['autoavaliacao']
            pdf.cell(0, 6, f"Idade: {auto_data['idade_anos']} anos", 0, 1)
            pdf.cell(0, 6, f"Sexo: {'Masculino' if auto_data['sexo_masculino'] else 'Feminino'}", 0, 1)
            pdf.cell(0, 6, f"IMC: {auto_data.get('imc', 'N/A')}", 0, 1)
            pdf.cell(0, 6, f"Historico familiar: {'Sim' if auto_data['historico_familiar_hipertensao'] else 'Nao'}", 0, 1)
            pdf.cell(0, 6, f"Exercicio semanal: {auto_data['minutos_exercicio_semana']} min", 0, 1)
            pdf.cell(0, 6, f"Fuma: {'Sim' if auto_data['fuma_atualmente'] else 'Nao'}", 0, 1)
            pdf.cell(0, 6, f"Nivel de estresse: {auto_data['nivel_estresse_0_10']}/10", 0, 1)
            pdf.ln(5)
            
            # Exames (se houver)
            if self.last_payload['exames']:
                pdf.set_font("Arial", 'B', 12)
                pdf.cell(0, 8, "EXAMES MEDICOS:", 0, 1)
                pdf.set_font("Arial", size=10)
                exames = self.last_payload['exames']
                for key, value in exames.items():
                    if value is not None and value != False:
                        pdf.cell(0, 6, f"{key}: {value}", 0, 1)
                pdf.ln(5)
            
            # Resultado da IA
            pdf.set_font("Arial", 'B', 12)
            pdf.cell(0, 8, "RESULTADO DA ANALISE:", 0, 1)
            pdf.set_font("Arial", size=10)
            
            # Quebra o texto da IA em linhas
            resultado_text = self.result.toPlainText()
            lines = resultado_text.split('\n')
            for line in lines:
                if len(line) > 80:
                    words = line.split(' ')
                    current_line = ""
                    for word in words:
                        if len(current_line + word) < 80:
                            current_line += word + " "
                        else:
                            if current_line:
                                pdf.cell(0, 6, current_line.encode('latin-1', 'replace').decode('latin-1'), 0, 1)
                            current_line = word + " "
                    if current_line:
                        pdf.cell(0, 6, current_line.encode('latin-1', 'replace').decode('latin-1'), 0, 1)
                else:
                    pdf.cell(0, 6, line.encode('latin-1', 'replace').decode('latin-1'), 0, 1)
            
            # Observações do médico
            if hasattr(self, 'observacoes_medico') and self.observacoes_medico.toPlainText():
                pdf.ln(5)
                pdf.set_font("Arial", 'B', 12)
                pdf.cell(0, 8, "OBSERVACOES DO MEDICO:", 0, 1)
                pdf.set_font("Arial", size=10)
                obs_text = self.observacoes_medico.toPlainText()
                obs_lines = obs_text.split('\n')
                for line in obs_lines:
                    pdf.cell(0, 6, line.encode('latin-1', 'replace').decode('latin-1'), 0, 1)
            
            # Salva o PDF
            filename = f"relatorio_hipertensao_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
            pdf.output(filename)
            QMessageBox.information(self, "Sucesso", f"PDF gerado: {filename}")
            
        except Exception as e:
            QMessageBox.critical(self, "Erro", f"Erro ao gerar PDF: {e}")

class UserManagementWidget(QWidget):
    def __init__(self, db_manager, current_user):
        super().__init__()
        self.db_manager = db_manager
        self.current_user = current_user
        self.init_ui()
    
    def init_ui(self):
        layout = QVBoxLayout()
        
        # Título
        title = QLabel("👥 Gerenciamento de Usuários")
        title.setFont(QFont("", 16, QFont.Bold))
        layout.addWidget(title)
        
        # Tabs para diferentes tipos de usuários
        tabs = QTabWidget()
        
        if self.current_user['tipo'] == 'admin':
            tabs.addTab(self.create_user_tab('medico'), "👨‍⚕️ Médicos")
            tabs.addTab(self.create_user_tab('paciente'), "👤 Pacientes")
            tabs.addTab(self.create_new_user_tab(), "➕ Novo Usuário")
        
        layout.addWidget(tabs)
        self.setLayout(layout)
    
    def create_user_tab(self, user_type):
        widget = QWidget()
        layout = QVBoxLayout()
        
        # Tabela de usuários
        table = QTableWidget()
        users = self.db_manager.get_users_by_type(user_type)
        
        if user_type == 'medico':
            headers = ['ID', 'Username', 'Nome', 'Email', 'CRM', 'Especialidade', 'Ativo']
            table.setColumnCount(len(headers))
            table.setHorizontalHeaderLabels(headers)
            table.setRowCount(len(users))
            
            for i, user in enumerate(users):
                table.setItem(i, 0, QTableWidgetItem(str(user[0])))
                table.setItem(i, 1, QTableWidgetItem(user[1]))
                table.setItem(i, 2, QTableWidgetItem(user[2]))
                table.setItem(i, 3, QTableWidgetItem(user[3] or ""))
                table.setItem(i, 4, QTableWidgetItem(user[5] or ""))
                table.setItem(i, 5, QTableWidgetItem(user[6] or ""))
                table.setItem(i, 6, QTableWidgetItem("Sim" if user[8] else "Não"))
        
        else:  # paciente
            headers = ['ID', 'Username', 'Nome', 'Email', 'Telefone', 'Data Nascimento', 'Ativo']
            table.setColumnCount(len(headers))
            table.setHorizontalHeaderLabels(headers)
            table.setRowCount(len(users))
            
            for i, user in enumerate(users):
                table.setItem(i, 0, QTableWidgetItem(str(user[0])))
                table.setItem(i, 1, QTableWidgetItem(user[1]))
                table.setItem(i, 2, QTableWidgetItem(user[2]))
                table.setItem(i, 3, QTableWidgetItem(user[3] or ""))
                table.setItem(i, 4, QTableWidgetItem(user[4] or ""))
                table.setItem(i, 5, QTableWidgetItem(user[7] or ""))
                table.setItem(i, 6, QTableWidgetItem("Sim" if user[8] else "Não"))
        
        table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        layout.addWidget(table)
        
        # Botão de atualizar
        refresh_btn = QPushButton("🔄 Atualizar")
        refresh_btn.clicked.connect(lambda: self.refresh_user_tab(table, user_type))
        layout.addWidget(refresh_btn)
        
        widget.setLayout(layout)
        return widget
    
    def refresh_user_tab(self, table, user_type):
        users = self.db_manager.get_users_by_type(user_type)
        table.setRowCount(len(users))
        
        for i, user in enumerate(users):
            table.setItem(i, 0, QTableWidgetItem(str(user[0])))
            table.setItem(i, 1, QTableWidgetItem(user[1]))
            table.setItem(i, 2, QTableWidgetItem(user[2]))
            table.setItem(i, 3, QTableWidgetItem(user[3] or ""))
            if user_type == 'medico':
                table.setItem(i, 4, QTableWidgetItem(user[5] or ""))
                table.setItem(i, 5, QTableWidgetItem(user[6] or ""))
                table.setItem(i, 6, QTableWidgetItem("Sim" if user[8] else "Não"))
            else:
                table.setItem(i, 4, QTableWidgetItem(user[4] or ""))
                table.setItem(i, 5, QTableWidgetItem(user[7] or ""))
                table.setItem(i, 6, QTableWidgetItem("Sim" if user[8] else "Não"))
    
    def create_new_user_tab(self):
        widget = QWidget()
        layout = QVBoxLayout()
        
        # Formulário para novo usuário
        form_group = QGroupBox("➕ Criar Novo Usuário")
        form_layout = QFormLayout()
        
        self.new_tipo = QComboBox()
        self.new_tipo.addItems(['medico', 'paciente'])
        self.new_tipo.currentTextChanged.connect(self.on_tipo_changed)
        
        self.new_username = QLineEdit()
        self.new_password = QLineEdit()
        self.new_password.setEchoMode(QLineEdit.Password)
        self.new_nome = QLineEdit()
        self.new_email = QLineEdit()
        self.new_telefone = QLineEdit()
        
        # Campos específicos para médico
        self.new_crm = QLineEdit()
        self.new_especialidade = QLineEdit()
        
        # Campos específicos para paciente
        self.new_data_nascimento = QLineEdit()
        self.new_data_nascimento.setPlaceholderText("DD/MM/AAAA")
        
        form_layout.addRow("Tipo:", self.new_tipo)
        form_layout.addRow("Username:", self.new_username)
        form_layout.addRow("Senha:", self.new_password)
        form_layout.addRow("Nome Completo:", self.new_nome)
        form_layout.addRow("Email:", self.new_email)
        form_layout.addRow("Telefone:", self.new_telefone)
        form_layout.addRow("CRM:", self.new_crm)
        form_layout.addRow("Especialidade:", self.new_especialidade)
        form_layout.addRow("Data Nascimento:", self.new_data_nascimento)
        
        form_group.setLayout(form_layout)
        layout.addWidget(form_group)
        
        # Botão criar
        create_btn = QPushButton("✅ Criar Usuário")
        create_btn.clicked.connect(self.create_new_user)
        layout.addWidget(create_btn)
        
        widget.setLayout(layout)
        
        # Inicializa visibilidade dos campos
        self.on_tipo_changed('medico')
        
        return widget
    
    def on_tipo_changed(self, tipo):
        is_medico = tipo == 'medico'
        self.new_crm.setVisible(is_medico)
        self.new_especialidade.setVisible(is_medico)
        self.new_data_nascimento.setVisible(not is_medico)
    
    def create_new_user(self):
        # Validações básicas
        if not all([self.new_username.text(), self.new_password.text(), self.new_nome.text()]):
            QMessageBox.warning(self, "Erro", "Preencha pelo menos username, senha e nome.")
            return
        
        # Coleta dados
        tipo = self.new_tipo.currentText()
        username = self.new_username.text().strip()
        password = self.new_password.text()
        nome = self.new_nome.text().strip()
        email = self.new_email.text().strip()
        telefone = self.new_telefone.text().strip()
        crm = self.new_crm.text().strip() if tipo == 'medico' else ""
        especialidade = self.new_especialidade.text().strip() if tipo == 'medico' else ""
        data_nascimento = self.new_data_nascimento.text().strip() if tipo == 'paciente' else ""
        
        # Cria usuário
        user_id = self.db_manager.create_user(
            username=username,
            password=password,
            tipo=tipo,
            nome=nome,
            email=email,
            telefone=telefone,
            crm=crm,
            especialidade=especialidade,
            data_nascimento=data_nascimento
        )
        
        if user_id:
            QMessageBox.information(self, "Sucesso", f"Usuário criado com ID: {user_id}")
            # Limpa formulário
            self.new_username.clear()
            self.new_password.clear()
            self.new_nome.clear()
            self.new_email.clear()
            self.new_telefone.clear()
            self.new_crm.clear()
            self.new_especialidade.clear()
            self.new_data_nascimento.clear()
        else:
            QMessageBox.warning(self, "Erro", "Username já existe ou erro ao criar usuário.")

class ReportsWidget(QWidget):
    def __init__(self, db_manager, current_user):
        super().__init__()
        self.db_manager = db_manager
        self.current_user = current_user
        self.init_ui()
    
    def init_ui(self):
        layout = QVBoxLayout()
        
        # Título
        title = QLabel("📊 Relatórios e Histórico")
        title.setFont(QFont("", 16, QFont.Bold))
        layout.addWidget(title)
        
        if self.current_user['tipo'] == 'paciente':
            # Para pacientes: mostrar apenas suas próprias avaliações
            self.show_patient_reports(layout)
        else:
            # Para médicos e admin: mostrar todas as avaliações
            self.show_all_reports(layout)
        
        self.setLayout(layout)
    
    def show_patient_reports(self, layout):
        avaliacoes = self.db_manager.get_avaliacoes_paciente(self.current_user['id'])
        
        if not avaliacoes:
            layout.addWidget(QLabel("Nenhuma avaliação encontrada."))
            return
        
        # Lista de avaliações
        list_widget = QListWidget()
        
        for avaliacao in avaliacoes:
            item_text = f"📅 {avaliacao[1][:16]} - Dr. {avaliacao[2] or 'Sistema'} - Status: {avaliacao[3]}"
            list_widget.addItem(item_text)
        
        list_widget.itemClicked.connect(lambda item: self.show_avaliacao_detail(avaliacoes[list_widget.row(item)]))
        
        layout.addWidget(QLabel("Suas Avaliações:"))
        layout.addWidget(list_widget)
        
        # Área de detalhes
        self.detail_area = QTextEdit()
        self.detail_area.setReadOnly(True)
        layout.addWidget(QLabel("Detalhes da Avaliação:"))
        layout.addWidget(self.detail_area)
    
    def show_all_reports(self, layout):
        avaliacoes = self.db_manager.get_all_avaliacoes()
        
        if not avaliacoes:
            layout.addWidget(QLabel("Nenhuma avaliação encontrada."))
            return
        
        # Tabela de avaliações
        table = QTableWidget()
        table.setColumnCount(5)
        table.setHorizontalHeaderLabels(['ID', 'Data', 'Paciente', 'Médico', 'Status'])
        table.setRowCount(len(avaliacoes))
        
        for i, avaliacao in enumerate(avaliacoes):
            table.setItem(i, 0, QTableWidgetItem(str(avaliacao[0])))
            table.setItem(i, 1, QTableWidgetItem(avaliacao[1][:16]))
            table.setItem(i, 2, QTableWidgetItem(avaliacao[2] or ""))
            table.setItem(i, 3, QTableWidgetItem(avaliacao[3] or "Sistema"))
            table.setItem(i, 4, QTableWidgetItem(avaliacao[4]))
        
        table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        layout.addWidget(table)
    
    def show_avaliacao_detail(self, avaliacao):
        detail_text = f"""
=== DETALHES DA AVALIAÇÃO ===

Data: {avaliacao[1]}
Médico: Dr. {avaliacao[2] or 'Sistema'}
Status: {avaliacao[3]}

=== DADOS DA AUTOAVALIAÇÃO ===
{json.dumps(json.loads(avaliacao[4]), indent=2, ensure_ascii=False)}

=== EXAMES ===
{json.dumps(json.loads(avaliacao[5]) if avaliacao[5] != 'null' else None, indent=2, ensure_ascii=False)}

=== RESULTADO DA IA ===
{avaliacao[6]}

=== OBSERVAÇÕES DO MÉDICO ===
{avaliacao[7] or 'Nenhuma observação'}
        """
        self.detail_area.setPlainText(detail_text)

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.db_manager = DatabaseManager()
        self.current_user = None
        self.init_ui()
        self.show_login()
    
    def init_ui(self):
        self.setWindowTitle("🏥 Sistema de Gestão de Hipertensão")
        self.setGeometry(100, 100, 1200, 800)
        self.setStyleSheet("""
            QMainWindow {
                background: #f5f5f5;
            }
            QMenuBar {
                background: #2c3e50;
                color: white;
                padding: 5px;
            }
            QMenuBar::item {
                background: transparent;
                padding: 5px 10px;
            }
            QMenuBar::item:selected {
                background: #34495e;
            }
            QTabWidget::pane {
                border: 1px solid #ccc;
                background: white;
            }
            QTabBar::tab {
                background: #ecf0f1;
                padding: 8px 12px;
                margin-right: 2px;
            }
            QTabBar::tab:selected {
                background: white;
                border-bottom: 2px solid #3498db;
            }
        """)
        
        # Menu bar
        menubar = self.menuBar()
        
        # Menu Sistema
        sistema_menu = menubar.addMenu('Sistema')
        logout_action = sistema_menu.addAction('🚪 Logout')
        logout_action.triggered.connect(self.logout)
        exit_action = sistema_menu.addAction('❌ Sair')
        exit_action.triggered.connect(self.close)
        
        # Widget central com stack
        self.central_stack = QStackedWidget()
        self.setCentralWidget(self.central_stack)
    
    def show_login(self):
        login_widget = LoginWindow(self.db_manager, self.on_login_success)
        self.central_stack.addWidget(login_widget)
        self.central_stack.setCurrentWidget(login_widget)
    
    def on_login_success(self, user):
        self.current_user = user
        self.setup_main_interface()
    
    def setup_main_interface(self):
        # Remove widget de login
        while self.central_stack.count() > 0:
            widget = self.central_stack.widget(0)
            self.central_stack.removeWidget(widget)
            widget.deleteLater()
        
        # Atualiza título da janela
        self.setWindowTitle(f"🏥 Sistema de Hipertensão - {self.current_user['nome']} ({self.current_user['tipo'].title()})")
        
        # Cria abas principais
        main_tabs = QTabWidget()
        
        # Aba de Avaliação
        evaluation_widget = HypertensionEvaluationWidget(self.db_manager, self.current_user)
        main_tabs.addTab(evaluation_widget, "💓 Avaliação")
        
        # Aba de Relatórios
        reports_widget = ReportsWidget(self.db_manager, self.current_user)
        main_tabs.addTab(reports_widget, "📊 Relatórios")
        
        # Aba de Gerenciamento (apenas para admin)
        if self.current_user['tipo'] == 'admin':
            management_widget = UserManagementWidget(self.db_manager, self.current_user)
            main_tabs.addTab(management_widget, "👥 Usuários")
        
        self.central_stack.addWidget(main_tabs)
        self.central_stack.setCurrentWidget(main_tabs)
    
    def logout(self):
        self.current_user = None
        # Limpa interface atual
        while self.central_stack.count() > 0:
            widget = self.central_stack.widget(0)
            self.central_stack.removeWidget(widget)
            widget.deleteLater()
        
        # Mostra login novamente
        self.show_login()
        self.setWindowTitle("🏥 Sistema de Gestão de Hipertensão")

def main():
    app = QApplication(sys.argv)
    app.setStyle('Fusion')
    
    window = MainWindow()
    window.show()
    
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()