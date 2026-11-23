"""Expedição ao Pico — ponto de entrada da demonstração acadêmica em OpenGL 2.1.

Python 3.10+. Execute: `python main.py`. Não há imagens ou modelos externos.
Decisões: o escalador sobe automaticamente; N sobrepõe o ciclo automático até
reiniciar; a escalada não usa corda. A lua ilumina o alto da montanha à noite.
O pico tem topo achatado para o personagem terminar em uma superfície sólida.
Unidades: Y aponta para cima; a face escalável é Z=0; a câmera fica em Z positivo.
"""

from expedicao.ambiente import preparar_ambiente_execucao, registrar_diagnostico

# O ajuste de ambiente e esquemas Linux precisa ocorrer ANTES de importar `pygame` e
# `PyOpenGL`, evitando abortos do GLib no terminal integrado do VS Code Snap.
preparar_ambiente_execucao(__file__)
registrar_diagnostico("Importando pygame, PyOpenGL e módulos gráficos...")

import pygame
from OpenGL.GL import glDeleteLists, glDeleteTextures, glGetString, GL_VERSION
from OpenGL.GLU import GLU_SMOOTH, gluDeleteQuadric, gluNewQuadric, gluQuadricNormals

from expedicao.cenario import compilar_cenario_estatico, gerar_arvores
from expedicao.configuracoes import (
    ALTURA_JANELA,
    DELTA_TEMPO_MAXIMO,
    DURACAO_ESCALADA,
    DURACAO_FUMACA,
    DURACAO_TRANSICAO,
    FASE_ACAMPAMENTO,
    LARGURA_JANELA,
    QUADROS_POR_SEGUNDO,
    TITULO_JANELA,
)
from expedicao.painel_controles import criar_painel_controles, desenhar_painel_controles
from expedicao.renderizacao import (
    RecursosCena,
    atualizar_projecao,
    desenhar_cena,
    inicializar_opengl,
)
from expedicao.simulacao import (
    EstadoCena,
    alternar_ciclo_noite_dia,
    atualizar_fases,
    iniciar_expedicao,
)
from expedicao.terreno import criar_textura_terreno


def validar_configuracoes() -> None:
    """Garante que as durações configuradas das animações sejam estritamente positivas."""
    if min(DURACAO_TRANSICAO, DURACAO_ESCALADA, DURACAO_FUMACA) <= 0.0:
        raise ValueError("As durações das animações precisam ser maiores que zero.")


def processar_eventos(
    estado: EstadoCena,
    largura_janela: int,
    altura_janela: int,
) -> tuple[bool, EstadoCena, int, int]:
    """Processa eventos da fila do `pygame` (janela, redimensionamento e teclas).

    Parâmetros:
        estado: Estado atual da simulação antes dos eventos deste quadro.
        largura_janela: Largura corrente da janela em pixels.
        altura_janela: Altura corrente da janela em pixels.

    Retorno:
        Tupla `(continuar_execucao, novo_estado, largura_atualizada, altura_atualizada)`.
    """
    executando = True
    for evento in pygame.event.get():
        if evento.type == pygame.QUIT:
            executando = False
        elif evento.type in (pygame.VIDEORESIZE, pygame.WINDOWSIZECHANGED):
            # No pygame 2, redimensionar preserva o contexto OpenGL sem recriar `set_mode`.
            largura_janela, altura_janela = pygame.display.get_window_size()
            atualizar_projecao(largura_janela, altura_janela)
        elif evento.type == pygame.KEYDOWN:
            if evento.key == pygame.K_ESCAPE:
                executando = False
            elif evento.key == pygame.K_r or (
                evento.key == pygame.K_SPACE and estado.fase != FASE_ACAMPAMENTO
            ):
                estado = EstadoCena()
            elif evento.key == pygame.K_SPACE:
                iniciar_expedicao(estado)
            elif evento.key == pygame.K_n:
                alternar_ciclo_noite_dia(estado)
    return executando, estado, largura_janela, altura_janela


def executar_aplicacao() -> None:
    """Inicializa contexto OpenGL 2.1, compila recursos da cena e executa o loop a 60 FPS."""
    validar_configuracoes()
    registrar_diagnostico("Inicializando vídeo e fontes do pygame...")
    pygame.display.init()
    registrar_diagnostico(f"Backend de vídeo ativo: {pygame.display.get_driver()}")
    pygame.font.init()

    quadrica = None
    textura_terreno = 0
    lista_cenario = 0
    painel_controles = None
    try:
        pygame.display.gl_set_attribute(pygame.GL_CONTEXT_MAJOR_VERSION, 2)
        pygame.display.gl_set_attribute(pygame.GL_CONTEXT_MINOR_VERSION, 1)
        pygame.display.gl_set_attribute(pygame.GL_DEPTH_SIZE, 24)
        pygame.display.gl_set_attribute(pygame.GL_DOUBLEBUFFER, 1)

        registrar_diagnostico("Criando janela OpenGL...")
        pygame.display.set_mode(
            (LARGURA_JANELA, ALTURA_JANELA),
            pygame.OPENGL | pygame.DOUBLEBUF | pygame.RESIZABLE,
        )
        registrar_diagnostico(f"Versão OpenGL ativa: {glGetString(GL_VERSION)!r}")
        pygame.display.set_caption(TITULO_JANELA)

        inicializar_opengl()
        largura_janela, altura_janela = pygame.display.get_window_size()
        atualizar_projecao(largura_janela, altura_janela)

        quadrica = gluNewQuadric()
        gluQuadricNormals(quadrica, GLU_SMOOTH)
        textura_terreno = criar_textura_terreno()
        arvores = gerar_arvores()
        lista_cenario = compilar_cenario_estatico(textura_terreno, arvores)
        painel_controles = criar_painel_controles()

        recursos = RecursosCena(
            quadrica=quadrica,
            textura_terreno=textura_terreno,
            lista_cenario=lista_cenario,
            painel_controles=painel_controles,
        )
        estado = EstadoCena()
        registrar_diagnostico("Cena pronta; entrando no loop de renderização.")

        relogio = pygame.time.Clock()
        executando = True
        while executando:
            # Limita saltos após pausas/arrastes de janela para não pular fases da animação.
            delta_tempo = min(relogio.tick(QUADROS_POR_SEGUNDO) / 1000.0, DELTA_TEMPO_MAXIMO)
            executando, estado, largura_janela, altura_janela = processar_eventos(
                estado, largura_janela, altura_janela
            )
            if not executando:
                break

            atualizar_fases(estado, delta_tempo)
            desenhar_cena(estado, recursos, arvores)
            desenhar_painel_controles(recursos.painel_controles, largura_janela, altura_janela)
            pygame.display.flip()
    finally:
        if lista_cenario:
            glDeleteLists(lista_cenario, 1)
        if quadrica is not None:
            gluDeleteQuadric(quadrica)
        texturas = [
            identificador
            for identificador in (
                textura_terreno,
                painel_controles.identificador_textura if painel_controles is not None else 0,
            )
            if identificador
        ]
        if texturas:
            glDeleteTextures(texturas)
        pygame.quit()


if __name__ == "__main__":
    executar_aplicacao()
