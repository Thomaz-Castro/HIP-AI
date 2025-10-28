from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QPushButton,
    QHBoxLayout, QTableWidget, QTableWidgetItem, QHeaderView, QMessageBox,
    QTabWidget, QLabel, QLineEdit, QCheckBox
)
from PyQt5.QtGui import QFont, QColor
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
            
            QPushButton#btn_reactivate {
                background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                                          stop: 0 #f39c12, stop: 1 #e67e22);
            }
            
            QPushButton#btn_reactivate:hover {
                background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                                          stop: 0 #f5b041, stop: 1 #f39c12);
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
            
            QCheckBox {
                font-size: 10pt;
                color: #2c3e50;
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

        # Barra de pesquisa e filtros
        search_layout = QHBoxLayout()
        search_label = QLabel("🔍 Pesquisar:")
        search_label.setStyleSheet("font-weight: bold; color: #2c3e50;")
        
        search_input = QLineEdit()
        search_input.setPlaceholderText(f"Digite o nome, email ou CPF...")
        search_input.textChanged.connect(lambda: self.filter_table(user_type, search_input.text()))
        
        # Checkbox para mostrar inativos
        show_inactive_check = QCheckBox("Mostrar inativos")
        show_inactive_check.stateChanged.connect(lambda: self.refresh_table(user_type))
        
        search_layout.addWidget(search_label)
        search_layout.addWidget(search_input)
        search_layout.addWidget(show_inactive_check)
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
        
        if user_type in ['doctor', 'patient']:
            delete_btn = QPushButton(f"🔒 Desativar")
            delete_btn.setObjectName("btn_delete")
            delete_btn.setMinimumHeight(40)
            delete_btn.clicked.connect(lambda: self.deactivate_user(user_type))
            
            reactivate_btn = QPushButton(f"🔓 Reativar")
            reactivate_btn.setObjectName("btn_reactivate")
            reactivate_btn.setMinimumHeight(40)
            reactivate_btn.clicked.connect(lambda: self.reactivate_user(user_type))
        else:
            delete_btn = QPushButton(f"🗑️ Excluir")
            delete_btn.setObjectName("btn_delete")
            delete_btn.setMinimumHeight(40)
            delete_btn.clicked.connect(lambda: self.delete_user(user_type))

        btn_layout.addWidget(add_btn)
        btn_layout.addWidget(edit_btn)
        btn_layout.addWidget(delete_btn)
        if user_type in ['doctor', 'patient']:
            btn_layout.addWidget(reactivate_btn)
        btn_layout.addStretch()

        layout.addLayout(btn_layout)

        # Tabela de usuários
        table = QTableWidget()
        
        if user_type == "admin":
            table.setColumnCount(5)
            table.setHorizontalHeaderLabels(["ID", "Nome", "Email", "CPF", "Data Criação"])
        elif user_type == "doctor":
            table.setColumnCount(8)
            table.setHorizontalHeaderLabels(["ID", "Nome", "Email", "CPF", "CRM", "Especialidade", "Status", "Data Criação"])
        else:  # patient
            table.setColumnCount(8)
            table.setHorizontalHeaderLabels(["ID", "Nome", "Email", "CPF", "Data Nascimento", "Telefone", "Status", "Data Criação"])
        
        table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        table.setSelectionBehavior(QTableWidget.SelectRows)
        table.setSelectionMode(QTableWidget.SingleSelection)
        table.setAlternatingRowColors(True)
        table.verticalHeader().setVisible(False)
        table.setEditTriggers(QTableWidget.NoEditTriggers)  # Tabela read-only
        
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
        setattr(self, f"{user_type}_show_inactive", show_inactive_check)

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
        show_inactive = getattr(self, f"{user_type}_show_inactive", None)
        
        include_inactive = show_inactive.isChecked() if show_inactive else False
        users = self.db_manager.get_users_by_type(user_type, include_inactive)

        table.setRowCount(len(users))
        
        active_count = 0
        inactive_count = 0
        
        for i, user in enumerate(users):
            is_active = user.get("is_active", True)
            
            if is_active:
                active_count += 1
            else:
                inactive_count += 1
            
            # ID (oculto)
            table.setItem(i, 0, QTableWidgetItem(str(user["id"])))
            
            # Nome
            name_item = QTableWidgetItem(user["name"])
            if not is_active:
                name_item.setForeground(QColor("#95a5a6"))
            table.setItem(i, 1, name_item)
            
            # Email
            email_item = QTableWidgetItem(user["email"])
            if not is_active:
                email_item.setForeground(QColor("#95a5a6"))
            table.setItem(i, 2, email_item)
            
            # CPF
            cpf_item = QTableWidgetItem(user.get("cpf", "N/A"))
            if not is_active:
                cpf_item.setForeground(QColor("#95a5a6"))
            table.setItem(i, 3, cpf_item)
            
            if user_type == "admin":
                # Data de criação
                date_item = QTableWidgetItem(user["created_at"].strftime("%d/%m/%Y %H:%M"))
                if not is_active:
                    date_item.setForeground(QColor("#95a5a6"))
                table.setItem(i, 4, date_item)
                    
            elif user_type == "doctor":
                # CRM
                crm_item = QTableWidgetItem(user.get("crm", "N/A"))
                if not is_active:
                    crm_item.setForeground(QColor("#95a5a6"))
                table.setItem(i, 4, crm_item)
                
                # Especialidade
                specialty_item = QTableWidgetItem(user.get("specialty", "N/A"))
                if not is_active:
                    specialty_item.setForeground(QColor("#95a5a6"))
                table.setItem(i, 5, specialty_item)
                
                # Status
                status_item = QTableWidgetItem("✅ Ativo" if is_active else "❌ Inativo")
                status_item.setForeground(QColor("#27ae60") if is_active else QColor("#e74c3c"))
                table.setItem(i, 6, status_item)
                
                # Data de criação
                date_item = QTableWidgetItem(user["created_at"].strftime("%d/%m/%Y"))
                if not is_active:
                    date_item.setForeground(QColor("#95a5a6"))
                table.setItem(i, 7, date_item)
                    
            else:  # patient
                # Data de nascimento
                birth_date = user.get("birth_date")
                birth_str = birth_date.strftime("%d/%m/%Y") if birth_date else "N/A"
                birth_item = QTableWidgetItem(birth_str)
                if not is_active:
                    birth_item.setForeground(QColor("#95a5a6"))
                table.setItem(i, 4, birth_item)
                
                # Telefone
                phone_item = QTableWidgetItem(user.get("phone", "N/A"))
                if not is_active:
                    phone_item.setForeground(QColor("#95a5a6"))
                table.setItem(i, 5, phone_item)
                
                # Status
                status_item = QTableWidgetItem("✅ Ativo" if is_active else "❌ Inativo")
                status_item.setForeground(QColor("#27ae60") if is_active else QColor("#e74c3c"))
                table.setItem(i, 6, status_item)
                
                # Data de criação
                date_item = QTableWidgetItem(user["created_at"].strftime("%d/%m/%Y"))
                if not is_active:
                    date_item.setForeground(QColor("#95a5a6"))
                table.setItem(i, 7, date_item)
        
        # Atualiza contagem
        if include_inactive:
            count_label.setText(
                f"Total: {len(users)} registro(s) - "
                f"✅ Ativos: {active_count} | ❌ Inativos: {inactive_count}"
            )
        else:
            count_label.setText(f"Total: {active_count} registro(s) ativos")

    def add_user(self, user_type):
        dialog = UserDialog(self.db_manager, user_type, current_user=self.user)
        if dialog.exec_():
            self.refresh_table(user_type)

    def edit_user(self, user_type):
        table = getattr(self, f"{user_type}_table")
        current_row = table.currentRow()
        
        if current_row < 0:
            QMessageBox.warning(
                self, "⚠️ Atenção", "Selecione um usuário para editar!")
            return

        user_id_str = table.item(current_row, 0).text()
        
        dialog = UserDialog(self.db_manager, user_type, int(user_id_str), self.user)
        if dialog.exec_():
            self.refresh_table(user_type)

    def deactivate_user(self, user_type):
        """Desativa um usuário (soft delete)"""
        table = getattr(self, f"{user_type}_table")
        current_row = table.currentRow()
        
        if current_row < 0:
            QMessageBox.warning(
                self, "⚠️ Atenção", "Selecione um usuário para desativar!")
            return

        user_id_str = table.item(current_row, 0).text()
        user_name = table.item(current_row, 1).text()

        user_id_int = int(user_id_str)
        
        # Não permite desativar o próprio usuário logado
        if self.user["id"] == user_id_int:
            QMessageBox.warning(
                self, "⚠️ Atenção", 
                "Você não pode desativar seu próprio usuário!"
            )
            return

        reply = QMessageBox.question(
            self, "⚠️ Confirmar Desativação",
            f"Deseja realmente desativar o usuário:\n\n"
            f"👤 {user_name}\n\n"
            f"🔒 O usuário será desativado mas seus dados serão mantidos.\n"
            f"Você poderá reativá-lo posteriormente.",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )

        if reply == QMessageBox.Yes:
            if self.db_manager.soft_delete_user(user_id_int, self.user["id"]):
                QMessageBox.information(
                    self, "✅ Sucesso", 
                    "Usuário desativado com sucesso!\n\n"
                    "Os dados foram preservados e podem ser reativados."
                )
                self.refresh_table(user_type)
            else:
                QMessageBox.warning(
                    self, "❌ Erro", "Erro ao desativar usuário!")

    def reactivate_user(self, user_type):
        """Reativa um usuário desativado"""
        table = getattr(self, f"{user_type}_table")
        current_row = table.currentRow()
        
        if current_row < 0:
            QMessageBox.warning(
                self, "⚠️ Atenção", "Selecione um usuário para reativar!")
            return

        user_id_str = table.item(current_row, 0).text()
        user_name = table.item(current_row, 1).text()
        user_id_int = int(user_id_str)
        
        # Verifica se o usuário está inativo
        user = self.db_manager.get_user_by_id(user_id_int)
        if user and user.get("is_active", True):
            QMessageBox.warning(
                self, "⚠️ Atenção", 
                "Este usuário já está ativo!"
            )
            return

        reply = QMessageBox.question(
            self, "⚠️ Confirmar Reativação",
            f"Deseja realmente reativar o usuário:\n\n"
            f"👤 {user_name}\n\n"
            f"🔓 O usuário voltará a ter acesso ao sistema.",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )

        if reply == QMessageBox.Yes:
            if self.db_manager.reactivate_user(user_id_int, self.user["id"]):
                QMessageBox.information(
                    self, "✅ Sucesso", "Usuário reativado com sucesso!")
                self.refresh_table(user_type)
            else:
                QMessageBox.warning(
                    self, "❌ Erro", "Erro ao reativar usuário!")

    def delete_user(self, user_type):
        """Deleta permanentemente um usuário (apenas admins)"""
        table = getattr(self, f"{user_type}_table")
        current_row = table.currentRow()
        
        if current_row < 0:
            QMessageBox.warning(
                self, "⚠️ Atenção", "Selecione um usuário para excluir!")
            return

        user_id_str = table.item(current_row, 0).text()
        user_name = table.item(current_row, 1).text()

        user_id_int = int(user_id_str)
        
        # Não permite excluir o próprio usuário logado
        if self.user["id"] == user_id_int:
            QMessageBox.warning(
                self, "⚠️ Atenção", 
                "Você não pode excluir seu próprio usuário!"
            )
            return

        reply = QMessageBox.question(
            self, "⚠️ ATENÇÃO - Exclusão Permanente",
            f"⛔ CUIDADO: Esta ação é IRREVERSÍVEL!\n\n"
            f"Deseja realmente excluir PERMANENTEMENTE o usuário:\n\n"
            f"👤 {user_name}\n\n"
            f"🗑️ Todos os dados serão perdidos definitivamente!\n"
            f"⚠️ Esta opção só está disponível para administradores.",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )

        if reply == QMessageBox.Yes:
            if self.db_manager.delete_user(user_id_int):
                QMessageBox.information(
                    self, "✅ Sucesso", "Usuário excluído permanentemente!")
                self.refresh_table(user_type)
            else:
                QMessageBox.warning(
                    self, "❌ Erro", "Erro ao excluir usuário!")