import unittest
from namad_matcher import expand_name, tag_numbers
import re


class TestStringMethods(unittest.TestCase):

    def test_expand_name(self):
        regex = expand_name('نفت ( ) -- _ـ  ‌ ها')
        test_str = 'نفتها'
        matches = re.finditer(regex, test_str, re.MULTILINE)
        matches_count = 0
        for _, _ in enumerate(matches, start=1):
            matches_count += 1
        self.assertTrue(matches_count == 1)

    def test_tag_numbers(self):
        original_text = 'امسال سه درصد یا ۳.۱۳ درصد یا 3.13 درصد سود کسب کردم.'
        true_tagged_text = 'امسال ~~ درصد یا ~~~~ درصد یا ~~~~ درصد سود کسب کردم.'
        self.assertTrue(tag_numbers(original_text) == true_tagged_text)


if __name__ == '__main__':
    unittest.main()
