# config.py - Arquivo de configuração do Sistema de Hipertensão

# =============================================================================
# CONFIGURAÇÕES DA API GEMINI
# =============================================================================

# Substitua pela sua chave API do Google Gemini
# Obtenha em: https://ai.google.dev/
GEMINI_API_KEY = "AIzaSyAmraGN6apiXmyQTcgKaj-BaM_Zzro6IHk"

# Modelo do Gemini a ser utilizado
GEMINI_MODEL = "gemini-2.0-flash"

# =============================================================================
# CONFIGURAÇÕES DO BANCO DE DADOS
# =============================================================================

# Nome do arquivo do banco de dados SQLite
DATABASE_PATH = "hypertension_system.db"

# =============================================================================
# CONFIGURAÇÕES DA INTERFACE
# =============================================================================

# Tema de cores da aplicação
COLORS = {
    'primary': '#667eea',
    'secondary': '#764ba2', 
    'success': '#4CAF50',
    'info': '#2196F3',
    'warning': '#FF9800',
    'danger': '#F44336',
    'light': '#FAFAFA',
    'dark': '#2c3e50',
    'background': '#f5f5f5'
}

# Configurações da janela principal
WINDOW_CONFIG = {
    'title': '🏥 Sistema de Gestão de Hipertensão',
    'width': 1200,
    'height': 800,
    'min_width': 800,
    'min_height': 600
}

# =============================================================================
# CONFIGURAÇÕES DOS RELATÓRIOS
# =============================================================================

# Configurações do PDF
PDF_CONFIG = {
    'font_family': 'Arial',
    'font_size': 12,
    'title_size': 16,
    'margin': 20,
    'encoding': 'latin-1'
}

# =============================================================================
# CONFIGURAÇÕES DE SEGURANÇA
# =============================================================================

# Algoritmo de hash para senhas (não alterar após dados em produção)
PASSWORD_HASH_ALGORITHM = 'sha256'

# Configurações de sessão
SESSION_CONFIG = {
    'timeout_minutes': 480,  # 8 horas
    'auto_logout': True
}

# =============================================================================
# CONFIGURAÇÕES DOS PROMPTS DA IA
# =============================================================================

# Prompt base para análise de hipertensão
HYPERTENSION_ANALYSIS_PROMPT = """
Você é um especialista em cardiologia e medicina preventiva. Analise os dados fornecidos sobre um paciente e forneça uma avaliação completa sobre o risco de hipertensão.

ESTRUTURE SUA RESPOSTA DA SEGUINTE FORMA:

🔍 ANÁLISE DE RISCO:
- Classifique o risco como: BAIXO, MODERADO, ALTO ou MUITO ALTO
- Justifique a classificação baseada nos dados

⚠️ FATORES DE RISCO IDENTIFICADOS:
- Liste os principais fatores de risco encontrados
- Explique como cada um impacta o risco cardiovascular

📋 RECOMENDAÇÕES ESPECÍFICAS:
- Mudanças no estilo de vida
- Monitoramento necessário
- Quando buscar acompanhamento médico

🎯 PLANO DE AÇÃO:
- Próximos passos recomendados
- Exames adicionais se necessários
- Cronograma de acompanhamento

⚕️ OBSERVAÇÕES IMPORTANTES:
- Limitações da análise
- Necessidade de avaliação médica presencial
- Sinais de alerta para procurar ajuda imediata

Seja detalhado mas use linguagem acessível. Foque em orientações práticas e baseadas em evidências científicas.

DADOS DO PACIENTE:
"""

# =============================================================================
# CONFIGURAÇÕES DE VALIDAÇÃO
# =============================================================================

# Limites para campos numéricos
FIELD_LIMITS = {
    'idade_max': 120,
    'peso_max': 500,
    'altura_max': 250,
    'pressao_sistolica_max': 300,
    'pressao_diastolica_max': 200,
    'colesterol_max': 1000,
    'glicemia_max': 600
}

# Validações de formato
VALIDATION_PATTERNS = {
    'email': r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$',
    'telefone': r'^\(?[0-9]{2}\)?[0-9]{4,5}-?[0-9]{4}$',
    'crm': r'^[0-9]{4,6}[A-Z]{2}$',
    'data': r'^[0-9]{2}/[0-9]{2}/[0-9]{4}$'
}

# =============================================================================
# CONFIGURAÇÕES DE LOGGING
# =============================================================================

# Configurações de log (para futuras implementações)
LOGGING_CONFIG = {
    'level': 'INFO',
    'format': '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    'file': 'system.log',
    'max_size': '10MB',
    'backup_count': 5
}

# =============================================================================
# TEXTOS E MENSAGENS
# =============================================================================

# Mensagens do sistema
MESSAGES = {
    'login_success': 'Login realizado com sucesso!',
    'login_error': 'Usuário ou senha incorretos.',
    'user_created': 'Usuário criado com sucesso!',
    'user_exists': 'Nome de usuário já existe.',
    'evaluation_saved': 'Avaliação salva com sucesso!',
    'pdf_generated': 'Relatório PDF gerado com sucesso!',
    'ai_error': 'Erro ao processar análise de IA. Tente novamente.',
    'database_error': 'Erro de banco de dados. Contate o administrador.',
    'permission_denied': 'Você não tem permissão para esta ação.',
    'session_expired': 'Sessão expirada. Faça login novamente.',
    'fields_required': 'Preencha todos os campos obrigatórios.',
    'invalid_format': 'Formato inválido para este campo.',
    'operation_cancelled': 'Operação cancelada pelo usuário.',
    'backup_success': 'Backup realizado com sucesso!',
    'restore_success': 'Sistema restaurado com sucesso!'
}

# Títulos das seções
SECTION_TITLES = {
    'autoavaliacao': '📝 Autoavaliação',
    'exames': '🩺 Exames Médicos',
    'resultado_ia': '🤖 Resultado da IA',
    'observacoes': '📋 Observações Médicas',
    'historico': '📊 Histórico de Avaliações',
    'usuarios': '👥 Gerenciamento de Usuários',
    'relatorios': '📈 Relatórios e Estatísticas'
}

# =============================================================================
# CONFIGURAÇÕES AVANÇADAS
# =============================================================================

# Configurações de performance
PERFORMANCE_CONFIG = {
    'cache_size': 100,
    'max_concurrent_requests': 5,
    'request_timeout': 30,
    'retry_attempts': 3
}

# Configurações de backup automático
BACKUP_CONFIG = {
    'enabled': True,
    'interval_hours': 24,
    'max_backups': 7,
    'backup_path': './backups/'
}

# Funcionalidades experimentais (podem ser instáveis)
EXPERIMENTAL_FEATURES = {
    'real_time_validation': False,
    'auto_save_drafts': False,
    'advanced_charts': False,
    'notification_system': False,
    'multi_language': False
}

# =============================================================================
# INFORMAÇÕES DO SISTEMA
# =============================================================================

SYSTEM_INFO = {
    'name': 'Sistema de Gestão de Hipertensão',
    'version': '1.0.0',
    'author': 'Assistente IA Claude',
    'description': 'Sistema completo para avaliação e gerenciamento de risco de hipertensão',
    'license': 'MIT',
    'python_required': '3.7+',
    'last_updated': '2024'
}