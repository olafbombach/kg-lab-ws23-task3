import os
import shutil
import urllib.request
from tqdm import tqdm
from urllib.parse import urlparse
import zipfile

from source.HelperFunctions import find_root_directory
from source.UpdateSources import WikidataQuery, ProceedingsUpdater


class DownloadProgressBar(tqdm):
    def update_to(self, b=1, bsize=1, tsize=None):
        if tsize is not None:
            self.total = tsize
        self.update(b * bsize - self.n)

class Downloader:
    """
    The class to download all necessary files.

    You should either call download_all() or update_datsets()
    depending on if the Glove dataset is already updated.
    """

    def download_all():
        """
        Downloads all needed resources for the pipeline.
        This function creates:
        Wikidata-file, Proceedings-file and Glove embedding files.
        """
        print("Downloading Wikidata resources...")
        Downloader.wikidata_downloader()
        print("Downloading Proceedings.com resources...")
        Downloader.proceedings_downloader()
        print("Downloading GloVe resources...")
        Downloader.glove_downloader()

    def update_datasets():
        """
        Updates the versions of the Wikidata-csv and the Proceedings.com excel file.
        """
        print("Downloading Wikidata resources...")
        Downloader.wikidata_downloader()
        print("Downloading Proceedings.com resources...")
        Downloader.proceedings_downloader()

    @staticmethod
    def glove_downloader(url: str = "https://nlp.stanford.edu/data/glove.6B.zip"):
        """
        Download the Glove encoding database.
        """
        try:
            # Parse the URL to extract the filename
            parsed_url = urlparse(url)
            filename = os.path.basename(parsed_url.path)

            # Download the file
            with DownloadProgressBar(unit='B', unit_scale=True, miniters=1, desc=url.split('/')[-1]) as t:
                urllib.request.urlretrieve(url, filename=filename, reporthook=t.update_to)

            # Move the downloaded file to the destination directory
            destination_path = find_root_directory() / "datasets" / "glove" 
            shutil.move(filename, destination_path) # Move the file 

            # Extract the zip file
            zip_filepath = os.path.join(destination_path, filename)
            with zipfile.ZipFile(zip_filepath, 'r') as zf:
                for member in tqdm(zf.infolist(), desc='Extracting '):
                    try:
                        zf.extract(member, destination_path)
                    except zipfile.error as e:
                        pass

            # Remove zip
            os.remove(zip_filepath)

        except Exception as e:
            print(f"Error: {e}")

        for i in range(3):
            try:
                os.remove(destination_path / f"glove.6B.{i+1}00d.txt")     
            except FileNotFoundError as e:
                print(f"filename: {destination_path} / glove.6B.{i+1}00d.txt does not exist after download?")

    @staticmethod
    def wikidata_downloader():
        """
        Queries the Wikidata database for conferences and creates a csv-file.
        """
        wdq = WikidataQuery()
        wdq.create_wikidata_dataset(overwrite_dataset=True)

    @staticmethod
    def proceedings_downloader():
        """
        Scraps the current cumulative entry of Proceedings.com and saves it in excel format.
        """
        ProceedingsUpdater.updateProceedings()

