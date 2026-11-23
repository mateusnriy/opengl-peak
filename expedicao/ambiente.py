"""Preparação do ambiente Linux/SDL e diagnóstico de inicialização.

Este módulo deve ser carregado e executado ANTES da importação de `pygame` ou
`PyOpenGL` para evitar abortos nativos do GLib causados por esquemas Snap herdados
do terminal integrado e para configurar o driver de vídeo compatível.

Tags da apresentação: [AMBIENTE], [JANELA].
"""

import os
import sys

from expedicao.configuracoes import CORRIGIR_ESQUEMAS_SNAP_NO_LINUX, PREFERIR_X11_NO_LINUX

# Ativado via argumento de linha de comando para rastrear etapas antes de carregar C/SDL.
MODO_DIAGNOSTICO = "--diagnostico" in sys.argv


def registrar_diagnostico(mensagem: str) -> None:
    """Imprime uma mensagem de diagnóstico com descarga imediata do buffer.

    O `flush=True` garante que o log apareça no terminal mesmo antes de uma eventual
    falha nativa em C/GLib onde não há traceback Python.

    Parâmetros:
        mensagem: Texto descritivo da etapa atual de inicialização.
    """
    if MODO_DIAGNOSTICO:
        print(f"[diagnóstico] {mensagem}", flush=True)


def _caminho_pertence_ao_snap(caminho: str) -> bool:
    """Verifica se um caminho do sistema contém o diretório de pacote Snap.

    Parâmetros:
        caminho: Caminho de diretório ou executável a ser inspecionado.

    Retorno:
        Verdadeiro se `snap` for um segmento do caminho normalizado; falso caso contrário.
    """
    return "snap" in os.path.normpath(caminho).split(os.sep)


def configurar_esquemas_linux() -> None:
    """Substitui esquemas GLib do Snap pelos do sistema apenas no processo atual.

    O terminal integrado do VS Code instalado via Snap exporta esquemas próprios em
    `GSETTINGS_SCHEMA_DIR` e `XDG_DATA_DIRS`. Misturar GTK nativo com esses esquemas
    pode abortar em `g_settings_get_enum` antes da criação da janela OpenGL.
    """
    if not sys.platform.startswith("linux") or not CORRIGIR_ESQUEMAS_SNAP_NO_LINUX:
        return

    # Um interpretador Python empacotado dentro do próprio Snap deve preservar seu ambiente.
    if _caminho_pertence_ao_snap(os.path.realpath(sys.executable)):
        return

    esquema_herdado = os.environ.get("GSETTINGS_SCHEMA_DIR", "")
    diretorios_herdados = os.environ.get("XDG_DATA_DIRS", "")
    possui_snap = _caminho_pertence_ao_snap(esquema_herdado) or any(
        _caminho_pertence_ao_snap(diretorio)
        for diretorio in diretorios_herdados.split(os.pathsep)
        if diretorio
    )
    if not possui_snap:
        return

    esquemas_sistema = "/usr/share/glib-2.0/schemas"
    if not os.path.isfile(os.path.join(esquemas_sistema, "gschemas.compiled")):
        return

    if _caminho_pertence_ao_snap(esquema_herdado):
        os.environ["GSETTINGS_SCHEMA_DIR"] = esquemas_sistema
        registrar_diagnostico(f"Esquemas do Snap substituídos por {esquemas_sistema}")

    if diretorios_herdados:
        diretorios_nativos = [
            diretorio
            for diretorio in diretorios_herdados.split(os.pathsep)
            if diretorio and not _caminho_pertence_ao_snap(diretorio)
        ]
        os.environ["XDG_DATA_DIRS"] = (
            os.pathsep.join(diretorios_nativos) or "/usr/local/share:/usr/share"
        )
        registrar_diagnostico(f"XDG_DATA_DIRS efetivo={os.environ['XDG_DATA_DIRS']!r}")


def configurar_driver_video() -> None:
    """Seleciona o driver X11 no Linux quando há `DISPLAY` e nenhum driver foi forçado.

    Atua como alternativa de compatibilidade via XWayland contra instabilidades do
    `libdecor` no Wayland, respeitando `SDL_VIDEODRIVER` definido externamente.
    """
    if sys.platform.startswith("linux") and PREFERIR_X11_NO_LINUX and os.environ.get("DISPLAY"):
        os.environ.setdefault("SDL_VIDEODRIVER", "x11")


def preparar_ambiente_execucao(caminho_arquivo_principal: str) -> None:
    """Executa diagnóstico inicial e saneia o ambiente antes de importar bibliotecas gráficas.

    Parâmetros:
        caminho_arquivo_principal: Caminho do script de entrada (`__file__` do `main.py`).
    """
    registrar_diagnostico(f"Arquivo: {os.path.realpath(caminho_arquivo_principal)}")
    registrar_diagnostico(f"Python: {sys.executable} ({sys.version.split()[0]})")
    if MODO_DIAGNOSTICO:
        for variavel in (
            "SDL_VIDEODRIVER",
            "GDK_BACKEND",
            "GTK_MODULES",
            "GSETTINGS_SCHEMA_DIR",
            "XDG_DATA_DIRS",
            "LD_LIBRARY_PATH",
        ):
            registrar_diagnostico(f"{variavel}={os.environ.get(variavel)!r}")

    configurar_esquemas_linux()
    configurar_driver_video()
    registrar_diagnostico(
        f"Ambiente pronto (SDL_VIDEODRIVER={os.environ.get('SDL_VIDEODRIVER')!r})."
    )
