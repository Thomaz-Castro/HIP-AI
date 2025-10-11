from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QPushButton, QHBoxLayout,
    QTableWidget, QTableWidgetItem, QHeaderView, QLineEdit,
    QLabel, QComboBox, QDateEdit, QFrame, QSpacerItem, QSizePolicy,
    QScrollArea
)
from PyQt5.QtCore import Qt, QDate
from PyQt5.QtGui import QFont, QColor

from Classes.ReportviewDialog import ReportViewDialog


class ReportsView(QWidget):
    def __init__(self, db_manager, user):
        super().__init__()
        self.db_manager = db_manager
        self.user = user
        self.all_reports = []
        self.init_ui()

    def init_ui(self):
        # Estilo moderno
        self.setStyleSheet("""
            QWidget {
                background-color: #f5f7fa;
                font-family: 'Segoe UI', Arial, sans-serif;
            }
            
            QScrollArea {
                border: none;
                background-color: #f5f7fa;
            }
            
            QLabel {
                color: #2c3e50;
                font-size: 10pt;
            }
            
            QLabel#title {
                font-size: 18pt;
                font-weight: bold;
                color: #2c3e50;
                padding: 10px;
            }
            
            QLabel#subtitle {
                font-size: 11pt;
                color: #7f8c8d;
                font-style: italic;
            }
            
            QLineEdit, QComboBox, QDateEdit {
                border: 2px solid #bdc3c7;
                border-radius: 6px;
                padding: 8px 12px;
                background-color: white;
                font-size: 10pt;
                min-height: 25px;
            }
            
            QLineEdit:focus, QComboBox:focus, QDateEdit:focus {
                border-color: #3498db;
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
                min-height: 35px;
            }
            
            QPushButton:hover {
                background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                                            stop: 0 #5dade2, stop: 1 #3498db);
            }
            
            QPushButton:pressed {
                background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                                            stop: 0 #2980b9, stop: 1 #21618c);
            }
            
            QPushButton#btn_refresh {
                background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                                            stop: 0 #27ae60, stop: 1 #229954);
            }
            
            QPushButton#btn_refresh:hover {
                background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                                            stop: 0 #58d68d, stop: 1 #27ae60);
            }
            
            QPushButton#btn_clear {
                background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                                            stop: 0 #95a5a6, stop: 1 #7f8c8d);
            }
            
            QPushButton#btn_clear:hover {
                background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                                            stop: 0 #b2babb, stop: 1 #95a5a6);
            }
            
            QPushButton#btn_view {
                background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                                            stop: 0 #3498db, stop: 1 #2980b9);
                padding: 6px 15px;
                font-size: 9pt;
                min-height: 25px;
            }
            
            QPushButton#btn_view:hover {
                background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                                            stop: 0 #5dade2, stop: 1 #3498db);
            }
            
            QTableWidget {
                background-color: white;
                border: 2px solid #dce1e8;
                border-radius: 8px;
                gridline-color: #ecf0f1;
                selection-background-color: #d6eaf8;
                selection-color: #2c3e50;
            }
            
            QTableWidget::item {
                padding: 8px;
                border-bottom: 1px solid #ecf0f1;
            }
            
            QTableWidget::item:selected {
                background-color: #d6eaf8;
                color: #2c3e50;
            }
            
            QHeaderView::section {
                background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                                            stop: 0 #34495e, stop: 1 #2c3e50);
                color: white;
                padding: 10px;
                border: none;
                font-weight: bold;
                font-size: 10pt;
            }
            
            QFrame#filter_frame {
                background-color: white;
                border: 2px solid #dce1e8;
                border-radius: 8px;
                padding: 15px;
                margin: 5px;
            }
            
            QFrame#stats_frame {
                background-color: white;
                border: 2px solid #dce1e8;
                border-radius: 8px;
                padding: 10px;
                margin: 5px;
            }
        """)

        main_wrapper_layout = QVBoxLayout(self)
        main_wrapper_layout.setContentsMargins(0, 0, 0, 0)
        main_wrapper_layout.setSpacing(0)

        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)

        content_widget = QWidget()
        main_layout = QVBoxLayout(content_widget)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(15)

        title = QLabel("📊 Relatórios Médicos")
        title.setObjectName("title")
        main_layout.addWidget(title)

        stats_frame = self.create_stats_frame()
        main_layout.addWidget(stats_frame)

        filter_frame = self.create_filter_frame()
        main_layout.addWidget(filter_frame)

        self.create_table()
        main_layout.addWidget(self.table)

        action_layout = QHBoxLayout()
        action_layout.addStretch()

        refresh_btn = QPushButton("🔄 Atualizar")
        refresh_btn.setObjectName("btn_refresh")
        refresh_btn.clicked.connect(self.load_reports)
        refresh_btn.setFixedWidth(150)

        action_layout.addWidget(refresh_btn)
        main_layout.addLayout(action_layout)

        scroll_area.setWidget(content_widget)
        main_wrapper_layout.addWidget(scroll_area)

        self.load_reports()

    def create_stats_frame(self):
        """Cria frame com estatísticas"""
        stats_frame = QFrame()
        stats_frame.setObjectName("stats_frame")
        stats_layout = QHBoxLayout(stats_frame)

        self.total_label = QLabel("📄 Total: 0")
        self.total_label.setStyleSheet("font-size: 11pt; font-weight: bold; color: #3498db;")

        self.month_label = QLabel("📅 Este mês: 0")
        self.month_label.setStyleSheet("font-size: 11pt; font-weight: bold; color: #27ae60;")

        self.today_label = QLabel("⏰ Hoje: 0")
        self.today_label.setStyleSheet("font-size: 11pt; font-weight: bold; color: #e74c3c;")

        stats_layout.addWidget(self.total_label)
        stats_layout.addSpacing(30)
        stats_layout.addWidget(self.month_label)
        stats_layout.addSpacing(30)
        stats_layout.addWidget(self.today_label)
        stats_layout.addStretch()

        return stats_frame

    def create_filter_frame(self):
        """Cria frame com filtros"""
        filter_frame = QFrame()
        filter_frame.setObjectName("filter_frame")
        filter_layout = QVBoxLayout(filter_frame)

        filter_title = QLabel("🔍 Filtros")
        filter_title.setStyleSheet("font-size: 12pt; font-weight: bold; color: #2c3e50;")
        filter_layout.addWidget(filter_title)

        filters_grid = QHBoxLayout()
        filters_grid.setSpacing(15)

        # Filtro de busca por texto
        search_layout = QVBoxLayout()
        search_label = QLabel("Buscar:")
        self.search_input = QLineEdit()
        # Placeholder muda dependendo do tipo de usuário
        placeholder = "Nome do médico..." if self.user["user_type"] == "patient" else "Nome do paciente ou médico..."
        self.search_input.setPlaceholderText(placeholder)
        self.search_input.textChanged.connect(self.apply_filters)
        search_layout.addWidget(search_label)
        search_layout.addWidget(self.search_input)
        filters_grid.addLayout(search_layout)

        
        # Filtro por período
        period_layout = QVBoxLayout()
        period_label = QLabel("Período:")
        self.period_combo = QComboBox()
        self.period_combo.addItems([
            "Todos",
            "Hoje",
            "Últimos 7 dias",
            "Últimos 30 dias",
            "Este mês",
            "Personalizado"
        ])
        self.period_combo.currentTextChanged.connect(self.on_period_changed)
        period_layout.addWidget(period_label)
        period_layout.addWidget(self.period_combo)
        filters_grid.addLayout(period_layout)

        # Data inicial
        date_from_layout = QVBoxLayout()
        date_from_label = QLabel("Data inicial:")
        self.date_from = QDateEdit()
        self.date_from.setCalendarPopup(True)
        self.date_from.setDisplayFormat("dd/MM/yyyy")
        self.date_from.setDate(QDate.currentDate().addMonths(-1))
        self.date_from.setEnabled(False)
        self.date_from.dateChanged.connect(self.apply_filters)
        date_from_layout.addWidget(date_from_label)
        date_from_layout.addWidget(self.date_from)
        filters_grid.addLayout(date_from_layout)

        # Data final
        date_to_layout = QVBoxLayout()
        date_to_label = QLabel("Data final:")
        self.date_to = QDateEdit()
        self.date_to.setCalendarPopup(True)
        self.date_to.setDisplayFormat("dd/MM/yyyy")
        self.date_to.setDate(QDate.currentDate())
        self.date_to.setEnabled(False)
        self.date_to.dateChanged.connect(self.apply_filters)
        date_to_layout.addWidget(date_to_label)
        date_to_layout.addWidget(self.date_to)
        filters_grid.addLayout(date_to_layout)

        filters_grid.addStretch()

        # Botão limpar filtros
        clear_btn = QPushButton("✖ Limpar Filtros")
        clear_btn.setObjectName("btn_clear")
        clear_btn.clicked.connect(self.clear_filters)
        clear_btn.setFixedWidth(150)
        filters_grid.addWidget(clear_btn)

        filter_layout.addLayout(filters_grid)
        return filter_frame

    def create_table(self):
        """Cria a tabela de relatórios"""
        self.table = QTableWidget()
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        self.table.setSelectionMode(QTableWidget.SingleSelection)
        self.table.setAlternatingRowColors(True)
        self.table.verticalHeader().setVisible(False)
        self.table.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

        if self.user["user_type"] == "patient":
            self.table.setColumnCount(3)
            self.table.setHorizontalHeaderLabels(["👨‍⚕️ Médico", "📅 Data e Hora", "⚙️ Ações"])
        else:
            self.table.setColumnCount(4)
            self.table.setHorizontalHeaderLabels([
                "👤 Paciente", "👨‍⚕️ Médico", "📅 Data e Hora", "⚙️ Ações"
            ])

        header = self.table.horizontalHeader()
        if self.user["user_type"] == "patient":
            header.setSectionResizeMode(0, QHeaderView.Stretch)
            header.setSectionResizeMode(1, QHeaderView.ResizeToContents)
            header.setSectionResizeMode(2, QHeaderView.Fixed)
            self.table.setColumnWidth(2, 150)
        else:
            header.setSectionResizeMode(0, QHeaderView.Stretch)
            header.setSectionResizeMode(1, QHeaderView.Stretch)
            header.setSectionResizeMode(2, QHeaderView.ResizeToContents)
            header.setSectionResizeMode(3, QHeaderView.Fixed)
            self.table.setColumnWidth(3, 150)

        self.table.verticalHeader().setDefaultSectionSize(50)

    def on_period_changed(self, period):
        """Ativa/desativa campos de data personalizada"""
        is_custom = period == "Personalizado"
        self.date_from.setEnabled(is_custom)
        self.date_to.setEnabled(is_custom)
        if not is_custom:
            self.apply_filters()

    def clear_filters(self):
        """Limpa todos os filtros"""
        self.search_input.clear()
        
        self.period_combo.setCurrentIndex(0)
        self.date_from.setDate(QDate.currentDate().addMonths(-1))
        self.date_to.setDate(QDate.currentDate())
        

        self.apply_filters()

    def load_reports(self):
        """Carrega os relatórios do banco de dados com base no tipo de usuário."""
        if self.user["user_type"] == "patient":
            reports = self.db_manager.get_patient_reports(self.user["_id"])
            self.all_reports = []
            for report in reports:
                doctor = self.db_manager.db.users.find_one({"_id": report["doctor_id"]})
                report["doctor"] = doctor if doctor else {"name": "N/A"}
                self.all_reports.append(report)
        elif self.user["user_type"] == "doctor":
            self.all_reports = self.db_manager.get_doctor_reports(self.user["_id"])
        else:
            self.all_reports = self.db_manager.get_all_reports()

        self.update_statistics()
        self.apply_filters()

    def update_statistics(self):
        """Atualiza as estatísticas"""
        from datetime import datetime

        total = len(self.all_reports)
        
        today = datetime.now().date()
        today_count = sum(1 for r in self.all_reports 
                          if r["created_at"].date() == today)
        
        current_month = datetime.now().month
        current_year = datetime.now().year
        month_count = sum(1 for r in self.all_reports 
                          if r["created_at"].month == current_month 
                          and r["created_at"].year == current_year)

        self.total_label.setText(f"📄 Total: {total}")
        self.month_label.setText(f"📅 Este mês: {month_count}")
        self.today_label.setText(f"⏰ Hoje: {today_count}")

    def apply_filters(self):
        """Aplica os filtros na tabela"""
        from datetime import datetime, timedelta

        filtered_reports = self.all_reports.copy()
        
        # Filtro de busca por texto
        search_text = self.search_input.text().lower().strip()
        if search_text:
            if self.user["user_type"] == "patient":
                # Paciente só busca por nome do médico
                filtered_reports = [
                    r for r in filtered_reports
                    if search_text in r.get("doctor", {}).get("name", "").lower()
                ]
            else:
                # Outros usuários buscam por paciente ou médico
                filtered_reports = [
                    r for r in filtered_reports
                    if search_text in r.get("patient", {}).get("name", "").lower()
                    or search_text in r.get("doctor", {}).get("name", "").lower()
                ]

        period = self.period_combo.currentText()
        now = datetime.now()
        
        if period == "Hoje":
            today = now.date()
            filtered_reports = [r for r in filtered_reports 
                                if r["created_at"].date() == today]
        elif period == "Últimos 7 dias":
            week_ago = now - timedelta(days=7)
            filtered_reports = [r for r in filtered_reports 
                                if r["created_at"] >= week_ago]
        elif period == "Últimos 30 dias":
            month_ago = now - timedelta(days=30)
            filtered_reports = [r for r in filtered_reports 
                                if r["created_at"] >= month_ago]
        elif period == "Este mês":
            filtered_reports = [r for r in filtered_reports 
                                if r["created_at"].month == now.month 
                                and r["created_at"].year == now.year]
        elif period == "Personalizado":
            date_from = self.date_from.date().toPyDate()
            date_to = self.date_to.date().toPyDate()
            filtered_reports = [r for r in filtered_reports 
                                if date_from <= r["created_at"].date() <= date_to]

        self.display_reports(filtered_reports)

    def display_reports(self, reports):
        """Exibe os relatórios na tabela"""
        self.table.setRowCount(len(reports))

        for i, report in enumerate(reports):
            if self.user["user_type"] == "patient":
                doctor_name = report["doctor"]["name"]
                
                self.table.setItem(i, 0, QTableWidgetItem(doctor_name))
                self.table.setItem(i, 1, QTableWidgetItem(
                    report["created_at"].strftime("%d/%m/%Y às %H:%M")))

                view_btn = QPushButton("👁️ Visualizar")
                view_btn.setObjectName("btn_view")
                view_btn.clicked.connect(lambda checked, r=report: self.view_report(r))
                self.table.setCellWidget(i, 2, view_btn)
            else:
                patient_name = report["patient"]["name"]
                doctor_name = report["doctor"]["name"]
                
                self.table.setItem(i, 0, QTableWidgetItem(patient_name))
                self.table.setItem(i, 1, QTableWidgetItem(doctor_name))
                self.table.setItem(i, 2, QTableWidgetItem(
                    report["created_at"].strftime("%d/%m/%Y às %H:%M")))

                view_btn = QPushButton("👁️ Visualizar")
                view_btn.setObjectName("btn_view")
                view_btn.clicked.connect(lambda checked, r=report: self.view_report(r))
                self.table.setCellWidget(i, 3, view_btn)

        header_height = self.table.horizontalHeader().height()
        rows_height = sum([self.table.rowHeight(i) for i in range(self.table.rowCount())])
        
        total_height = header_height + rows_height + 5
        
        self.table.setFixedHeight(total_height)

    def view_report(self, report):
        """Abre o diálogo para visualizar o relatório"""
        dialog = ReportViewDialog(report)
        dialog.exec_()