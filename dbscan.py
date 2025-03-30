import numpy as np


class DBSCAN:
    """DBSCAN clustering using Manhattan distance.

    Parameters
    ----------
    eps : float, default=0.5
        The maximum Manhattan distance between two samples for one to be considered
        as in the neighborhood of the other.

    min_samples : int, default=5
        The number of samples in a neighborhood for a point to be considered as a core point.

    Attributes
    ----------
    core_sample_indices_ : ndarray
        Indices of core samples.

    labels_ : ndarray
        Cluster labels for each point. Noisy samples are labeled -1.
    """

    def __init__(self, eps=0.5, min_samples=5, metric="manhattan"):
        self.eps = eps
        self.min_samples = min_samples

    def fit(self, X):
        """Perform DBSCAN clustering.

        Parameters
        ----------
        X : ndarray of shape (n_samples, n_features)
            The input data to cluster.
        """
        n_samples = X.shape[0]

        # Calculate pairwise Manhattan distances
        distances = np.sum(np.abs(X[:, np.newaxis, :] - X[np.newaxis, :, :]), axis=2)

        # Find neighbors within eps distance (including self)
        neighborhoods = [np.where(dist <= self.eps)[0] for dist in distances]

        # Count neighbors (including self)
        n_neighbors = np.array([len(neigh) for neigh in neighborhoods])

        # Identify core points
        core_samples = n_neighbors >= self.min_samples
        self.core_sample_indices_ = np.where(core_samples)[0]

        # Initialize labels (-1 for noise)
        labels = np.full(n_samples, -1, dtype=int)
        cluster_id = 0

        for i in range(n_samples):
            if not core_samples[i] or labels[i] != -1:
                continue  # Skip non-core points or already labeled points

            # Start new cluster
            labels[i] = cluster_id
            queue = [i]

            # Expand the cluster
            while queue:
                current = queue.pop(0)

                # Get all reachable points from current core point
                neighbors = neighborhoods[current]

                for neighbor in neighbors:
                    if labels[neighbor] == -1:  # If unvisited
                        labels[neighbor] = cluster_id

                        # If neighbor is core, add its neighbors to queue
                        if core_samples[neighbor]:
                            queue.append(neighbor)

            cluster_id += 1

        self.labels_ = labels
        return self

    def fit_predict(self, X):
        """Perform clustering and return cluster labels."""
        self.fit(X)
        return self.labels_