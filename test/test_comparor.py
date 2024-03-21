from source.Comparor import Comparor
import numpy as np

vec = np.array([1.4, 0.3, 4.8, 2.6, 6.7, 8.1, 1.1])


def test_euc():
    """
    Test the function that creates the euclidean distance similarity.
    """
    dist = Comparor.euclidean_similarity(vec, vec)
    assert dist == 0.0, "The euclidean distance measure is incorrect!"

def test_cos():
    """
    Test the function that creates the cosine similarity.
    """
    sim = Comparor.cos_similarity(vec, vec)
    assert sim == 1.0, "The cosine similarity measure is incorrect!"

