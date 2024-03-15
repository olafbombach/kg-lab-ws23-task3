from source.WikidataUpdater import WikidataUpdater
from source.EventClass import ProceedingsEvent
from source.Tokenizer import TokenSet


#Sanity check
def test_base():
    w = WikidataUpdater()
    

#Test editing an entry
@pytest.mark.skip(reason="No valid event yet")
def test_WDedit():
    event = ProceedingsEvent({},TokenSet(),"AACE INTERNATIONAL. ANNUAL MEETING. 59TH 2015",None,None,None,"United States of America",None,city_name="San Antonio",year=2015)
    print(WikidataUpdater.uploadToWikidata(event))
    

    
