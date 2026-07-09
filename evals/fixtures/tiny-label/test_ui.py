import unittest

from ui import save_button_label


class SaveButtonTest(unittest.TestCase):
    def test_label(self) -> None:
        self.assertEqual(save_button_label(), "Save")


if __name__ == "__main__":
    unittest.main()
