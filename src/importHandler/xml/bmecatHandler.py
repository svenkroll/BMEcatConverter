'''
Created on 05.05.2017

@author: henrik.pilz
'''
import logging

from xml.sax import handler
from datetime import datetime

from data.product import Product
from data.productDetails import ProductDetails
from data.price import Price
from data.priceDetails import PriceDetails
from data.orderDetails import OrderDetails
from data.feature import Feature
from data.featureSet import FeatureSet
from data.mime import Mime
from data.treatmentClass import TreatmentClass
from data.reference import Reference
from data.variantSet import VariantSet
from data.variant import Variant

from mapping.units import BMEcatUnitMapper
from mapping.units import ETIMUnitMapper
from mapping.blacklist import FeatureBlacklist
from mapping.blacklist import FeatureSetBlacklist


class BMEcatHandler(handler.ContentHandler):
    
    ''' alle registrierten StartElementhandler '''
    _startElementHandler = {
                "article" : "createProduct",
                "article_details" : "createProductDetails", 
                "order_details" : "createOrderDetails",
                "price_details" : "createPriceDetails",
                "price" : "createPrice",                
                "mime" : "createMime",
                "mime_info" : "startMimeInfo",
                "datetime" : "startDateTime",
                "article_features" :"createFeatureSet",
                "feature" : "createFeature",
                "special_treatment_class" : "createTreatmentClass",
                "article_reference" : "createReference",
                "variants" : "createFeatureVariantSet",
                "variant" : "createFeatureVariant",
                "description_long" : "startDescription"
                }

    ''' Mögliche Aliase für Varianten der BMEcats '''
    _alias = {
                "product" : "article",
                "product_details" : "article_details",
                "supplier_pid" : "supplier_aid",
                "supplier_alt_pid" : "supplier_alt_aid",
                "manufacturer_pid" : "manufacturer_aid",
                "buyer_pid" : "buyer_aid",
                "article_order_details" : "order_details",
                "article_price_details" : "price_details",
                "article_price" : "price",
                "product_features" : "article_features",
                "international_pid" : "ean",
                "product_order_details" : "order_details",
                "product_price_details" : "price_details",
                "product_price" : "price",
                "product_reference" : "article_reference",
                "prod_id_to" : "art_id_to",
                "supplier_pid_supplement" : "supplier_aid_supplement"
            }
            
    ''' alle registrierten EndElementhandler '''
    _endElementHandler = {
                "article_features" :"saveFeatureSet",
                "feature" : "saveFeature",
                "article" : "saveProduct",
                "mime_info" : "endMimeInfo",
                "datetime" : "endDateTime",
                "mime" : "saveMime",
                "supplier_aid" : "addArticleId",
                "supplier_alt_aid" : "addAlternativeArticleId",
                "buyer_aid" : "addAlternativeArticleId",
                "manufacturer_aid" : "addManufacturerArticleId",
                "manufacturer_name" : "addManufacturerName",
                "ean" : "addEAN", 
                "description_long" : "saveDescription",
                "description_short" : "addTitle",
                "price" : "savePrice",
                "price_details" : "savePriceDetails",
                "delivery_time" : "addDeliveryTime",
                "price_amount" : "addPriceAmount",
                "tax" : "addPriceTax",
                "price_currency" : "addPriceCurrency",
                "price_factor" : "addPriceFactor",
                "territory" : "addTerritory",
                "lower_bound" : "addPriceLowerBound",
                "mime_source" : "addMimeSource",
                "mime_type" : "addMimeType",
                "mime_descr" : "addMimeDescription",
                "mime_alt" : "addMimeAlt",
                "mime_purpose" : "addMimePurpose",
                "mime_order" : "addMimeOrder",
                "order_unit" : "addOrderUnit",
                "content_unit" : "addContentUnit",
                "no_cu_per_ou " : "addPackagingQuantity",
                "price_quantity " : "addPriceQuantity",
                "quantity_min " : "addQuantityMin",
                "quantity_interval" : "addQuantityInterval",
                "date" : "addDate",
                "fname" : "addFeatureName",
                "fvalue" : "addFeatureValue",
                "fvalue_details" : "addFeatureValueDetails",
                "funit" : "addFeatureUnit",
                "fdesc" : "addFeatureDescription",
                "special_treatment_class" : "saveTreatmentClass",
                "catalog_group_system" : "resetAll",
                "article_reference" : "saveReference",
                "art_id_to" : "addReferenceArticleId",
                "reference_descr" : "addReferenceDescription",
                "variants" : "saveFeatureVariantSet",
                "vorder" : "addFeatureVariantSetOrder",
                "variant" : "addFeatureVariant",
                "supplier_aid_supplement" : "addFeatureVariantProductIdSuffix",
                "reference_feature_system_name" : "addFeatureSetReferenceSystem",
                "reference_feature_group_id" : "addFeatureSetReferenceGroupId"
                }
    
    bmecatUnitMapper = BMEcatUnitMapper()
    etimUnitMapper = ETIMUnitMapper()
    
    featureSetBlacklist = FeatureSetBlacklist()
    featureBlacklist = FeatureBlacklist()
    
    ''' Handlernamen für das XML-Element ermitteln. '''
    def determinteHandlername(self, tag, bOpen):
        name = tag.lower()
        if tag.lower() in self._alias:
            logging.debug("[" + str(bOpen) +"] '" + tag + "' has an alias")
            name = self._alias[tag.lower()]

        handlerName = None
        if bOpen:
            try:
                handlerName = self._startElementHandler[name]
            except KeyError:
                logging.debug("Call for Start Tag <" + name + "> FAILED:")            
        else :
            try:
                handlerName = self._endElementHandler[name]
            except KeyError:
                logging.debug("Call for End Tag <" + name + "> FAILED:")            
        return handlerName

    ''' Konstruktor '''
    def __init__(self, dateFormat, decimalSeparator, thousandSeparator):
        self._dateFormat=dateFormat 
        self._decimalSeparator = decimalSeparator
        self._thousandSeparator = thousandSeparator
        
        if self._decimalSeparator is None or self._thousandSeparator  is None:
            raise Exception("Dezimaltrennzeichen und Tausendertrennzeichen müssen angegeben werden.")
        if self._decimalSeparator==self._thousandSeparator:
            raise Exception("Dezimaltrennzeichen und Tausendertrennzeichen dürfen nicht gleich sein.")
        
        '''articles by SKU and Product Structure as Value'''
        self._articles = { "new" : [], "update" : [], "delete" : [], "failed" : [] }
        self._currentArticle = None
        self._currentPrice = None
        self._currentMime = None
        self._currentPriceDetails = None
        self._currentElement = None
        self._currentContent = ""
        self._dateType = None
        self._currentFeatureSet = None
        self._currentFeature = None
        self._currentTreatmentClass = None
        self._currentReference = None
        self._currentVariant = None
        self.lineFeedToHTML = False
        self._currentArticleMode = "failed"
  
    ''' Starte aktuelles XML Element '''
    def startElement(self, name, attrs):
        self.workOnElement(name, attrs, True)

    ''' Schließe aktuelles XML Element '''
    def endElement(self, name):
        self.workOnElement(name, None, False)
    
    ''' Handler ermitteln, der die Arbeit macht. '''
    def workOnElement(self, name, attrs, bOpen):
        logging.debug("Call for Tag <" + name + ">")
        elementHandler = None
        try:
            handlerName = self.determinteHandlername(name, bOpen)
            if not handlerName is None:
                elementHandler = getattr(self, handlerName)
                elementHandler(attrs)
            self._currentContent = ""
        except AttributeError:
            raise NotImplementedError("Class [" + self.__class__.__name__ + "] does not implement [" + handlerName + "]")

    ''' ---------------------------------------------------------------------'''
    def resetAll(self, attrs = None):
        self._currentArticle = None
        self._currentPrice = None
        self._currentMime = None
        self._currentPriceDetails = None
        self._currentElement = None
        self._currentContent = ""
        self._dateType = None
        self._currentFeatureSet = None
        self._currentFeature = None
        self._currentTreatmentClass = None

    ''' ---------------------------------------------------------------------'''
    def startMimeInfo(self, attrs = None):
        self._currentElement = self._currentArticle
        
    def endMimeInfo(self, attrs = None):
        self._currentMime = None
        self._currentElement = None
    
    ''' ---------------------------------------------------------------------'''
    ''' Anfang Artikel '''
    def createProduct(self, attrs):
        logging.debug("Anfang Produkt " + ", ".join(attrs.getNames()))
        if not self._currentArticle is None:
            raise Exception("Fehler im BMEcat: Neuer Artikel soll erstellt werden. Es wird schon ein Artikel verarbeitet.")
        else:
            self._currentArticle = Product()
            self._currentContent = ""
            self._currentElement = self._currentArticle
            self._currentArticleMode = 'new'
            if 'mode' in attrs.getNames():
                self._currentArticleMode = attrs.getValue('mode')
            else:
                logging.warning("Fehler im BMEcat: es wurde kein mode für den Artikel angegeben.")

    ''' Artikel speichern '''
    def saveProduct(self, attr=None):
        if self._currentArticle.productId is None:            
            '''self._articles["failed"].append(self._currentArticle)'''
            logging.error("Produkt konnte nicht gespeichert werden. Fehlerhafte Daten: Keine Artikelnummer.")
        else:
            logging.info("Produkt validieren: " + self._currentArticle.productId)
            self.validateCurrentProduct()
            logging.debug("Neues Produkt erstellt. Modus: " + self._currentArticleMode)
            self._articles[self._currentArticleMode].append(self._currentArticle)
        logging.debug("Produktende")
        self.resetAll()

    ''' ---------------------------------------------------------------------'''
    def createProductDetails(self, attrs):
        if self._currentArticle is None:
            raise Exception("Artikeldetails sollen erstellt werden. Aber es ist kein Artikel vorhanden")
        if not self._currentArticle.details is None:
            raise Exception("Fehler im BMEcat: Neue Artikeldetails sollen erstellt werden. Es werden schon Artikeldetails verarbeitet.")
        else:
            self._currentArticle.details = ProductDetails()

    ''' ---------------------------------------------------------------------'''
    def createOrderDetails(self, attrs):
        if self._currentArticle is None:
            raise Exception("Bestelldetails sollen erstellt werden. Aber es ist kein Artikel vorhanden")
        if not self._currentArticle.orderDetails is None:
            raise Exception("Fehler im BMEcat: Neue Bestelldetails sollen erstellt werden. Es werden schon Bestelldetails verarbeitet.")
        else: 
            self._currentArticle.orderDetails = OrderDetails()

    ''' ---------------------------------------------------------------------'''
    def createPriceDetails(self, attrs):
        if not self._currentPriceDetails is None:
            raise Exception("Fehler im BMEcat: Neue Preisdetails sollen erstellt werden. Es werden schon Preisdetails verarbeitet.") 
        else: 
            self._currentPriceDetails = PriceDetails()
            self._currentElement = self._currentPriceDetails

    def savePriceDetails(self, attrs):
        if self._currentArticle is None:
            raise Exception("Preisdetails sollen gespeichert werden. Aber es ist kein Artikel vorhanden")
        self._currentArticle.addPriceDetails(self._currentPriceDetails)
        self._currentPriceDetails = None
        self._currentElement = None

    ''' ---------------------------------------------------------------------'''
    ''' Anfang Bild '''
    def createMime(self, attrs):
        if not self._currentMime is None:
            raise Exception("Fehler im BMEcat: Neues Bild soll erstellt werden. Es wird schon ein Bild verarbeitet.")
        else: 
            self._currentMime = Mime()

    ''' Bild speichern '''
    def saveMime(self, attrs):
        if self._currentElement is None:
            logging.warning("Bild konnte nicht gespeichert werden.")
        else:
            self._currentElement.addMime(self._currentMime)
        self._currentMime = None

    ''' ---------------------------------------------------------------------'''
    ''' Anfang Preis '''
    def createPrice(self, attrs):
        if not self._currentPrice is None:
            raise Exception("Fehler im BMEcat: Neuer Preis soll erstellt werden. Es wird schon ein Preis verarbeitet.")
        else: 
            self._currentPrice = Price()
            self._currentPrice.priceType = attrs.getValue('price_type')
            self._currentElement = self._currentPrice

    ''' Preis speichern '''
    def savePrice(self, attrs):
        if self._currentPriceDetails is None:
            raise Exception("Preis soll gespeichert werden. Aber es sind keine Preisdetails  vorhanden")
        self._currentPriceDetails.prices.append(self._currentPrice)
        self._currentPrice = None
        self._currentElement = self._currentPriceDetails     


    ''' ---------------------------------------------------------------------'''
    ''' Anfang TreatmentClass '''
    def createTreatmentClass(self, attrs):
        if not self._currentTreatmentClass is None:
            raise Exception("Fehler im BMEcat: Neue SpecialTreatmentClass soll erstellt werden. Es wird schon ein SpecialTreatmentClass verarbeitet.")
        else: 
            self._currentTreatmentClass = TreatmentClass()
            self._currentTreatmentClass.classType = attrs.getValue('type')
            self._currentElement = self._currentTreatmentClass

    ''' TreatmentClass speichern '''
    def saveTreatmentClass(self, attrs):
        if self._currentArticle is None:
            raise Exception("SpecialTreatmentClass soll gespeichert werden. Aber es ist kein Artikel vorhanden")
        self._currentTreatmentClass.value = self._currentContent
        self._currentArticle.addSpecialTreatmentClass(self._currentTreatmentClass)
        self._currentTreatmentClass = None
        self._currentElement = None

    ''' ---------------------------------------------------------------------'''
    def createFeatureSet(self, attrs = None):
        if not self._currentFeature is None:
            raise Exception("Fehler im BMEcat: Neues Attributset soll erstellt werden. Es wird schon ein Attributset verarbeitet.")
        else: 
            self._currentFeatureSet = FeatureSet()
            self._currentContent = ""

    def saveFeatureSet(self, attrs = None):
        if self._currentArticle is None:
            raise Exception("Attributset soll gespeichert werden. Aber es ist kein Artikel vorhanden")
        if len(self._currentFeatureSet.features) < 1:
            logging.info("Attributset wird nicht gespeichert, da kein Attribute enthalten sind.")
        elif BMEcatHandler.featureSetBlacklist.contains(self._currentFeatureSet.referenceSytem):
            logging.info("Attributset wird nicht gespeichert, da es auf der Blacklist ist.")
        else:
            self._currentArticle.featureSets.append(self._currentFeatureSet)
        self._currentFeatureSet = None
    
    def addFeatureSetReferenceSystem(self, attrs = None):
        if self._currentFeatureSet is None:
            raise Exception("Referenzsystem soll gesetzt werden. Aber es ist kein Attributset vorhanden")                
        self._currentFeatureSet.referenceSytem = self._currentContent

    def addFeatureSetReferenceGroupId(self, attrs = None):
        if self._currentFeatureSet is None:
            raise Exception("Gruppen ID soll gesetzt werden. Aber es ist kein Attributset vorhanden")                
        self._currentFeatureSet.referenceGroupId = self._currentContent

    ''' ---------------------------------------------------------------------'''
    def createFeature(self, attrs = None):
        if not self._currentFeature is None:
            raise Exception("Fehler im BMEcat: Neues Attribut soll erstellt werden. Es wird schon ein Attribut verarbeitet.")
        else: 
            self._currentFeature = Feature()
            self._currentElement = self._currentFeature
            self._currentContent = ""

    def saveFeature(self, attrs = None):
        if self._currentFeatureSet is None:
            raise Exception("Attribut soll gespeichert werden. Aber es ist kein Attributset vorhanden")
        elif BMEcatHandler.featureBlacklist.contains(self._currentFeature.name):
            logging.info("Attribut wird nicht gespeichert, da es auf der Blacklist ist.")
        else:
            self._currentFeatureSet.features.append(self._currentFeature)

            if self._currentFeature.variants is not None:
                self._currentArticle.variants.append((self._currentFeature.variants.order, self._currentFeature.name, self._currentFeature.variants))

        self._currentFeature = None
        self._currentElement = None

    ''' ---------------------------------------------------------------------'''
    ''' Referenz erstellen'''
    def createReference(self, attrs = None):
        if not self._currentReference is None:
            raise Exception("Fehler im BMEcat: Neue Referenz soll erstellt werden. Es wird schon eine Referenz verarbeitet.")
        if not 'type' in attrs.getNames():
            logging.warning("Referenz auf Artikel konnte nicht verarbeitet werdern, da kein Typ angegeben wurde.")
        else:
            self._currentReference = Reference()
            self._currentElement = self._currentReference
            self._currentReference.referenceType = attrs.getValue('type')
            if 'quantity' in attrs.getNames():
                self._currentReference.quantity = attrs.getValue('quantity')
                
    ''' Referenz speichern'''
    def saveReference(self, attrs = None):
        self._currentArticle.references.append(self._currentReference)
        self._currentReference = None
        self._currentElement = None

    ''' ---------------------------------------------------------------------'''
    ''' Referenz ID speichern'''
    def addReferenceArticleId(self, attrs = None):
        self._currentReference.supplierArticleIds.append(self._currentContent)
        
    ''' Referenz Beschreibung speichern'''
    def addReferenceDescription(self, attrs = None):
        self._currentReference.description = self._currentContent
        
        
    ''' ---------------------------------------------------------------------'''
    ''' Artikelnummer speichern'''
    def addArticleId(self, attrs = None):
        if self._currentArticle is None:
            raise Exception("Artikelnummer soll gespeichert werden. Aber es ist kein Artikel vorhanden")
        logging.debug("Artikelnummer " + self._currentContent)
        self._currentArticle.productId = self._currentContent

    ''' HerstellerArtikelnummer speichern'''
    def addManufacturerArticleId(self, attrs = None):
        if self._currentArticle is None:
            raise Exception("Herstellerartikelnummer soll gespeichert werden. Aber es ist kein Artikel vorhanden")
        self._currentArticle.addManufacturerId(self._currentContent)

    def addManufacturerName(self, attrs = None):
        if self._currentArticle is None:
            raise Exception("Herstellername soll gespeichert werden. Aber es ist kein Artikel vorhanden")
        self._currentArticle.addManufacturerName(self._currentContent)

    def addEAN(self, attrs = None):
        if self._currentArticle is None:
            raise Exception("EAN soll gespeichert werden. Aber es ist kein Artikel vorhanden")
        self._currentArticle.addEAN(self._currentContent)

    def addTitle(self, attrs = None):
        if self._currentArticle is None:
            raise Exception("Artikelname soll gespeichert werden. Aber es ist kein Artikel vorhanden")
        self._currentArticle.addTitle(self._currentContent)

    def startDescription(self, attrs = None):
        self.lineFeedToHTML = True
        
    def saveDescription(self, attrs = None):
        if self._currentArticle is None:
            raise Exception("Artikelbeschreibung soll gespeichert werden. Aber es ist kein Artikel vorhanden")
        self._currentArticle.addDescription(self._currentContent)
        self.lineFeedToHTML = False

    def addAlternativeArticleId(self, attrs = None):
        if self._currentArticle is None:
            raise Exception("Alternative Herstellerartikelnummer soll gespeichert werden. Aber es ist kein Artikel vorhanden")
        if self._currentArticle.productId is None:
            logging.info("Alternative Artikelnummer als Artikelnummer gesetzt!")
            self._currentArticle.productId = self._currentContent
        if self._currentArticle.details is None:
            raise Exception("Alternative Herstellerartikelnummer soll gespeichert werden. Aber es sind keine Artikeldetails vorhanden")
        else:
            logging.debug("Alternative Artikelnummer: " + self._currentContent)
            self._currentArticle.details.supplierAltId = self._currentContent
        
    def addDeliveryTime(self, attrs = None):
        if self._currentArticle is None:
            raise Exception("Lieferzeit soll gespeichert werden. Aber es ist kein Artikel vorhanden")
        self._currentArticle.addDeliveryTime(self._currentContent)

    ''' ---------------------------------------------------------------------'''
    def convertToEnglishDecimalValue(self, stringValue):
        convertedString = stringValue
        if not self._decimalSeparator == ".": 
            convertedString = convertedString.replace(",",";").replace(self._thousandSeparator,"").replace(";",".")
        return float(convertedString)


    ''' ---------------------------------------------------------------------'''
    def addPriceAmount(self, attrs = None):
        self._currentPrice.amount = round(self.convertToEnglishDecimalValue(self._currentContent), 2)

    def addPriceCurrency(self, attrs = None):
        self._currentPrice.currency = self._currentContent

    def addPriceTax(self, attrs = None):
        stringValue = self._currentContent.replace("%", "").strip()
        convertedValue = self.convertToEnglishDecimalValue(stringValue)
        if convertedValue > 1:
            convertedValue = convertedValue / 100
        self._currentPrice.tax = round(convertedValue, 2)

    def addPriceFactor(self, attrs = None):
        self._currentPrice.factor = self.convertToEnglishDecimalValue(self._currentContent)
    
    def addPriceLowerBound(self, attrs = None):
        self._currentPrice.lowerBound = self._currentContent
        
    ''' ---------------------------------------------------------------------'''
    def addTerritory(self, attrs = None):
        if self._currentElement is None:
            logging.warning("Territory kann nicht gespeichert werden.")
        else:
            self._currentElement.territory = self._currentContent

    ''' ---------------------------------------------------------------------'''
    def addMimeSource(self, attrs = None):
        self._currentMime.source = self._currentContent

    def addMimeType(self, attrs = None):
        self._currentMime.mimeType = self._currentContent

    def addMimeAlt(self, attrs = None):
        self._currentMime.altenativeContent = self._currentContent

    def addMimePurpose(self, attrs = None):
        self._currentMime.purpose = self._currentContent

    def addMimeDescription(self, attrs = None):
        self._currentMime.description = self._currentContent

    def addMimeOrder(self, attrs = None):
        self._currentMime.order = self._currentContent
    
    ''' ---------------------------------------------------------------------'''
    def addOrderUnit(self, attrs = None):
        self._currentArticle.orderDetails.orderUnit = self._currentContent
    
    def addContentUnit(self, attrs = None):
        self._currentArticle.orderDetails.contentUnit = self._currentContent

    def addPriceQuantity(self, attrs = None):
        self._currentArticle.orderDetails.priceQuantity = self._currentContent
        
    def addPackagingQuantity(self, attrs = None):
        self._currentArticle.orderDetails.packagingQuantity = self._currentContent

    def addQuantityInterval(self, attrs = None):
        self._currentArticle.orderDetails.quantityInterval = self._currentContent

    def addQuantityMin(self, attrs = None):
        self._currentArticle.orderDetails.quantityMin = self._currentContent
        
    ''' ---------------------------------------------------------------------'''
    def addFeatureValue(self, attrs = None):
        if self._currentFeature.variants is not None and len(self._currentFeature.variants) > 0:
            raise Exception("Fehler im BMEcat: FeatureValue soll hinzugefügt werden, es existieren aber schon FeatureVariants.")        
        self._currentElement.addValue(self._currentContent)

    def addFeatureUnit(self, attrs = None):
        if self._currentFeature.unit is not None:
            raise Exception("Fehler im BMEcat: FeatureUnit soll gesetzt werden existiert aber schon.")
        currentUnit = self._currentContent
        if BMEcatHandler.bmecatUnitMapper.hasKey(currentUnit):
            self._currentFeature.unit = BMEcatHandler.bmecatUnitMapper.getSIUnit(currentUnit)
        elif BMEcatHandler.etimUnitMapper.hasKey(currentUnit):
            self._currentFeature.unit = BMEcatHandler.etimUnitMapper.getSIUnit(currentUnit)
        else:
            self._currentFeature.unit = currentUnit
    def addFeatureName(self, attrs = None):
        if self._currentFeature.name is not None:
            raise Exception("Fehler im BMEcat: FeatureName soll gesetzt werden existiert aber schon.")
        self._currentFeature.name = self._currentContent

    def addFeatureDescription(self, attrs = None):
        if self._currentFeature.description is not None:
            raise Exception("Fehler im BMEcat: FeatureDescription soll gesetzt werden existiert aber schon.")
        self._currentFeature.description = self._currentContent

    def addFeatureValueDetails(self, attrs = None):
        if self._currentFeature.valueDetails is not None:
            raise Exception("Fehler im BMEcat: FeatureValueDetails sollen gesetzt werden existieren aber schon.")
        self._currentFeature.valueDetails = self._currentContent

    ''' -------------- '''
    def createFeatureVariantSet(self, attrs = None):
        if self._currentFeature.values is not None and len(self._currentFeature.values) > 0:
            raise Exception("Fehler im BMEcat: FeatureVariants sollen hinzugefügt werden, es existieren aber schon FeatureValues.")
        if self._currentFeature.variants is not None:
            raise Exception("Fehler im BMEcat: FeatureVariants sollen hinzugefügt werden, es existieren aber schon FeatureVariants.")
        self._currentFeature.variants = VariantSet()

    def addFeatureVariantSetOrder(self, attrs = None):
        if self._currentFeature.variants is None:
            raise Exception("Fehler im BMEcat: FeatureVariantSetOrder soll gesetzt werden, aber es existiert noch kein VariantSet.")
        self._currentFeature.variants.order = int(self._currentContent)

    def createFeatureVariant(self, attrs = None):
        if self._currentFeature.values is not None and len(self._currentFeature.values) > 0:
            raise Exception("Fehler im BMEcat: FeatureVariants sollen hinzugefügt werden, es existieren aber schon FeatureValues.")
        if self._currentFeature.variants is None:
            raise Exception("Fehler im BMEcat: FeatureVariant soll erstellt werden, aber es existiert noch kein VariantSet.")
        if self._currentVariant is None:
            raise Exception("Fehler im BMEcat: FeatureVariant soll erstellt werden, aber es existiert schon eine.")
        self._currentVariant = Variant()
        self._currentElement = self._currentVariant
        
    def addFeatureVariantProductIdSuffix(self, attrs = None):
        if self._currentVariant is None:
            raise Exception("Fehler im BMEcat: FeatureVariantProductIdSuffix soll gesetzt werden, aber es existiert noch keine Variante.")
        self._currentVariant.productIdSuffix = self._currentContent

    def saveFeatureVariant(self, attrs = None):
        if self._currentArticle.variants is None:
            raise Exception("Fehler im BMEcat: FeatureVariant soll gespeichert werden, aber es existiert kein VariantSet mehr.")
        self._currentFeature.variants.append(self._currentVariant)
        self._currentVariant = None
        self._currentElement = None
           
    ''' ---------------------------------------------------------------------'''
    def startDateTime(self, attrs = None):
        if attrs is None or not 'type' in attrs.getNames():
            logging.warning("DateTime kann nicht gespeichert werden.")
        else:
            self._dateType = attrs.getValue('type')
            self._currentElement = self._currentPriceDetails
    
    def endDateTime(self, attrs = None):
        self._dateType = None
        self._currentElement = None
    
    def addDate(self, attrs = None):
        if self._dateType is None:
            logging.warning("Datum kann nicht gespeichert werden.")
        elif self._currentElement is None:
            logging.warning("Datum [" + self._dateType + "] kann nicht gespeichert werden, weil kein Element zum Speichern existiert.")
        else:
            if self._dateType == 'valid_start_date':
                self._currentElement.validFrom = datetime.strptime(self._currentContent, self._dateFormat)
            elif self._dateType == 'valid_end_date':
                self._currentElement.validTo = datetime.strptime(self._currentContent, self._dateFormat)
            else:
                logging.warning("Datum [" + self._dateType + "] kann nicht gespeichert werden.")

        
    ''' ---------------------------------------------------------------------'''
    def addKeyword(self, attrs = None):
        if self._currentArticle is not None:
            self._currentArticle.addKeyword(self._currentContent)
            
    ''' ---------------------------------------------------------------------'''
    '''aktuellen Inhalt des XML-Elements ermitteln'''
    def characters(self, content):
        if self.lineFeedToHTML:
            self._currentContent += content.replace("\n","<br>").strip()
        else:
            self._currentContent += content.strip()

    def validateCurrentProduct(self):
        if self._currentArticle is None:
            raise Exception("Es wurde kein aktuell zu bearbeitender Artikel gefunden.")
        self._currentArticle.validate()