import os
import shutil
import urllib.request
from tqdm import tqdm
from urllib.parse import urlparse
import zipfile
from source.HelperFunctions import find_root_directory


class DownloadProgressBar(tqdm):
    def update_to(self, b=1, bsize=1, tsize=None):
        if tsize is not None:
            self.total = tsize
        self.update(b * bsize - self.n)

class Downloader:

    @staticmethod
    def glove_downloader(url: str = "https://nlp.stanford.edu/data/glove.6B.zip"):
        try:
            # Parse the URL to extract the filename
            parsed_url = urlparse(url)
            filename = os.path.basename(parsed_url.path)

            # Download the file
            with DownloadProgressBar(unit='B', unit_scale=True, miniters=1, desc=url.split('/')[-1]) as t:
                urllib.request.urlretrieve(url, filename=filename, reporthook=t.update_to)

            # Move the downloaded file to the destination directory
            destination_path = find_root_directory() / "datasets" # Path to destination
            shutil.move(filename, destination_path) # Move the file 
            print(f"File downloaded and moved to {destination_path}")

            # Extract the zip file
            zip_filepath = os.path.join(destination_path, filename)
            with zipfile.ZipFile(zip_filepath, 'r') as zf:
                for member in tqdm(zf.infolist(), desc='Extracting '):
                    try:
                        zf.extract(member, destination_path)
                    except zipfile.error as e:
                        pass
            print("Zip file contents extracted successfully.")

            # Remove zip
            os.remove(zip_filepath)
            print("Zip file removed.")
        except Exception as e:
            print(f"Error: {e}")

# Test            
#a = Downloader()
#a = Downloader("https://getsamplefiles.com/download/zip/sample-1.zip")
#a.glove_downloader("https://nlp.stanford.edu/data/glove.6B.zip")
#a.glove_downloader("https://getsamplefiles.com/download/zip/sample-1.zip")
#a.glove_downloader()