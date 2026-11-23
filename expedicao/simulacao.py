"""Estado da simulação, máquina de fases e trajetórias cinemáticas da cena.

Módulo puro em Python (sem OpenGL/pygame) que controla o tempo decorrido, as
transições entre acampamento, paredão, escalada e órbita final, além do ciclo
de amanhecer e da alternância manual entre noite e dia.

Tags da apresentação: [FASES], [ANIM_A2_CAMERA], [ANIM_A3_ESCALADA],
[ANIM_A6_AMANHECER], [ANIM_A7_ORBITAL_FINAL].
"""

import math
from dataclasses import dataclass, field

from expedicao.configuracoes import (
    ALTURA_CUME,
    AMPLITUDE_ORBITAL,
    CAMERA_ACAMPAMENTO,
    CAMERA_PAREDAO,
    DURACAO_ESCALADA,
    DURACAO_TRANSICAO,
    FASE_ACAMPAMENTO,
    FASE_ESCALADA,
    FASE_FINAL,
    FASE_TRANSICAO_CAMERA,
    POSICAO_INICIAL_CAMERA_FINAL,
    ROTA_ESCALADA,
    SUAVIDADE_CAMERA,
    SUAVIDADE_LUZ_MANUAL,
    SUAVIDADE_POSE_PERSONAGEM,
    VELOCIDADE_ORBITAL,
    PoseCamera,
)
from expedicao.matematica import (
    calcular_fator_suavizacao,
    interpolacao_suave,
    interpolar,
    misturar_vetores,
)


@dataclass
class EstadoCena:
    """Agrupa todo o estado temporal e cinemático mutável da expedição.

    Atributos:
        fase: Nome da etapa atual (`ACAMPAMENTO`, `TRANSICAO_CAMERA`, `ESCALADA` ou `FINAL`).
        tempo_fase: Tempo decorrido dentro da fase corrente, em segundos.
        tempo_total: Tempo acumulado desde o início ou último reinício, em segundos.
        fracao_dia: Nível efetivo de claridade do ambiente entre 0.0 (noite) e 1.0 (dia).
        dia_manual: Sobreposição escolhida pela tecla N (`0.0`, `1.0`) ou `None` no ciclo automático.
        camera: Pose atual da câmera aplicada à matriz de visão neste quadro.
        posicao_personagem: Coordenadas (x, y, z) do centro do torso do escoteiro no mundo.
        em_movimento: Indica se o personagem está se deslocando entre pontos da rota.
        peso_escalada: Fator contínuo [0.0, 1.0] que suaviza a pose entre descanso e escalada.
        progresso_escalada: Progresso normalizado [0.0, 1.0] ao longo da fase de escalada.
    """

    fase: str = FASE_ACAMPAMENTO
    tempo_fase: float = 0.0
    tempo_total: float = 0.0
    fracao_dia: float = 0.0
    dia_manual: float | None = None
    camera: PoseCamera = field(default_factory=lambda: CAMERA_ACAMPAMENTO)
    posicao_personagem: tuple[float, float, float] = ROTA_ESCALADA[0][1]
    em_movimento: bool = False
    peso_escalada: float = 0.0
    progresso_escalada: float = 0.0


def interpolar_camera(
    camera_inicial: PoseCamera,
    camera_final: PoseCamera,
    progresso: float,
) -> PoseCamera:
    """[ANIM_A2_CAMERA] Interpola suavemente posição e orientação entre duas câmeras.

    Conceito CG: interpolação suave (smoothstep) dos parâmetros de visão usados
    depois para compor manualmente a matriz inversa em `aplicar_camera`.

    Parâmetros:
        camera_inicial: Pose de partida da câmera.
        camera_final: Pose de destino da câmera.
        progresso: Progresso normalizado esperado entre 0.0 e 1.0.

    Retorno:
        Nova instância imutável de `PoseCamera` intermediária.
    """
    fator_suave = interpolacao_suave(progresso)
    return PoseCamera(
        misturar_vetores(camera_inicial.posicao, camera_final.posicao, fator_suave),
        interpolar(camera_inicial.angulo_horizontal, camera_final.angulo_horizontal, fator_suave),
        interpolar(camera_inicial.angulo_vertical, camera_final.angulo_vertical, fator_suave),
    )


def calcular_posicao_escalada(progresso: float) -> tuple[tuple[float, float, float], bool]:
    """[ANIM_A3_ESCALADA] Calcula a posição do escalador e o estado de movimento na rota.

    Conceito CG: interpolação por trechos entre quadros-chave (*keyframes*) com
    suavização local; trechos com início e fim idênticos geram pausas nos platôs.

    Parâmetros:
        progresso: Fração normalizada [0.0, 1.0] da duração total da escalada.

    Retorno:
        Tupla `(posicao_torso, em_movimento)` com coordenadas (x, y, z) e booleano ativo.
    """
    progresso_limitado = max(0.0, min(1.0, progresso))
    for (tempo_inicial, posicao_inicial), (tempo_final, posicao_final) in zip(
        ROTA_ESCALADA, ROTA_ESCALADA[1:]
    ):
        if progresso_limitado <= tempo_final:
            fator_local = interpolacao_suave(
                (progresso_limitado - tempo_inicial) / max(tempo_final - tempo_inicial, 1e-9)
            )
            em_movimento = posicao_inicial != posicao_final and progresso_limitado < 1.0
            return misturar_vetores(posicao_inicial, posicao_final, fator_local), em_movimento
    return ROTA_ESCALADA[-1][1], False


def calcular_camera_orbital_final(tempo_fase: float) -> PoseCamera:
    """[ANIM_A7_ORBITAL_FINAL] Calcula pose da câmera em órbita pendular ao redor do cume.

    Conceito CG: rotação de ponto no plano XZ em torno do eixo +Y com ângulo senoidal
    contínuo em `t=0` e orientação trigonométrica (`atan2`) voltada ao alvo no cume.

    Parâmetros:
        tempo_fase: Tempo decorrido na fase final, em segundos.

    Retorno:
        Instância de `PoseCamera` posicionada no arco orbital mirando o pico.
    """
    alvo = (0.0, ALTURA_CUME + 1.0, 0.0)
    x_base, y_base, z_base = POSICAO_INICIAL_CAMERA_FINAL
    angulo = AMPLITUDE_ORBITAL * math.sin(tempo_fase * VELOCIDADE_ORBITAL)
    cosseno = math.cos(angulo)
    seno = math.sin(angulo)
    posicao = (x_base * cosseno + z_base * seno, y_base, z_base * cosseno - x_base * seno)
    delta_x, delta_y, delta_z = (
        coord_alvo - coord_camera for coord_camera, coord_alvo in zip(posicao, alvo)
    )
    # Como a câmera observa o sentido -Z no espaço local, invertendo sinais alinhamos ao alvo.
    angulo_horizontal = math.degrees(math.atan2(-delta_x, -delta_z))
    angulo_vertical = math.degrees(math.atan2(delta_y, math.hypot(delta_x, delta_z)))
    return PoseCamera(posicao, angulo_horizontal, angulo_vertical)


def iniciar_expedicao(estado: EstadoCena) -> None:
    """Inicia a sequência automática a partir da fase inicial de acampamento.

    Parâmetros:
        estado: Estado atual da cena a ser transitado para a transição de câmera.
    """
    estado.fase = FASE_TRANSICAO_CAMERA
    estado.tempo_fase = 0.0


def alternar_ciclo_noite_dia(estado: EstadoCena) -> None:
    """Alterna manualmente entre noite e dia mantendo a escolha até o reinício.

    Parâmetros:
        estado: Estado da cena onde `dia_manual` será alternado entre `0.0` e `1.0`.
    """
    referencia = estado.fracao_dia if estado.dia_manual is None else estado.dia_manual
    estado.dia_manual = 0.0 if referencia >= 0.5 else 1.0


def atualizar_fases(estado: EstadoCena, delta_tempo: float) -> None:
    """[FASES] Avança a máquina de estados, câmera, escalador, pose e ciclo do dia.

    [ANIM_A6_AMANHECER] O valor `fracao_dia` acompanha o smoothstep da transição ou
    converge suavemente para a escolha manual da tecla N.

    Parâmetros:
        estado: Estrutura mutável com o estado corrente da cena.
        delta_tempo: Intervalo de tempo decorrido desde o quadro anterior, em segundos.
    """
    delta_tempo = max(0.0, delta_tempo)
    estado.tempo_total += delta_tempo
    estado.tempo_fase += delta_tempo

    # Preserva excedentes de tempo nas viradas de fase para manter sincronismo exato.
    while True:
        if estado.fase == FASE_TRANSICAO_CAMERA and estado.tempo_fase >= DURACAO_TRANSICAO:
            estado.tempo_fase -= DURACAO_TRANSICAO
            estado.fase = FASE_ESCALADA
        elif estado.fase == FASE_ESCALADA and estado.tempo_fase >= DURACAO_ESCALADA:
            estado.tempo_fase -= DURACAO_ESCALADA
            estado.fase = FASE_FINAL
        else:
            break

    if estado.fase == FASE_ACAMPAMENTO:
        estado.camera = CAMERA_ACAMPAMENTO
        dia_automatico = 0.0
    elif estado.fase == FASE_TRANSICAO_CAMERA:
        progresso_transicao = estado.tempo_fase / DURACAO_TRANSICAO
        estado.camera = interpolar_camera(CAMERA_ACAMPAMENTO, CAMERA_PAREDAO, progresso_transicao)
        dia_automatico = interpolacao_suave(progresso_transicao)
    elif estado.fase == FASE_ESCALADA:
        estado.progresso_escalada = min(1.0, estado.tempo_fase / DURACAO_ESCALADA)
        estado.posicao_personagem, estado.em_movimento = calcular_posicao_escalada(
            estado.progresso_escalada
        )
        pos_x, pos_y, _ = estado.posicao_personagem
        # A pose de seguimento coincide com CAMERA_PAREDAO no instante inicial.
        alvo_seguimento = PoseCamera((5.5 + pos_x * 0.18, pos_y + 5.64, 26.0), 12.0, -5.0)
        alvo = interpolar_camera(CAMERA_PAREDAO, alvo_seguimento, estado.progresso_escalada / 0.15)
        fator_chegada = (estado.progresso_escalada - 0.88) / 0.12
        alvo = interpolar_camera(alvo, calcular_camera_orbital_final(0.0), fator_chegada)
        fator_suave = calcular_fator_suavizacao(SUAVIDADE_CAMERA, delta_tempo)
        estado.camera = PoseCamera(
            misturar_vetores(estado.camera.posicao, alvo.posicao, fator_suave),
            interpolar(estado.camera.angulo_horizontal, alvo.angulo_horizontal, fator_suave),
            interpolar(estado.camera.angulo_vertical, alvo.angulo_vertical, fator_suave),
        )
        dia_automatico = 1.0
    else:
        estado.posicao_personagem = ROTA_ESCALADA[-1][1]
        estado.progresso_escalada = 1.0
        estado.em_movimento = False
        alvo = calcular_camera_orbital_final(estado.tempo_fase)
        fator_suave = calcular_fator_suavizacao(SUAVIDADE_CAMERA, delta_tempo)
        estado.camera = PoseCamera(
            misturar_vetores(estado.camera.posicao, alvo.posicao, fator_suave),
            interpolar(estado.camera.angulo_horizontal, alvo.angulo_horizontal, fator_suave),
            interpolar(estado.camera.angulo_vertical, alvo.angulo_vertical, fator_suave),
        )
        dia_automatico = 1.0

    # Transiciona suavemente a postura dos membros entre descanso (0.0) e escalada (1.0).
    peso_alvo = 1.0 if estado.em_movimento else 0.0
    estado.peso_escalada = interpolar(
        estado.peso_escalada,
        peso_alvo,
        calcular_fator_suavizacao(SUAVIDADE_POSE_PERSONAGEM, delta_tempo),
    )

    if estado.dia_manual is None:
        estado.fracao_dia = dia_automatico
    else:
        estado.fracao_dia = interpolar(
            estado.fracao_dia,
            estado.dia_manual,
            calcular_fator_suavizacao(SUAVIDADE_LUZ_MANUAL, delta_tempo),
        )
