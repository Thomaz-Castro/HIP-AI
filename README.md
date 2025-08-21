# 🏥 Sistema de Gestão de Hipertensão

## 📖 Sobre o Sistema

Sistema completo para avaliação e gerenciamento de risco de hipertensão, desenvolvido em Python com PyQt5. Integra inteligência artificial (Google Gemini) para análise personalizada de fatores de risco cardiovascular.

### 🎯 Funcionalidades Principais

- **Sistema de Login Multi-perfil**: Admin, Médicos e Pacientes
- **Avaliação de Risco Inteligente**: Análise por IA baseada em dados clínicos
- **Gestão Completa de Usuários**: Criação e gerenciamento de médicos e pacientes
- **Relatórios Profissionais**: Geração de PDFs com resultados detalhados
- **Histórico Completo**: Acompanhamento da evolução dos pacientes
- **Interface Moderna**: Design intuitivo e responsivo

## 🚀 Instalação Rápida

### Opção 1: Instalação Automática (Recomendada)

```bash
# 1. Baixe todos os arquivos para uma pasta
# 2. Execute o script de configuração
python setup.py
```

### Opção 2: Instalação Manual

```bash
# 1. Instalar dependências
pip install -r requirements.txt

# 2. Configurar chave API do Gemini
# Edite main.py, linha 265, com sua chave

# 3. Executar sistema
python main.py
```

## 📋 Arquivos do Sistema

```
sistema_hipertensao/
├── main.py                 # Código principal
├── config.py              # Configurações
├── setup.py               # Script de instalação
├── requirements.txt       # Dependências
├── README.md             # Este arquivo
└── hypertension_system.db # Banco de dados (criado automaticamente)
```

## 🔑 Usuários Padrão

| Tipo | Username | Senha | Descrição |
|------|----------|-------|-----------|
| 👑 Admin | `admin` | `admin123` | Controle total do sistema |
| 👨‍⚕️ Médico | `dr_silva` | `medico123` | Usuário de exemplo |
| 👤 Paciente | `maria_santos` | `paciente123` | Usuário de exemplo |

## 🔧 Configuração da API Gemini

1. **Obter chave gratuita:**
   - Acesse: https://ai.google.dev/
   - Faça login com conta Google
   - Gere uma chave API

2. **Configurar no sistema:**
   - Abra `main.py`
   - Linha 265: substitua pela sua chave
   - Ou use o script `setup.py` para configuração automática

## 📊 Como Usar

### Para Administradores:
1. **Login** com `admin/admin123`
2. **Criar médicos** na aba "👥 Usuários"
3. **Criar pacientes** com dados básicos
4. **Monitorar** todas as avaliações do sistema
5. **Gerenciar** usuários e permissões

### Para Médicos:
1. **Login** com credenciais fornecidas pelo admin
2. **Selecionar paciente** na lista disponível
3. **Realizar avaliação completa** com dados clínicos
4. **Adicionar observações** médicas especializadas
5. **Salvar avaliação** no histórico do paciente
6. **Gerar relatório PDF** para consulta

### Para Pacientes:
1. **Login** com credenciais fornecidas
2. **Preencher autoavaliação** com dados pessoais
3. **Incluir exames** se disponíveis
4. **Obter análise de IA** sobre riscos
5. **Visualizar histórico** de avaliações anteriores
6. **Gerar PDF** para levar ao médico

## 🏗️ Arquitetura do Sistema

### Tecnologias Utilizadas:
- **Frontend**: PyQt5 (Interface gráfica)
- **Backend**: Python 3.7+
- **Banco de Dados**: SQLite3
- **IA**: Google Gemini API
- **Relatórios**: FPDF2
- **Segurança**: SHA-256 para senhas

### Estrutura do Banco de Dados:

```sql
-- Usuários do sistema
CREATE TABLE usuarios (
    id INTEGER PRIMARY KEY,
    username TEXT UNIQUE,
    password_hash TEXT,
    tipo TEXT CHECK(tipo IN ('admin', 'medico', 'paciente')),
    nome TEXT,
    email TEXT,
    telefone TEXT,
    crm TEXT,
    especialidade TEXT,
    data_nascimento DATE,
    data_criacao TIMESTAMP,
    ativo BOOLEAN
);

-- Dados clínicos adicionais de pacientes
CREATE TABLE pacientes_dados (
    id INTEGER PRIMARY KEY,
    usuario_id INTEGER,
    altura_cm REAL,
    peso_kg REAL,
    historico_familiar_hipertensao BOOLEAN,
    observacoes TEXT,
    FOREIGN KEY (usuario_id) REFERENCES usuarios (id)
);

-- Histórico de avaliações
CREATE TABLE avaliacoes (
    id INTEGER PRIMARY KEY,
    paciente_id INTEGER,
    medico_id INTEGER,
    data_avaliacao TIMESTAMP,
    dados_autoavaliacao TEXT, -- JSON
    dados_exames TEXT, -- JSON
    resultado_ia TEXT,
    observacoes_medico TEXT,
    status TEXT CHECK(status IN ('pendente', 'revisado', 'finalizado')),
    FOREIGN KEY (paciente_id) REFERENCES usuarios (id),
    FOREIGN KEY (medico_id) REFERENCES usuarios (id)
);
```

## 🔍 Parâmetros de Avaliação

### Dados de Autoavaliação:
- **Demográficos**: Idade, sexo
- **Antropométricos**: Altura, peso, IMC (calculado)
- **Histórico**: Familiar de hipertensão
- **Estilo de vida**: Exercícios, alimentação, tabagismo
- **Fatores psicossociais**: Estresse, qualidade do sono
- **Consumo**: Álcool por semana

### Exames Clínicos (Opcionais):
- **Perfil lipídico**: LDL, HDL, triglicerídeos
- **Metabolismo**: Glicemia, HbA1c
- **Função renal**: Creatinina, proteinúria
- **Cardiovascular**: Frequência cardíaca de repouso
- **Hormonal**: Cortisol sérico
- **Genético**: Mutações para hipertensão
- **Ambiental**: Índice de poluição PM2.5
- **Distúrbios**: Apneia do sono

## 🤖 Análise por Inteligência Artificial

### Características da Análise:
- **Modelo**: Google Gemini 2.0 Flash
- **Abordagem**: Análise médica especializada
- **Saída**: Relatório estruturado em português
- **Componentes**:
  - Classificação de risco (BAIXO/MODERADO/ALTO/MUITO ALTO)
  - Fatores de risco identificados
  - Recomendações específicas
  - Plano de ação detalhado
  - Alertas e limitações

### Prompt Especializado:
O sistema utiliza prompt médico otimizado que instrui a IA a:
- Atuar como cardiologista especialista
- Fornecer análise baseada em evidências
- Usar linguagem acessível ao paciente
- Incluir recomendações práticas
- Alertar sobre limitações da análise automática

## 📄 Sistema de Relatórios

### Relatórios em PDF:
- **Cabeçalho**: Identificação do paciente e médico
- **Dados coletados**: Autoavaliação e exames
- **Análise de IA**: Resultado completo da avaliação
- **Observações médicas**: Comentários do profissional
- **Formatação**: Profissional e legível
- **Codificação**: Latin-1 para compatibilidade

### Histórico Digital:
- **Pacientes**: Visualizam apenas suas avaliações
- **Médicos**: Acessam todas as avaliações
- **Administradores**: Visão completa do sistema
- **Detalhamento**: Dados estruturados em JSON
- **Pesquisa**: Por data, médico ou status

## 🔒 Segurança e Privacidade

### Autenticação:
- **Hash**: SHA-256 para todas as senhas
- **Sessões**: Controle por usuário logado
- **Permissões**: Baseadas no tipo de usuário
- **Validação**: Entrada de dados em todas as telas

### Proteção de Dados:
- **Banco local**: SQLite criptografado por SO
- **Backup automático**: Opcional via configuração
- **Logs de auditoria**: Para implementação futura
- **LGPD**: Estrutura preparada para conformidade

## 🎨 Interface e Usabilidade

### Design Responsivo:
- **Resolução**: Otimizado para 16:9, mínimo 640x360
- **Tema**: Cores profissionais e modernas
- **Ícones**: Unicode para compatibilidade universal
- **Navegação**: Abas intuitivas por perfil
- **Feedback**: Visual em todas as ações

### Acessibilidade:
- **Contraste**: Alto contraste para leitura
- **Fontes**: Tamanhos legíveis (14px+)
- **Navegação**: Keyboard-friendly
- **Mensagens**: Claras e informativas
- **Validação**: Em tempo real quando possível

## ⚙️ Personalização Avançada

### Arquivo config.py:
```python
# Modificar cores do tema
COLORS = {
    'primary': '#667eea',
    'success': '#4CAF50',
    # ... outras cores
}

# Ajustar prompt da IA
HYPERTENSION_ANALYSIS_PROMPT = """
Seu prompt personalizado aqui...
"""

# Configurar validações
FIELD_LIMITS = {
    'idade_max': 120,
    'peso_max': 500,
    # ... outros limites
}
```

### Adicionando Novos Campos:
1. **Modificar** classe `HypertensionEvaluationWidget`
2. **Atualizar** estrutura do banco se necessário
3. **Ajustar** prompt da IA para incluir novos dados
4. **Testar** integração completa

## 🔧 Resolução de Problemas

### Problemas Comuns:

#### "ModuleNotFoundError: No module named 'PyQt5'"
```bash
pip install PyQt5==5.15.7
# Se falhar:
pip install --user PyQt5==5.15.7
```

#### "Erro ao inicializar Gemini"
1. Verificar chave API no código
2. Testar chave em: https://ai.google.dev/
3. Verificar conexão com internet
4. Reinstalar: `pip install google-generativeai`

#### "Banco de dados bloqueado"
1. Fechar todas as instâncias do programa
2. Renomear `hypertension_system.db`
3. Executar novamente (será recriado)

#### Interface não aparece (Linux)
```bash
# Instalar dependências do sistema
sudo apt-get install python3-pyqt5
sudo apt-get install python3-pyqt5.qtwidgets
```

#### Erro de codificação no PDF
- Sistema usa Latin-1 para máxima compatibilidade
- Caracteres especiais são convertidos automaticamente
- Para UTF-8: modificar função `gerar_pdf()`

### Logs de Debug:
```python
# Adicionar no início do main.py para debug
import logging
logging.basicConfig(level=logging.DEBUG)
```

## 🚀 Próximas Funcionalidades

### Versão 2.0 (Planejado):
- [ ] **Dashboard estatístico** com gráficos
- [ ] **Notificações por email** para médicos
- [ ] **Export para Excel** dos dados
- [ ] **API REST** para integrações
- [ ] **Aplicativo móvel** complementar
- [ ] **Integração com IoT** (medidores de pressão)

### Melhorias Técnicas:
- [ ] **Cache inteligente** para consultas IA
- [ ] **Backup automático** na nuvem
- [ ] **Logs de auditoria** completos
- [ ] **Criptografia avançada** do banco
- [ ] **Modo offline** parcial
- [ ] **Multi-idioma** (EN, ES)

## 📞 Suporte

### Documentação:
- **README**: Instruções básicas
- **config.py**: Comentários detalhados em cada configuração
- **Código fonte**: Comentado e estruturado

### Comunidade:
- **Issues**: Para reportar bugs
- **Discussões**: Para sugestões de melhorias
- **Wiki**: Documentação expandida (em desenvolvimento)

### Contribuições:
1. **Fork** do repositório
2. **Branch** para sua feature: `git checkout -b feature/nova-funcionalidade`
3. **Commit** suas mudanças: `git commit -m 'Adiciona nova funcionalidade'`
4. **Push** para branch: `git push origin feature/nova-funcionalidade`
5. **Pull Request** detalhado

## ⚖️ Licença e Responsabilidade

### Licença MIT:
```
Copyright (c) 2024 Sistema de Gestão de Hipertensão

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software...
```

### Aviso Médico:
⚠️ **IMPORTANTE**: Este sistema é uma ferramenta de apoio à decisão clínica. 

- **NÃO substitui** consulta médica presencial
- **NÃO deve ser usado** para autodiagnóstico
- **Sempre consulte** profissionais qualificados
- **Resultados da IA** são orientativos, não definitivos
- **Para emergências** procure atendimento imediato

### Conformidade:
- **LGPD**: Estrutura preparada para adequação
- **CFM**: Respeita diretrizes do Conselho Federal de Medicina
- **Ética médica**: Ferramenta de apoio, não substituto do médico

## 📊 Especificações Técnicas

### Requisitos Mínimos:
- **SO**: Windows 10+, Linux Ubuntu 18+, macOS 10.14+
- **Python**: 3.7 ou superior
- **RAM**: 2GB mínimo, 4GB recomendado
- **Armazenamento**: 100MB + dados do usuário
- **Internet**: Necessária para análise de IA

### Performance:
- **Inicialização**: < 3 segundos
- **Consulta IA**: 5-15 segundos (depende da rede)
- **Geração PDF**: < 2 segundos
- **Banco de dados**: Suporta milhares de avaliações

### Compatibilidade:
- **Python**: 3.7, 3.8, 3.9, 3.10, 3.11, 3.12
- **PyQt5**: 5.15.x (todas as versões)
- **SQLite**: 3.6+ (incluído no Python)

---

## 🎉 Conclusão

O **Sistema de Gestão de Hipertensão** combina tecnologia moderna com práticas médicas estabelecidas, oferecendo uma ferramenta robusta e intuitiva para profissionais de saúde e pacientes.

### Características Principais:
✅ **Completo** - Cobre todo o fluxo de avaliação cardiovascular  
✅ **Inteligente** - IA especializada em cardiologia  
✅ **Seguro** - Criptografia e controle de acesso  
✅ **Profissional** - Interface e relatórios de qualidade hospitalar  
✅ **Extensível** - Arquitetura preparada para crescimento  

### Começar Agora:
```bash
git clone [repositorio]
cd sistema_hipertensao
python setup.py
```

**Desenvolvido com ❤️ para melhorar o cuidado cardiovascular**

---

*Última atualização: 2024 | Versão: 1.0.0*