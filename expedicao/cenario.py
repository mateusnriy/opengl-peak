"""Geometria estática da cena e compilação em Lista de Exibição (Display List).

Agrupa todos os elementos fixos da paisagem: acampamento (fogueira, lenha,
assentos e barraca), floresta determinística de pinheiros, paredões escaláveis,
platôs, pico nevado com bandeira, contrafortes laterais e terreno texturizado.

Tags da apresentação: [ACAMPAMENTO], [BARRACA], [ARVORES], [PAREDE_1],
[PAREDE_2], [PAREDE_3], [PLATO_1], [PLATO_2], [PLATO_3], [PICO_NEVADO],
[MASSA_LATERAL], [OTIMIZACAO].
"""

import math
import random
from dataclasses import dataclass

from OpenGL.GL import (
    GL_COMPILE,
    glColor3f,
    glDeleteLists,
    glEndList,
    glGenLists,
    glNewList,
    glPopMatrix,
    glPushMatrix,
    glRotatef,
    glScalef,
    glTranslatef,
)

from expedicao.configuracoes import (
    ALTURA_CUME,
    ALTURA_PLATO_1,
    ALTURA_PLATO_2,
    ALTURA_PLATO_3,
    COR_BARRACA,
    COR_FOLHAS,
    COR_NEVE,
    COR_PLATO,
    COR_ROCHA,
    COR_TIRANTES_BARRACA,
    COR_TRONCO,
    POSICAO_BARRACA,
    POSICAO_FOGUEIRA,
    QUANTIDADE_ARVORES,
    SEMENTE,
)
from expedicao.matematica import interpolar
from expedicao.primitivas import (
    desenhar_bloco,
    desenhar_cone_vertical,
    desenhar_face,
    desenhar_segmento,
)
from expedicao.terreno import desenhar_terreno


@dataclass(frozen=True)
class Arvore:
    """Descreve um pinheiro posicionado no cenário estático.

    Atributos:
        x: Coordenada X da base do tronco no espaço do mundo.
        z: Coordenada Z da base do tronco no espaço do mundo.
        escala: Fator de escala uniforme aplicado ao tronco e às copas.
        rotacao_y: Rotação em torno do eixo vertical +Y, em graus.
    """

    x: float
    z: float
    escala: float
    rotacao_y: float


def gerar_arvores(
    semente: int = SEMENTE,
    quantidade: int = QUANTIDADE_ARVORES,
) -> tuple[Arvore, ...]:
    """[ARVORES] Gera posições, escalas e rotações determinísticas para os pinheiros.

    Parâmetros:
        semente: Semente fixa para manter o mesmo posicionamento entre execuções e reinícios.
        quantidade: Quantidade total de árvores distribuídas nas laterais do cenário.

    Retorno:
        Tupla imutável de instâncias `Arvore` alternadas à esquerda e à direita.
    """
    gerador = random.Random(semente)
    arvores = []
    for indice in range(quantidade):
        # Alterna os lados para preservar livre o corredor central entre acampamento e paredão.
        lado = -1 if indice % 2 else 1
        arvores.append(
            Arvore(
                x=lado * gerador.uniform(11.5, 22.0),
                z=gerador.uniform(-15.0, 8.0),
                escala=gerador.uniform(0.7, 1.5),
                rotacao_y=gerador.uniform(0.0, 360.0),
            )
        )
    return tuple(arvores)


def desenhar_barraca() -> None:
    """[BARRACA] Desenha a barraca em prisma triangular com porta, cumeeira e estacas.

    Conceito CG: utiliza translação e rotação no referencial do conjunto e modela
    faces manuais fechadas com normais externas.
    """
    glPushMatrix()
    glTranslatef(*POSICAO_BARRACA)
    glRotatef(-12.0, 0.0, 1.0, 0.0)

    frente_esq, frente_dir, frente_topo = (-1.8, 0.0, 1.7), (1.8, 0.0, 1.7), (0.0, 2.6, 1.7)
    tras_esq, tras_dir, tras_topo = (-1.8, 0.0, -1.7), (1.8, 0.0, -1.7), (0.0, 2.6, -1.7)
    glColor3f(*COR_BARRACA)
    for face in (
        (frente_esq, frente_dir, frente_topo),
        (tras_dir, tras_esq, tras_topo),
        (frente_esq, frente_topo, tras_topo, tras_esq),
        (frente_topo, frente_dir, tras_dir, tras_topo),
        (tras_esq, tras_dir, frente_dir, frente_esq),
    ):
        desenhar_face(face)

    # Porta deslocada ligeiramente à frente em Z=1.712 para evitar Z-fighting com o tecido.
    glColor3f(0.18, 0.22, 0.22)
    desenhar_face(((-1.15, 0.02, 1.712), (1.15, 0.02, 1.712), (0.0, 2.14, 1.712)))
    desenhar_segmento((0.0, 2.6, 1.7), (0.0, 2.6, -1.7), 0.045, (0.88, 0.85, 0.68))

    for lado in (-1, 1):
        desenhar_segmento(
            (lado * 1.8, 0.0, 1.7),
            (lado * 2.6, 0.05, 2.4),
            0.021,
            COR_TIRANTES_BARRACA,
        )
        desenhar_bloco((lado * 2.6, 0.12, 2.4), (0.07, 0.24, 0.07), COR_TRONCO)
    glPopMatrix()


def desenhar_acampamento() -> None:
    """[ACAMPAMENTO] Desenha anel de pedras, lenha cruzada, três assentos e a barraca.

    Conceito CG: aplica posicionamento polar radial nas pedras e transformações
    locais de translação e rotação na lenha e nos bancos ao redor da fogueira.
    """
    glPushMatrix()
    glTranslatef(*POSICAO_FOGUEIRA)
    for indice in range(11):
        angulo = indice * math.tau / 11.0
        desenhar_bloco(
            (math.cos(angulo) * 1.04, 0.1, math.sin(angulo) * 1.04),
            (0.49, 0.35, 0.38),
            (0.35, 0.36, 0.38),
            (8.0, indice * 360.0 / 11.0, 7.0),
        )

    for indice, angulo in enumerate((25.0, 115.0, 65.0)):
        glPushMatrix()
        glTranslatef(0.0, 0.17 + indice * 0.09, 0.0)
        glRotatef(angulo, 0.0, 1.0, 0.0)
        desenhar_segmento((-0.83, 0.0, 0.0), (0.83, 0.0, 0.0), 0.16, COR_TRONCO)
        glPopMatrix()

    for pos_x, pos_z, angulo in ((-2.7, 0.7, 15.0), (1.8, 2.8, -35.0), (-0.4, -2.8, 70.0)):
        glPushMatrix()
        glTranslatef(pos_x, 0.28, pos_z)
        glRotatef(angulo, 0.0, 1.0, 0.0)
        desenhar_segmento((-1.05, 0.0, 0.0), (1.05, 0.0, 0.0), 0.28, COR_TRONCO)
        glPopMatrix()
    glPopMatrix()

    desenhar_barraca()


def desenhar_arvores(arvores: tuple[Arvore, ...]) -> None:
    """[ARVORES] Renderiza cada pinheiro com tronco cilíndrico e três cones sobrepostos.

    Parâmetros:
        arvores: Coleção de instâncias `Arvore` contendo posição, escala e rotação.
    """
    for arvore in arvores:
        glPushMatrix()
        glTranslatef(arvore.x, 0.0, arvore.z)
        glRotatef(arvore.rotacao_y, 0.0, 1.0, 0.0)
        glScalef(arvore.escala, arvore.escala, arvore.escala)
        desenhar_segmento((0.0, 0.0, 0.0), (0.0, 3.3, 0.0), 0.20, COR_TRONCO)
        for camada in range(3):
            cor_camada = tuple(canal * (1.0 + 0.12 * camada) for canal in COR_FOLHAS)
            desenhar_cone_vertical(
                (0.0, 1.15 + camada * 0.88, 0.0),
                1.5 - camada * 0.34,
                2.05 - camada * 0.18,
                cor_camada,
            )
        glPopMatrix()


def desenhar_secao_rochosa(
    altura_base: float,
    altura_topo: float,
    largura_base: float,
    largura_topo: float,
    semente: int,
) -> None:
    """Constrói uma seção trapezoidal do paredão com saliências rochosas e agarras.

    Parâmetros:
        altura_base: Coordenada Y da base da seção da parede.
        altura_topo: Coordenada Y do topo da seção da parede.
        largura_base: Meia-largura horizontal da parede na base.
        largura_topo: Meia-largura horizontal da parede no topo.
        semente: Semente determinística para variar inclinação e cor das facetas.
    """
    glColor3f(*COR_ROCHA)
    frente_inf_esq = (-largura_base, altura_base, 0.0)
    frente_inf_dir = (largura_base, altura_base, 0.0)
    frente_sup_dir = (largura_topo, altura_topo, 0.0)
    frente_sup_esq = (-largura_topo, altura_topo, 0.0)

    tras_inf_esq = (-largura_base, altura_base, -6.0)
    tras_inf_dir = (largura_base, altura_base, -6.0)
    tras_sup_dir = (largura_topo, altura_topo, -6.0)
    tras_sup_esq = (-largura_topo, altura_topo, -6.0)

    for face in (
        (frente_inf_esq, frente_inf_dir, frente_sup_dir, frente_sup_esq),
        (tras_inf_dir, tras_inf_esq, tras_sup_esq, tras_sup_dir),
        (tras_inf_esq, frente_inf_esq, frente_sup_esq, tras_sup_esq),
        (frente_inf_dir, tras_inf_dir, tras_sup_dir, frente_sup_dir),
        (frente_sup_esq, frente_sup_dir, tras_sup_dir, tras_sup_esq),
        (tras_inf_esq, tras_inf_dir, frente_inf_dir, frente_inf_esq),
    ):
        desenhar_face(face)

    gerador = random.Random(semente)
    # Os blocos facetados avançam no máximo até Z≈0.55; a rota de escalada mantém o
    # personagem à frente desse limite para evitar interseção com a rocha.
    for linha in range(4):
        coord_y = interpolar(altura_base, altura_topo, (linha + 0.5) / 4.0)
        largura = interpolar(largura_base, largura_topo, (linha + 0.5) / 4.0)
        for coluna in range(5):
            coord_x = (coluna - 2) * largura * 0.37
            cor_bloco = tuple(canal * gerador.uniform(0.85, 1.13) for canal in COR_ROCHA)
            desenhar_bloco(
                (coord_x, coord_y, -0.05),
                (largura * 0.37, (altura_topo - altura_base) * 0.27, 0.52),
                cor_bloco,
                (0.0, gerador.uniform(-9.0, 9.0), gerador.uniform(-7.0, 7.0)),
            )

    # Agarras lisas em cor ocre dispostas em curva senoidal ao longo da parede.
    for indice in range(7):
        coord_y = interpolar(altura_base, altura_topo, (indice + 0.5) / 7.0)
        coord_x = math.sin(coord_y * 0.55) * 2.3
        desenhar_bloco(
            (coord_x, coord_y, 0.09),
            (0.45, 0.18, 0.28),
            COR_PLATO,
            (0.0, 0.0, gerador.uniform(-15.0, 15.0)),
        )


def desenhar_parede_1() -> None:
    """[PAREDE_1] Desenha a face rochosa inferior entre o solo e o primeiro platô."""
    desenhar_secao_rochosa(0.0, ALTURA_PLATO_1, 7.0, 5.8, SEMENTE + 1)


def desenhar_parede_2() -> None:
    """[PAREDE_2] Desenha a face rochosa intermediária entre o primeiro e o segundo platô."""
    desenhar_secao_rochosa(ALTURA_PLATO_1, ALTURA_PLATO_2, 5.8, 4.5, SEMENTE + 2)


def desenhar_parede_3() -> None:
    """[PAREDE_3] Desenha a face rochosa superior entre o segundo e o terceiro platô."""
    desenhar_secao_rochosa(ALTURA_PLATO_2, ALTURA_PLATO_3, 4.5, 3.2, SEMENTE + 3)


def desenhar_plato_1() -> None:
    """[PLATO_1] Desenha o primeiro descanso plano, posicionado do lado esquerdo."""
    desenhar_bloco((-2.7, ALTURA_PLATO_1 - 0.20, 0.35), (3.4, 0.40, 2.4), COR_PLATO)


def desenhar_plato_2() -> None:
    """[PLATO_2] Desenha o segundo descanso plano, à direita, já com cobertura de neve."""
    desenhar_bloco((2.0, ALTURA_PLATO_2 - 0.20, 0.35), (3.0, 0.40, 2.4), COR_PLATO)
    desenhar_bloco((2.0, ALTURA_PLATO_2 + 0.025, 0.35), (3.0, 0.05, 2.4), COR_NEVE)


def desenhar_plato_3() -> None:
    """[PLATO_3] Desenha o terceiro descanso plano coberto de neve antes do cume."""
    desenhar_bloco((-0.7, ALTURA_PLATO_3 - 0.20, 0.35), (3.2, 0.40, 2.4), COR_PLATO)
    desenhar_bloco((-0.7, ALTURA_PLATO_3 + 0.025, 0.35), (3.2, 0.05, 2.4), COR_NEVE)


def desenhar_pico_nevado() -> None:
    """[PICO_NEVADO] Desenha o cume nevado em prisma truncado plano e a bandeira no topo."""
    base, topo = ALTURA_PLATO_3, ALTURA_CUME
    frente_inf_esq = (-3.2, base, 0.0)
    frente_inf_dir = (3.2, base, 0.0)
    frente_sup_dir = (1.7, topo, 0.65)
    frente_sup_esq = (-1.7, topo, 0.65)

    tras_inf_esq = (-3.2, base, -6.0)
    tras_inf_dir = (3.2, base, -6.0)
    tras_sup_dir = (1.7, topo, -2.8)
    tras_sup_esq = (-1.7, topo, -2.8)

    glColor3f(*COR_NEVE)
    for face in (
        (frente_inf_esq, frente_inf_dir, frente_sup_dir, frente_sup_esq),
        (tras_inf_dir, tras_inf_esq, tras_sup_esq, tras_sup_dir),
        (tras_inf_esq, frente_inf_esq, frente_sup_esq, tras_sup_esq),
        (frente_inf_dir, tras_inf_dir, tras_sup_dir, frente_sup_dir),
        (frente_sup_esq, frente_sup_dir, tras_sup_dir, tras_sup_esq),
        (tras_inf_esq, tras_inf_dir, frente_inf_dir, frente_inf_esq),
    ):
        desenhar_face(face)

    desenhar_segmento((-1.05, topo, -1.0), (-1.05, topo + 2.3, -1.0), 0.045, (0.32, 0.34, 0.36))
    glColor3f(0.96, 0.35, 0.16)
    # Vértices em sentido anti-horário vistos da câmera garantem normal apontando para +Z.
    desenhar_face(((-1.05, topo + 2.2, -1.0), (-1.05, topo + 1.6, -1.0), (0.18, topo + 1.9, -1.0)))


def desenhar_massa_lateral() -> None:
    """[MASSA_LATERAL] Desenha contrafortes rochosos inclinados atrás da face escalável."""
    contrafortes = (
        ((-6.0, 4.0, -5.0), (6.0, 9.0, 7.0), (4.0, -12.0, -19.0)),
        ((6.0, 4.5, -5.0), (5.0, 10.0, 7.0), (-5.0, 14.0, 18.0)),
        ((-3.7, 11.0, -5.8), (4.0, 12.0, 5.0), (8.0, -8.0, -12.0)),
        ((3.0, 12.0, -6.0), (4.4, 13.0, 6.0), (-8.0, 10.0, 12.0)),
        ((0.0, 8.0, -8.0), (7.0, 17.0, 7.0), (8.0, 12.0, 0.0)),
    )
    for posicao, escala, rotacao in contrafortes:
        desenhar_bloco(posicao, escala, (0.36, 0.39, 0.39), rotacao)


def desenhar_cenario_estatico(
    identificador_textura: int,
    arvores: tuple[Arvore, ...],
) -> None:
    """Desenha em sequência imediata toda a geometria fixa do cenário.

    Parâmetros:
        identificador_textura: Textura do solo criada para o terreno.
        arvores: Coleção determinística de árvores gerada para a cena.
    """
    desenhar_terreno(identificador_textura)
    desenhar_massa_lateral()
    desenhar_parede_1()
    desenhar_parede_2()
    desenhar_parede_3()
    desenhar_plato_1()
    desenhar_plato_2()
    desenhar_plato_3()
    desenhar_pico_nevado()
    desenhar_arvores(arvores)
    desenhar_acampamento()


def compilar_cenario_estatico(
    identificador_textura: int,
    arvores: tuple[Arvore, ...],
) -> int:
    """[OTIMIZACAO] Compila o cenário estático em uma Lista de Exibição OpenGL.

    Conceito CG: `glNewList`/`glCallList` armazena as chamadas do pipeline fixo na
    GPU após a criação do contexto, mantendo a avaliação das luzes dinâmica por quadro.

    Parâmetros:
        identificador_textura: Textura OpenGL do terreno vinculada durante a compilação.
        arvores: Coleção de árvores incluída na geometria compilada.

    Retorno:
        Identificador inteiro positivo da Lista de Exibição criada.
    """
    identificador_lista = glGenLists(1)
    if not identificador_lista:
        raise RuntimeError("Não foi possível criar a lista de exibição OpenGL.")
    glNewList(identificador_lista, GL_COMPILE)
    try:
        desenhar_cenario_estatico(identificador_textura, arvores)
    except Exception:
        glEndList()
        glDeleteLists(identificador_lista, 1)
        raise
    glEndList()
    return identificador_lista
