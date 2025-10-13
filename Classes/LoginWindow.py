from PyQt5.QtWidgets import (
    QVBoxLayout, QFormLayout,
    QGroupBox, QLabel, 
    QPushButton, QLineEdit,
    QMessageBox, QDialog
)
from PyQt5.QtGui import QFont
from PyQt5.QtCore import Qt

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
        title.setStyleSheet("font-size: 32px;")
        layout.addWidget(title)

        # Formulário de login
        login_group = QGroupBox()
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
        # info_label = QLabel("👨‍💼 Admin padrão: admin@sistema.com / admin123")
        # info_label.setAlignment(Qt.AlignCenter)
        # info_label.setStyleSheet("font-size: 12px; margin-top: 20px;")
        # layout.addWidget(info_label)

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
            print(
                f"Login bem sucedido para: {user['name']} ({user['user_type']})")
            self.user = user
            # Fecha o diálogo de login e abre a janela principal
            self.accept()
        else:
            print("Login falhou - credenciais inválidas")
            QMessageBox.warning(self, "Erro", "Email ou senha inválidos!")
            self.password_input.clear()

    def accept(self):
        print("LoginWindow.accept() chamado")
        # Import apenas quando necessário (lazy import)
        from Classes.MainWindow import MainWindow
        
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