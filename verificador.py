import sys
from datetime import datetime
from PyQt5.QtCore import QObject, QTimer, pyqtSignal, QCoreApplication
from config import INTERVALO_VERIFICADOR_MS
import db


class VerificadorLembretes(QObject):
    """
    Monitora tarefas no SQLite a cada INTERVALO_VERIFICADOR_MS (30s)
    e emite o sinal lembrete_disparado com os dados da tarefa quando
    o horário do lembrete for atingido.
    """
    lembrete_disparado = pyqtSignal(dict)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.verificar)
        self.disparados = set()

    def iniciar(self):
        """Inicia o timer de verificação e roda uma checagem imediata."""
        self.timer.start(INTERVALO_VERIFICADOR_MS)
        self.verificar()

    def parar(self):
        """Pausa o timer de verificação."""
        self.timer.stop()

    def verificar(self):
        """Consulta as tarefas pendentes no banco e emite sinal para as devidas."""
        agora = datetime.now().strftime("%Y-%m-%d %H:%M")
        pendentes = db.listar_tarefas_pendentes()

        for t in pendentes:
            tarefa_dict = dict(t)
            tarefa_id = tarefa_dict["id"]
            horario = tarefa_dict["horario_lembrete"]

            # Dispara quando o horário for atingido (ou já passou e ainda está pendente)
            if horario <= agora:
                if tarefa_id in self.disparados:
                    continue
                self.disparados.add(tarefa_id)
                self.lembrete_disparado.emit(tarefa_dict)


if __name__ == "__main__":
    app = QCoreApplication(sys.argv)
    db.criar_tabela()

    verificador = VerificadorLembretes()

    def ao_disparar(tarefa):
        print(f"\n🔔 LEMBRETE DISPARADO: [{tarefa['id']}] {tarefa['titulo']}")
        print(f"   Descrição: {tarefa['descricao']}")
        print(f"   Horário: {tarefa['horario_lembrete']}")

    verificador.lembrete_disparado.connect(ao_disparar)
    verificador.iniciar()
    print("Verificador iniciado em background com QTimer. Aguardando lembretes...")
    sys.exit(app.exec_())