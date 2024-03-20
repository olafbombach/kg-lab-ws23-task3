from source.UpdateSources import ProceedingsUpdater
import polars as pl
from source.HelperFunctions import find_root_directory

def test_proceedingsupdater():
    filename=ProceedingsUpdater.updateProceedings()
    assert len(filename)>0
    path=find_root_directory()
    path_to_dataset = path / "datasets" / "proceedings.com"
    data_proceedings = pl.read_excel(path_to_dataset /filename,engine='openpyxl')
    assert data_proceedings.shape[0]>10000
    print(data_proceedings.shape[0])