from APICORE import APICORE
import json


#Calls the corresponding APIs (currently only core) depending on the used method
#initializes them by forcing instantiating this class
#returns the output as a json
class API:
    
   
    def __init__(self):
        APICORE.init()

    def APICORE_paper(self,name):
       response = APICORE.query_api("search/works","title = \""+name+"\"")
       return json.dumps(response,indent = 2)



    def APICORE_conference(self,conference):
        response = APICORE.query_api("search/works","title = \""+conference+"\"")
        return json.dumps(response,indent = 2)
    
    
    def APICORE_query(self,query):
        response = APICORE.query_api(query)
        return json.dumps(response,indent = 2)
    

