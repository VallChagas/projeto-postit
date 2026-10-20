import sys
from datetime import datetime, timedelta
from PyQt5.QtWidgets import (
    QWidget,
    QDialog,
    QLabel,
    QLineEdit,
    QTextEdit,
    QDateTimeEdit,
    QPushButton,
    QVBoxLayout,
    QHBoxLayout,
    QScrollArea,
    QButtonGroup,
    QMessageBox,
    QFrame,
    QGraphicsDropShadowEffect,
)
from PyQt5.QtCore import Qt, QDateTime, pyqtSignal
from PyQt5.QtGui import QColor, QFont

import db


def formatar_horario_amigavel(horario_str):
    """Formata o horário de forma amigável (Hoje, Amanhã, Ontem ou DD/MM HH:MM)."""
    try:
        dt = datetime.strptime(horario_str, "%Y-%m-%d %H:%M")
        hoje = datetime.now().date()
        data_tarefa = dt.date()
        hora_str = dt.strftime("%H:%M")

        if data_tarefa == hoje:
            return f"Hoje {hora_str}"
        elif data_tarefa == hoje + timedelta(days=1):
            return f"Amanhã {hora_str}"
        elif data_tarefa == hoje - timedelta(days=1):
            return f"Ontem {hora_str}"
        else:
            return dt.strftime("%d/%m %H:%M")
    except Exception:
        return horario_str


class DialogTarefa(QDialog):
    """Diálogo modal para criação e edição de tarefas."""

    def __init__(self, parent=None, tarefa=None):
        super().__init__(parent)
        self.tarefa = tarefa
        self.setWindowTitle("Editar Tarefa" if tarefa else "Nova Tarefa")
        self.setFixedWidth(360)
        self.setStyleSheet("""
            QDialog {
                background-color: #FEF9E7;
                border: 1px solid #E7E5E4;
            }
            QLabel {
                color: #451A03;
                font-size: 12px;
                font-weight: bold;
            }
            QLineEdit, QTextEdit, QDateTimeEdit {
                background-color: #FFFFFF;
                border: 1px solid #D6D3D1;
                border-radius: 6px;
                padding: 6px;
                color: #1C1917;
                font-size: 12px;
            }
            QLineEdit:focus, QTextEdit:focus, QDateTimeEdit:focus {
                border: 1px solid #F59E0B;
            }
            QPushButton {
                border-radius: 6px;
                padding: 6px 14px;
                font-weight: bold;
                font-size: 12px;
            }
        """)

        layout = QVBoxLayout(self)
        layout.setSpacing(10)
        layout.setContentsMargins(18, 18, 18, 18)

        # Campo Título
        layout.addWidget(QLabel("Título (obrigatório):"))
        self.input_titulo = QLineEdit(self)
        self.input_titulo.setPlaceholderText("Ex: Reunião de alinhamento")
        if tarefa:
            self.input_titulo.setText(tarefa["titulo"])
        layout.addWidget(self.input_titulo)

        # Campo Descrição
        layout.addWidget(QLabel("Descrição (opcional):"))
        self.input_desc = QTextEdit(self)
        self.input_desc.setFixedHeight(75)
        self.input_desc.setPlaceholderText("Detalhes ou anotações...")
        if tarefa and tarefa["descricao"]:
            self.input_desc.setPlainText(tarefa["descricao"])
        layout.addWidget(self.input_desc)

        # Campo Data e Hora do Lembrete
        layout.addWidget(QLabel("Data e Horário do Lembrete:"))
        self.input_data = QDateTimeEdit(self)
        self.input_data.setCalendarPopup(True)
        self.input_data.setDisplayFormat("yyyy-MM-dd HH:mm")

        if tarefa:
            try:
                dt = datetime.strptime(tarefa["horario_lembrete"], "%Y-%m-%d %H:%M")
                self.input_data.setDateTime(QDateTime(dt.year, dt.month, dt.day, dt.hour, dt.minute))
            except Exception:
                self.input_data.setDateTime(QDateTime.currentDateTime().addSecs(3600))
        else:
            # Padrão: agora + 1 hora
            self.input_data.setDateTime(QDateTime.currentDateTime().addSecs(3600))

        layout.addWidget(self.input_data)

        # Botões de ação
        layout_botoes = QHBoxLayout()
        layout_botoes.addStretch()

        btn_cancelar = QPushButton("Cancelar", self)
        btn_cancelar.setStyleSheet("""
            QPushButton {
                background-color: #E7E5E4;
                color: #44403C;
                border: none;
            }
            QPushButton:hover {
                background-color: #D6D3D1;
            }
        """)
        btn_cancelar.clicked.connect(self.reject)
        layout_botoes.addWidget(btn_cancelar)

        btn_salvar = QPushButton("Salvar", self)
        btn_salvar.setStyleSheet("""
            QPushButton {
                background-color: #15803D;
                color: #FFFFFF;
                border: none;
            }
            QPushButton:hover {
                background-color: #16A34A;
            }
            QPushButton:pressed {
                background-color: #166534;
            }
        """)
        btn_salvar.clicked.connect(self.validar_e_salvar)
        layout_botoes.addWidget(btn_salvar)

        layout.addLayout(layout_botoes)

    def validar_e_salvar(self):
        """Valida que o título foi preenchido antes de fechar."""
        if not self.input_titulo.text().strip():
            QMessageBox.warning(self, "Aviso", "O título da tarefa é obrigatório.")
            self.input_titulo.setFocus()
            return
        self.accept()

    def obter_dados(self):
        """Retorna os dados limpos preenchidos no diálogo."""
        titulo = self.input_titulo.text().strip()
        descricao = self.input_desc.toPlainText().strip()
        dt = self.input_data.dateTime().toPyDateTime()
        horario = dt.strftime("%Y-%m-%d %H:%M")
        return titulo, descricao, horario


class JanelaAgenda(QWidget):
    """
    Janela de gerenciamento de tarefas no estilo caderno ('📓 Minha Agenda').
    Permite visualizar, filtrar, criar, editar, concluir e excluir tarefas.
    """

    tarefa_alterada = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.filtro_atual = "Recentes"

        self.setWindowTitle("📓 Minha Agenda")
        self.resize(430, 580)
        self.setMinimumSize(380, 480)

        self.init_ui()
        self.carregar_tarefas()

    def init_ui(self):
        # Estilo geral do caderninho
        self.setStyleSheet("""
            QWidget#caderno {
                background-color: #FEF9E7;
            }
        """)
        self.setObjectName("caderno")

        layout_principal = QVBoxLayout(self)
        layout_principal.setContentsMargins(16, 16, 16, 16)
        layout_principal.setSpacing(12)

        # Cabeçalho com Título e Botão "+ Nova tarefa"
        layout_cabecalho = QHBoxLayout()

        label_titulo = QLabel("📓 Minha Agenda", self)
        label_titulo.setStyleSheet("""
            font-size: 19px;
            font-weight: bold;
            color: #78350F;
        """)
        layout_cabecalho.addWidget(label_titulo)
        layout_cabecalho.addStretch()

        btn_nova = QPushButton("+ Nova tarefa", self)
        btn_nova.setCursor(Qt.PointingHandCursor)
        btn_nova.setStyleSheet("""
            QPushButton {
                background-color: #15803D;
                color: #FFFFFF;
                font-weight: bold;
                font-size: 12px;
                padding: 6px 14px;
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
        btn_nova.clicked.connect(self.abrir_dialogo_nova_tarefa)
        layout_cabecalho.addWidget(btn_nova)
        layout_principal.addLayout(layout_cabecalho)

        # Linha de Filtros (Recentes, Próximas, Todas, Concluídas)
        layout_filtros = QHBoxLayout()
        layout_filtros.setSpacing(6)

        self.grupo_filtros = QButtonGroup(self)
        self.grupo_filtros.setExclusive(True)

        filtros = ["Recentes", "Próximas", "Todas", "Concluídas"]
        self.botoes_filtros = {}

        for nome in filtros:
            btn = QPushButton(nome, self)
            btn.setCheckable(True)
            btn.setCursor(Qt.PointingHandCursor)
            btn.setStyleSheet("""
                QPushButton {
                    background-color: #FDFBF7;
                    color: #57534E;
                    border: 1px solid #D6D3D1;
                    border-radius: 12px;
                    padding: 4px 10px;
                    font-size: 11px;
                    font-weight: bold;
                }
                QPushButton:hover {
                    background-color: #FEF3C7;
                    color: #78350F;
                }
                QPushButton:checked {
                    background-color: #FDE047;
                    color: #713F12;
                    border: 1px solid #EAB308;
                }
            """)
            if nome == self.filtro_atual:
                btn.setChecked(True)

            btn.clicked.connect(lambda _, n=nome: self.mudar_filtro(n))
            self.grupo_filtros.addButton(btn)
            self.botoes_filtros[nome] = btn
            layout_filtros.addWidget(btn)

        layout_filtros.addStretch()
        layout_principal.addLayout(layout_filtros)

        # Divisor sutil
        linha_divisoria = QFrame(self)
        linha_divisoria.setFrameShape(QFrame.HLine)
        linha_divisoria.setStyleSheet("color: #E7E5E4; background-color: #E7E5E4; height: 1px;")
        layout_principal.addWidget(linha_divisoria)

        # Área de conteúdo com margem vermelha sutil de caderno à esquerda
        layout_caderno_conteudo = QHBoxLayout()
        layout_caderno_conteudo.setSpacing(8)

        # Margem avermelhada sutil à esquerda (linha de caderno escolar)
        linha_margem_caderno = QFrame(self)
        linha_margem_caderno.setFrameShape(QFrame.VLine)
        linha_margem_caderno.setStyleSheet("color: #FCA5A5; background-color: #FCA5A5; width: 2px;")
        layout_caderno_conteudo.addWidget(linha_margem_caderno)

        # Scroll Area rolável para os cartões de tarefas
        self.scroll = QScrollArea(self)
        self.scroll.setWidgetResizable(True)
        self.scroll.setFrameShape(QFrame.NoFrame)
        self.scroll.setStyleSheet("""
            QScrollArea {
                background: transparent;
                border: none;
            }
            QScrollBar:vertical {
                border: none;
                background: #FDFBF7;
                width: 7px;
                border-radius: 3px;
            }
            QScrollBar::handle:vertical {
                background: #D6D3D1;
                border-radius: 3px;
            }
            QScrollBar::handle:vertical:hover {
                background: #A8A29E;
            }
        """)

        self.container_cards = QWidget()
        self.container_cards.setStyleSheet("background: transparent;")
        self.layout_cards = QVBoxLayout(self.container_cards)
        self.layout_cards.setContentsMargins(6, 4, 6, 4)
        self.layout_cards.setSpacing(8)
        self.layout_cards.addStretch()

        self.scroll.setWidget(self.container_cards)
        layout_caderno_conteudo.addWidget(self.scroll)
        layout_principal.addLayout(layout_caderno_conteudo)

    def mudar_filtro(self, novo_filtro):
        """Altera a categoria de filtro selecionada e recarrega os cartões."""
        self.filtro_atual = novo_filtro
        self.carregar_tarefas()

    def focusInEvent(self, event):
        """Recarrega as tarefas automaticamente quando a janela ganhar foco."""
        super().focusInEvent(event)
        self.carregar_tarefas()

    def carregar_tarefas(self):
        """Busca as tarefas do SQLite conforme o filtro atual e recria os cartões."""
        # Limpa os cartões anteriores
        while self.layout_cards.count() > 1:
            item = self.layout_cards.takeAt(0)
            widget = item.widget()
            if widget:
                widget.deleteLater()

        # Consulta conforme filtro
        if self.filtro_atual == "Recentes":
            tarefas = db.listar_recentes(limite=15)
        elif self.filtro_atual == "Próximas":
            tarefas = db.listar_proximas()
        elif self.filtro_atual == "Concluídas":
            tarefas = db.listar_concluidas()
        else:  # "Todas"
            tarefas = db.listar_todas()

        if not tarefas:
            label_vazio = QLabel("Nenhuma tarefa nesta categoria.", self.container_cards)
            label_vazio.setAlignment(Qt.AlignCenter)
            label_vazio.setStyleSheet("color: #A8A29E; font-size: 13px; font-style: italic; padding: 40px 0;")
            self.layout_cards.insertWidget(0, label_vazio)
            return

        for idx, t in enumerate(tarefas):
            card = self.criar_card_tarefa(dict(t))
            self.layout_cards.insertWidget(idx, card)

    def criar_card_tarefa(self, tarefa):
        """Cria e formata o widget visual de cartão para uma tarefa."""
        card = QWidget(self.container_cards)
        concluida = bool(tarefa.get("concluido", 0))

        # Estilo do cartão: branco suave, bordas arredondadas e sombra sutil
        card.setStyleSheet("""
            QWidget#cardWidget {
                background-color: #FFFDF5;
                border: 1px solid #E7E5E4;
                border-radius: 8px;
            }
        """)
        card.setObjectName("cardWidget")

        sombra = QGraphicsDropShadowEffect(card)
        sombra.setBlurRadius(8)
        sombra.setColor(QColor(0, 0, 0, 20))
        sombra.setOffset(1, 2)
        card.setGraphicsEffect(sombra)

        layout_card = QHBoxLayout(card)
        layout_card.setContentsMargins(12, 10, 12, 10)
        layout_card.setSpacing(10)

        # Círculo / Ícone de status
        label_status = QLabel(card)
        if concluida:
            label_status.setText("✓")
            label_status.setStyleSheet("color: #15803D; font-size: 16px; font-weight: bold; border: none;")
        else:
            label_status.setText("○")
            label_status.setStyleSheet("color: #D97706; font-size: 16px; font-weight: bold; border: none;")
        layout_card.addWidget(label_status, alignment=Qt.AlignTop)

        # Conteúdo de texto (Título, Descrição, Horário)
        layout_texto = QVBoxLayout()
        layout_texto.setSpacing(4)

        # Título em negrito (riscado se concluída)
        label_titulo = QLabel(card)
        titulo_texto = tarefa.get("titulo", "Sem título")
        if concluida:
            label_titulo.setText(f"<s>{titulo_texto}</s>")
            label_titulo.setStyleSheet("color: #78716C; font-size: 13px; font-weight: bold; border: none;")
        else:
            label_titulo.setText(titulo_texto)
            label_titulo.setStyleSheet("color: #1C1917; font-size: 13px; font-weight: bold; border: none;")
        label_titulo.setWordWrap(True)
        layout_texto.addWidget(label_titulo)

        # Descrição em cinza (se houver)
        descricao = tarefa.get("descricao")
        if descricao:
            label_desc = QLabel(descricao, card)
            label_desc.setWordWrap(True)
            label_desc.setStyleSheet("color: #57534E; font-size: 11px; border: none;")
            layout_texto.addWidget(label_desc)

        # Horário formatado de forma amigável
        horario_raw = tarefa.get("horario_lembrete", "")
        horario_amigavel = formatar_horario_amigavel(horario_raw)
        label_hora = QLabel(f"⏰ {horario_amigavel}", card)
        label_hora.setStyleSheet("color: #854D0E; font-size: 10px; font-weight: bold; border: none;")
        layout_texto.addWidget(label_hora)

        layout_card.addLayout(layout_texto, stretch=1)

        # Botões de ação do cartão (Editar, Concluir, Excluir)
        layout_acoes = QVBoxLayout()
        layout_acoes.setSpacing(4)
        layout_acoes.setAlignment(Qt.AlignTop)

        # Botão Concluir (apenas se pendente)
        if not concluida:
            btn_concluir = QPushButton("Concluir", card)
            btn_concluir.setCursor(Qt.PointingHandCursor)
            btn_concluir.setStyleSheet("""
                QPushButton {
                    background-color: #DCFCE7;
                    color: #15803D;
                    font-size: 10px;
                    font-weight: bold;
                    border: 1px solid #86EFAC;
                    border-radius: 4px;
                    padding: 3px 8px;
                }
                QPushButton:hover {
                    background-color: #BBF7D0;
                }
            """)
            btn_concluir.clicked.connect(lambda _, t_id=tarefa["id"]: self.concluir_tarefa(t_id))
            layout_acoes.addWidget(btn_concluir)

        # Botão Editar
        btn_editar = QPushButton("Editar", card)
        btn_editar.setCursor(Qt.PointingHandCursor)
        btn_editar.setStyleSheet("""
            QPushButton {
                background-color: #F3F4F6;
                color: #374151;
                font-size: 10px;
                font-weight: bold;
                border: 1px solid #D1D5DB;
                border-radius: 4px;
                padding: 3px 8px;
            }
            QPushButton:hover {
                background-color: #E5E7EB;
                color: #1F2937;
            }
        """)
        btn_editar.clicked.connect(lambda _, t=tarefa: self.editar_tarefa(t))
        layout_acoes.addWidget(btn_editar)

        # Botão Excluir
        btn_excluir = QPushButton("Excluir", card)
        btn_excluir.setCursor(Qt.PointingHandCursor)
        btn_excluir.setStyleSheet("""
            QPushButton {
                background-color: #FEE2E2;
                color: #991B1B;
                font-size: 10px;
                font-weight: bold;
                border: 1px solid #FCA5A5;
                border-radius: 4px;
                padding: 3px 8px;
            }
            QPushButton:hover {
                background-color: #FECACA;
            }
        """)
        btn_excluir.clicked.connect(lambda _, t=tarefa: self.excluir_tarefa(t))
        layout_acoes.addWidget(btn_excluir)

        layout_card.addLayout(layout_acoes)
        return card

    # ---------- Ações de gerenciamento de tarefas ----------
    def abrir_dialogo_nova_tarefa(self):
        """Abre o diálogo modal para cadastrar uma nova tarefa."""
        dialog = DialogTarefa(self)
        if dialog.exec_() == QDialog.Accepted:
            titulo, descricao, horario = dialog.obter_dados()
            db.adicionar_tarefa(titulo, descricao, horario)
            self.tarefa_alterada.emit()
            self.carregar_tarefas()

    def editar_tarefa(self, tarefa):
        """Abre o diálogo modal pré-preenchido para editar uma tarefa."""
        dialog = DialogTarefa(self, tarefa=tarefa)
        if dialog.exec_() == QDialog.Accepted:
            titulo, descricao, horario = dialog.obter_dados()
            db.atualizar_tarefa(tarefa["id"], titulo, descricao, horario)
            self.tarefa_alterada.emit()
            self.carregar_tarefas()

    def concluir_tarefa(self, tarefa_id):
        """Marca a tarefa como concluída no banco e recarrega."""
        db.marcar_concluida(tarefa_id)
        self.tarefa_alterada.emit()
        self.carregar_tarefas()

    def excluir_tarefa(self, tarefa):
        """Confirma e deleta uma tarefa do banco SQLite."""
        resposta = QMessageBox.question(
            self,
            "Confirmar Exclusão",
            f"Deseja realmente excluir a tarefa '{tarefa['titulo']}'?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No,
        )
        if resposta == QMessageBox.Yes:
            db.deletar_tarefa(tarefa["id"])
            self.tarefa_alterada.emit()
            self.carregar_tarefas()


# ---------- Teste individual do módulo ----------
if __name__ == "__main__":
    from PyQt5.QtWidgets import QApplication
    app = QApplication(sys.argv)
    db.criar_tabela()
    agenda = JanelaAgenda()
    agenda.show()
    sys.exit(app.exec_())
