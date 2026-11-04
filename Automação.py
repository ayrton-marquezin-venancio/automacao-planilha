"""Cadastro assistido de equipamentos; entradas CSV sempre somente para leitura."""

import csv
import argparse
import ctypes
import hashlib
import os
import re
from pathlib import Path
import time
from contextlib import contextmanager
from datetime import date, datetime, timezone
from zipfile import BadZipFile

import pandas as pd
import pyautogui
import pyperclip
from openpyxl import Workbook, load_workbook


COLUNAS = ("id_equipamento", "nome_equipamento", "categoria", "setor", "situacao")
SITUACOES = {"Disponível", "Em uso", "Em manutenção"}


def _extrair_numero_versao(nome: str) -> int | None:
    partes = re.fullmatch(
        r"Planilha Versão ([1-9][0-9]*) - ([0-9]{4}-[0-9]{2}-[0-9]{2})", nome
    )

    if partes is None:
        return None

    try:
        date.fromisoformat(partes.group(2))
    except ValueError:
        return None

    return int(partes.group(1))


@contextmanager
def _bloqueio_reserva_versao(saidas: Path):
    identidade = hashlib.sha256(
        str(saidas.resolve()).casefold().encode("utf-8")
    ).hexdigest()
    kernel = ctypes.WinDLL("kernel32", use_last_error=True)
    kernel.CreateMutexW.argtypes = (ctypes.c_void_p, ctypes.c_int, ctypes.c_wchar_p)
    kernel.CreateMutexW.restype = ctypes.c_void_p
    kernel.WaitForSingleObject.argtypes = (ctypes.c_void_p, ctypes.c_uint32)
    kernel.WaitForSingleObject.restype = ctypes.c_uint32
    kernel.ReleaseMutex.argtypes = (ctypes.c_void_p,)
    kernel.CloseHandle.argtypes = (ctypes.c_void_p,)

    handle = kernel.CreateMutexW(None, False, f"Local\\AtlasCadastroVersoes_{identidade}")
    if not handle:
        raise ctypes.WinError(ctypes.get_last_error())

    adquirido = False
    try:
        resultado = kernel.WaitForSingleObject(handle, 0xFFFFFFFF)
        if resultado not in (0, 0x80):
            raise ctypes.WinError(ctypes.get_last_error())
        adquirido = True
        yield
    finally:
        if adquirido:
            kernel.ReleaseMutex(handle)
        kernel.CloseHandle(handle)


def _reservar_pasta_versao(saidas: Path, data_execucao: date) -> Path:
    saidas = Path(saidas)
    saidas.mkdir(parents=True, exist_ok=True)

    with _bloqueio_reserva_versao(saidas):
        maior_numero = 0

        for existente in saidas.iterdir():
            if not existente.is_dir() or existente.is_symlink():
                continue

            numero = _extrair_numero_versao(existente.name)

            if numero is not None:
                maior_numero = max(maior_numero, numero)

        numero = maior_numero + 1

        while True:
            pasta_versao = saidas / f"Planilha Versão {numero} - {data_execucao.isoformat()}"

            try:
                pasta_versao.mkdir()
            except FileExistsError:
                numero += 1
                continue

            return pasta_versao


def hash_arquivo(caminho: Path) -> str:
    """SHA-256 dos bytes recebidos, sem interpretar ou alterar o arquivo."""

    digest = hashlib.sha256()

    with Path(caminho).open("rb") as arquivo:
        for bloco in iter(lambda: arquivo.read(1024 * 1024), b""):
            digest.update(bloco)

    return digest.hexdigest()


def validar_base(df: pd.DataFrame, *, origem: str) -> None:
    """Bloqueia entradas ambíguas antes de qualquer operação no Excel."""

    if len(df.columns) != len(COLUNAS) or set(df.columns) != set(COLUNAS):
        raise ValueError(f"Colunas obrigatórias ausentes ou extras em {origem}.")

    ids = df["id_equipamento"]

    if ids.eq("").any() or ids.ne(ids.str.strip()).any():
        raise ValueError(f"ID vazio ou com espaços laterais em {origem}.")

    if origem == "originais" and ids.duplicated().any():
        raise ValueError("ID duplicado no cadastro original.")

    for coluna in COLUNAS[1:]:
        if df[coluna].eq("").any():
            raise ValueError(f"Campo vazio em {origem}: {coluna}.")

    if not df["situacao"].isin(SITUACOES).all():
        raise ValueError(f"Situação desconhecida em {origem}.")


def carregar_csv(caminho: Path) -> pd.DataFrame:
    """Lê o CSV real com IDs textuais e confere o cabeçalho bruto."""

    caminho = Path(caminho)

    with caminho.open("r", encoding="utf-8-sig", newline="") as arquivo:
        cabecalho = next(csv.reader(arquivo, delimiter=";"), [])

    if len(cabecalho) != len(COLUNAS) or set(cabecalho) != set(COLUNAS):
        raise ValueError(f"Cabeçalho inválido ou duplicado: {caminho.name}.")

    dados = pd.read_csv(
        caminho, sep=";", encoding="utf-8-sig", dtype=str, keep_default_na=False
    )

    validar_base(
        dados,
        origem="originais"
        if caminho.name == "equipamentos_cadastrados.csv"
        else "solicitacoes",
    )

    return dados.loc[:, list(COLUNAS)]


def carregar_bases(pasta: Path) -> tuple[pd.DataFrame, pd.DataFrame, dict[str, str]]:
    pasta = Path(pasta)
    nomes = ("equipamentos_cadastrados.csv", "novos_equipamentos.csv")
    caminhos = [pasta / nome for nome in nomes]

    for caminho in caminhos:
        if not caminho.is_file():
            raise FileNotFoundError(f"Entrada não encontrada: {caminho}")

    hashes = {caminho.name: hash_arquivo(caminho) for caminho in caminhos}

    return carregar_csv(caminhos[0]), carregar_csv(caminhos[1]), hashes


def classificar_solicitacoes(
    originais: pd.DataFrame, solicitacoes: pd.DataFrame
) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Classifica cada linha sem depender de rótulos recebidos."""

    validar_base(originais, origem="originais")
    validar_base(solicitacoes, origem="solicitacoes")

    existentes = set(originais["id_equipamento"])
    aceitos: set[str] = set()
    estados, motivos = [], []

    # Classifica cada solicitação na ordem recebida.
    for identificador in solicitacoes["id_equipamento"]:
        if identificador in existentes:
            estados.append("Equipamento Duplicado")
            motivos.append("Já cadastrado na base original")

        elif identificador in aceitos:
            estados.append("Equipamento Duplicado")
            motivos.append("Repetido na base de novos equipamentos")

        else:
            aceitos.add(identificador)
            estados.append("Novo Equipamento")
            motivos.append("")

    classificadas = solicitacoes.loc[:, list(COLUNAS)].copy().reset_index(drop=True)
    classificadas["status_cadastro"] = estados
    classificadas["motivo_duplicidade"] = motivos
    classificadas["linha_origem"] = range(2, len(classificadas) + 2)

    novos = classificadas.loc[
        classificadas["status_cadastro"].eq("Novo Equipamento"), list(COLUNAS)
    ].reset_index(drop=True)

    resumo = resumir_classificacao(classificadas)

    if sum(resumo.values()) != len(solicitacoes):
        raise RuntimeError("Classificação não conciliou todas as solicitações.")

    return classificadas, novos


def resumir_classificacao(classificadas: pd.DataFrame) -> dict[str, int]:
    motivos = classificadas["motivo_duplicidade"]

    return {
        "ja_cadastrados": int(motivos.eq("Já cadastrado na base original").sum()),
        "repetidos_na_lista": int(
            motivos.eq("Repetido na base de novos equipamentos").sum()
        ),
        "novos_validos": int(
            classificadas["status_cadastro"].eq("Novo Equipamento").sum()
        ),
    }


def preparar_copia(
    originais: pd.DataFrame, destino: Path, *, capacidade: int = 0
) -> Path:
    """Cria um XLSX novo com os originais, sem sobrescrever saídas anteriores."""

    validar_base(originais, origem="originais")

    destino = Path(destino)
    destino.parent.mkdir(parents=True, exist_ok=True)

    workbook = Workbook()
    planilha = workbook.active
    planilha.title = "Equipamentos"
    planilha.append(COLUNAS)

    for linha in originais.loc[:, list(COLUNAS)].itertuples(index=False, name=None):
        planilha.append(linha)
        planilha.cell(planilha.max_row, 1).number_format = "@" 

    for numero in range(len(originais) + 2, len(originais) + capacidade + 2):
        for coluna in range(1, len(COLUNAS) + 1):
            planilha.cell(numero, coluna).number_format = "@"

    # Salva em modo exclusivo para não sobrescrever outra saída.
    with destino.open("xb") as arquivo:
        workbook.save(arquivo)

    workbook.close()

    return destino


def _linhas_reais(planilha) -> list[tuple]:
    linhas = list(planilha.values)

    # Remove apenas as linhas vazias finais da área formatada.
    while len(linhas) > 1 and all(valor is None for valor in linhas[-1]):
        linhas.pop()

    return linhas


def verificar_xlsx(
    destino: Path, originais: pd.DataFrame, novos_validos: pd.DataFrame
) -> dict[str, int]:
    """Compara a planilha salva com todas as linhas que deveriam existir."""

    destino = Path(destino)

    # Reabre a planilha para conferir os dados efetivamente salvos.
    workbook = load_workbook(destino, read_only=True, data_only=False)

    try:
        linhas = _linhas_reais(workbook.active)
    finally:
        workbook.close()

    if not linhas or tuple(linhas[0]) != COLUNAS:
        raise ValueError("Cabeçalho do XLSX divergente.")

    obtidas = linhas[1:]
    esperadas = [
        tuple(linha)
        for tabela in (originais, novos_validos)
        for linha in tabela.loc[:, list(COLUNAS)].itertuples(index=False, name=None)
    ]
    ids = [linha[0] for linha in obtidas]

    if any(not isinstance(valor, str) for valor in ids):
        raise ValueError("ID não textual no XLSX.")

    if len(ids) != len(set(ids)):
        raise ValueError("ID duplicado no XLSX.")

    if obtidas != esperadas:
        raise ValueError("Linhas ou atributos do XLSX divergem do resultado esperado.")

    return {
        "originais": len(originais),
        "novos": len(novos_validos),
        "total": len(obtidas),
    }


def _publicar_final_ordenado(
    destino: Path,
    originais: pd.DataFrame,
    novos_validos: pd.DataFrame,
    final: Path,
    *,
    permitir_existente: bool = False,
) -> dict[str, int]:
    """Publica ou confere o XLSX final sem alterar a ordem da cópia de trabalho."""

    resultado = verificar_xlsx(destino, originais, novos_validos)
    tabela = pd.concat(
        [originais.loc[:, list(COLUNAS)], novos_validos.loc[:, list(COLUNAS)]],
        ignore_index=True,
    )

    if not tabela["id_equipamento"].str.fullmatch(r"EQP[0-9]{4}").all():
        raise ValueError("ID fora do padrão EQP0000; publicação não realizada.")

    ordenada = tabela.sort_values("id_equipamento", kind="stable").reset_index(
        drop=True
    )
    final = Path(final)

    if final.exists():
        if not permitir_existente:
            raise FileExistsError(f"Saída final já existe: {final}")

        try:
            verificar_xlsx(final, ordenada, ordenada.iloc[0:0])
        except (ValueError, BadZipFile) as erro:
            raise ValueError(f"Saída final existente incompatível: {final}") from erro
    else:
        preparar_copia(ordenada, final)
        verificar_xlsx(final, ordenada, ordenada.iloc[0:0])

    return resultado


def _colar_tsv(texto: str) -> None:
    """Usa a área de transferência para preservar acentos na digitação visual."""

    pyperclip.copy(texto)
    pyautogui.hotkey("ctrl", "v")
    time.sleep(0.4)


def _ativar_excel(destino: Path, *, abrir: bool = False) -> None:
    """Devolve foco ao arquivo desta execução após a confirmação no terminal."""

    existentes = [
        j
        for j in pyautogui.getWindowsWithTitle(destino.name)
        if destino.name.casefold() in j.title.casefold()
    ]

    # Abre a cópia apenas quando ainda não há uma janela correspondente.

    if abrir and not existentes:
        os.startfile(destino)

    limite = time.monotonic() + 15

    while time.monotonic() < limite:
        janelas = [
            j
            for j in pyautogui.getWindowsWithTitle(destino.name)
            if destino.name.casefold() in j.title.casefold()
            and "excel" in j.title.casefold()
        ]

        if len(janelas) == 1:
            janelas[0].activate()
            time.sleep(0.8)

            ativa = pyautogui.getActiveWindow()

            if ativa and destino.name.casefold() in ativa.title.casefold():
                return
        elif len(janelas) > 1:
            raise RuntimeError("Há mais de uma janela Excel para esta execução.")

        time.sleep(0.3)

    raise RuntimeError("Não foi possível ativar a planilha correta no Excel.")


def _aguardar_salvamento(destino: Path, minimo_linhas: int) -> None:
    limite = time.monotonic() + 15

    while time.monotonic() < limite:
        try:
            workbook = load_workbook(destino, read_only=True, data_only=False)

            try:
                linhas = _linhas_reais(workbook.active)
            finally:
                workbook.close()

            if len(linhas) - 1 >= minimo_linhas:
                return
        except (OSError, ValueError):
            pass

        time.sleep(0.3)

    raise RuntimeError("O Excel não confirmou o salvamento das linhas esperadas.")


def _salvar_como_excel(destino: Path) -> None:
    """Recupera uma gravação não confirmada, sempre no XLSX de trabalho."""

    pyautogui.press("f12")

    limite = time.monotonic() + 10

    while time.monotonic() < limite:
        titulo = getattr(pyautogui.getActiveWindow(), "title", "").casefold()

        if "salvar como" in titulo or "save as" in titulo:
            break

        time.sleep(0.2)
    else:
        raise RuntimeError("O diálogo Salvar como não abriu no Excel.")

    pyperclip.copy(str(destino.resolve()))
    pyautogui.hotkey("ctrl", "a")
    pyautogui.hotkey("ctrl", "v")
    pyautogui.press("enter")

    limite = time.monotonic() + 10

    while time.monotonic() < limite:
        titulo = getattr(pyautogui.getActiveWindow(), "title", "").casefold()

        if "confirmar salvar como" in titulo or "confirm save as" in titulo:
            pyautogui.press("left")
            pyautogui.press("enter")
            break

        if destino.name.casefold() in titulo and "excel" in titulo:
            return

        time.sleep(0.8)
    else:
        raise RuntimeError("O Excel não confirmou o destino do salvamento.")

    limite = time.monotonic() + 10

    while time.monotonic() < limite:
        titulo = getattr(pyautogui.getActiveWindow(), "title", "").casefold()

        if destino.name.casefold() in titulo and "excel" in titulo:
            return

        time.sleep(0.8)

    raise RuntimeError("O Excel não retornou ao XLSX de trabalho após salvar.")


def inserir_no_excel(
    novos_validos: pd.DataFrame, destino: Path, *, limite: int | None = None
) -> int:
    """Envia somente novas linhas ao Excel ativo e salva o arquivo aberto."""

    if not pyautogui.FAILSAFE:
        raise RuntimeError("PyAutoGUI FAILSAFE deve permanecer ativo.")

    destino = Path(destino)
    janela = pyautogui.getActiveWindow()
    titulo = getattr(janela, "title", "")

    if (
        destino.name.casefold() not in titulo.casefold()
        or "excel" not in titulo.casefold()
    ):
        raise RuntimeError("A janela ativa não é o arquivo correto no Excel.")

    if limite is not None and limite < 0:
        raise ValueError("Limite do lote deve ser não negativo.")

    workbook = load_workbook(destino, read_only=True, data_only=False)

    try:
        linhas = _linhas_reais(workbook.active)
    finally:
        workbook.close()

    if not linhas or tuple(linhas[0]) != COLUNAS:
        raise ValueError("Cabeçalho inesperado na planilha de trabalho.")

    if any(
        any(valor is None or valor == "" for valor in linha) for linha in linhas[1:]
    ):
        raise ValueError("Há lacuna na planilha; linha inicial incerta.")

    if list(novos_validos.columns) != list(COLUNAS):
        raise ValueError("A seleção deve conter somente os cinco campos comerciais.")

    selecionados = novos_validos.head(limite) if limite is not None else novos_validos
    ids_existentes = {linha[0] for linha in linhas[1:]}
    ids_novos = selecionados["id_equipamento"].tolist()

    if len(ids_novos) != len(set(ids_novos)) or ids_existentes.intersection(ids_novos):
        raise ValueError("A seleção contém ID duplicado ou já presente no XLSX.")

    valores = selecionados.loc[:, list(COLUNAS)].itertuples(index=False, name=None)

    for linha in valores:
        if any(not isinstance(v, str) or any(c in v for c in "\t\r\n") for v in linha):
            raise ValueError("Campo inválido para colagem tabular no Excel.")

    if selecionados.empty:
        return 0

    # Prepara o bloco tabulado para o lote selecionado.
    primeira_linha = len(linhas) + 1
    bloco = "\n".join(
        "\t".join(linha)
        for linha in selecionados.loc[:, list(COLUNAS)].itertuples(
            index=False, name=None
        )
    )

    pyautogui.hotkey("ctrl", "g")
    pyautogui.write(f"A{primeira_linha}")
    pyautogui.press("enter")

    limite_foco = time.monotonic() + 3

    while time.monotonic() < limite_foco:
        titulo_atual = getattr(pyautogui.getActiveWindow(), "title", "")

        if destino.name.casefold() in titulo_atual.casefold():
            break

        time.sleep(0.8)
    else:
        raise RuntimeError(
            f"O Excel não recuperou o foco após navegar: {titulo_atual!r}."
        )

    _colar_tsv(bloco)
    time.sleep(0.8)

    titulo_atual = getattr(pyautogui.getActiveWindow(), "title", "")

    if destino.name.casefold() not in titulo_atual.casefold():
        raise RuntimeError(f"A janela do Excel mudou após a colagem: {titulo_atual!r}.")

    pyautogui.press("esc")
    pyautogui.hotkey("ctrl", "s")
    time.sleep(1)

    minimo_linhas = len(linhas) - 1 + len(selecionados)

    try:
        _aguardar_salvamento(destino, minimo_linhas)
    except RuntimeError:
        _salvar_como_excel(destino)
        _aguardar_salvamento(destino, minimo_linhas)

    return len(selecionados)


def ids_pendentes_em_saida_parcial(
    destino: Path, novos_validos: pd.DataFrame, originais: pd.DataFrame
) -> list[str]:
    """Aceita retomada apenas quando os novos já gravados formam um prefixo."""

    workbook = load_workbook(destino, read_only=True, data_only=False)

    try:
        linhas = _linhas_reais(workbook.active)
    finally:
        workbook.close()

    if not linhas or tuple(linhas[0]) != COLUNAS:
        raise ValueError("Saída parcial com cabeçalho inesperado.")

    # Confirma os registros existentes antes de calcular o que falta.
    quantidade_novos = len(linhas) - 1 - len(originais)

    if quantidade_novos < 0 or quantidade_novos > len(novos_validos):
        raise ValueError("Quantidade de linhas inválida na saída parcial.")

    verificar_xlsx(destino, originais, novos_validos.head(quantidade_novos))

    return novos_validos["id_equipamento"].iloc[quantidade_novos:].tolist()


def conferir_hashes(pasta: Path, hashes: dict[str, str]) -> None:
    for nome, esperado in hashes.items():
        caminho = Path(pasta) / nome

        if not caminho.is_file() or hash_arquivo(caminho) != esperado:
            raise RuntimeError(f"Entrada original ausente ou alterada: {nome}.")


def confirmar_abertura_excel() -> bool:
    """Solicita autorização explícita antes de preparar a saída e abrir o Excel."""

    pergunta = (
        "\nConfirma a seleção e autoriza abrir o Excel? "
        "Digite SIM para continuar ou NÃO para encerrar: "
    )

    while True:
        resposta = input(pergunta).strip().casefold()

        if resposta == "sim":
            return True

        if resposta in {"não", "nao"}:
            return False

        print(
            "Resposta inválida. A seleção permanece pendente. "
            "Digite SIM para continuar ou NÃO para encerrar a automação."
        )

        pergunta = ""


def confirmar_operacao(pergunta: str) -> bool:
    """Aguarda a decisão explícita para o piloto ou a continuação."""

    while True:
        resposta = input(pergunta).strip().casefold()

        if resposta == "sim":
            return True

        if resposta in {"não", "nao"}:
            return False

        print(
            "Resposta inválida. A confirmação permanece pendente. "
            "Digite SIM para continuar ou NÃO para encerrar a automação."
        )

        pergunta = ""


def _restaurar_foco_terminal(janela) -> None:
    """Reativa a janela capturada do VS Code, sem digitar no painel interno."""

    identificador = getattr(janela, "_hWnd", None)
    titulo = getattr(janela, "title", "")

    if (
        type(identificador) is not int
        or identificador <= 0
        or "visual studio code" not in titulo.casefold()
    ):
        raise RuntimeError("Não foi possível identificar a janela do terminal no VS Code.")

    try:
        janela.activate()
    except Exception as erro:
        raise RuntimeError("Não foi possível restaurar a janela do terminal.") from erro

    limite = time.monotonic() + 3

    while time.monotonic() < limite:
        ativa = pyautogui.getActiveWindow()

        if (
            getattr(ativa, "_hWnd", None) == identificador
            and "visual studio code" in getattr(ativa, "title", "").casefold()
        ):
            return

        time.sleep(0.5)

    raise RuntimeError("A janela do terminal não recuperou o foco.")


def main(pasta: Path | None = None, *, parcial: Path | None = None) -> int:
    """Executa fases assistidas; sucesso só após conferir o arquivo salvo."""

    pasta = Path(pasta) if pasta is not None else Path(__file__).resolve().parent

    try:
        originais, solicitacoes, hashes = carregar_bases(pasta)
        classificadas, novos = classificar_solicitacoes(originais, solicitacoes)
        resumo = resumir_classificacao(classificadas)

        print("\n" + "=" * 72)
        print("CADASTRO DE EQUIPAMENTOS")
        print("=" * 72)
        print("\n[ETAPA 1/4] ENTRADAS E CLASSIFICAÇÃO")
        print(f"  Equipamentos cadastrados : {len(originais)}")
        print(f"  Solicitações recebidas    : {len(solicitacoes)}")
        print("\n  Resultado da classificação")
        print(f"    Já cadastrados : {resumo['ja_cadastrados']}")
        print(f"    Repetidos      : {resumo['repetidos_na_lista']}")
        print(f"    Novos válidos  : {resumo['novos_validos']}")
        print("\n  Amostra das solicitações classificadas (até 10):")
        print("-" * 72)
        print(
            classificadas[["id_equipamento", "status_cadastro", "motivo_duplicidade"]]
            .head(10)
            .to_string(index=False)
        )
        print("-" * 72)

        if not confirmar_abertura_excel():
            print("\n[ENCERRADO] Automação encerrada pelo usuário.")
            return 0

        janela_terminal = pyautogui.getActiveWindow()

        if parcial is None:
            identificador = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S%fZ")
            pasta_execucao = _reservar_pasta_versao(
                (pasta / "saidas").resolve(), datetime.now().astimezone().date()
            )
            destino = (
                pasta_execucao
                / f"equipamentos_atualizados_{identificador}.xlsx"
            )

            preparar_copia(originais, destino, capacidade=len(novos))

            feitos = 0

            verificar_xlsx(destino, originais, novos.iloc[0:0])
        else:
            destino = Path(parcial).resolve()
            raiz = (pasta / "saidas").resolve()

            if (
                destino.parent.parent != raiz
                or _extrair_numero_versao(destino.parent.name) is None
            ):
                raise ValueError("Parcial fora de uma execução identificada.")

            if not destino.name.startswith("equipamentos_atualizados_"):
                raise ValueError("Nome da saída parcial inesperado.")

            pendentes = ids_pendentes_em_saida_parcial(destino, novos, originais)
            feitos = len(novos) - len(pendentes)

        print("\n[ETAPA 2/4] PREPARAÇÃO DA CÓPIA")
        print(f"  Pasta da versão: {destino.parent}")
        print("  Cópia de trabalho:")
        print(f"    {destino}")

        # Finaliza imediatamente se a saída retomada já estiver completa.
        if feitos == len(novos):
            verificar_xlsx(destino, originais, novos)
            conferir_hashes(pasta, hashes)

            final = destino.parent / "equipamentos_atualizados.xlsx"
            _publicar_final_ordenado(
                destino, originais, novos, final, permitir_existente=True
            )

            print("\n[CONCLUÍDO] Cópia completa e verificada.")
            print("  Arquivo final:")
            print(f"    {final}")

            return 0

        # Executa o lote piloto e pede autorização separada para continuar.
        if feitos < min(3, len(novos)):
            piloto = min(3 - feitos, len(novos) - feitos)

            print("\n[ETAPA 3/4] LOTE PILOTO")
            print(
                f"  Confira no Excel a planilha e a próxima linha ({piloto} itens)."
            )

            if not confirmar_operacao(
                "\nAutoriza o lote piloto na tela? "
                "Digite SIM para continuar ou NÃO para encerrar: "
            ):
                print("\n[ENCERRADO] Automação encerrada pelo usuário.")
                print("  Cópia parcial preservada em:")
                print(f"    {destino}")
                return 0

            _ativar_excel(destino, abrir=True)
            inserir_no_excel(
                novos.iloc[feitos : feitos + piloto].reset_index(drop=True), destino
            )
            feitos += piloto
            verificar_xlsx(destino, originais, novos.head(feitos))

        if feitos < len(novos):
            print("\n[CONFERÊNCIA DA CÓPIA]")
            print(f"  Equipamentos já registrados : {feitos}")
            print(f"  Equipamentos pendentes      : {len(novos) - feitos}")

            _restaurar_foco_terminal(janela_terminal)
            print("\n[ETAPA 4/4] AUTORIZAÇÃO PARA CONTINUAR")
            print(
                "Selecione o terminal integrado do VS Code que executa este script "
                "antes de responder."
            )

            if not confirmar_operacao(
                "\nAutoriza continuar o preenchimento? "
                "Digite SIM para continuar ou NÃO para encerrar: "
            ):
                print("\n[ENCERRADO] Automação encerrada pelo usuário.")
                print("  Cópia parcial preservada em:")
                print(f"    {destino}")
                return 0

            pendentes = ids_pendentes_em_saida_parcial(destino, novos, originais)

            if pendentes != novos.iloc[feitos:]["id_equipamento"].tolist():
                raise ValueError("Lote parcial diverge da sequência esperada.")

            _ativar_excel(destino)
            inserir_no_excel(novos.iloc[feitos:].reset_index(drop=True), destino)

        verificar_xlsx(destino, originais, novos)

        conferir_hashes(pasta, hashes)

        final = destino.parent / "equipamentos_atualizados.xlsx"
        resultado = _publicar_final_ordenado(destino, originais, novos, final)

        print("\n" + "=" * 72)
        print("[CONCLUÍDO] Cadastro conferido e salvo.")
        print(f"  Equipamentos originais : {resultado['originais']}")
        print(f"  Novos equipamentos     : {resultado['novos']}")
        print(f"  Total conferido        : {resultado['total']}")
        print("\n  Arquivo final:")
        print(f"    {final}")
        print("=" * 72)

        return 0

    except Exception as erro:
        print("\n" + "!" * 72)
        print("[ERRO] Execução interrompida.")
        print(f"  Tipo    : {type(erro).__name__}")
        print(f"  Detalhe : {erro}")
        print("  Ação    : confira o XLSX parcial antes de qualquer retomada.")
        print("!" * 72)

        return 1


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Cadastro assistido de equipamentos")
    parser.add_argument(
        "--retomar", type=Path, help="XLSX parcial de uma execução anterior"
    )
    args = parser.parse_args()
    raise SystemExit(main(parcial=args.retomar))
