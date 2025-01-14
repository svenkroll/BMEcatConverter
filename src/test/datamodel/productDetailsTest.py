'''
Created on 16.07.2017

@author: Henrik Pilz
'''
import unittest

from datamodel import ProductDetails
from datamodel import TreatmentClass


class ProductDetailsTest(unittest.TestCase):

    def testInit(self):
        productdetails = ProductDetails()
        self.assertIsNone(productdetails.title)
        self.assertIsNone(productdetails.description)
        self.assertIsNone(productdetails.manufacturerTypeDescription)
        self.assertIsNone(productdetails.ean)
        self.assertIsNone(productdetails.supplierAltId)
        self.assertIsNone(productdetails.buyerId)
        self.assertIsNone(productdetails.manufacturerArticleId)
        self.assertIsNone(productdetails.manufacturerName)
        self.assertIsNone(productdetails.erpGroupBuyer)
        self.assertIsNone(productdetails.erpGroupSupplier)
        self.assertEqual(productdetails.deliveryTime, 2)
        self.assertIsNotNone(productdetails.specialTreatmentClasses)
        self.assertEqual(len(productdetails.specialTreatmentClasses), 0)
        self.assertIsNotNone(productdetails.keywords)
        self.assertEqual(len(productdetails.keywords), 0)
        self.assertIsNotNone(productdetails.remarks)
        self.assertEqual(len(productdetails.remarks), 0)
        self.assertIsNotNone(productdetails.segment)
        self.assertEqual(len(productdetails.segment), 0)

        self.assertEqual(productdetails.articleOrder, 1)
        self.assertIsNone(productdetails.articleStatus)

    def testAddSpecialTreatmentClass(self):
        productdetails = ProductDetails()
        self.assertEqual(len(productdetails.specialTreatmentClasses), 0)
        productdetails.addSpecialTreatmentClass(TreatmentClass())
        self.assertEqual(len(productdetails.specialTreatmentClasses), 0)
        treatmentclass = TreatmentClass()
        treatmentclass.classType = "CType"
        treatmentclass.value = "CValue"
        productdetails.addSpecialTreatmentClass(treatmentclass)
        self.assertEqual(len(productdetails.specialTreatmentClasses), 1)

    def testAddKeyword(self,):
        productdetails = ProductDetails()
        self.assertEqual(len(productdetails.keywords), 0)
        productdetails.addKeyword(None)
        self.assertEqual(len(productdetails.keywords), 0)
        productdetails.addKeyword("")
        self.assertEqual(len(productdetails.keywords), 0)
        productdetails.addKeyword("Test")
        self.assertEqual(len(productdetails.keywords), 1)

    def testValidateExceptionNoArticleTitle(self):
        productdetails = ProductDetails()
        with self.assertRaisesRegex(Exception, "Der Artikelname fehlt."):
            productdetails.validate(True)

    def testValidateExceptionDescriptionWrongEndDoubleQuoteForFiege(self):
        productdetails = ProductDetails()
        productdetails.title = "Test"
        productdetails.manufacturerArticleId = " 01239 \n"
        productdetails.description = " \t asdfkjah sdlfas \r\n\""
        with self.assertRaisesRegex(Exception, "Die Artikelbeschreibung sollte nicht mit Anführungsstrichen enden."):
            productdetails.validate(True)

    def testValidateExceptionDescriptionWrongEndDoubleQuote(self):
        productdetails = ProductDetails()
        productdetails.title = "Test"
        productdetails.manufacturerArticleId = " 01239 \n"
        productdetails.description = " \t asdfkjah sdlfas \r\n\""
        productdetails.validate(False)

    def testValidateExceptionDescriptionWrongContainsDoubleDoubleQuote(self):
        productdetails = ProductDetails()
        productdetails.title = "Test"
        productdetails.manufacturerArticleId = " 01239"
        productdetails.description = ' asd ""fkjah sdlfas '
        with self.assertRaisesRegex(Exception, "Die Artikelbeschreibung darf keine doppelten Anführungsstriche enthalten!"):
            productdetails.validate(True)

    def testValidateNoExceptionNoArticleTitle(self):
        productdetails = ProductDetails()
        productdetails.validate(False)

    def testValidate(self):
        productdetails = ProductDetails()
        productdetails.title = "Test"
        productdetails.manufacturerArticleId = " 01239 \n"
        productdetails.description = " \t asdfkjahsdlfas \r\n"
        productdetails.validate(True)
        self.assertEqual(productdetails.manufacturerArticleId, "01239", "Leerzeichen in der Herstellerartikelnummer.")
        self.assertEqual(productdetails.description, "asdfkjahsdlfas", "Leerzeichen in der Beschreibung.")

    def testEqual(self):
        productdetails1 = ProductDetails()
        self.assertNotEqual(productdetails1, None, "Productdetails should not be equal to None")
        self.assertNotEqual(productdetails1, "", "Productdetails should not be equal to str")

        productdetails2 = ProductDetails()
        self.assertEqual(productdetails1, productdetails2, "Empty Productdetails should not be equal")
        self.assertTrue(productdetails1 == productdetails2, "Productdetails should be equal via '=='")
        self.assertFalse(productdetails1 != productdetails2, "Productdetails should not be nonequal via '!='")

# if __name__ == "__main__":
    # import sys;sys.argv = ['', 'Test.testName']
#    unittest.main()
