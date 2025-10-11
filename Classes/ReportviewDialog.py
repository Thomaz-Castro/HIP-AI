import json
from PyQt5.QtWidgets import (
    QVBoxLayout, QFormLayout, QLabel, QPushButton,
    QTextEdit, QDialog
)

class ReportViewDialog(QDialog):
    def __init__(self, report):
        super().__init__()
        self.report = report
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("Visualizar Relatório")
        self.setModal(True)
        self.resize(800, 600)

        layout = QVBoxLayout()

        # Informações do relatório
        info_layout = QFormLayout()

        # Verifica se o relatório tem dados de paciente/médico embedded
        if "patient" in self.report:
            info_layout.addRow("Paciente:", QLabel(
                self.report["patient"]["name"]))
            info_layout.addRow("Médico:", QLabel(
                self.report["doctor"]["name"]))

        info_layout.addRow("Data:", QLabel(
            self.report["created_at"].strftime("%d/%m/%Y %H:%M")))

        layout.addLayout(info_layout)

        # Dados da avaliação
        data_text = QTextEdit()
        data_text.setReadOnly(True)

        # Formata os dados para exibição
        report_data = self.report["report_data"]
        content = f"""
📊 DADOS DA AVALIAÇÃO:
{json.dumps(report_data.get('input_data', {}), ensure_ascii=False, indent=2)}

🤖 RESULTADO DA IA:
{report_data.get('ai_result', 'N/A')}
"""

        data_text.setPlainText(content)
        layout.addWidget(data_text)

        # Botão fechar
        close_btn = QPushButton("Fechar")
        close_btn.clicked.connect(self.accept)
        layout.addWidget(close_btn)

        self.setLayout(layout)

