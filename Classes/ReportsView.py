from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QPushButton,
    QTableWidget, QTableWidgetItem, QHeaderView
)

from Classes.ReportviewDialog import ReportViewDialog

class ReportsView(QWidget):
    def __init__(self, db_manager, user):
        super().__init__()
        self.db_manager = db_manager
        self.user = user
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()

        # Botão de atualizar
        refresh_btn = QPushButton("🔄 Atualizar Relatórios")
        refresh_btn.clicked.connect(self.load_reports)
        layout.addWidget(refresh_btn)

        # Tabela de relatórios
        self.table = QTableWidget()
        if self.user["user_type"] == "patient":
            self.table.setColumnCount(3)
            self.table.setHorizontalHeaderLabels(["Médico", "Data", "Ações"])
        else:
            self.table.setColumnCount(4)
            self.table.setHorizontalHeaderLabels(
                ["Paciente", "Médico", "Data", "Ações"])

        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        layout.addWidget(self.table)

        self.setLayout(layout)
        self.load_reports()

    def load_reports(self):
        if self.user["user_type"] == "patient":
            reports = self.db_manager.get_patient_reports(self.user["_id"])
            self.table.setRowCount(len(reports))

            for i, report in enumerate(reports):
                # Busca dados do médico
                doctor = self.db_manager.db.users.find_one(
                    {"_id": report["doctor_id"]})
                doctor_name = doctor["name"] if doctor else "N/A"

                self.table.setItem(i, 0, QTableWidgetItem(doctor_name))
                self.table.setItem(i, 1, QTableWidgetItem(
                    report["created_at"].strftime("%d/%m/%Y %H:%M")))

                # Botão para visualizar
                view_btn = QPushButton("👁️ Visualizar")
                view_btn.clicked.connect(
                    lambda checked, r=report: self.view_report(r))
                self.table.setCellWidget(i, 2, view_btn)

        else:  # admin ou doctor
            reports = self.db_manager.get_all_reports()
            self.table.setRowCount(len(reports))

            for i, report in enumerate(reports):
                self.table.setItem(i, 0, QTableWidgetItem(
                    report["patient"]["name"]))
                self.table.setItem(i, 1, QTableWidgetItem(
                    report["doctor"]["name"]))
                self.table.setItem(i, 2, QTableWidgetItem(
                    report["created_at"].strftime("%d/%m/%Y %H:%M")))

                # Botão para visualizar
                view_btn = QPushButton("👁️ Visualizar")
                view_btn.clicked.connect(
                    lambda checked, r=report: self.view_report(r))
                self.table.setCellWidget(i, 3, view_btn)

    def view_report(self, report):
        dialog = ReportViewDialog(report)
        dialog.exec_()

