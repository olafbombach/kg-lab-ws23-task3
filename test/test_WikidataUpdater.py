from ast import Dict
from source.WikidataUpdater import WikidataUpdater
from source.EventClass import ProceedingsEvent
from source.Tokenizer import TokenSet


#Sanity check
def test_base():
    w = WikidataUpdater()
    

#Test editing an entry
def test_WDedit():
    dicti = {"Conference Title":"LIQUID CRYSTALS XXI","Mtg Year":"2017.0","POD Publisher":"Curran Associates, Inc."}
    event = ProceedingsEvent(dicti,TokenSet(),"AACE INTERNATIONAL. ANNUAL MEETING. 59TH 2015",None,None,None,"United States of America",None,city_name="San Antonio",year=2015)
    print(WikidataUpdater.uploadToWikidata(event))
    

    
