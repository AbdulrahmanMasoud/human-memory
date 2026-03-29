"""Episode clustering by embedding similarity for consolidation."""

import math


def cosine_similarity(a: list[float], b: list[float]) -> float:
    """Compute cosine similarity between two vectors."""
    dot = sum(x * y for x, y in zip(a, b))
    norm_a = math.sqrt(sum(x * x for x in a))
    norm_b = math.sqrt(sum(x * x for x in b))
    if norm_a < 1e-9 or norm_b < 1e-9:
        return 0.0
    return dot / (norm_a * norm_b)


def cluster_episodes(
    episodes: list[dict[str, object]],
    threshold: float = 0.7,
    min_cluster_size: int = 3,
) -> list[list[dict[str, object]]]:
    """Cluster episodes by embedding similarity using simple greedy clustering.

    Each episode dict must have 'embedding' (list[float]) and 'id' keys.

    Returns list of clusters, each containing min_cluster_size+ episodes.
    """
    if not episodes:
        return []

    assigned = [False] * len(episodes)
    clusters: list[list[dict[str, object]]] = []

    for i, ep_i in enumerate(episodes):
        if assigned[i]:
            continue

        cluster = [ep_i]
        assigned[i] = True

        for j, ep_j in enumerate(episodes):
            if assigned[j] or i == j:
                continue

            sim = cosine_similarity(
                ep_i["embedding"],  # type: ignore[arg-type]
                ep_j["embedding"],  # type: ignore[arg-type]
            )
            if sim >= threshold:
                cluster.append(ep_j)
                assigned[j] = True

        if len(cluster) >= min_cluster_size:
            clusters.append(cluster)
        else:
            # Unassign if cluster too small
            for ep in cluster:
                idx = episodes.index(ep)
                if idx != i:
                    assigned[idx] = False

    return clusters
