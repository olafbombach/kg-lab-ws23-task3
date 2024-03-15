from math import e
from os import system
from quopri import encodestring
from xml.dom.minidom import Entity
from source.Tokenizer import *
from source.EventClass import ProceedingsEvent
from wikibaseintegrator import WikibaseIntegrator
from wikibaseintegrator.wbi_config import config as wbi_config
from wikibaseintegrator.datatypes import *
from wikibaseintegrator.wbi_enums import ActionIfExists
from wikibaseintegrator.wbi_login import Clientlogin
from source.UpdateSources import WikidataQuery
from typing import Optional


class WikidataUpdater:


    @staticmethod
    def uploadToWikidata(event: ProceedingsEvent):
        """
        Logs into the account given in the login() Method and performs an edit operation on a Wikidata object.
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
                   entity.claims.add(Item(WDid,prop_nr = "P495"))
        #add City (P276 = location)
        if(not event.city_name == None):
            WDid = WikidataQuery.getWDIdfromLabel(event.country_name)
            if(not WDid == None):
                entity.claims.add(Item(WDid,prop_nr = "P495"))
        
        #add event series (P179 = part of the series)
        if(not event.part_of_series == None):
            WDid = WikidataQuery.getWDIdfromLabel(event.part_of_series)
            if(not WDid == None):
                entity.claims.add(Item(WDid,prop_nr = "P179"))
                
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
        Logs into the account given in the login() Method and performs an edit operation on a Wikidata object.
        The login only persists in this method
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
        if(not event.year == None):
            entity.claims.add(Time(str(event.year)+"-01-01T00:00:00Z",precision=9,prop_nr = "P571"))
        #add country (P495 = Country of origin)
        if(not event.country_name == None):
               WDid = WikidataQuery.getWDIdfromLabel(event.country_name)
               if(not WDid == None):
                   entity.claims.add(Item(WDid,prop_nr = "P495"))
        #add City (P276 = location)
        if(not event.city_name == None):
            WDid = WikidataQuery.getWDIdfromLabel(event.country_name)
            if(not WDid == None):
                entity.claims.add(Item(WDid,prop_nr = "P495"))
        
        #add event series (P179 = part of the series)
        if(not event.part_of_series == None):
            WDid = WikidataQuery.getWDIdfromLabel(event.part_of_series)
            if(not WDid == None):
                entity.claims.add(Item(WDid,prop_nr = "P179"))
                
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
        """
        Method that returns a login object using the encoded credentials (stored in github secrets for this repository)
        Sets the user agent in wikidata to the username
        Returns a wbi_login Object to be used for write actions with a WikibaseIntegrator instance
        """
        wbi_config['USER_AGENT'] = 'MyWikibaseBot/1.0 (https://www.wikidata.org/wiki/User:Christophe Haag)'
        #Remember to change the credentials after testing
        login = Clientlogin("user a", "some secret")
        return login









