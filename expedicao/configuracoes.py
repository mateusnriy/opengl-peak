"""Constantes ajustáveis e poses de câmera do projeto Expedição ao Pico.

Centraliza parâmetros de janela, fases da narrativa, geometria da montanha,
paleta de cores, textura procedural, iluminação e rota de escalada para facilitar
calibração ao vivo durante a apresentação acadêmica.

Tags da apresentação: [JANELA], [FASES], [CAMERA], [ANIM_A3_ESCALADA],
[TERRENO], [TEXTURA], [ILUMINACAO], [LUA].
"""

from dataclasses import dataclass


@dataclass(frozen=True)
class PoseCamera:
    """Representa a posição e orientação de uma câmera em coordenadas do mundo.

    Atributos:
        posicao: Coordenadas (x, y, z) da câmera no mundo, em unidades de cena.
        angulo_horizontal: Giro horizontal em torno do eixo +Y (equivalente a yaw), em graus.
        angulo_vertical: Inclinação vertical em torno do eixo +X (equivalente a pitch), em graus.
    """

    posicao: tuple[float, float, float]
    angulo_horizontal: float
    angulo_vertical: float


# ================= CONSTANTES AJUSTÁVEIS: AMBIENTE E JANELA =================
# Corrige conflito de schemas GTK exportados pelo terminal integrado do VS Code Snap no Linux.
CORRIGIR_ESQUEMAS_SNAP_NO_LINUX = True
# Alternativa de compatibilidade via X11/XWayland caso o backend Wayland apresente falhas.
PREFERIR_X11_NO_LINUX = True

LARGURA_JANELA, ALTURA_JANELA = 1280, 720
TITULO_JANELA = "Expedição ao Pico | PyOpenGL + pygame"
QUADROS_POR_SEGUNDO = 60
# Limita saltos de tempo ao arrastar/redimensionar a janela para evitar pulo de fases.
DELTA_TEMPO_MAXIMO = 0.1
CAMPO_VISAO = 49.0  # Abertura vertical da lente perspectiva, em graus.
PLANO_PROXIMO, PLANO_DISTANTE = 0.1, 180.0
# False usa GL_FLAT (arestas facetadas low-poly); True usa GL_SMOOTH (interpolação nos vértices).
USAR_SOMBREAMENTO_SUAVE = False
SEMENTE = 47  # Semente fixa para reproduzir exatamente árvores, rochas e textura entre execuções.

# ================= CONSTANTES AJUSTÁVEIS: FASES E ANIMAÇÕES =================
FASE_ACAMPAMENTO = "ACAMPAMENTO"
FASE_TRANSICAO_CAMERA = "TRANSICAO_CAMERA"
FASE_ESCALADA = "ESCALADA"
FASE_FINAL = "FINAL"

DURACAO_TRANSICAO = 7.0  # Duração do amanhecer e movimento de câmera até o paredão, em segundos.
DURACAO_ESCALADA = 32.0  # Altere este valor para acelerar ou desacelerar a subida completa.
SUAVIDADE_CAMERA = 3.6  # Taxa de amortecimento exponencial no seguimento do escalador.
SUAVIDADE_LUZ_MANUAL = 2.5  # Velocidade da transição noite/dia ao pressionar a tecla N.
SUAVIDADE_POSE_PERSONAGEM = 10.0  # Suaviza a transição de braços e pernas ao pausar nos platôs.
VELOCIDADE_ORBITAL = 0.075  # Frequência angular da órbita suave no cume, em radianos por segundo.
AMPLITUDE_ORBITAL = 0.28  # Amplitude máxima do arco orbital ao redor do pico, em radianos.

# ================= CONSTANTES AJUSTÁVEIS: CENÁRIO E CORES =================
ALTURA_PLATO_1, ALTURA_PLATO_2, ALTURA_PLATO_3 = 6.5, 13.0, 19.5
ALTURA_CUME = 23.3  # Topo plano do pico nevado onde o personagem termina em pé.

POSICAO_FOGUEIRA = (-5.6, 0.15, 6.3)
POSICAO_BARRACA = (-10.0, 0.0, 2.8)
POSICAO_SOL = (-22.0, 37.0, 18.0)
# Componente w=0.0 informa ao pipeline fixo que o Sol é uma fonte direcional no infinito.
DIRECAO_SOL = (*POSICAO_SOL, 0.0)
POSICAO_LUA = (-4.0, 28.0, 7.0)
ALVO_LUZ_LUA = (0.0, 21.0, -1.0)
RAIO_LUA = 1.15

COR_LUA = (0.81, 0.88, 1.0)
COR_ROCHA = (0.46, 0.43, 0.38)
COR_PLATO = (0.61, 0.57, 0.46)
COR_NEVE = (0.91, 0.96, 1.0)
COR_TRONCO = (0.28, 0.16, 0.09)
COR_FOLHAS = (0.13, 0.31, 0.24)
COR_BARRACA = (0.95, 0.50, 0.15)
COR_CAMISA = (0.83, 0.70, 0.40)
COR_CALCA = (0.16, 0.28, 0.29)
COR_PELE = (0.82, 0.53, 0.33)
COR_MOCHILA = (0.72, 0.24, 0.12)
COR_TIRANTES_BARRACA = (0.95, 0.77, 0.30)
CORES_CHAMAS = ((1.0, 0.19, 0.035), (1.0, 0.47, 0.04), (1.0, 0.87, 0.30))
COR_FUMACA = (0.42, 0.44, 0.47)

# ================= CONSTANTES AJUSTÁVEIS: TERRENO, TEXTURA E NEBLINA =================
TAMANHO_TERRENO = 120.0
PASSO_TERRENO = 4.0  # Subdivisão da malha para iluminação pontual e neblina variarem pelo solo.
TAMANHO_TEXTURA = 256  # Resolução lateral da textura procedural em pixels.
REPETICOES_TEXTURA = 18.0  # Controla o tamanho das manchas de grama e areia no terreno.
COR_GRAMA = (71, 119, 43)  # RGB 0..255 usado na rasterização da textura.
COR_AREIA = (224, 194, 135)
COR_BASE_TERRENO = (1.0, 1.0, 1.0)  # Branco para não alterar as cores da textura em GL_MODULATE.
LIMIAR_AREIA = 0.43  # Valores menores ampliam a área de areia; maiores favorecem grama.
SUAVIDADE_MISTURA_TERRENO = 0.18
QUANTIDADE_FIOS_GRAMA = 1600
INICIO_NEBLINA, FIM_NEBLINA = 38.0, 85.0

QUANTIDADE_ARVORES = 25
QUANTIDADE_FUMACA = 9
DURACAO_FUMACA = 4.0  # Ciclo de vida completo de cada partícula de fumaça, em segundos.
ALTURA_FUMACA = 3.6
FREQUENCIA_PASSADA = 2.3  # Ciclos de movimento de braços/pernas por segundo, independente do FPS.
ALTURA_QUADRIL = 1.36  # Distância vertical do centro do torso até a sola das botas no chão.

# ================= CONSTANTES AJUSTÁVEIS: ILUMINAÇÃO =================
FUNDO_NOITE, FUNDO_DIA = (0.018, 0.031, 0.075), (0.48, 0.72, 0.83)
AMBIENTE_NOITE, AMBIENTE_DIA = (0.065, 0.085, 0.15), (0.30, 0.32, 0.34)
SOL_NOITE, SOL_DIA = (0.045, 0.065, 0.12), (0.95, 0.88, 0.73)
COR_LUZ_FOGO = (1.0, 0.39, 0.09)
COR_LUZ_LUA = (0.40, 0.56, 0.92)
INTENSIDADE_LUA = 1.15
ABERTURA_LUZ_LUA = 30.0  # Meio-ângulo do cone do holofote lunar: evita clarear o acampamento.
EXPOENTE_LUZ_LUA = 6.0  # Concentração de brilho no centro do feixe lunar.
ATENUACAO_LUA = (1.0, 0.008, 0.0004)  # Coeficientes (constante, linear, quadrática).
INTENSIDADE_FOGO = 2.5
ATENUACAO_FOGO = (1.0, 0.12, 0.028)  # Coeficientes (constante, linear, quadrática).
ESPECULAR_GLOBAL = (0.16, 0.16, 0.16, 1.0)
BRILHO_GLOBAL = 20.0

# ================= CONSTANTES AJUSTÁVEIS: POSES DE CÂMERA E ROTA =================
CAMERA_ACAMPAMENTO = PoseCamera((13.5, 7.8, 24.0), 36.0, -12.0)
CAMERA_PAREDAO = PoseCamera((5.5, 7.0, 26.0), 12.0, -5.0)
# Posição inicial da câmera no cume; orientação é recalculada olhando para o topo na órbita.
POSICAO_INICIAL_CAMERA_FINAL = (7.5, 28.2, 17.0)

# Cada item define (fração_tempo_em_0_1, (x, y, z)_do_torso).
# Pausas nos platôs são representadas por dois quadros-chave consecutivos na mesma posição.
ROTA_ESCALADA = (
    (0.00, (-2.7, ALTURA_QUADRIL, 1.40)),
    # Aproximação por fora da borda, seguida de um passo sobre cada platô.
    (0.03, (-2.7, ALTURA_QUADRIL + 0.9, 2.35)),
    (0.21, (-2.7, ALTURA_PLATO_1 + ALTURA_QUADRIL + 0.3, 2.35)),
    (0.24, (-2.7, ALTURA_PLATO_1 + ALTURA_QUADRIL, 1.30)),
    (0.29, (-2.7, ALTURA_PLATO_1 + ALTURA_QUADRIL, 1.30)),
    (0.32, (-2.7, ALTURA_PLATO_1 + ALTURA_QUADRIL + 0.9, 2.35)),
    (0.50, (2.0, ALTURA_PLATO_2 + ALTURA_QUADRIL + 0.3, 2.35)),
    (0.53, (2.0, ALTURA_PLATO_2 + ALTURA_QUADRIL + 0.05, 1.30)),
    (0.58, (2.0, ALTURA_PLATO_2 + ALTURA_QUADRIL + 0.05, 1.30)),
    (0.61, (2.0, ALTURA_PLATO_2 + ALTURA_QUADRIL + 0.9, 2.35)),
    (0.78, (-0.7, ALTURA_PLATO_3 + ALTURA_QUADRIL + 0.3, 2.35)),
    (0.81, (-0.7, ALTURA_PLATO_3 + ALTURA_QUADRIL + 0.05, 1.30)),
    (0.86, (-0.7, ALTURA_PLATO_3 + ALTURA_QUADRIL + 0.05, 1.30)),
    (0.89, (-0.7, ALTURA_PLATO_3 + ALTURA_QUADRIL + 0.9, 2.35)),
    (0.96, (0.0, ALTURA_CUME + ALTURA_QUADRIL + 0.25, 1.40)),
    (1.00, (0.0, ALTURA_CUME + ALTURA_QUADRIL, -0.25)),
)

# ================= CONSTANTES AJUSTÁVEIS: PAINEL DE CONTROLES (2D) =================
LARGURA_PAINEL_CONTROLES = 660
ALTURA_PAINEL_CONTROLES = 46
TAMANHO_FONTE_PAINEL = 23
TEXTO_PAINEL_CONTROLES = (
    "ESPAÇO  iniciar / reiniciar     R  reiniciar     N  noite / dia     ESC  sair"
)
