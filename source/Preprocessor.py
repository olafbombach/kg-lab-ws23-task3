import polars as pl
from typing import Optional, Union
import json
from pathlib import Path


class Preprocessor:
    def __init__(self, raw_data: Union[pl.DataFrame, object]) -> None:
        """
        Initialize with the data you want to preprocess.
        Takes a polars DataFrame or a json as input.
        Currently, (08.02.2024) only DataFrame!
        """
        self._raw_data = raw_data
        self._preprocessed_data = raw_data

    def apply_preprocessing_pipeline(self, del_columns: Optional[list] = None) -> None:
        """
        Applies the preprocessing pipeline for the specified data.
        Please make sure that the deletion_columns can be applied, since no errors will occur otherwise.
        """
        if type(self._raw_data) == pl.DataFrame:
            if del_columns is not None:
                Preprocessor.delete_columns(self, del_columns)
            Preprocessor.delete_duplicates(self)
            Preprocessor.to_string(self)
            Preprocessor.preproc_years(self)
            Preprocessor.fill_null(self)

    def delete_columns(self, columns: list) -> None:
        for string in columns:
            self._preprocessed_data = self._preprocessed_data.drop(string)

    def delete_duplicates(self) -> None:
        columns = self._preprocessed_data.columns
        columns_without_index = [col for col in columns if col != "index"]
        self._preprocessed_data = self._preprocessed_data.unique(columns_without_index, maintain_order=True)

    def to_string(self) -> None:
        self._preprocessed_data = self._preprocessed_data.cast(pl.String)

    def preproc_years(self) -> None:
        columns = self._preprocessed_data.columns

        # check if columns include specific columns:
        if "beginnings" in columns:
            # if they end with ".0", drop the end
            self._preprocessed_data = self._preprocessed_data.with_columns(pl.col("beginnings").str.replace("\.0$", ""))

    def fill_null(self) -> None:
        self._preprocessed_data = self._preprocessed_data.fill_null("")
        self._preprocessed_data = self._preprocessed_data.fill_nan("")

    @property
    def get_raw_data(self) -> Union[pl.DataFrame, object]:
        return self._raw_data

    @property
    def get_preprocessed_data(self) -> Union[pl.DataFrame, object]:
        return self._preprocessed_data


if __name__ == "__main__":

    repo_path = Path(__file__).parent.parent.resolve()
    test_frame = pl.read_csv(repo_path / "datasets" / "wikidata" / "testset_v1.csv", separator=';')
    pr = Preprocessor(test_frame)
    pr.apply_preprocessing_pipeline()
    print(pr.get_preprocessed_data)

