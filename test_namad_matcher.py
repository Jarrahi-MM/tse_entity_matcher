from tse_entity_matcher import expand_persian_name, remove_complete_overlaps, tag_numbers, map_event_regexes, \
    find_entities


class TestTagNumbers:
    def test_tag_numbers(self):
        original_text = 'امسال سه درصد یا ۳.۱۳ درصد یا 3.13 درصد سود کسب کردم.'
        true_tagged_text = 'امسال ~~ درصد یا ~~~~ درصد یا ~~~~ درصد سود کسب کردم.'
        assert (tag_numbers(original_text) == true_tagged_text)


class TestExpansion:

    def test_expand_name(self):
        regex = expand_persian_name('نفت ( ) -- _ـ  ‌ ها')
        test_str = 'نفتها'
        matches_count = 0
        for _ in regex[0][0].finditer(test_str):
            matches_count += 1
        assert (matches_count == 1)

    def test_expand_term_1(self):
        original_text = 'جریان آغاز معاملات فزر با ۱۵.۲ واحد تاثیر مثبت بر روند صعودی بازار فرابورس اثر گذار بود.'
        tagged_text = tag_numbers(original_text)
        regex = map_event_regexes['رشد سهم'][0]
        matches_list = []
        for match in regex[0].finditer(tagged_text):
            matches_list.append(original_text[match.start(): match.end()])
        assert (len(matches_list) == 1)
        assert (matches_list[0] == '۱۵.۲ واحد تاثیر مثبت')

    def test_expand_term_2(self):
        original_text = 'برکت همین افشای ب باعث شد سهم سه درصد مثبت شود. به خاطر همین میگم پیگیر باشید.'
        tagged_text = tag_numbers(original_text)
        regex = map_event_regexes['رشد سهم'][0]
        matches_list = []
        for match in regex[0].finditer(tagged_text):
            matches_list.append(original_text[match.start(): match.end()])
        assert (len(matches_list) == 1)
        assert (matches_list[0] == 'سه درصد مثبت')

        regex = map_event_regexes['اطلاعیه'][0]
        matches_list = []
        for match in regex[0].finditer(tagged_text):
            matches_list.append(original_text[match.start(): match.end()])
        assert (len(matches_list) == 1)
        assert (matches_list[0] == 'افشای ب')

    def test_expand_term_3(self):
        original_text = 'گزارش فعالیت ماهانه دوره ۱ ماهه منتهی به ۱۴۰۰/۰۹/۳۰ برای دیران منتشر شد.'
        tagged_text = tag_numbers(original_text)
        regex = map_event_regexes['گزارش'][0]
        matches_list = []
        for match in regex[0].finditer(tagged_text):
            matches_list.append(original_text[match.start(): match.end()])
        assert (len(matches_list) == 1)
        assert (matches_list[0] == 'گزارش فعالیت ماهانه')


class TestRemoveOverlaps:
    def test_remove_complete_overlap_1(self):
        cleaned_sample = remove_complete_overlaps(
            [{"span": (0, 10)}, {"span": (0, 20)}, {"span": (2, 20)}])
        assert (len(cleaned_sample) == 1)
        assert (cleaned_sample[0]["span"] == (0, 20))

    def test_remove_complete_overlap_2(self):
        cleaned_sample = remove_complete_overlaps(
            [{"span": (0, 10)}, {"span": (1, 8)}, {"span": (2, 9)}])
        assert (len(cleaned_sample) == 1)
        assert (cleaned_sample[0]["span"] == (0, 10))


class TestFind:
    def test_find_1(self):
        text = "فولاد مبارکه اصفهان"
        results = find_entities(text)
        assert (len(results) == 1)
        assert (results[0]['type'] == "نماد")
        assert (results[0]['symbol'] == 'فولاد')
        assert (results[0]['span'] == (0, 19))

    def test_find_2(self):
        text = "فولاد مبارکه‌ی اصفهان"
        results = find_entities(text)
        assert (len(results) == 1)
        assert (results[0]['type'] == "نماد")
        assert (results[0]['symbol'] == 'فولاد')
        assert (results[0]['marker'] == 'فولاد مبارکه\u200cی اصفهان')

    def test_find_3(self):
        text = 'جریان آغاز معاملات فزر با ۱۵.۲ واحد تاثیر مثبت بر روند صعودی بازار فرابورس اثر گذار بود.'
        results = find_entities(text)
        assert (len(results) == 4)
        assert (results[0]['type'] == "نماد")
        assert (results[0]['symbol'] == 'فزر')
        assert (results[0]['span'] == (19, 22))
        assert (results[1]['type'] == 'رشد سهم')
        assert (results[1]['span'] == (26, 46))
        assert (results[2]['type'] == 'روند')
        assert (results[2]['marker'] == 'روند صعودی')
        assert (results[3]['type'] == "نماد")
        assert (results[3]['symbol'] == 'فرابورس')
        assert (results[3]['span'] == (67, 74))

    def test_find_4(self):
        text = 'برکت همین افشای ب باعث شد سهم سه درصد مثبت شود. بخاطر همین میگم پیگیر باشید.'
        results = find_entities(text)
        assert (len(results) == 3)
        assert (results[0]['type'] == "نماد")
        assert (results[0]['symbol'] == 'برکت')
        assert (results[0]['span'] == (0, 4))
        assert (results[1]['type'] == 'اطلاعیه')
        assert (results[1]['span'] == (10, 17))
        assert (results[2]['type'] == 'رشد سهم')
        assert (results[2]['span'] == (30, 42))

    def test_find_5(self):
        text = 'گزارش فعالیت ماهانه دوره ۱ ماهه منتهی به ۱۴۰۰̸۰۹̸۳۰ برای دیران منتشر شد.'
        results = find_entities(text)
        assert (len(results) == 2)
        assert (results[0]['type'] == 'گزارش')
        assert (results[0]['span'] == (0, 19))
        assert (results[1]['type'] == "نماد")
        assert (results[1]['symbol'] == 'دیران')
        assert (results[1]['span'] == (57, 62))

    def test_find_6(self):
        text = 'Sina Insurance is a good Insurance company!'
        results = find_entities(text)
        assert (len(results) == 1)
        assert (results[0]['type'] == "نماد")
        assert (results[0]['symbol'] == 'وسین')
        assert (results[0]['marker'] == 'Sina Insurance')

    def test_find_7(self):
        text = ' IRO7VSNP0001 is a good Insurance company!'
        results = find_entities(text)
        assert (len(results) == 1)
        assert (results[0]['type'] == "نماد")
        assert (results[0]['symbol'] == 'وسین')
        assert (results[0]['marker'] == 'IRO7VSNP0001')

    def test_find_8(self):
        text = 'انرژی ۳  یا انرژی‌۳ یا انرژی۳ یا انرژی 3 یا انرژی‌3 یا انرژی3 خیلی خوب است.'
        results = find_entities(text)
        assert (len(results) == 6)
        assert (results[0]['marker'] == 'انرژی ۳')
        assert (results[1]['marker'] == 'انرژی‌۳')
        assert (results[2]['marker'] == 'انرژی۳')
        assert (results[3]['marker'] == 'انرژی 3')
        assert (results[4]['marker'] == 'انرژی‌3')
        assert (results[5]['marker'] == 'انرژی3')

    def test_find_9(self):
        text = "سهم بازگشایی شد"
        results = find_entities(text)
        assert (len(results) == 1)
        assert (results[0]['marker'] == 'بازگشایی')
        assert (results[0]['type'] == "بازگشایی")

    def test_find_10(self):
        text = "سهم افزایش سرمایه خورد"
        results = find_entities(text)
        assert (len(results) == 1)
        assert (results[0]['marker'] == 'افزایش سرمایه')
        assert (results[0]['type'] == "افزایش سرمایه")

    def test_find_11(self):
        text = "به لحظات 12.30 و صف خرید نزدیک می شویم"
        results = find_entities(text)
        assert (len(results) == 1)
        assert (results[0]['marker'] == 'صف خرید')
        assert (results[0]['type'] == "صف")

    def test_find_12(self):
        text = "به لحظات 12.30 و روندی صعودی نزدیک می شویم"
        results = find_entities(text)
        assert (len(results) == 1)
        assert (results[0]['marker'] == 'روندی صعودی')
        assert (results[0]['type'] == "روند")

    def test_find_13(self):
        text = 'یک نکته  تکنیکالی هم در صورت دستکاری نشدن اضافه کنم؛ کندلی که روز سه شنبه گذشته ثبت کرد بلحاظ فنی چون دو سوم آن از ابر خارج شده و کندل کاملی است و می تواند بعنوان تایید و خروج از ابر درنظر گرفت. و پولبک آن هم چهارشنبه توضیحاتش گذشت. '
        results = find_entities(text)
        assert (len(results) == 3)
        assert (results[0]['marker'] == 'کندلی')
        assert (results[1]['marker'] == 'کندل')
        assert (results[2]['marker'] == 'پولبک')

    def test_find_14(self):
        text = "فراکابی ها همگی خوبند. فراکاب ها و علی الخصوص بورس و کالا کندل پرقدرتی زدن"
        results = find_entities(text)
        assert (len(results) == 5)
        assert (results[0]['type'] == "نماد")
        assert (results[0]['symbol'] == 'فراکاب')
        assert (results[0]['marker'] == 'فراکابی')
        assert (results[1]['type'] == "نماد")
        assert (results[1]['symbol'] == 'فراکاب')
        assert (results[1]['marker'] == 'فراکاب')

    def test_find_15(self):
        text = 'ریزش شدید جفت ارز های فارکس '
        results = find_entities(text)
        assert (len(results) == 1)
        assert (results[0]['marker'] == 'ریزش')

    def test_find_16(self):
        text = 'تشکیل کف دوقلو و پیش بسوی ۱۲۰۰'
        results = find_entities(text)
        assert (len(results) == 2)
        assert (results[0]['marker'] == 'کف')
        assert (results[0]['type'] == 'تکنیکال')
        assert (results[1]['marker'] == 'دوقلو')

    def test_find_17(self):
        text = 'گزارش نه ماهه هم که خوب نبوده'
        results = find_entities(text)
        assert (len(results) == 1)
        assert (results[0]['marker'] == 'گزارش نه ماهه')

    def test_find_18(self):
        text = 'در یک نگاه کلاسیک الگوی سروشانه رو هم ساخته'
        results = find_entities(text)
        assert (len(results) == 1)
        assert (results[0]['marker'] == 'سروشانه')

    def test_find_19(self):
        text = 'مکدی هم شرایط خوبی داره و کراس رو به بالا زده'
        results = find_entities(text)
        assert (len(results) == 2)
        assert (results[0]['marker'] == 'مکدی')
        assert (results[1]['marker'] == 'کراس')

    def test_find_20(self):
        text = ' بازار با عبور از ابر کومو و کف سازی دلاری'
        results = find_entities(text)
        assert (len(results) == 2)
        assert (results[0]['marker'] == 'ابر کومو')
        assert (results[1]['marker'] == 'کف سازی')

    def test_find_21(self):
        text = 'یه کد به کد داشت تو قیمت ۱۰۰۰'
        results = find_entities(text)
        assert (len(results) == 1)
        assert (results[0]['marker'] == 'کد به کد')

    def test_find_22(self):
        text = ' پس از توقف نماد معاملاتی باز خواهد شد.'
        results = find_entities(text)
        assert (len(results) == 1)
        assert (results[0]['marker'] == 'توقف نماد')

    def test_find_23(self):
        text = 'خبر دارم از #انرژی ۲'
        results = find_entities(text)
        assert (len(results) == 1)
        assert (results[0]['marker'] == 'انرژی ۲')

    def test_find_24(self):
        text = "سهم فولاد مبارکه بسیار عالی است و سهم فولاد مبارکه‌ی شهر اصفهان عالی است."
        results = find_entities(text)
        assert (len(results) == 2)
        assert (results[0]['type'] == "نماد")
        assert (results[0]['marker'] == 'فولاد مبارکه')
        assert (results[0]['symbol'] == 'فولاد')
        assert (results[1]['type'] == "نماد")
        assert (results[1]['marker'] == 'فولاد مبارکه‌ی')
        assert (results[1]['symbol'] == 'فولاد')

    def test_find_25(self):
        text = 'پالایش بندرعباس دارم ببین اصن عالیه'
        results = find_entities(text)
        assert (len(results) == 1)
        assert (results[0]['marker'] == 'پالایش بندرعباس')
        assert (results[0]['symbol'] == 'شبندر')

    def test_find_26(self):
        text = 'نفت قشم ولک عالیه'
        results = find_entities(text)
        assert (len(results) == 1)
        assert (results[0]['marker'] == 'نفت قشم')

    def test_find_hagh_1(self):
        text = "من کویرح را فروختم و به کویر تبدیل کردم."
        results = find_entities(text)
        assert (len(results) == 2)
        assert (results[0]['type'] == "نماد")
        assert (results[0]['type_detailed'] == 'نماد حق تقدم شرکت')
        assert (results[0]['symbol'] == 'کویر')
        assert (results[0]['marker'] == 'کویرح')
        assert (results[0]['span'] == (3, 8))
        assert (results[1]['type'] == "نماد")
        assert (results[1]['type_detailed'] == 'نماد شرکت')
        assert (results[1]['symbol'] == 'کویر')
        assert (results[1]['marker'] == 'کویر')
        assert (results[1]['span'] == (24, 28))

    def test_find_hagh_2(self):
        text = "من سهم حق تقدم کویر را خریدم"
        results = find_entities(text)
        assert (len(results) == 1)
        assert (results[0]['type'] == "نماد")
        assert (results[0]['type_detailed'] == 'نماد حق تقدم شرکت')
        assert (results[0]['symbol'] == 'کویر')
        assert (results[0]['marker'] == 'حق تقدم کویر')

    def test_find_hagh_3(self):
        text = "من سهم حق‌تقدم کویر را خریدم"
        results = find_entities(text)
        assert (len(results) == 1)
        assert (results[0]['type'] == "نماد")
        assert (results[0]['type_detailed'] == 'نماد حق تقدم شرکت')
        assert (results[0]['symbol'] == 'کویر')
        assert (results[0]['marker'] == 'حق‌تقدم کویر')

    def test_find_hagh_4(self):
        text = "من سهم تقدم کویر را خریدم"
        results = find_entities(text)
        assert (len(results) == 1)
        assert (results[0]['type'] == "نماد")
        assert (results[0]['type_detailed'] == 'نماد حق تقدم شرکت')
        assert (results[0]['symbol'] == 'کویر')
        assert (results[0]['marker'] == 'تقدم کویر')


