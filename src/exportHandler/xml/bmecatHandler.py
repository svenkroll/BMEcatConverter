'''
Created on 12.05.2017

@author: henrik.pilz
'''
from datetime import datetime
import getpass
import logging

from lxml import etree
from lxml.etree import Element, SubElement


class BMEcatHandler(object):
    
    def __init__(self, articles, filename):
        self._articles = articles # dict!
        self._filename = filename
    
    def __createArticleElements(self):
        articleElements = []
        for articleType, articles in self._articles.items():
            articleElements.extend(self.__createArticleElementsForSet(articles, articleType))
        return articleElements

    def __createArticleElementsForSet(self, articles, articleType='new'):
        articleElements = []
        for article in articles:
            articleElement = article.toXml(articleType)
            articleElements.append(articleElement)
        return articleElements
    
    def writeBMEcatAsXML(self):
        with open(self._filename, "wb") as file:
            bmecat = self.__createBMEcatRootElement()
            bmecat.append(self.__createHeaderElement())
            
            newCatalog = Element("T_NEW_CATALOG")
            newCatalog.append(self.__createCatalogGroupSystemElement())
            bmecat.append(newCatalog)    
            newCatalog.extend(self.__createArticleElements())
            newCatalog.extend(self.__createArticleCatalogMapping())
            file.write(self.__prettyFormattedOutput(bmecat))
            file.close()
        
    def __createBMEcatRootElement(self):
        return etree.XML('<!DOCTYPE BMECAT SYSTEM "bmecat_new_catalog.dtd">' +
                        '<BMECAT version="1.2" xml:lang="de" xmlns="http://www.bmecat.org/bmecat/1.2/bmecat_new_catalog" />')

    def __createCatalogGroupSystemElement(self):
        return etree.XML("<CATALOG_GROUP_SYSTEM>" +
                            "<GROUP_SYSTEM_ID>1</GROUP_SYSTEM_ID>" +
                            "<GROUP_SYSTEM_NAME>Default Groupsystem Contorion</GROUP_SYSTEM_NAME>" +
                            '<CATALOG_STRUCTURE type="root">' +
                            "<GROUP_ID>1</GROUP_ID>" +
                            "<GROUP_NAME>Katalog</GROUP_NAME>" +
                            "<PARENT_ID>0</PARENT_ID>" +
                            "<GROUP_ORDER>1</GROUP_ORDER>" +
                            "</CATALOG_STRUCTURE>" +
                            '<CATALOG_STRUCTURE type="leaf">' +
                            "<GROUP_ID>2</GROUP_ID>" +
                            "<GROUP_NAME>Produkte</GROUP_NAME>" +
                            "<PARENT_ID>1</PARENT_ID>" +
                            "<GROUP_ORDER>2</GROUP_ORDER>" +
                            "</CATALOG_STRUCTURE>" +
                            "</CATALOG_GROUP_SYSTEM>")


    def __determineInitials(self):
        userName = getpass.getuser()
        initials = "BC_TEMP"
        logging.debug("Username: {0}".format(userName))
        if userName is not None:
            usplit = []
            if len(userName.split(" ")) > 1:
                usplit = userName.split(" ")
            if len(userName.split(".")) > 1:
                usplit = userName.split(".")

            if len(usplit) > 1 and len(usplit[0].split("-")) > 1:
                usplit = usplit[0].split("-").append(usplit[1])
            initials = ""
            for elem in usplit:
                if len(elem) > 0:
                    initials += elem[0].upper()
            
        return initials

    def __createHeaderElement(self):
        ''' Create Header of BMEcat
        '''
        initials = self.__determineInitials()
        logging.debug("Initialen: {0}".format(initials))
        now = datetime.now()

        generationDate = now.strftime("%Y-%m-%d")
        dateKz = now.strftime("%Y%m%d")
        generationTIme = now.strftime("%H:%M:%S")
        return etree.XML("<HEADER>" +
                            "<GENERATOR_INFO>BMEcatConverter Contorion</GENERATOR_INFO>" +
                            "<CATALOG>" +
                            "<LANGUAGE>deu</LANGUAGE>" +
                            "<CATALOG_ID>" + dateKz + "_" + initials +"</CATALOG_ID>" +
                            "<CATALOG_VERSION>1.0</CATALOG_VERSION>" +
                            "<CATALOG_NAME>" + dateKz + "-Fiege-Update_" + initials +"</CATALOG_NAME>" +
                            '<DATETIME type="generation_date">' +
                            "<DATE>" + generationDate + "</DATE>" +
                            "<TIME>"+ generationTIme + "</TIME>" +
                            "</DATETIME>" +
                            "<CURRENCY>EUR</CURRENCY>" +
                            "</CATALOG>" +
                            "<BUYER>" +
                            "<BUYER_NAME>Contorion GmbH</BUYER_NAME>" +
                            "</BUYER>" +
                            "<SUPPLIER>" +
                            "<SUPPLIER_NAME>Contorion GmbH</SUPPLIER_NAME>" +
                            "</SUPPLIER>" +
                            "</HEADER>")

    def __prettyFormattedOutput(self, elem):
        """Return a pretty-printed XML string for the Element.
        """
        return etree.tostring(elem, encoding="UTF-8", pretty_print=True, xml_declaration=True)
    
    def __createArticleCatalogMapping(self):
        mapping = []
        for articleType, articles in self._articles.items():
            for article in articles:
                parent = Element("ARTICLE_TO_CATALOGGROUP_MAP")
                SubElement(parent,"ART_ID").text = article.productId
                SubElement(parent,"CATALOG_GROUP_ID").text = "2"
                SubElement(parent,"ARTICLE_TO_CATALOGGROUP_MAP_ORDER").text = "2"
                mapping.append(parent)
        return mapping