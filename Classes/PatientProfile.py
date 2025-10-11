from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QFormLayout, QGroupBox,
    QPushButton,
    QHBoxLayout, QLineEdit, QMessageBox,
    QDateEdit
)

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
            QMessageBox.information(
                self, "Sucesso", "Perfil atualizado com sucesso!")
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
            QMessageBox.warning(
                self, "Erro", "Nova senha e confirmação não coincidem!")
            return

        # Verifica senha atual
        if self.user["password"] != self.db_manager.hash_password(old_password):
            QMessageBox.warning(self, "Erro", "Senha atual incorreta!")
            return

        # Atualiza senha
        update_data = {"password": self.db_manager.hash_password(new_password)}
        if self.db_manager.update_user(str(self.user["_id"]), update_data):
            self.user["password"] = update_data["password"]
            QMessageBox.information(
                self, "Sucesso", "Senha alterada com sucesso!")
            self.old_password_input.clear()
            self.new_password_input.clear()
            self.confirm_password_input.clear()
        else:
            QMessageBox.warning(self, "Erro", "Erro ao alterar senha!")

