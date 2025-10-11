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
        print("Conectando ao MongoDB...")
        db_manager = DatabaseManager()
        if not db_manager.client:
            QMessageBox.critical(
                None, "Erro", "Não foi possível conectar ao MongoDB!")
            return

        print("Conexão MongoDB OK")

        # Mostra tela de login
        print("Abrindo tela de login...")
        login_window = LoginWindow(db_manager)
        login_result = login_window.exec_()

        print(f"Resultado do login: {login_result}")

        if login_result == QDialog.Accepted and login_window.user:
            print("Login aceito, executando aplicação principal...")
            # Login bem sucedido, a janela principal já foi aberta
            # Agora executa o loop principal da aplicação
            app.exec_()
            print("Aplicação encerrada normalmente")
        else:
            print("Login cancelado ou falhou")

    except Exception as e:
        QMessageBox.critical(None, "Erro Crítico",
                             f"Erro inesperado: {str(e)}")
        print(f"Erro crítico: {e}")
        import traceback
        traceback.print_exc()

    finally:
        print("Sistema encerrado.")


if __name__ == "__main__":
    main()
