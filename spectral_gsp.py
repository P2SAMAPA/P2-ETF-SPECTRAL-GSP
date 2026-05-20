import numpy as np
import networkx as nx
from scipy.linalg import eigh

def build_correlation_graph(returns_df, threshold=0.3):
    """
    Build a weighted graph where nodes are ETFs, edge weight = absolute correlation.
    Keep only edges with weight > threshold.
    Returns adjacency matrix (numpy) and node list.
    """
    corr = returns_df.corr().abs()
    n = corr.shape[0]
    # Build adjacency
    adj = np.zeros((n, n))
    for i in range(n):
        for j in range(n):
            if i != j and corr.iloc[i, j] > threshold:
                adj[i, j] = corr.iloc[i, j]
    # Make symmetric
    adj = (adj + adj.T) / 2
    return adj, returns_df.columns.tolist()

def graph_laplacian(adj):
    """Compute unnormalized Laplacian L = D - A."""
    deg = np.sum(adj, axis=1)
    D = np.diag(deg)
    return D - adj

def graph_fourier_basis(L):
    """Compute eigenvectors (U) and eigenvalues (Λ) of Laplacian."""
    eigvals, eigvecs = eigh(L)
    return eigvals, eigvecs

def low_freq_components(returns_vector, eigvecs, n_low=5):
    """
    Project return vector onto the first n_low eigenvectors (lowest eigenvalues).
    Returns the projection coefficients (graph Fourier coefficients).
    """
    # Use eigenvectors corresponding to smallest eigenvalues
    U_low = eigvecs[:, :n_low]
    r_hat = U_low.T @ returns_vector
    return r_hat

def compute_scores(returns_df, window, threshold=0.3, n_low=5):
    """
    For the last `window` days of returns:
    - Build correlation graph from the entire window (static graph)
    - Compute graph Laplacian eigenvectors (once per window)
    - For the most recent day (last row), project its return vector onto low-frequency eigenvectors
    - Score for each ETF = magnitude of its low-frequency coefficient? Actually each ETF's score = low-freq component * sign(ETF return)
      But the low-freq component is a scalar for the whole market, not per ETF.
    Instead, we can compute the low-frequency reconstruction of the return vector: r_low = U_low * r_hat.
    Then for each ETF, score = r_low[i] (the reconstructed low-frequency part). That is the systematic market component aligned with ETF i.
    """
    # Use all returns in window to build graph
    ret_win = returns_df.iloc[-window:]
    adj, nodes = build_correlation_graph(ret_win, threshold)
    L = graph_laplacian(adj)
    eigvals, eigvecs = graph_fourier_basis(L)
    # Most recent day's return vector
    r_today = ret_win.iloc[-1].values
    # Project onto low-frequency eigenvectors
    r_hat = low_freq_components(r_today, eigvecs, n_low)
    # Reconstruct low-frequency part
    U_low = eigvecs[:, :n_low]
    r_low = U_low @ r_hat
    # Score per ETF = r_low (systematic component) times sign of original return? We'll use r_low directly.
    # To make it bullish for positive systematic component, we'll just use r_low.
    scores = {nodes[i]: r_low[i] for i in range(len(nodes))}
    return scores
