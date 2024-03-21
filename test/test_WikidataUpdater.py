from ast import Dict
from source.WikidataUpdater import WikidataUpdater
from source.EventClass import ProceedingsEvent
from source.Tokenizer import TokenSet
from source.UpdateSources import WikidataQuery
import pytest


#Sanity check
#With the new init method, it adds all results onto Wikidata (result folder)
#Disabled until addition of the required folders
def test_base():
    #w = WikidataUpdater(True)
    i = 1
    

#Test query
def test_query():
    print(WikidataQuery.getWDIdfromLabel("USA"))

#Test editing an entry (disabled due to concurrent tests -> Race conditions)
#def test_WDedit():
    #dicti = {"Conference Title":"LIQUID CRYSTALS XXI","Mtg Year":"2017.0","POD Publisher":"Curran Associates, Inc."}
    #event = ProceedingsEvent(dicti,TokenSet(),"AACE INTERNATIONAL. ANNUAL MEETING. 59TH 2015",None,None,None,"United States of America",None,city_name="San Antonio",year=2015)
    #WikidataUpdater.editOnWikidata(event,"Q124901747")
    

    
