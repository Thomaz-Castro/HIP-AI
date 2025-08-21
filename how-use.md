# 🏥 Sistema de Gestão de Hipertensão

## 📋 Pré-requisitos

- Python 3.7 ou superior
- Windows 10/11
- Chave API do Google Gemini

## 🚀 Instalação

### 1. Preparar o ambiente

```bash
# Baixe e instale Python do site oficial: https://python.org
# Certifique-se de marcar "Add Python to PATH" durante a instalação
```

### 2. Criar diretório do projeto

```bash
# Crie uma pasta para o projeto
mkdir sistema_hipertensao
cd sistema_hipertensao
```

### 3. Salvar os arquivos

Salve os seguintes arquivos na pasta do projeto:
- `main.py` (código principal)
- `requirements.txt` (dependências)

### 4. Instalar dependências

```bash
# Abra o Command Prompt ou PowerShell na pasta do projeto
pip install -r requirements.txt
```

### 5. Configurar API do Gemini

1. Acesse: https://ai.google.dev/
2. Crie uma conta/faça login
3. Gere uma chave API gratuita
4. No arquivo `main.py`, linha 265, substitua `"AIzaSyAmraGN6apiXmyQTcgKaj-BaM_Zzro6IHk"` pela sua chave

### 6. Executar o sistema

```bash
python main.py
```

## 👥 Usuários Padrão

### Administrador
- **Username:** admin
- **Senha:** admin123
- **Permissões:** Acesso total, criar médicos e pacientes

### Primeiros passos como Admin:
1. Faça login como admin
2. Vá na aba "👥 Usuários"
3. Crie médicos e pacientes
4. Faça logout e teste os novos usuários

## 🔧 Funcionalidades

### 🔐 Sistema de Login
- **3 tipos de usuário:** Admin, Médico, Paciente
- **Autenticação segura** com hash SHA-256
- **Controle de acesso** baseado em perfis

### 👨‍⚕️ Para Médicos
- ✅ Realizar avaliações de pacientes
- ✅ Selecionar paciente da lista
- ✅ Adicionar observações médicas
- ✅ Salvar avaliações no banco
- ✅ Gerar relatórios em PDF
- ✅ Ver histórico de todas as avaliações

### 👤 Para Pacientes
- ✅ Realizar autoavaliação
- ✅ Ver histórico pessoal
- ✅ Gerar PDF de suas avaliações
- ✅ Visualizar resultados detalhados

### 👑 Para Administradores
- ✅ Gerenciar médicos e pacientes
- ✅ Criar novos usuários
- ✅ Visualizar todas as avaliações
- ✅ Controle total do sistema

### 🤖 Integração com IA
- **Análise inteligente** usando Google Gemini
- **Avaliação de risco** personalizada
- **Recomendações específicas** para cada caso
- **Linguagem acessível** ao paciente

### 📊 Sistema de Relatórios
- **Histórico completo** de avaliações
- **Relatórios em PDF** profissionais
- **Dados estruturados** para análise
- **Observações médicas** incluídas

## 🗄️ Banco de Dados

O sistema usa SQLite com as seguintes tabelas:
- `usuarios` - Dados de login e perfil
- `pacientes_dados` - Informações clínicas extras
- `avaliacoes` - Histórico de avaliações e resultados

**Backup automático:** O arquivo `hypertension_system.db` é criado automaticamente.

## 🔍 Campos de Avaliação

### Autoavaliação
- Dados demográficos (idade, sexo)
- Medidas físicas (altura, peso, IMC)
- Estilo de vida (exercícios, alimentação, fumo)
- Fatores de risco (histórico familiar, estresse)

### Exames Médicos (Opcional)
- Perfil lipídico (LDL, HDL, triglicerídeos)
- Glicemia e HbA1c
- Função renal (creatinina, proteinúria)
- Outros marcadores (cortisol, BPM, PM2.5)

## 🎨 Interface Moderna

- **Design responsivo** adaptável
- **Cores profissionais** e agradáveis
- **Ícones intuitivos** para navegação
- **Formulários organizados** por grupos
- **Feedback visual** em tempo real

## 🔒 Segurança

- **Senhas criptografadas** com hash SHA-256
- **Controle de sessão** por usuário
- **Validação de dados** em formulários
- **Backup automático** do banco de dados

## ❌ Resolução de Problemas

### Erro: "ModuleNotFoundError"
```bash
pip install --upgrade pip
pip install -r requirements.txt
```

### Erro: "API Key inválida"
1. Verifique se copiou a chave corretamente
2. Confirme se a API está ativa no Google AI Studio
3. Teste a chave em outro cliente

### Erro: "Banco de dados bloqueado"
1. Feche todas as instâncias do programa
2. Delete o arquivo `hypertension_system.db`
3. Execute novamente (será recriado)

### Interface não aparece
1. Confirme se PyQt5 está instalado
2. Execute: `python -m PyQt5.QtWidgets`
3. Reinstale PyQt5: `pip uninstall PyQt5 && pip install PyQt5`

### Erro de PDF
1. Confirme se fpdf2 está instalado
2. Verifique permissões de escrita na pasta
3. Execute como administrador se necessário

## 📱 Uso Detalhado

### Como Admin criar usuários:

1. **Login como admin** (admin/admin123)
2. **Ir para aba "👥 Usuários"**
3. **Clicar na sub-aba "➕ Novo Usuário"**
4. **Preencher dados:**
   - Para médicos: incluir CRM e especialidade
   - Para pacientes: incluir data de nascimento
5. **Clicar "✅ Criar Usuário"**

### Como Médico avaliar paciente:

1. **Login com credenciais de médico**
2. **Ir para aba "💓 Avaliação"**
3. **Selecionar paciente no dropdown**
4. **Preencher dados da avaliação**
5. **Marcar "Possui dados de exame" se aplicável**
6. **Clicar "🔍 Avaliar com IA"**
7. **Adicionar observações médicas**
8. **Clicar "💾 Salvar Avaliação"**
9. **Opcionalmente "📄 Gerar PDF"**

### Como Paciente fazer autoavaliação:

1. **Login com credenciais de paciente**
2. **Ir para aba "💓 Avaliação"**
3. **Preencher todos os dados solicitados**
4. **Incluir exames se disponíveis**
5. **Clicar "🔍 Avaliar com IA"**
6. **Revisar resultado**
7. **Gerar PDF para levar ao médico**

### Visualizar histórico:

1. **Ir para aba "📊 Relatórios"**
2. **Pacientes:** veem apenas suas avaliações
3. **Médicos/Admin:** veem todas as avaliações
4. **Clicar em avaliação para ver detalhes**

## 🔄 Fluxo de Trabalho Recomendado

### 1. Configuração Inicial
- Admin cria médicos
- Admin cria pacientes
- Distribui credenciais

### 2. Processo Clínico
- Paciente faz autoavaliação em casa
- Médico revisa e complementa com exames
- Sistema gera análise de IA
- Médico adiciona observações
- Relatório é salvo e pode ser impresso

### 3. Acompanhamento
- Paciente acessa histórico
- Médico monitora evolução
- Admin supervisiona sistema

## 🔧 Personalização

### Modificar campos de avaliação:
Edite a classe `HypertensionEvaluationWidget` no arquivo `main.py`

### Alterar prompt da IA:
Modifique a variável `prompt` na função `enviar_para_ia()`

### Customizar relatório PDF:
Edite a função `gerar_pdf()` na classe `HypertensionEvaluationWidget`

### Adicionar novos tipos de usuário:
1. Modificar tabela `usuarios` no banco
2. Atualizar classe `DatabaseManager`
3. Criar nova interface se necessário

## 🆘 Suporte

### Logs de erro:
- Erros aparecem no console
- Para debug detalhado, adicione prints no código

### Backup manual:
```bash
copy hypertension_system.db backup_YYYYMMDD.db
```

### Reset completo:
```bash
del hypertension_system.db
python main.py
```

## 🚀 Próximas Funcionalidades

### Planejadas:
- [ ] Gráficos de evolução do paciente
- [ ] Notificações por email
- [ ] Export para Excel
- [ ] Dashboard estatístico
- [ ] Integração com equipamentos
- [ ] Modo escuro na interface
- [ ] Múltiplos idiomas

### Melhorias técnicas:
- [ ] Cache das consultas IA
- [ ] Backup automático na nuvem
- [ ] Logs de auditoria
- [ ] Criptografia do banco
- [ ] API REST para integrações

---

## 📞 Contato

**Desenvolvido para avaliação médica de hipertensão**

⚠️ **AVISO:** Este sistema é uma ferramenta de apoio. Sempre consulte profissionais de saúde qualificados para diagnósticos e tratamentos definitivos.

---

*Sistema desenvolvido com Python, PyQt5 e Google Gemini AI*