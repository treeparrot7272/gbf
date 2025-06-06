def post_test_probability(pre_test_probability: float, likelihood_ratio: float) -> float:
    """
    Calculates post-test probability given pre-test probability and a likelihood ratio.
    """
    pre_test_odds = pre_test_probability / (1 - pre_test_probability)
    post_test_odds = pre_test_odds * likelihood_ratio
    return post_test_odds / (1 + post_test_odds)
