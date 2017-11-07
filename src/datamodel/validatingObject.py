'''
Created on 07.10.2017

@author: Henrik Pilz
'''
from abc import abstractmethod
from array import array
import logging

from lxml.etree import SubElement, Element


class NoValueGivenException(Exception):
    '''
    Exception thrown when no Value is given.
    '''
    
class ComparableEqual(object):
    '''
    Interface Class for a Class which are comparable
    '''
    
    def __eq__(self, other):
        return isinstance(other, self.__class__)

    def __ne__(self, other):
        return not self.__eq__(other)


class ValidatingObject(object):
    '''
    Interface Class for a Class which validates its content
    '''
    
    def add(self, attributeName, attributeValue):
        try:
            if not isinstance(getattr(self, attributeName), (list, array)):
                setattr(self, attributeName, attributeValue)
            else:
                getattr(self, attributeName).append(attributeValue)
        except AttributeError as ae:
            logging.error("Klassenattribut nicht gefunden: ", str(ae))
    
    @classmethod
    def checkListForEquality(self, lhs, rhs):
        for leftItem in lhs:
            if leftItem not in rhs:
                return False

        for rightItem in rhs:
            if rightItem not in lhs:
                return False
        return True
    
    def validateList(self, listToValidate, raiseException):
        for listItem in listToValidate:
            listItem.validate(raiseException)
    
    @abstractmethod
    def validate(self, raiseException=False):
        raise NotImplementedError("Please implement 'validate' in your class '{0}".format(__file__))
    
    def valueNotNone(self, attribute, message=None, raiseException=False):
        if attribute is None:
            self.logError(message, raiseException)
            return False
        return True

    def valueNotNoneOrEmpty(self, attribute, message=None, raiseException=False):
        if not self.valueNotNone(attribute, message, raiseException):
            return False
        isNotEmpty = True
        if isinstance(attribute, str):
            isNotEmpty = len(attribute.strip()) > 0                
        elif isinstance(attribute, (list, array)):
            isNotEmpty = len(attribute) > 0
        else:
            isNotEmpty = len(str(attribute).strip()) > 0
        if isNotEmpty:
            return True
        self.logError(message, raiseException)
        return False

    
    def logError(self, errMsg=None, raiseException=False):
        '''
         Taking an ErrorMessage, logging it and if wanted throwing an Exception
        '''
        if errMsg is not None:
            logging.error(errMsg)
        if raiseException:
            raise Exception(errMsg)

    def addToListIfValid(self, item, listToAddTo, errorMessage, raiseException=True):
        try:
            self.__determineOrderIfNeeded(item, listToAddTo)
            item.validate(raiseException)
            if item not in listToAddTo:
                listToAddTo.append(item)
                return True
        except Exception as ve:
            logging.warning(errorMessage + "{0}".format(str(ve)))
        return False


    def __determineOrderIfNeeded(self, item, orderedList):
        try:
            if getattr(item, "order") is None or int(item.order) <= 0:
                self.__determineOrder(item, orderedList)
        except AttributeError:
            pass

    def __determineOrder(self, item, orderedList):
        maxItem = max(orderedList, key=lambda item: int(item.order), default=None)
        if maxItem is None:             
            item.order = 1
        else:
            item.order = int(maxItem.order) + 1


class XMLObject(object):
    '''
    Interface Class for a Class which validates its content
    '''
    
    @abstractmethod
    def toXml(self):
        raise NotImplementedError("Please implement 'toXml' in your class '{0}".format(__file__))
    
    def addMandatorySubElement(self, parent, tag, value):
        '''
        Erstellt eiin Child-Element und wirft eine Exception, falls value nicht None
        '''
        if value is None:
            raise NoValueGivenException("Kein Wert übergeben.")
        subElement = SubElement(parent, tag)
        subElement.text = str(value)
        return subElement
        
    
    def addOptionalSubElement(self, parent, tag, value):
        '''
        Erstellt eiin Child-Element, falls value nicht None
        '''
        if value is not None and len(str(value)) > 0:
            return self.addMandatorySubElement(parent, tag, value)
        return None

    def addListOfSubElements(self, parent, listOfSubElements, raiseExceptionOnValidate=True):
        for element in listOfSubElements:
            parent.append(element.toXml(raiseExceptionOnValidate=raiseExceptionOnValidate))

    def addDateTimeSubElement(self, parent, dateType, date):
        dateTimeSubElement = SubElement(parent, "DATETIME", { "type"  : dateType})
        dateSubElement = SubElement(dateTimeSubElement, "DATE")
        dateSubElement.text = date.strftime("%Y-%m-%d")
        timeSubElement = SubElement(dateTimeSubElement, "TIME")
        timeSubElement.text = date.strftime("%H:%M:%S")
        
class ValidatingXMLObject(ValidatingObject, XMLObject):

    def validateAndCreateBaseElement(self, tagname, attributes=None, raiseExceptionOnValidate=True):
        self.validate(raiseExceptionOnValidate)
        return Element(tagname, attributes)

