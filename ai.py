import sys
import json
from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QFormLayout, QGroupBox,
    QLabel, QSpinBox, QDoubleSpinBox, QCheckBox, QPushButton,
    QPlainTextEdit, QHBoxLayout, QLineEdit, QScrollArea
)
from PyQt5.QtGui import QFont
from PyQt5.QtCore import Qt
from fpdf import FPDF
from google import genai
from google.genai import types

class HypertensionApp(QWidget):
    def __init__(self):
        super().__init__()
        # Tamanho 16:9 por padrão e responsivo
        self.setWindowTitle("💓 Avaliação de Risco de Hipertensão")
        self.resize(960, 540)
        self.setMinimumSize(640, 360)
        self.setStyleSheet("""
            QWidget { background: #FAFAFA; }
            QGroupBox { 
                border: 1px solid #CCCCCC; 
                border-radius: 5px; 
                margin-top: 10px;
            }
            QGroupBox::title { 
                subcontrol-origin: margin; 
                subcontrol-position: top left; 
                padding: 0 5px; 
                font-weight: bold;
            }
            QLabel, QSpinBox, QDoubleSpinBox, QLineEdit, QPlainTextEdit {
                font-size: 14px;
            }
            QPushButton {
                padding: 8px 16px; 
                font-size: 14px;
                border-radius: 5px;
            }
            QPushButton#avaliar { background-color: #4CAF50; color: white; }
            QPushButton#pdf     { background-color: #2196F3; color: white; }
        """)

        # Widget de conteúdo para scroll
        content = QWidget()
        content_layout = QVBoxLayout(content)
        content_layout.setContentsMargins(20,20,20,20)
        content_layout.setSpacing(15)

        # --- Autoavaliação ---
        auto_gbox = QGroupBox("📝 Autoavaliação")
        auto_form = QFormLayout()
        self.idade = QSpinBox(); self.idade.setRange(0, 120); self.idade.setSuffix(" anos")
        auto_form.addRow("idade_anos:", self.idade)
        self.sexo_m = QCheckBox("Masculino?"); auto_form.addRow("sexo_masculino:", self.sexo_m)
        self.hist_fam = QCheckBox(); auto_form.addRow("historico_familiar_hipertensao:", self.hist_fam)
        self.altura = QDoubleSpinBox(); self.altura.setRange(0,300); self.altura.setSuffix(" cm")
        auto_form.addRow("altura_cm:", self.altura)
        self.peso = QDoubleSpinBox(); self.peso.setRange(0,500); self.peso.setDecimals(1); self.peso.setSuffix(" kg")
        auto_form.addRow("peso_kg:", self.peso)
        self.imc = QLineEdit(); self.imc.setReadOnly(True); auto_form.addRow("imc (calculado):", self.imc)
        self.altura.valueChanged.connect(self.calcular_imc)
        self.peso.valueChanged.connect(self.calcular_imc)
        self.frutas = QSpinBox(); self.frutas.setRange(0, 20); auto_form.addRow("porcoes_frutas_vegetais_dia:", self.frutas)
        self.exercicio = QSpinBox(); self.exercicio.setRange(0,10000); self.exercicio.setSuffix(" min")
        auto_form.addRow("minutos_exercicio_semana:", self.exercicio)
        self.fuma = QCheckBox(); auto_form.addRow("fuma_atualmente:", self.fuma)
        self.alcool = QSpinBox(); self.alcool.setRange(0,100); self.alcool.setSuffix(" doses")
        auto_form.addRow("bebidas_alcoolicas_semana:", self.alcool)
        self.estresse = QSpinBox(); self.estresse.setRange(0,10); auto_form.addRow("nivel_estresse_0_10:", self.estresse)
        self.sono = QCheckBox(); auto_form.addRow("sono_qualidade_ruim:", self.sono)
        auto_gbox.setLayout(auto_form)
        content_layout.addWidget(auto_gbox)

        # --- Exames Médicos opcionais ---
        self.chk_exames = QCheckBox("Possui dados de exame médico?")
        self.chk_exames.stateChanged.connect(self.toggle_exames)
        content_layout.addWidget(self.chk_exames)

        self.exame_gbox = QGroupBox("🩺 Exames Médicos (opcional)")
        exame_form = QFormLayout()
        def make_spin(maxv, suffix=""):
            sb = QDoubleSpinBox(); sb.setRange(0, maxv); sb.setDecimals(1); sb.setSuffix(suffix)
            sb.setSpecialValueText("nulo"); return sb
        self.ldl    = make_spin(500, " mg/dL"); exame_form.addRow("colesterol_ldl_mg_dL:", self.ldl)
        self.hdl    = make_spin(200, " mg/dL"); exame_form.addRow("colesterol_hdl_mg_dL:", self.hdl)
        self.trig   = make_spin(1000, " mg/dL"); exame_form.addRow("triglicerideos_mg_dL:", self.trig)
        self.glic   = make_spin(500, " mg/dL"); exame_form.addRow("glicemia_jejum_mg_dL:", self.glic)
        self.hba1c  = make_spin(20, " %");     exame_form.addRow("hba1c_percent:", self.hba1c)
        self.creat  = make_spin(10, " mg/dL"); exame_form.addRow("creatinina_mg_dL:", self.creat)
        self.protein= QCheckBox();          exame_form.addRow("proteinuria_positiva:", self.protein)
        self.apneia = QCheckBox();          exame_form.addRow("diagnostico_apneia_sono:", self.apneia)
        self.cortisol = make_spin(100, " µg/dL"); exame_form.addRow("cortisol_serico_ug_dL:", self.cortisol)
        self.mutacao = QCheckBox();             exame_form.addRow("mutacao_genetica_hipertensao:", self.mutacao)
        self.bpm     = make_spin(200, " bpm");   exame_form.addRow("bpm_repouso:", self.bpm)
        self.pm25    = make_spin(500, " µg/m³"); exame_form.addRow("indice_pm25:", self.pm25)
        self.exame_gbox.setLayout(exame_form)
        content_layout.addWidget(self.exame_gbox)

        # --- Botões ---
        btns = QHBoxLayout()
        self.btn_avaliar = QPushButton("Avaliar"); self.btn_avaliar.setObjectName("avaliar")
        self.btn_avaliar.clicked.connect(self.enviar_para_ia)
        btns.addWidget(self.btn_avaliar)
        self.btn_pdf = QPushButton("Gerar PDF"); self.btn_pdf.setObjectName("pdf")
        self.btn_pdf.clicked.connect(self.gerar_pdf)
        self.btn_pdf.setEnabled(False)
        btns.addWidget(self.btn_pdf)
        content_layout.addLayout(btns)

        # --- Resultado da IA ---
        lbl = QLabel("🖥️ Resultado da IA:"); lbl.setFont(QFont("",12,QFont.Bold))
        content_layout.addWidget(lbl)
        self.result = QPlainTextEdit(); self.result.setReadOnly(True)
        self.result.setStyleSheet("background: #EFEFEF;")
        self.result.setMinimumHeight(200)
        content_layout.addWidget(self.result)

        # Scroll area
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setWidget(content)

        # Layout principal
        main = QVBoxLayout(self)
        main.addWidget(scroll)

        # Inicializa API Gemini
        API_KEY = "AIzaSyAmraGN6apiXmyQTcgKaj-BaM_Zzro6IHk"  # substitua pela sua chave
        try:
            self.gemini = genai.Client(api_key=API_KEY,
                                      http_options=types.HttpOptions(api_version="v1alpha"))
            self.chat   = self.gemini.chats.create(model="gemini-2.0-flash")
        except Exception as e:
            print("Erro ao inicializar Gemini:", e)
            self.chat = None

        # Oculta exames por padrão
        self.toggle_exames(0)
        self.last_payload = None

    def calcular_imc(self):
        h = self.altura.value() / 100
        if h > 0:
            imc = self.peso.value() / (h * h)
            self.imc.setText(f"{imc:.1f}")
        else:
            self.imc.clear()

    def toggle_exames(self, estado):
        self.exame_gbox.setVisible(estado == Qt.Checked)

    def enviar_para_ia(self):
        # Monta dados de autoavaliação
        auto = {
            "idade_anos": self.idade.value(),
            "sexo_masculino": self.sexo_m.isChecked(),
            "historico_familiar_hipertensao": self.hist_fam.isChecked(),
            "altura_cm": self.altura.value(),
            "peso_kg": self.peso.value(),
            "imc": float(self.imc.text()) if self.imc.text() else None,
            "porcoes_frutas_vegetais_dia": self.frutas.value(),
            "minutos_exercicio_semana": self.exercicio.value(),
            "fuma_atualmente": self.fuma.isChecked(),
            "bebidas_alcoolicas_semana": self.alcool.value(),
            "nivel_estresse_0_10": self.estresse.value(),
            "sono_qualidade_ruim": self.sono.isChecked()
        }
        # Monta dados de exames (ou null)
        exames = None
        if self.chk_exames.isChecked():
            exames = {
                "colesterol_ldl_mg_dL":     None if self.ldl.value()==0 else self.ldl.value(),
                "colesterol_hdl_mg_dL":     None if self.hdl.value()==0 else self.hdl.value(),
                "triglicerideos_mg_dL":     None if self.trig.value()==0 else self.trig.value(),
                "glicemia_jejum_mg_dL":     None if self.glic.value()==0 else self.glic.value(),
                "hba1c_percent":            None if self.hba1c.value()==0 else self.hba1c.value(),
                "creatinina_mg_dL":         None if self.creat.value()==0 else self.creat.value(),
                "proteinuria_positiva":     self.protein.isChecked(),
                "diagnostico_apneia_sono":  self.apneia.isChecked(),
                "cortisol_serico_ug_dL":    None if self.cortisol.value()==0 else self.cortisol.value(),
                "mutacao_genetica_hipertensao": self.mutacao.isChecked(),
                "bpm_repouso":              None if self.bpm.value()==0 else self.bpm.value(),
                "indice_pm25":              None if self.pm25.value()==0 else self.pm25.value()
            }
        # Payload final
        payload = {"autoavaliacao": auto, "exames": exames}
        self.last_payload = payload

        # Monta prompt
        prompt = (
            "Analise este JSON e forneça diagnóstico completo de hipertensão em português, "
            "explicando riscos, probabilidades, recomendações e cuidados:\n\n"
            f"```json\n{json.dumps(payload, ensure_ascii=False, indent=2)}\n```"
        )
        if not self.chat:
            self.result.setPlainText("Erro: IA indisponível.")
            return
        try:
            resp = self.chat.send_message(prompt)
            texto = resp.text
        except Exception as e:
            texto = f"Erro ao chamar IA: {e}"
        self.result.setPlainText(texto)
        self.btn_pdf.setEnabled(True)

    def gerar_pdf(self):
        # Cria PDF com payload e feedback
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Arial", size=12)
        # Dados enviados
        pdf.multi_cell(0, 8, "Dados enviados:")
        pdf.multi_cell(0, 6, json.dumps(self.last_payload, ensure_ascii=False, indent=2))
        pdf.ln(4)
        # Feedback da IA
        pdf.multi_cell(0, 8, "Feedback da IA:")
        pdf.multi_cell(0, 6, self.result.toPlainText())
        # Salva
        pdf.output("relatorio_hipertensao.pdf")
        print("PDF salvo como relatorio_hipertensao.pdf")
        self.btn_pdf.setEnabled(False)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    janela = HypertensionApp()
    janela.show()
    sys.exit(app.exec_())