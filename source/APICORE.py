import pandas
import json
import requests

#static CORE DB API class
#build similarly to the documentation examples
class APICORE(object):
    
     #static class parameters (API Key from apikey.txt and endpoints is the V3 CORE API)
     api_key = os.environ['CORE_API_KEY']
     api_endpoint = ""
     #initialize API_Key to access DB
     @classmethod
     def init(cls):
            cls.api_endpoint = "https://api.core.ac.uk/v3/"
     
     @classmethod
     def get_entity(cls,url_fragment):
      headers={"Authorization":"Bearer "+cls.api_key}
      response = requests.get(cls.api_endpoint + url_fragment, headers=headers)
      if response.status_code == 200:
           return response.json(), response.elapsed.total_seconds()
      else:
           print(f"Error code {response.status_code}, {response.content}")
          
     #send a html query to the API endpoint
     #intput is only the query according to the documentation of the CORE DB API
     @classmethod
     def query_api(cls,url_fragment, query,limit=100):
       headers={"Authorization":"Bearer "+cls.api_key}
       query = {"q":query, "limit":limit}
       response = requests.post(f"{cls.api_endpoint}{url_fragment}",data = json.dumps(query), headers=headers)
       if response.status_code ==200:
          return response.json(), response.elapsed.total_seconds()
       else:
          print(f"Error code {response.status_code}, {response.content}")

