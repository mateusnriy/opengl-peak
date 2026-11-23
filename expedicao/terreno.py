"""Textura procedural do solo e malha subdividida do terreno.

Gera inteiramente em Python uma textura tileable de grama e areia com mipmaps e
desenha o plano horizontal subdividido para capturar iluminação local e neblina.

Tags da apresentação: [TEXTURA], [TERRENO].
"""

import math
import random

import pygame
from OpenGL.GL import (
    GL_CURRENT_BIT,
    GL_ENABLE_BIT,
    GL_LINEAR,
    GL_LINEAR_MIPMAP_LINEAR,
    GL_MODULATE,
    GL_QUADS,
    GL_REPEAT,
    GL_RGB,
    GL_TEXTURE_2D,
    GL_TEXTURE_BIT,
    GL_TEXTURE_ENV,
    GL_TEXTURE_ENV_MODE,
    GL_TEXTURE_MAG_FILTER,
    GL_TEXTURE_MIN_FILTER,
    GL_TEXTURE_WRAP_S,
    GL_TEXTURE_WRAP_T,
    GL_UNSIGNED_BYTE,
    glBegin,
    glBindTexture,
    glColor3f,
    glDisable,
    glEnable,
    glEnd,
    glGenTextures,
    glNormal3f,
    glPopAttrib,
    glPushAttrib,
    glTexCoord2f,
    glTexEnvi,
    glTexParameteri,
    glVertex3f,
)
from OpenGL.GLU import gluBuild2DMipmaps

from expedicao.configuracoes import (
    COR_AREIA,
    COR_BASE_TERRENO,
    COR_GRAMA,
    LIMIAR_AREIA,
    PASSO_TERRENO,
    QUANTIDADE_FIOS_GRAMA,
    REPETICOES_TEXTURA,
    SEMENTE,
    SUAVIDADE_MISTURA_TERRENO,
    TAMANHO_TERRENO,
    TAMANHO_TEXTURA,
)
from expedicao.matematica import interpolacao_suave, interpolar, misturar_vetores


def _calcular_ruido_periodico(
    u: float,
    v: float,
    grade: tuple[tuple[float, ...], ...],
) -> float:
    """Calcula valor contínuo de ruído periódico 2D para evitar emendas na repetição.

    Conceito CG: interpolação bilinear suavizada com indexação modular (`% tamanho`)
    nas bordas para garantir textura perfeitamente contínua em `GL_REPEAT`.

    Parâmetros:
        u: Coordenada horizontal normalizada [0.0, 1.0).
        v: Coordenada vertical normalizada [0.0, 1.0).
        grade: Matriz quadrada de valores pseudoaleatórios em [0.0, 1.0).

    Retorno:
        Valor interpolado de ruído em [0.0, 1.0].
    """
    tamanho = len(grade)
    coord_x, coord_y = u * tamanho, v * tamanho
    indice_x, indice_y = math.floor(coord_x), math.floor(coord_y)
    fator_x = interpolacao_suave(coord_x - indice_x)
    fator_y = interpolacao_suave(coord_y - indice_y)
    amostra_inferior = interpolar(
        grade[indice_y % tamanho][indice_x % tamanho],
        grade[indice_y % tamanho][(indice_x + 1) % tamanho],
        fator_x,
    )
    amostra_superior = interpolar(
        grade[(indice_y + 1) % tamanho][indice_x % tamanho],
        grade[(indice_y + 1) % tamanho][(indice_x + 1) % tamanho],
        fator_x,
    )
    return interpolar(amostra_inferior, amostra_superior, fator_y)


def criar_textura_terreno() -> int:
    """[TEXTURA] Gera textura procedural de grama e areia e envia mipmaps para a GPU.

    Conceito CG: combina duas oitavas de ruído periódico, granulação e traços de
    grama, aplicando `GL_MODULATE` (preserva sombras/luzes) e `GL_LINEAR_MIPMAP_LINEAR`
    para evitar serrilhado e cintilação à distância.

    Retorno:
        Identificador inteiro da textura OpenGL alocada na placa de vídeo.
    """
    gerador = random.Random(SEMENTE)
    superficie = pygame.Surface((TAMANHO_TEXTURA, TAMANHO_TEXTURA))
    grades = tuple(
        tuple(tuple(gerador.random() for _ in range(tamanho)) for _ in range(tamanho))
        for tamanho in (6, 12)
    )

    for pixel_y in range(TAMANHO_TEXTURA):
        for pixel_x in range(TAMANHO_TEXTURA):
            u, v = pixel_x / TAMANHO_TEXTURA, pixel_y / TAMANHO_TEXTURA
            mancha = 0.75 * _calcular_ruido_periodico(
                u, v, grades[0]
            ) + 0.25 * _calcular_ruido_periodico(u, v, grades[1])
            fator_areia = interpolacao_suave((mancha - LIMIAR_AREIA) / SUAVIDADE_MISTURA_TERRENO)
            cor_base = misturar_vetores(COR_GRAMA, COR_AREIA, fator_areia)
            granulacao = gerador.uniform(-15.0, 15.0)
            cor_pixel = tuple(
                max(0, min(255, int(canal + granulacao))) for canal in cor_base
            )
            superficie.set_at((pixel_x, pixel_y), cor_pixel)

    # Desenha pequenos fios verticais apenas nas regiões predominantes de grama.
    for _ in range(QUANTIDADE_FIOS_GRAMA):
        pixel_x = gerador.randrange(TAMANHO_TEXTURA)
        pixel_y = gerador.randrange(TAMANHO_TEXTURA)
        cor_atual = superficie.get_at((pixel_x, pixel_y))
        if cor_atual.g > cor_atual.r * 1.15:
            brilho = gerador.randint(8, 27)
            cor_fio = tuple(min(255, canal + brilho) for canal in cor_atual[:3])
            pygame.draw.line(
                superficie,
                cor_fio,
                (pixel_x, pixel_y),
                (pixel_x + gerador.choice((-1, 0, 1)), pixel_y - gerador.randint(2, 5)),
            )

    identificador_textura = glGenTextures(1)
    glBindTexture(GL_TEXTURE_2D, identificador_textura)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR_MIPMAP_LINEAR)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_REPEAT)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_REPEAT)
    glTexEnvi(GL_TEXTURE_ENV, GL_TEXTURE_ENV_MODE, GL_MODULATE)
    gluBuild2DMipmaps(
        GL_TEXTURE_2D,
        GL_RGB,
        TAMANHO_TEXTURA,
        TAMANHO_TEXTURA,
        GL_RGB,
        GL_UNSIGNED_BYTE,
        pygame.image.tobytes(superficie, "RGB", True),
    )
    return identificador_textura


def desenhar_terreno(identificador_textura: int) -> None:
    """[TERRENO] Desenha o plano horizontal Y=0 texturizado e subdividido em malha.

    Conceito CG: como o pipeline fixo calcula iluminação por vértice, subdividir o
    plano em malha regular permite que a atenuação da fogueira e a neblina variem
    suavemente pelo chão em vez de ficarem uniformes em um único quadrilátero.

    Parâmetros:
        identificador_textura: Identificador OpenGL retornado por `criar_textura_terreno`.
    """
    glPushAttrib(GL_ENABLE_BIT | GL_CURRENT_BIT | GL_TEXTURE_BIT)
    glEnable(GL_TEXTURE_2D)
    glBindTexture(GL_TEXTURE_2D, identificador_textura)
    glColor3f(*COR_BASE_TERRENO)
    glBegin(GL_QUADS)
    glNormal3f(0.0, 1.0, 0.0)

    divisoes = max(1, math.ceil(2.0 * TAMANHO_TERRENO / PASSO_TERRENO))
    passo = 2.0 * TAMANHO_TERRENO / divisoes
    extensao_total = 2.0 * TAMANHO_TERRENO
    for linha in range(divisoes):
        coord_z = -TAMANHO_TERRENO + linha * passo
        for coluna in range(divisoes):
            coord_x = -TAMANHO_TERRENO + coluna * passo
            for vertice_x, vertice_z in (
                (coord_x, coord_z + passo),
                (coord_x + passo, coord_z + passo),
                (coord_x + passo, coord_z),
                (coord_x, coord_z),
            ):
                u = (vertice_x + TAMANHO_TERRENO) / extensao_total * REPETICOES_TEXTURA
                v = (vertice_z + TAMANHO_TERRENO) / extensao_total * REPETICOES_TEXTURA
                glTexCoord2f(u, v)
                glVertex3f(vertice_x, 0.0, vertice_z)
    glEnd()
    glDisable(GL_TEXTURE_2D)
    glPopAttrib()
