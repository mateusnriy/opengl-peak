"""Faixa inferior de controles 2D renderizada via projeção ortográfica.

Gera a textura RGBA do painel de atalhos uma única vez na inicialização da cena
e a projeta sobre a janela 3D restaurando integralmente matrizes e estados OpenGL.

Tag da apresentação: [HUD].
"""

from dataclasses import dataclass

import pygame
from OpenGL.GL import (
    GL_BLEND,
    GL_COLOR_BUFFER_BIT,
    GL_CURRENT_BIT,
    GL_DEPTH_BUFFER_BIT,
    GL_DEPTH_TEST,
    GL_ENABLE_BIT,
    GL_FOG,
    GL_LIGHTING,
    GL_LINEAR,
    GL_MODELVIEW,
    GL_ONE_MINUS_SRC_ALPHA,
    GL_PROJECTION,
    GL_QUADS,
    GL_RGBA,
    GL_SRC_ALPHA,
    GL_TEXTURE_2D,
    GL_TEXTURE_BIT,
    GL_TEXTURE_MAG_FILTER,
    GL_TEXTURE_MIN_FILTER,
    GL_UNSIGNED_BYTE,
    glBegin,
    glBindTexture,
    glBlendFunc,
    glColor4f,
    glDisable,
    glEnable,
    glEnd,
    glGenTextures,
    glLoadIdentity,
    glMatrixMode,
    glOrtho,
    glPopAttrib,
    glPopMatrix,
    glPushAttrib,
    glPushMatrix,
    glTexCoord2f,
    glTexImage2D,
    glTexParameteri,
    glVertex2f,
)

from expedicao.configuracoes import (
    ALTURA_PAINEL_CONTROLES,
    LARGURA_PAINEL_CONTROLES,
    TAMANHO_FONTE_PAINEL,
    TEXTO_PAINEL_CONTROLES,
)


@dataclass(frozen=True)
class PainelControles:
    """Armazena a textura OpenGL e dimensões originais da faixa inferior de controles.

    Atributos:
        identificador_textura: ID da textura RGBA pré-carregada na GPU.
        largura: Largura base da superfície do painel, em pixels.
        altura: Altura base da superfície do painel, em pixels.
    """

    identificador_textura: int
    largura: int
    altura: int


def criar_painel_controles() -> PainelControles:
    """[HUD] Rasteriza a barra de controles uma única vez e envia a textura à GPU.

    Conceito CG: evita re-upload de textura a cada quadro ao preparar a superfície
    RGBA estática com canal alfa na inicialização da aplicação.

    Retorno:
        Instância de `PainelControles` pronta para uso em `desenhar_painel_controles`.
    """
    identificador_textura = glGenTextures(1)
    glBindTexture(GL_TEXTURE_2D, identificador_textura)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)

    superficie = pygame.Surface((LARGURA_PAINEL_CONTROLES, ALTURA_PAINEL_CONTROLES), pygame.SRCALPHA)
    pygame.draw.rect(
        superficie,
        (12, 22, 30, 218),
        (0, 0, LARGURA_PAINEL_CONTROLES, ALTURA_PAINEL_CONTROLES),
        border_radius=10,
    )
    fonte = pygame.font.Font(None, TAMANHO_FONTE_PAINEL)
    superficie_texto = fonte.render(TEXTO_PAINEL_CONTROLES, True, (219, 229, 230))
    superficie.blit(superficie_texto, (16, 14))

    glTexImage2D(
        GL_TEXTURE_2D,
        0,
        GL_RGBA,
        LARGURA_PAINEL_CONTROLES,
        ALTURA_PAINEL_CONTROLES,
        0,
        GL_RGBA,
        GL_UNSIGNED_BYTE,
        pygame.image.tobytes(superficie, "RGBA", True),
    )
    return PainelControles(
        identificador_textura=identificador_textura,
        largura=LARGURA_PAINEL_CONTROLES,
        altura=ALTURA_PAINEL_CONTROLES,
    )


def desenhar_painel_controles(
    painel: PainelControles,
    largura_janela: int,
    altura_janela: int,
) -> None:
    """[HUD] Renderiza a faixa de atalhos 2D sobreposta no canto inferior esquerdo.

    Conceito CG: empilha `GL_PROJECTION` e `GL_MODELVIEW`, aplica `glOrtho` em
    coordenadas de pixels e desliga profundidade, luz e neblina temporariamente.

    Parâmetros:
        painel: Estrutura `PainelControles` contendo textura e tamanho base.
        largura_janela: Largura atual da janela em pixels.
        altura_janela: Altura atual da janela em pixels.
    """
    glPushAttrib(
        GL_ENABLE_BIT
        | GL_CURRENT_BIT
        | GL_COLOR_BUFFER_BIT
        | GL_DEPTH_BUFFER_BIT
        | GL_TEXTURE_BIT
    )
    glDisable(GL_LIGHTING)
    glDisable(GL_DEPTH_TEST)
    glDisable(GL_FOG)
    glEnable(GL_TEXTURE_2D)
    glEnable(GL_BLEND)
    glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
    glBindTexture(GL_TEXTURE_2D, painel.identificador_textura)

    glMatrixMode(GL_PROJECTION)
    glPushMatrix()
    glLoadIdentity()
    glOrtho(0.0, float(largura_janela), float(altura_janela), 0.0, -1.0, 1.0)

    glMatrixMode(GL_MODELVIEW)
    glPushMatrix()
    glLoadIdentity()
    glColor4f(1.0, 1.0, 1.0, 1.0)

    escala = min(
        1.0,
        max(1, largura_janela - 32) / painel.largura,
        max(1, altura_janela - 32) / painel.altura,
    )
    pos_x = 16.0
    pos_y = altura_janela - 16.0 - painel.altura * escala
    largura_desenho = painel.largura * escala
    altura_desenho = painel.altura * escala

    # `pygame.image.tobytes(..., True)` inverte o eixo Y, logo o topo da tela usa v=1.0.
    glBegin(GL_QUADS)
    for coord_uv, vertice_2d in (
        ((0.0, 1.0), (pos_x, pos_y)),
        ((1.0, 1.0), (pos_x + largura_desenho, pos_y)),
        ((1.0, 0.0), (pos_x + largura_desenho, pos_y + altura_desenho)),
        ((0.0, 0.0), (pos_x, pos_y + altura_desenho)),
    ):
        glTexCoord2f(*coord_uv)
        glVertex2f(*vertice_2d)
    glEnd()

    glPopMatrix()
    glMatrixMode(GL_PROJECTION)
    glPopMatrix()
    glMatrixMode(GL_MODELVIEW)
    glPopAttrib()
