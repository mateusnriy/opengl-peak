"""Configuração das fontes de luz e do modelo de iluminação local (Phong).

Gerencia a luz ambiente global e as três fontes distintas do pipeline fixo:
Sol direcional (`GL_LIGHT0`), fogueira pontual com tremulação e atenuação
(`GL_LIGHT1`) e holofote lunar azulado dirigido ao topo (`GL_LIGHT2`).

Tags da apresentação: [ILUMINACAO], [LUA], [ANIM_A6_AMANHECER].
"""

import math

from OpenGL.GL import (
    GL_AMBIENT,
    GL_CONSTANT_ATTENUATION,
    GL_DIFFUSE,
    GL_LIGHT0,
    GL_LIGHT1,
    GL_LIGHT2,
    GL_LIGHT_MODEL_AMBIENT,
    GL_LINEAR_ATTENUATION,
    GL_POSITION,
    GL_QUADRATIC_ATTENUATION,
    GL_SPECULAR,
    GL_SPOT_CUTOFF,
    GL_SPOT_DIRECTION,
    GL_SPOT_EXPONENT,
    glDisable,
    glEnable,
    glLightf,
    glLightfv,
    glLightModelfv,
)

from expedicao.configuracoes import (
    ABERTURA_LUZ_LUA,
    ALVO_LUZ_LUA,
    AMBIENTE_DIA,
    AMBIENTE_NOITE,
    ATENUACAO_FOGO,
    ATENUACAO_LUA,
    COR_LUZ_FOGO,
    COR_LUZ_LUA,
    DIRECAO_SOL,
    EXPOENTE_LUZ_LUA,
    INTENSIDADE_FOGO,
    INTENSIDADE_LUA,
    POSICAO_FOGUEIRA,
    POSICAO_LUA,
    SOL_DIA,
    SOL_NOITE,
)
from expedicao.matematica import interpolacao_suave, misturar_vetores
from expedicao.simulacao import EstadoCena


def configurar_luz_sol(fracao_dia: float) -> None:
    """[ANIM_A6_AMANHECER] Configura a fonte direcional do Sol (`GL_LIGHT0`).

    Conceito CG: coordenada homogênea `w=0.0` em `GL_POSITION` define raios
    paralelos vindos do infinito, sem atenuação por distância.

    Parâmetros:
        fracao_dia: Nível de claridade entre 0.0 (noite) e 1.0 (dia).
    """
    cor_sol = misturar_vetores(SOL_NOITE, SOL_DIA, fracao_dia)
    glLightfv(GL_LIGHT0, GL_POSITION, DIRECAO_SOL)
    glLightfv(GL_LIGHT0, GL_AMBIENT, (*(canal * 0.12 for canal in cor_sol), 1.0))
    glLightfv(GL_LIGHT0, GL_DIFFUSE, (*cor_sol, 1.0))
    glLightfv(GL_LIGHT0, GL_SPECULAR, (*(canal * 0.55 for canal in cor_sol), 1.0))


def configurar_luz_fogueira(tempo_total: float) -> None:
    """Configura a luz pontual da fogueira (`GL_LIGHT1`) com tremulação e atenuação.

    Conceito CG: coordenada homogênea `w=1.0` define fonte posicional local;
    a soma de senoides simula oscilação orgânica e determinística do fogo.

    Parâmetros:
        tempo_total: Tempo acumulado da cena em segundos, usado na tremulação.
    """
    tremulacao = (
        1.0
        + 0.08 * math.sin(tempo_total * 11.0)
        + 0.025 * math.sin(tempo_total * 37.7 + math.sin(tempo_total * 6.3))
    )
    intensidade = INTENSIDADE_FOGO * tremulacao
    cor_fogo = tuple(canal * intensidade for canal in COR_LUZ_FOGO)
    pos_x, pos_y, pos_z = POSICAO_FOGUEIRA

    glLightfv(GL_LIGHT1, GL_POSITION, (pos_x, pos_y + 0.85, pos_z, 1.0))
    glLightfv(GL_LIGHT1, GL_AMBIENT, (0.025, 0.008, 0.002, 1.0))
    glLightfv(GL_LIGHT1, GL_DIFFUSE, (*cor_fogo, 1.0))
    glLightfv(GL_LIGHT1, GL_SPECULAR, (*(canal * 0.45 for canal in cor_fogo), 1.0))
    for parametro, valor in zip(
        (GL_CONSTANT_ATTENUATION, GL_LINEAR_ATTENUATION, GL_QUADRATIC_ATTENUATION),
        ATENUACAO_FOGO,
    ):
        glLightf(GL_LIGHT1, parametro, valor)


def configurar_luz_lua(fracao_dia: float) -> None:
    """[LUA] Configura o holofote azulado (`GL_LIGHT2`) apontado para o topo da montanha.

    Conceito CG: spotlight posicional com ângulo de corte restrito e ambiente nulo
    para iluminar as seções superiores à noite sem clarear o acampamento inferior.

    Parâmetros:
        fracao_dia: Nível de claridade entre 0.0 (noite) e 1.0 (dia).
    """
    fator_noite = 1.0 - interpolacao_suave(fracao_dia)
    if fator_noite <= 0.001:
        glDisable(GL_LIGHT2)
        return

    glEnable(GL_LIGHT2)
    glLightfv(GL_LIGHT2, GL_POSITION, (*POSICAO_LUA, 1.0))
    direcao = tuple(alvo - origem for origem, alvo in zip(POSICAO_LUA, ALVO_LUZ_LUA))
    glLightfv(GL_LIGHT2, GL_SPOT_DIRECTION, direcao)
    glLightf(GL_LIGHT2, GL_SPOT_CUTOFF, ABERTURA_LUZ_LUA)
    glLightf(GL_LIGHT2, GL_SPOT_EXPONENT, EXPOENTE_LUZ_LUA)

    cor_lua = tuple(canal * INTENSIDADE_LUA * fator_noite for canal in COR_LUZ_LUA)
    glLightfv(GL_LIGHT2, GL_AMBIENT, (0.0, 0.0, 0.0, 1.0))
    glLightfv(GL_LIGHT2, GL_DIFFUSE, (*cor_lua, 1.0))
    glLightfv(GL_LIGHT2, GL_SPECULAR, (*(canal * 0.45 for canal in cor_lua), 1.0))
    for parametro, valor in zip(
        (GL_CONSTANT_ATTENUATION, GL_LINEAR_ATTENUATION, GL_QUADRATIC_ATTENUATION),
        ATENUACAO_LUA,
    ):
        glLightf(GL_LIGHT2, parametro, valor)


def configurar_iluminacao(estado: EstadoCena) -> None:
    """[ILUMINACAO] Atualiza a luz ambiente global e as três fontes da cena no quadro atual.

    Conceito CG: deve ser chamada DEPOIS da matriz de câmera em `GL_MODELVIEW` para
    que posições e direções das luzes permaneçam fixas em coordenadas do mundo.

    Parâmetros:
        estado: Estado atual da cena contendo `fracao_dia` e `tempo_total`.
    """
    ambiente_atual = (*misturar_vetores(AMBIENTE_NOITE, AMBIENTE_DIA, estado.fracao_dia), 1.0)
    glLightModelfv(GL_LIGHT_MODEL_AMBIENT, ambiente_atual)
    configurar_luz_sol(estado.fracao_dia)
    configurar_luz_fogueira(estado.tempo_total)
    configurar_luz_lua(estado.fracao_dia)
