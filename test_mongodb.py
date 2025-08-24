#!/usr/bin/env python
"""
Script para testar conexão com MongoDB Atlas
Execute este script antes de usar o sistema principal
"""

import os
from pymongo import MongoClient
from dotenv import load_dotenv

def test_mongodb_connection():
    print("🔧 Testando conexão com MongoDB Atlas...")
    print("=" * 50)
    
    # Carrega variáveis de ambiente
    load_dotenv()
    
    # Obtém string de conexão
    mongodb_uri = os.getenv("MONGODB_URI")
    
    if not mongodb_uri:
        print("❌ ERRO: Variável MONGODB_URI não encontrada!")
        print("💡 Verifique se o arquivo .env existe e contém MONGODB_URI")
        return False
    
    print(f"🔗 Conectando com: {mongodb_uri[:30]}...")
    
    try:
        # Tenta conectar
        client = MongoClient(mongodb_uri, serverSelectionTimeoutMS=10000)
        
        # Testa a conexão
        client.admin.command('ismaster')
        print("✅ Conexão estabelecida com sucesso!")
        
        # Testa acesso ao banco
        db = client.medical_system
        
        # Testa criação de documento
        test_collection = db.test_connection
        result = test_collection.insert_one({"test": "connection", "status": "ok"})
        print(f"✅ Escrita no banco funcionando! ID: {result.inserted_id}")
        
        # Remove documento de teste
        test_collection.delete_one({"_id": result.inserted_id})
        print("✅ Leitura/exclusão no banco funcionando!")
        
        # Lista collections existentes
        collections = db.list_collection_names()
        print(f"📦 Collections existentes: {collections}")
        
        # Fecha conexão
        client.close()
        print("✅ Teste concluído com sucesso!")
        print("\n🚀 Você pode executar o sistema principal agora!")
        return True
        
    except Exception as e:
        print(f"❌ ERRO na conexão: {e}")
        print("\n💡 Possíveis soluções:")
        print("1. Verificar string de conexão no arquivo .env")
        print("2. Confirmar usuário/senha do MongoDB Atlas")
        print("3. Verificar liberação de IP no Network Access")
        print("4. Testar conectividade: ping cluster.mongodb.net")
        return False

def check_dependencies():
    print("\n🔍 Verificando dependências...")
    
    required_modules = ['pymongo', 'PyQt5', 'fpdf2', 'python-dotenv']
    missing_modules = []
    
    for module in required_modules:
        try:
            __import__(module)
            print(f"✅ {module}: OK")
        except ImportError:
            missing_modules.append(module)
            print(f"❌ {module}: FALTANDO")
    
    if missing_modules:
        print(f"\n❌ Módulos faltando: {missing_modules}")
        print("💡 Execute: pip install -r requirements.txt")
        return False
    
    return True

def check_env_file():
    print("\n📄 Verificando arquivo .env...")
    
    if not os.path.exists('.env'):
        print("❌ Arquivo .env não encontrado!")
        if os.path.exists('.env.example'):
            print("💡 Copie .env.example para .env e configure sua conexão")
            return False
        else:
            print("❌ Arquivo .env.example também não encontrado!")
            return False
    
    load_dotenv()
    mongodb_uri = os.getenv("MONGODB_URI")
    
    if not mongodb_uri:
        print("❌ MONGODB_URI não definido no .env")
        return False
    
    if "username:password" in mongodb_uri:
        print("⚠️  MONGODB_URI ainda contém valores de exemplo!")
        print("💡 Edite o arquivo .env com suas credenciais reais")
        return False
    
    print("✅ Arquivo .env configurado!")
    return True

if __name__ == "__main__":
    print("🏥 SISTEMA MÉDICO - TESTE DE CONFIGURAÇÃO")
    print("=" * 50)
    
    # Verifica dependências
    if not check_dependencies():
        input("\n❌ Pressione Enter para sair...")
        exit(1)
    
    # Verifica arquivo .env
    if not check_env_file():
        input("\n❌ Pressione Enter para sair...")
        exit(1)
    
    # Testa conexão MongoDB
    if test_mongodb_connection():
        print("\n" + "=" * 50)
        print("🎉 CONFIGURAÇÃO OK! Sistema pronto para uso!")
        print("🚀 Execute: python medical_system.py")
    else:
        print("\n❌ Configure o MongoDB Atlas primeiro!")
    
    input("\nPressione Enter para sair...")