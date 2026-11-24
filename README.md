<div align="center">

# Expedição ao Pico

**Cena 3D Low-Poly Procedural em OpenGL 2.1 para Computação Gráfica**

![OpenGL 2.1](https://img.shields.io/badge/OpenGL-2.1%20Fun%C3%A7%C3%A3o%20Fixa-0A66C2?style=for-the-badge&logo=opengl&logoColor=white)
![Modelagem Procedural](https://img.shields.io/badge/Cena-100%25%20Procedural-1D4ED8?style=for-the-badge)
![Zero Assets](https://img.shields.io/badge/Assets-Zero%20Arquivos%20Externos-0D9488?style=for-the-badge)

[![Python 3.10+](https://img.shields.io/badge/Python-3.10%2B-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://www.python.org/)
[![pygame-ce](https://img.shields.io/badge/pygame--ce-2.5%2B-22C55E?style=for-the-badge)](https://pyga.me/)
[![PyOpenGL](https://img.shields.io/badge/PyOpenGL-3.1%2B-1E3A8A?style=for-the-badge)](https://pyopengl.sourceforge.net/)

</div>

---

## Sumário

- [Visão Geral](#visão-geral)
- [Tecnologias Utilizadas](#tecnologias-utilizadas)
- [Estrutura do Repositório](#estrutura-do-repositório)
- [Como Executar](#como-executar)
- [Controles](#controles)
- [Solução de Problemas e Diagnóstico](#solução-de-problemas-e-diagnóstico)

---

## Visão Geral

**Expedição ao Pico** é uma animação 3D *low-poly* inspirada no jogo *PEAK*, desenvolvida em Python puro para a disciplina de **Computação Gráfica**. Toda a geometria, a textura procedural do solo, o personagem articulado, a iluminação e a interface 2D de atalhos são gerados em tempo de execução utilizando o pipeline fixo do **OpenGL 2.1** — sem modelos ou imagens externas, shaders, VBOs ou `numpy`.

- **Narrativa Automática:** Inicia à noite no acampamento (`ACAMPAMENTO`), realiza `7 s` de amanhecer e transição de câmera até o paredão (`TRANSICAO_CAMERA`), executa `32 s` de escalada com pausas em três platôs (`ESCALADA`) e finaliza em órbita contínua ao redor do cume nevado (`FINAL`).
- **Iluminação e Atmosfera:** Combina Sol direcional (`GL_LIGHT0`), fogueira pontual oscilante (`GL_LIGHT1`), holofote lunar noturno (`GL_LIGHT2`), neblina linear (`GL_FOG`) e partículas semitransparentes de fumaça.
- **Execução e Calibração:** Janela redimensionável (`1280×720`) limitada a `60 FPS`, com constantes de tempo, cores, câmeras e sombreamento (`GL_FLAT` / `GL_SMOOTH`) centralizadas em [`expedicao/configuracoes.py`](./expedicao/configuracoes.py).

---

## Tecnologias Utilizadas

| Categoria | Tecnologia | Papel no Projeto |
| :--- | :--- | :--- |
| **Linguagem** | Python `3.10+` | Lógica da simulação, matemática vetorial e geração procedural com biblioteca padrão (sem `numpy`). |
| **Janela e Eventos** | [`pygame-ce`](./requirements.txt) | Criação do contexto OpenGL, controle de eventos/FPS e geração inicial das superfícies de textura e HUD. |
| **Renderização 3D** | [`PyOpenGL`](./requirements.txt) | Bindings do pipeline fixo OpenGL 2.1 (matrizes, iluminação Phong, Display List, texturas e *blending*). |
| **Utilitários GL** | `OpenGL.GLU` | Projeção perspectiva (`gluPerspective`), quádricas esféricas (`gluSphere`) e mipmaps (`gluBuild2DMipmaps`). |

---

## Estrutura do Repositório

```text
opengl-peak/
├── main.py                     # Ponto de entrada: janela OpenGL 2.1, eventos e loop a 60 FPS
├── requirements.txt            # Dependências Python (pygame-ce e PyOpenGL)
├── README.md                   # Visão geral e instruções de execução
│
└── expedicao/
    ├── __init__.py             # Inicializador do pacote (sem imports automáticos)
    ├── ambiente.py             # Ajuste de compatibilidade Linux/Snap e modo --diagnostico
    ├── configuracoes.py        # Parâmetros ajustáveis da cena, câmeras, luzes e durações
    ├── matematica.py           # Interpolações, smoothstep, amortecimento e normais de face
    ├── simulacao.py            # Estado da cena, máquina de fases e trajetórias cinemáticas
    ├── primitivas.py           # Primitivas 3D (faces, cubos, blocos, esferas, cones e segmentos)
    ├── terreno.py              # Textura procedural com mipmaps e malha subdividida do solo
    ├── cenario.py              # Acampamento, árvores, montanha, platôs, cume e Display List
    ├── personagem.py           # Modelagem hierárquica articulada do escoteiro
    ├── iluminacao.py           # Configuração das luzes (Sol, fogueira e holofote lunar)
    ├── efeitos.py              # Chamas, fumaça transparente, lua e marcadores de luz
    ├── painel_controles.py     # Faixa inferior 2D de controles em projeção ortográfica
    └── renderizacao.py         # Estado global OpenGL, projeção, câmera e desenho da cena
```

---

## Como Executar

### Pré-requisitos

- **Python 3.10+** (em Debian/Ubuntu, instale também `python3-venv` caso necessário)
- **Sessão gráfica ativa** com suporte a **OpenGL 2.1** e **GLU**
  - No Debian/Ubuntu, se a biblioteca GLU não estiver instalada:
    ```bash
    sudo apt install libglu1-mesa
    ```

### Passo a Passo

1. **Crie e ative o ambiente virtual:**
   - **Linux / macOS:**
     ```bash
     python3 -m venv .venv
     source .venv/bin/activate
     ```
   - **Windows (PowerShell):**
     ```powershell
     python -m venv .venv
     .\.venv\Scripts\Activate.ps1
     ```

2. **Instale as dependências:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Inicie a aplicação:**
   - **Linux / macOS:**
     ```bash
     python3 main.py
     ```
   - **Windows:**
     ```powershell
     python main.py
     ```

---

## Controles

| Tecla | Ação |
| :---: | :--- |
| `Espaço` | Inicia a expedição no acampamento; nas demais fases ou no final, reinicia a sequência |
| `R` | Reinicia toda a cena, incluindo câmera e ciclo automático noite/dia |
| `N` | Alterna suavemente entre noite e dia (mantém a escolha até reiniciar) |
| `Esc` | Fecha a janela e encerra a aplicação |

---

## Solução de Problemas e Diagnóstico

- **Aviso sobre `numpy` no terminal:** A mensagem `Unable to import OpenGL.arrays.numpymodule.NumpyHandler: No numpy module present` é apenas informativa e esperada, pois o projeto não utiliza `numpy`.
- **Pasta do projeto movida:** Caso o diretório do projeto tenha sido movido após criar a `.venv`, recrie o ambiente virtual (`rm -rf .venv && python3 -m venv .venv`) e reinstale o `requirements.txt`.
- **Linux (VS Code Snap e Wayland/X11):** O módulo `expedicao/ambiente.py` corrige automaticamente conflitos de schemas GTK do VS Code Snap no processo atual e prioriza `SDL_VIDEODRIVER=x11` quando `DISPLAY` está ativo. Para forçar outro driver manualmente, defina `SDL_VIDEODRIVER` antes do comando.
- **Comandos de verificação e diagnóstico:**
  ```bash
  # Validar compilação e sintaxe dos módulos
  python3 -m compileall main.py expedicao

  # Rastrear inicialização de vídeo, variáveis de ambiente e versão OpenGL
  python3 -u main.py --diagnostico
  ```
