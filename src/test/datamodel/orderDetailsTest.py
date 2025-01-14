'''
Created on 16.07.2017

@author: Henrik Pilz
'''
import unittest

from datamodel import OrderDetails


class OrderDetailsTest(unittest.TestCase):

    def testInit(self):
        orderDetails = OrderDetails()

        self.assertEqual(orderDetails.orderUnit, "C62")
        self.assertEqual(orderDetails.contentUnit, "C62")
        self.assertEqual(orderDetails.packingQuantity, 1)
        self.assertEqual(orderDetails.priceQuantity, 1)
        self.assertEqual(orderDetails.quantityMin, 1)
        self.assertEqual(orderDetails.quantityInterval, 1)

    def testValidateExceptionNoOrderUnitSet(self):
        orderDetails = OrderDetails()
        orderDetails.orderUnit = None
        with self.assertRaisesRegex(Exception, "Keine Bestelleinheit angeben."):
            orderDetails.validate(True)
        orderDetails.orderUnit = ""
        with self.assertRaisesRegex(Exception, "Keine Bestelleinheit angeben."):
            orderDetails.validate(True)

    def testValidateExceptionWrongOrderUnitSet(self):
        orderDetails = OrderDetails()
        orderDetails.orderUnit = "Bla"
        with self.assertRaisesRegex(Exception, "Falsche Bestelleinheit angeben. Wert: " + str(orderDetails.orderUnit)):
            orderDetails.validate(True)

    def testValidateExceptionNoContentUnitSet(self):
        orderDetails = OrderDetails()
        orderDetails.orderUnit = "C62"
        orderDetails.contentUnit = None
        with self.assertRaisesRegex(Exception, "Keine Verpackungseinheit angeben."):
            orderDetails.validate(True)
        orderDetails.contentUnit = ""
        with self.assertRaisesRegex(Exception, "Keine Verpackungseinheit angeben."):
            orderDetails.validate(True)

    def testValidateExceptionWrongContentUnitSet(self):
        orderDetails = OrderDetails()
        orderDetails.orderUnit = "C62"
        orderDetails.contentUnit = "Blubb"
        with self.assertRaisesRegex(Exception, "Falsche Verpackungseinheit angeben. Wert: " + str(orderDetails.contentUnit)):
            orderDetails.validate(True)

    def testValidate(self):
        orderDetails = OrderDetails()
        orderDetails.orderUnit = "C62"
        orderDetails.contentUnit = "C62"
        orderDetails.validate(False)
        orderDetails.quantityMin = 11
        orderDetails.validate(False)
        orderDetails.quantityInterval = 12
        orderDetails.validate(False)
        orderDetails.packingQuantity = 2
        orderDetails.validate(False)
        orderDetails.priceQuantity = 18
        orderDetails.validate(False)

    def testValidateFiege(self):
        orderDetails = OrderDetails()
        orderDetails.orderUnit = "C62"
        orderDetails.contentUnit = "C62"
        orderDetails.validate(True)
        orderDetails.quantityMin = 11
        with self.assertRaisesRegex(Exception, "Mindestbestellmenge und Bestellintervall sollten gleich sein."):
            orderDetails.validate(True)

        orderDetails.quantityInterval = 11
        orderDetails.packingQuantity = 12
        # with self.assertRaisesRegex(Exception, "Mindestbestellmenge und PackingQuantity duerfen nicht beide ungleich eins sein."):
        orderDetails.validate(True)
        orderDetails.quantityMin = 1
        orderDetails.quantityInterval = 1
        orderDetails.packingQuantity = 2
        orderDetails.validate(True)
        orderDetails.priceQuantity = 18
        orderDetails.validate(True)

    def testEqual(self):
        orderDetails1 = OrderDetails()
        self.assertNotEqual(orderDetails1, "", "OrderDetails should not be equal to str")
        orderDetails2 = OrderDetails()
        self.assertEqual(orderDetails1, orderDetails2, "Empty orderDetails should be equal.")
        self.assertTrue(orderDetails1 == orderDetails2, "Empty orderDetails should be equal via '=='.")
        self.assertFalse(orderDetails1 != orderDetails2, "Empty orderDetails should not be unequal via '!='.")

# if __name__ == "__main__":
    # import sys;sys.argv = ['', 'Test.testName']
#    unittest.main()
