from PyQt5.QtWidgets import (
    QVBoxLayout, QFormLayout, 
    QPushButton, QHBoxLayout,
    QLineEdit, QMessageBox,
    QDateEdit, QDialog
)
from PyQt5.QtCore import QDate


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
        self.setWindowTitle(
            f"{'Editar' if self.user_id else 'Adicionar'} {self.user_type.title()}")
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
            self.password_input.setPlaceholderText(
                "Deixe em branco para manter senha atual")
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
        user = self.db_manager.db.users.find_one(
            {"_id": ObjectId(self.user_id)})
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
            QMessageBox.warning(
                self, "Erro", "Senha é obrigatória para novos usuários!")
            return

        # Dados específicos
        additional_data = {}
        if self.user_type == "doctor":
            additional_data["crm"] = self.crm_input.text().strip()
            additional_data["specialty"] = self.specialty_input.text().strip()
        elif self.user_type == "patient":
            additional_data["birth_date"] = self.birth_date_input.date(
            ).toPyDate()
            additional_data["phone"] = self.phone_input.text().strip()

        if self.user_id:
            # Editar usuário existente
            update_data = {"name": name, "email": email}
            if password:
                update_data["password"] = self.db_manager.hash_password(
                    password)
            update_data.update(additional_data)

            if self.db_manager.update_user(self.user_id, update_data):
                QMessageBox.information(
                    self, "Sucesso", "Usuário atualizado com sucesso!")
                self.accept()
            else:
                QMessageBox.warning(self, "Erro", "Erro ao atualizar usuário!")
        else:
            # Criar novo usuário
            user_id = self.db_manager.create_user(
                name, email, password, self.user_type, additional_data)
            if user_id:
                QMessageBox.information(
                    self, "Sucesso", "Usuário criado com sucesso!")
                self.accept()
            else:
                QMessageBox.warning(
                    self, "Erro", "Erro ao criar usuário! Verifique se o email já não está em uso.")

