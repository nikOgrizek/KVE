import unittest
from unittest import mock
import tkinter as tk
from app.GUI.turbine_frame import TurbineFrame


class TestTurbineFrame(unittest.TestCase):

    def setUp(self):
        self.root = tk.Tk()  # Ustvarimo pravi Tkinter root
        self.frame = TurbineFrame(self.root)  # Inicializiramo razred TurbineFrame
        self.frame.turbines = []  # Inicializiramo prazno listo turbin
        self.frame.selected_turbine_index = None

    def tearDown(self):
        self.root.destroy()  # Uničimo Tkinter root po končanih testih

    @mock.patch('app.GUI.turbine_frame.save_turbines')
    def test_update_turbine(self, mock_save_turbines):
        # Dodamo turbino in jo izberemo
        self.frame.turbines.append({"name": "Turbina 1", "speeds": ["5", "10"], "powers": ["100", "200"]})
        self.frame.selected_turbine_index = 0

        # Simuliramo vnos vnosnih polj
        self.frame.turbine_name_entry = mock.Mock()
        self.frame.turbine_name_entry.get = mock.Mock(return_value="Turbina 1 Updated")
        self.frame.speed_entries = [mock.Mock(), mock.Mock()]
        self.frame.power_entries = [mock.Mock(), mock.Mock()]
        self.frame.speed_entries[0].get.return_value = "6"
        self.frame.speed_entries[1].get.return_value = "11"
        self.frame.power_entries[0].get.return_value = "110"
        self.frame.power_entries[1].get.return_value = "210"

        # Izvedemo posodobitev
        self.frame.update_turbine()

        # Preverimo, da je turbina posodobljena
        self.assertEqual(self.frame.turbines[0],
                         {"name": "Turbina 1 Updated", "speeds": ["6", "11"], "powers": ["110", "210"]})
        mock_save_turbines.assert_called_once()  # Preverimo, da je bila funkcija save_turbines klicana
        self.assertIsNone(self.frame.selected_turbine_index)  # Preverimo, da je index izbrana turbina None

    @mock.patch('app.GUI.turbine_frame.save_turbines')
    def test_delete_turbine(self, mock_save_turbines):
        # Dodamo turbino
        self.frame.turbines.append({"name": "Turbina 1", "speeds": ["5", "10"], "powers": ["100", "200"]})
        self.frame.selected_turbine_index = 0  # Izberemo turbino

        # Izvedemo brisanje
        self.frame.delete_turbine()

        # Preverimo, da je turbina odstranjena
        self.assertEqual(len(self.frame.turbines), 0)
        mock_save_turbines.assert_called_once()  # Preverimo, da je bila funkcija save_turbines klicana
        self.assertIsNone(self.frame.selected_turbine_index)  # Preverimo, da je index izbrana turbina None


if __name__ == '__main__':
    unittest.main()
