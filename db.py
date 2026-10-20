import sqlite3
from datetime import datetime
from config import DB_PATH


def conectar():
    """Abre conexão com o banco SQLite. Cria o arquivo se não existir."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row  # Permite acessar colunas por nome: t['titulo']
    return conn


def criar_tabela():
    """Cria a tabela de tarefas se ainda não existir."""
    with conectar() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS tarefas (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                titulo TEXT NOT NULL,
                descricao TEXT,
                horario_lembrete TEXT NOT NULL,   -- formato 'YYYY-MM-DD HH:MM'
                concluido INTEGER NOT NULL DEFAULT 0,
                criado_em TEXT NOT NULL
            )
        """)
        conn.commit()


def adicionar_tarefa(titulo, descricao, horario_lembrete):
    """
    Adiciona uma nova tarefa ao banco de dados.
    horario_lembrete: string no formato 'YYYY-MM-DD HH:MM'
    """
    # Valida o formato da data antes de salvar
    datetime.strptime(horario_lembrete, "%Y-%m-%d %H:%M")
    with conectar() as conn:
        cursor = conn.execute(
            """
            INSERT INTO tarefas (titulo, descricao, horario_lembrete, criado_em)
            VALUES (?, ?, ?, ?)
            """,
            (
                titulo,
                descricao,
                horario_lembrete,
                datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            ),
        )
        conn.commit()
        return cursor.lastrowid


def obter_tarefa(tarefa_id):
    """Retorna uma única tarefa pelo ID ou None se não existir."""
    with conectar() as conn:
        cursor = conn.execute("SELECT * FROM tarefas WHERE id = ?", (tarefa_id,))
        return cursor.fetchone()


def atualizar_tarefa(tarefa_id, titulo, descricao, horario_lembrete):
    """Atualiza o título, descrição e horário de uma tarefa existente."""
    datetime.strptime(horario_lembrete, "%Y-%m-%d %H:%M")
    with conectar() as conn:
        conn.execute(
            """
            UPDATE tarefas
            SET titulo = ?, descricao = ?, horario_lembrete = ?
            WHERE id = ?
            """,
            (titulo, descricao, horario_lembrete, tarefa_id),
        )
        conn.commit()


def listar_tarefas_pendentes():
    """Retorna todas as tarefas não concluídas, ordenadas por horário."""
    with conectar() as conn:
        cursor = conn.execute(
            "SELECT * FROM tarefas WHERE concluido = 0 ORDER BY horario_lembrete"
        )
        return cursor.fetchall()


def listar_todas():
    """Retorna todas as tarefas registradas no banco."""
    with conectar() as conn:
        cursor = conn.execute("SELECT * FROM tarefas ORDER BY horario_lembrete")
        return cursor.fetchall()


def listar_recentes(limite=10):
    """Retorna as tarefas criadas mais recentemente."""
    with conectar() as conn:
        cursor = conn.execute(
            "SELECT * FROM tarefas ORDER BY criado_em DESC LIMIT ?",
            (limite,),
        )
        return cursor.fetchall()


def listar_proximas():
    """Retorna as tarefas não concluídas com horário igual ou posterior ao atual."""
    agora = datetime.now().strftime("%Y-%m-%d %H:%M")
    with conectar() as conn:
        cursor = conn.execute(
            "SELECT * FROM tarefas WHERE concluido = 0 AND horario_lembrete >= ? ORDER BY horario_lembrete ASC",
            (agora,),
        )
        return cursor.fetchall()


def listar_concluidas():
    """Retorna todas as tarefas marcadas como concluídas, ordenadas por horário decrescente."""
    with conectar() as conn:
        cursor = conn.execute(
            "SELECT * FROM tarefas WHERE concluido = 1 ORDER BY horario_lembrete DESC"
        )
        return cursor.fetchall()


def marcar_concluida(tarefa_id):
    """Marca uma tarefa como concluída."""
    with conectar() as conn:
        conn.execute("UPDATE tarefas SET concluido = 1 WHERE id = ?", (tarefa_id,))
        conn.commit()


def deletar_tarefa(tarefa_id):
    """Remove uma tarefa do banco pelo ID."""
    with conectar() as conn:
        conn.execute("DELETE FROM tarefas WHERE id = ?", (tarefa_id,))
        conn.commit()


# ---------- Teste manual / utilitário CLI ----------
if __name__ == "__main__":
    criar_tabela()
    print("Banco de dados SQLite pronto em:", DB_PATH)

    horario_agora = datetime.now().strftime("%Y-%m-%d %H:%M")
    tid = adicionar_tarefa("Lembrete Imediato", "Esta é uma tarefa de demonstração da Persona!", horario_agora)
    print(f"Tarefa de teste #{tid} criada para AGORA: {horario_agora}")

    print("\n--- Tarefas Pendentes ---")
    for t in listar_tarefas_pendentes():
        print(f"[{t['id']}] {t['titulo']} — {t['horario_lembrete']} (concluído: {t['concluido']})")