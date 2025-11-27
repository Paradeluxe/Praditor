"""Unsupervised nearest neighbors learner"""

# Authors: The scikit-learn developers
# SPDX-License-Identifier: BSD-3-Clause

from ._base import KNeighborsMixin, NeighborsBase, RadiusNeighborsMixin


class NearestNeighbors(KNeighborsMixin, RadiusNeighborsMixin, NeighborsBase):


    def __init__(
        self,
        *,
        n_neighbors=5,
        radius=1.0,
        algorithm="auto",
        leaf_size=30,
        metric="minkowski",
        p=2,
        metric_params=None,
        n_jobs=None,
    ):
        super().__init__(
            n_neighbors=n_neighbors,
            radius=radius,
            algorithm=algorithm,
            leaf_size=leaf_size,
            metric=metric,
            p=p,
            metric_params=metric_params,
            n_jobs=n_jobs,
        )

    def fit(self, X, y=None):
        """Fit the nearest neighbors estimator from the training dataset.

        Parameters
        ----------
        X : {array-like, sparse matrix} of shape (n_samples, n_features) or \
                (n_samples, n_samples) if metric='precomputed'
            Training data.

        y : Ignored
            Not used, present for API consistency by convention.

        Returns
        -------
        self : NearestNeighbors
            The fitted nearest neighbors estimator.
        """
        return self._fit(X)
