'''
Created on 16.07.2017

@author: Henrik Pilz
'''
import unittest

from data.mime import Mime
from data.reference import Reference


class TestReference(unittest.TestCase):

    def testInit(self):
        reference = Reference()
        
        self.assertIsNone(reference.referenceType)
        self.assertIsNone( reference.description)
        self.assertEqual( reference.quantity, 1)
        
        self.assertIsNotNone(reference.supplierArticleIds)
        self.assertEqual( len(reference.supplierArticleIds), 0)
        
        self.assertIsNotNone(reference.mimeInfo)
        self.assertEqual( len(reference.mimeInfo), 0)

    def testAddMime(self):
        reference = Reference()
        self.assertEqual( len(reference.mimeInfo), 0)
        reference.addMime(Mime())
        self.assertEqual( len(reference.mimeInfo), 1)    
            
    def testAddSupplierArticleId(self):
        reference = Reference()
        self.assertEqual( len(reference.supplierArticleIds), 0)
        reference.addSupplierArticleId("test")
        self.assertEqual( len(reference.supplierArticleIds), 1)
        
        
        
    # Testcases  
    #
    #    if self.referenceType is None:
    #        super().logError("Der Referenz wurde kein Typ zugewiesen.",  raiseException)
    #    if self.supplierArticleIds is None or len(self.supplierArticleIds) == 0:
    #        super().logError("Es wird keine Artikelnummer referenziert.",  raiseException)
    def testValidateExceptionNoType(self):
        reference = Reference()
        with self.assertRaisesRegex(Exception, "Der Referenz wurde kein Typ zugewiesen."):
            reference.validate(True)

    def testValidateExceptionNoIds(self):
        reference = Reference()
        reference.referenceType = "sparepart"
        with self.assertRaisesRegex(Exception, "Es wird keine Artikelnummer referenziert."):
            reference.validate(True)
        
    def testValidate(self):
        reference = Reference()
        reference.referenceType = "sparepart"
        reference.addSupplierArticleId("Test")
        reference.validate(True)
        

if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()
    