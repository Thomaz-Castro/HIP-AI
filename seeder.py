#!/usr/bin/env python3
"""
Script de Seeding do Banco de Dados
Popula o banco com dados de exemplo: administradores, médicos e pacientes
"""

from datetime import date
from dotenv import load_dotenv
from Classes.DatabaseManager import DatabaseManager

# Carrega variáveis de ambiente
load_dotenv()

def seed_database():
    """Popula o banco de dados com dados de exemplo"""
    
    print("=" * 60)
    print("INICIANDO SEEDING DO BANCO DE DADOS POSTGRESQL")
    print("=" * 60)
    
    db_manager = None
    
    try:
        # Conecta ao banco
        print("\n[1/4] Conectando ao PostgreSQL...")
        db_manager = DatabaseManager()
        
        if not db_manager.connection_pool:
            print("❌ ERRO: Não foi possível inicializar o pool de conexões!")
            return False
        
        print("✓ Conexão estabelecida (via pool)!")
        
        # Administradores
        print("\n[2/4] Criando administradores...")
        admins = [
            {
                "name": "Admin Principal",
                "email": "admin@sistema.com",
                "password": "admin123",
                "user_type": "admin",
                "additional_data": {
                    "cpf": "143.963.380-07"
                }
            },
            {
                "name": "Admin Secundário",
                "email": "admin2@sistema.com",
                "password": "admin123",
                "user_type": "admin",
                "additional_data": {
                    "cpf": "023.305.392-15"
                }
            }
        ]
        
        admin_count = 0
        for admin in admins:
            result = db_manager.create_user(
                admin["name"],
                admin["email"],
                admin["password"],
                admin["user_type"],
                admin.get("additional_data")
            )
            if result:
                admin_count += 1
                print(f"  ✓ Admin criado: {admin['email']}")
            else:
                print(f"  ⚠ Admin já existe ou houve erro: {admin['email']}")
        
        print(f"Total de admins novos criados: {admin_count}")
        
        # Médicos
        print("\n[3/4] Criando médicos...")
        doctors = [
            {
                "name": "Dr. Carlos Silva",
                "email": "carlos.silva@clinica.com",
                "password": "medico123",
                "user_type": "doctor",
                "additional_data": {
                    "cpf": "244.610.632-32",
                    "crm": "12345-SP",
                    "specialty": "Cardiologia",
                    "phone": "(11) 98765-4321"
                }
            },
            {
                "name": "Dra. Maria Santos",
                "email": "maria.santos@clinica.com",
                "password": "medico123",
                "user_type": "doctor",
                "additional_data": {
                    "cpf": "842.459.065-10",
                    "crm": "67890-SP",
                    "specialty": "Clínica Geral",
                }
            },
            {
                "name": "Dr. João Oliveira",
                "email": "joao.oliveira@clinica.com",
                "password": "medico123",
                "user_type": "doctor",
                "additional_data": {
                    "cpf": "254.045.786-02",
                    "crm": "54321-RJ",
                    "specialty": "Cardiologia",
                }
            },
            {
                "name": "Dra. Ana Paula Costa",
                "email": "ana.costa@clinica.com",
                "password": "medico123",
                "user_type": "doctor",
                "additional_data": {
                    "cpf": "443.526.585-02",
                    "crm": "98765-SP",
                    "specialty": "Endocrinologia",
                }
            }
        ]
        
        doctor_count = 0
        for doctor in doctors:
            result = db_manager.create_user(
                doctor["name"],
                doctor["email"],
                doctor["password"],
                doctor["user_type"],
                doctor.get("additional_data")
            )
            if result:
                doctor_count += 1
                print(f"  ✓ Médico criado: {doctor['name']} - {doctor['email']}")
            else:
                print(f"  ⚠ Médico já existe ou houve erro: {doctor['email']}")
        
        print(f"Total de médicos criados: {doctor_count}")
        
        # Pacientes
        print("\n[4/4] Criando pacientes...")
        patients = [
            {
                "name": "José da Silva",
                "email": "jose.silva@email.com",
                "password": "paciente123",
                "user_type": "patient",
                "additional_data": {
                    "cpf": "865.952.089-03",
                    "birth_date": date(1980, 5, 15),
                    "phone": "(11) 91234-5678",
                }
            },
            {
                "name": "Maria Oliveira",
                "email": "maria.oliveira@email.com",
                "password": "paciente123",
                "user_type": "patient",
                "additional_data": {
                    "cpf": "824.964.531-67",
                    "birth_date": date(1975, 8, 20),
                    "phone": "(11) 91234-5679",
                }
            },
            {
                "name": "Pedro Santos",
                "email": "pedro.santos@email.com",
                "password": "paciente123",
                "user_type": "patient",
                "additional_data": {
                    "cpf": "084.632.978-62",
                    "birth_date": date(1990, 3, 10),
                    "phone": "(11) 91234-5680",
                }
            },
            {
                "name": "Ana Costa",
                "email": "ana.costa.paciente@email.com",
                "password": "paciente123",
                "user_type": "patient",
                "additional_data": {
                    "cpf": "991.877.805-93",
                    "birth_date": date(1985, 12, 5),
                    "phone": "(11) 91234-5681",
                }
            },
            {
                "name": "Carlos Ferreira",
                "email": "carlos.ferreira@email.com",
                "password": "paciente123",
                "user_type": "patient",
                "additional_data": {
                    "cpf": "051.120.300-46",
                    "birth_date": date(1978, 7, 25),
                    "phone": "(11) 91234-5682",
                }
            },
            {
                "name": "Beatriz Lima",
                "email": "beatriz.lima@email.com",
                "password": "paciente123",
                "user_type": "patient",
                "additional_data": {
                    "cpf": "408.027.247-28",
                    "birth_date": date(1995, 1, 30),
                    "phone": "(11) 91234-5683",
                }
            },
            {
                "name": "Roberto Alves",
                "email": "roberto.alves@email.com",
                "password": "paciente123",
                "user_type": "patient",
                "additional_data": {
                    "cpf": "116.836.556-21",
                    "birth_date": date(1988, 9, 12),
                    "phone": "(11) 91234-5684",
                }
            },
            {
                "name": "Juliana Rocha",
                "email": "juliana.rocha@email.com",
                "password": "paciente123",
                "user_type": "patient",
                "additional_data": {
                    "cpf": "449.737.112-33",
                    "birth_date": date(1992, 4, 18),
                    "phone": "(11) 91234-5685",
                }
            },
            {
                "name": "Fernando Souza",
                "email": "fernando.souza@email.com",
                "password": "paciente123",
                "user_type": "patient",
                "additional_data": {
                    "cpf": "985.228.198-40",
                    "birth_date": date(1983, 11, 8),
                    "phone": "(11) 91234-5686",
                }
            },
            {
                "name": "Camila Martins",
                "email": "camila.martins@email.com",
                "password": "paciente123",
                "user_type": "patient",
                "additional_data": {
                    "cpf": "442.898.867-28",
                    "birth_date": date(1991, 6, 22),
                    "phone": "(11) 91234-5687",
                }
            }
        ]
        
        patient_count = 0
        for patient in patients:
            result = db_manager.create_user(
                patient["name"],
                patient["email"],
                patient["password"],
                patient["user_type"],
                patient.get("additional_data")
            )
            if result:
                patient_count += 1
                print(f"  ✓ Paciente criado: {patient['name']} - {patient['email']}")
            else:
                print(f"  ⚠ Paciente já existe ou houve erro: {patient['email']}")
        
        print(f"Total de pacientes criados: {patient_count}")
        
        # Resumo final
        print("\n" + "=" * 60)
        print("RESUMO DO SEEDING")
        print("=" * 60)
        print(f"Administradores novos: {admin_count}/{len(admins)}")
        print(f"Médicos criados:       {doctor_count}/{len(doctors)}")
        print(f"Pacientes criados:     {patient_count}/{len(patients)}")
        print(f"Total de usuários novos: {admin_count + doctor_count + patient_count}")
        print("=" * 60)
        
        print("\n✓ SEEDING CONCLUÍDO COM SUCESSO!")
        print("\nCredenciais de acesso:")
        print("  Admin:    admin@sistema.com / admin123")
        print("  Admin 2:  admin2@sistema.com / admin123")
        print("  Médico:   carlos.silva@clinica.com / medico123")
        print("  Paciente: jose.silva@email.com / paciente123")
        print("\nℹ️  Nota: CPFs de exemplo foram adicionados a todos os usuários")
        
        return True

    except Exception as e:
        print(f"\n❌ ERRO DURANTE O SEEDING: {str(e)}")
        import traceback
        traceback.print_exc()
        return False
        
    finally:
        if db_manager:
            print("\n[FINAL] Fechando conexões...")
            db_manager.close()

if __name__ == "__main__":
    seed_database()