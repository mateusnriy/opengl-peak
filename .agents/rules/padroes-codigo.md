---
trigger: always_on
---

# Padrões de Código e Arquitetura — Expedição ao Pico

Estas regras definem a arquitetura modular, as convenções de nomenclatura em português e o padrão de documentação do projeto **Expedição ao Pico**.

## 1. Escopo Técnico de Computação Gráfica
- O projeto utiliza exclusivamente **Python 3.10+**, **OpenGL 2.1 (pipeline de função fixa)**, **GLU** e **pygame**.
- **Proibido introduzir:** shaders (GLSL), VBOs/VAOs, `numpy`, `gluLookAt`, arquivos externos de imagem/modelo 3D ou controle livre de câmera/personagem.
- Toda geometria, textura procedural, iluminação de Phong local, modelagem hierárquica e faixa de controles deve permanecer 100% gerada em código Python.

## 2. Nomenclatura Legível em Português
- **Arquivo de entrada na raiz:** deve permanecer `main.py`.
- **Módulos internos (`expedicao/*.py`):** nomes em `snake_case`, legíveis e em português claro, sem abreviações crípticas ou anglicismos (ex.: `configuracoes.py`, `renderizacao.py`, `painel_controles.py`).
- **Classes e dataclasses:** `PascalCase` em português (ex.: `PoseCamera`, `EstadoCena`, `Arvore`, `PainelControles`, `RecursosCena`).
- **Funções, métodos, parâmetros e variáveis:** `snake_case` em português, usando verbos de ação claros nas funções (`calcular_*`, `desenhar_*`, `configurar_*`, `criar_*`, `atualizar_*`, `aplicar_*`, `gerar_*`, `processar_*`).
  - Usar sempre termos claros em português: `delta_tempo` (não `dt`), `semente` (não `seed`), `angulo_horizontal` e `angulo_vertical` (não `yaw` e `pitch`), `interpolacao_suave` (não `smoothstep`), `painel_controles` (não `hud`), `POSICAO_*` (não `POS_*`), `QUADROS_POR_SEGUNDO` (não `FPS`).
  - Evitar identificadores de uma única letra, exceto coordenadas matemáticas consagradas (`x`, `y`, `z`, `u`, `v`) e índices triviais quando o contexto for imediato.
- **Constantes:** `MAIÚSCULAS_COM_SUBLINHADO` em português.
- **Exceções técnicas inevitáveis:** chamadas de API do `OpenGL.GL`, `OpenGL.GLU` e `pygame`, variáveis de ambiente do sistema operacional (`GSETTINGS_SCHEMA_DIR`, `XDG_DATA_DIRS`, `SDL_VIDEODRIVER`), o arquivo raiz `main.py` e protocolos especiais do Python (`__init__.py`, `__name__ == "__main__"`).

## 3. Docstrings e Comentários Estratégicos
- **Todo módulo** deve iniciar com uma docstring de 2 a 4 linhas descrevendo sua responsabilidade, os conceitos de Computação Gráfica aplicados e as tags `[...]` da apresentação presentes nele.
- **Toda classe / `@dataclass`** deve ter docstring explicando o que representa e uma seção `Atributos:` documentando cada campo e sua unidade.
- **Toda função e método** (inclusive auxiliares internas) deve ter docstring direta e objetiva contendo:
  - Resumo em uma frase clara do que faz;
  - `Conceito CG:` quando envolver matemática vetorial, iluminação, projeção, textura ou pipeline OpenGL;
  - `Parâmetros:` listando todos os parâmetros com significado e unidade/faixa;
  - `Retorno:` descrevendo o valor retornado quando não for `None`.
- **Comentários inline estratégicos:** explicar o *porquê* e o efeito visual/matemático (ordem de transformações `T * R * S`, vértices em sentido anti-horário CCW, `w=0` vs. `w=1`, envio de luzes após a câmera, ordenação *back-to-front* com `glDepthMask(GL_FALSE)`, subdivisão da malha para luz por vértice, bootstrap Linux antes de importar `pygame`/`OpenGL`, efeito visual das constantes em `configuracoes.py`). Nunca comentar sintaxe trivial de Python.

## 4. Invariantes de Arquitetura (DAG Sem Ciclos)
- **Camada 1 (Python puro):** `expedicao/__init__.py`, `expedicao/configuracoes.py`, `expedicao/ambiente.py`, `expedicao/matematica.py` e `expedicao/simulacao.py` **nunca** devem importar `pygame`, `OpenGL.GL` ou `OpenGL.GLU`.
- `expedicao/__init__.py` deve permanecer sem imports de submódulos.
- Em `main.py`, `preparar_ambiente_execucao(__file__)` deve ser executada **antes** de importar `pygame`, `OpenGL` ou qualquer módulo gráfico de `expedicao/`.
- Não calcular geometria aleatória no tempo de importação; gerar dados determinísticos explicitamente em tempo de inicialização (ex.: `gerar_arvores()`).
- Toda rotina gráfica que alterar flags globais de estado do OpenGL (iluminação, neblina, blending, depth mask) deve preservar o estado com `glPushAttrib`/`glPopAttrib`.
