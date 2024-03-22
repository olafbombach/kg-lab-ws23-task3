from nicegui import ui, app
from typing import Union
from pathlib import Path
import orjson

from source.HelperFunctions import find_root_directory


class GUI:
    """
    Setup for the GUI that compares critical events.
    """
    TABLE_COLUMNS = [
        {"name": "qid", "label": "QID", "field": "qid", "align": "mid", "required": True, "sortable": False},
        {"name": "full_title", "label": "Full Title", "field": "full_title", "align": "left", "required": True, "sortable": False},
        {"name": "short_name", "label": "Short Name", "field": "short_name", "align": "center", "required": True, "sortable": False},
        {"name": "ordinal", "label": "Ordinal", "field": "ordinal", "align": "center", "required": True, "sortable": False},
        {"name": "part_of_series", "label": "Part of the Series", "field": "part_of_series", "align": "center", "required": True, "sortable": False},
        {"name": "country_name", "label": "Country", "field": "country_name", "align": "center", "required": True, "sortable": False},
        {"name": "countr_short", "label": "Country ID", "field": "country_short", "align": "center", "required": True, "sortable": False},
        {"name": "city_name", "label": "City", "field": "city_name", "align": "center", "required": True, "sortable": False},
        {"name": "year", "label": "Year", "field": "year", "align": "center", "required": True, "sortable": False},
        {"name": "start_time", "label": "Start Date", "field": "start_time", "align": "center", "required": True, "sortable": False},
        {"name": "end_time", "label": "End Time", "field": "end_time", "align": "center", "required": True, "sortable": False}     
    ]
    FINAL_COLUMNS = [
        {'name': 'feature', 'label': 'Feature', 'field': 'feature', 'align': 'left', 'required': True},
        {'name': 'proc_event', 'label': 'Proceedings Event', 'field': 'proc_event', 'align': 'center', 'required': True},
        {'name': 'your_choice', 'label': 'Your choice', 'field': 'your_choice', 'align': 'center', 'required': True}
    ]

    def __init__(self, files_directory: Path=find_root_directory() / "results" / "unclear_entries" / "manual.json"):
        self.f_dir = files_directory
        self.data_dict = self._read_json()  
        self.current_selected = None      
    
    def gui_main(self):
        """
        Take the up-most entry and starts the GUI.
        """
        key, info = list(self.data_dict.items())[0]
        
        proceed_data = [info['proc_event']]
        wikidata_data = list(info["loe"].values())
        entries_left = len(self.data_dict)

        self.GUI_design(proceedings_data=proceed_data, 
                        wikidata_entries=wikidata_data, 
                        entries_left=entries_left,
                        current_key=key)
        self.run()


    def GUI_design(self, proceedings_data: list, wikidata_entries: list, entries_left: int, current_key: str):    
        """
        design of the GUI here.
        """
        ui.markdown("# For this case, supervision is needed.")
        ui.markdown(f"Still {entries_left} entries left.")
        ui.html("<b>Proceedings Event:</b>")
        self.proc_table = ui.table(columns=GUI.TABLE_COLUMNS[1:], rows=proceedings_data)
        ui.html("<b>Wikidata Events that were the best hits:</b>")
        self.hit_table = ui.table(columns=GUI.TABLE_COLUMNS, rows=wikidata_entries, row_key="qid")

        ui.markdown("## Your choice in comparison to the Proceedings Event:")

        with ui.row():
            self.choice_table(selected_item=None)
            self.hit_table.on(type="rowClick", handler=lambda event: self.choice_table.refresh(selected_item=event.args[2]))

            with ui.card():
                ui.button(text="Clear", color="blue", on_click=lambda: self.choice_table.refresh(selected_item=None))
                ui.space()
                ui.space()
                ui.button(text="This is the correct hit!", color="green", on_click=lambda: self.change_to_found(current_key))
                ui.button(text="There is no good hit!", color="red", on_click=lambda: self.change_to_unfound(current_key))

    @staticmethod
    def run():
        """
        Creates and calls the GUI that is designed in the initialization.
        """
        ui.run(reload=False)

    def change_to_found(self, current_key: str):
        """
        When correct QID can be found:
        Take the current proceedings.com entry and delete it from this data_dict.
        Add QID and append it to results/found
        """
        selected_item = self.hit_table.rows[self.current_selected]
        qid_of_found = selected_item.get('qid')
        proc_entry = self.proc_table.rows[0]

        proc_entry['wd_qid'] = qid_of_found

        # delete from unclear_dataset
        self.data_dict.pop(current_key)

        # upload to found_dataset
        file_to_found = find_root_directory() / "results" / "found_entries" / "upload.json"

        with open(file_to_found, "r", encoding="utf-8") as json_file:
            json_str = json_file.read()
            found_dict = orjson.loads(json_str)

        found_dict[current_key] = proc_entry

        with open(file_to_found, "wb") as json_file:
            json_str = orjson.dumps(found_dict,
                                        option=
                                        orjson.OPT_INDENT_2 |
                                        orjson.OPT_NON_STR_KEYS | 
                                        orjson.OPT_SERIALIZE_NUMPY | 
                                        orjson.OPT_SERIALIZE_UUID | 
                                        orjson.OPT_NAIVE_UTC)
            json_file.write(json_str)
        
        ui.notify(f"Changed position of found entry {current_key} to results/found_entries.")

        self._update_json()
        app.shutdown

    def change_to_unfound(self, current_key: str):
        """
        When correct QID can not be found:
        Take the current proceedings.com entry and delete it from data_dict.
        Append it to results/unfound
        """
        proc_entry = self.proc_table.rows[0]

        # delete from unclear_dataset
        self.data_dict.pop(current_key)

        # upload to unfound_dataset
        file_to_unfound = find_root_directory() / "results" / "unfound_entries" / "upload.json"

        with open(file_to_unfound, "r", encoding="utf-8") as json_file:
            json_str = json_file.read()
            found_dict = orjson.loads(json_str)

        found_dict[current_key] = proc_entry

        with open(file_to_unfound, "wb") as json_file:
            json_str = orjson.dumps(found_dict,
                                        option=
                                        orjson.OPT_INDENT_2 |
                                        orjson.OPT_NON_STR_KEYS | 
                                        orjson.OPT_SERIALIZE_NUMPY | 
                                        orjson.OPT_SERIALIZE_UUID | 
                                        orjson.OPT_NAIVE_UTC)
            json_file.write(json_str)
        
        ui.notify(f"Changed position of unfound entry {current_key} to results/unfound_entries.")

        self._update_json()
        app.shutdown

    def get_your_choice(self, sel_item: Union[None, int]) -> list:
        """
        Method to define the current rows after selecting one specific item 
        The outcome of this method is a list with all new rows as dictionary.
        """
        new_rows = []

        if sel_item is not None:  # we have a selection
            for item in self.hit_table.rows[sel_item].items():
                if item[0] in self.proc_table.rows[0]:  # check wheter the item is also part of the Proceedings.com event or not
                    new_rows.append({"feature": item[0], 
                                     "proc_event": self.proc_table.rows[0][item[0]], 
                                     "your_choice": item[1]})
                else:  # this case is good for the signature of similarity (not part of Proceedings.com event)
                    new_rows.append({"feature": item[0],
                                     "proc_event": "-",
                                     "your_choice": item[1]})
        else:  # we have no selection yet
            for item in self.proc_table.rows[0].items():
                new_rows.append({"feature": item[0],
                                 "proc_event": item[1],
                                 "your_choice": "-"})
        self.current_selected = sel_item
        return new_rows
    
    @ui.refreshable
    def choice_table(self, selected_item: Union[None, int]) -> None:
        my_rows = GUI.get_your_choice(self, sel_item = selected_item)
        ui.table(columns=GUI.FINAL_COLUMNS, rows=my_rows)
    
    def _read_json(self):
        """
        Read in data-file of unclear_data.
        """
        with open(self.f_dir, "r", encoding="utf-8") as json_file:
            json_str = json_file.read()
            data_dict = orjson.loads(json_str)

        return data_dict
    
    def _update_json(self):
        """
        Write data-file of unclear_data after deletion of item.
        """
        with open(self.f_dir, "wb") as json_file:
            json_str = orjson.dumps(self.data_dict,
                                        option=
                                        orjson.OPT_INDENT_2 |
                                        orjson.OPT_NON_STR_KEYS | 
                                        orjson.OPT_SERIALIZE_NUMPY | 
                                        orjson.OPT_SERIALIZE_UUID | 
                                        orjson.OPT_NAIVE_UTC)
            json_file.write(json_str)
