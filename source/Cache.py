from source.HelperFunctions import find_root_directory

from typing import Union
import orjson

class CacheManager:
    """
    A JSON based Cache manager to store already semantified Wikidata entries.
    """

    def __init__(self, json_path: str = "semwikientry"):
        self.json_path = CacheManager.set_json_path(json_path)
        self.current_dict = {}

    @staticmethod
    def set_json_path(json_path: str) -> str:
        """
        Set the JSON path to the cache.
        """
        assert not json_path.endswith(".json"), "Only give the name without the file ending."
        root_path = find_root_directory()
        dir_path = root_path / "cache"
        json_path = f"{dir_path}/{json_path}.json"
        return json_path
    
    def load_cache(self):
        """
        Load the Cache to get information about Wikidata Events.
        """
        try:
            with open(self.json_path, encoding="utf-8") as f:
                json_str = f.read()
                if not json_str:
                    # If the file is empty, set self.current_dict to an empty dictionary
                    self.current_dict = dict()
                else:
                    # Load the cache from the existing file
                    self.current_dict = orjson.loads(json_str)
        except FileNotFoundError:
            # Handle case where file does not exist
            print("Cache does not exist yet. It will be initialized after the first iteration.")
        except Exception as e:
            # Handle other exceptions (e.g., invalid JSON data)
            print(f"Error loading cache due to {e}")

    def store_cache(self):
        """
        Store the changed dictionary in the cache again.
        """
        try:
            with open(self.json_path, 'wb') as f:
                json_str = orjson.dumps(self.current_dict,
                                        option=
                                        orjson.OPT_INDENT_2 |
                                        orjson.OPT_NON_STR_KEYS | 
                                        orjson.OPT_SERIALIZE_NUMPY | 
                                        orjson.OPT_SERIALIZE_UUID | 
                                        orjson.OPT_NAIVE_UTC)
                f.write(json_str)
        except Exception as e:
            raise Exception(str(e))
    
    def get_entry(self, qid: str) -> Union[dict,None]:
        """
        From the dictionary search for the specified qid.
        If nothing can be found, will return nothing.
        """
        return self.current_dict.get(qid, None)
    
    def add_entry(self, qid: str, qid_dict: dict) -> None:
        """
        Stores the new entry in the current dictionary.
        """
        self.current_dict[qid] = qid_dict
    
'''if __name__ == "__main__":
    cm = CacheManager("test")
    dicti = {"full_title": "IIFI 2001", "city": "Göttingen"}
    cm.current_dict = dicti
    cm.store_cache()'''
