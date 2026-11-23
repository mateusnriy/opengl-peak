"""Primitivas geométricas 3D reutilizáveis para o pipeline OpenGL de função fixa.

Implementa faces planas com cálculo manual de normais, cubo unitário, blocos
transformados, esferas via quádrica GLU, cilindros/cones fechados e segmentos
arbitrários entre dois pontos no espaço 3D.

Tag da apresentação: [PRIMITIVAS].
"""

import math

from OpenGL.GL import (
    GL_QUADS,
    GL_TRIANGLES,
    glBegin,
    glColor3f,
    glEnd,
    glNormal3f,
    glPopMatrix,
    glPushMatrix,
    glRotatef,
    glScalef,
    glVertex3f,
)
from OpenGL.GLU import gluSphere

from expedicao.matematica import calcular_normal_face


def desenhar_face(vertices: tuple[tuple[float, float, float], ...]) -> None:
    """[PRIMITIVAS] Desenha um triângulo ou quadrilátero com normal plana calculada.

    Conceito CG: define uma única normal unitária via produto vetorial antes de
    enviar os vértices, garantindo resposta consistente à iluminação de Phong.

    Parâmetros:
        vertices: Tupla com 3 ou 4 coordenadas (x, y, z) em ordem anti-horária (CCW).
    """
    glBegin(GL_TRIANGLES if len(vertices) == 3 else GL_QUADS)
    glNormal3f(*calcular_normal_face(vertices))
    for vertice in vertices:
        glVertex3f(*vertice)
    glEnd()


def desenhar_cubo() -> None:
    """[PRIMITIVAS] Desenha um cubo unitário centrado na origem [-0.5, 0.5]³.

    Conceito CG: todas as 6 faces seguem orientação anti-horária vistas de fora,
    produzindo normais externas exatas nos eixos ±X, ±Y e ±Z.
    """
    faces_unitarias = (
        ((-0.5, -0.5, 0.5), (0.5, -0.5, 0.5), (0.5, 0.5, 0.5), (-0.5, 0.5, 0.5)),
        ((0.5, -0.5, -0.5), (-0.5, -0.5, -0.5), (-0.5, 0.5, -0.5), (0.5, 0.5, -0.5)),
        ((0.5, -0.5, 0.5), (0.5, -0.5, -0.5), (0.5, 0.5, -0.5), (0.5, 0.5, 0.5)),
        ((-0.5, -0.5, -0.5), (-0.5, -0.5, 0.5), (-0.5, 0.5, 0.5), (-0.5, 0.5, -0.5)),
        ((-0.5, 0.5, 0.5), (0.5, 0.5, 0.5), (0.5, 0.5, -0.5), (-0.5, 0.5, -0.5)),
        ((-0.5, -0.5, -0.5), (0.5, -0.5, -0.5), (0.5, -0.5, 0.5), (-0.5, -0.5, 0.5)),
    )
    for face in faces_unitarias:
        desenhar_face(face)


def desenhar_bloco(
    posicao: tuple[float, float, float],
    escala: tuple[float, float, float],
    cor: tuple[float, float, float],
    rotacao: tuple[float, float, float] = (0.0, 0.0, 0.0),
) -> None:
    """[PRIMITIVAS] Transforma o cubo unitário em um paralelepípedo posicionado e colorido.

    Conceito CG: pilha de matrizes (`glPushMatrix`/`glPopMatrix`) isola a ordem
    `T * Rx * Ry * Rz * S` (no espaço do objeto: escala, rotaciona e translada).

    Parâmetros:
        posicao: Coordenadas (x, y, z) do centro do bloco no referencial atual.
        escala: Dimensões (largura, altura, profundidade) aplicadas ao cubo unitário.
        cor: Cor RGB normalizada [0.0, 1.0].
        rotacao: Ângulos de Euler (x, y, z) em graus em torno do centro do bloco.
    """
    glPushMatrix()
    glColor3f(*cor)
    glTranslatef(*posicao)  # TRANSLAÇÃO: posiciona o bloco no espaço do pai.
    for angulo, eixo in zip(rotacao, ((1.0, 0.0, 0.0), (0.0, 1.0, 0.0), (0.0, 0.0, 1.0))):
        if angulo != 0.0:
            glRotatef(angulo, *eixo)  # ROTAÇÃO: inclina o bloco em torno de seu centro.
    glScalef(*escala)  # ESCALA: transforma o cubo unitário nas dimensões finais.
    desenhar_cubo()
    glPopMatrix()


def desenhar_esfera(quadrica, raio: float = 1.0, fatias: int = 10, aneis: int = 6) -> None:
    """[PRIMITIVAS] Desenha uma esfera utilizando uma quádrica GLU pré-alocada.

    Parâmetros:
        quadrica: Ponteiro de quádrica GLU criado após a inicialização do OpenGL.
        raio: Raio da esfera no referencial local.
        fatias: Número de subdivisões longitudinais em torno do eixo Z.
        aneis: Número de subdivisões latitudinais ao longo do eixo Z.
    """
    gluSphere(quadrica, raio, fatias, aneis)


def desenhar_cilindro(
    raio_base: float = 1.0,
    raio_topo: float = 1.0,
    lados: int = 9,
) -> None:
    """[PRIMITIVAS] Constrói cilindro, tronco ou cone fechado no eixo local +Z.

    Conceito CG: gera polígono prismático de comprimento unitário (z de 0.0 a 1.0)
    com normais planas por face lateral e fechamento opcional das duas tampas.

    Parâmetros:
        raio_base: Raio no plano z = 0.0.
        raio_topo: Raio no plano z = 1.0 (use 0.0 para formar um cone).
        lados: Quantidade de facetas ao redor da circunferência.
    """
    for indice in range(lados):
        angulo_a = indice * math.tau / lados
        angulo_b = (indice + 1) * math.tau / lados
        base_a = (raio_base * math.cos(angulo_a), raio_base * math.sin(angulo_a), 0.0)
        base_b = (raio_base * math.cos(angulo_b), raio_base * math.sin(angulo_b), 0.0)
        topo_b = (raio_topo * math.cos(angulo_b), raio_topo * math.sin(angulo_b), 1.0)
        topo_a = (raio_topo * math.cos(angulo_a), raio_topo * math.sin(angulo_a), 1.0)
        desenhar_face(
            (base_a, base_b, topo_a) if raio_topo == 0 else (base_a, base_b, topo_b, topo_a)
        )
        if raio_base > 0:
            desenhar_face(((0.0, 0.0, 0.0), base_b, base_a))
        if raio_topo > 0:
            desenhar_face(((0.0, 0.0, 1.0), topo_a, topo_b))


def desenhar_cone_vertical(
    posicao: tuple[float, float, float],
    raio: float,
    altura: float,
    cor: tuple[float, float, float],
) -> None:
    """[PRIMITIVAS] Desenha um cone fechado apontado verticalmente para +Y.

    Conceito CG: reaproveita o cilindro unitário em +Z aplicando rotação de -90°
    em torno do eixo X e escala independente para base e altura.

    Parâmetros:
        posicao: Coordenadas (x, y, z) do centro da base do cone.
        raio: Raio circular da base do cone.
        altura: Altura do cone ao longo de +Y.
        cor: Cor RGB normalizada [0.0, 1.0].
    """
    glPushMatrix()
    glColor3f(*cor)
    glTranslatef(*posicao)
    glRotatef(-90.0, 1.0, 0.0, 0.0)  # Orienta o eixo local +Z do cilindro para cima (+Y).
    glScalef(raio, raio, altura)
    desenhar_cilindro(1.0, 0.0)
    glPopMatrix()


def desenhar_segmento(
    ponto_inicial: tuple[float, float, float],
    ponto_final: tuple[float, float, float],
    raio: float,
    cor: tuple[float, float, float],
) -> None:
    """[PRIMITIVAS] Desenha um cilindro conectando dois pontos arbitrários no espaço 3D.

    Conceito CG: alinha o eixo local +Z ao vetor `ponto_final - ponto_inicial`
    usando o eixo perpendicular obtido por `(0, 0, 1) x direcao = (-dy, dx, 0)`.

    Parâmetros:
        ponto_inicial: Coordenadas (x, y, z) da extremidade inicial.
        ponto_final: Coordenadas (x, y, z) da extremidade final.
        raio: Raio da seção transversal do segmento.
        cor: Cor RGB normalizada [0.0, 1.0].
    """
    vetor = tuple(fim - inicio for inicio, fim in zip(ponto_inicial, ponto_final))
    comprimento = math.sqrt(sum(componente * componente for componente in vetor))
    if comprimento < 1e-8:
        return

    glPushMatrix()
    glColor3f(*cor)
    glTranslatef(*ponto_inicial)
    # Produto vetorial de +Z com o vetor direção fornece o eixo de rotação ortogonal.
    eixo_rotacao = (-vetor[1], vetor[0], 0.0)
    if math.hypot(*eixo_rotacao[:2]) > 1e-8:
        cosseno = max(-1.0, min(1.0, vetor[2] / comprimento))
        glRotatef(math.degrees(math.acos(cosseno)), *eixo_rotacao)
    elif vetor[2] < 0:
        # Quando o vetor aponta exatamente para -Z, basta inverter 180° em torno de X.
        glRotatef(180.0, 1.0, 0.0, 0.0)
    glScalef(raio, raio, comprimento)
    desenhar_cilindro()
    glPopMatrix()
