import numpy as np
import networkx as nx

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
    """
    Calcula o PageRank de um grafo dirigido usando power-iteration.

    Parâmetros
    ----------
    G : nx.DiGraph       Grafo de entrada (precisa ser dirigido).
    alpha : float        Fator de amortecimento (0 < alpha < 1).
    max_iter : int       Número máximo de iterações.
    tol : float          Critério de convergência (erro L1).
    personalization :    Vetor de teletransporte. Se None → uniforme.
    nstart :             Vetor inicial. Se None → uniforme.
    weight : str|None    Nome do atributo-peso ou None (peso=1).
    dangling :           Distribuição para nós sem saída. Se None → usa
                         o vetor de personalização.
    Retorno
    -------
    dict {nó: score}     Valores normalizados (somam 1).
    """
    #0. Verifica se o grafo nulo
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

    # 7.  Normaliza (por precaução) e devolve
    s = sum(x.values())
    return {n: val / s for n, val in x.items()}


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
