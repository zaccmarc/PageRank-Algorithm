# PageRank-Algorithm
Algoritimo de pagerank calculado a partir de um grafo dirigido usando power interation

# PAGERANK ALGORITHM

Date: May 27, 2025

## PageRank Algorithm using Power Interation

PageRank é uma métrica de **centralidade de autovetor** criada por Larry Page e Sergey Brin em 1997 para medir a relevância de páginas na Web. A intuição é simples: uma página é “importante” se recebe muitos links — e, sobretudo, se esses links vêm de outras páginas importantes. O algoritmo traduz essa ideia em uma cadeia de Markov: um “surfista aleatório” navega pelos links com probabilidade d (tipicamente 0,85) e, com probabilidade 1 - d “teleporta-se” para qualquer página. A distribuição estacionária dessa navegação é o vetor de PageRank.

## Algoritmo que utilizaremos

Para calcular o PageRank empregaremos o chamado método de iteração das potências. Ele parte de um princípio simples: começamos atribuindo a cada nó do grafo a mesma pontuação inicial, representando uma distribuição totalmente neutra. Em seguida repetimos um ciclo de redistribuição. Em cada ciclo, cada nó reparte a sua pontuação entre todos os nós para os quais ele possui ligação, respeitando a força (ou peso) de cada uma dessas ligações. Quando todos os nós terminam de repartir seus valores, somamos novamente as pontuações obtidas e ajustamos (normalizamos) para que a soma total continue igual a 1; desse modo mantemos a interpretação de que estamos lidando com uma distribuição de probabilidades.

Depois de cada rodada calculamos a diferença entre o vetor de pontuações recém-gerado e o vetor da rodada anterior. Se essa diferença global for menor do que o limite de tolerância estabelecido, entendemos que o processo atingiu estabilidade e podemos encerrar a iteração. Caso contrário, tomamos o novo vetor como ponto de partida e repetimos o ciclo de redistribuição. Esse procedimento converge porque, a cada repetição, pequenas oscilações locais se anulam e as pontuações vão se ajustando até chegar a um único conjunto de valores que não muda mais quando aplicamos o mesmo cálculo.

O vetor resultante, obtido quando a diferença entre duas rodadas sucessivas fica abaixo da tolerância ou quando atingimos o número máximo de iterações permitido, é justamente o PageRank do grafo. Ele reflete, de forma equilibrada, o impacto acumulado das ligações de saída de cada nó e fornece uma medida de importância relativa para toda a rede analisada.

## Codigo

Iniciamos o metodo definindo parametros que serão utilizados neste algoritimos, eis cada um individualmente: 

- **`G: nx.DiGraph`** – grafo dirigido cujos vértices terão o PageRank calculado; a estrutura e o número de arestas determinam o custo de cada iteração.
- **`alpha: float = 0.85`** – *damping factor*; probabilidade de o “surfista” seguir um link (quanto maior, mais peso para a malha de links; quanto menor, mais teleporte e convergência ligeiramente mais rápida).
- **`max_iter: int = 100`** – limite superior de iterações do método das potências; impede loops infinitos se a tolerância não for atingida.
- **`tol: float = 1e-6`** – tolerância de convergência; o algoritmo para quando a diferença entre dois vetores sucessivos de PageRank ficar abaixo desse valor (norma-1).
- **`personalization: dict | None`** – distribuição de teleporte não uniforme; permite dar preferência a determinados nós quando ocorre teleporte. Se `None`, assume distribuição uniforme entre todos os vértices.
- **`nstart: dict | None`** – vetor inicial para a iteração; um chute bem escolhido (ex.: grau de entrada normalizado) pode acelerar a convergência. Ausente → vetor uniforme.
- **`weight: str | None = "weight"`** – nome do atributo de aresta que contém o peso do link; `None` faz todas as arestas valerem 1. Pesos alteram a fração de probabilidade atribuída a cada destino.
- **`dangling: dict | None`** – distribuição usada para nós sem links de saída (*dangling nodes*); evita colunas vazias e mantém a matriz estocástica. Se omitido, herda a distribuição de `personalization` (ou uniforme).
- **Retorno** – dicionário `{nó: score}` com os valores de PageRank normalizados (soma total = 1).

```python
def pagerank(
        G: nx.DiGraph,
        alpha: float = 0.85,
        max_iter: int = 100,
        tol: float = 1e-6,
        personalization: dict | None = None,
        nstart: dict | None = None,
        weight: str | None = "weight",
        dangling: dict | None = None
) -> dict[int, float]:
```

A partir da qui faremos a construção, nesta parte focaremos em manipular o grafo recebi e aplicar os conceitos, cada parte está comentada com sua devida explicação

**Passo #1 – Garantir grafo dirigido**

- PageRank pressupõe direcionalidade (quem “cita” quem).
- Se `G` é não-dirigido, `to_directed()` cria arestas em ambas as direções; caso contrário, usa-se o próprio `G`.

**Passo #2 – Construir grafo estocástico**

- `nx.stochastic_graph(W, weight)` divide o peso de cada aresta pelo **grau de saída ponderado** do seu nó-origem, de modo que **a soma dos pesos que saem de qualquer nó vale 1**.
- Uma matriz (ou grafo) com essa propriedade é chamada **estocástica por coluna**: cada coluna é uma distribuição de probabilidade sobre os destinos possíveis. Isso significa que cada coluna da matriz (ou conjunto de arestas que saem de um nó) soma 1, representando probabilidades de saída válidas.
- Por que fazer isso? O método do “surfista aleatório” precisa de probabilidades válidas para que a multiplicação matriz × vetor mantenha o vetor PageRank como distribuição (soma = 1).

**Passo #3 – Vetor inicial `x`**

- **Se `nstart is None`:** inicia uniforme (`1/N` para cada nó) — hipótese neutra.
- **Caso contrário:** normaliza o vetor fornecido (`nstart`) para somar 1; boas chances de acelerar a convergência se refletir alguma informação prévia (ex.: grau de entrada).

```python
		#0. Verifica se o grafo nulo
    #Se G não contém nós, não há PageRank a calcular ⇒ devolve {} imediatamente.

    if G.number_of_nodes() == 0:
        return {}

    # 1.  Garante grafo dirigido
   
    W = G.to_directed() if not G.is_directed() else G

    # 2.  Constrói versão estocástica (probabilidades de saída)
    W = nx.stochastic_graph(W, weight=weight)

    N = W.number_of_nodes()
    nodes = list(W)                      # preservamos a ordem

    # 3.  Vetor inicial x
    if nstart is None:
        x = {n: 1.0 / N for n in nodes}
    else:
        total = float(sum(nstart.values()))
        x = {n: nstart.get(n, 0.0) / total for n in nodes}
```

**Passo #4 – Vetor de personalização `p`**

- **Se `personalization is None`:** teleporte é uniforme — qualquer página recebe a mesma probabilidade de salto.
- **Senão:** normaliza o dicionário dado; isso permite “puxar” o PageRank para um subconjunto (ex.: notarespecialidade de um domínio).

**Passo #5 – Tratamento de dangling nodes**

- *Dangling nodes* = vértices com **grau de saída zero** (nenhum link).
- `dangling_w` define para onde vai a probabilidade “presa” neles:
    - **Se `dangling is None`:** usa-se o mesmo vetor `p` (uniforme ou personalizado).
    - **Senão:** normaliza a distribuição informada pelo usuário.
- Lista `dangling_nodes` identifica esses vértices para o loop principal.

```python
# 4.  Personalização p
    if personalization is None:
        p = {n: 1.0 / N for n in nodes}
    else:
        total = float(sum(personalization.values()))
        p = {n: personalization.get(n, 0.0) / total for n in nodes}

    # 5.  Vetor para dangling nodes
    if dangling is None:
        dangling_w = p
    else:
        total = float(sum(dangling.values()))
        dangling_w = {n: dangling.get(n, 0.0) / total for n in nodes}

    dangling_nodes = [n for n in nodes
                      if W.out_degree(n, weight=weight) == 0]
```

**Passo #6 – Power Iteration**

1. **Salvar estado anterior:** `x_last = x`.
2. **Zerar acumulador:** `x = dict.fromkeys(nodes, 0.0)`.
3. **Probabilidade que “escorre” dos dangling**
    - `dangling_sum = alpha * sum(x_last[n] for n in dangling_nodes)`
    - Multiplica pelo damping porque essa parte ainda conta como “seguir link” (embora não exista link real).
4. **Distribuir pelas arestas**
    - Para cada aresta `u → v`, adiciona-se `alpha * x_last[u] * probabilidade(u→v)` ao novo score de `v`.
    - Resultado: todo o fluxo que sai de nós com links é propagado proporcionalmente aos pesos estocásticos.
5. **Teleporte + redistribuição dos dangling**
    - Para cada nó `n`:
        - **Teleporte global:** `(1 - alpha) * p[n]` (chance de o surfista pular para `n`).
        - **Redistribuição do dangling:** `dangling_sum * dangling_w[n]` (espalha o fluxo dos nós sem saída segundo `dangling_w`).
6. **Teste de convergência**
    - `err = Σ |x[n] − x_last[n]|` (norma-L1).
    - Se `err < tol * N`, considera-se convergido e interrompe o loop.
7. **Se exceder `max_iter` sem convergir:** lança `RuntimeError`.

### Fator dangling

O fator *dangling* trata dos nós que não têm ligações de saída. Quando o algoritmo chega a um desses vértices, não há para onde repassar a pontuação, o que faria a “probabilidade” ficar presa ali e a soma total deixar de ser 1. A solução é recolher toda a pontuação desses nós a cada iteração e redistribuí-la imediatamente segundo uma distribuição pré-definida—normalmente a mesma distribuição de teletransporte, que pode ser uniforme ou personalizada. Assim, mantemos a matriz de transição válida como uma distribuição de probabilidades, preservamos a soma global igual a 1 e garantimos que o processo continue convergindo para o vetor de PageRank final.

```python
  # 6.  Power-iteration
    for _ in range(max_iter):
        x_last = x
        x = dict.fromkeys(nodes, 0.0)

        # probabilidade que escorre dos dangling
        dangling_sum = alpha * sum(x_last[n] for n in dangling_nodes)

        # distribui pelas arestas
        for u in nodes:
            for v, edata in W[u].items():
                x[v] += alpha * x_last[u] * edata.get(weight, 1.0)

        # teletransporte + redistribuição dos dangling
        for n in nodes:
            x[n] += dangling_sum * dangling_w[n] + (1.0 - alpha) * p[n]

        # convergência (norma-L1)
        err = sum(abs(x[n] - x_last[n]) for n in nodes)
        if err < tol * N:
            break
    else:
        raise RuntimeError(f"PageRank não convergiu em {max_iter} iterações.")

```

**Passo #7 – Normalização final**

- `s = sum(x.values())` e divide-se cada valor por `s`.
- Garante que o vetor final seja **distribuição de probabilidade** (soma exata = 1), removendo pequenos desvios numéricos acumulados.

```python
    # 7.  Normaliza (por precaução) e devolve
    s = sum(x.values())
    return {n: val / s for n, val in x.items()}
```

## Resultado

Para visualizarmos o resultado, faremos a seguinte aplicação

```python
# --- monta o grafo a partir de L ---
L = np.array([
    [0,   1/3, 0,   1/4, 0, 0],
    [1/3, 0,   0,   0,   0, 0],
    [1/3, 0,   0,   1/4, 0, 0],
    [1/3, 1/3, 1,   0,   0, 1],
    [0,   0,   0,   1/4, 0, 0],
    [0,   1/3, 0,   1/4, 0, 0]
], dtype=float)

G = nx.from_numpy_array(L, create_using=nx.DiGraph)

# --- roda o PageRank escrito do zero ---
scores = pagerank(G, alpha=0.85)

for node, score in sorted(scores.items(), key=lambda t: -t[1]):
    print(f"{node}: {score:.4f}")
```

Ao rodar recebemos o seguinte resultado

```python
0: 0.3052
1: 0.2451
3: 0.2288
2: 0.0979
5: 0.0979
4: 0.0250
```

Em suma, o experimento confirma que a implementação do PageRank por iteração das potências está funcionando corretamente. O grafo foi convertido para uma representação estocástica, o vetor inicial e o teletransporte foram normalizados, e a rotina convergiu dentro do limite de tolerância, devolvendo um vetor cuja soma é 1.

O ranking obtido faz sentido à luz da malha de ligações: o nó 0 aparece como o mais influente (≈ 30 %), porque recebe fluxo direto de três outros vértices bem conectados; o nó 1 vem em seguida (≈ 24 %), sustentado por ligações de 0, 3 e 5; e o nó 3 (≈ 23 %) mantém alta relevância graças a múltiplas entradas — ainda que reparta muito do seu próprio peso para outros nós, o que reduz ligeiramente a sua pontuação. Já os nós 2 e 5 têm valor idêntico (≈ 9,8 %) porque partilham um padrão parecido de ligações, enquanto o nó 4, limitado a apontar apenas para 3 e quase sem referências de volta, permanece na cauda (≈ 2,5 %).

Esses resultados ilustram dois pontos-chave do algoritmo: (1) a importância de receber links de páginas que também são bem avaliadas e (2) o fato de que meramente emitir ligações não melhora o score; é a qualidade — não a quantidade — das recomendações recebidas que conta. O código, portanto, entrega um vetor de PageRank coerente com a topologia do grafo e comprova que o tratamento de normalização, damping e possíveis dangling nodes garante estabilidade e interpretabilidade probabilística do resultado final.
