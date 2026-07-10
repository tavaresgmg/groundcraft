import unittest

from services import auth_timeout, profile_timeout


class TimeoutConversionTest(unittest.TestCase):
    def test_auth_timeout_is_250_milliseconds(self) -> None:
        self.assertEqual(auth_timeout(), 0.25)

    def test_profile_timeout_is_500_milliseconds(self) -> None:
        self.assertEqual(profile_timeout(), 0.5)


if __name__ == "__main__":
    unittest.main()
