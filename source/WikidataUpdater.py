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
import os,json


class WikidataUpdater:


    @staticmethod
    def uploadToWikidata(event: ProceedingsEvent):
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
        entity.labels.set('en', event.full_title,action_if_exists=ActionIfExists.KEEP)
        #add year (P571 = inception)
        if(not event.year == None):
            entity.claims.add(Time(str(event.year)+"-01-01T00:00:00Z",precision=9,prop_nr = "P571"))
        #add country (P495 = Country of origin)
        if(not event.country_name == None):
               WDid = WikidataQuery.getWDIdfromLabel(event.country_name)
               if(not WDid == None):
                   qualifiers = Qualifiers() 
                   if(not event.country_identifier == None):
                       #add Short name for country (Short name = P1813)
                       qualifiers.add(MonolingualText(str(event.country_identifier),prop_nr = "P1813"))
                   entity.claims.add(Item(WDid,prop_nr = "P495", qualifiers = qualifiers))
        #add City (P276 = location)
        if(not event.city_name == None):
            WDid = WikidataQuery.getWDIdfromLabel(event.country_name)
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
                WDid = WikidataUpdater.create_Series(event.part_of_series)
            entity.claims.add(Item(WDid,prop_nr = "P179", qualifiers = qualifiers))
          
                
        #Basic information independant of entry
        #origin (proceedings.com currently still missing in WD)
        #reference = References()
        #proceedingscom = Reference()
        
        #Proceeding (P31 = instance of, Q1143604 = proceedings)
        entity.claims.add(Item("Q1143604",prop_nr = "P31"))#,reference = reference))
        
        entity.write()
        
        return entity


    @staticmethod
    def editOnWikidata(event: ProceedingsEvent, WDid: string):
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
        entity.labels.set('en', event.full_title,action_if_exists=ActionIfExists.KEEP)
        #add year (P571 = inception)
        if(not event.year == None and entity.claims.get("P571") == []):
            entity.claims.add(Time(str(event.year)+"-01-01T00:00:00Z",precision=9,prop_nr = "P571"))
        #add country (P495 = Country of origin)
        if(not event.country_name == None and entity.claims.get("P495") == []):
               WDid = WikidataQuery.getWDIdfromLabel(event.country_name)
               if(not WDid == None):
                   qualifiers = Qualifiers() 
                   if(not event.country_identifier == None):
                       #add Short name for country (Short name = P1813)
                       qualifiers.add(MonolingualText(str(event.country_identifier),prop_nr = "P1813"))
                   entity.claims.add(Item(WDid,prop_nr = "P495", qualifiers = qualifiers))
        #add City (P276 = location)
        if(not event.city_name == None and entity.claims.get("P276") == []):
            WDid = WikidataQuery.getWDIdfromLabel(event.city_name)
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
                WDid = WikidataUpdater.create_Series(event.part_of_series)
            entity.claims.add(Item(WDid,prop_nr = "P179", qualifiers = qualifiers))
            
        #add short name (Short name = P1813)
        if(not event.short_name == None and entity.claims.get("P1813") == []):
            entity.claims.add(MonolingualText(str(event.short_name), prop_nr = "P1813"))
                
        #Basic information independant of entry
        #origin (proceedings.com currently still missing in WD)
        #reference = References()
        #proceedingscom = Reference()
        
        #Proceeding (P31 = instance of, Q1143604 = proceedings)
        entity.claims.add(Item("Q1143604",prop_nr = "P31"))#,reference = reference))
        
        entity.write()
        
        return entity

    
        
    @staticmethod
    def login():
        credentialsPath = Path.home()
        credentialsPath = credentialsPath.joinpath(".WDCredentials.json")
        wdName = os.getenv("WIKIDATA_LOGIN_NAME")
        wdPassword = os.getenv("WIKIDATA_LOGIN_PASSWORD")
        json_file = Path.home() / ".WDCredentials.json"
        if os.path.exists(credentialsPath) and (wdName == None or wdPassword == None):
           with open(credentialsPath, "r") as json_file:
                data = json.load(json_file)
                wdName = data["user"]
                wdPassword = data["password"]
        wbi_config['USER_AGENT'] = 'MyWikibaseBot/1.0 (https://www.wikidata.org/wiki/"+wdname")'
        print('MyWikibaseBot/1.0 (https://www.wikidata.org/wiki/"+wdname")')
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
        entity.write()
        print("Entity ID"+str(entity.id))
        return entity.id









