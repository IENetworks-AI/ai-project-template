import os
import pandas as pd

def test_extracted_data():
    path = "data/raw/procurement_data.csv"
    assert os.path.exists(path)
    df = pd.read_csv(path)
    assert not df.empty
