from source.UpdateSources import WikidataQuery

#With the new init method, it adds all results onto Wikidata (result folder)
#Disabled until addition of the required folders
def test_base():
    """
    Sanity check.
    """
    #w = WikidataUpdater(True)
    i = 1

def test_query():
    """
    Test the query
    """
    print(WikidataQuery.getWDIdfromLabel("USA"))

#Test editing an entry (disabled due to concurrent tests -> Race conditions)
#def test_WDedit():
    #dicti = {"Conference Title":"LIQUID CRYSTALS XXI","Mtg Year":"2017.0","POD Publisher":"Curran Associates, Inc."}
    #event = ProceedingsEvent(dicti,TokenSet(),"AACE INTERNATIONAL. ANNUAL MEETING. 59TH 2015",None,None,None,"United States of America",None,city_name="San Antonio",year=2015)
    #WikidataUpdater.editOnWikidata(event,"Q124901747")
    

    
