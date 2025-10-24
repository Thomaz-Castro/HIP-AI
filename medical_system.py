import sys
from PyQt5.QtWidgets import (
    QApplication, QMessageBox,
    QDialog
)
from dotenv import load_dotenv
from Classes.LoginWindow import LoginWindow
from Classes.DatabaseManager import DatabaseManager 

# Carrega variáveis de ambiente
load_dotenv()

def main():
    app = QApplication(sys.argv)

    try:
        print("Iniciando Sistema Médico...")

        # Inicializa banco de dados
        print("Conectando ao PostgreSQL...")
        db_manager = DatabaseManager()
        
        # 1. ERRO ESTAVA AQUI: Verifique 'connection_pool', não 'client'
        if not db_manager.connection_pool: 
            QMessageBox.critical(
                None, "Erro", "Não foi possível conectar ao PostgreSQL!")
            return

        # 2. Apenas texto atualizado
        print("Conexão PostgreSQL OK")

        # Mostra tela de login
        print("Abrindo tela de login...")
        login_window = LoginWindow(db_manager)
        login_result = login_window.exec_()

        print(f"Resultado do login: {login_result}")

        if login_result == QDialog.Accepted and login_window.user:
            print("Login aceito, executando aplicação principal...")
            # Login bem sucedido, a janela principal já foi aberta
            # Agora executa o loop principal da aplicação
            app_result = app.exec_()
            print(f"Aplicação encerrada com código: {app_result}")
        else:
            print("Login cancelado ou falhou")

    except Exception as e:
        QMessageBox.critical(None, "Erro Crítico",
                             f"Erro inesperado: {str(e)}")
        print(f"Erro crítico: {e}")
        import traceback
        traceback.print_exc()

    finally:
        # 3. Garante que o pool de conexões será fechado ao sair
        if 'db_manager' in locals() and db_manager.connection_pool:
            db_manager.close()
        print("Sistema encerrado.")


if __name__ == "__main__":
    main()