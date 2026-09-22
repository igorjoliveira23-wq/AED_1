# E1 — Preparação do acervo

## Fonte dos dados

**MovieLens `ml-latest-small`** — GroupLens Research, Universidade de Minnesota.
Endereço: https://grouplens.org/datasets/movielens/latest/

Catálogo de filmes com título, ano e gêneros, mais avaliações de usuários em escala de 0,5 a 5 estrelas. Versão usada: 9.742 filmes, 100.836 avaliações de 610 usuários, gerada em 26/09/2018.

Arquivos originais utilizados (incluídos em `dados_originais/`): `movies.csv` (`movieId,title,genres`) e `ratings.csv` (`userId,movieId,rating,timestamp`).

**Licença**: uso livre para fins de pesquisa/estudo, sem fins comerciais, com exigência de citação:

> F. Maxwell Harper and Joseph A. Konstan. 2015. The MovieLens Datasets: History and Context. *ACM Transactions on Interactive Intelligent Systems (TiiS)* 5, 4: 19:1–19:19.

## Mapeamento de campos

| Campo do registro | Tipo | Origem | Transformação aplicada |
|---|---|---|---|
| `id` | int | `movieId` (movies.csv) | usado diretamente, já é identificador único |
| `nome` | texto (chave de busca) | `title` (movies.csv) | remove o "(AAAA)" do fim do título |
| `ano` | int | `title` (movies.csv) | extraído do "(AAAA)" no fim do título |
| `valor` | float | `rating` (ratings.csv) | média das notas do filme, agrupada por `movieId`, arredondada a 2 casas |
| `categoria` | texto | `genres` (movies.csv) | primeiro gênero da lista separada por `\|` |

`links.csv` e `tags.csv` não foram usados — não fazem parte do formato de 5 campos exigido.

## Critério de seleção dos 5.000 registros

Dos 9.742 filmes originais, 9.704 ficaram válidos após a limpeza (abaixo). Não foram usados os 5.000 primeiros: a base tende a vir ordenada por ordem de inclusão no catálogo, o que esconderia o comportamento que os algoritmos de ordenação devem revelar nas etapas seguintes.

Em vez disso foi usada **amostragem aleatória estratificada por categoria**, proporcional ao tamanho de cada gênero na base (método dos maiores restos, para o total fechar exatamente em 5.000), com semente fixa (`seed = 42`) para reprodutibilidade. Isso preserva a distribuição original entre gêneros (ex.: Comedy e Drama continuam sendo as categorias mais frequentes) em vez de favorecer ou eliminar categorias minoritárias. Ao final, a ordem das linhas é embaralhada (mesma semente) para que o arquivo não saia pré-ordenado por nenhum critério.

## Decisões de limpeza

| O que foi removido/tratado | Quantidade | Motivo |
|---|---|---|
| Filmes sem `(AAAA)` reconhecível no fim do título (ex.: *Babylon 5*, *Black Mirror*) | 13 | impossível extrair o campo `ano` de forma confiável |
| Filmes com `genres = (no genres listed)` | 34 | campo `categoria` é obrigatório no formato do registro |
| Filmes sem nenhuma avaliação em `ratings.csv` | — | impossível calcular o campo `valor` |
| `;` literal dentro do título (ex.: *Steins;Gate the Movie*) | 1 | conflita com o separador de campos do `acervo.txt` |
| `,` dentro de títulos (ex.: *"Shawshank Redemption, The"*) | 2.079 | o Anexo C proíbe vírgula **e** ponto e vírgula dentro dos campos, não só o separador escolhido |
| `:` dentro de títulos (ex.: *"Godfather: Part III, The"*) | — | não é exigido pelo Anexo C, mas removido por precaução para simplificar o parsing em C |
| Quebras de linha dentro de campos de texto | — | normalizadas para espaço, para não quebrar a leitura linha a linha em C |

`;`, `,` e `:` em `nome`/`categoria` são substituídos por espaço (e espaços duplicados são colapsados em um só). Por isso `Shawshank Redemption, The (1994)` vira `Shawshank Redemption The` e `Godfather: Part III, The` vira `Godfather Part III The` no `acervo.txt` — perde pontuação, mas mantém o texto legível e sem nenhum caractere que possa confundir o `sscanf` em C.

## Formato do arquivo final

`acervo.txt`: 5.000 linhas, sem cabeçalho, sem aspas, campos separados por `;`:

```
96283;Diary of a Wimpy Kid Dog Days;2012;3.0;Children
2571;Matrix The;1999;4.19;Action
318;Shawshank Redemption The;1994;4.43;Crime
2023;Godfather Part III The;1990;3.36;Crime
63;Don't Be a Menace to South Central While Drinking Your Juice in the Hood;1996;2.71;Comedy
```

Validado via `assert` em `preparar.py`: exatamente 5.000 linhas, todos os campos preenchidos, nenhum `;`, `,` ou `:` remanescente dentro de `nome`/`categoria`, `ano` em faixa plausível.

## Reprodutibilidade

```bash
python preparar.py
```

Requer **pandas** (`pip install pandas`) além da biblioteca padrão. Roda sobre os arquivos em `dados_originais/movies.csv` e `dados_originais/ratings.csv` e sempre gera o mesmo `acervo.txt` (semente fixa) — verificado rodando o script duas vezes e comparando a saída byte a byte.

## Estrutura da entrega

```
E1/
├── acervo.txt              # arquivo de dados final (5.000 registros)
├── preparar.py              # script de preparação (Python + pandas)
├── dados_originais/
│   ├── movies.csv
│   └── ratings.csv
└── README.md                 # este arquivo
```

## Declaração de uso de IA generativa

**Gerado com apoio da IA**: o script `preparar.py` (leitura dos arquivos originais, extração do ano a partir do título, cálculo da nota média por filme via `ratings.csv`, definição da categoria, tratamento dos caracteres proibidos nos campos de texto, amostragem estratificada por categoria e as validações finais) e a redação deste `README.md` foram produzidos pelo grupo e revisados com IA.

**Decidido e conduzido exclusivamente pelo grupo**: escolha do dataset (MovieLens `ml-latest-small`) e da fonte; definição de quais colunas do dataset mapeiam para os 5 campos do registro exigidos pelo Anexo C; definição do critério de recorte (amostragem estratificada por categoria, explicitamente não pelos N primeiros); conferência das regras de formatação do arquivo (separador `;`, sem cabeçalho, sem aspas, sem `;`/`,`/`:` dentro dos campos); e validação dos resultados gerados (5.000 registros, reprodutibilidade confirmada por execuções repetidas do script).

A IA foi usada como ferramenta de geração e depuração de código, sob orientação e validação do grupo, e não como autora independente das decisões e arquivos de projeto.
