import sys
from PyQt5.QtWidgets import QApplication
import db
from avatar import JanelaAvatar
from verificador import VerificadorLembretes
from agenda import JanelaAgenda

# Referência global para manter a instância da agenda ativa
agenda = None


def main():
    global agenda

    # Cria a aplicação Qt
    app = QApplication(sys.argv)

    # Impede que o app encerre quando a agenda ou post-it for fechado
    app.setQuitOnLastWindowClosed(False)

    # Garante que a tabela do SQLite existe
    db.criar_tabela()

    # Cria a janela principal do avatar
    avatar = JanelaAvatar()
    avatar.show()

    # Função para abrir/focar a janela da Agenda
    def abrir_agenda():
        global agenda
        if agenda is None or not agenda.isVisible():
            agenda = JanelaAgenda()
            agenda.show()
        else:
            agenda.raise_()
            agenda.activateWindow()

    # Conecta o sinal emitido pelo menu de contexto da Persona
    avatar.abrir_agenda_solicitada.connect(abrir_agenda)

    # Cria e inicia o verificador de lembretes em background
    verificador = VerificadorLembretes()
    verificador.lembrete_disparado.connect(avatar.exibir_lembrete)
    verificador.iniciar()

    # Inicia o loop de eventos
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
