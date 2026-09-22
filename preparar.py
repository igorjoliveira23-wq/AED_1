"""
Prepara acervo.txt (formato id;nome;ano;valor;categoria) a partir do
dataset MovieLens ml-latest-small (movies.csv + ratings.csv).
Uso: python preparar.py
"""
from pathlib import Path

import pandas as pd

BASE_DIR = Path(__file__).resolve().parent
MOVIES_CSV = BASE_DIR / "dados_originais" / "movies.csv"
RATINGS_CSV = BASE_DIR / "dados_originais" / "ratings.csv"
SAIDA = BASE_DIR / "acervo.txt"

TOTAL_REGISTROS = 5000
SEED = 42


def carregar_registros():
    movies = pd.read_csv(MOVIES_CSV)
    ratings = pd.read_csv(RATINGS_CSV)

    notas_medias = ratings.groupby("movieId")["rating"].mean().round(2)
    df = movies.merge(notas_medias.rename("valor"), on="movieId", how="inner")

    ano = df["title"].str.extract(r"\((\d{4})\)\s*$")[0]
    df["ano"] = pd.to_numeric(ano, errors="coerce")
    df = df.dropna(subset=["ano"])
    df["ano"] = df["ano"].astype(int)

    df["nome"] = df["title"].str.replace(r"\s*\(\d{4}\)\s*$", "", regex=True)
    df["categoria"] = df["genres"].str.split("|").str[0]
    df = df[df["categoria"] != "(no genres listed)"]

    for coluna in ("nome", "categoria"):
        df[coluna] = (
            df[coluna]
            .str.replace(r"[;,:]", " ", regex=True)
            .str.replace(r"[\r\n]+", " ", regex=True)
            .str.replace(r"\s+", " ", regex=True)
            .str.strip()
        )

    df = df.rename(columns={"movieId": "id"})
    return df[["id", "nome", "ano", "valor", "categoria"]]


def amostrar_estratificado(df, total, seed):
    """Amostragem aleatória proporcional por categoria (método dos maiores
    restos), para não recortar os N primeiros nem enviesar por gênero."""
    contagem = df["categoria"].value_counts()
    cotas_exatas = total * contagem / len(df)
    cotas = cotas_exatas.astype(int)

    faltam = total - cotas.sum()
    restos = (cotas_exatas - cotas).sort_values(ascending=False)
    cotas[restos.index[:faltam]] += 1

    partes = [
        grupo.sample(n=cotas[categoria], random_state=seed)
        for categoria, grupo in df.groupby("categoria")
    ]
    amostra = pd.concat(partes)
    return amostra.sample(frac=1, random_state=seed).reset_index(drop=True)


def validar(df):
    assert len(df) == TOTAL_REGISTROS, f"esperado {TOTAL_REGISTROS}, obtido {len(df)}"
    assert df.notna().all().all(), "há campos vazios"
    assert not df["nome"].str.contains("[;,:]", regex=True).any()
    assert not df["categoria"].str.contains("[;,:]", regex=True).any()
    assert df["ano"].between(1800, 2100).all()


def main():
    registros = carregar_registros()
    amostra = amostrar_estratificado(registros, TOTAL_REGISTROS, SEED)
    validar(amostra)

    amostra.to_csv(SAIDA, sep=";", header=False, index=False, lineterminator="\n")

    print(f"acervo.txt gerado com {len(amostra)} registros em {SAIDA}")


if __name__ == "__main__":
    main()
