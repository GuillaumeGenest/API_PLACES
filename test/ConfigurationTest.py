import os
import sys
import importlib
import time
import unittest


class CustomTestResult(unittest.TextTestResult):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.test_counter = 0  # Compteur pour suivre le numéro du test

    def startTest(self, test):
        super().startTest(test)
        self.test_counter += 1  # Incrémenter le compteur pour chaque nouveau test
        print(f"\nDébut du test {self.test_counter}: {test._testMethodName}")
        self.start_time = time.time()  # Enregistrer le temps de début

    def stopTest(self, test):
        super().stopTest(test)
        duration = time.time() - self.start_time  # Calculer la durée du test
        print(f"  =>  Fin du test {self.test_counter}: {test._testMethodName} - Durée : {duration:.4f} secondes")
        if test._outcome.success:
            print(f"Statut : SUCCESS ✅")
        else:
            print(f"Statut : FAILED ⛔️")
