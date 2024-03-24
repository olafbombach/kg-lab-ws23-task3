import os
import re
import orjson, json
from pathlib import Path

from wikibaseintegrator import WikibaseIntegrator
from wikibaseintegrator.wbi_config import config as wbi_config
from wikibaseintegrator.datatypes import *
from wikibaseintegrator.wbi_enums import ActionIfExists
from wikibaseintegrator.wbi_login import Clientlogin
from wikibaseintegrator.models import Qualifiers
from source.UpdateSources import WikidataQuery
from source.HelperFunctions import find_root_directory


class WikidataUpdater:
    """
    Adds the entries stored in the result/found_entries and result/unfound_entries folders onto Wikidata, by edit and upload respectively
    """
    def __init__(self, found: bool, wd_username: str = None, wd_password: str = None):
        """
        Initialize whether we look at the found or the not found entries here.
        """
        self.found = found
        self.data_dict = self._read_json()
        self.login = self.login(wd_username, wd_password)

    def update_all_entries(self):
        """
        Applies the loop over all current Events in the specified results-file.
        If an entry is created, deletes the item from the stored dictionary.
        In the end reuploads the dictionary. 
        
        Note: This might lead to an empty json-file.
        """
        print("herew again")
        for key, value in self.data_dict.copy().items():
            if self.found:  # found_entries (has wd_qid as attribute)
                try:
                    self.uploadToWikidata(dictionary=value, edit=True)
                    self.delete_item_of_dict(key)
                except Exception as e:
                    print("Error has occured.", e)
                    continue
            else:  # unfound_entries
                try:
                    self.uploadToWikidata(dictionary=value, edit=False)
                    self.delete_item_of_dict(key)
                except Exception as e:
                    print("Error has occured.", e)
                    continue
            self._restore_json()
            break

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
        wbi = WikibaseIntegrator(login = self.login)
        if edit:
            WDid = dictionary.get("wd_qid")
            entity = wbi.item.get(WDid)
        else:
            entity = wbi.item.new()
            
        print("Why is this now such a damn complicated mess")

        # get attributes
        full_title = dictionary.get("full_title")
        short_name = dictionary.get("short_name")
        ordinal = dictionary.get("ordinal")
        part_of_series = dictionary.get("part_of_series")
        country_name = dictionary.get("country_name")
        country_short = dictionary.get("country_short")
        country_qid = dictionary.get("country_qid")
        city_name = dictionary.get("city_name")
        city_qid = dictionary.get("city_qid")
        year = dictionary.get("year")
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
            pass

        #add start_time and end_time (property P580 and P582)
        if start_time:
            entity.claims.add(Time(start_time+"T00:00:00Z", precision=11, prop_nr="P580"))
        if end_time:
            entity.claims.add(Time(end_time+"T00:00:00Z", precision=11, prop_nr="P582"))
 
        #add event series (P179 = part of the series)
        if part_of_series:
            qualifiers = Qualifiers()
            if ordinal:
                #add only ordinals containing at most 2 digits
                if WikidataUpdater.count_digits_loop(ordinal) < 3:
                    # Add ordinal (series ordinal = P1545)
                    qualifiers.add(String(ordinal, prop_nr = "P1545"))
            WDid = WikidataQuery.getWDIdfromLabel(part_of_series)
            if WDid is None:
                WDid = WikidataUpdater.create_Series(self.login, part_of_series)
            entity.claims.add(Item(WDid, prop_nr="P179", qualifiers=qualifiers)) 

        #Instance of academic conference and proceeding
        entity.claims.add([Item("Q2020153", prop_nr="P31"),
                           Item("Q1143604", prop_nr="P31")])
        
        
        #Add ISBN-13 number
        references = [Item("Q108267044",prop_nr = "P248")]
        entity.claims.add(String(str(isbn),prop_nr = "P212", references = references))
        
        #entity.write()
        print(entity)
   
        #Basic information independant of entry
        #reference = References()
        #proceedingscom = Reference()

        return entity
    
    #Helperfunction count number of digits
    
    @staticmethod
    def count_digits_loop(s):
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
    
            
