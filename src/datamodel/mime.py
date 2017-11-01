'''
Created on 05.05.2017

@author: henrik.pilz
'''
from . import ValidatingXMLObject, ComparableEqual

class Mime(ValidatingXMLObject, ComparableEqual):
    
    __allowedTypes = [ "url", "application/pdf", "image/jpeg", "image/jpg", "image/tif", "text/html", "text/plain", "image/tiff", "image/eps" ]
    __allowedPurposes = [ "thumbnail", "normal", "detail", "data_sheet", "logo", "others" ]
    __allowedCombinations = {}
    
    def __init__(self):
        self.source = None
        self.mimeType = None
        self.description = None
        self.altenativeContent = None
        self.purpose = None
        self.order = None
        
    def __eq__(self, other):
        if not super().__eq__(other):
            return False
        else:
            return self.source == other.source

    def validate(self, raiseException=False):
        super().valueNotNone(self.source, "Kein Bildpfad angegeben.", raiseException)
        super().valueNotNone(self.order, "Bildreihenfolge fehlerhaft: " + str(self.order), raiseException)
        if super().valueNotNone(self.mimeType, "Bildtyp nicht gesetzt.", raiseException) and self.mimeType not in Mime.__allowedTypes:
            super().logError("Bildtyp fehlerhaft: " + str(self.mimeType), raiseException)
        if super().valueNotNone(self.purpose, "Bildverwendung nicht gesetzt.", raiseException) and self.purpose not in Mime.__allowedPurposes:
            super().logError("Bildverwendung fehlerhaft: " + str(self.purpose), raiseException)

    def toXml(self, raiseExceptionOnValidate=True):
        mimeElement = super().validateAndCreateBaseElement("MIME", raiseExceptionOnValidate=raiseExceptionOnValidate)
        super().addMandatorySubElement(mimeElement, "MIME_SOURCE", self.source)
        super().addMandatorySubElement(mimeElement, "MIME_TYPE", self.mimeType)
        super().addMandatorySubElement(mimeElement, "MIME_PURPOSE", self.purpose)
        super().addMandatorySubElement(mimeElement, "MIME_ORDER", self.order)
        super().addOptionalSubElement(mimeElement, "MIME_DESCR", self.description)
        super().addOptionalSubElement(mimeElement, "MIME_ALT", self.altenativeContent)
        return mimeElement