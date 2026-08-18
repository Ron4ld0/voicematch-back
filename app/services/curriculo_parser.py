import io
import os
import httpx
import pdfplumber
import docx


def extrair_texto_curriculo(curriculo_url: str) -> str:
    """
    Extrai o texto de um currículo nos formatos .pdf ou .docx a partir de uma URL remota ou caminho local.
    Levanta ValueError, FileNotFoundError ou RuntimeError se a extração falhar.
    """
    if not curriculo_url or not isinstance(curriculo_url, str):
        raise ValueError("URL ou caminho do currículo inválido ou vazio.")

    url_clean = curriculo_url.strip()
    path_without_query = url_clean.split("?")[0]
    ext = os.path.splitext(path_without_query)[1].lower()

    if ext not in [".pdf", ".docx"]:
        raise ValueError(
            f"Formato de arquivo '{ext}' não suportado para extração. Apenas .pdf e .docx são aceitos."
        )

    # Obter os bytes do arquivo (remoto ou local)
    file_bytes: bytes
    if url_clean.startswith("http://") or url_clean.startswith("https://"):
        try:
            response = httpx.get(url_clean, timeout=15.0, follow_redirects=True)
            response.raise_for_status()
            file_bytes = response.content
        except Exception as e:
            raise RuntimeError(
                f"Falha ao baixar o currículo da URL remota ({url_clean}): {str(e)}"
            ) from e
    else:
        file_path = url_clean.replace("file://", "")

        # Tentar resolver o caminho local se for relativo (ex: /media/curriculos/nome.pdf)
        candidatos_path = [
            file_path,
            file_path.lstrip("/"),
            os.path.join(os.getcwd(), file_path.lstrip("/")),
        ]

        resolved_path = None
        for p in candidatos_path:
            if os.path.exists(p) and os.path.isfile(p):
                resolved_path = p
                break

        if not resolved_path:
            raise FileNotFoundError(
                f"Arquivo de currículo não encontrado no caminho local: '{file_path}'."
            )
        try:
            with open(resolved_path, "rb") as f:
                file_bytes = f.read()
        except Exception as e:
            raise RuntimeError(
                f"Erro ao ler o arquivo de currículo local ('{resolved_path}'): {str(e)}"
            ) from e

    if not file_bytes:
        raise ValueError("O arquivo de currículo obtido está vazio (0 bytes).")

    # Extrair o texto
    texto_extraido = ""
    try:
        if ext == ".pdf":
            with pdfplumber.open(io.BytesIO(file_bytes)) as pdf:
                paginas_texto = []
                for page in pdf.pages:
                    txt = page.extract_text()
                    if txt and txt.strip():
                        paginas_texto.append(txt.strip())
                texto_extraido = "\n".join(paginas_texto)
        elif ext == ".docx":
            doc = docx.Document(io.BytesIO(file_bytes))
            paragrafos = [
                p.text.strip() for p in doc.paragraphs if p.text and p.text.strip()
            ]
            texto_extraido = "\n".join(paragrafos)
    except Exception as e:
        raise RuntimeError(
            f"Erro ao processar o conteúdo do currículo ({ext}): {str(e)}"
        ) from e

    texto_final = texto_extraido.strip()
    if not texto_final:
        raise ValueError(
            "Não foi possível extrair nenhum texto válido do arquivo de currículo."
        )

    return texto_final
