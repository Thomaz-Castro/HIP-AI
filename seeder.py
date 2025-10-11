#!/usr/bin/env python3
"""
Script de Seeding do Banco de Dados
Popula o banco com dados de exemplo: administradores, médicos e pacientes
"""

from datetime import datetime, date
from dotenv import load_dotenv
from Classes.DatabaseManager import DatabaseManager

# Carrega variáveis de ambiente
load_dotenv()

def seed_database():
    """Popula o banco de dados com dados de exemplo"""
    
    print("=" * 60)
    print("INICIANDO SEEDING DO BANCO DE DADOS")
    print("=" * 60)
    
    # Conecta ao banco
    print("\n[1/4] Conectando ao MongoDB...")
    db_manager = DatabaseManager()
    
    if not db_manager.client:
        print("❌ ERRO: Não foi possível conectar ao MongoDB!")
        return False
    
    print("✓ Conectado com sucesso!")
    
    # Administradores
    print("\n[2/4] Criando administradores...")
    admins = [
        {
            "name": "Admin Principal",
            "email": "admin@sistema.com",
            "password": "admin123",
            "user_type": "admin"
        },
        {
            "name": "Admin Secundário",
            "email": "admin2@sistema.com",
            "password": "admin123",
            "user_type": "admin"
        }
    ]
    
    admin_count = 0
    for admin in admins:
        result = db_manager.create_user(
            admin["name"],
            admin["email"],
            admin["password"],
            admin["user_type"]
        )
        if result:
            admin_count += 1
            print(f"  ✓ Admin criado: {admin['email']}")
        else:
            print(f"  ⚠ Admin já existe: {admin['email']}")
    
    print(f"Total de admins criados: {admin_count}")
    
    # Médicos
    print("\n[3/4] Criando médicos...")
    doctors = [
        {
            "name": "Dr. Carlos Silva",
            "email": "carlos.silva@clinica.com",
            "password": "medico123",
            "user_type": "doctor",
            "additional_data": {
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
                "crm": "67890-SP",
                "specialty": "Clínica Geral",
                "phone": "(11) 98765-4322"
            }
        },
        {
            "name": "Dr. João Oliveira",
            "email": "joao.oliveira@clinica.com",
            "password": "medico123",
            "user_type": "doctor",
            "additional_data": {
                "crm": "54321-RJ",
                "specialty": "Cardiologia",
                "phone": "(21) 98765-4323"
            }
        },
        {
            "name": "Dra. Ana Paula Costa",
            "email": "ana.costa@clinica.com",
            "password": "medico123",
            "user_type": "doctor",
            "additional_data": {
                "crm": "98765-SP",
                "specialty": "Endocrinologia",
                "phone": "(11) 98765-4324"
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
            print(f"  ⚠ Médico já existe: {doctor['email']}")
    
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
                "cpf": "123.456.789-00",
                "birth_date": date(1980, 5, 15),
                "phone": "(11) 91234-5678",
                "address": "Rua das Flores, 123 - São Paulo/SP"
            }
        },
        {
            "name": "Maria Oliveira",
            "email": "maria.oliveira@email.com",
            "password": "paciente123",
            "user_type": "patient",
            "additional_data": {
                "cpf": "234.567.890-11",
                "birth_date": date(1975, 8, 20),
                "phone": "(11) 91234-5679",
                "address": "Av. Paulista, 456 - São Paulo/SP"
            }
        },
        {
            "name": "Pedro Santos",
            "email": "pedro.santos@email.com",
            "password": "paciente123",
            "user_type": "patient",
            "additional_data": {
                "cpf": "345.678.901-22",
                "birth_date": date(1990, 3, 10),
                "phone": "(11) 91234-5680",
                "address": "Rua Augusta, 789 - São Paulo/SP"
            }
        },
        {
            "name": "Ana Costa",
            "email": "ana.costa.paciente@email.com",
            "password": "paciente123",
            "user_type": "patient",
            "additional_data": {
                "cpf": "456.789.012-33",
                "birth_date": date(1985, 12, 5),
                "phone": "(21) 91234-5681",
                "address": "Rua Copacabana, 321 - Rio de Janeiro/RJ"
            }
        },
        {
            "name": "Carlos Pereira",
            "email": "carlos.pereira@email.com",
            "password": "paciente123",
            "user_type": "patient",
            "additional_data": {
                "cpf": "567.890.123-44",
                "birth_date": date(1970, 7, 25),
                "phone": "(11) 91234-5682",
                "address": "Rua Oscar Freire, 654 - São Paulo/SP"
            }
        },
        {
            "name": "Fernanda Lima",
            "email": "fernanda.lima@email.com",
            "password": "paciente123",
            "user_type": "patient",
            "additional_data": {
                "cpf": "678.901.234-55",
                "birth_date": date(1995, 2, 14),
                "phone": "(11) 91234-5683",
                "address": "Rua Consolação, 987 - São Paulo/SP"
            }
        },
        {
            "name": "Roberto Alves",
            "email": "roberto.alves@email.com",
            "password": "paciente123",
            "user_type": "patient",
            "additional_data": {
                "cpf": "789.012.345-66",
                "birth_date": date(1988, 11, 30),
                "phone": "(21) 91234-5684",
                "address": "Av. Atlântica, 147 - Rio de Janeiro/RJ"
            }
        },
        {
            "name": "Juliana Rocha",
            "email": "juliana.rocha@email.com",
            "password": "paciente123",
            "user_type": "patient",
            "additional_data": {
                "cpf": "890.123.456-77",
                "birth_date": date(1992, 4, 18),
                "phone": "(11) 91234-5685",
                "address": "Rua Haddock Lobo, 258 - São Paulo/SP"
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
            print(f"  ⚠ Paciente já existe: {patient['email']}")
    
    print(f"Total de pacientes criados: {patient_count}")
    
    # Resumo final
    print("\n" + "=" * 60)
    print("RESUMO DO SEEDING")
    print("=" * 60)
    print(f"Administradores criados: {admin_count}/{len(admins)}")
    print(f"Médicos criados:         {doctor_count}/{len(doctors)}")
    print(f"Pacientes criados:       {patient_count}/{len(patients)}")
    print(f"Total de usuários:       {admin_count + doctor_count + patient_count}")
    print("=" * 60)
    
    print("\n✓ SEEDING CONCLUÍDO COM SUCESSO!")
    print("\nCredenciais de acesso:")
    print("  Admin:    admin@sistema.com / admin123")
    print("  Médico:   carlos.silva@clinica.com / medico123")
    print("  Paciente: jose.silva@email.com / paciente123")
    
    return True

if __name__ == "__main__":
    try:
        seed_database()
    except Exception as e:
        print(f"\n❌ ERRO DURANTE O SEEDING: {str(e)}")
        import traceback
        traceback.print_exc()