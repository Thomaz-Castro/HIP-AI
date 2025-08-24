# 🏥 Sistema Médico - Guia de Instalação

## 📋 Pré-requisitos
- Python 3.8 ou superior
- Conta no MongoDB Atlas (gratuita)

## 🚀 Instalação Passo a Passo

### 1. Preparar o Ambiente Python

```bash
# Criar ambiente virtual (recomendado)
python -m venv medical_system
cd medical_system
Scripts\activate  # Windows
# source bin/activate  # Linux/Mac

# Instalar dependências
pip install -r requirements.txt
```

### 2. Configurar MongoDB Atlas

#### 2.1 Criar Conta no MongoDB Atlas
1. Acesse: https://www.mongodb.com/cloud/atlas
2. Clique em "Try Free" 
3. Crie sua conta gratuita

#### 2.2 Criar Cluster
1. No dashboard, clique "Create Cluster"
2. Escolha o plano FREE (M0)
3. Selecione uma região próxima
4. Clique "Create Cluster"

#### 2.3 Configurar Acesso
1. **Database Access**: 
   - Vá em "Database Access" no menu lateral
   - Clique "Add New Database User"
   - Escolha username/password
   - Selecione "Read and write to any database"
   - Clique "Add User"

2. **Network Access**:
   - Vá em "Network Access" 
   - Clique "Add IP Address"
   - Clique "Allow Access from Anywhere" (0.0.0.0/0)
   - Clique "Confirm"

#### 2.4 Obter String de Conexão
1. Vá em "Clusters"
2. Clique no botão "Connect" do seu cluster
3. Escolha "Connect your application"
4. Selecione "Python" e versão "3.6 or later"
5. Copie a connection string (algo como):
   ```
   mongodb+srv://username:<password>@cluster0.xxxxx.mongodb.net/?retryWrites=true&w=majority
   ```

### 3. Configurar o Sistema

#### 3.1 Arquivo de Configuração
1. Copie o arquivo `.env.example` para `.env`:
   ```bash
   copy .env.example .env  # Windows
   # cp .env.example .env  # Linux/Mac
   ```

2. Edite o arquivo `.env` com seus dados:
   ```env
   MONGODB_URI=mongodb+srv://seuusuario:suasenha@cluster0.xxxxx.mongodb.net/medical_system?retryWrites=true&w=majority
   ```

   **⚠️ IMPORTANTE**: 
   - Substitua `seuusuario` pelo username criado
   - Substitua `suasenha` pela senha criada
   - Substitua `cluster0.xxxxx` pelo seu cluster real

### 4. Executar o Sistema

```bash
python medical_system.py
```

## 👥 Usuários Padrão

O sistema cria automaticamente um administrador:
- **Email**: admin@sistema.com  
- **Senha**: admin123

## 🎯 Funcionalidades por Tipo de Usuário

### 👨‍💼 Administrador
- ✅ Criar, editar e excluir médicos
- ✅ Criar, editar e excluir pacientes  
- ✅ Visualizar todos os relatórios
- ❌ NÃO pode gerar relatórios

### 👨‍⚕️ Médicos
- ✅ Realizar avaliações de hipertensão
- ✅ Gerar relatórios para pacientes
- ✅ Salvar relatórios no banco de dados
- ✅ Visualizar relatórios criados por ele
- ✅ Exportar relatórios em PDF

### 👤 Pacientes  
- ✅ Visualizar seus próprios relatórios
- ✅ Editar dados do perfil
- ✅ Alterar senha
- ❌ NÃO pode criar relatórios

## 🔧 Estrutura do Banco de Dados

### Collection: users
```javascript
{
  "_id": ObjectId,
  "name": String,
  "email": String, // único
  "password": String, // hash SHA256
  "user_type": String, // "admin", "doctor", "patient"
  "created_at": DateTime,
  
  // Campos específicos para médicos
  "crm": String,
  "specialty": String,
  
  // Campos específicos para pacientes  
  "birth_date": Date,
  "phone": String
}
```

### Collection: reports
```javascript
{
  "_id": ObjectId,
  "doctor_id": ObjectId, // referência para users
  "patient_id": ObjectId, // referência para users
  "report_data": {
    "input_data": Object, // dados da avaliação
    "ai_result": String, // resultado da IA
    "timestamp": String
  },
  "created_at": DateTime
}
```

## 🚨 Solução de Problemas

### Erro de Conexão MongoDB
```
pymongo.errors.ServerSelectionTimeoutError
```
**Soluções**:
1. Verificar se a string de conexão está correta
2. Confirmar que o IP foi liberado no Network Access
3. Testar conectividade: `ping cluster0.xxxxx.mongodb.net`

### Erro de Autenticação
```
pymongo.errors.OperationFailure: Authentication failed
```
**Soluções**:
1. Verificar username/password na string de conexão
2. Confirmar que o usuário foi criado corretamente
3. Verificar se a senha não contém caracteres especiais (@ # %)

### Erro de Módulo PyQt5
```
ModuleNotFoundError: No module named 'PyQt5'
```
**Soluções**:
1. Reinstalar: `pip uninstall PyQt5 && pip install PyQt5==5.15.10`
2. No Ubuntu: `sudo apt install python3-pyqt5`
3. Verificar ambiente virtual ativo

### Interface não Responsiva
**Soluções**:
1. Fechar e reabrir o sistema
2. Verificar conexão com internet
3. Limpar cache do navegador (se houver)

## 📱 Como Usar

### Para Administradores:
1. Faça login com admin@sistema.com / admin123
2. Vá na aba "Gerenciar Usuários"
3. Crie médicos e pacientes conforme necessário
4. Monitore relatórios na aba "Todos os Relatórios"

### Para Médicos:
1. Receba suas credenciais do administrador
2. Na aba "Nova Avaliação":
   - Selecione o paciente
   - Preencha os dados da avaliação
   - Clique "Avaliar Hipertensão" 
   - Clique "Salvar Relatório"
3. Visualize histórico na aba "Meus Relatórios"

### Para Pacientes:
1. Receba suas credenciais do administrador
2. Atualize seu perfil na aba "Meu Perfil"
3. Visualize seus relatórios na aba "Meus Relatórios"

## 🔐 Segurança

- Senhas são criptografadas com SHA256
- Cada tipo de usuário tem permissões específicas
- Conexão segura com MongoDB Atlas via TLS
- Validação de dados nos formulários

## 📞 Suporte

Para dúvidas ou problemas:
1. Verificar este guia de instalação
2. Consultar logs de erro no terminal
3. Verificar configurações do MongoDB Atlas

## 🔄 Atualizações Futuras

Funcionalidades planejadas:
- [ ] Integração real com Google Gemini AI
- [ ] Dashboard com estatísticas
- [ ] Notificações por email
- [ ] Backup automático de dados
- [ ] Modo escuro na interface
- [ ] Suporte a múltiplos idiomas
- [ ] API REST para integração externa

---

✅ **Sistema testado no Windows 10/11 com Python 3.9+**