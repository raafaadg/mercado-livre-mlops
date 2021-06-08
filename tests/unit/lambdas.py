from lambdas.trigger.trigger import calculate_formulas
from lambdas.scraper.main import get_refs_from_link
from unittest import TestCase, mock

class TestLambda(TestCase):

    def test_formulas(self):
        self.assertAlmostEqual(len(calculate_formulas('https://google.com', 2)),12)
        assert len(calculate_formulas('https://google.com', 2)) == 12

    def test_input_value(self):
        self.assertRaises(TypeError, calculate_formulas, True)

    def test_get_links_size(self):
        assert len(get_refs_from_link('https://google.com')) > 0

    def test_get_links_type(self):
        assert isinstance(get_refs_from_link('https://google.com'), list)
