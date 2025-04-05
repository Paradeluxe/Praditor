import numpy as np
from scipy.spatial import cKDTree
from collections import deque

class DBSCAN:
    def __init__(self, eps=0.5, min_samples=5, metric="manhattan"):
        self.eps = eps
        self.min_samples = min_samples

    def fit(self, X):
        n_samples = X.shape[0]
        tree = cKDTree(X)
        neighborhoods = tree.query_ball_point(X, r=self.eps, p=1)
        n_neighbors = np.array([len(neigh) for neigh in neighborhoods])
        core_samples = n_neighbors >= self.min_samples
        self.core_sample_indices_ = np.where(core_samples)[0]
        labels = np.full(n_samples, -1, dtype=int)
        cluster_id = 0

        for i in range(n_samples):
            if not core_samples[i] or labels[i] != -1:
                continue
            labels[i] = cluster_id
            queue = deque([i])

            while queue:
                current = queue.popleft()
                neighbors = neighborhoods[current]

                for neighbor in neighbors:
                    if labels[neighbor] == -1:
                        labels[neighbor] = cluster_id
                        if core_samples[neighbor]:
                            queue.append(neighbor)
            cluster_id += 1

        self.labels_ = labels
        return self

    def fit_predict(self, X):
        self.fit(X)
        return self.labels_