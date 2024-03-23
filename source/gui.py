from typing import Union
from functools import partial
import orjson
from collections import OrderedDict

from nicegui import ui, background_tasks
import asyncio

from source.HelperFunctions import find_root_directory

class DataHandler:
    
    def __init__(self):
        self.f_dir = find_root_directory() / "results" / "unclear_entries" / "manual.json"
        self.data_dict = None

        self.current_data = None
        self.current_key = None
        self.current_choice = None

    async def fetch_data(self) -> tuple:
        """
        Get the data from the unclear entries json file.
        Give the information about the current top data to the GUI.
        """
        
        data_dict = await DataHandler._read_json(self.f_dir)
        self.data_dict = data_dict

        self.current_key, self.current_data = list(self.data_dict.items())[0]  # first item to read

        proc_data = [self.current_data['proc_event']]
        hit_data = list(self.current_data["loe"].values())

        await asyncio.sleep(1.5)

        return len(self.data_dict), proc_data, hit_data
    
    async def update_data(self, action: str) -> tuple:
        """
        First take the current selection.
        """
        await asyncio.sleep(1)
        # change directory of current data and delete from unclear directory
        if action == "found":
            # get the current_selection after communication with GUI
            qid_selection = list(self.current_data["loe"].values())[self.current_choice]['qid']
            await self._change_to_dir(qid_selection=qid_selection)
        elif action == "unfound":
            await self._change_to_dir(qid_selection=None)

        # reading new first entry after the update step
        data_dict = await DataHandler._read_json(self.f_dir)
        self.data_dict = data_dict

        self.current_key, self.current_data = list(self.data_dict.items())[0]

        proc_data = [self.current_data['proc_event']]
        hit_data = list(self.current_data["loe"].values())

        return len(self.data_dict), proc_data, hit_data
    
    async def skip_data(self) -> tuple:
        """
        Put current data to the end of the dictionary and fetch the next item.
        """
        await asyncio.sleep(1)
        self.data_dict.move_to_end(key=self.current_key)

        self.current_key, self.current_data = list(self.data_dict.items())[0]

        proc_data = [self.current_data['proc_event']]
        hit_data = list(self.current_data["loe"].values())

        return len(self.data_dict), proc_data, hit_data
    
    async def _change_to_dir(self, qid_selection: Union[str,None]) -> None:
        """
        Delete the current data from the data dict 
        and change its direction to either found or unfound entries.
        Further updates the unclear json.
        """
        proc_entry = self.current_data['proc_event']
        
        if qid_selection:
            proc_entry['wd_qid'] = qid_selection
        else:
            pass

        # delete from unclear_dataset
        self.data_dict.pop(self.current_key)

        # upload to corresponding dataset
        if qid_selection:
            filename = find_root_directory() / "results" / "found_entries" / "upload.json"
        else:
            filename = find_root_directory() / "results" / "unfound_entries" / "upload.json"

        dir_dict = await DataHandler._read_json(filename=filename)
        dir_dict[self.current_key] = proc_entry  # add entry
        await DataHandler._update_json(filename=filename, data=dir_dict)
        if qid_selection:
            ui.notify(f"Changed position of found entry {self.current_key} to results/found_entries.")
        else:
            ui.notify(f"Changed position of found entry {self.current_key} to results/unfound_entries.")
        await self._update_json(self.f_dir, self.data_dict)
            
    @staticmethod
    async def _read_json(filename: str) -> OrderedDict:
        """
        Read in data-file of unclear_data.
        """
        try:
            with open(filename, "r", encoding="utf-8") as json_file:
                json_str = json_file.read()
                data_dict = orjson.loads(json_str)
                data_dict = OrderedDict(data_dict.items())
            return data_dict
        except FileNotFoundError:
            raise FileNotFoundError(f"{filename} does not exist! \nYou first have to perform the pipeline to get data.")
        except Exception as e:
            raise Exception(f"Unexpected Error due to: {e}")
    
    @staticmethod
    async def _update_json(filename: str, data: dict):
        """
        Write data-file of unclear_data after deletion of item.
        """
        with open(filename, "wb") as json_file:
            json_str = orjson.dumps(data,
                                    option=
                                    orjson.OPT_INDENT_2 |
                                    orjson.OPT_NON_STR_KEYS | 
                                    orjson.OPT_SERIALIZE_NUMPY | 
                                    orjson.OPT_SERIALIZE_UUID | 
                                    orjson.OPT_NAIVE_UTC)
            json_file.write(json_str)

    def current_setter(self, choice):
        self.current_choice = choice

class Gui:

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

    @ui.page("/")
    def index_page():
        async def load(first_iter: bool, action: Union[str, None] = None):
            """
            First async for set up and fetching
            """
            if first_iter:
                try:
                    current_data = await dh.fetch_data()
                except IndexError as e:
                    raise IndexError(f"Because there are no entries in the unclear state! \nPlease make sure to first apply the pipeline.")
                except FileNotFoundError as e:
                    raise FileNotFoundError(e)
                except Exception as e:
                    raise Exception(f"Unexpected error due to {e}.")
                content.clear()
            else:
                if action == "skip":
                    # here should be no Error call (just sorting of OrderedDict)
                    current_data = await dh.skip_data()
                    content.clear()
                elif action == "found" or "unfound":
                    try:
                        current_data = await dh.update_data(action=action)
                    except IndexError as e:
                        raise IndexError(f"You cleared all of the unclear states! \n Please perform the pipeline to get new entries!")
                    except Exception as e:
                        raise Exception(f"Unexpected error due to {e}.")
                    content.clear()
        
            async def skip():
                """
                Second async to continue after one iteration (crucial)!
                """
                await asyncio.sleep(0.5) # for better feeling of the button
                content.clear()
                with content:
                    ui.spinner(size="10em")
                    ui.markdown("Get new data...")

                await load(first_iter=False, action="skip")

            async def new_data(action: str):
                """
                Second async to continue after one iteration (crucial)!
                """
                await asyncio.sleep(0.5) # for better feeling of the button
                content.clear()
                with content:
                    ui.spinner(size="10em")
                    ui.markdown("Get new data...")
                    ui.timer(5, lambda: ui.notify("Something is not correct! :( Please check your prompt!"), once=True)

                await load(first_iter=False, action=action)


            with content:
                # actual content of the UI
                ui.markdown("# For this case, supervision is needed.")
                
                with ui.row():
                    if current_data[0] > 1:
                        ui.markdown(f"Still {current_data[0]} entries left.")
                    else:
                        ui.markdown(f"Still {current_data[0]} entry left.")
                    ui.button(text='skip', on_click=partial(skip))
                
                ui.html("<b>Proceedings Event:</b>")
                proc_table = ui.table(columns=Gui.TABLE_COLUMNS[1:], rows=current_data[1])

                ui.html("<b>Wikidata Events that were the best hits:</b>")
                hit_table = ui.table(columns=Gui.TABLE_COLUMNS, rows=current_data[2], row_key="qid")

                ui.markdown("## Your choice in comparison to the Proceedings Event:")

                with ui.row():
                    Gui.choice_table(hit_table=hit_table, proc_table=proc_table, selected_item=None)
                    hit_table.on(type="rowClick", handler=lambda event: Gui.choice_table.refresh(selected_item=event.args[2]))
                    
                    with ui.card():
                        ui.button(text="Clear", color="blue", on_click=lambda: Gui.choice_table.refresh(selected_item=None))
                        ui.space()
                        ui.space()
                        ui.button(text="This is the correct hit!", color="green", on_click=partial(new_data, "found"))
                        ui.button(text="There is no good hit!", color="red", on_click=partial(new_data, "unfound"))

        with ui.card() as content:
            ui.spinner(size="10em")
            ui.markdown("Fetching data...")
            ui.timer(5, lambda: ui.notify("Something is not correct! :( Please check your prompt!"), once=True)
            background_tasks.create(load(first_iter=True))

    @ui.refreshable
    def choice_table(hit_table: ui.table, proc_table: ui.table, selected_item: Union[None, int]) -> ui.table:
        """
        The definition of the choice table depicted at the bottom of the GUI.
        """
        my_rows = Gui.get_your_choice(hit_table, proc_table, sel_item=selected_item)
        
        ui.table(columns=Gui.FINAL_COLUMNS, rows=my_rows)

    def get_your_choice(hit_table: ui.table, proc_table: ui.table, sel_item: Union[None, int]) -> list:
        """
        Method to define the current rows after selecting one specific item 
        The outcome of this method is a list with all new rows as dictionary.
        """
        new_rows = []
        if type(sel_item) == int:  # we have a selection
            for item in hit_table.rows[sel_item].items():
                if item[0] in proc_table.rows[0]:  # check whether the item is also part of the Proceedings.com event or not
                    new_rows.append({"feature": item[0], 
                                     "proc_event": proc_table.rows[0][item[0]], 
                                     "your_choice": item[1]})
                else:  # this case is good for the signature of similarity (not part of Proceedings.com event)
                    new_rows.append({"feature": item[0],
                                     "proc_event": "-",
                                     "your_choice": item[1]})
        else:  # we have no selection yet
            for item in proc_table.rows[0].items():
                new_rows.append({"feature": item[0],
                                 "proc_event": item[1],
                                 "your_choice": "-"})
                
        dh.current_setter(sel_item)
        return new_rows


if __name__ in { '__main__', '__mp_main__' } :
    dh = DataHandler()
    
    gui = Gui()
    ui.run()
