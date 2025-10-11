from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QFormLayout, QPushButton,
    QLineEdit, QMessageBox, QDateEdit, QLabel, QFrame, QScrollArea
)
from PyQt5.QtCore import QDate, Qt
import re

class PatientProfile(QWidget):
    """
    Uma widget para exibir e editar o perfil do paciente, com um design
    moderno, validação de dados em tempo real e layout responsivo que
    se adapta ao tamanho da janela usando QScrollArea.
    """
    def __init__(self, db_manager, user):
        super().__init__()
        self.db_manager = db_manager
        self.user = user
        self.init_ui()
        self._load_user_data()

    def init_ui(self):
        """Inicializa a interface do usuário com estilo e layout modernos."""
        self.setStyleSheet("""
            /* Estilo geral para o fundo da área de conteúdo */
            #content_widget {
                background-color: #f5f7fa;
            }
            QLabel[class="title"] {
                font-size: 16pt;
                font-weight: bold;
                color: #2c3e50;
                padding-bottom: 15px;
            }
            QLabel[class="subtitle"] {
                font-size: 12pt;
                font-weight: bold;
                color: #34495e;
                padding-top: 10px;
                padding-bottom: 5px;
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
            }
            QLineEdit[valid="true"] {
                border-color: #27ae60;
            }
            QPushButton {
                border: none;
                color: white;
                padding: 12px 24px;
                font-size: 11pt;
                font-weight: bold;
                border-radius: 6px;
                min-width: 150px;
                min-height: 40px;
            }
            QPushButton:hover {
                opacity: 0.9;
            }
            QPushButton#btn_save_profile {
                background-color: #27ae60;
            }
            QPushButton#btn_save_profile:hover {
                background-color: #2ecc71;
            }
            QPushButton#btn_change_password {
                background-color: #3498db;
            }
            QPushButton#btn_change_password:hover {
                background-color: #5dade2;
            }
            QFrame#card {
                background-color: white;
                border: 1px solid #e0e0e0;
                border-radius: 10px;
                padding: 20px;
            }
            /* Estilo para a área de rolagem */
            QScrollArea {
                border: none;
                background-color: #f5f7fa;
            }
            /* Estilo para a barra de rolagem */
            QScrollBar:vertical {
                border: none;
                background: #e0e0e0;
                width: 10px;
                margin: 0px 0px 0px 0px;
                border-radius: 5px;
            }
            QScrollBar::handle:vertical {
                background: #bdc3c7;
                min-height: 20px;
                border-radius: 5px;
            }
            QScrollBar::handle:vertical:hover {
                background: #95a5a6;
            }
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
                height: 0px;
            }
        """)

        # --- Estrutura Principal com ScrollArea ---
        # 1. Layout principal que conterá APENAS a área de rolagem
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)

        # 2. A Área de Rolagem
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True) # MUITO IMPORTANTE para a responsividade
        
        # 3. Widget de conteúdo que irá DENTRO da área de rolagem
        content_widget = QWidget()
        content_widget.setObjectName("content_widget")
        
        # 4. Layout do conteúdo onde todos os elementos da UI serão adicionados
        content_layout = QVBoxLayout(content_widget)
        content_layout.setContentsMargins(20, 20, 20, 20)
        content_layout.setSpacing(20)

        # Adiciona os elementos da UI ao layout de conteúdo
        title_label = QLabel("👤 Meu Perfil")
        title_label.setProperty("class", "title")
        content_layout.addWidget(title_label)

        # --- Card de Informações Pessoais ---
        profile_frame = QFrame()
        profile_frame.setObjectName("card")
        profile_layout = QVBoxLayout(profile_frame)
        
        profile_subtitle = QLabel("Informações Pessoais")
        profile_subtitle.setProperty("class", "subtitle")
        profile_layout.addWidget(profile_subtitle)

        form_layout = QFormLayout()
        form_layout.setSpacing(15)
        form_layout.setFieldGrowthPolicy(QFormLayout.ExpandingFieldsGrow)

        self.name_input = QLineEdit(placeholderText="Digite seu nome completo")
        self.name_input.textChanged.connect(self._validate_name)
        form_layout.addRow("Nome:", self.name_input)

        self.email_input = QLineEdit(placeholderText="exemplo@email.com")
        self.email_input.textChanged.connect(self._validate_email)
        form_layout.addRow("Email:", self.email_input)

        self.phone_input = QLineEdit(placeholderText="(00) 00000-0000")
        self.phone_input.textChanged.connect(self._format_phone)
        form_layout.addRow("Telefone:", self.phone_input)

        self.birth_date_input = QDateEdit(calendarPopup=True)
        self.birth_date_input.setDisplayFormat("dd/MM/yyyy")
        self.birth_date_input.setMaximumDate(QDate.currentDate())
        self.birth_date_input.setMinimumDate(QDate(1900, 1, 1))
        form_layout.addRow("Data Nascimento:", self.birth_date_input)
        
        profile_layout.addLayout(form_layout)

        save_profile_btn = QPushButton("💾 Salvar Perfil")
        save_profile_btn.setObjectName("btn_save_profile")
        save_profile_btn.clicked.connect(self.save_profile)
        profile_layout.addWidget(save_profile_btn, 0, Qt.AlignRight)
        content_layout.addWidget(profile_frame)

        # --- Card de Alteração de Senha ---
        password_frame = QFrame()
        password_frame.setObjectName("card")
        password_layout_main = QVBoxLayout(password_frame)

        password_subtitle = QLabel("🔒 Alterar Senha")
        password_subtitle.setProperty("class", "subtitle")
        password_layout_main.addWidget(password_subtitle)

        password_form = QFormLayout()
        password_form.setSpacing(15)
        password_form.setFieldGrowthPolicy(QFormLayout.ExpandingFieldsGrow)

        self.old_password_input = QLineEdit(echoMode=QLineEdit.Password, placeholderText="Sua senha atual")
        password_form.addRow("Senha Atual:", self.old_password_input)

        self.new_password_input = QLineEdit(echoMode=QLineEdit.Password, placeholderText="Mínimo 6 caracteres")
        self.new_password_input.textChanged.connect(self._validate_passwords)
        password_form.addRow("Nova Senha:", self.new_password_input)

        self.confirm_password_input = QLineEdit(echoMode=QLineEdit.Password, placeholderText="Confirme a nova senha")
        self.confirm_password_input.textChanged.connect(self._validate_passwords)
        password_form.addRow("Confirmar Senha:", self.confirm_password_input)
        
        password_layout_main.addLayout(password_form)
        
        save_password_btn = QPushButton("🔐 Alterar Senha")
        save_password_btn.setObjectName("btn_change_password")
        save_password_btn.clicked.connect(self.change_password)
        password_layout_main.addWidget(save_password_btn, 0, Qt.AlignRight)
        content_layout.addWidget(password_frame)
        
        # Garante que o conteúdo não fique esticado verticalmente
        content_layout.addStretch()

        # 5. Define o widget de conteúdo DENTRO da área de rolagem
        scroll_area.setWidget(content_widget)

        # 6. Adiciona a área de rolagem ao layout principal da janela
        main_layout.addWidget(scroll_area)

    def _load_user_data(self):
        # (O resto do código permanece o mesmo, não precisa de alterações)
        """Preenche os campos com os dados do usuário atual."""
        self.name_input.setText(self.user.get("name", ""))
        self.email_input.setText(self.user.get("email", ""))
        self.phone_input.setText(self.user.get("phone", ""))
        
        birth_date = self.user.get("birth_date")
        if birth_date:
            qdate = QDate(birth_date.year, birth_date.month, birth_date.day)
            self.birth_date_input.setDate(qdate)
        else:
            self.birth_date_input.setDate(QDate.currentDate().addYears(-20))

    def _update_style(self, widget):
        """Força a atualização do estilo do widget para refletir a validação."""
        widget.style().unpolish(widget)
        widget.style().polish(widget)

    def _validate_name(self):
        """Valida o campo de nome em tempo real."""
        is_valid = len(self.name_input.text().strip()) >= 3
        self.name_input.setProperty("valid", is_valid)
        self._update_style(self.name_input)

    def _validate_email(self):
        """Valida o campo de email em tempo real."""
        email = self.email_input.text().strip()
        email_regex = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}'
        is_valid = bool(re.match(email_regex, email))
        self.email_input.setProperty("valid", is_valid)
        self._update_style(self.email_input)

    def _validate_passwords(self):
        """Valida os campos de nova senha e confirmação em tempo real."""
        new_pass = self.new_password_input.text()
        confirm_pass = self.confirm_password_input.text()
        
        is_new_valid = len(new_pass) >= 6
        self.new_password_input.setProperty("valid", is_new_valid)
        
        is_confirm_valid = bool(confirm_pass and new_pass == confirm_pass)
        self.confirm_password_input.setProperty("valid", is_confirm_valid)

        self._update_style(self.new_password_input)
        self._update_style(self.confirm_password_input)
        
    def _format_phone(self):
        """Formata o número de telefone automaticamente."""
        text = self.phone_input.text()
        numbers = re.sub(r'\D', '', text)[:11]
        
        formatted = ""
        if len(numbers) > 10:
            formatted = f"({numbers[:2]}) {numbers[2:7]}-{numbers[7:]}"
        elif len(numbers) > 6:
            formatted = f"({numbers[:2]}) {numbers[2:6]}-{numbers[6:]}"
        elif len(numbers) > 2:
            formatted = f"({numbers[:2]}) {numbers[2:]}"
        else:
            formatted = numbers

        self.phone_input.blockSignals(True)
        self.phone_input.setText(formatted)
        self.phone_input.setCursorPosition(len(formatted))
        self.phone_input.blockSignals(False)

    def save_profile(self):
        """Valida e salva as informações do perfil."""
        name = self.name_input.text().strip()
        email = self.email_input.text().strip()
        
        if len(name) < 3:
            QMessageBox.warning(self, "❌ Erro de Validação", "O nome deve ter pelo menos 3 caracteres!")
            return

        if not self.email_input.property("valid"):
            QMessageBox.warning(self, "❌ Erro de Validação", "Por favor, insira um email válido.")
            return

        update_data = {
            "name": name,
            "email": email,
            "phone": self.phone_input.text().strip(),
            "birth_date": self.birth_date_input.date().toPyDate()
        }

        if self.db_manager.update_user(str(self.user["_id"]), update_data):
            self.user.update(update_data)
            QMessageBox.information(self, "✅ Sucesso", "Perfil atualizado com sucesso!")
        else:
            QMessageBox.warning(self, "❌ Erro", "Não foi possível atualizar o perfil. O email pode já estar em uso por outro usuário.")

    def change_password(self):
        """Valida e altera a senha do usuário."""
        old_password = self.old_password_input.text()
        new_password = self.new_password_input.text()
        confirm_password = self.confirm_password_input.text()

        if not any([old_password, new_password, confirm_password]):
            QMessageBox.information(self, "ℹ️ Informação", "Nenhuma senha foi digitada para alteração.")
            return
            
        if not all([old_password, new_password, confirm_password]):
            QMessageBox.warning(self, "❌ Erro", "Para alterar a senha, todos os três campos devem ser preenchidos.")
            return

        if self.user["password"] != self.db_manager.hash_password(old_password):
            QMessageBox.warning(self, "❌ Erro de Autenticação", "A senha atual está incorreta!")
            return
            
        if len(new_password) < 6:
            QMessageBox.warning(self, "❌ Erro", "A nova senha deve ter pelo menos 6 caracteres.")
            return

        if new_password != confirm_password:
            QMessageBox.warning(self, "❌ Erro", "A nova senha e a confirmação não coincidem!")
            return

        update_data = {"password": self.db_manager.hash_password(new_password)}
        if self.db_manager.update_user(str(self.user["_id"]), update_data):
            self.user["password"] = update_data["password"]
            QMessageBox.information(self, "✅ Sucesso", "Senha alterada com sucesso!")
            self.old_password_input.clear()
            self.new_password_input.clear()
            self.confirm_password_input.clear()
        else:
            QMessageBox.warning(self, "❌ Erro", "Ocorreu um erro inesperado ao tentar alterar a senha.")