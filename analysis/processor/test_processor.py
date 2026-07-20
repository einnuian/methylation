import pandas as pd
import unittest
from processor.processor import Target

class TestTarget(unittest.TestCase):
    def setUp(self):
        df = pd.DataFrame(
            {   
                "Well": ["5", "5", "6", "6", "7", "7", "8", "8"],
                "Well Position": ["A5", "A5", "A6", "A6", "A7", "A7", "A8", "A8"],
                "Sample": ["Control A", "Control A", "Control A", "Control A", "Control A", "Control A", "Control A", "Control A"],
                "Target": ["ICR1_M", "ICR1_UM", "ICR1_M", "ICR1_UM", "ICR1_M", "ICR1_UM", "ICR1_M", "ICR1_UM"],
                "Cq": [29.19904654, 27.24041701, 28.96478726, 27.07540189, 28.98907573, 27.22249379, 29.06881308, 27.12756556]
            }
        )
        self.target = Target(df, "ICR1_M", "ICR1_UM")
        self.target.reference = "Control A"

    def test_find_outliers(self):
        '''values = [-0.683, -0.509, -0.420, -0.130]
        index = self.target.find_outliers(values, -0.7796)
        self.assertEqual(index, 3, "The index of the outlier should be 3")'''

        values = [3.826, 4.037, 4.028, 4.561]
        index = self.target.find_outliers(values, 4.113)
        self.assertEqual(index, 3, "The index of the outlier should be 3")


if __name__ == '__main__':
    unittest.main()
