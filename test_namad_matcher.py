import unittest
from namad_matcher import expand_name, tag_numbers, expand_term
import re
from namad_matcher import events_dict


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

    def test_expand_term_1(self):
        original_text = 'جریان آغاز معاملات فزر با ۱۵.۲ واحد تاثیر مثبت بر روند صعودی بازار فرابورس اثر گذار بود.'
        tagged_text = tag_numbers(original_text)
        regex = events_dict['رشد سهم'][0]
        matches = re.finditer(regex, tagged_text, re.MULTILINE)
        matches_list = []
        for matchNum, match in enumerate(matches, start=1):
            matches_list.append(original_text[match.start(): match.end()])
        self.assertTrue(len(matches_list) == 1)
        self.assertTrue(matches_list[0] == '۱۵.۲ واحد تاثیر مثبت')

    def test_expand_term_2(self):
        # Todo سهم پاک شد، کد کتابخانه مشکل دارد
        original_text = 'برکت همین افشای ب باعث شد سه درصد مثبت شود. به خاطر همین میگم پیگیر باشید.'
        tagged_text = tag_numbers(original_text)
        regex = events_dict['رشد سهم'][0]
        matches = re.finditer(regex, tagged_text, re.MULTILINE)
        matches_list = []
        for matchNum, match in enumerate(matches, start=1):
            matches_list.append(original_text[match.start(): match.end()])
        self.assertTrue(len(matches_list) == 1)
        self.assertTrue(matches_list[0] == 'سه درصد مثبت')

        regex = events_dict['اطلاعیه'][0]
        matches = re.finditer(regex, tagged_text, re.MULTILINE)
        matches_list = []
        for matchNum, match in enumerate(matches, start=1):
            matches_list.append(original_text[match.start(): match.end()])
        self.assertTrue(len(matches_list) == 1)
        self.assertTrue(matches_list[0] == 'افشای ب')

    def test_expand_term_3(self):
        original_text = 'گزارش فعالیت ماهانه دوره ۱ ماهه منتهی به ۱۴۰۰/۰۹/۳۰ برای دیران منتشر شد.'
        tagged_text = tag_numbers(original_text)
        regex = events_dict['گزارش'][0]
        matches = re.finditer(regex, tagged_text, re.MULTILINE)
        matches_list = []
        for matchNum, match in enumerate(matches, start=1):
            matches_list.append(original_text[match.start(): match.end()])
        self.assertTrue(len(matches_list) == 1)
        self.assertTrue(matches_list[0] == 'گزارش فعالیت ماهانه')


if __name__ == '__main__':
    unittest.main()
