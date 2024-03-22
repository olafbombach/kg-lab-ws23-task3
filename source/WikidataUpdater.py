from math import e
from os import system
from quopri import encodestring
from xml.dom.minidom import Entity
from xml.sax.handler import property_dom_node
from source.Tokenizer import *
from source.EventClass import ProceedingsEvent
from wikibaseintegrator import WikibaseIntegrator
from wikibaseintegrator.wbi_config import config as wbi_config
from wikibaseintegrator.datatypes import *
from wikibaseintegrator.wbi_enums import ActionIfExists
from wikibaseintegrator.wbi_login import Clientlogin
from wikibaseintegrator.models import Qualifiers
from source.UpdateSources import WikidataQuery
from typing import Optional
from pathlib import Path
from source.Tokenizer import TokenSet
import os,json
import re


class WikidataUpdater:

    #Adds the entries stored in the result/found_entries and result/unfound_entries folders onto WIkidata, by edit and upload respectively
    def __init__(self, found:bool):
        if(found):
            path = os.path.join("results","found_entries","upload.json")
        else:
            path = os.path.join("results","unfound_entries","upload.json")
        with open(path,"r") as json_file:
            data = json.load(json_file)
            keys = list(data.keys())
            print(data[keys[0]]["full_title"])
        for (key,value) in data.items():
            #So that init does not fail, the value of this dict has no meaning
            dicti = {"Conference Title" : "Dummy"}
            event = ProceedingsEvent(dicti,TokenSet(),value["full_title"],value["short_name"],value["ordinal"],value["part_of_series"],value["country_name"],value["country_short"],value["city_name"],value["year"],value["start_time"],value["end_time"])
            countryID = value["countryID"]
            cityID = value["cityID"]
            if(found):
                WDid = value["QID"]
                print(WikidataUpdater.editOnWikidata(event,WDid,countryID,cityID))
            else:
                print(WikidataUpdater.uploadToWikidata(event,countryID,cityID))

    @staticmethod
    def uploadToWikidata(event: ProceedingsEvent, countryID = None, cityID = None):
        """
        Static Method. Logs into the account given in the login() Method and performs an edit operation on a Wikidata object.
        The login only persists in this method
        Parameters: 
        event: The information on the proceeding found in proceedings.com encoded as ProceedingsEvent object
        Output:
        A WikibaseIntegrator Entity (base-entity class) describing the created object
        """
        login = WikidataUpdater.login()
        wbi = WikibaseIntegrator(login = login)
        entity = wbi.item.new()
        #fill out claims and label
        label = event.full_title
        if(not event.ordinal == None):
            label = str(event.ordinal)+" "+label
        if(not event.year == None):
            label += " "+str(event.year)
            if(not event.city_name == None):
                label += ", "+event.city_name
        label = re.sub(r'\s{2,}', ' ', label)
        label = label.rstrip()
        entity.labels.set('en', label,action_if_exists=ActionIfExists.KEEP)
        #add year (P571 = inception)
        if(not event.year == None):
            entity.claims.add(Time(str(event.year)+"-01-01T00:00:00Z",precision=9,prop_nr = "P571"))
        #add country (P495 = Country of origin)
        if(not event.country_name == None):
               if countryID == None:   
                    WDid = WikidataQuery.getWDIdfromLabel(event.country_name)
               else:
                    WDid = countryID
               if(not WDid == None):
                   qualifiers = Qualifiers() 
                   if(not event.country_short == None):
                       #add Short name for country (Short name = P1813)
                       qualifiers.add(MonolingualText(str(event.country_short),prop_nr = "P1813"))
                   entity.claims.add(Item(WDid,prop_nr = "P495", qualifiers = qualifiers))
        #add City (P276 = location)
        if(not event.city_name == None):
            if cityID == None:
               WDid = WikidataQuery.getWDIdfromLabel(event.city_name)
            else:
                WDid = cityID
            if(not WDid == None):
                entity.claims.add(Item(WDid,prop_nr = "P495"))
                
        #add short name (Short name = P1813)
        if(not event.short_name == None):
            entity.claims.add(MonolingualText(str(event.short_name), prop_nr = "P1813"))
            
        #add event series (P179 = part of the series)
        if(not event.part_of_series == None):
            qualifiers = Qualifiers()
            if(not event.ordinal == None):
                #Add ordinal (series ordinal = P1545)
                qualifiers.add(String(str(event.ordinal), prop_nr = "P1545"))
            WDid = WikidataQuery.getWDIdfromLabel(event.part_of_series)
            if WDid == None:
                WDid = WikidataUpdater.create_Series(login,event.part_of_series)
            entity.claims.add(Item(WDid,prop_nr = "P179", qualifiers = qualifiers))
          
                
        #Basic information independant of entry
        #origin (proceedings.com currently still missing in WD)
        #reference = References()
        #proceedingscom = Reference()
        
        #Instance of academic conference and proceeding
        entity.claims.add([Item("Q1143604",prop_nr = "P31"),Item("Q2020153",prop_nr = "P31")])

        
        entity.write()
        
        return entity


    @staticmethod
    def editOnWikidata(event: ProceedingsEvent, WDid: string, countryID = None, cityID = None):
        """
        Static Method. Logs into the account given in the login() Method and performs an edit operation on a Wikidata object.
        The login only persists in this method. Only adds claims for which a claim for that property did not exist yet.
        Parameters: 
        event: The information on the proceeding found in proceedings.com encoded as ProceedingsEvent object
        WBid: The Wikidata identifier of the existing object to modify
        Output:
        A WikibaseIntegrator Entity (base-entity class) describing the edited object after the edit
        """
        login = WikidataUpdater.login()
        wbi = WikibaseIntegrator(login = login)
        entity = wbi.item.get(WDid)
        #fill out claims and label
        label = event.full_title
        if(not event.ordinal == None):
            label = str(event.ordinal)+" "+label
        if(not event.year == None):
            label += " "+str(event.year)
            if(not event.city_name == None):
                label += ", "+event.city_name
        label = re.sub(r'\s{2,}', ' ', label)
        label = label.rstrip()
        entity.labels.set('en', label,action_if_exists=ActionIfExists.KEEP)
        #add year (P571 = inception)
        if(not event.year == None and entity.claims.get("P571") == []):
            entity.claims.add(Time(str(event.year)+"-01-01T00:00:00Z",precision=9,prop_nr = "P571"))
        #add country (P495 = Country of origin)
        if(not event.country_name == None and entity.claims.get("P495") == []):
               if countryID == None:   
                    WDid = WikidataQuery.getWDIdfromLabel(event.country_name)
               else:
                    WDid = countryID
               if(not WDid == None):
                   qualifiers = Qualifiers() 
                   if(not event.country_short == None):
                       #add Short name for country (Short name = P1813)
                       qualifiers.add(MonolingualText(str(event.country_short),prop_nr = "P1813"))
                   entity.claims.add(Item(WDid,prop_nr = "P495", qualifiers = qualifiers))
        #add City (P276 = location)
        if(not event.city_name == None and entity.claims.get("P276") == []):
            if cityID == None:
               WDid = WikidataQuery.getWDIdfromLabel(event.city_name)
            else:
                WDid = cityID
            if(not WDid == None):
                entity.claims.add(Item(WDid,prop_nr = "P276"))
        
        #add event series (P179 = part of the series)
        if(not event.part_of_series == None and entity.claims.get("P179") == []):
            qualifiers = Qualifiers()
            if(not event.ordinal == None):
                #Add ordinal (series ordinal = P1545)
                qualifiers.add(String(str(event.ordinal), prop_nr = "P1545"))
            WDid = WikidataQuery.getWDIdfromLabel(event.part_of_series)
            if WDid == None:
                WDid = WikidataUpdater.create_Series(login,event.part_of_series)
            entity.claims.add(Item(WDid,prop_nr = "P179", qualifiers = qualifiers))
            
        #add short name (Short name = P1813)
        if(not event.short_name == None and entity.claims.get("P1813") == []):
            entity.claims.add(MonolingualText(str(event.short_name), prop_nr = "P1813"))
                
        #Basic information independant of entry
        #origin (proceedings.com currently still missing in WD)
        #reference = References()
        #proceedingscom = Reference()
        
        #Proceeding (P31 = instance of, Q1143604 = proceedings)
        #entity.claims.add(Item("Q1143604",prop_nr = "P31"))#,reference = reference))
        
        #Instance of academic conference and proceeding
        entity.claims.add([Item("Q1143604",prop_nr = "P31"),Item("Q2020153",prop_nr = "P31")])
        
        entity.write()
        
        return entity

    
        
    @staticmethod
    def login():
        """
        Static method that uses the credentials stored either locally in "home/.WDCredentials.json" as json or as environment 
        variables. 
        Returns a login object.
        """
        credentialsPath = Path.home()
        credentialsPath = credentialsPath.joinpath(".WDCredentials.json")
        wdName = os.getenv("WIKIDATA_LOGIN_NAME")
        wdPassword = os.getenv("WIKIDATA_LOGIN_PASSWORD")
        if os.path.exists(credentialsPath) and (wdName == None or wdPassword == None):
           with open(credentialsPath, "r") as json_file:
                data = json.load(json_file)
                wdName = data["user"]
                wdPassword = data["password"]
        wbi_config['USER_AGENT'] = 'MyWikibaseBot/1.0 (https://www.wikidata.org/wiki/https://github.com/olafbombach/kg-lab-ws23-task3/actions/runs/8364288152/job/22899251617)'
        login = Clientlogin(wdName, wdPassword)
        return login
    
    @staticmethod
    def create_Series(login, label):
        """
        Static Method that creates an entry for a proceedings series (label only)
        It is called if such an object does not exist in uploadToWikidata and editOnWikidata
        Returns the Wikidata ID of the created object
        """
        wbi = WikibaseIntegrator(login = login)
        entity = wbi.item.new()
        entity.labels.set('en', label)
        entity.claims.add(Item("Q27785883",prop_nr = "P31"))
        entity.write()
        print("Entity ID"+str(entity.id))
        return entity.id









