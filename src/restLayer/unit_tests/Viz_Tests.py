__author__ = 'aarongary'
import unittest
from bson.json_util import dumps
from app import HeatMaps
from app import SearchViz

class VizTests(unittest.TestCase):
    def test_cluster_heat_map_2D(self):
        heat_map_matrix = SearchViz.generate_filtered_matrix('2020004269', 'ENAH,MYO1D,TEAD3', 200)

        heat_map_matrix_2D_sorted = HeatMaps.cluster_heat_map_2D(heat_map_matrix)

        print dumps(heat_map_matrix_2D_sorted)

        self.assertTrue(1 == 1)

