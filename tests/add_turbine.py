import unittest
from unittest.mock import MagicMock, patch
import tkinter as tk
from app.GUI.turbine_frame import TurbineFrame

class TestTurbineFrame(unittest.TestCase):
    def setUp(self):
        # Ustvari osnovno okno tkinter kot starševski element
        self.root = tk.Tk()
        self.frame = TurbineFrame(parent=self.root)

        # Ustvari lažne vnose za simulacijo vnosov uporabnika
        self.frame.turbine_name_entry = MagicMock()
        self.frame.speed_entries = [MagicMock() for _ in range(3)]
        self.frame.power_entries = [MagicMock() for _ in range(3)]

    def tearDown(self):
        # Zapri tkinter okno po testu
        self.root.destroy()

    @patch("app.GUI.turbine_frame.save_turbines")
    @patch("app.GUI.turbine_frame.logger")
    def test_add_turbine_success(self, mock_logger, mock_save_turbines):
        """ Test uspešnega dodajanja turbine z vsemi pravilnimi podatki """
        self.frame.turbine_name_entry.get.return_value = "Turbina1"
        for entry in self.frame.speed_entries:
            entry.get.return_value = "10"
        for entry in self.frame.power_entries:
            entry.get.return_value = "1000"

        self.frame.add_turbine()

        self.assertEqual(len(self.frame.turbines), 1)
        self.assertEqual(self.frame.turbines[0]["name"], "Turbina1")
        mock_save_turbines.assert_called_once_with(self.frame.turbines)
        mock_logger.info.assert_called_once_with("Turbine added: %s", "Turbina1")

    @patch("app.GUI.turbine_frame.save_turbines")
    @patch("app.GUI.turbine_frame.logger")
    def test_add_turbine_missing_name(self, mock_logger, mock_save_turbines):
        """ Test dodajanja turbine brez imena """
        self.frame.turbine_name_entry.get.return_value = ""
        for entry in self.frame.speed_entries:
            entry.get.return_value = "10"
        for entry in self.frame.power_entries:
            entry.get.return_value = "1000"

        self.frame.add_turbine()

        self.assertEqual(len(self.frame.turbines), 0)
        mock_save_turbines.assert_not_called()
        mock_logger.info.assert_not_called()

    @patch("app.GUI.turbine_frame.save_turbines")
    @patch("app.GUI.turbine_frame.logger")
    def test_add_turbine_missing_speed_values(self, mock_logger, mock_save_turbines):
        """ Test dodajanja turbine brez vrednosti hitrosti """
        self.frame.turbine_name_entry.get.return_value = "Turbina1"
        self.frame.speed_entries[0].get.return_value = ""
        self.frame.speed_entries[1].get.return_value = "10"
        self.frame.speed_entries[2].get.return_value = "10"
        for entry in self.frame.power_entries:
            entry.get.return_value = "1000"

        self.frame.add_turbine()

        self.assertEqual(len(self.frame.turbines), 0)
        mock_save_turbines.assert_not_called()
        mock_logger.info.assert_not_called()

    @patch("app.GUI.turbine_frame.save_turbines")
    @patch("app.GUI.turbine_frame.logger")
    def test_add_turbine_non_numeric_power(self, mock_logger, mock_save_turbines):
        """ Test dodajanja turbine z neštevilčno vrednostjo moči """
        self.frame.turbine_name_entry.get.return_value = "Turbina1"
        for entry in self.frame.speed_entries:
            entry.get.return_value = "10"
        self.frame.power_entries[0].get.return_value = "1000"
        self.frame.power_entries[1].get.return_value = "invalid"
        self.frame.power_entries[2].get.return_value = "1000"

        self.frame.add_turbine()

        self.assertEqual(len(self.frame.turbines), 0)
        mock_save_turbines.assert_not_called()
        mock_logger.info.assert_not_called()

    @patch("app.GUI.turbine_frame.save_turbines")
    @patch("app.GUI.turbine_frame.logger")
    def test_add_turbine_partial_data(self, mock_logger, mock_save_turbines):
        """ Test dodajanja turbine s samo enim nizom hitrosti in moči """
        self.frame.turbine_name_entry.get.return_value = "Turbina1"
        self.frame.speed_entries[0].get.return_value = "10"
        self.frame.speed_entries[1].get.return_value = ""
        self.frame.speed_entries[2].get.return_value = ""
        self.frame.power_entries[0].get.return_value = "1000"
        self.frame.power_entries[1].get.return_value = ""
        self.frame.power_entries[2].get.return_value = ""

        self.frame.add_turbine()

        self.assertEqual(len(self.frame.turbines), 0)
        mock_save_turbines.assert_not_called()
        mock_logger.info.assert_not_called()

if __name__ == '__main__':
    unittest.main()
