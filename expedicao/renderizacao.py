"""Inicialização do estado OpenGL, projeção, câmera manual e composição da cena.

Configura o pipeline fixo (profundidade, normalização, material, sombreamento e
neblina), aplica a matriz de visão inversa sem `gluLookAt` e orquestra a ordem
correta de desenho entre elementos opacos e transparentes.

Tags da apresentação: [CAMERA], [JANELA].
"""

from dataclasses import dataclass

from OpenGL.GL import (
    GL_AMBIENT_AND_DIFFUSE,
    GL_COLOR_BUFFER_BIT,
    GL_COLOR_MATERIAL,
    GL_DEPTH_BUFFER_BIT,
    GL_DEPTH_TEST,
    GL_FLAT,
    GL_FOG,
    GL_FOG_COLOR,
    GL_FOG_END,
    GL_FOG_MODE,
    GL_FOG_START,
    GL_FRONT_AND_BACK,
    GL_LIGHT0,
    GL_LIGHT1,
    GL_LIGHTING,
    GL_LIGHT_MODEL_LOCAL_VIEWER,
    GL_LIGHT_MODEL_TWO_SIDE,
    GL_LINEAR,
    GL_MODELVIEW,
    GL_NORMALIZE,
    GL_PROJECTION,
    GL_SHININESS,
    GL_SMOOTH,
    GL_SPECULAR,
    GL_TRUE,
    glCallList,
    glClear,
    glClearColor,
    glColorMaterial,
    glEnable,
    glFogf,
    glFogfv,
    glFogi,
    glLightModeli,
    glLoadIdentity,
    glMaterialf,
    glMaterialfv,
    glMatrixMode,
    glRotatef,
    glShadeModel,
    glTranslatef,
    glViewport,
)
from OpenGL.GLU import gluPerspective

from expedicao.cenario import Arvore, desenhar_cenario_estatico
from expedicao.configuracoes import (
    BRILHO_GLOBAL,
    CAMPO_VISAO,
    ESPECULAR_GLOBAL,
    FIM_NEBLINA,
    FUNDO_DIA,
    FUNDO_NOITE,
    INICIO_NEBLINA,
    PLANO_DISTANTE,
    PLANO_PROXIMO,
    USAR_SOMBREAMENTO_SUAVE,
    PoseCamera,
)
from expedicao.efeitos import (
    desenhar_chamas,
    desenhar_fumaca,
    desenhar_lua,
    desenhar_marcadores_luz,
)
from expedicao.iluminacao import configurar_iluminacao
from expedicao.matematica import misturar_vetores
from expedicao.painel_controles import PainelControles
from expedicao.personagem import desenhar_personagem
from expedicao.simulacao import EstadoCena


@dataclass
class RecursosCena:
    """Agrupa os recursos alocados na GPU/GLU para uso e liberação segura no encerramento.

    Atributos:
        quadrica: Objeto de quádrica GLU compartilhado entre esferas da cena.
        textura_terreno: Identificador da textura procedural do solo.
        lista_cenario: Identificador da Display List do cenário estático (ou 0 se não compilada).
        painel_controles: Estrutura com a textura da faixa inferior de atalhos.
    """

    quadrica: object
    textura_terreno: int
    lista_cenario: int
    painel_controles: PainelControles


def inicializar_opengl() -> None:
    """[JANELA] Configura o estado global do pipeline OpenGL 2.1 de função fixa.

    Conceito CG: ativa Z-buffer, normalização automática após escalas (`GL_NORMALIZE`),
    materiais via `glColor3f`, modelo de iluminação bilateral e neblina linear.
    """
    glEnable(GL_DEPTH_TEST)
    glEnable(GL_NORMALIZE)  # Preserva módulo unitário das normais após `glScalef`.
    glEnable(GL_LIGHTING)
    glEnable(GL_LIGHT0)
    glEnable(GL_LIGHT1)
    glEnable(GL_COLOR_MATERIAL)
    glColorMaterial(GL_FRONT_AND_BACK, GL_AMBIENT_AND_DIFFUSE)
    glMaterialfv(GL_FRONT_AND_BACK, GL_SPECULAR, ESPECULAR_GLOBAL)
    glMaterialf(GL_FRONT_AND_BACK, GL_SHININESS, BRILHO_GLOBAL)
    glLightModeli(GL_LIGHT_MODEL_LOCAL_VIEWER, GL_TRUE)
    glLightModeli(GL_LIGHT_MODEL_TWO_SIDE, GL_TRUE)
    glShadeModel(GL_SMOOTH if USAR_SOMBREAMENTO_SUAVE else GL_FLAT)

    glEnable(GL_FOG)
    glFogi(GL_FOG_MODE, GL_LINEAR)
    glFogf(GL_FOG_START, INICIO_NEBLINA)
    glFogf(GL_FOG_END, FIM_NEBLINA)


def atualizar_projecao(largura_janela: int, altura_janela: int) -> None:
    """[JANELA] Atualiza a área de desenho e a matriz de projeção perspectiva.

    Conceito CG: recalcula `gluPerspective` mantendo a razão de aspecto ao
    redimensionar a janela e protege contra divisão por zero ao minimizar.

    Parâmetros:
        largura_janela: Largura atual da janela em pixels.
        altura_janela: Altura atual da janela em pixels.
    """
    largura_segura = max(1, largura_janela)
    altura_segura = max(1, altura_janela)
    glViewport(0, 0, largura_segura, altura_segura)
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    gluPerspective(CAMPO_VISAO, largura_segura / altura_segura, PLANO_PROXIMO, PLANO_DISTANTE)
    glMatrixMode(GL_MODELVIEW)


def aplicar_camera(pose: PoseCamera) -> None:
    """[CAMERA] Constrói manualmente a matriz de visão inversa sem usar `gluLookAt`.

    Conceito CG: aplica `Rx(-angulo_vertical) * Ry(-angulo_horizontal) * T(-posicao)`
    em `GL_MODELVIEW` para deslocar o mundo na direção oposta à da câmera.

    Parâmetros:
        pose: Pose alvo contendo coordenadas e ângulos em graus da câmera.
    """
    glMatrixMode(GL_MODELVIEW)
    glLoadIdentity()
    glRotatef(-pose.angulo_vertical, 1.0, 0.0, 0.0)
    glRotatef(-pose.angulo_horizontal, 0.0, 1.0, 0.0)
    glTranslatef(*(-coordenada for coordenada in pose.posicao))


def desenhar_cena(
    estado: EstadoCena,
    recursos: RecursosCena,
    arvores: tuple[Arvore, ...] | None = None,
) -> None:
    """[JANELA] Renderiza um quadro 3D completo respeitando a ordem opaco -> transparente.

    Conceito CG: aplica câmera antes das luzes (para posicioná-las no mundo),
    reaproveita o cenário compilado via Display List e desenha elementos opacos
    antes de qualquer geometria semitransparente (lua e partículas de fumaça).

    Parâmetros:
        estado: Estado atual da simulação.
        recursos: Recursos de GPU compilados para a cena.
        arvores: Coleção de árvores usada apenas como fallback se `lista_cenario` for 0.
    """
    cor_fundo = (*misturar_vetores(FUNDO_NOITE, FUNDO_DIA, estado.fracao_dia), 1.0)
    glClearColor(*cor_fundo)
    glFogfv(GL_FOG_COLOR, cor_fundo)
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

    aplicar_camera(estado.camera)
    configurar_iluminacao(estado)

    if recursos.lista_cenario:
        glCallList(recursos.lista_cenario)
    else:
        desenhar_cenario_estatico(recursos.textura_terreno, arvores or ())

    # Elementos opacos dinâmicos primeiro; elementos com alpha blending por último.
    desenhar_personagem(estado, recursos.quadrica)
    desenhar_marcadores_luz(estado, recursos.quadrica)
    desenhar_chamas(estado.tempo_total)
    desenhar_lua(estado, recursos.quadrica)
    desenhar_fumaca(estado.tempo_total, recursos.quadrica, estado.camera)
