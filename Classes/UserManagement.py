from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QPushButton,
    QHBoxLayout, QTableWidget, QTableWidgetItem, QHeaderView, QMessageBox,
    QTabWidget
)

from Classes.UserDialog import UserDialog

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
        table.setHorizontalHeaderLabels(
            ["ID", "Nome", "Email", "Data Criação"])
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
            table.setItem(i, 3, QTableWidgetItem(
                user["created_at"].strftime("%d/%m/%Y")))

    def add_user(self, user_type):
        dialog = UserDialog(self.db_manager, user_type)
        if dialog.exec_():
            self.refresh_table(user_type)

    def edit_user(self, user_type):
        table = getattr(self, f"{user_type}_table")
        current_row = table.currentRow()
        if current_row < 0:
            QMessageBox.warning(
                self, "Erro", "Selecione um usuário para editar!")
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
                self, "Erro", "Selecione um usuário para excluir!")
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
                QMessageBox.information(
                    self, "Sucesso", "Usuário excluído com sucesso!")
                self.refresh_table(user_type)
            else:
                QMessageBox.warning(self, "Erro", "Erro ao excluir usuário!")

