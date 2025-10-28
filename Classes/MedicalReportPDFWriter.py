from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.pdfgen import canvas
from reportlab.lib import colors
from datetime import datetime
from PyQt5.QtWidgets import QFileDialog
import os


class MedicalReportPDFWriter:
    """
    Gera um laudo médico profissional em PDF a partir de dados de avaliação e
    resultado de uma análise de IA. O layout é inspirado em uma ficha clínica,
    separando os dados do paciente (Anamnese) do parecer da IA.
    """

    def __init__(self):
        self.filename = None
        self.c = None
        self.width, self.height = A4
        self.margin = 15 * mm

    def get_save_filename(self, patient_name=None):
        """
        Abre diálogo para selecionar local e nome do arquivo
        Retorna o caminho completo ou None se cancelado
        """
        hoje = datetime.now().strftime("%Y%m%d_%H%M%S")
        if patient_name:
            safe_name = "".join(c for c in patient_name if c.isalnum() or c in (' ', '-', '_'))
            safe_name = safe_name.replace(' ', '_')
            suggested_name = f"Relatorio_Hipertensao_{safe_name}_{hoje}.pdf"
        else:
            suggested_name = f"Relatorio_Hipertensao_{hoje}.pdf"
        
        default_dir = os.path.join(os.path.expanduser("~"), "Documents")
        if not os.path.exists(default_dir):
            default_dir = os.path.expanduser("~")
        
        suggested_path = os.path.join(default_dir, suggested_name)
        
        filename, _ = QFileDialog.getSaveFileName(
            None,
            "Salvar Relatório PDF",
            suggested_path,
            "Arquivos PDF (*.pdf);;Todos os arquivos (*.*)"
        )
        
        return filename if filename else None

    def draw_title(self):
        """Desenha o título principal"""
        y_pos = self.height - self.margin - 10 * mm
        self.c.setFont("Helvetica-Bold", 14)
        title = "RELATÓRIO DE AVALIAÇÃO DE RISCO DE HIPERTENSÃO"
        title_width = self.c.stringWidth(title, "Helvetica-Bold", 14)
        self.c.drawString((self.width - title_width) / 2, y_pos, title)

        data_hoje = datetime.now().strftime("%d/%m/%Y")
        self.c.setFont("Helvetica", 9)
        data_text = f"Data: {data_hoje}"
        data_width = self.c.stringWidth(data_text, "Helvetica", 9)
        self.c.drawString((self.width - data_width) / 2, y_pos - 5*mm, data_text)

        return y_pos - 10*mm

    def draw_section_header(self, title, y_pos):
        """Desenha cabeçalho de seção com fundo preto e texto branco"""
        x_start = self.margin
        width = self.width - 2 * self.margin
        header_height = 5.5 * mm
        rect_y = y_pos - header_height

        self.c.setFillColor(colors.black)
        self.c.rect(x_start, rect_y, width, header_height, fill=1)

        self.c.setFillColor(colors.white)
        self.c.setFont("Helvetica-Bold", 9)
        font_size = 9

        text_y = rect_y + (header_height - font_size) / 2
        self.c.drawString(x_start + 2*mm, text_y, title.upper())

        self.c.setFillColor(colors.black)

        return rect_y

    def draw_field_row(self, y_pos, fields, widths=None, row_height=6*mm):
        """Desenha uma linha de campos alinhados com bordas finas"""
        x_start = self.margin
        total_width = self.width - 2 * self.margin
        num_fields = len(fields)
        widths = widths or [1.0 / num_fields] * num_fields
        field_widths = [w * total_width for w in widths]

        self.c.setStrokeColor(colors.black)
        self.c.setLineWidth(0.4)

        current_x = x_start
        for i, field in enumerate(fields):
            field_width = field_widths[i]
            self.c.rect(current_x, y_pos - row_height, field_width, row_height)

            label = field.get('label', '')
            value = field.get('value', '')

            self.c.setFont("Helvetica-Bold", 7.5)
            self.c.drawString(current_x + 2*mm, y_pos - row_height + 2.5*mm, label)
            if value:
                self.c.setFont("Helvetica", 7.5)
                self.c.drawRightString(
                    current_x + field_width - 2*mm, y_pos - row_height + 2.5*mm, str(value))

            current_x += field_width

        return y_pos - row_height

    def draw_multiline_text(self, y_pos, text, line_height=4*mm):
        """Desenha texto multilinha dentro da área"""
        x_start = self.margin + 3
        max_width = self.width - 2 * self.margin - 6
        self.c.setFont("Helvetica", 6)

        for line in text.split('\n'):
            if not line.strip():
                y_pos -= line_height / 2
                continue
            words = line.split()
            current_line = ""
            for word in words:
                test_line = (current_line + " " + word).strip()
                if self.c.stringWidth(test_line, "Helvetica", 6) <= max_width:
                    current_line = test_line
                else:
                    self.c.drawString(x_start, y_pos, current_line)
                    y_pos -= line_height
                    current_line = word
            if current_line:
                self.c.drawString(x_start, y_pos, current_line)
                y_pos -= line_height
        return y_pos

    def draw_legal_disclaimer(self, y_pos):
        """Desenha o aviso legal destacado com fundo amarelo e borda vermelha"""
        x_start = self.margin
        width = self.width - 2 * self.margin
        padding = 3 * mm
        
        # Texto do aviso
        disclaimer_lines = [
            "IMPORTANTE: Esta avaliação é apenas informativa.",
            "Consulte sempre um médico para diagnóstico e tratamento adequados."
        ]
        
        # Calcula altura necessária
        line_height = 4.5 * mm
        box_height = len(disclaimer_lines) * line_height + 2 * padding
        
        # Desenha fundo amarelo claro
        self.c.setFillColor(colors.Color(1, 1, 0.85))  # Amarelo claro
        self.c.rect(x_start, y_pos - box_height, width, box_height, fill=1, stroke=0)
        
        # Desenha borda vermelha grossa
        self.c.setStrokeColor(colors.red)
        self.c.setLineWidth(1.5)
        self.c.rect(x_start, y_pos - box_height, width, box_height, fill=0, stroke=1)
        
        # Desenha o texto em vermelho e negrito
        self.c.setFillColor(colors.red)
        self.c.setFont("Helvetica-Bold", 9)
        
        text_y = y_pos - padding - line_height + 1*mm
        for line in disclaimer_lines:
            # Centraliza o texto
            text_width = self.c.stringWidth(line, "Helvetica-Bold", 9)
            text_x = x_start + (width - text_width) / 2
            self.c.drawString(text_x, text_y, line)
            text_y -= line_height
        
        # Reseta cores
        self.c.setFillColor(colors.black)
        self.c.setStrokeColor(colors.black)
        
        return y_pos - box_height

    def generate_pdf(self, data, user_info, patient_name=None):
        """
        Gera o PDF com os dados fornecidos
        Abre diálogo para o usuário escolher onde salvar
        Retorna o caminho do arquivo salvo ou None se cancelado
        """
        self.filename = self.get_save_filename(patient_name)
        
        if not self.filename:
            return None
        
        if not self.filename.lower().endswith('.pdf'):
            self.filename += '.pdf'
        
        self.c = canvas.Canvas(self.filename, pagesize=A4)
        
        y_pos = self.draw_title()

        # INFORMAÇÕES GERAIS
        y_pos -= 4 * mm
        y_pos = self.draw_section_header("INFORMAÇÕES DO PROFISSIONAL E PACIENTE", y_pos)
        y_pos = self.draw_field_row(y_pos, [
            {'label': 'Médico', 'value': user_info.get('name', '')},
            {'label': 'Paciente', 'value': patient_name or 'N/A'}
        ], widths=[0.5, 0.5])

        # AVALIAÇÃO ÁGIL
        y_pos -= 2 * mm
        y_pos = self.draw_section_header("AVALIAÇÃO ÁGIL - DADOS GERAIS", y_pos)
        a = data.get('avaliacaoagil', {})

        y_pos = self.draw_field_row(y_pos, [
            {'label': 'Idade', 'value': f"{a.get('idade_anos', '')} anos"},
            {'label': 'Sexo', 'value': 'Masculino' if a.get('sexo_masculino') else 'Feminino'},
            {'label': 'Altura', 'value': f"{a.get('altura_cm', '')} cm"},
            {'label': 'Peso', 'value': f"{a.get('peso_kg', '')} kg"}
        ])

        y_pos = self.draw_field_row(y_pos, [
            {'label': 'IMC', 'value': a.get('imc', '')},
            {'label': 'Histórico de Hipertensão Familiar', 
             'value': 'Sim' if a.get('historico_familiar_hipertensao') else 'Não'},
            {'label': 'Fumante', 'value': 'Sim' if a.get('fuma_atualmente') else 'Não'}
        ], widths=[0.25, 0.45, 0.3])

        y_pos = self.draw_field_row(y_pos, [
            {'label': 'Frutas/Veg', 'value': f"{a.get('porcoes_frutas_vegetais_dia', '')}/dia"},
            {'label': 'Exercício', 'value': f"{a.get('minutos_exercicio_semana', '')} min/sem"},
            {'label': 'Álcool', 'value': f"{a.get('bebidas_alcoolicas_semana', '')}/sem"}
        ], widths=[0.33, 0.37, 0.3])

        y_pos = self.draw_field_row(y_pos, [
            {'label': 'Estresse', 'value': f"{a.get('nivel_estresse_0_10', '')}/10"},
            {'label': 'Sono', 'value': 'Ruim' if a.get('sono_qualidade_ruim') else 'Bom'}
        ], widths=[0.5, 0.5])

        # EXAMES
        y_pos -= 2 * mm
        y_pos = self.draw_section_header("EXAMES LABORATORIAIS E CLÍNICOS", y_pos)
        e = data.get('exames', {})
        if e is None:
            e = {}

        y_pos = self.draw_field_row(y_pos, [
            {'label': 'LDL', 'value': f"{e.get('colesterol_ldl_mg_dL', '')} mg/dL"},
            {'label': 'HDL', 'value': f"{e.get('colesterol_hdl_mg_dL', '')} mg/dL"},
            {'label': 'Triglicerídeos', 'value': f"{e.get('triglicerideos_mg_dL', '')} mg/dL"}
        ], widths=[0.3, 0.3, 0.4])

        y_pos = self.draw_field_row(y_pos, [
            {'label': 'Glicemia', 'value': f"{e.get('glicemia_jejum_mg_dL', '')} mg/dL"},
            {'label': 'HbA1c', 'value': f"{e.get('hba1c_percent', '')}%"},
            {'label': 'Creatinina', 'value': f"{e.get('creatinina_mg_dL', '')} mg/dL"}
        ], widths=[0.35, 0.25, 0.4])

        y_pos = self.draw_field_row(y_pos, [
            {'label': 'Proteinúria', 'value': 'Positiva' if e.get('proteinuria_positiva') else 'Negativa'},
            {'label': 'Apneia', 'value': 'Sim' if e.get('diagnostico_apneia_sono') else 'Não'},
            {'label': 'Cortisol', 'value': f"{e.get('cortisol_serico_ug_dL', '')} µg/dL"}
        ], widths=[0.33, 0.27, 0.4])

        y_pos = self.draw_field_row(y_pos, [
            {'label': 'Mutação Genetica', 'value': 'Sim' if e.get('mutacao_genetica_hipertensao') else 'Não'},
            {'label': 'BPM', 'value': e.get('bpm_repouso', '')},
            {'label': 'PM2.5', 'value': e.get('indice_pm25', '')}
        ], widths=[0.4, 0.3, 0.3])

        # RESULTADO
        y_pos -= 2 * mm
        y_pos = self.draw_section_header("RESULTADO DA AVALIAÇÃO", y_pos)

        ai_result = data.get('ai_result', '')
        clean_text = ai_result.translate(str.maketrans('', '', '🏥📊🎯⚠️💡📝⏰'))
        
        # Separa o aviso legal do resto do texto
        disclaimer_marker = "IMPORTANTE:"
        if disclaimer_marker in clean_text:
            main_text = clean_text.split(disclaimer_marker)[0].strip()
        else:
            main_text = clean_text

        # Desenha o texto principal
        y_box_top = y_pos
        padding = 3 * mm

        y_text_start = y_box_top - padding
        final_y_after_text = self.draw_multiline_text(y_text_start, main_text, line_height=3*mm)

        y_box_bottom = final_y_after_text - padding
        box_height = y_box_top - y_box_bottom

        # Desenha a borda para a seção de resultado
        self.c.setStrokeColor(colors.black)
        self.c.setLineWidth(0.5)
        self.c.rect(self.margin, y_box_bottom, self.width - 2 * self.margin, box_height)

        # Desenha o aviso legal destacado
        y_pos = y_box_bottom - 3*mm
        y_pos = self.draw_legal_disclaimer(y_pos)

        self.c.save()
        print(f"PDF gerado com sucesso: {self.filename}")
        return self.filename


# --- EXEMPLO DE USO ---
if __name__ == '__main__':

    data = {
        'avaliacaoagil': {
            'idade_anos': 55, 'sexo_masculino': True, 'historico_familiar_hipertensao': True,
            'altura_cm': 175, 'peso_kg': 85, 'imc': 27.8, 'porcoes_frutas_vegetais_dia': 3,
            'minutos_exercicio_semana': 90, 'fuma_atualmente': False, 'bebidas_alcoolicas_semana': 4,
            'nivel_estresse_0_10': 7, 'sono_qualidade_ruim': True
        },
        'exames': {
            'colesterol_ldl_mg_dL': 145, 'colesterol_hdl_mg_dL': 42,
            'triglicerideos_mg_dL': 180, 'glicemia_jejum_mg_dL': 105,
            'hba1c_percent': 5.8, 'creatinina_mg_dL': 1.1,
            'proteinuria_positiva': False, 'diagnostico_apneia_sono': True,
            'cortisol_serico_ug_dL': 12, 'mutacao_genetica_hipertensao': False,
            'bpm_repouso': 75, 'indice_pm25': 35
        },
        'ai_result': """RELATÓRIO DE AVALIAÇÃO DE RISCO DE HIPERTENSÃO

PONTUAÇÃO DE RISCO: 55 pontos
NÍVEL DE RISCO: ALTO

FATORES DE RISCO IDENTIFICADOS:
1. Idade acima de 50 anos
2. Sexo masculino
3. Histórico familiar de hipertensão
4. Sobrepeso (IMC 27.8)
5. LDL elevado (145 mg/dL)
6. HDL baixo (42 mg/dL)
7. Glicemia alterada (105 mg/dL)
8. Triglicerídeos elevados (180 mg/dL)
9. Apneia do sono diagnosticada
10. Alto nível de estresse (7/10)
11. Qualidade de sono ruim
12. Sedentarismo relativo (90 min/semana)
13. Dieta pobre em frutas/vegetais (3 porções/dia)

RECOMENDAÇÕES:
- URGENTE: Consultar cardiologista para avaliação completa
- Aumentar exercícios para mínimo 150 min/semana
- Dieta com mínimo 5 porções frutas/vegetais/dia
- Reduzir consumo de álcool
- Tratamento para apneia do sono
- Técnicas de gerenciamento de estresse
- Monitoramento trimestral de pressão arterial

ORIENTAÇÕES GERAIS:
- Manter pressão arterial abaixo de 120/80 mmHg
- Praticar exercícios regulares (mínimo 150min/semana)
- Manter dieta rica em frutas, vegetais e pobre em sódio
- Controlar peso corporal (IMC < 25)
- Evitar tabagismo e consumo excessivo de álcool
- Gerenciar níveis de estresse
- Manter qualidade adequada do sono

Data da Avaliação: 09/10/2025 23:14

IMPORTANTE: Esta avaliação é apenas informativa. 
Consulte sempre um médico para diagnóstico e tratamento adequados."""
    }
    user_info = {'name': 'Dr. João Silva'}
    patient_name = 'Carlos Santos'
    
    from PyQt5.QtWidgets import QApplication
    import sys
    
    app = QApplication(sys.argv)
    relatorio = MedicalReportPDFWriter()
    filename = relatorio.generate_pdf(data, user_info, patient_name)
    
    if filename:
        print(f"PDF salvo em: {filename}")
    else:
        print("Geração de PDF cancelada pelo usuário")