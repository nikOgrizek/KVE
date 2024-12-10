import unittest
from unittest import mock
from app.GUI.calculator_frame import CalculatorFrame  # Uporabljen pravilen import

class TestCalculationFrame(unittest.TestCase):
    def setUp(self):
        # Ustvari instance razreda z ustreznimi argumenti
        self.parent = None  # Ali ustrezni parent objekt
        self.save_report_callback = mock.Mock()  # Simulacija callback funkcije
        self.frame = CalculatorFrame(self.parent, self.save_report_callback)

    @mock.patch('app.GUI.calculator_frame.export_to_pdf')  # Ponarejanje funkcije export_to_pdf
    def test_export_pdf_no_coordinates(self, mock_export_pdf):
        self.frame.selected_turbines = ["Turbina 1"]  # Simulirajte izbrane turbine
        self.frame.coordinates = None  # Simulirajte manjkajoče koordinate

        with self.assertRaises(ValueError):  # Očekujte napako
            self.frame.export_pdf()  # Klic funkcije naj povzroči napako

    @mock.patch('app.GUI.calculator_frame.export_to_pdf')  # Ponarejanje funkcije export_to_pdf
    def test_export_pdf_no_selected_turbines(self, mock_export_pdf):
        self.frame.selected_turbines = []  # Ni izbranih turbin
        self.frame.coordinates = [(10.0, 20.0)]  # Simulirajte koordinate

        with self.assertRaises(ValueError):  # Očekujte napako
            self.frame.export_pdf()  # Klic funkcije naj povzroči napako

    @mock.patch('os.path.exists', return_value=True)  # Ponarejanje os.path.exists
    @mock.patch('os.remove')  # Ponarejanje os.remove
    @mock.patch('app.GUI.calculator_frame.export_to_pdf')  # Ponarejanje funkcije export_to_pdf
    def test_export_pdf_success(self, mock_export_pdf, mock_remove, mock_exists):
        self.frame.selected_turbines = ["Turbina 1", "Turbina 2"]  # Simulirajte izbrane turbine
        self.frame.coordinates = [(10.0, 20.0)]  # Simulirajte koordinate
        self.frame.results_label = mock.Mock()  # Ustvarimo mock za results_label
        self.frame.results_label.cget.return_value = "Test report"  # Nastavimo vrnjeno vrednost

        # Klic funkcije naj uspe
        self.frame.export_pdf()

        # Preverimo, da je bila funkcija export_to_pdf klicana
        mock_export_pdf.assert_called_once()
        # Preverimo, da je bil os.remove poklican
        mock_remove.assert_called_once()

if __name__ == '__main__':
    unittest.main()
