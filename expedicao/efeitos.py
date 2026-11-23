"""Elementos dinâmicos, emissivos e transparentes da cena.

Reúne a animação das chamas, partículas transparentes de fumaça ordenadas por
profundidade, esfera emissiva da lua e marcadores visuais de posição das luzes.

Tags da apresentação: [ANIM_A1_CHAMAS], [ANIM_A5_FUMACA], [LUA], [MARCADORES].
"""

import math

from OpenGL.GL import (
    GL_BLEND,
    GL_COLOR_BUFFER_BIT,
    GL_CURRENT_BIT,
    GL_DEPTH_BUFFER_BIT,
    GL_ENABLE_BIT,
    GL_FALSE,
    GL_FOG,
    GL_LIGHTING,
    GL_ONE_MINUS_SRC_ALPHA,
    GL_SRC_ALPHA,
    glBlendFunc,
    glColor3f,
    glColor4f,
    glDepthMask,
    glDisable,
    glEnable,
    glPopAttrib,
    glPopMatrix,
    glPushAttrib,
    glPushMatrix,
    glRotatef,
    glScalef,
    glTranslatef,
)

from expedicao.configuracoes import (
    ALTURA_FUMACA,
    COR_FUMACA,
    COR_LUA,
    CORES_CHAMAS,
    DURACAO_FUMACA,
    FUNDO_NOITE,
    POSICAO_FOGUEIRA,
    POSICAO_LUA,
    POSICAO_SOL,
    QUANTIDADE_FUMACA,
    RAIO_LUA,
    PoseCamera,
)
from expedicao.matematica import interpolacao_suave, misturar_vetores
from expedicao.primitivas import desenhar_cone_vertical, desenhar_esfera
from expedicao.simulacao import EstadoCena


def desenhar_chamas(tempo_total: float) -> None:
    """[ANIM_A1_CHAMAS] Desenha os três cones emissivos da fogueira com pulsação contínua.

    Conceito CG: combina translação oscilatória, rotação em Y/Z e escala inversa
    `(1/pulso, pulso, 1)` sem iluminação externa, preservando o volume visual.

    Parâmetros:
        tempo_total: Tempo acumulado da cena em segundos.
    """
    glPushAttrib(GL_ENABLE_BIT | GL_CURRENT_BIT)
    glDisable(GL_LIGHTING)
    glPushMatrix()
    glTranslatef(*POSICAO_FOGUEIRA)
    for indice, ((raio, altura), cor) in enumerate(
        zip(((0.69, 1.9), (0.49, 1.5), (0.26, 1.1)), CORES_CHAMAS)
    ):
        glPushMatrix()
        # Camadas internas avançam em +Z para não ficarem ocultas pelo cone externo.
        glTranslatef(
            0.10 * math.sin(tempo_total * 3.0 + indice) + indice * 0.14,
            0.28,
            0.08 * math.cos(tempo_total * 4.0 + indice) + indice * 0.23,
        )
        glRotatef(tempo_total * 36.0 + indice * 80.0, 0.0, 1.0, 0.0)
        glRotatef(8.0 * math.sin(tempo_total * 5.0 + indice), 0.0, 0.0, 1.0)
        pulso = 1.0 + 0.14 * math.sin(tempo_total * 7.0 + indice * 2.0)
        glScalef(1.0 / pulso, pulso, 1.0)
        desenhar_cone_vertical((0.0, 0.0, 0.0), raio, altura, cor)
        glPopMatrix()
    glPopMatrix()
    glPopAttrib()


def desenhar_fumaca(tempo_total: float, quadrica, camera: PoseCamera) -> None:
    """[ANIM_A5_FUMACA] Simula partículas de fumaça transparentes ordenadas do fundo à frente.

    Conceito CG: mistura alfa (`GL_SRC_ALPHA`, `GL_ONE_MINUS_SRC_ALPHA`) exige
    ordenação back-to-front e `glDepthMask(GL_FALSE)` para evitar buracos na transparência.

    Parâmetros:
        tempo_total: Tempo acumulado da cena em segundos.
        quadrica: Quádrica GLU usada para desenhar cada partícula esférica.
        camera: Pose atual da câmera para calcular a distância de ordenação.
    """
    particulas = []
    for indice in range(QUANTIDADE_FUMACA):
        idade = (tempo_total + indice * DURACAO_FUMACA / QUANTIDADE_FUMACA) % DURACAO_FUMACA
        vida = idade / DURACAO_FUMACA
        posicao = (
            POSICAO_FOGUEIRA[0] + 0.35 * math.sin(indice + vida * 3.0) + vida * 0.7,
            POSICAO_FOGUEIRA[1] + 1.35 + vida * ALTURA_FUMACA,
            POSICAO_FOGUEIRA[2] + 0.2 * math.cos(indice * 2.0 + vida * 3.0),
        )
        distancia_quadrada = sum(
            (coord_p - coord_c) ** 2 for coord_p, coord_c in zip(posicao, camera.posicao)
        )
        particulas.append((distancia_quadrada, indice, vida, posicao))

    glPushAttrib(GL_ENABLE_BIT | GL_CURRENT_BIT | GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    glEnable(GL_BLEND)
    glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
    glDepthMask(GL_FALSE)
    for _, indice, vida, posicao in sorted(particulas, reverse=True):
        glPushMatrix()
        glTranslatef(*posicao)
        glRotatef(tempo_total * 18.0 + indice * 40.0, 0.0, 1.0, 0.0)
        tamanho = 0.18 + vida * 0.65
        glScalef(tamanho, tamanho * 0.8, tamanho)
        glColor4f(*COR_FUMACA, 0.27 * math.sin(math.pi * vida))
        desenhar_esfera(quadrica)
        glPopMatrix()
    glPopAttrib()


def desenhar_lua(estado: EstadoCena, quadrica) -> None:
    """[LUA] Desenha a esfera lunar emissiva que desaparece gradualmente ao amanhecer.

    Conceito CG: mantém o teste de profundidade ativo (para ser ocultada atrás da
    montanha se necessário) com escrita desativada (`glDepthMask(GL_FALSE)`) e sem neblina.

    Parâmetros:
        estado: Estado atual da cena contendo `fracao_dia`.
        quadrica: Quádrica GLU usada para renderizar a esfera lunar.
    """
    fator_noite = 1.0 - interpolacao_suave(estado.fracao_dia)
    if fator_noite <= 0.001:
        return

    glPushAttrib(GL_ENABLE_BIT | GL_CURRENT_BIT | GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    glDisable(GL_LIGHTING)
    glDisable(GL_FOG)
    glEnable(GL_BLEND)
    glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
    glDepthMask(GL_FALSE)
    glPushMatrix()
    glTranslatef(*POSICAO_LUA)
    glColor4f(*COR_LUA, fator_noite)
    desenhar_esfera(quadrica, RAIO_LUA, 18, 12)
    glPopMatrix()
    glPopAttrib()


def desenhar_marcadores_luz(estado: EstadoCena, quadrica) -> None:
    """[MARCADORES] Desenha pequenas esferas emissivas indicando as fontes de luz.

    Conceito CG: desliga a iluminação no Sol e na fogueira e desliga `GL_FOG`
    especificamente no Sol (cuja posição excede `INICIO_NEBLINA`) para mantê-lo visível.

    Parâmetros:
        estado: Estado atual da cena contendo `fracao_dia`.
        quadrica: Quádrica GLU usada para renderizar as esferas marcadoras.
    """
    glPushAttrib(GL_ENABLE_BIT | GL_CURRENT_BIT)
    glDisable(GL_LIGHTING)

    # O marcador solar fica além do início da neblina e precisa ignorar GL_FOG.
    glPushAttrib(GL_ENABLE_BIT)
    glDisable(GL_FOG)
    glPushMatrix()
    glTranslatef(*POSICAO_SOL)
    glColor3f(*misturar_vetores(FUNDO_NOITE, (1.0, 0.92, 0.65), estado.fracao_dia))
    desenhar_esfera(quadrica, 1.1, 12, 8)
    glPopMatrix()
    glPopAttrib()

    pos_x, pos_y, pos_z = POSICAO_FOGUEIRA
    glPushMatrix()
    glTranslatef(pos_x, pos_y + 0.85, pos_z)
    glColor3f(1.0, 0.73, 0.22)
    desenhar_esfera(quadrica, 0.16, 12, 8)
    glPopMatrix()

    glPopAttrib()
