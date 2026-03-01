import sqlite3
import os

def seed_database():
    # Caminho para o seu banco SQLite
    db_path = os.path.join('data', 'student_subjects.db')
    
    if not os.path.exists(db_path):
        print("Erro: Banco de dados não encontrado. Rode o backend primeiro para criar o schema.")
        return

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Limpa as disciplinas atuais para evitar duplicatas ao testar
    cursor.execute('DELETE FROM subjects')

    cursor.execute("INSERT OR IGNORE INTO courses (id, name, course_code) VALUES (1, 'Sistemas de Informação', 'GSI')")
    cursor.execute("INSERT OR IGNORE INTO courses (id, name, course_code) VALUES (2, 'Ciência da Computação', 'BCC')")

    # Lista de disciplinas extraídas dos fluxogramas
    subjects = [
        # --- SISTEMAS DE INFORMAÇÃO (SI) ---
        (
            'Introdução à Programação de Computadores', 'GSI002', 
            'Lógica e algoritmos iniciais.', 'Programação', 2, 4, '1º Período', 1,
            'Prof. Dr. Ricardo Silva', 'Segunda (19:00-20:40), Quarta (20:50-22:30)'
        ),
        (
            'Banco de Dados 1', 'GSI016', 
            'Modelagem ER e SQL básico.', 'Banco de Dados', 3, 4, '4º Período', 1,
            'Profa. Ana Oliveira', 'Terça (19:30-22:30)'
        ),
        # --- CIÊNCIA DA COMPUTAÇÃO (BCC) ---
        (
            'Programação Procedimental', 'FACOM31103', 
            'C e fundamentos de memória.', 'Programação', 3, 4, '1º Período', 2,
            'Prof. Marcos Souza', 'Quarta (19:30-20:40), Quinta (20:50-22:30)'
        ),
    ]

    try:
        cursor.executemany('''
            INSERT INTO subjects (name, code, description, category, difficulty_level, credits, semester, course_id, teacher_name, schedule)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', subjects)
        
        conn.commit()
        print(f"Sucesso! {len(subjects)} disciplinas inseridas no banco.")
    except Exception as e:
        print(f"Erro ao inserir: {e}")
    finally:
        conn.close()

if __name__ == "__main__":
    seed_database()