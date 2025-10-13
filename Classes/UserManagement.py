from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QPushButton,
    QHBoxLayout, QTableWidget, QTableWidgetItem, QHeaderView, QMessageBox,
    QTabWidget, QLabel, QLineEdit
)
from PyQt5.QtGui import QFont
from PyQt5.QtCore import Qt
from Classes.UserDialog import UserDialog


class UserManagement(QWidget):
    def __init__(self, db_manager, user):
        super().__init__()
        self.db_manager = db_manager
        self.user = user
        self.init_ui()

    def init_ui(self):
        # Estilo moderno
        self.setStyleSheet("""
            QWidget {
                font-family: 'Segoe UI', Arial, sans-serif;
                font-size: 10pt;
                background-color: #f5f7fa;
            }
            
            QTabWidget::pane {
                border: 2px solid #bdc3c7;
                border-radius: 8px;
                background-color: white;
                padding: 10px;
            }
            
            QTabWidget::tab-bar {
                alignment: left;
            }
            
            QTabBar::tab {
                background: #ecf0f1;
                color: #2c3e50;
                padding: 12px 35px;
                margin-right: 4px;
                border-top-left-radius: 8px;
                border-top-right-radius: 8px;
                font-weight: bold;
                font-size: 11pt;
                min-width: 180px;
            }
            
            QTabBar::tab:selected {
                background: #3498db;
                color: white;
            }
            
            QTabBar::tab:hover:!selected {
                background: #d5dbdb;
            }
            
            QPushButton {
                background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                                          stop: 0 #3498db, stop: 1 #2980b9);
                border: none;
                color: white;
                padding: 10px 20px;
                font-size: 10pt;
                font-weight: bold;
                border-radius: 6px;
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
            
            QPushButton#btn_add {
                background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                                          stop: 0 #27ae60, stop: 1 #229954);
            }
            
            QPushButton#btn_add:hover {
                background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                                          stop: 0 #58d68d, stop: 1 #27ae60);
            }
            
            QPushButton#btn_delete {
                background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                                          stop: 0 #e74c3c, stop: 1 #c0392b);
            }
            
            QPushButton#btn_delete:hover {
                background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                                          stop: 0 #ec7063, stop: 1 #e74c3c);
            }
            
            QTableWidget {
                border: 2px solid #bdc3c7;
                border-radius: 8px;
                background-color: white;
                gridline-color: #ecf0f1;
                selection-background-color: #3498db;
                selection-color: white;
            }
            
            QTableWidget::item {
                padding: 8px;
            }
            
            QHeaderView::section {
                background-color: #34495e;
                color: white;
                padding: 10px;
                border: none;
                font-weight: bold;
                font-size: 10pt;
            }
            
            QHeaderView::section:first {
                border-top-left-radius: 6px;
            }
            
            QHeaderView::section:last {
                border-top-right-radius: 6px;
            }
            
            QLineEdit {
                border: 2px solid #bdc3c7;
                border-radius: 6px;
                padding: 8px 12px;
                background-color: white;
                font-size: 10pt;
            }
            
            QLineEdit:focus {
                border-color: #3498db;
            }
        """)

        layout = QVBoxLayout()
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)

        # Título
        title_label = QLabel("👥 Gerenciamento de Usuários")
        title_label.setFont(QFont("Segoe UI", 16, QFont.Bold))
        title_label.setStyleSheet("""
            QLabel {
                color: #2c3e50;
                padding: 15px;
                background-color: white;
                border-radius: 10px;
                border: 2px solid #3498db;
            }
        """)
        title_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(title_label)

        # Tabs para diferentes tipos de usuários
        self.tabs = QTabWidget()

        if self.user["user_type"] == "admin":
            self.admins_tab = self.create_users_tab("admin", "Administradores")
            self.doctors_tab = self.create_users_tab("doctor", "Médicos")
            self.patients_tab = self.create_users_tab("patient", "Pacientes")
            
            self.tabs.addTab(self.admins_tab, "🔑 Administradores")
            self.tabs.addTab(self.doctors_tab, "👨‍⚕️ Médicos")
            self.tabs.addTab(self.patients_tab, "👤 Pacientes")

            # Configurar fonte que suporta emojis
            emoji_font = QFont("Segoe UI Emoji", 11)
            for i in range(self.tabs.count()):
                self.tabs.tabBar().setFont(emoji_font)

        layout.addWidget(self.tabs)
        self.setLayout(layout)

        self.refresh_all_tables()

    def create_users_tab(self, user_type, title):
        widget = QWidget()
        layout = QVBoxLayout()
        layout.setContentsMargins(15, 15, 15, 15)
        layout.setSpacing(15)

        # Barra de pesquisa
        search_layout = QHBoxLayout()
        search_label = QLabel("🔍 Pesquisar:")
        search_label.setStyleSheet("font-weight: bold; color: #2c3e50;")
        
        search_input = QLineEdit()
        search_input.setPlaceholderText(f"Digite o nome ou email...")
        search_input.textChanged.connect(lambda: self.filter_table(user_type, search_input.text()))
        
        search_layout.addWidget(search_label)
        search_layout.addWidget(search_input)
        layout.addLayout(search_layout)

        # Botões de ação
        btn_layout = QHBoxLayout()
        
        add_btn = QPushButton(f"➕ Adicionar {title[:-1] if title.endswith('s') else title}")
        add_btn.setObjectName("btn_add")
        add_btn.setMinimumHeight(40)
        add_btn.clicked.connect(lambda: self.add_user(user_type))
        
        edit_btn = QPushButton(f"✏️ Editar")
        edit_btn.setMinimumHeight(40)
        edit_btn.clicked.connect(lambda: self.edit_user(user_type))
        
        delete_btn = QPushButton(f"🗑️ Excluir")
        delete_btn.setObjectName("btn_delete")
        delete_btn.setMinimumHeight(40)
        delete_btn.clicked.connect(lambda: self.delete_user(user_type))

        btn_layout.addWidget(add_btn)
        btn_layout.addWidget(edit_btn)
        btn_layout.addWidget(delete_btn)
        btn_layout.addStretch()

        layout.addLayout(btn_layout)

        # Tabela de usuários
        table = QTableWidget()
        
        if user_type == "admin":
            table.setColumnCount(4)
            table.setHorizontalHeaderLabels(["ID", "Nome", "Email", "Data Criação"])
        elif user_type == "doctor":
            table.setColumnCount(6)
            table.setHorizontalHeaderLabels(["ID", "Nome", "Email", "CRM", "Especialidade", "Data Criação"])
        else:  # patient
            table.setColumnCount(6)
            table.setHorizontalHeaderLabels(["ID", "Nome", "Email", "Data Nascimento", "Telefone", "Data Criação"])
        
        table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        table.setSelectionBehavior(QTableWidget.SelectRows)
        table.setSelectionMode(QTableWidget.SingleSelection)
        table.setAlternatingRowColors(True)
        table.verticalHeader().setVisible(False)
        
        # Oculta coluna ID
        table.setColumnHidden(0, True)

        layout.addWidget(table)
        
        # Label de contagem
        count_label = QLabel()
        count_label.setStyleSheet("""
            QLabel {
                color: #7f8c8d;
                font-style: italic;
                padding: 5px;
            }
        """)
        layout.addWidget(count_label)
        
        widget.setLayout(layout)

        # Armazena referências
        setattr(self, f"{user_type}_table", table)
        setattr(self, f"{user_type}_search", search_input)
        setattr(self, f"{user_type}_count", count_label)

        return widget

    def filter_table(self, user_type, search_text):
        """Filtra a tabela baseado no texto de pesquisa"""
        table = getattr(self, f"{user_type}_table")
        search_text = search_text.lower()
        
        for row in range(table.rowCount()):
            should_show = False
            for col in range(1, table.columnCount()):  # Pula coluna ID (0)
                item = table.item(row, col)
                if item and search_text in item.text().lower():
                    should_show = True
                    break
            table.setRowHidden(row, not should_show)

    def refresh_all_tables(self):
        if self.user["user_type"] == "admin":
            self.refresh_table("admin")
            self.refresh_table("doctor")
            self.refresh_table("patient")

    def refresh_table(self, user_type):
        table = getattr(self, f"{user_type}_table")
        count_label = getattr(self, f"{user_type}_count")
        users = self.db_manager.get_users_by_type(user_type)

        table.setRowCount(len(users))
        
        for i, user in enumerate(users):
            # ID (oculto)
            table.setItem(i, 0, QTableWidgetItem(str(user["_id"])))
            
            # Nome
            table.setItem(i, 1, QTableWidgetItem(user["name"]))
            
            # Email
            table.setItem(i, 2, QTableWidgetItem(user["email"]))
            
            if user_type == "admin":
                # Data de criação
                table.setItem(i, 3, QTableWidgetItem(
                    user["created_at"].strftime("%d/%m/%Y %H:%M")))
                    
            elif user_type == "doctor":
                # CRM
                table.setItem(i, 3, QTableWidgetItem(user.get("crm", "N/A")))
                
                # Especialidade
                table.setItem(i, 4, QTableWidgetItem(user.get("specialty", "N/A")))
                
                # Data de criação
                table.setItem(i, 5, QTableWidgetItem(
                    user["created_at"].strftime("%d/%m/%Y")))
                    
            else:  # patient
                # Data de nascimento
                birth_date = user.get("birth_date")
                birth_str = birth_date.strftime("%d/%m/%Y") if birth_date else "N/A"
                table.setItem(i, 3, QTableWidgetItem(birth_str))
                
                # Telefone
                table.setItem(i, 4, QTableWidgetItem(user.get("phone", "N/A")))
                
                # Data de criação
                table.setItem(i, 5, QTableWidgetItem(
                    user["created_at"].strftime("%d/%m/%Y")))
        
        # Atualiza contagem
        count_label.setText(f"Total: {len(users)} registro(s)")

    def add_user(self, user_type):
        dialog = UserDialog(self.db_manager, user_type)
        if dialog.exec_():
            self.refresh_table(user_type)

    def edit_user(self, user_type):
        table = getattr(self, f"{user_type}_table")
        current_row = table.currentRow()
        
        if current_row < 0:
            QMessageBox.warning(
                self, "⚠️ Atenção", "Selecione um usuário para editar!")
            return

        user_id = table.item(current_row, 0).text()
        
        dialog = UserDialog(self.db_manager, user_type, user_id)
        if dialog.exec_():
            self.refresh_table(user_type)

    def delete_user(self, user_type):
        table = getattr(self, f"{user_type}_table")
        current_row = table.currentRow()
        
        if current_row < 0:
            QMessageBox.warning(
                self, "⚠️ Atenção", "Selecione um usuário para excluir!")
            return

        user_id = table.item(current_row, 0).text()
        user_name = table.item(current_row, 1).text()
        
        # Não permite excluir o próprio usuário logado
        if str(self.user["_id"]) == user_id:
            QMessageBox.warning(
                self, "⚠️ Atenção", 
                "Você não pode excluir seu próprio usuário!"
            )
            return

        reply = QMessageBox.question(
            self, "⚠️ Confirmar Exclusão",
            f"Deseja realmente excluir o usuário:\n\n"
            f"👤 {user_name}\n\n"
            f"Esta ação não pode ser desfeita!",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )

        if reply == QMessageBox.Yes:
            if self.db_manager.delete_user(user_id):
                QMessageBox.information(
                    self, "✅ Sucesso", "Usuário excluído com sucesso!")
                self.refresh_table(user_type)
            else:
                QMessageBox.warning(
                    self, "❌ Erro", "Erro ao excluir usuário!")