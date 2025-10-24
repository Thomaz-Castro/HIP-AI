from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QFormLayout, QPushButton, QHBoxLayout,
    QLineEdit, QMessageBox, QDateEdit, QDialog, QLabel,
    QFrame
)
from PyQt5.QtCore import QDate, Qt, QRegExp
from PyQt5.QtGui import QRegExpValidator
import re


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
        # Títulos amigáveis
        type_names = {
            "admin": "Administrador",
            "doctor": "Médico",
            "patient": "Paciente"
        }
        
        type_icons = {
            "admin": "🔑",
            "doctor": "👨‍⚕️",
            "patient": "👤"
        }
        
        action = "Editar" if self.user_id else "Adicionar"
        type_name = type_names.get(self.user_type, self.user_type)
        icon = type_icons.get(self.user_type, "")
        
        self.setWindowTitle(f"{action} {type_name}")
        self.setModal(True)
        self.resize(500, 450)
        
        # Estilo moderno
        self.setStyleSheet("""
            QDialog {
                background-color: #f5f7fa;
            }
            
            QLabel {
                color: #2c3e50;
                font-size: 10pt;
            }
            
            QLabel[class="title"] {
                font-size: 16pt;
                font-weight: bold;
                color: #2c3e50;
                padding: 15px;
            }
            
            QLabel[class="required"] {
                color: #e74c3c;
                font-weight: bold;
            }
            
            QLineEdit, QDateEdit {
                border: 2px solid #bdc3c7;
                border-radius: 6px;
                padding: 10px 12px;
                background-color: white;
                font-size: 10pt;
                min-height: 20px;
            }
            
            QLineEdit:focus, QDateEdit:focus {
                border-color: #3498db;
            }
            
            QLineEdit[valid="false"] {
                border-color: #e74c3c;
                background-color: #fadbd8;
            }
            
            QLineEdit[valid="true"] {
                border-color: #27ae60;
            }
            
            QPushButton {
                background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                                          stop: 0 #3498db, stop: 1 #2980b9);
                border: none;
                color: white;
                padding: 12px 24px;
                font-size: 11pt;
                font-weight: bold;
                border-radius: 6px;
                min-width: 100px;
                min-height: 40px;
            }
            
            QPushButton:hover {
                background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                                          stop: 0 #5dade2, stop: 1 #3498db);
            }
            
            QPushButton#btn_save {
                background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                                          stop: 0 #27ae60, stop: 1 #229954);
            }
            
            QPushButton#btn_save:hover {
                background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                                          stop: 0 #58d68d, stop: 1 #27ae60);
            }
            
            QPushButton#btn_cancel {
                background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                                          stop: 0 #95a5a6, stop: 1 #7f8c8d);
            }
            
            QPushButton#btn_cancel:hover {
                background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                                          stop: 0 #b2babb, stop: 1 #95a5a6);
            }
            
            QFrame {
                background-color: white;
                border-radius: 10px;
                padding: 20px;
            }
        """)

        layout = QVBoxLayout()
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)

        # Título
        title = QLabel(f"{icon} {action} {type_name}")
        title.setProperty("class", "title")
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)

        # Frame do formulário
        form_frame = QFrame()
        form_layout = QFormLayout()
        form_layout.setSpacing(15)
        form_layout.setFieldGrowthPolicy(QFormLayout.ExpandingFieldsGrow)

        # Nome *
        name_label_widget = QWidget()
        name_label_layout = QHBoxLayout(name_label_widget)
        name_label_layout.setContentsMargins(0, 0, 0, 0)
        name_label = QLabel("Nome completo:")
        name_required = QLabel("*")
        name_required.setProperty("class", "required")
        name_label_layout.addWidget(name_label)
        name_label_layout.addWidget(name_required)
        name_label_layout.addStretch()
        
        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("Digite o nome completo")
        self.name_input.textChanged.connect(self.validate_name)
        form_layout.addRow(name_label_widget, self.name_input)

        # Email *
        email_label_widget = QWidget()
        email_label_layout = QHBoxLayout(email_label_widget)
        email_label_layout.setContentsMargins(0, 0, 0, 0)
        email_label = QLabel("Email:")
        email_required = QLabel("*")
        email_required.setProperty("class", "required")
        email_label_layout.addWidget(email_label)
        email_label_layout.addWidget(email_required)
        email_label_layout.addStretch()
        
        self.email_input = QLineEdit()
        self.email_input.setPlaceholderText("exemplo@email.com")
        self.email_input.textChanged.connect(self.validate_email)
        form_layout.addRow(email_label_widget, self.email_input)

        # Senha *
        password_label_widget = QWidget()
        password_label_layout = QHBoxLayout(password_label_widget)
        password_label_layout.setContentsMargins(0, 0, 0, 0)
        password_label = QLabel("Senha:")
        if not self.user_id:
            password_required = QLabel("*")
            password_required.setProperty("class", "required")
            password_label_layout.addWidget(password_label)
            password_label_layout.addWidget(password_required)
        else:
            password_label_layout.addWidget(password_label)
        password_label_layout.addStretch()
        
        self.password_input = QLineEdit()
        self.password_input.setEchoMode(QLineEdit.Password)
        if self.user_id:
            self.password_input.setPlaceholderText("Deixe em branco para manter a senha atual")
        else:
            self.password_input.setPlaceholderText("Mínimo 6 caracteres")
            self.password_input.textChanged.connect(self.validate_password)
        form_layout.addRow(password_label_widget, self.password_input)

        # Campos específicos para admin
        if self.user_type == "admin":
            info_label = QLabel("ℹ️ Administradores têm acesso total ao sistema")
            info_label.setStyleSheet("color: #7f8c8d; font-style: italic; padding: 10px;")
            form_layout.addRow("", info_label)

        # Campos específicos para médicos
        elif self.user_type == "doctor":
            # CRM *
            crm_label_widget = QWidget()
            crm_label_layout = QHBoxLayout(crm_label_widget)
            crm_label_layout.setContentsMargins(0, 0, 0, 0)
            crm_label = QLabel("CRM:")
            crm_required = QLabel("*")
            crm_required.setProperty("class", "required")
            crm_label_layout.addWidget(crm_label)
            crm_label_layout.addWidget(crm_required)
            crm_label_layout.addStretch()
            
            self.crm_input = QLineEdit()
            self.crm_input.setPlaceholderText("Ex: 12345")
            # Apenas números
            crm_validator = QRegExpValidator(QRegExp("[0-9]+"))
            self.crm_input.setValidator(crm_validator)
            form_layout.addRow(crm_label_widget, self.crm_input)

            # Especialidade *
            specialty_label_widget = QWidget()
            specialty_label_layout = QHBoxLayout(specialty_label_widget)
            specialty_label_layout.setContentsMargins(0, 0, 0, 0)
            specialty_label = QLabel("Especialidade:")
            specialty_required = QLabel("*")
            specialty_required.setProperty("class", "required")
            specialty_label_layout.addWidget(specialty_label)
            specialty_label_layout.addWidget(specialty_required)
            specialty_label_layout.addStretch()
            
            self.specialty_input = QLineEdit()
            self.specialty_input.setPlaceholderText("Ex: Cardiologia")
            form_layout.addRow(specialty_label_widget, self.specialty_input)

        # Campos específicos para pacientes
        elif self.user_type == "patient":
            # Data de Nascimento *
            birth_label_widget = QWidget()
            birth_label_layout = QHBoxLayout(birth_label_widget)
            birth_label_layout.setContentsMargins(0, 0, 0, 0)
            birth_label = QLabel("Data de Nascimento:")
            birth_required = QLabel("*")
            birth_required.setProperty("class", "required")
            birth_label_layout.addWidget(birth_label)
            birth_label_layout.addWidget(birth_required)
            birth_label_layout.addStretch()
            
            self.birth_date_input = QDateEdit()
            self.birth_date_input.setDate(QDate.currentDate().addYears(-30))
            self.birth_date_input.setCalendarPopup(True)
            self.birth_date_input.setDisplayFormat("dd/MM/yyyy")
            self.birth_date_input.setMaximumDate(QDate.currentDate())
            self.birth_date_input.setMinimumDate(QDate(1900, 1, 1))
            form_layout.addRow(birth_label_widget, self.birth_date_input)

            # Telefone *
            phone_label_widget = QWidget()
            phone_label_layout = QHBoxLayout(phone_label_widget)
            phone_label_layout.setContentsMargins(0, 0, 0, 0)
            phone_label = QLabel("Telefone:")
            phone_required = QLabel("*")
            phone_required.setProperty("class", "required")
            phone_label_layout.addWidget(phone_label)
            phone_label_layout.addWidget(phone_required)
            phone_label_layout.addStretch()
            
            self.phone_input = QLineEdit()
            self.phone_input.setPlaceholderText("(00) 00000-0000")
            self.phone_input.textChanged.connect(self.format_phone)
            form_layout.addRow(phone_label_widget, self.phone_input)

        form_frame.setLayout(form_layout)
        layout.addWidget(form_frame)

        # Nota sobre campos obrigatórios
        required_note = QLabel("* Campos obrigatórios")
        required_note.setStyleSheet("color: #7f8c8d; font-style: italic;")
        layout.addWidget(required_note)

        # Botões
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()
        
        save_btn = QPushButton("💾 Salvar")
        save_btn.setObjectName("btn_save")
        save_btn.clicked.connect(self.save_user)
        
        cancel_btn = QPushButton("✖ Cancelar")
        cancel_btn.setObjectName("btn_cancel")
        cancel_btn.clicked.connect(self.reject)

        btn_layout.addWidget(save_btn)
        btn_layout.addWidget(cancel_btn)

        layout.addLayout(btn_layout)
        self.setLayout(layout)

    def validate_name(self):
        """Valida o nome"""
        name = self.name_input.text().strip()
        if len(name) >= 3:
            self.name_input.setProperty("valid", "true")
        else:
            self.name_input.setProperty("valid", "false")
        self.name_input.setStyleSheet(self.name_input.styleSheet())

    def validate_email(self):
        """Valida o email"""
        email = self.email_input.text().strip()
        email_regex = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}'
        if re.match(email_regex, email):
            self.email_input.setProperty("valid", "true")
        else:
            self.email_input.setProperty("valid", "false")
        self.email_input.setStyleSheet(self.email_input.styleSheet())

    def validate_password(self):
        """Valida a senha"""
        password = self.password_input.text()
        if len(password) >= 6:
            self.password_input.setProperty("valid", "true")
        else:
            self.password_input.setProperty("valid", "false")
        self.password_input.setStyleSheet(self.password_input.styleSheet())

    def format_phone(self):
        """Formata o telefone automaticamente"""
        text = self.phone_input.text()
        # Remove tudo que não é número
        numbers = re.sub(r'\D', '', text)
        
        # Limita a 11 dígitos
        numbers = numbers[:11]
        
        # Formata
        if len(numbers) <= 10:
            # Formato: (00) 0000-0000
            if len(numbers) >= 6:
                formatted = f"({numbers[:2]}) {numbers[2:6]}-{numbers[6:]}"
            elif len(numbers) >= 2:
                formatted = f"({numbers[:2]}) {numbers[2:]}"
            else:
                formatted = numbers
        else:
            # Formato: (00) 00000-0000
            formatted = f"({numbers[:2]}) {numbers[2:7]}-{numbers[7:]}"
        
        # Bloqueia sinais para evitar loop
        self.phone_input.blockSignals(True)
        self.phone_input.setText(formatted)
        self.phone_input.blockSignals(False)

    def load_user_data(self):
        """Carrega dados do usuário para edição"""
        
        # self.user_id já é um inteiro vindo do UserManagement
        user = self.db_manager.get_user_by_id(self.user_id)
        
        if user:
            self.name_input.setText(user["name"])
            self.email_input.setText(user["email"])

            if self.user_type == "doctor":
                self.crm_input.setText(user.get("crm", ""))
                self.specialty_input.setText(user.get("specialty", ""))
                
            elif self.user_type == "patient":
                birth_date = user.get("birth_date") 
                if birth_date:
                    qdate = QDate(birth_date.year, birth_date.month, birth_date.day)
                    self.birth_date_input.setDate(qdate)
                self.phone_input.setText(user.get("phone", ""))

    def save_user(self):
        """Salva ou atualiza o usuário com validações"""
        name = self.name_input.text().strip()
        email = self.email_input.text().strip()
        password = self.password_input.text()

        # Validação de nome
        if not name or len(name) < 3:
            QMessageBox.warning(
                self, "❌ Erro de Validação", 
                "O nome deve ter pelo menos 3 caracteres!"
            )
            self.name_input.setFocus()
            return

        # Validação de email
        email_regex = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}'
        if not email or not re.match(email_regex, email):
            QMessageBox.warning(
                self, "❌ Erro de Validação", 
                "Digite um email válido!\n\nExemplo: usuario@email.com"
            )
            self.email_input.setFocus()
            return

        # Validação de senha (apenas para novo usuário)
        if not self.user_id and (not password or len(password) < 6):
            QMessageBox.warning(
                self, "❌ Erro de Validação", 
                "A senha deve ter pelo menos 6 caracteres!"
            )
            self.password_input.setFocus()
            return
        
        # Se está editando e digitou senha, valida também
        if self.user_id and password and len(password) < 6:
            QMessageBox.warning(
                self, "❌ Erro de Validação", 
                "Se alterar a senha, ela deve ter pelo menos 6 caracteres!"
            )
            self.password_input.setFocus()
            return

        # Dados específicos por tipo
        additional_data = {}
        
        if self.user_type == "doctor":
            crm = self.crm_input.text().strip()
            specialty = self.specialty_input.text().strip()
            
            if not crm:
                QMessageBox.warning(
                    self, "❌ Erro de Validação", 
                    "O CRM é obrigatório!"
                )
                self.crm_input.setFocus()
                return
            
            if not specialty:
                QMessageBox.warning(
                    self, "❌ Erro de Validação", 
                    "A especialidade é obrigatória!"
                )
                self.specialty_input.setFocus()
                return
            
            additional_data["crm"] = crm
            additional_data["specialty"] = specialty
            
        elif self.user_type == "patient":
            birth_date = self.birth_date_input.date().toPyDate()
            phone = self.phone_input.text().strip()
            
            # Remove formatação do telefone para validar
            phone_numbers = re.sub(r'\D', '', phone)
            
            if not phone_numbers or len(phone_numbers) < 10:
                QMessageBox.warning(
                    self, "❌ Erro de Validação", 
                    "Digite um telefone válido!\n\n"
                    "Mínimo: 10 dígitos (com DDD)"
                )
                self.phone_input.setFocus()
                return
            
            additional_data["birth_date"] = birth_date
            additional_data["phone"] = phone

        # Salvar ou atualizar
        try:
            if self.user_id:
                # Editar usuário existente
                update_data = {"name": name, "email": email}
                
                if password:
                    update_data["password"] = self.db_manager.hash_password(password)
                
                update_data.update(additional_data)

                if self.db_manager.update_user(self.user_id, update_data):
                    QMessageBox.information(
                        self, "✅ Sucesso", 
                        "Usuário atualizado com sucesso!"
                    )
                    self.accept()
                else:
                    QMessageBox.warning(
                        self, "❌ Erro", 
                        "Erro ao atualizar usuário!\n\n"
                        "Verifique se o email já não está em uso."
                    )
            else:
                # Criar novo usuário
                user_id = self.db_manager.create_user(
                    name, email, password, self.user_type, additional_data
                )
                
                if user_id:
                    type_names = {
                        "admin": "Administrador",
                        "doctor": "Médico",
                        "patient": "Paciente"
                    }
                    type_name = type_names.get(self.user_type, self.user_type)
                    
                    QMessageBox.information(
                        self, "✅ Sucesso", 
                        f"{type_name} criado com sucesso!\n\n"
                        f"📧 Email: {email}\n"
                        f"🔑 Senha: {password}\n\n"
                        f"Guarde estas informações!"
                    )
                    self.accept()
                else:
                    QMessageBox.warning(
                        self, "❌ Erro", 
                        "Erro ao criar usuário!\n\n"
                        "Verifique se o email já não está em uso."
                    )
                    
        except Exception as e:
            QMessageBox.critical(
                self, "❌ Erro Crítico", 
                f"Erro ao salvar usuário:\n\n{str(e)}"
            )