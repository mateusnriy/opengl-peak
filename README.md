# Expedição ao Pico

Cena 3D low-poly inspirada em PEAK, para apresentação de Computação Gráfica.
Tudo é gerado em Python: geometria, textura de terreno e faixa inferior de controles.
Sem assets externos, shaders, VBOs, `numpy` ou controle livre de personagem/câmera.

## Executar

Python 3.10+ e driver com OpenGL 2.1/compatibilidade e GLU, em sessão gráfica.

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
python main.py
```

No Linux, use `python3` se `python` não existir. Se faltar a biblioteca GLU,
instale o pacote do sistema `libglu1-mesa` (Debian/Ubuntu).

O terminal integrado do VS Code Snap pode exportar schemas incompatíveis com o
GTK do sistema, causando aborto na chave `antialiasing` do schema
`org.gnome.settings-daemon.plugins.xsettings`. Antes de carregar as bibliotecas
gráficas, `expedicao/ambiente.py` substitui `GSETTINGS_SCHEMA_DIR` do Snap pelos
schemas do sistema e retira diretórios Snap de `XDG_DATA_DIRS`, somente neste processo.
Schemas personalizados fora do Snap são preservados. `CORRIGIR_ESQUEMAS_SNAP_NO_LINUX`
em `expedicao/configuracoes.py` controla esse ajuste.

Com `DISPLAY` disponível, o programa também prefere X11/XWayland como alternativa
de compatibilidade. Para escolher outro backend, defina `SDL_VIDEODRIVER` antes
de executar, ou ajuste `PREFERIR_X11_NO_LINUX` em `expedicao/configuracoes.py`.
Se houver aborto nativo, execute `python -u main.py --diagnostico` para rastrear
interpretador, variáveis de ambiente e etapa de inicialização.

| Tecla | Ação |
|---|---|
| `Espaço` | Inicia; durante a sequência ou no final, reinicia para o acampamento |
| `R` | Reinicia tudo, incluindo noite e câmera |
| `N` | Alterna suavemente noite/dia; mantém a escolha até reiniciar |
| `Esc` | Fecha a janela |

Janela redimensionável, 1280×720, limite de 60 FPS. A sequência dura 7 s de
amanhecer + 32 s de escalada com pausas suaves nos três platôs; o orbital final
continua até reiniciar. A fogueira e a fumaça se animam em todas as fases.
A escalada acontece sem corda ou âncora. À noite, uma lua azulada ilumina a parte
superior da montanha com `GL_LIGHT2`, um holofote apontado para o topo. A lua e sua
luz desaparecem suavemente no amanhecer e retornam ao alternar para noite com `N`.

## Estrutura Modular do Projeto

```text
opengl-peak/
├── main.py                         # Ponto de entrada: janela, eventos e loop principal
├── requirements.txt                # Dependências (pygame e PyOpenGL)
├── .agents/rules/padroes-codigo.md # Regras de nomenclatura em português e docstrings
└── expedicao/
    ├── configuracoes.py            # Constantes ajustáveis e poses de câmera
    ├── ambiente.py                 # Diagnóstico e saneamento Linux/Snap (antes de pygame/GL)
    ├── matematica.py               # Interpolações, smoothstep, amortecimento e normal de face
    ├── simulacao.py                # EstadoCena, máquina de fases e trajetórias cinemáticas
    ├── primitivas.py               # Face, cubo, bloco, esfera, cilindro, cone e segmento
    ├── terreno.py                  # Textura procedural (ruído periódico + mipmaps) e solo
    ├── cenario.py                  # Montanha, platôs, pico, árvores, acampamento e Display List
    ├── personagem.py               # Hierarquia articulada do escoteiro (pilha de matrizes)
    ├── iluminacao.py               # Sol direcional, fogueira pontual e holofote lunar (Phong)
    ├── efeitos.py                  # Chamas, fumaça ordenada back-to-front, lua e marcadores
    ├── painel_controles.py         # Faixa inferior 2D via projeção ortográfica (`glOrtho`)
    └── renderizacao.py             # Estado OpenGL, projeção, câmera manual e composição 3D
```

## Referência para a Apresentação

Em `expedicao/configuracoes.py`, ajuste durações, cores, alturas, poses de câmera e luzes.
`USAR_SOMBREAMENTO_SUAVE = False` usa `GL_FLAT`; altere para `True` para comparar
com `GL_SMOOTH` (mais evidente na cabeça, lua e fumaça; blocos preservam suas arestas).

| Conceito de Computação Gráfica | Tags | Módulo | Funções / Estruturas Principais |
|---|---|---|---|
| Primitivas manuais e normais (CCW) | `[PRIMITIVAS]` | `expedicao/matematica.py`, `expedicao/primitivas.py` | `calcular_normal_face`, `desenhar_face`, `desenhar_cubo`, `desenhar_bloco`, `desenhar_cilindro`, `desenhar_segmento` |
| Modelagem hierárquica (pilha de matrizes) | `[PERSONAGEM]`, `[BRACO]`, `[PERNA]` | `expedicao/personagem.py` | `desenhar_personagem`, `desenhar_braco`, `desenhar_perna`, `desenhar_cabeca_e_chapeu` |
| Cenário estático e Display List | `[ACAMPAMENTO]`, `[BARRACA]`, `[ARVORES]`, `[PAREDE_1..3]`, `[PLATO_1..3]`, `[PICO_NEVADO]`, `[MASSA_LATERAL]`, `[OTIMIZACAO]` | `expedicao/cenario.py` | `gerar_arvores`, `desenhar_secao_rochosa`, `desenhar_cenario_estatico`, `compilar_cenario_estatico` |
| Textura procedural + Mipmaps | `[TEXTURA]`, `[TERRENO]` | `expedicao/terreno.py` | `_calcular_ruido_periodico`, `criar_textura_terreno`, `desenhar_terreno` |
| Câmera manual (sem `gluLookAt`) e projeção | `[CAMERA]`, `[JANELA]` | `expedicao/renderizacao.py` | `aplicar_camera`, `atualizar_projecao`, `inicializar_opengl`, `desenhar_cena` |
| Iluminação local (3 fontes) e amanhecer | `[ILUMINACAO]`, `[LUA]`, `[ANIM_A6_AMANHECER]` | `expedicao/iluminacao.py` | `configurar_iluminacao`, `configurar_luz_sol`, `configurar_luz_fogueira`, `configurar_luz_lua` |
| Animações, transparência e neblina | `[ANIM_A1_CHAMAS]`, `[ANIM_A5_FUMACA]`, `[MARCADORES]` | `expedicao/efeitos.py` | `desenhar_chamas`, `desenhar_fumaca`, `desenhar_lua`, `desenhar_marcadores_luz` |
| Máquina de estados e trajetórias | `[FASES]`, `[ANIM_A2_CAMERA]`, `[ANIM_A3_ESCALADA]`, `[ANIM_A7_ORBITAL_FINAL]` | `expedicao/simulacao.py` | `EstadoCena`, `atualizar_fases`, `interpolar_camera`, `calcular_posicao_escalada`, `calcular_camera_orbital_final` |
| Interface 2D ortográfica | `[HUD]` | `expedicao/painel_controles.py` | `PainelControles`, `criar_painel_controles`, `desenhar_painel_controles` |
| Bootstrap Linux e loop de eventos | `[AMBIENTE]`, `[JANELA]` | `expedicao/ambiente.py`, `main.py` | `preparar_ambiente_execucao`, `processar_eventos`, `executar_aplicacao` |

Validação de sintaxe e compilação de todos os módulos:

```bash
python -m compileall main.py expedicao
```
