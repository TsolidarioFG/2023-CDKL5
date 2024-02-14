from django.test import TransactionTestCase

from dataManagement.models import Macros

class testModel(TransactionTestCase):
    tarifaEntera = 20
    tarifaDecimal = 45.54
    diaCobro = 5
    mesCobro = 12

#---------------------------------------------------------------------------------------------------------------------------------------------------
#                                                           T E S T S
#---------------------------------------------------------------------------------------------------------------------------------------------------

    def testBeforeWritingInDB(self):
        with self.assertRaises(Macros.DoesNotExist):
            macroEntry = Macros(
                TarifaSocios = self.tarifaEntera,
                MinimoAmigos = self.tarifaDecimal,
                diaCobro = self.diaCobro,
                mesCobro = self.mesCobro,
            )
            Macros.objects.get(TarifaSocios=self.tarifaEntera) # aún no guardado en la base de datos, debe saltar una excepción

#---------------------------------------------------------------------------------------------------------------------------------------------------

    def testAddToDB(self):
        macroEntry = Macros(
            TarifaSocios = self.tarifaEntera,
            MinimoAmigos = self.tarifaDecimal,
            diaCobro = self.diaCobro,
            mesCobro = self.mesCobro,
        )
        macroEntry.save()
        instance = Macros.objects.get(TarifaSocios=self.tarifaEntera)
        self.assertIsNotNone(instance)
        self.assertEquals(instance.id, 1)
        self.assertEquals(instance.TarifaSocios, self.tarifaEntera)
        self.assertEquals(instance.MinimoAmigos, self.tarifaDecimal)
        self.assertEquals(instance.diaCobro, self.diaCobro)
        self.assertEquals(instance.mesCobro, self.mesCobro)

        # ---------- Modificar valores ---------------

        macroEntry.mesCobro = 5
        macroEntry.TarifaSocios = self.tarifaDecimal
        macroEntry.save()

        instance = Macros.objects.get(id=1)
        self.assertIsNotNone(instance)
        self.assertEquals(instance.mesCobro, 5)
        self.assertEquals(instance.TarifaSocios, self.tarifaDecimal)