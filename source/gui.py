from nicegui import ui
from typing import Union


class GUI:
    """
    Setup for the GUI that compares critical events.
    """
    def __init__(self, files_directory):
        self.f_dir = files_directory
    

table_columns = [
    {"name": "similarity",  # end_time
     "label": "Similarity", 
     "field": "similarity", 
     "align": "mid", 
     "required": True,
     "sortable": True},
    {"name": "full_title",  # full_title
     "label": "Full Title", 
     "field": "full_title",
     "align": "left",
     "required": True,
     "sortable": True},
    {"name": "short_name",  # short_name
     "label": "Short Name", 
     "field": "short_name",
     "align": "center", 
     "required": True,
     "sortable": True},
    {"name": "ordinal",  # ordinal
     "label": "Ordinal", 
     "field": "ordinal", 
     "align": "center", 
     "required": True,
     "sortable": True},
    {"name": "part_of_series",  # part_of_series
     "label": "Part of the Series", 
     "field": "part_of_series", 
     "align": "center", 
     "required": True,
     "sortable": True},
    {"name": "country_name",  # country_name
     "label": "Country", 
     "field": "country_name", 
     "align": "center", 
     "required": True,
     "sortable": True},
    {"name": "country_identifier",  # country_identifier
     "label": "Country ID", 
     "field": "country_identifier", 
     "align": "center", 
     "required": True,
     "sortable": True},
    {"name": "city_name",  # city_name
     "label": "City", 
     "field": "city_name", 
     "align": "center", 
     "required": True,
     "sortable": True},
    {"name": "year",  # year
     "label": "Year", 
     "field": "year", 
     "align": "center", 
     "required": True,
     "sortable": True},
    {"name": "start_time",  # start_time
     "label": "Start Date", 
     "field": "start_time", 
     "align": "center", 
     "required": True,
     "sortable": True},
    {"name": "end_time",  # end_time
     "label": "End Time", 
     "field": "end_time", 
     "align": "center", 
     "required": True,
     "sortable": True}     
]

final_columns = [
    {'name': 'feature', 
     'label': 'Feature', 
     'field': 'feature', 
     'align': 'left', 
     'required': True},
     {'name': 'proc_event', 
      'label': 'Proceedings Event', 
      'field': 'proc_event', 
      'align': 'center', 
      'required': True},
      {'name': 'your_choice', 
      'label': 'Your choice', 
      'field': 'your_choice', 
      'align': 'center', 
      'required': True}
]

example_row_proceeding = [
    {'full_title': 'International Conference Telecommunications', 
     'short_name': 'ICT 2012', 
     'ordinal': '19th', 
     'part_of_series': None, 
     'country_name': 'Lebanon', 
     'country_identifier': 'LB', 
     'city_name': 'Jounieh', 
     'year': 2012, 
     'start_time': '2012-04-23', 
     'end_time': '2012-04-25'}
]
example_rows_wikidata = [
    {'similarity': 2.27,
     'full_title': 'International Conference on Telecommunications', 
     'short_name': 'ICT 2012', 
     'ordinal': '19th', 
     'part_of_series': 'International Conference on Telecommunications', 
     'country_name': 'Lebanon', 
     'country_identifier': 'LB', 
     'city_name': 'Jounieh', 
     'year': '2012', 
     'start_time': '2012-04-23',
     'end_time': '2012-04-25'},
     {'similarity': 8.25,
      'full_title': 'IEEE Virtual Reality Conference', 
      'short_name': 'VR 2011', 
      'ordinal': 'null', 
      'part_of_series': 'Virtual Reality and 3D User Interfaces', 
      'country_name': 'Singapore', 
      'country_identifier': 'SG', 
      'city_name': 'Singapore', 
      'year': '2011', 
      'start_time': '2011-03-19', 
      'end_time': '2011-03-23'}
]

def get_your_choice(sel_item: Union[None, int]) -> list:
    new_rows = []
    if sel_item != None:
        for item in hit_table.rows[sel_item].items():
            new_rows.append({"feature": item[0], 
                            "proc_event": table.rows[0][item[0]], 
                            "your_choice": item[1]})
    elif sel_item == None:
        for item in table.rows[0].items():
            new_rows.append({"feature": item[0],
                             "proc_event": item[1],
                             "your_choice": "-"})
    return new_rows

@ui.refreshable
def choice_table(selected_item: Union[None, int]) -> None:
    my_rows = get_your_choice(sel_item = selected_item)
    ui.table(columns=final_columns, rows=my_rows)

ui.markdown("# For this case, supervision is needed.")

ui.html("<b>Proceedings Event:</b>")
table = ui.table(columns=table_columns[1:], rows=example_row_proceeding)
    
ui.html("<b>Wikidata Events that were the best hits:</b>")
hit_table = ui.table(columns=table_columns, rows=example_rows_wikidata, row_key="full_title")

ui.markdown("## Your choice in comparison to the Proceedings Event:")

with ui.row():
    choice_table(selected_item=None)
    hit_table.on(type="rowClick", handler=lambda event: choice_table.refresh(selected_item=event.args[2]))

    with ui.card():
        ui.button(text="This is the \n correct hit!", color="green", on_click=lambda: ui.notify("Good hit."))
        ui.button(text=f"There is \n no good hit!", color="red", on_click=lambda: ui.notify("Alright."))

ui.run()