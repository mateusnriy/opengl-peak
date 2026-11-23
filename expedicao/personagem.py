"""Modelagem hierárquica articulada do escoteiro (torso, membros e cabeça).

Demonstra transformações locais encadeadas via pilha de matrizes OpenGL
(`glPushMatrix`/`glPopMatrix`), onde movimentos do torso e das articulações
proximais são herdados automaticamente pelos segmentos filhos.

Tags da apresentação: [PERSONAGEM], [BRACO], [PERNA].
"""

import math

from OpenGL.GL import (
    glColor3f,
    glPopMatrix,
    glPushMatrix,
    glRotatef,
    glTranslatef,
)

from expedicao.configuracoes import (
    COR_CALCA,
    COR_CAMISA,
    COR_MOCHILA,
    COR_PELE,
    FREQUENCIA_PASSADA,
)
from expedicao.matematica import interpolar
from expedicao.primitivas import (
    desenhar_bloco,
    desenhar_cone_vertical,
    desenhar_esfera,
    desenhar_face,
    desenhar_segmento,
)
from expedicao.simulacao import EstadoCena


def desenhar_braco(
    lado: int,
    angulo_ombro: float,
    angulo_cotovelo: float,
    quadrica,
) -> None:
    """[BRACO] Desenha a cadeia ombro -> braço -> cotovelo -> antebraço -> mão.

    Conceito CG: hierarquia articulada em pilha de matrizes; a rotação do ombro
    arrasta todo o braço e a do cotovelo atua apenas sobre antebraço e mão.

    Parâmetros:
        lado: Indicador lateral (-1 para esquerdo, +1 para direito).
        angulo_ombro: Rotação da articulação do ombro no eixo X local, em graus.
        angulo_cotovelo: Rotação da articulação do cotovelo no eixo X local, em graus.
        quadrica: Quádrica GLU usada para desenhar a esfera da mão.
    """
    glPushMatrix()
    glTranslatef(lado * 0.47, 0.32, 0.0)  # Posiciona a origem na articulação do ombro.
    glRotatef(lado * 13.0, 0.0, 0.0, 1.0)
    glRotatef(angulo_ombro, 1.0, 0.0, 0.0)
    desenhar_bloco((0.0, -0.25, 0.0), (0.24, 0.50, 0.26), COR_CAMISA)

    glTranslatef(0.0, -0.50, 0.0)  # Transfere a origem local para o cotovelo.
    glRotatef(angulo_cotovelo, 1.0, 0.0, 0.0)
    desenhar_bloco((0.0, -0.24, 0.0), (0.18, 0.48, 0.19), COR_PELE)

    glTranslatef(0.0, -0.49, 0.0)
    glColor3f(*COR_PELE)
    desenhar_esfera(quadrica, 0.14)
    glPopMatrix()


def desenhar_perna(lado: int, angulo_quadril: float, angulo_joelho: float) -> None:
    """[PERNA] Desenha a cadeia quadril -> coxa -> joelho -> canela -> bota.

    Conceito CG: transformações locais aninhadas isolam a rotação do joelho para
    movimentar apenas canela e bota após herdar a inclinação da coxa.

    Parâmetros:
        lado: Indicador lateral (-1 para perna esquerda, +1 para perna direita).
        angulo_quadril: Rotação da articulação do quadril no eixo X local, em graus.
        angulo_joelho: Rotação da articulação do joelho no eixo X local, em graus.
    """
    glPushMatrix()
    glTranslatef(lado * 0.24, -0.43, 0.0)
    glRotatef(angulo_quadril, 1.0, 0.0, 0.0)
    desenhar_bloco((0.0, -0.22, 0.0), (0.27, 0.44, 0.28), COR_CALCA)

    glTranslatef(0.0, -0.44, 0.0)  # Origem local passa a ser a dobra do joelho.
    glRotatef(angulo_joelho, 1.0, 0.0, 0.0)
    desenhar_bloco((0.0, -0.19, 0.0), (0.21, 0.38, 0.23), COR_PELE)
    desenhar_bloco((0.0, -0.39, -0.07), (0.30, 0.20, 0.43), (0.20, 0.16, 0.13))
    glPopMatrix()


def desenhar_cabeca_e_chapeu(quadrica) -> None:
    """Desenha a sub-hierarquia da cabeça, nariz e chapéu de escoteiro.

    Parâmetros:
        quadrica: Quádrica GLU usada para renderizar a esfera da cabeça.
    """
    glPushMatrix()
    glTranslatef(0.0, 0.79, 0.0)
    glColor3f(*COR_PELE)
    desenhar_esfera(quadrica, 0.36)
    desenhar_segmento((0.0, 0.20, 0.0), (0.0, 0.28, 0.0), 0.54, (0.44, 0.36, 0.18))
    desenhar_cone_vertical((0.0, 0.25, 0.0), 0.36, 0.32, (0.52, 0.43, 0.23))
    # O nariz aponta para -Z para deixar evidente que o escoteiro olha o paredão.
    desenhar_bloco((0.0, 0.0, -0.34), (0.12, 0.12, 0.12), COR_PELE)
    glPopMatrix()


def desenhar_personagem(estado: EstadoCena, quadrica) -> None:
    """[PERSONAGEM] Desenha o escoteiro completo a partir do torso como nó raiz.

    Conceito CG: aplica translação global na raiz (`estado.posicao_personagem`) e
    interpola os ângulos de descanso e escalada usando `estado.peso_escalada` para
    suavizar as pausas nos platôs.

    Parâmetros:
        estado: Estado atual da simulação com posição, movimento, peso e tempo de fase.
        quadrica: Quádrica GLU compartilhada para cabeça e mãos.
    """
    glPushMatrix()
    glTranslatef(*estado.posicao_personagem)
    passo = math.sin(estado.tempo_fase * math.tau * FREQUENCIA_PASSADA) if estado.em_movimento else 0.0

    # Torso e mochila voltada para a câmera (+Z), mantendo o rosto voltado à rocha (-Z).
    desenhar_bloco((0.0, 0.0, 0.0), (0.80, 0.88, 0.45), COR_CAMISA)
    desenhar_bloco((0.0, 0.02, 0.40), (0.67, 0.78, 0.39), COR_MOCHILA)
    desenhar_bloco((0.0, -0.25, 0.61), (0.45, 0.24, 0.09), (0.84, 0.43, 0.20))

    for lado in (-1, 1):
        desenhar_bloco((lado * 0.26, 0.05, 0.245), (0.09, 0.78, 0.065), (0.26, 0.25, 0.17))
        angulo_ombro = interpolar(8.0, 148.0 + lado * passo * 23.0, estado.peso_escalada)
        angulo_cotovelo = interpolar(-18.0, -35.0 - lado * passo * 18.0, estado.peso_escalada)
        desenhar_braco(lado, angulo_ombro, angulo_cotovelo, quadrica)

        angulo_quadril = interpolar(0.0, -22.0 - lado * passo * 25.0, estado.peso_escalada)
        angulo_joelho = interpolar(0.0, 32.0 + lado * passo * 20.0, estado.peso_escalada)
        desenhar_perna(lado, angulo_quadril, angulo_joelho)

    desenhar_cabeca_e_chapeu(quadrica)
    glColor3f(0.85, 0.17, 0.10)
    desenhar_face(((-0.33, 0.39, -0.24), (0.33, 0.39, -0.24), (0.0, 0.04, -0.26)))
    desenhar_bloco((0.0, -0.39, 0.0), (0.84, 0.12, 0.50), (0.25, 0.24, 0.18))
    glPopMatrix()
