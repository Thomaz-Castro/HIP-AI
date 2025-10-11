from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout,
    QLabel, QPushButton,
    QTabWidget
)

from Classes.LoginWindow import LoginWindow
from Classes.PatientProfile import PatientProfile
from Classes.ReportsView import ReportsView
from Classes.UserManagement import UserManagement
from Classes.HypertensionAssessment import HypertensionAssessment


class MainWindow(QWidget):
    def __init__(self, db_manager, user):
        super().__init__()
        self.db_manager = db_manager
        self.user = user
        self.login_window = None
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle(
            f"Sistema Médico - {self.user['name']} ({self.user['user_type'].title()})")
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
            self.tabs.addTab(UserManagement(
                self.db_manager, self.user), "👥 Gerenciar Usuários")
            self.tabs.addTab(ReportsView(
                self.db_manager, self.user), "📊 Todos os Relatórios")

        elif self.user["user_type"] == "doctor":
            self.tabs.addTab(HypertensionAssessment(
                self.db_manager, self.user), "🩺 Nova Avaliação")
            self.tabs.addTab(ReportsView(
                self.db_manager, self.user), "📋 Meus Relatórios")

        elif self.user["user_type"] == "patient":
            self.tabs.addTab(PatientProfile(
                self.db_manager, self.user), "👤 Meu Perfil")
            self.tabs.addTab(ReportsView(
                self.db_manager, self.user), "📋 Meus Relatórios")

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