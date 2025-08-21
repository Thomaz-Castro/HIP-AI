#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script de configuração inicial do Sistema de Gestão de Hipertensão

Este script automatiza a instalação e configuração inicial do sistema.
Execute: python setup.py
"""

import os
import sys
import subprocess
import sqlite3
from pathlib import Path

def print_banner():
    """Exibe o banner do sistema"""
    banner = """
    ╔══════════════════════════════════════════════════════════════╗
    ║                                                              ║
    ║        🏥 SISTEMA DE GESTÃO DE HIPERTENSÃO 🏥              ║
    ║                                                              ║
    ║                    Script de Configuração                   ║
    ║                                                              ║
    ╚══════════════════════════════════════════════════════════════╝
    """
    print(banner)

def check_python_version():
    """Verifica se a versão do Python é compatível"""
    print("🔍 Verificando versão do Python...")
    version = sys.version_info
    if version.major < 3 or (version.major == 3 and version.minor < 7):
        print("❌ ERRO: Python 3.7+ é necessário!")
        print(f"   Versão atual: {version.major}.{version.minor}.{version.micro}")
        print("   Baixe a versão mais recente em: https://python.org")
        return False
    else:
        print(f"✅ Python {version.major}.{version.minor}.{version.micro} - OK")
        return True

def install_requirements():
    """Instala as dependências necessárias"""
    print("\n📦 Instalando dependências...")
    
    requirements = [
        "PyQt5==5.15.7",
        "fpdf2==2.7.4", 
        "google-generativeai==0.3.2"
    ]
    
    for package in requirements:
        print(f"   Instalando {package}...")
        try:
            result = subprocess.run([
                sys.executable, "-m", "pip", "install", package
            ], capture_output=True, text=True, check=True)
            print(f"   ✅ {package} instalado com sucesso")
        except subprocess.CalledProcessError as e:
            print(f"   ❌ Erro ao instalar {package}")
            print(f"   Detalhes: {e.stderr}")
            return False
    
    return True

def create_directories():
    """Cria diretórios necessários"""
    print("\n📁 Criando diretórios...")
    
    directories = ["backups", "reports", "logs"]
    
    for directory in directories:
        path = Path(directory)
        if not path.exists():
            path.mkdir(parents=True, exist_ok=True)
            print(f"   ✅ Diretório '{directory}' criado")
        else:
            print(f"   ℹ️  Diretório '{directory}' já existe")
    
    return True

def setup_database():
    """Configura o banco de dados inicial"""
    print("\n🗄️  Configurando banco de dados...")
    
    db_path = "hypertension_system.db"
    
    try:
        # Importa a classe DatabaseManager do main.py
        sys.path.append(os.path.dirname(os.path.abspath(__file__)))
        from main import DatabaseManager
        
        # Inicializa o banco
        db_manager = DatabaseManager(db_path)
        print("   ✅ Banco de dados configurado")
        print("   ℹ️  Usuário admin criado: admin/admin123")
        
        return True
        
    except Exception as e:
        print(f"   ❌ Erro ao configurar banco: {e}")
        return False

def configure_gemini_api():
    """Configura a API do Gemini"""
    print("\n🤖 Configuração da API Gemini...")
    print("   Para usar o sistema completo, você precisa de uma chave API do Google Gemini.")
    print("   Passos para obter a chave:")
    print("   1. Acesse: https://ai.google.dev/")
    print("   2. Crie uma conta ou faça login")
    print("   3. Gere uma chave API gratuita")
    print("   4. Substitua no arquivo main.py, linha 265")
    
    choice = input("\n   Você já tem uma chave API? (s/n): ").lower().strip()
    
    if choice == 's':
        api_key = input("   Cole sua chave API aqui: ").strip()
        if api_key:
            try:
                # Lê o arquivo main.py
                with open('main.py', 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # Substitui a chave API
                old_key = 'API_KEY = "AIzaSyAmraGN6apiXmyQTcgKaj-BaM_Zzro6IHk"'
                new_key = f'API_KEY = "{api_key}"'
                content = content.replace(old_key, new_key)
                
                # Salva o arquivo
                with open('main.py', 'w', encoding='utf-8') as f:
                    f.write(content)
                
                print("   ✅ Chave API configurada com sucesso!")
                return True
                
            except Exception as e:
                print(f"   ❌ Erro ao configurar chave: {e}")
                return False
    else:
        print("   ⚠️  Lembre-se de configurar a chave API antes de usar o sistema!")
        return True

def create_sample_users():
    """Cria usuários de exemplo"""
    print("\n👥 Criando usuários de exemplo...")
    
    try:
        from main import DatabaseManager
        db = DatabaseManager()
        
        # Médico de exemplo
        medico_id = db.create_user(
            username="dr_silva",
            password="medico123",
            tipo="medico",
            nome="Dr. João Silva",
            email="joao.silva@hospital.com",
            crm="12345SP",
            especialidade="Cardiologia"
        )
        
        if medico_id:
            print("   ✅ Médico criado: dr_silva/medico123")
        
        # Paciente de exemplo
        paciente_id = db.create_user(
            username="maria_santos",
            password="paciente123", 
            tipo="paciente",
            nome="Maria Santos",
            email="maria.santos@email.com",
            telefone="(11) 99999-9999",
            data_nascimento="15/03/1980"
        )
        
        if paciente_id:
            print("   ✅ Paciente criado: maria_santos/paciente123")
            
        return True
        
    except Exception as e:
        print(f"   ❌ Erro ao criar usuários: {e}")
        return False

def create_desktop_shortcut():
    """Cria atalho na área de trabalho (Windows)"""
    if os.name != 'nt':  # Não é Windows
        return True
        
    print("\n🖥️  Criando atalho na área de trabalho...")
    
    try:
        import winshell
        desktop = winshell.desktop()
        
        shortcut = os.path.join(desktop, "Sistema Hipertensão.lnk")
        target = os.path.join(os.getcwd(), "main.py")
        
        with winshell.shortcut(shortcut) as link:
            link.path = sys.executable
            link.arguments = f'"{target}"'
            link.description = "Sistema de Gestão de Hipertensão"
            link.working_directory = os.getcwd()
        
        print("   ✅ Atalho criado na área de trabalho")
        return True
        
    except ImportError:
        print("   ⚠️  Para criar atalho, instale: pip install winshell")
        return True
    except Exception as e:
        print(f"   ⚠️  Não foi possível criar atalho: {e}")
        return True

def run_tests():
    """Executa testes básicos do sistema"""
    print("\n🧪 Executando testes básicos...")
    
    try:
        # Testa importação do módulo principal
        from main import DatabaseManager, LoginWindow
        print("   ✅ Importação dos módulos - OK")
        
        # Testa conexão com banco
        db = DatabaseManager()
        user = db.authenticate_user("admin", "admin123")
        if user:
            print("   ✅ Autenticação do admin - OK")
        else:
            print("   ❌ Erro na autenticação")
            return False
        
        # Testa dependências
        import PyQt5
        print("   ✅ PyQt5 - OK")
        
        import fpdf
        print("   ✅ FPDF - OK")
        
        try:
            import google.generativeai
            print("   ✅ Google Gemini - OK")
        except:
            print("   ⚠️  Google Gemini - Verifique a instalação")
        
        return True
        
    except Exception as e:
        print(f"   ❌ Erro nos testes: {e}")
        return False

def main():
    """Função principal do script de configuração"""
    print_banner()
    
    # Lista de etapas da configuração
    steps = [
        ("Verificação do Python", check_python_version),
        ("Instalação de dependências", install_requirements),
        ("Criação de diretórios", create_directories),
        ("Configuração do banco", setup_database),
        ("Configuração da IA", configure_gemini_api),
        ("Criação de usuários exemplo", create_sample_users),
        ("Atalho da área de trabalho", create_desktop_shortcut),
        ("Testes do sistema", run_tests)
    ]
    
    print("🚀 Iniciando configuração do sistema...\n")
    
    success_count = 0
    total_steps = len(steps)
    
    for step_name, step_function in steps:
        print(f"[{success_count + 1}/{total_steps}] {step_name}")
        
        if step_function():
            success_count += 1
        else:
            print(f"\n❌ Falha na etapa: {step_name}")
            print("   A configuração foi interrompida.")
            
            retry = input("\n   Tentar novamente? (s/n): ").lower().strip()
            if retry == 's':
                if step_function():
                    success_count += 1
                else:
                    print("\n💔 Configuração falhou. Verifique os erros acima.")
                    return False
            else:
                print("\n⏸️  Configuração interrompida pelo usuário.")
                return False
        
        print()
    
    # Resultado final
    if success_count == total_steps:
        print("🎉 CONFIGURAÇÃO CONCLUÍDA COM SUCESSO! 🎉")
        print("\n📋 Resumo:")
        print("   ✅ Sistema configurado e pronto para uso")
        print("   ✅ Banco de dados inicializado")
        print("   ✅ Usuários de exemplo criados")
        print("\n🔑 Credenciais de acesso:")
        print("   👑 Admin: admin / admin123")
        print("   👨‍⚕️ Médico: dr_silva / medico123")
        print("   👤 Paciente: maria_santos / paciente123")
        print("\n🚀 Para iniciar o sistema, execute:")
        print("   python main.py")
        print("\n📖 Para mais informações, consulte o arquivo README.")
        
        # Pergunta se quer executar o sistema agora
        run_now = input("\n🏃 Executar o sistema agora? (s/n): ").lower().strip()
        if run_now == 's':
            print("\n🚀 Iniciando sistema...")
            try:
                subprocess.run([sys.executable, "main.py"])
            except KeyboardInterrupt:
                print("\n👋 Sistema encerrado pelo usuário.")
        
        return True
    else:
        print("⚠️  CONFIGURAÇÃO PARCIALMENTE CONCLUÍDA")
        print(f"   {success_count}/{total_steps} etapas completadas")
        print("   Revise os erros acima antes de executar o sistema.")
        return False

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⏸️  Configuração cancelada pelo usuário.")
        sys.exit(1)
    except Exception as e:
        print(f"\n💥 Erro inesperado: {e}")
        print("   Entre em contato com o suporte técnico.")
        sys.exit(1)
    
    input("\n⏎  Pressione Enter para sair...")