import os
import re
import orjson, json
from pathlib import Path
from tqdm import tqdm

from wikibaseintegrator import WikibaseIntegrator
from wikibaseintegrator.wbi_config import config as wbi_config
from wikibaseintegrator.datatypes import *
from wikibaseintegrator.wbi_enums import ActionIfExists
from wikibaseintegrator.wbi_login import Clientlogin
from wikibaseintegrator.models import Qualifiers

from source.UpdateSources import WikidataQuery
from source.HelperFunctions import find_root_directory
from source.PPNIdentifier import ppnidentifier


class WikidataUpdater:
    """
    Adds the entries stored in the result/found_entries and result/unfound_entries folders 
    onto Wikidata, by edit and upload (respectively).
    """
    # lookup table for publishers that captures roughly 85 percent of proceedings.com
    PUBLISHER_DICT = {
        'Institute of Electrical and Electronics Engineers (IEEE)': 'Q131566', 'SPIE - International Society for Optics and Photonics': 'Q2140443',
        'Institute of Physics Publishing (IOP)': 'Q2915886', 'Atlantis Press': 'Q52660748', 'Elsevier Procedia': 'Q746413', 'EDP Sciences': 'Q114404',
        'Association for Computational Linguistics (ACL)': 'Q4346375', 'Electrochemical Society (ECS)': 'Q3721278', 
        'American Institute of Chemical Engineers (AIChE)': 'Q465184', 'International Academy, Research, and Industry Association (IARIA)': 'Q10850977',
        'American Institute for Aeronautics and Astronautics (AIAA)': 'Q465165', 'Cambridge University Press (CUP) / Materials Research Society (MRS)': 'Q912887',
        'Society of Petroleum Engineers (SPE)': 'Q2249890', 'American Society of Civil Engineers (ASCE)': 'Q466880',
        'American Society of Mechanical Engineers (ASME)': 'Q466950', 'Institution of Engineering and Technology (IET)': 'Q1164410',
        'European Association of Geoscientists and Engineers (EAGE)': 'Q1750463', 'Elsevier Science Direct - IFAC PapersOnline': 'Q2571518',
        'Schloss Dagstuhl': 'Q52663531', 'USENIX Association': 'Q2141768', 'American Institute of Physics (AIP)': 'Q465230',
        'Academic Conferences Ltd': 'Q52636351', 'Trans Tech Publications Ltd': 'Q30289413', 'Scientific Research Publishing Inc.': 'Q7433770',
        'Society for Imaging Science and Technology (IS&T)': 'Q3963258', 'Association for the Advancement of Artificial Intelligence (AAAI)': 'Q2739680',
        'Society for Modeling & Simulation International (SCS)': 'Q7552176', 'Science and Technology Publications, LDA (SciTePress)': 'Q106714378',
        'International Astronautical Federation (IAF)': 'Q1634011'
        }


    def __init__(self, found: bool, wd_username: str = None, wd_password: str = None):
        """
        Initialize whether we look at the found or the not found entries here.
        Further specify credentials if it does not lie in home-dir or env.
        """
        self.found = found
        self.data_dict = self._read_json()
        self._login = self.login(wd_username, wd_password)

    def update_all_entries(self, current_limit: int = 8):
        """
        Applies the loop over all current Events in the specified results-file.
        If an entry is created, deletes the item from the stored dictionary.
        In the end reuploads the dictionary. 
        
        Note: This might lead to an empty json-file.
        """
        i = 0
        for key, value in tqdm(self.data_dict.copy().items()):  # set copy for adapting self.data_dict
            i += 1 

            if self.found:  # found_entries (has wd_qid as attribute)
                try:
                    self.uploadToWikidata(dictionary=value, edit=True)
                    self.delete_item_of_dict(key)
                except Exception as e:
                    print("Upload error has occured.", e)
                    continue
            else:  # unfound_entries
                try:
                    self.uploadToWikidata(dictionary=value, edit=False)
                    self.delete_item_of_dict(key)
                except Exception as e:
                    print("Upload error has occured.", e)
                    continue
            if i >= current_limit:
                print(f"\nMax-Limit of {current_limit} reached.")
                break
        self._restore_json()
        

    def delete_item_of_dict(self, key: str):
        """
        Naive approach to delete the item of the json-file.
        """
        self.data_dict.pop(key)

    def uploadToWikidata(self, dictionary: dict, edit: bool):
        """
        Performs an edit operation on a Wikidata object.
        Parameters: 
        dictionary: The information on the proceeding found in proceedings.com as dict
        edit: boolean if it is a edit-case or not
        Output:
        A WikibaseIntegrator Entity (base-entity class) describing the created object
        """
        wbi = WikibaseIntegrator(login=self._login)
        if edit:
            WDid_entry = dictionary.get("wd_qid")
            entity = wbi.item.get(WDid_entry)
        else:
            entity = wbi.item.new()

        # get attributes
        full_title = dictionary.get("full_title")
        short_name = dictionary.get("short_name")
        ordinal = dictionary.get("ordinal")
        part_of_series = dictionary.get("part_of_series")
        country_name = dictionary.get("country_name")
        country_short = dictionary.get("country_short")  # not needed..
        country_qid = dictionary.get("country_qid")
        city_name = dictionary.get("city_name")
        city_qid = dictionary.get("city_qid")
        year = dictionary.get("year")
        publisher = dictionary.get("publisher")
        start_time = dictionary.get("start_time")
        end_time = dictionary.get("end_time")
        isbn = dictionary.get("isbn")

        # create and set label
        label = full_title
        if ordinal is not None and WikidataUpdater.count_digits_loop(ordinal) < 3:
            label = ordinal + " " + label
        if city_name is not None:
            label = label + ", " + city_name
            if country_name is not None:
                label = label + ", " + country_name
        if year is not None:
            label = label + f" ({year})"

        label = re.sub(r'\s{2,}', ' ', label)
        label = label.rstrip()
        
        entity.labels.set('en', label, action_if_exists=ActionIfExists.KEEP) 

        # add country (property P17 = country)
        if country_qid:
            pass
        else:
            country_qid = WikidataQuery.getWDIdfromLabel(country_name)
        entity.claims.add(Item(country_qid, prop_nr="P17"))

        # add city (property P276 = location)
        if city_qid:
            pass
        else:
            city_qid = WikidataQuery.getWDIdfromLabel(city_name)
        entity.claims.add(Item(city_qid, prop_nr="P276"))
        
        # add short_name (property P1813 = Short Name)
        if short_name:
            entity.claims.add(MonolingualText(short_name, prop_nr="P1813"))
        else:
            pass

        # add event series (property P179)
        if part_of_series:
            # This is still problematic...
            pass

        # add start_time and end_time (property P580 and P582)
        if start_time:
            entity.claims.add(Time(start_time+"T00:00:00Z", precision=11, prop_nr="P580"))
        if end_time:
            entity.claims.add(Time(end_time+"T00:00:00Z", precision=11, prop_nr="P582"))
 
        # this is still problematic ...
        '''if part_of_series:
            qualifiers = Qualifiers()
            if ordinal:
                #add only ordinals containing at most 2 digits
                if WikidataUpdater.count_digits_loop(ordinal) < 3:
                    # Add ordinal (series ordinal = P1545)
                    qualifiers.add(String(ordinal, prop_nr = "P1545"))

            WDid = WikidataQuery.getWDIdfromLabel(part_of_series)
            if WDid is None:
                WDid = WikidataUpdater.create_Series(self.login, part_of_series)
            entity.claims.add(Item(WDid, prop_nr="P179", qualifiers=qualifiers))'''

        #Instance of academic conference and proceeding
        entity.claims.add([Item("Q2020153", prop_nr="P31"),
                           Item("Q1143604", prop_nr="P31")])
        
        # Add publisher
        if publisher:
            pub_qid = WikidataUpdater.PUBLISHER_DICT.get(publisher)
            if pub_qid:
                entity.claims.add(Item(pub_qid, prop_nr="P123"))
            else:
                pass
        else: 
            pass

        #Add ISBN-13 number (in viable format)
        references = [Item("Q108267044", prop_nr="P248")]
        correct_isbn = isbn[0:3]+"-"+isbn[3]+"-"+isbn[4:7]+"-"+isbn[7:12]+"-"+isbn[12]
        entity.claims.add(String(correct_isbn, prop_nr="P212", references=references))

        # KD10+ identifier
        current_ppn = ppnidentifier(isbn=isbn, output_type_k10plus=False)[0]
        if type(current_ppn) == str:
            entity.claims.add(String(current_ppn, prop_nr="P6721"))
        else:
            pass

        entity.write(login=self._login)
   
    @staticmethod
    def count_digits_loop(s):
        """
        Helperfunction to check whether the ordinal is correct or not.
        """
        count = 0
        for char in s:
            if char.isdigit():
                count += 1
        return count
    
    @staticmethod
    def create_Series(login, label):
        """
        Static Method that creates an entry for a proceedings series (label only)
        It is called if such an object does not exist in uploadToWikidata and editOnWikidata
        Returns the Wikidata ID of the created object
        """
        wbi = WikibaseIntegrator(login = login)
        entity = wbi.item.new()
        entity.labels.set('en', label)
        entity.claims.add(Item("Q27785883",prop_nr = "P31"))
        entity.write()
        return entity.id
    
    @staticmethod
    def login(wd_username: str, wd_password: str):
        """
        Static method that uses the credentials stored either locally in "home/.wd_credentials/wd_credentials.json" as json or as environment 
        variables. 
        Returns a login object.
        """
        # get Wikidata credentials
        if wd_username and wd_password:
            pass
        else:
            # Load the credentials from the environment
            wd_username = os.getenv("WIKIDATA_LOGIN_NAME")
            wd_password = os.getenv("WIKIDATA_LOGIN_PASSWORD")

            # or a JSON file in home dir
            json_file = Path.home() / ".wd_credentials" / "wd_credentials.json"

            if wd_username is None and wd_password is None and json_file.resolve().is_file():
                with open(json_file, "r", encoding="utf-8") as file:
                    data = json.load(file)
                    wd_username = data.get("user")
                    wd_password = data.get("password")

        if wd_username is None and wd_password is None:
            raise ValueError(
                "No Wikidata credentials found. Please set corresponding "
                "environment variables or "
                "store it in `~/.wd_credentials/wd_credentials.json`.")
        
        # get login
        wbi_config['USER_AGENT'] = 'MyWikibaseBot/1.0 (https://www.wikidata.org/wiki/https://github.com/olafbombach/kg-lab-ws23-task3/actions/runs/8364288152/job/22899251617)'
        login = Clientlogin(user=wd_username, password=wd_password)

        return login  
      
    def _read_json(self) -> dict:
        """
        Reads in the json-file specified with the found-attribute.
        Returns a dictionary that has to be uploaded.
        """
        if self.found:
            folder = "found_entries"
        else:
            folder = "unfound_entries"

        file_path = find_root_directory() / "results" / folder / "upload.json"

        with open(file_path, "r", encoding="utf-8") as json_file:
            json_str = json_file.read()
            data_dict = orjson.loads(json_str)

        return data_dict
    
    def _restore_json(self):
        """
        Restores json after the entries are created of the json file.
        Only non-working entries are still left in the json.
        """
        if self.found:
            folder = "found_entries"
        else:
            folder = "unfound_entries"

        file_path = find_root_directory() / "results" / folder / "upload.json"

        try:
            with open(file_path, 'wb') as f:
                json_str = orjson.dumps(self.data_dict,
                                        option=
                                        orjson.OPT_INDENT_2 |
                                        orjson.OPT_NON_STR_KEYS | 
                                        orjson.OPT_SERIALIZE_NUMPY | 
                                        orjson.OPT_SERIALIZE_UUID | 
                                        orjson.OPT_NAIVE_UTC)
                f.write(json_str)
        except Exception as e:
            raise Exception(f"Error updating json-file due to {e}")


if __name__ == "__main__":
    wu = WikidataUpdater(found=False)
    wu.update_all_entries()

