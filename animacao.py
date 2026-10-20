import os
from PyQt5.QtGui import QPixmap
from PyQt5.QtCore import Qt
from config import PASTA_PERSONA, ESCALA


def carregar_frames(animacao, direcao):
    """
    Carrega todos os PNGs de imagens/persona/<animacao>/<direcao>/
    ordenados numericamente pelo nome do arquivo (1.png, 2.png, ...).
    Retorna lista de QPixmap escalonados para pixel art limpo.
    """
    pasta = os.path.join(PASTA_PERSONA, animacao, direcao)

    # Tolerância/fallback para 'hurt': aceita tanto 'down' quanto 'up'
    if not os.path.isdir(pasta) and animacao == "hurt":
        direcao_alternativa = "up" if direcao == "down" else "down"
        pasta_alt = os.path.join(PASTA_PERSONA, animacao, direcao_alternativa)
        if os.path.isdir(pasta_alt):
            pasta = pasta_alt

    if not os.path.isdir(pasta):
        return []

    arquivos = [f for f in os.listdir(pasta) if f.lower().endswith(".png")]

    def chave_numerica(nome):
        base = os.path.splitext(nome)[0]
        try:
            return int(base)
        except ValueError:
            return 9999

    arquivos.sort(key=chave_numerica)

    frames = []
    for nome in arquivos:
        caminho = os.path.join(pasta, nome)
        pix = QPixmap(caminho)
        if not pix.isNull():
            largura = int(pix.width() * ESCALA)
            altura = int(pix.height() * ESCALA)
            # FastTransformation preserva o aspecto nítido de pixel art
            pix = pix.scaled(largura, altura, Qt.KeepAspectRatio, Qt.FastTransformation)
            frames.append(pix)

    return frames


def carregar_todas():
    """
    Carrega e retorna um dicionário contendo todas as animações e direções suportadas.
    Garante que hurt esteja disponível tanto em 'down' quanto em 'up'.
    """
    direcoes = ["down", "left", "right", "up"]

    todas = {
        "idle": {d: carregar_frames("idle", d) for d in direcoes},
        "walk": {
            "left": carregar_frames("walk", "left"),
            "right": carregar_frames("walk", "right"),
            # Walk não tem frente/costas nos sprites, usa left/right como fallback
            "down": carregar_frames("walk", "right"),
            "up": carregar_frames("walk", "left"),
        },
        "sit": {d: carregar_frames("sit", d) for d in direcoes},
        "emote": {d: carregar_frames("emote", d) for d in direcoes},
        "hurt": {
            "down": carregar_frames("hurt", "down"),
            "up": carregar_frames("hurt", "up"),
        },
    }

    # Assegura que 'hurt' tenha frames em ambas as direções
    frames_hurt = todas["hurt"]["down"] or todas["hurt"]["up"]
    if frames_hurt:
        todas["hurt"]["down"] = frames_hurt
        todas["hurt"]["up"] = frames_hurt

    return todas
