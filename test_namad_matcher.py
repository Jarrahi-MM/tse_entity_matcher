import unittest
from namad_matcher import expand_persian_name, remove_complete_overlaps, tag_numbers
import re
from namad_matcher import map_event_regexes, find, map_symbol_regexes


class TestTagNumbers(unittest.TestCase):
    def test_tag_numbers(self):
        original_text = 'امسال سه درصد یا ۳.۱۳ درصد یا 3.13 درصد سود کسب کردم.'
        true_tagged_text = 'امسال ~~ درصد یا ~~~~ درصد یا ~~~~ درصد سود کسب کردم.'
        self.assertTrue(tag_numbers(original_text) == true_tagged_text)


class TestExpansion(unittest.TestCase):

    def test_expand_name(self):
        regex = expand_persian_name('نفت ( ) -- _ـ  ‌ ها')
        test_str = 'نفتها'
        matches = re.finditer(regex[0][0], test_str, re.MULTILINE)
        matches_count = 0
        for _, _ in enumerate(matches, start=1):
            matches_count += 1
        self.assertTrue(matches_count == 1)

    def test_expand_term_1(self):
        original_text = 'جریان آغاز معاملات فزر با ۱۵.۲ واحد تاثیر مثبت بر روند صعودی بازار فرابورس اثر گذار بود.'
        tagged_text = tag_numbers(original_text)
        regex = map_event_regexes['رشد سهم'][0]
        matches = re.finditer(regex[0], tagged_text, re.MULTILINE)
        matches_list = []
        for matchNum, match in enumerate(matches, start=1):
            matches_list.append(original_text[match.start(): match.end()])
        self.assertTrue(len(matches_list) == 1)
        self.assertTrue(matches_list[0] == '۱۵.۲ واحد تاثیر مثبت')

    def test_expand_term_2(self):
        original_text = 'برکت همین افشای ب باعث شد سهم سه درصد مثبت شود. به خاطر همین میگم پیگیر باشید.'
        tagged_text = tag_numbers(original_text)
        regex = map_event_regexes['رشد سهم'][0]
        matches = re.finditer(regex[0], tagged_text, re.MULTILINE)
        matches_list = []
        for matchNum, match in enumerate(matches, start=1):
            matches_list.append(original_text[match.start(): match.end()])
        self.assertTrue(len(matches_list) == 1)
        self.assertTrue(matches_list[0] == 'سه درصد مثبت')

        regex = map_event_regexes['اطلاعیه'][0]
        matches = re.finditer(regex[0], tagged_text, re.MULTILINE)
        matches_list = []
        for matchNum, match in enumerate(matches, start=1):
            matches_list.append(original_text[match.start(): match.end()])
        self.assertTrue(len(matches_list) == 1)
        self.assertTrue(matches_list[0] == 'افشای ب')

    def test_expand_term_3(self):
        original_text = 'گزارش فعالیت ماهانه دوره ۱ ماهه منتهی به ۱۴۰۰/۰۹/۳۰ برای دیران منتشر شد.'
        tagged_text = tag_numbers(original_text)
        regex = map_event_regexes['گزارش'][0]
        matches = re.finditer(regex[0], tagged_text, re.MULTILINE)
        matches_list = []
        for matchNum, match in enumerate(matches, start=1):
            matches_list.append(original_text[match.start(): match.end()])
        self.assertTrue(len(matches_list) == 1)
        self.assertTrue(matches_list[0] == 'گزارش فعالیت ماهانه')


class TestRemoveOverlaps(unittest.TestCase):
    def test_remove_complete_overlap_1(self):
        cleaned_sample = remove_complete_overlaps(
            [{"span": (0, 10)}, {"span": (0, 20)}, {"span": (2, 20)}])
        self.assertTrue(len(cleaned_sample) == 1)
        self.assertTrue(cleaned_sample[0]["span"] == (0, 20))

    def test_remove_complete_overlap_2(self):
        cleaned_sample = remove_complete_overlaps(
            [{"span": (0, 10)}, {"span": (1, 8)}, {"span": (2, 9)}])
        self.assertTrue(len(cleaned_sample) == 1)
        self.assertTrue(cleaned_sample[0]["span"] == (0, 10))


class TestFind(unittest.TestCase):
    def test_find_1(self):
        text = "فولاد مبارکه اصفهان"
        results = find(text)
        self.assertTrue(len(results) == 1)
        self.assertTrue(results[0]['type'] == "نماد")
        self.assertTrue(results[0]['symbol'] == 'فولاد')
        self.assertTrue(results[0]['span'] == (0, 19))

    def test_find_2(self):
        text = "فولاد مبارکه‌ی اصفهان"
        results = find(text)
        self.assertTrue(len(results) == 1)
        self.assertTrue(results[0]['type'] == "نماد")
        self.assertTrue(results[0]['symbol'] == 'فولاد')
        self.assertTrue(results[0]['marker'] == 'فولاد مبارکه\u200cی اصفهان')

    def test_find_3(self):
        text = 'جریان آغاز معاملات فزر با ۱۵.۲ واحد تاثیر مثبت بر روند صعودی بازار فرابورس اثر گذار بود.'
        results = find(text)
        self.assertTrue(len(results) == 3)
        self.assertTrue(results[0]['type'] == "نماد")
        self.assertTrue(results[0]['symbol'] == 'فزر')
        self.assertTrue(results[0]['span'] == (19, 22))
        self.assertTrue(results[1]['type'] == 'رشد سهم')
        self.assertTrue(results[1]['span'] == (26, 46))
        self.assertTrue(results[2]['type'] == "نماد")
        self.assertTrue(results[2]['symbol'] == 'فرابورس')
        self.assertTrue(results[2]['span'] == (67, 74))

    def test_find_4(self):
        text = 'برکت همین افشای ب باعث شد سهم سه درصد مثبت شود. به خاطر همین میگم پیگیر باشید.'
        results = find(text)
        self.assertTrue(len(results) == 3)
        self.assertTrue(results[0]['type'] == "نماد")
        self.assertTrue(results[0]['symbol'] == 'برکت')
        self.assertTrue(results[0]['span'] == (0, 4))
        self.assertTrue(results[1]['type'] == 'اطلاعیه')
        self.assertTrue(results[1]['span'] == (10, 17))
        self.assertTrue(results[2]['type'] == 'رشد سهم')
        self.assertTrue(results[2]['span'] == (30, 42))


    def test_find_5(self):
        text = 'گزارش فعالیت ماهانه دوره ۱ ماهه منتهی به ۱۴۰۰/۰۹/۳۰ برای دیران منتشر شد.'
        results = find(text)
        self.assertTrue(len(results) == 2)
        self.assertTrue(results[0]['type'] == 'گزارش')
        self.assertTrue(results[0]['span'] == (0, 19))
        self.assertTrue(results[1]['type'] == "نماد")
        self.assertTrue(results[1]['symbol'] == 'دیران')
        self.assertTrue(results[1]['span'] == (57, 62))
        
    def test_find_6(self):
        text='Sina Insurance is a good Insurance company!'
        results = find(text)
        self.assertTrue(len(results) == 1)
        self.assertTrue(results[0]['type'] == "نماد")
        self.assertTrue(results[0]['symbol'] == 'وسین')
        self.assertTrue(results[0]['marker'] == 'Sina Insurance')
        
    def test_find_7(self):
        text=' IRO7VSNP0001 is a good Insurance company!'
        results = find(text)
        self.assertTrue(len(results) == 1)
        self.assertTrue(results[0]['type'] == "نماد")
        self.assertTrue(results[0]['symbol'] == 'وسین')
        self.assertTrue(results[0]['marker'] == 'IRO7VSNP0001')
        
    def test_find_8(self):
        text='انرژی ۳  یا انرژی‌۳ یا انرژی۳ یا انرژی 3 یا انرژی‌3 یا انرژی3 خیلی خوب است.'
        results = find(text)
        self.assertTrue(len(results) == 6)
        self.assertTrue(results[0]['marker'] == 'انرژی ۳')
        self.assertTrue(results[1]['marker'] == 'انرژی‌۳')
        self.assertTrue(results[2]['marker'] == 'انرژی۳')
        self.assertTrue(results[3]['marker'] == 'انرژی 3')
        self.assertTrue(results[4]['marker'] == 'انرژی‌3')
        self.assertTrue(results[5]['marker'] == 'انرژی3')

class TestFindHagh(unittest.TestCase):
    def test_find_hagh_1(self):
        text = "من کویرح را فروختم و به کویر تبدیل کردم."
        results = find(text)
        self.assertTrue(len(results) == 2)
        self.assertTrue(results[0]['type'] == "نماد")
        self.assertTrue(results[0]['type_detailed'] == 'نماد حق تقدم شرکت')
        self.assertTrue(results[0]['symbol'] == 'کویر')
        self.assertTrue(results[0]['marker'] == 'کویرح')
        self.assertTrue(results[0]['span'] == (3, 8))
        self.assertTrue(results[1]['type'] == "نماد")
        self.assertTrue(results[1]['type_detailed'] == 'نماد شرکت')
        self.assertTrue(results[1]['symbol'] == 'کویر')
        self.assertTrue(results[1]['marker'] == 'کویر')
        self.assertTrue(results[1]['span'] == (24, 28))
        
    def test_find_hagh_2(self):
        text = "من سهم حق تقدم کویر را خریدم"
        results = find(text)
        self.assertTrue(len(results) == 1)
        self.assertTrue(results[0]['type'] == "نماد")
        self.assertTrue(results[0]['type_detailed'] == 'نماد حق تقدم شرکت')
        self.assertTrue(results[0]['symbol'] == 'کویر')
        self.assertTrue(results[0]['marker'] == 'حق تقدم کویر')
    
    def test_find_hagh_3(self):
        text = "من سهم حق‌تقدم کویر را خریدم"
        results = find(text)
        self.assertTrue(len(results) == 1)
        self.assertTrue(results[0]['type'] == "نماد")
        self.assertTrue(results[0]['type_detailed'] == 'نماد حق تقدم شرکت')
        self.assertTrue(results[0]['symbol'] == 'کویر')
        self.assertTrue(results[0]['marker'] == 'حق‌تقدم کویر')
        
    def test_find_hagh_4(self):
        text = "من سهم تقدم کویر را خریدم"
        results = find(text)
        self.assertTrue(len(results) == 1)
        self.assertTrue(results[0]['type'] == "نماد")
        self.assertTrue(results[0]['type_detailed'] == 'نماد حق تقدم شرکت')
        self.assertTrue(results[0]['symbol'] == 'کویر')
        self.assertTrue(results[0]['marker'] == 'تقدم کویر')

if __name__ == '__main__':
    unittest.main()
