# 🐾 Persona Desktop Pet & Lembretes

Pet de desktop offline baseado na personagem Persona (estilo LPC), com animações autônomas na barra de tarefas, reações a interações do usuário e lembretes com post-its flutuantes integrados ao SQLite.

---

## 🚀 Como Rodar o Projeto

### Pré-requisitos
- Python 3.8+
- PyQt5 instalado:
  ```bash
  pip install PyQt5
  ```

### Executar
Na pasta do projeto, execute:
```bash
python main.py
```

---

## 📝 Como Adicionar Tarefas e Lembretes

### Opção 1: Via script de teste do banco (`db.py`)
Para adicionar uma tarefa rápida para daqui a 1 minuto (ideal para testar o popup):
```bash
python db.py
```

### Opção 2: Via linha de comando interativa (Python)
Abra o Python no terminal da pasta do projeto:
```python
import db

# Formato de data/hora obrigatório: 'YYYY-MM-DD HH:MM'
db.adicionar_tarefa(
    titulo="Beber Água",
    descricao="Hora de tomar um copo de água e esticar as pernas!",
    horario_lembrete="2026-10-20 15:30"
)
```

---

## 🎮 Interações da Persona

- **Clique simples**: Persona faz a pose com mãos na cintura (emote frame 1) e volta ao idle.
- **Arrastar e soltar na metade inferior**: Volta suavemente ao modo idle.
- **Arrastar e soltar na metade superior**: Persona levanta os braços (emote frame 3), cai até a barra de tarefas e toca a animação de se levantar (`hurt`).
- **Autonomia**: De tempos em tempos, Persona anda de um lado para o outro na barra de tarefas ou senta para descansar.
- **Botão Direito**: Abre o menu de controle com opção para abrir a **📓 Minha Agenda**, animações manuais (`Idle`, `Andar`, `Sentar`, `Emote`, `Hurt`) e `Sair`.
- **📓 Minha Agenda**: Caderninho de tarefas com filtros ("Recentes", "Próximas", "Todas", "Concluídas"), criação com diálogo visual, edição, conclusão e exclusão.
- **Post-It Flutuante (Lembrete Instantâneo)**: No horário agendado, um post-it amarelo surge próximo à Persona com opções de **✓ Concluir** e **✕ Fechar**.



---

## 📦 Como Empacotar com PyInstaller (.exe)

O projeto foi estruturado com caminhos relativos compatíveis com `sys._MEIPASS`, garantindo que imagens e banco funcionem no executável.

1. Instale o PyInstaller:
   ```bash
   pip install pyinstaller
   ```

2. Execute o comando exato no Windows:
   ```bash
   pyinstaller --noconsole --onefile --name "PersonaPet" --add-data "imagens;imagens" main.py
   ```

O executável independente estará disponível na pasta `dist/PersonaPet.exe`. Ao rodar, o arquivo persistente `tarefas.db` será criado na mesma pasta do executável.
