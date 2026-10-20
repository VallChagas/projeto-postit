import random
from PyQt5.QtWidgets import (
    QApplication,
    QWidget,
    QLabel,
    QMenu,
    QAction,
    QVBoxLayout,
    QHBoxLayout,
    QPushButton,
    QGraphicsDropShadowEffect,
)
from PyQt5.QtCore import Qt, QPoint, QTimer, pyqtSignal
from PyQt5.QtGui import QColor, QFont

from config import (
    ESCALA,
    INTERVALO_IDLE_MS,
    INTERVALO_WALK_MS,
    INTERVALO_SIT_MS,
    INTERVALO_EMOTE_MS,
    INTERVALO_HURT_MS,
    DURACAO_QUEDA_MS,
    VELOCIDADE_ANDAR_PX_S,
    INTERVALO_DECISAO_MS,
    LIMIAR_TOPO,
)
import animacao
import db


class JanelaPostIt(QWidget):
    """
    Janela flutuante no estilo Post-it com design moderno, sem bordas,
    sempre no topo, que exibe o lembrete disparado e permite concluí-lo.
    """

    def __init__(self, tarefa, parent=None, posicao_alvo=None):
        super().__init__(parent)
        self.tarefa = tarefa

        self.setWindowFlags(
            Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint | Qt.Tool
        )
        self.setAttribute(Qt.WA_TranslucentBackground)

        self.arrastando = False
        self.offset = QPoint()

        self.init_ui()

        if posicao_alvo:
            self.posicionar_proximo(posicao_alvo)

    def init_ui(self):
        # Container principal com estilo de post-it amarelo suave
        self.container = QWidget(self)
        self.container.setStyleSheet("""
            QWidget {
                background-color: #FEF08A;
                border: 1px solid #FACC15;
                border-radius: 10px;
            }
        """)

        # Efeito de sombra elegante
        sombra = QGraphicsDropShadowEffect(self)
        sombra.setBlurRadius(18)
        sombra.setColor(QColor(0, 0, 0, 80))
        sombra.setOffset(2, 4)
        self.container.setGraphicsEffect(sombra)

        layout_conteudo = QVBoxLayout(self.container)
        layout_conteudo.setContentsMargins(14, 12, 14, 12)
        layout_conteudo.setSpacing(8)

        # Cabeçalho com ícone, horário e botão fechar
        layout_topo = QHBoxLayout()
        layout_topo.setSpacing(6)

        label_icone = QLabel("📌 Lembrete", self.container)
        label_icone.setStyleSheet("color: #854D0E; font-weight: bold; font-size: 11px; border: none;")

        horario = self.tarefa.get("horario_lembrete", "")
        label_hora = QLabel(horario, self.container)
        label_hora.setStyleSheet("color: #A16207; font-size: 10px; border: none;")

        btn_fechar = QPushButton("✕", self.container)
        btn_fechar.setFixedSize(20, 20)
        btn_fechar.setCursor(Qt.PointingHandCursor)
        btn_fechar.setStyleSheet("""
            QPushButton {
                background: transparent;
                color: #854D0E;
                font-weight: bold;
                border: none;
                font-size: 11px;
                border-radius: 10px;
            }
            QPushButton:hover {
                background: #FDE047;
                color: #713F12;
            }
        """)
        btn_fechar.clicked.connect(self.close)

        layout_topo.addWidget(label_icone)
        layout_topo.addWidget(label_hora)
        layout_topo.addStretch()
        layout_topo.addWidget(btn_fechar)
        layout_conteudo.addLayout(layout_topo)

        # Título da tarefa
        label_titulo = QLabel(self.tarefa.get("titulo", "Tarefa"), self.container)
        label_titulo.setWordWrap(True)
        label_titulo.setStyleSheet("color: #1C1917; font-weight: bold; font-size: 13px; border: none;")
        layout_conteudo.addWidget(label_titulo)

        # Descrição da tarefa (se houver)
        descricao = self.tarefa.get("descricao")
        if descricao:
            label_desc = QLabel(descricao, self.container)
            label_desc.setWordWrap(True)
            label_desc.setStyleSheet("color: #44403C; font-size: 11px; border: none;")
            layout_conteudo.addWidget(label_desc)

        # Botão de Ação: Concluir
        layout_rodape = QHBoxLayout()
        layout_rodape.addStretch()

        btn_concluir = QPushButton("✓ Concluir", self.container)
        btn_concluir.setCursor(Qt.PointingHandCursor)
        btn_concluir.setStyleSheet("""
            QPushButton {
                background-color: #15803D;
                color: white;
                font-weight: bold;
                font-size: 11px;
                padding: 4px 10px;
                border: none;
                border-radius: 6px;
            }
            QPushButton:hover {
                background-color: #16A34A;
            }
            QPushButton:pressed {
                background-color: #166534;
            }
        """)
        btn_concluir.clicked.connect(self.concluir_tarefa)
        layout_rodape.addWidget(btn_concluir)
        layout_conteudo.addLayout(layout_rodape)

        # Layout da janela com padding para acomodar a sombra
        layout_raiz = QVBoxLayout(self)
        layout_raiz.setContentsMargins(10, 10, 10, 10)
        layout_raiz.addWidget(self.container)

        self.setFixedWidth(240)
        self.adjustSize()

    def posicionar_proximo(self, pos_avatar):
        """Posiciona o post-it à esquerda ou acima da Persona sem sair da tela."""
        tela = QApplication.primaryScreen().availableGeometry()
        x = pos_avatar.x() - self.width() + 20
        y = pos_avatar.y() - self.height() + 30

        # Se sair pela esquerda, joga para a direita
        if x < tela.left() + 10:
            x = pos_avatar.x() + 90
        # Se sair pelo topo, ajusta para dentro
        if y < tela.top() + 10:
            y = tela.top() + 20

        self.move(x, y)

    def concluir_tarefa(self):
        tarefa_id = self.tarefa.get("id")
        if tarefa_id:
            db.marcar_concluida(tarefa_id)
        self.close()

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.arrastando = True
            self.offset = event.globalPos() - self.frameGeometry().topLeft()
            event.accept()

    def mouseMoveEvent(self, event):
        if self.arrastando and event.buttons() & Qt.LeftButton:
            self.move(event.globalPos() - self.offset)
            event.accept()

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.arrastando = False
            event.accept()


class JanelaAvatar(QWidget):
    """
    Janela transparente e interativa da personagem Persona.
    Contém sistema de estados de animação, arrastar/soltar com física de queda,
    comportamento autônomo na barra de tarefas e exibição de lembretes.
    """

    abrir_agenda_solicitada = pyqtSignal()

    def __init__(self):
        super().__init__()

        self.setWindowFlags(
            Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint | Qt.Tool
        )
        self.setAttribute(Qt.WA_TranslucentBackground)

        # Carrega todos os frames escalonados do LPC
        self.frames = animacao.carregar_todas()

        if not self.frames.get("idle", {}).get("down"):
            raise FileNotFoundError("Não foi possível carregar os sprites básicos da Persona.")

        self.label = QLabel(self)
        self.label.setAlignment(Qt.AlignCenter)

        # Estado da animação
        self.animacao_atual = "idle"
        self.direcao_atual = "down"
        self.frame_index = 0
        self.em_loop = True

        # Timers principais
        self.timer_animacao = QTimer(self)
        self.timer_animacao.timeout.connect(self.proximo_frame)

        self.timer_andar = QTimer(self)
        self.timer_andar.timeout.connect(self.passo_caminhada)

        self.timer_queda = QTimer(self)
        self.timer_queda.timeout.connect(self.passo_de_queda)

        self.timer_decisao = QTimer(self)
        self.timer_decisao.timeout.connect(self.decidir_acao_autonoma)

        # Controle de Arraste e Clique
        self.arrastando = False
        self.pos_pressionada = QPoint()
        self.offset = QPoint()
        self.caindo = False

        # Variáveis de movimento autônomo
        self.andando_autonomo = False
        self.direcao_caminhada = 1  # 1 = direita, -1 = esquerda
        self.passos_restantes_andar = 0

        # Lista de janelas de post-its ativas para não sofrerem garbage collection
        self.postits_ativos = []

        # Inicia idle virada para frente
        self.tocar("idle", "down", loop=True)

        # Posiciona inicialmente no canto inferior direito da tela
        tela = QApplication.primaryScreen().availableGeometry()
        self.move(
            tela.right() - self.width() - 40,
            tela.bottom() - self.height() - 60,
        )

        # Ativa o ciclo autônomo da Persona
        self.timer_decisao.start(INTERVALO_DECISAO_MS)

    # ---------- Controle de Animação ----------
    def frames_atuais(self):
        return self.frames.get(self.animacao_atual, {}).get(self.direcao_atual, [])

    def tocar(self, animacao_nome, direcao="down", loop=True, intervalo_ms=None):
        """Inicia uma animação com direção e intervalo especificados."""
        direcoes = self.frames.get(animacao_nome, {})
        if not direcoes.get(direcao):
            if direcoes.get("down"):
                direcao = "down"
            else:
                for d, fs in direcoes.items():
                    if fs:
                        direcao = d
                        break
                else:
                    return

        self.animacao_atual = animacao_nome
        self.direcao_atual = direcao
        self.frame_index = 0
        self.em_loop = loop

        if intervalo_ms is None:
            intervalo_ms = {
                "idle": INTERVALO_IDLE_MS,
                "walk": INTERVALO_WALK_MS,
                "sit": INTERVALO_SIT_MS,
                "emote": INTERVALO_EMOTE_MS,
                "hurt": INTERVALO_HURT_MS,
            }.get(animacao_nome, INTERVALO_IDLE_MS)

        self.timer_animacao.start(intervalo_ms)
        self.mostrar_frame_atual()

    def fixar_frame(self, animacao_nome, direcao, frame_idx):
        """Fixa um frame estático específico (usado na pose de queda ou clique)."""
        direcoes = self.frames.get(animacao_nome, {})
        lista = direcoes.get(direcao) or direcoes.get("down") or []
        if not lista:
            return
        self.animacao_atual = animacao_nome
        self.direcao_atual = direcao
        self.frame_index = min(frame_idx, len(lista) - 1)
        self.timer_animacao.stop()
        self.mostrar_frame_atual()

    def mostrar_frame_atual(self):
        lista = self.frames_atuais()
        if not lista:
            return
        pix = lista[self.frame_index % len(lista)]
        self.label.setPixmap(pix)
        self.label.resize(pix.size())
        self.resize(pix.size())

    def proximo_frame(self):
        lista = self.frames_atuais()
        if not lista:
            return

        self.frame_index += 1

        if self.frame_index >= len(lista):
            if self.em_loop:
                self.frame_index = 0
            else:
                # Animação de tiro único terminou
                self.frame_index = len(lista) - 1
                self.timer_animacao.stop()
                self.ao_terminar_animacao()
                return

        self.mostrar_frame_atual()

    def ao_terminar_animacao(self):
        """Transições após terminar animações sem loop."""
        if self.animacao_atual == "sit":
            # Requisito: 'sit' NÃO deve repetir em loop; fica no último frame
            pass
        elif self.animacao_atual == "hurt":
            # Ao levantar do tombo, volta ao idle
            self.tocar("idle", "down", loop=True)
        elif self.animacao_atual == "emote":
            # Emote temporário (ex: reação de clique ou lembrete) volta para idle
            self.tocar("idle", self.direcao_atual, loop=True)
        else:
            self.tocar("idle", self.direcao_atual, loop=True)

    # ---------- Comportamento Autônomo ----------
    def parar_movimento_autonomo(self):
        """Interrompe qualquer caminhada ou rotina autônoma em andamento."""
        self.andando_autonomo = False
        self.timer_andar.stop()

    def decidir_acao_autonoma(self):
        """Decide a cada intervalo se a Persona anda, senta ou fica em idle."""
        if self.arrastando or self.caindo:
            return

        # Só toma decisões autônomas se estiver no chão em estado ocioso
        if self.animacao_atual not in ("idle", "sit"):
            return

        tela = QApplication.primaryScreen().availableGeometry()
        sorteio = random.random()

        if sorteio < 0.45:
            # 45% de chance: Andar pela barra de tarefas
            self.iniciar_caminhada_autonoma()
        elif sorteio < 0.70:
            # 25% de chance: Sentar
            if self.animacao_atual != "sit":
                self.tocar("sit", "down", loop=False)
        else:
            # 30% de chance: Ficar em Idle virando para algum lado
            direcao_olhar = random.choice(["down", "left", "right"])
            self.tocar("idle", direcao_olhar, loop=True)

    def iniciar_caminhada_autonoma(self):
        tela = QApplication.primaryScreen().availableGeometry()
        largura = self.width()

        # Decide direção priorizando não sair da tela
        if self.x() <= tela.left() + 40:
            self.direcao_caminhada = 1  # Direita
        elif self.x() >= tela.right() - largura - 40:
            self.direcao_caminhada = -1  # Esquerda
        else:
            self.direcao_caminhada = random.choice([-1, 1])

        direcao_str = "right" if self.direcao_caminhada == 1 else "left"
        self.tocar("walk", direcao_str, loop=True)

        duracao_segundos = random.uniform(2.5, 5.0)
        self.passos_restantes_andar = int(duracao_segundos * 30)  # ~30 ticks por segundo
        self.andando_autonomo = True
        self.timer_andar.start(33)  # ~30 FPS

    def passo_caminhada(self):
        if not self.andando_autonomo:
            self.timer_andar.stop()
            return

        tela = QApplication.primaryScreen().availableGeometry()
        deslocamento = (VELOCIDADE_ANDAR_PX_S / 30.0) * self.direcao_caminhada
        novo_x = int(self.x() + deslocamento)

        # Respeita limites horizontais da tela
        limite_esq = tela.left()
        limite_dir = tela.right() - self.width()

        if novo_x <= limite_esq:
            novo_x = limite_esq
            self.passos_restantes_andar = 0
        elif novo_x >= limite_dir:
            novo_x = limite_dir
            self.passos_restantes_andar = 0

        self.move(novo_x, self.y())
        self.passos_restantes_andar -= 1

        if self.passos_restantes_andar <= 0:
            self.parar_movimento_autonomo()
            self.tocar("idle", "down", loop=True)

    # ---------- Queda até a barra de tarefas ----------
    def iniciar_queda(self):
        """Inicia animação suave de queda (~60 FPS) até o rodapé da tela."""
        self.parar_movimento_autonomo()
        self.caindo = True

        tela = QApplication.primaryScreen().availableGeometry()
        self.y_inicial = self.y()
        self.y_final = tela.bottom() - self.height()  # Encosta na barra

        self.passo_queda = 0
        self.total_passos_queda = max(1, DURACAO_QUEDA_MS // 16)  # ~60 FPS

        self.timer_queda.start(16)

    def passo_de_queda(self):
        self.passo_queda += 1
        progresso = min(1.0, self.passo_queda / self.total_passos_queda)
        novo_y = int(self.y_inicial + (self.y_final - self.y_inicial) * progresso)
        self.move(self.x(), novo_y)

        if progresso >= 1.0:
            self.timer_queda.stop()
            self.caindo = False
            # Ao bater no chão: toca animação hurt/down (levantar)
            self.tocar("hurt", "down", loop=False, intervalo_ms=INTERVALO_HURT_MS)

    # ---------- Interações de Mouse (Clique vs Arraste) ----------
    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton and not self.caindo:
            self.parar_movimento_autonomo()
            self.pos_pressionada = event.globalPos()
            self.arrastando = False
            self.offset = event.globalPos() - self.frameGeometry().topLeft()
            event.accept()

    def mouseMoveEvent(self, event):
        if event.buttons() & Qt.LeftButton and not self.caindo:
            # Distingue clique de arraste: se moveu mais de 6px, passa a ser arraste
            if (event.globalPos() - self.pos_pressionada).manhattanLength() > 6:
                if not self.arrastando:
                    self.arrastando = True
                    self.timer_animacao.stop()
                self.move(event.globalPos() - self.offset)
            event.accept()

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.LeftButton and not self.caindo:
            if not self.arrastando:
                # Interação de CLIQUE simples:
                # Requisito: clique = emote frame 1 (mãos na cintura)
                self.fixar_frame("emote", "down", frame_idx=0)
                # Volta para idle após 1.5 segundos
                QTimer.singleShot(1500, lambda: self.tocar("idle", "down", loop=True))
            else:
                self.arrastando = False
                self.ao_soltar()
            event.accept()

    def ao_soltar(self):
        tela = QApplication.primaryScreen().availableGeometry()
        # Se soltou na metade superior:
        # Requisito: emote frame 3 (braços pra cima) + queda até a barra de tarefas + hurt/down (levantar)
        if self.y() < tela.top() + int(tela.height() * LIMIAR_TOPO):
            # Fixa pose de susto/queda: emote frame 3 (índice 2)
            self.fixar_frame("emote", "down", frame_idx=2)
            self.iniciar_queda()
        else:
            # Requisito: soltar embaixo = volta ao idle
            self.tocar("idle", "down", loop=True)

    # ---------- Disparo de Lembrete ----------
    def exibir_lembrete(self, tarefa):
        """Reage visualmente ao lembrete e exibe o post-it flutuante."""
        self.parar_movimento_autonomo()

        # Persona reage surpresa/alegre com emote
        self.tocar("emote", "down", loop=False)

        # Abre o Post-it posicionado perto da Persona
        postit = JanelaPostIt(tarefa, parent=None, posicao_alvo=self.pos())
        self.postits_ativos.append(postit)
        postit.show()
        return postit

    # ---------- Menu de Botão Direito ----------
    def contextMenuEvent(self, event):
        self.parar_movimento_autonomo()

        menu = QMenu(self)
        menu.setStyleSheet("""
            QMenu {
                background-color: #262626;
                color: #F5F5F5;
                border: 1px solid #404040;
                border-radius: 6px;
                padding: 4px;
            }
            QMenu::item {
                padding: 6px 20px;
                border-radius: 4px;
            }
            QMenu::item:selected {
                background-color: #3B82F6;
                color: #FFFFFF;
            }
            QMenu::separator {
                height: 1px;
                background: #404040;
                margin: 4px 8px;
            }
        """)

        acao_agenda = QAction("📓 Abrir Agenda", self)
        acao_agenda.triggered.connect(self.abrir_agenda_solicitada.emit)
        menu.addAction(acao_agenda)

        menu.addSeparator()

        acao_idle = QAction("Idle", self)
        acao_idle.triggered.connect(lambda: self.tocar("idle", "down", loop=True))
        menu.addAction(acao_idle)

        acao_walk = QAction("Andar", self)
        acao_walk.triggered.connect(self.iniciar_caminhada_autonoma)
        menu.addAction(acao_walk)

        acao_sit = QAction("Sentar", self)
        acao_sit.triggered.connect(lambda: self.tocar("sit", "down", loop=False))
        menu.addAction(acao_sit)

        acao_emote = QAction("Emote", self)
        acao_emote.triggered.connect(lambda: self.tocar("emote", "down", loop=False))
        menu.addAction(acao_emote)

        acao_hurt = QAction("Hurt (Levantar)", self)
        acao_hurt.triggered.connect(lambda: self.tocar("hurt", "down", loop=False))
        menu.addAction(acao_hurt)

        menu.addSeparator()

        acao_sair = QAction("Sair", self)
        acao_sair.triggered.connect(QApplication.quit)
        menu.addAction(acao_sair)

        menu.exec_(event.globalPos())