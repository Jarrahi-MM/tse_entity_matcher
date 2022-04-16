import unittest
from namad_matcher import expand
import re


class TestStringMethods(unittest.TestCase):

    def test_upper(self):
        regex = expand('نفت ( ) -- _ـ  ‌ ها')
        test_str = 'نفتها'
        matches = re.finditer(regex, test_str, re.MULTILINE)
        matches_count = 0
        for _, _ in enumerate(matches, start=1):
            matches_count += 1
        self.assertTrue(matches_count == 1)


if __name__ == '__main__':
    unittest.main()
