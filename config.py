import os
import sys

# ============ CAMINHOS (Compatível com PyInstaller) ============
def get_base_dir():
    """
    Retorna a pasta base dos recursos (imagens, sprites).
    Quando empacotado em .exe (PyInstaller --onefile), os recursos
    são extraídos na pasta temporária apontada por sys._MEIPASS.
    Em modo desenvolvimento, usa a pasta deste arquivo.
    """
    if getattr(sys, "frozen", False):
        return getattr(sys, "_MEIPASS", os.path.dirname(sys.executable))
    return os.path.dirname(os.path.abspath(__file__))


def get_data_dir():
    """
    Retorna a pasta onde dados persistentes (como tarefas.db) devem ser salvos.
    Nunca deve apontar para sys._MEIPASS (que é efêmero e apagado ao fechar).
    """
    if getattr(sys, "frozen", False):
        return os.path.dirname(sys.executable)
    return os.path.dirname(os.path.abspath(__file__))


BASE_DIR = get_base_dir()
DATA_DIR = get_data_dir()

PASTA_IMAGENS = os.path.join(BASE_DIR, "imagens")
PASTA_PERSONA = os.path.join(PASTA_IMAGENS, "persona")
DB_PATH = os.path.join(DATA_DIR, "tarefas.db")

# ============ PARÂMETROS VISUAIS E DE ANIMAÇÃO ============
ESCALA = 2.0                 # 2.0 => dobra o tamanho dos frames (pixel art LPC)

INTERVALO_IDLE_MS = 500      # Troca de frame do idle (2 frames)
INTERVALO_WALK_MS = 120      # Troca de frame do walk (9 frames)
INTERVALO_SIT_MS = 250       # Troca de frame do sit (3 frames, não-loop)
INTERVALO_EMOTE_MS = 350     # Troca de frame do emote (3 frames)
INTERVALO_HURT_MS = 220      # Troca de frame do hurt (6 frames, levantar)

DURACAO_QUEDA_MS = 400       # Duração da queda até a barra de tarefas
VELOCIDADE_ANDAR_PX_S = 50   # Velocidade horizontal ao andar autonomamente
INTERVALO_DECISAO_MS = 8000  # A cada 8s a Anais decide uma ação autônoma
LIMIAR_TOPO = 0.5            # Soltar na metade superior da tela dispara queda
INTERVALO_VERIFICADOR_MS = 2000   # Verificação do banco a cada 2 segundos (resposta imediata)


