import pandas as pd
import unittest
from processor.processor import Target

class TestTarget(unittest.TestCase):
    def setUp(self):
        df = pd.DataFrame()
        self.target = Target(df, "ICR1_M", "ICR1_UM")
        self.target.reference = "Control A"
        self.target.df = pd.DataFrame(
            {
                "Sample": ["Control A"],
                "dEqCq Mean": [-0.844]
            }
        )

    def test_find_outliers(self):
        values = [-0.683, -0.509, -0.420, -0.130]
        index = self.target.find_outliers(values, -0.7796)
        self.assertEqual(index, 3, "The index of the outlier should be 3")


if __name__ == '__main__':
    unittest.main()
