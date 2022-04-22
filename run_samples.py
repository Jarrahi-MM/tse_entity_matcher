from namad_matcher import *

comments = pd.read_csv("comments.csv")
for index, row in comments.iterrows():
    print(index, end="")
    run(row['body'])
sample1 = 'تمام تلاش بازیگر اینه که کسی نتونه قیمت رو پیش بینی کنه ، حرکتهای سهم در این چند ماه بعد از بازگشایی فقط بازی بیش نیست برای بیرون انداختن نوسانگیر ها و مخفی نگهداشتن موعد صعود قیمت وگرنه همه میدونن افزایش سرمایه از طریق سود انباشته یعنی قیمت سهم باید به همون اندازه بالا بره حالا کی ؟ بازیگر تعیین می‌کنه.'
# بازگشایی-افزایش سرمایه
sample2 = 'سلام چند بار پرسیدید قیمت بورس بدلیل افزایش سرمایه بیشتر نسبت به فرابورس کمتره بورس 250 درصد بوده'
# tag expand persian name? add tagger in find?
sample3 = 'وفرابورس وضرر کردیم سودی هم نداشت'
sample4 = 'به لحظات 12.30 و صف خرید نزدیک می شویم'
sample5 = 'به نظرم فردا میتونه به روند صعودی باز گرردد مجدد . منتظر میمونیم کمی'
sample6 = 'یک نکته  تکنیکالی هم در صورت دستکاری نشدن اضافه کنم؛ کندلی که روز سه شنبه گذشته ثبت کرد بلحاظ فنی چون دو سوم آن از ابر خارج شده و کندل کاملی است و می تواند بعنوان تایید و خروج از ابر درنظر گرفت. و پولبک آن هم چهارشنبه توضیحاتش گذشت. '
sample7 = 'روز چهارشنبه یه دفعه برا خودشون افشا زدند و سهم آزاد کردن و تکنیکال و تابلو رو بهم ریختن و خب خبر نداره ما توانایی رفتارشناسی و مقایسه تابلو و روند ها رو داریم و غیره مسایل ...که انتقاد ها رو دیدید. '
sample8 = 'نماد بورس دو حمایت معتبر داره شنبه و این کار رو کرد که یسری ها بفروشند و بعد بالاتر از صفر تابلو شنبه قرار بده.'
sample9 = 'فراکابی ها همگی خوبند ولی کالا آینده بهتری داره'
sample10 = 'فراکاب ها و علی الخصوص بورس و کالا کندل پرقدرتی زدن ، احتمال رشد شارپی ازشون میره'
sample11 = 'مسیر نوسانی رو داشته باشیم'
# ?: dar expand ha
sample12 = 'حمایت و مقاومت های الکی'
sample13 = 'سلام باید منتظر صف خرید ممتد بود وضعیت عالیه نوسانگیر رو تکاندن'
sample14 = 'مکدی هم شرایط خوبی داره و کراس رو به بالا زده'
sample15 = 'هر دو تا حدود زیادی کف قیمتی خودشون را پیدا کردند و همچنین ناحیه تقاضای سهم '
sample16 = 'سر شیر فلکه رو یکدفعه باز کن 50 درصد رو حقیقی های نوسانگیر پیاده می شند اینم روش خوبیه اصلا ما نمی دانیم حجم مبنا رو پر کن'
sample17 = 'اصلا فکر کن سال جدید شده باز هم منفیه در 3/5 درصد سود بفروش'
sample18 = 'رشد خوبی این دور نخواهند داشت فراکاب ها به نظر .. آر اس آی بدون اینکه سهم بالا بیاد . چقدر اومده بالا....'
sample19 = 'سوال : آیا اصلاح دوره ای شاخص تمام شده است؟ سوالان مشابه :  '
sample20 = ' بازار با عبور از ابر کومو و کف سازی دلاری'
sample21 = 'ریزش شدید جفت ارز های فارکس '
sample22 = ' مدیریت امید'
sample23 = 'حمایت و مقاومت را شکسته'
sample24 = 'تشکیل کف دوقلو و پیش بسوی ۱۲۰۰'
sample25 = 'بانک آینده در آینده ممکنه کنه'
sample26 = 'گزارش نه ماهه هم که خوب نبود ،فرابورسم هم که گزارشش خراب بود فقط کالا خوب بوده'
sample27 = 'برکتم خوب نیست، فرابورسم خوب نیست فقط اتکام'
sample28 = '- در صورتیکه قیمت پایانی سهم طی 15 روز معاملاتی متوالی در دامنه عادی نوسان قیمت، بیش از 50 درصد افزایش داشته باشد، بورس موظف است در اولین زمان ممکن از لحاظ فنی نماد معاملاتی را متوقف کرده و از ناشر درخواست برگزاری کنفرانس اطلاع رسانی کند. نماد معاملاتی حداکثر 2 روز کاری پس از توقف نماد معاملاتی با محدودیت دامنه نوسان "بازگشایی خواهد شد.'
sample29 = 'یه کد به کد حقوقی به حقیقی ضعیفی داشت تو قیمت ۱۰۰۰'
sample30 = 'سهم در یک نگاه کلاسیک الگوی سروشانه کف رو هم ساخته که چندان این الگوها رو نباید جدی گرفت،هرچند یک نکته مثبت هست در هرصورت'
sample31 = 'اندیکاتور ها هم در تایم فریم روزانه هفتگی صعودیه دلیلی نیست فردا برنگرده'
sample32 = 'صف فروش کاملا فیک و کار حقوقیه-- هدف:ایجاد ترس و جمع اوری سهم --نتیجه:سهمتو از چنگت در نیاره'
sample33 = ''
sample34 = ''
sample35 = ''
