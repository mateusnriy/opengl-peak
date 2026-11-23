"""Funções matemáticas puras para interpolação, suavização e normais geométricas.

Módulo sem dependências gráficas, usado na geração da textura procedural, na
cinemática das animações e no cálculo manual de normais pelo pipeline fixo.
"""

import math


def interpolar(valor_inicial: float, valor_final: float, fator: float) -> float:
    """Calcula a interpolação linear escalar (lerp) entre dois valores.

    Conceito CG: interpolação linear parametrizada por `fator` em [0, 1].

    Parâmetros:
        valor_inicial: Valor de saída quando `fator` é 0.0.
        valor_final: Valor de saída quando `fator` é 1.0.
        fator: Fração de progresso entre os extremos.

    Retorno:
        Valor escalar interpolado entre `valor_inicial` e `valor_final`.
    """
    return valor_inicial + (valor_final - valor_inicial) * fator


def misturar_vetores(
    vetor_inicial: tuple[float, ...],
    vetor_final: tuple[float, ...],
    fator: float,
) -> tuple[float, ...]:
    """Interpola linearmente dois vetores ou cores RGB componente a componente.

    Conceito CG: mistura linear de coordenadas 3D ou canais de cor.

    Parâmetros:
        vetor_inicial: Tupla numérica inicial (ex.: posição ou cor RGB).
        vetor_final: Tupla numérica final com o mesmo número de componentes.
        fator: Fração de mistura entre `vetor_inicial` (0.0) e `vetor_final` (1.0).

    Retorno:
        Tupla contendo cada componente interpolado separadamente.
    """
    return tuple(
        interpolar(componente_a, componente_b, fator)
        for componente_a, componente_b in zip(vetor_inicial, vetor_final)
    )


def interpolacao_suave(fator: float) -> float:
    """Aplica a curva hermite cúbica clássica (smoothstep) limitada ao intervalo [0, 1].

    Conceito CG: curva S(t) = 3t² - 2t³ com derivadas nulas nas extremidades,
    garantindo aceleração e desaceleração contínuas em câmera, escalada e amanhecer.

    Parâmetros:
        fator: Valor de entrada a ser saturado em [0.0, 1.0] e suavizado.

    Retorno:
        Fator suavizado no intervalo fechado [0.0, 1.0].
    """
    fator_limitado = max(0.0, min(1.0, fator))
    return fator_limitado * fator_limitado * (3.0 - 2.0 * fator_limitado)


def calcular_fator_suavizacao(velocidade: float, delta_tempo: float) -> float:
    """Calcula o fator de amortecimento exponencial independente da taxa de quadros.

    Conceito CG: resposta exponencial contínua `1 - exp(-velocidade * delta_tempo)`
    que produz o mesmo deslocamento visual em 30, 60 ou 144 FPS.

    Parâmetros:
        velocidade: Constante positiva de rapidez da aproximação (1/segundos).
        delta_tempo: Intervalo decorrido desde o último quadro, em segundos.

    Retorno:
        Fator de interpolação no intervalo [0.0, 1.0).
    """
    return 1.0 - math.exp(-velocidade * max(0.0, delta_tempo))


def calcular_normal_face(
    vertices: tuple[tuple[float, float, float], ...],
) -> tuple[float, float, float]:
    """Calcula o vetor normal unitário de um triângulo ou quadrilátero plano.

    Conceito CG: produto vetorial `(B - A) x (C - A)` normalizado para vértices
    ordenados no sentido anti-horário (CCW), necessário para o cálculo de iluminação.

    Parâmetros:
        vertices: Sequência de pelo menos 3 vértices (x, y, z) no espaço do objeto.

    Retorno:
        Tupla unitária (nx, ny, nz) perpendicular ao plano da face.
    """
    vertice_a, vertice_b, vertice_c = vertices[:3]
    aresta_u = tuple(vertice_b[indice] - vertice_a[indice] for indice in range(3))
    aresta_v = tuple(vertice_c[indice] - vertice_a[indice] for indice in range(3))
    normal_bruta = (
        aresta_u[1] * aresta_v[2] - aresta_u[2] * aresta_v[1],
        aresta_u[2] * aresta_v[0] - aresta_u[0] * aresta_v[2],
        aresta_u[0] * aresta_v[1] - aresta_u[1] * aresta_v[0],
    )
    comprimento = math.sqrt(sum(componente * componente for componente in normal_bruta))
    # Evita divisão por zero caso vértices colineares produzam área nula.
    return tuple(componente / max(comprimento, 1e-9) for componente in normal_bruta)
