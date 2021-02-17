from unittest import TestCase
import Kittens.utils


class TestUtils(TestCase):
    def test_pyfits(self):
        Kittens.utils.import_pyfits()
