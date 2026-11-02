# VietFlowers — сайт доставки цветов в Нячанге. Генерирует site/: главные RU (/), EN (/en/), VI (/vi/),
# посадочные страницы под запросы RU + EN, sitemap.xml, robots.txt. Запуск: python build.py
# Править здесь: контакты, домен, цены, тексты. Готовые html руками не трогать — пересобрать.
import json, os, html, shutil
from urllib.parse import quote

BRAND = 'VietFlowers'
SITE = 'https://admin11111111113.github.io/vietflowers'   # пока без домена; купим — поменять
TG_USER = 'workminer'                      # Telegram без @
WA_PHONE = '79041188897'                   # WhatsApp цифрами с кодом страны
WA_SHOW = '+7 904 118-88-97'
DISCOUNT = 100_000                         # насколько дешевле конкурента, в донгах
RUB, USD = 294, 25000                      # донгов за 1 ₽ / за $1
HOURS = '07:00–21:00'
LEAD_URL = 'https://vietavto-orders.onrender.com/flower-lead'   # заявка → бот @VietAvto_bot (тот же релей)

# каталог: цена = цена конкурента − DISCOUNT. Фото и закупка — наши поставщики:
# TB = «Hoa tươi thả bình», 27 Chu Văn An (прайс в FB 27–28.10); AT = Athena Nguyen, Phước Đồng. Себестоимость + ~40k упаковка.
CATALOG = [  # (id, категория, цена конкурента, с кем сравнили, закупка)
    ('r25', 'roses', 500_000, 'flowers-nha-trang.online, 25 роз', 'AT розы 105k/50 → ~55k'),
    ('tul_p', 'tulips', 650_000, 'hoathanhnha.com, самый дешёвый букет HB165', 'TB тюльпан 350k/10'),
    ('hydr3', 'hydr', 650_000, 'hoathanhnha.com, HB165', 'TB гортензия имп. 60k/шт ×3'),
    ('r101', 'roses', 1_500_000, 'flowers-nha-trang.online, 101 роза', 'TB розы 190k/50 ×2'),
    ('lily_p', 'lily', 600_000, 'flowers-nha-trang.online, 7 веток лилий', 'TB ly hồng công chúa 80k/пачка'),
    ('mix', 'bouquet', 1_500_000, 'flowers-nha-trang.online, сборный букет', 'TB альстромерия/микс ~400k'),
    ('r15', 'roses', 300_000, 'hoathanhnha.com, базовый букет HB110', 'AT розы 105k/50 → ~32k'),
    ('tul_w', 'tulips', 650_000, 'hoathanhnha.com, HB165', 'TB тюльпан 350k/10'),
    ('hydr_mix', 'hydr', 750_000, 'hoathanhnha.com, HB158', 'TB гортензия имп. 60k ×5'),
    ('r51', 'roses', 1_000_000, 'flowers-nha-trang.online, 51 роза', 'TB розы 190k/50'),
    ('lily_dbl', 'lily', 600_000, 'flowers-nha-trang.online, 7 веток лилий', 'TB ly kép hồng 180k/пачка'),
    ('green_hydr', 'hydr', 650_000, 'hoathanhnha.com, HB165', 'TB гортензия xanh bơ 50k/5 + tana 70k'),
    ('gerb', 'bouquet', 300_000, 'hoathanhnha.com, HB110', 'TB đồng tiền nhí 60k/20'),
    ('tana', 'bouquet', 300_000, 'hoathanhnha.com, HB110', 'TB cúc tana 70k'),
    ('star', 'bouquet', 300_000, 'hoathanhnha.com, HB110', 'TB sao xanh 100k'),
]
PRICE = {k: bench - DISCOUNT for k, _c, bench, _s, _cost in CATALOG}
ZONES = [('center', None), ('north', 50_000), ('west', 50_000), ('south', 50_000), ('camranh', 200_000)]   # наша цена (у конкурента 100k / 300k); None = бесплатно

T = {
'ru': {
    'lang': 'ru', 'path': '', 'locale': 'ru_RU',
    'title': 'Доставка цветов в Нячанге — цены на сайте, букеты от 200 000 ₫ | VietFlowers',
    'desc': 'Доставка цветов в Нячанге и Камрани в день заказа: розы, 101 роза, тюльпаны, гортензии, лилии. Все цены на сайте и на 100 000 ₫ ниже конкурентов, фото букета до отправки, отвечаем по-русски.',
    'h1': 'Доставка цветов в&nbsp;Нячанге',
    'lead': 'Свежие букеты в отель, квартиру или ресторан — в день заказа. Все цены прямо на сайте, фото готового букета присылаем до отправки, говорим по-русски.',
    'promise': 'Каждый букет на 100 000 ₫ дешевле конкурентов',
    'cta': 'Заказать букет', 'tg': 'Telegram', 'wa': 'WhatsApp', 'order': 'Заказать', 'more': 'Все букеты',
    'nav': [('catalog', 'Букеты'), ('order', 'Заказ'), ('delivery', 'Доставка'), ('faq', 'Вопросы')],
    'adv': [('💸', 'Цены на сайте', 'Не нужно спрашивать в личке — всё видно сразу'),
            ('📸', 'Фото до отправки', 'Показываем ваш букет перед доставкой'),
            ('🏨', 'В отели и квартиры', 'Нячанг и Камрань, до лобби или в руки'),
            ('🇷🇺', 'По-русски', 'Пишите в WhatsApp или Telegram, оплата в ₽, $ или ₫')],
    'catalog': 'Букеты и цены', 'catalog_sub': 'Цены в донгах, рядом — примерно в рублях и долларах. Любой букет соберём в другом цвете.',
    'cats': [('all', 'Все'), ('roses', 'Розы'), ('tulips', 'Тюльпаны'), ('hydr', 'Гортензии'), ('lily', 'Лилии'), ('bouquet', 'Букеты')],
    'items': {
        'r25': ('25 красных роз', 'Крупные далатские розы с зеленью'),
        'tul_p': ('Розовые тюльпаны, 10 шт', 'Нежная классика, редкость для Нячанга'),
        'hydr3': ('Гортензии, 3 шт', 'Крупные импортные шапки — розовые, голубые или белые'),
        'r101': ('101 роза', 'Огромный букет, который запомнят'),
        'lily_p': ('Розовые лилии', 'Лилии «принцесса» с ароматом'),
        'mix': ('Большой яркий букет', 'Альстромерии и сезонные цветы — море красок'),
        'r15': ('15 красных роз', 'Аккуратный букет для свидания'),
        'tul_w': ('Белые тюльпаны, 10 шт', 'Чистые и свежие — для любого повода'),
        'hydr_mix': ('Микс гортензий, 5 шт', 'Розовые, голубые и белые шапки'),
        'r51': ('51 розовая роза', 'Круглый букет в стильной упаковке'),
        'lily_dbl': ('Белые лилии', 'Пышный букет с ароматом'),
        'green_hydr': ('Бело-зелёные гортензии', 'Свежий букет из пышных шапок'),
        'gerb': ('Белые герберы, 7 шт', 'Крупные герберы в упаковке'),
        'tana': ('Ромашки', 'Букет садовой ромашки (танацетум)'),
        'star': ('Голубой букет', 'Голубые и жёлтые цветы в синей упаковке'),
    },
    'delivery': 'Доставка по Нячангу и Камрани', 'delivery_sub': f'Каждый день {HOURS}. Везём в отели, апартаменты, рестораны и домой, время согласуем при заказе.',
    'zones': {'center': 'Центр Нячанга', 'north': 'Север (Хон Чонг, Винь Хоа)', 'west': 'Запад (Винь Хьеп, Винь Тхань)', 'south': 'Юг (Винь Чыонг, Фыок Донг)', 'camranh': 'Камрань (отели и аэропорт)'},
    'free': 'бесплатно',
    'how': 'Как заказать', 'steps': [('Выберите букет', 'Здесь на сайте или пришлите фото-пример'), ('Напишите нам', 'Форма ниже соберёт сообщение в WhatsApp или Telegram'), ('Получите фото', 'Покажем готовый букет перед отправкой'), ('Встречайте курьера', 'Привезём в отель, квартиру или ресторан')],
    'pay': 'Оплата', 'pay_sub': 'Как удобно: перевод в рублях, долларах или донгах, или наличными курьеру. Заказ из России — оплачиваете переводом, мы присылаем фото букета и вручения.',
    'faq': 'Частые вопросы',
    'faqs': [('Можно ли заказать цветы в Нячанг из России?', 'Да. Напишите нам в WhatsApp или Telegram: какой букет, адрес получателя в Нячанге и время. Оплата переводом в рублях, после вручения пришлём фото.'),
             ('Доставляете в отели?', 'Да, в любые отели и апартаменты Нячанга и Камрани. Курьер оставит букет на ресепшене или передаст лично в руки.'),
             ('Как быстро привезёте?', 'В день заказа. Срочный заказ — напишите, скажем точное время.'),
             ('Почему у вас дешевле?', 'Мы берём цветы напрямую у оптовиков Нячанга и Далата, без лишних посредников. Поэтому каждый букет на 100 000 ₫ дешевле, чем у других доставок, и цена видна сразу.'),
             ('Можно собрать свой букет?', 'Да. Пришлите фото-пример или бюджет — соберём в нужных цветах.'),
             ('Будет открытка?', 'Да, открытка с вашим текстом — бесплатно. Напишите текст в форме заказа.')],
    'form': 'Оформить заказ', 'form_sub': 'Заполните, что знаете, — мы соберём сообщение, вам останется нажать «Отправить» в мессенджере.',
    'f_item': 'Букет', 'f_custom': 'Свой вариант (опишу в сообщении)', 'f_date': 'Дата', 'f_time': 'Время', 'f_addr': 'Адрес или отель',
    'f_addr_ph': 'Например: Sheraton, номер 1205', 'f_to': 'Кому (имя получателя)', 'f_card': 'Текст открытки', 'f_card_ph': 'С днём рождения!',
    'f_from': 'Ваше имя', 'f_send_wa': 'Отправить в WhatsApp', 'f_send_tg': 'Отправить в Telegram',
    'f_hint': 'Telegram: если текст не подставился, он уже скопирован — просто вставьте.',
    'f_phone': 'Ваш WhatsApp или Telegram', 'f_phone_ph': '+7 900 000-00-00 или @username', 'f_lead': 'Оставить заявку — мы напишем',
    'f_ok': 'Заявка отправлена! Напишем вам в течение 15 минут.', 'f_err': 'Не отправилось — нажмите WhatsApp или Telegram.', 'f_need': 'Укажите ваш WhatsApp или Telegram, чтобы мы могли ответить.',
    'm_hello': 'Здравствуйте! Хочу заказать цветы.', 'm_item': 'Букет: ', 'm_date': 'Когда: ', 'm_addr': 'Адрес: ', 'm_to': 'Кому: ', 'm_card': 'Открытка: ', 'm_from': 'От: ',
    'contacts': 'Напишите нам', 'contacts_sub': 'Отвечаем быстро. Пришлите фото понравившегося букета — подскажем цену.',
    'credits': 'Фото: Pexels', 'wa_text': 'Здравствуйте! Хочу заказать: ', 'approx_rub': True,
    'related': 'Ещё по теме', 'home': 'Главная',
},
'en': {
    'lang': 'en', 'path': 'en/', 'locale': 'en_US',
    'title': 'Flower Delivery in Nha Trang — prices online, bouquets from 200,000 ₫ | VietFlowers',
    'desc': 'Same-day flower delivery in Nha Trang and Cam Ranh: roses, 101 roses, tulips, hydrangeas, lilies. All prices online and 100,000 ₫ below competitors, photo of your bouquet before delivery.',
    'h1': 'Flower delivery in&nbsp;Nha&nbsp;Trang',
    'lead': 'Fresh bouquets to your hotel, apartment or restaurant — same day. All prices are right here, and we send a photo of the finished bouquet before it leaves.',
    'promise': 'Every bouquet 100,000 ₫ cheaper than competitors',
    'cta': 'Order a bouquet', 'tg': 'Telegram', 'wa': 'WhatsApp', 'order': 'Order', 'more': 'All bouquets',
    'nav': [('catalog', 'Bouquets'), ('order', 'Order'), ('delivery', 'Delivery'), ('faq', 'FAQ')],
    'adv': [('💸', 'Prices online', 'No need to ask — every price is on the site'),
            ('📸', 'Photo before delivery', 'See your bouquet before it leaves'),
            ('🏨', 'Hotels & apartments', 'Nha Trang and Cam Ranh, to the lobby or in person'),
            ('💬', 'Easy to order', 'WhatsApp or Telegram, pay in $, ₽ or ₫')],
    'catalog': 'Bouquets & prices', 'catalog_sub': 'Prices in VND with approx. USD. Any bouquet can be made in another colour.',
    'cats': [('all', 'All'), ('roses', 'Roses'), ('tulips', 'Tulips'), ('hydr', 'Hydrangeas'), ('lily', 'Lilies'), ('bouquet', 'Bouquets')],
    'items': {
        'r25': ('25 red roses', 'Large Da Lat roses with greenery'),
        'tul_p': ('Pink tulips, 10 stems', 'Soft classic, rare in Nha Trang'),
        'hydr3': ('Hydrangeas, 3 stems', 'Big imported heads — pink, blue or white'),
        'r101': ('101 roses', 'A huge bouquet to remember'),
        'lily_p': ('Pink lilies', 'Fragrant “princess” lilies'),
        'mix': ('Big bright bouquet', 'Alstroemerias and seasonal flowers'),
        'r15': ('15 red roses', 'A neat bouquet for a date'),
        'tul_w': ('White tulips, 10 stems', 'Clean and fresh for any occasion'),
        'hydr_mix': ('Hydrangea mix, 5 stems', 'Pink, blue and white heads'),
        'r51': ('51 pink roses', 'A round bouquet in stylish wrapping'),
        'lily_dbl': ('White lilies', 'A lush, fragrant bouquet'),
        'green_hydr': ('White-green hydrangeas', 'Fresh bouquet of lush heads'),
        'gerb': ('White gerberas, 7 stems', 'Large gerberas, wrapped'),
        'tana': ('Daisies', 'Garden daisy (tanacetum) bouquet'),
        'star': ('Blue bouquet', 'Blue and yellow flowers in blue wrapping'),
    },
    'delivery': 'Delivery in Nha Trang and Cam Ranh', 'delivery_sub': f'Every day {HOURS}. To hotels, apartments, restaurants and homes; time agreed when ordering.',
    'zones': {'center': 'Nha Trang centre', 'north': 'North (Hon Chong, Vinh Hoa)', 'west': 'West (Vinh Hiep, Vinh Thanh)', 'south': 'South (Vinh Truong, Phuoc Dong)', 'camranh': 'Cam Ranh (resorts & airport)'},
    'free': 'free',
    'how': 'How to order', 'steps': [('Pick a bouquet', 'On this site, or send us a photo'), ('Message us', 'The form below writes the WhatsApp or Telegram message'), ('Get a photo', 'We show the finished bouquet before delivery'), ('Meet the courier', 'Delivered to your hotel, apartment or restaurant')],
    'pay': 'Payment', 'pay_sub': 'Bank transfer in USD, RUB or VND, or cash to the courier. Ordering from abroad — pay by transfer, we send photos of the bouquet and the hand-over.',
    'faq': 'FAQ',
    'faqs': [('Can I send flowers to Nha Trang from abroad?', 'Yes. Message us on WhatsApp or Telegram with the bouquet, the recipient’s address and the time. Pay by transfer; we send a photo after delivery.'),
             ('Do you deliver to hotels?', 'Yes, to any hotel or apartment in Nha Trang and Cam Ranh — at reception or in person.'),
             ('How fast is delivery?', 'Same day. For urgent orders, message us and we’ll give an exact time.'),
             ('Why are you cheaper?', 'We buy directly from Nha Trang and Da Lat wholesalers, so every bouquet is 100,000 ₫ below other delivery shops — and the price is right on the site.'),
             ('Can I design my own bouquet?', 'Yes. Send a photo or your budget and we’ll make it in your colours.'),
             ('Is a card included?', 'Yes, a card with your message is free. Type it in the order form.')],
    'form': 'Place an order', 'form_sub': 'Fill in what you know — we’ll write the message, you just press Send in the messenger.',
    'f_item': 'Bouquet', 'f_custom': 'Something else (I’ll describe it)', 'f_date': 'Date', 'f_time': 'Time', 'f_addr': 'Address or hotel',
    'f_addr_ph': 'e.g. Sheraton, room 1205', 'f_to': 'Recipient’s name', 'f_card': 'Card message', 'f_card_ph': 'Happy birthday!',
    'f_from': 'Your name', 'f_send_wa': 'Send via WhatsApp', 'f_send_tg': 'Send via Telegram',
    'f_hint': 'Telegram: if the text didn’t appear, it’s already copied — just paste it.',
    'f_phone': 'Your WhatsApp or Telegram', 'f_phone_ph': '+1 555 000 0000 or @username', 'f_lead': 'Send request — we’ll message you',
    'f_ok': 'Request sent! We’ll message you within 15 minutes.', 'f_err': 'Couldn’t send — please use WhatsApp or Telegram.', 'f_need': 'Add your WhatsApp or Telegram so we can reply.',
    'm_hello': 'Hello! I would like to order flowers.', 'm_item': 'Bouquet: ', 'm_date': 'When: ', 'm_addr': 'Address: ', 'm_to': 'To: ', 'm_card': 'Card: ', 'm_from': 'From: ',
    'contacts': 'Message us', 'contacts_sub': 'We reply fast. Send a photo of a bouquet you like and we’ll quote a price.',
    'credits': 'Photos: Pexels', 'wa_text': 'Hello! I would like to order: ', 'approx_rub': False,
    'related': 'See also', 'home': 'Home',
},
'vi': {
    'lang': 'vi', 'path': 'vi/', 'locale': 'vi_VN',
    'title': 'Hoa tươi Nha Trang giao tận nơi — bó hoa từ 200.000 ₫ | VietFlowers',
    'desc': 'Giao hoa tươi Nha Trang, Cam Ranh trong ngày: hoa hồng, 101 bông hồng, tulip, cẩm tú cầu, hoa ly. Giá công khai, gửi ảnh thật trước khi giao.',
    'h1': 'Hoa tươi Nha&nbsp;Trang giao tận&nbsp;nơi',
    'lead': 'Hoa tươi giao đến khách sạn, căn hộ hay nhà hàng ngay trong ngày. Giá công khai, gửi ảnh bó hoa thật trước khi giao.',
    'promise': 'Rẻ hơn các shop khác cho mọi bó hoa',
    'cta': 'Đặt hoa', 'tg': 'Telegram', 'wa': 'WhatsApp', 'order': 'Đặt', 'more': 'Tất cả mẫu hoa',
    'nav': [('catalog', 'Bó hoa'), ('order', 'Đặt hoa'), ('delivery', 'Giao hàng'), ('faq', 'Hỏi đáp')],
    'adv': [('💸', 'Giá công khai', 'Không cần hỏi giá qua tin nhắn'),
            ('📸', 'Ảnh thật trước khi giao', 'Xem bó hoa của bạn trước khi gửi'),
            ('🏨', 'Khách sạn, căn hộ', 'Nha Trang và Cam Ranh'),
            ('💬', 'Đặt dễ dàng', 'WhatsApp hoặc Telegram')],
    'catalog': 'Mẫu hoa và bảng giá', 'catalog_sub': 'Giá bằng VNĐ. Mọi mẫu đều có thể đổi màu theo ý bạn.',
    'cats': [('all', 'Tất cả'), ('roses', 'Hoa hồng'), ('tulips', 'Tulip'), ('hydr', 'Cẩm tú cầu'), ('lily', 'Hoa ly'), ('bouquet', 'Bó hoa')],
    'items': {
        'r25': ('25 bông hồng đỏ', 'Hồng Đà Lạt bông to kèm lá'),
        'tul_p': ('Tulip hồng, 10 cành', 'Nhẹ nhàng, hiếm ở Nha Trang'),
        'hydr3': ('Cẩm tú cầu, 3 bông', 'Bông nhập to — hồng, xanh hoặc trắng'),
        'r101': ('101 bông hồng', 'Bó hoa lớn đáng nhớ'),
        'lily_p': ('Ly hồng công chúa', 'Hoa ly thơm dịu'),
        'mix': ('Bó hoa lớn rực rỡ', 'Thủy tiên và hoa theo mùa'),
        'r15': ('15 bông hồng đỏ', 'Bó hoa gọn cho buổi hẹn'),
        'tul_w': ('Tulip trắng, 10 cành', 'Tinh khôi cho mọi dịp'),
        'hydr_mix': ('Cẩm tú cầu mix, 5 bông', 'Hồng, xanh và trắng'),
        'r51': ('51 bông hồng sen', 'Bó tròn gói sang trọng'),
        'lily_dbl': ('Hoa ly trắng', 'Bó ly thơm sum suê'),
        'green_hydr': ('Cẩm tú cầu trắng xanh', 'Bó hoa tươi mát'),
        'gerb': ('Đồng tiền trắng, 7 bông', 'Bông to, gói giấy'),
        'tana': ('Cúc tana', 'Bó cúc tana xinh xắn'),
        'star': ('Bó hoa xanh dương', 'Hoa xanh và vàng gói giấy xanh'),
    },
    'delivery': 'Giao hoa Nha Trang, Cam Ranh', 'delivery_sub': f'Mỗi ngày {HOURS}. Giao đến khách sạn, căn hộ, nhà hàng và nhà riêng.',
    'zones': {'center': 'Trung tâm Nha Trang', 'north': 'Phía Bắc (Hòn Chồng, Vĩnh Hòa)', 'west': 'Phía Tây (Vĩnh Hiệp, Vĩnh Thạnh)', 'south': 'Phía Nam (Vĩnh Trường, Phước Đồng)', 'camranh': 'Cam Ranh'},
    'free': 'miễn phí',
    'how': 'Cách đặt hoa', 'steps': [('Chọn mẫu', 'Trên trang này hoặc gửi ảnh mẫu'), ('Nhắn tin', 'Form bên dưới soạn sẵn tin nhắn WhatsApp/Telegram'), ('Nhận ảnh', 'Gửi ảnh bó hoa thật trước khi giao'), ('Nhận hoa', 'Giao tận khách sạn, căn hộ hoặc nhà hàng')],
    'pay': 'Thanh toán', 'pay_sub': 'Chuyển khoản hoặc tiền mặt khi nhận hoa.',
    'faq': 'Câu hỏi thường gặp',
    'faqs': [('Đặt hoa từ xa được không?', 'Được. Nhắn tin địa chỉ người nhận ở Nha Trang và giờ giao — thanh toán chuyển khoản, gửi ảnh sau khi giao.'),
             ('Có giao đến khách sạn không?', 'Có, mọi khách sạn và căn hộ ở Nha Trang, Cam Ranh.'),
             ('Giao nhanh không?', 'Giao trong ngày. Đơn gấp — nhắn tin để biết giờ chính xác.'),
             ('Vì sao giá rẻ hơn?', 'Chúng tôi lấy hoa trực tiếp từ vựa ở Nha Trang và Đà Lạt, nên mỗi mẫu rẻ hơn các shop khác 100.000 ₫.'),
             ('Có thể tự chọn mẫu không?', 'Có. Gửi ảnh mẫu hoặc ngân sách — chúng tôi cắm theo màu bạn thích.'),
             ('Có thiệp không?', 'Có, thiệp kèm lời chúc miễn phí.')],
    'form': 'Đặt hoa', 'form_sub': 'Điền thông tin — chúng tôi soạn sẵn tin nhắn, bạn chỉ cần bấm Gửi.',
    'f_item': 'Mẫu hoa', 'f_custom': 'Mẫu khác (mô tả trong tin nhắn)', 'f_date': 'Ngày', 'f_time': 'Giờ', 'f_addr': 'Địa chỉ hoặc khách sạn',
    'f_addr_ph': 'Ví dụ: Sheraton, phòng 1205', 'f_to': 'Tên người nhận', 'f_card': 'Lời chúc trên thiệp', 'f_card_ph': 'Chúc mừng sinh nhật!',
    'f_from': 'Tên của bạn', 'f_send_wa': 'Gửi qua WhatsApp', 'f_send_tg': 'Gửi qua Telegram',
    'f_hint': 'Telegram: nếu tin nhắn chưa hiện, nội dung đã được sao chép — chỉ cần dán.',
    'f_phone': 'Zalo / WhatsApp / Telegram của bạn', 'f_phone_ph': '0900 000 000 hoặc @username', 'f_lead': 'Gửi yêu cầu — chúng tôi sẽ nhắn lại',
    'f_ok': 'Đã gửi! Chúng tôi sẽ nhắn bạn trong 15 phút.', 'f_err': 'Gửi không được — hãy bấm WhatsApp hoặc Telegram.', 'f_need': 'Nhập số điện thoại hoặc Telegram để chúng tôi trả lời.',
    'm_hello': 'Xin chào! Tôi muốn đặt hoa.', 'm_item': 'Mẫu: ', 'm_date': 'Thời gian: ', 'm_addr': 'Địa chỉ: ', 'm_to': 'Người nhận: ', 'm_card': 'Thiệp: ', 'm_from': 'Người gửi: ',
    'contacts': 'Liên hệ đặt hoa', 'contacts_sub': 'Trả lời nhanh. Gửi ảnh mẫu bạn thích để được báo giá.',
    'credits': 'Ảnh: Pexels', 'wa_text': 'Xin chào! Tôi muốn đặt: ', 'approx_rub': False,
    'related': 'Xem thêm', 'home': 'Trang chủ',
},
}

# посадочные страницы под запросы (RU + EN; VI не продвигаем)
LANDINGS = {
'ru': [
    dict(slug='101-roza-nyachang', title='101 роза в Нячанге с доставкой — {p} | VietFlowers', h1='101 роза в&nbsp;Нячанге',
         desc='Букет из 101 розы с доставкой по Нячангу и Камрани в день заказа: {p}. Фото букета до отправки, открытка бесплатно, заказ в WhatsApp и Telegram.',
         price_key='r101', keys=['r101', 'r51', 'r25', 'r15'],
         text=['101 роза — главный подарок для предложения руки и сердца, годовщины или дня рождения. Собираем букет в день доставки из свежих далатских роз: красных, розовых, белых или микс.',
               'Цена у нас ниже, чем у других доставок Нячанга, и она указана прямо на сайте. Перед отправкой присылаем фото готового букета, а после вручения — фото с получателем, если попросите.'],
         faqs=[('Сколько весит букет из 101 розы?', 'Около 8–10 кг — курьер донесёт до номера или лобби.'), ('Можно другие цвета?', 'Да: красные, розовые, белые, кремовые или микс — напишите в заказе.')]),
    dict(slug='dostavka-cvetov-kamran', title='Доставка цветов в Камрань — отели и аэропорт | VietFlowers', h1='Доставка цветов в&nbsp;Камрань',
         desc='Цветы в отели Камрани (Movenpick, Radisson, Alma, Riviera и другие) и в аэропорт Камрань. Цены на сайте, фото до отправки, доставка в день заказа.',
         price_key=None, keys=['r25', 'tul_p', 'hydr3', 'r101'],
         text=['Камрань — это курортные отели в 40–50 минутах от Нячанга. Привозим цветы на ресепшен или лично гостю, договариваемся с отелем заранее.',
               'Доставка в Камрань дешевле, чем у конкурентов. Чтобы букет пришёл к нужному часу, напишите заранее — лучше утром в день доставки.'],
         faqs=[('Доставляете в аэропорт Камрань?', 'Да, встретим с цветами в зоне прилёта — напишите номер рейса.'), ('В какие отели возите?', 'Во все отели Камрани: Movenpick, Radisson Blu, Alma, Riviera, Duyen Ha и другие.')]),
    dict(slug='rozy-nyachang', title='Розы в Нячанге с доставкой — от 15 до 101 розы | VietFlowers', h1='Розы с доставкой в&nbsp;Нячанге',
         desc='Купить розы в Нячанге с доставкой: 15, 25, 51, 101 роза. Свежие далатские розы, цены на сайте, фото до отправки.',
         price_key='r15', keys=['r15', 'r25', 'r51', 'r101'],
         text=['Розы для букетов везут в Нячанг из Далата — это крупные свежие бутоны, которые стоят 5–7 дней. Собираем букет в день доставки.',
               'Можно выбрать готовый букет ниже или написать нам количество и цвет — посчитаем цену сразу.'],
         faqs=[('Сколько стоят розы в Нячанге?', 'Букет из 25 роз — {p25}, 101 роза — {p101}. Все цены на сайте.'), ('Сколько стоят розы?', 'Розы из Далата стоят 5–7 дней, если менять воду и подрезать стебли.')]),
    dict(slug='buket-na-den-rozhdeniya-nyachang', title='Букет на день рождения в Нячанге с доставкой | VietFlowers', h1='Цветы на день рождения в&nbsp;Нячанге',
         desc='Поздравить с днём рождения в Нячанге: букеты от {p} с доставкой в отель или домой, открытка с вашим текстом бесплатно. Заказ из России — оплата в рублях.',
         price_key='gerb', keys=['mix', 'tul_p', 'hydr_mix', 'lily_p', 'r25', 'gerb'],
         text=['Хотите поздравить близкого человека, который отдыхает или живёт в Нячанге? Выберите букет, напишите текст открытки — мы привезём в отель или домой в нужное время.',
               'Заказ из России оплачивается переводом в рублях. После вручения пришлём фото, чтобы вы знали, что всё получилось.'],
         faqs=[('Можно сделать сюрприз?', 'Да, курьер позвонит получателю только у двери или передаст через ресепшен.'), ('Добавите шарики или торт?', 'Напишите, что хотите добавить, — подскажем, что можем привезти.')]),
    dict(slug='cvety-v-otel-nyachang', title='Цветы в отель в Нячанге — доставка в номер | VietFlowers', h1='Цветы в&nbsp;отель в&nbsp;Нячанге',
         desc='Доставка цветов в отели Нячанга: на ресепшен или в номер к приезду гостя. Цены на сайте, фото до отправки, заказ в WhatsApp и Telegram.',
         price_key='gerb', keys=['r25', 'hydr3', 'lily_dbl', 'tul_w', 'r101', 'star'],
         text=['Возим цветы во все отели Нячанга: от небольших гостиниц до Sheraton, InterContinental и Vinpearl. Можно передать букет к заселению — договоримся с ресепшеном.',
               'Укажите название отеля, номер (если знаете) и имя гостя — остальное сделаем мы.'],
         faqs=[('Можно в номер к заселению?', 'Да, договоримся с отелем, чтобы букет ждал в номере.'), ('Если гостя нет в отеле?', 'Оставим на ресепшене и пришлём вам фото.')]),
],
'en': [
    dict(slug='101-roses-nha-trang', title='101 Roses in Nha Trang with delivery — {p} | VietFlowers', h1='101 roses in&nbsp;Nha&nbsp;Trang',
         desc='A 101-rose bouquet delivered in Nha Trang and Cam Ranh the same day: {p}. Photo before delivery, free card, order on WhatsApp or Telegram.',
         price_key='r101', keys=['r101', 'r51', 'r25', 'r15'],
         text=['101 roses is the classic gift for a proposal, an anniversary or a birthday. We make it on the day of delivery from fresh Da Lat roses — red, pink, white or mixed.',
               'Our price is lower than other Nha Trang florists and it is right here on the site. We send a photo of the bouquet before it leaves.'],
         faqs=[('How heavy is a 101-rose bouquet?', 'About 8–10 kg — the courier carries it to the room or lobby.'), ('Other colours?', 'Yes: red, pink, white, cream or mixed.')]),
    dict(slug='cam-ranh-flower-delivery', title='Flower delivery to Cam Ranh — resorts & airport | VietFlowers', h1='Flower delivery to&nbsp;Cam&nbsp;Ranh',
         desc='Flowers to Cam Ranh resorts (Movenpick, Radisson, Alma, Riviera…) and Cam Ranh airport. Prices online, photo before delivery, same day.',
         price_key=None, keys=['r25', 'tul_p', 'hydr3', 'r101'],
         text=['Cam Ranh resorts are 40–50 minutes from Nha Trang. We deliver to reception or to the guest in person and arrange it with the resort in advance.',
               'Delivery to Cam Ranh costs less than with other florists. Message us in the morning for same-day delivery.'],
         faqs=[('Do you deliver to Cam Ranh airport?', 'Yes, we can meet arrivals with flowers — send the flight number.'), ('Which resorts?', 'All Cam Ranh resorts: Movenpick, Radisson Blu, Alma, Riviera, Duyen Ha and more.')]),
    dict(slug='roses-nha-trang', title='Roses in Nha Trang with delivery — 15 to 101 roses | VietFlowers', h1='Roses delivered in&nbsp;Nha&nbsp;Trang',
         desc='Buy roses in Nha Trang with delivery: 15, 25, 51, 101 roses. Fresh Da Lat roses, prices online, photo before delivery.',
         price_key='r15', keys=['r15', 'r25', 'r51', 'r101'],
         text=['Roses come to Nha Trang from Da Lat — big fresh buds that last 5–7 days. We arrange your bouquet on the day of delivery.',
               'Pick a bouquet below or tell us the number and colour — we’ll quote right away.'],
         faqs=[('How much are roses in Nha Trang?', '25 roses — {p25}, 101 roses — {p101}. All prices are on the site.'), ('How long do they last?', '5–7 days with fresh water and trimmed stems.')]),
    dict(slug='birthday-flowers-nha-trang', title='Birthday flowers in Nha Trang with delivery | VietFlowers', h1='Birthday flowers in&nbsp;Nha&nbsp;Trang',
         desc='Send birthday flowers in Nha Trang: bouquets from {p} delivered to a hotel or home, free card with your message.',
         price_key='gerb', keys=['mix', 'tul_p', 'hydr_mix', 'lily_p', 'r25', 'gerb'],
         text=['Want to surprise someone staying or living in Nha Trang? Choose a bouquet, write the card — we deliver to the hotel or home at the right time.',
               'Ordering from abroad is easy: pay by transfer and we send a photo after the hand-over.'],
         faqs=[('Can it be a surprise?', 'Yes, the courier only calls at the door or leaves it at reception.'), ('Balloons or cake?', 'Tell us what you’d like to add and we’ll see what we can bring.')]),
    dict(slug='hotel-flower-delivery-nha-trang', title='Flowers to your hotel in Nha Trang | VietFlowers', h1='Flowers to a&nbsp;hotel in&nbsp;Nha&nbsp;Trang',
         desc='Flower delivery to Nha Trang hotels: at reception or in the room before arrival. Prices online, photo before delivery.',
         price_key='gerb', keys=['r25', 'hydr3', 'lily_dbl', 'tul_w', 'r101', 'star'],
         text=['We deliver to every hotel in Nha Trang, from small guesthouses to Sheraton, InterContinental and Vinpearl. Flowers can be waiting in the room at check-in — we arrange it with reception.',
               'Send the hotel name, room number (if you know it) and the guest’s name — we handle the rest.'],
         faqs=[('In the room at check-in?', 'Yes, we arrange it with the hotel.'), ('If the guest is out?', 'We leave it at reception and send you a photo.')]),
],
}


def vnd(x, lang):
    return f'{x:,}'.replace(',', '.' if lang == 'vi' else ' ') + ' ₫'


def approx(x, t):
    if t['lang'] == 'vi':
        return ''
    if not t['approx_rub']:
        return f'≈ ${x / USD:.0f}'
    return f'≈ {round(x / RUB, -1):,.0f}'.replace(',', ' ') + ' ₽ · $' + f'{x / USD:.0f}'


def tg_link():
    return f'https://t.me/{TG_USER}'


def wa_link(text=''):
    return f'https://wa.me/{WA_PHONE}' + (f'?text={quote(text)}' if text else '')


def esc(s):
    return html.escape(s, quote=True)


TG_SVG = '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M21.9 4.6 18.6 20c-.2 1.1-.9 1.4-1.8.9l-5-3.7-2.4 2.3c-.3.3-.5.5-1 .5l.4-5.1 9.2-8.3c.4-.4-.1-.6-.6-.2L6 13.6l-4.9-1.5c-1.1-.3-1.1-1.1.2-1.6l19.1-7.4c.9-.3 1.7.2 1.5 1.5z"/></svg>'
WA_SVG = '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M12 2a10 10 0 0 0-8.6 15.1L2 22l5-1.3A10 10 0 1 0 12 2zm5.8 14.2c-.2.7-1.4 1.3-2 1.4-.5.1-1.2.1-1.9-.1-.4-.1-1-.3-1.7-.6-3-1.3-4.9-4.3-5-4.5-.1-.2-1.2-1.6-1.2-3s.8-2.2 1-2.5c.3-.3.6-.4.8-.4h.6c.2 0 .4 0 .6.5l.9 2.1c.1.2.1.4 0 .5l-.3.5-.4.5c-.1.1-.3.3-.1.6.2.3.8 1.3 1.7 2.1 1.2 1 2.1 1.4 2.4 1.5.3.1.5.1.6-.1l.9-1.1c.2-.3.4-.2.7-.1l2 1c.3.1.5.2.5.3.1.2.1.8-.1 1.4z"/></svg>'


def btns(t, text, cls=''):
    return (f'<a class="btn wa{cls}" href="{esc(wa_link(text))}" target="_blank" rel="noopener nofollow">{WA_SVG}{t["wa"]}</a>'
            f'<a class="btn tg{cls}" href="{esc(tg_link())}" target="_blank" rel="noopener nofollow">{TG_SVG}{t["tg"]}</a>')


def card(t, code, key, root):
    cat = next(c for k, c, *_ in CATALOG if k == key)
    name, desc = t['items'][key]
    price = PRICE[key]
    ap = approx(price, t)
    return f'''<article class="card" data-cat="{cat}">
  <div class="ph"><img src="{root}img/{key}.webp" alt="{esc(name)} — {BRAND}" loading="lazy" width="600" height="800"></div>
  <div class="cb"><h3>{esc(name)}</h3><p>{esc(desc)}</p>
  <div class="pr"><b>{vnd(price, code)}</b>{f'<span>{ap}</span>' if ap else ''}</div>
  <button class="btn pick" data-item="{key}">{esc(t['order'])}</button></div>
</article>'''


def page(code, land=None):
    t = T[code]
    root = '../' * (t['path'].count('/') + (1 if land else 0))
    path = t['path'] + (land['slug'] + '/' if land else '')
    url = SITE + '/' + path
    fill = lambda s: s.format(p=vnd(PRICE.get(land and land['price_key'] or 'gerb', 0) if land else 0, code), p25=vnd(PRICE['r25'], code), p101=vnd(PRICE['r101'], code))
    title = fill(land['title']) if land else t['title']
    desc = fill(land['desc']) if land else t['desc']
    h1 = land['h1'] if land else t['h1']
    keys = land['keys'] if land else [k for k, *_ in CATALOG]
    faqs = ([(q, fill(a)) for q, a in land['faqs']] + t['faqs'][:3]) if land else t['faqs']
    cards = ''.join(card(t, code, k, root) for k in keys)
    zones = ''.join(f'<tr><td>{esc(t["zones"][z])}</td><td>{t["free"] if p is None else "+" + vnd(p, code)}</td></tr>' for z, p in ZONES)
    adv = ''.join(f'<li><span class="ic">{i}</span><b>{esc(a)}</b><small>{esc(b)}</small></li>' for i, a, b in t['adv'])
    steps = ''.join(f'<li><span class="n">{n}</span><b>{esc(a)}</b><small>{esc(b)}</small></li>' for n, (a, b) in enumerate(t['steps'], 1))
    faq_html = ''.join(f'<details><summary>{esc(q)}</summary><p>{esc(a)}</p></details>' for q, a in faqs)
    chips = '' if land else '<div class="chips">' + ''.join(f'<button class="chip{" on" if k == "all" else ""}" data-f="{k}">{esc(v)}</button>' for k, v in t['cats']) + '</div>'
    home = root + t['path']
    nav = ''.join(f'<a href="{"" if not land else home}#{a}">{esc(b)}</a>' for a, b in t['nav'])
    langs = ''.join(f'<a href="{root}{T[c]["path"]}" hreflang="{c}"{" aria-current=\"page\"" if c == code else ""}>{c.upper()}</a>' for c in T)
    if land:
        alts = ''
    else:
        alts = ''.join(f'<link rel="alternate" hreflang="{c}" href="{SITE}/{T[c]["path"]}">' for c in T) + f'<link rel="alternate" hreflang="x-default" href="{SITE}/">'
    opts = ''.join(f'<option value="{k}">{esc(t["items"][k][0])} — {vnd(PRICE[k], code)}</option>' for k, *_ in CATALOG) + f'<option value="">{esc(t["f_custom"])}</option>'
    related = ''
    if code in LANDINGS:
        links = ''.join(f'<a href="{root}{t["path"]}{l["slug"]}/">{l["h1"]}</a>' for l in LANDINGS[code] if not land or l['slug'] != land['slug'])
        related = f'<section class="panel related"><h2>{esc(t["related"])}</h2><div class="rel">{links}</div></section>'
    intro = ''.join(f'<p>{esc(p)}</p>' for p in land['text']) if land else ''
    lo, hi = min(PRICE.values()), max(PRICE.values())
    ld = [{'@context': 'https://schema.org', '@type': 'Florist', 'name': BRAND, 'url': SITE + '/' + t['path'], 'image': f'{SITE}/img/og.jpg',
           'description': desc, 'priceRange': f'{lo}–{hi} VND', 'currenciesAccepted': 'VND, RUB, USD', 'telephone': '+' + WA_PHONE,
           'address': {'@type': 'PostalAddress', 'addressLocality': 'Nha Trang', 'addressRegion': 'Khánh Hòa', 'addressCountry': 'VN'},
           'areaServed': ['Nha Trang', 'Cam Ranh'], 'openingHours': 'Mo-Su ' + HOURS.replace('–', '-'),
           'hasOfferCatalog': {'@type': 'OfferCatalog', 'name': t['catalog'], 'itemListElement': [
               {'@type': 'Offer', 'price': PRICE[k], 'priceCurrency': 'VND', 'availability': 'https://schema.org/InStock',
                'itemOffered': {'@type': 'Product', 'name': t['items'][k][0], 'description': t['items'][k][1], 'image': f'{SITE}/img/{k}.webp'}} for k in keys]}},
          {'@context': 'https://schema.org', '@type': 'FAQPage',
           'mainEntity': [{'@type': 'Question', 'name': q, 'acceptedAnswer': {'@type': 'Answer', 'text': a}} for q, a in faqs]}]
    if land:
        ld.append({'@context': 'https://schema.org', '@type': 'BreadcrumbList', 'itemListElement': [
            {'@type': 'ListItem', 'position': 1, 'name': t['home'], 'item': SITE + '/' + t['path']},
            {'@type': 'ListItem', 'position': 2, 'name': html.unescape(h1).replace('\xa0', ' '), 'item': url}]})
    js_t = {k: t[k] for k in ('m_hello', 'm_item', 'm_date', 'm_addr', 'm_to', 'm_card', 'm_from', 'f_hint', 'f_ok', 'f_err', 'f_need')}
    js_t['items'] = {k: t['items'][k][0] + ' — ' + vnd(PRICE[k], code) for k in PRICE}
    return f'''<!doctype html>
<html lang="{t['lang']}">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>{esc(title)}</title>
<meta name="description" content="{esc(desc)}">
<link rel="canonical" href="{url}">
{alts}
<meta property="og:type" content="website"><meta property="og:title" content="{esc(title)}"><meta property="og:description" content="{esc(desc)}">
<meta property="og:url" content="{url}"><meta property="og:image" content="{SITE}/img/og.jpg"><meta property="og:locale" content="{t['locale']}">
<meta name="theme-color" content="#2a0f1c">
<link rel="icon" href="data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 100 100'%3E%3Ctext y='.9em' font-size='90'%3E%F0%9F%8C%B8%3C/text%3E%3C/svg%3E">
<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Cormorant+Garamond:wght@500;600&family=Manrope:wght@400;600;700&display=swap&subset=cyrillic,vietnamese" rel="stylesheet">
<link rel="preload" as="image" href="{root}img/bg.jpg">
<link rel="stylesheet" href="{root}style.css">
<script type="application/ld+json">{json.dumps(ld, ensure_ascii=False)}</script>
</head>
<body>
<div class="bg" aria-hidden="true">
  <video autoplay muted loop playsinline preload="auto" poster="{root}img/bg.jpg"><source src="{root}img/bg.webm" type="video/webm"><source src="{root}img/bg.mp4" type="video/mp4"></video>
  <canvas id="petals"></canvas><div class="veil"></div>
</div>
<header class="top"><a class="logo" href="{home}">🌸 {BRAND}</a><nav>{nav}</nav><div class="langs">{langs}</div></header>
<main>
<section class="hero{' small' if land else ''}">
  {'' if land else f'<p class="badge">{esc(t["promise"])}</p>'}
  <h1>{h1}</h1>
  {intro if land else f'<p class="lead">{esc(t["lead"])}</p>'}
  <div class="cta"><a class="btn main" href="#order">{esc(t['cta'])}</a>{btns(t, t['wa_text'])}</div>
  <ul class="adv">{adv}</ul>
</section>
<section id="catalog" class="panel"><h2>{esc(t['catalog'])}</h2><p class="sub">{esc(t['catalog_sub'])}</p>
  {chips}<div class="grid">{cards}</div>{f'<p class="more"><a href="{home}#catalog">{esc(t["more"])} →</a></p>' if land else ''}</section>
<section id="order" class="panel order"><h2>{esc(t['form'])}</h2><p class="sub">{esc(t['form_sub'])}</p>
  <form id="of" autocomplete="on" onsubmit="return false">
    <label class="w2">{esc(t['f_item'])}<select id="o-item">{opts}</select></label>
    <label>{esc(t['f_date'])}<input id="o-date" type="date"></label>
    <label>{esc(t['f_time'])}<input id="o-time" type="time" step="1800"></label>
    <label class="w2">{esc(t['f_addr'])}<input id="o-addr" placeholder="{esc(t['f_addr_ph'])}"></label>
    <label>{esc(t['f_to'])}<input id="o-to"></label>
    <label>{esc(t['f_from'])}<input id="o-from" autocomplete="name"></label>
    <label class="w2">{esc(t['f_card'])}<textarea id="o-card" rows="2" placeholder="{esc(t['f_card_ph'])}"></textarea></label>
    <label class="w2">{esc(t['f_phone'])}<input id="o-phone" autocomplete="tel" placeholder="{esc(t['f_phone_ph'])}"></label>
    <input name="website" id="o-hp" tabindex="-1" autocomplete="off" style="position:absolute;left:-9999px" aria-hidden="true">
    <div class="w2 cta"><button class="btn wa" id="o-wa" type="button">{WA_SVG}{esc(t['f_send_wa'])}</button><button class="btn tg" id="o-tg" type="button">{TG_SVG}{esc(t['f_send_tg'])}</button><button class="btn main" id="o-lead" type="button">✉️ {esc(t['f_lead'])}</button></div>
    <p class="w2 hint" id="o-hint" hidden></p>
  </form></section>
<section id="delivery" class="panel"><h2>{esc(t['delivery'])}</h2><p class="sub">{esc(t['delivery_sub'])}</p><table class="zones">{zones}</table>
  <h3>{esc(t['pay'])}</h3><p class="sub">{esc(t['pay_sub'])}</p></section>
<section id="how" class="panel"><h2>{esc(t['how'])}</h2><ol class="steps">{steps}</ol></section>
<section id="faq" class="panel"><h2>{esc(t['faq'])}</h2>{faq_html}</section>
{related}
<section id="contacts" class="panel contacts"><h2>{esc(t['contacts'])}</h2><p class="sub">{esc(t['contacts_sub'])}</p>
  <div class="cta">{btns(t, t['wa_text'])}</div><p class="sub">WhatsApp {WA_SHOW} · Telegram @{TG_USER} · {HOURS}</p></section>
</main>
<footer><span>© {BRAND} · Nha Trang, Khánh Hòa</span><span>{langs}</span><span>{esc(t['credits'])}</span></footer>
<div class="bar">{btns(t, t['wa_text'])}</div>
<script>window.VF={json.dumps({'wa': WA_PHONE, 'tg': TG_USER, 'lead': LEAD_URL, 'lang': code, 't': js_t}, ensure_ascii=False)};</script>
<script src="{root}app.js" defer></script>
</body>
</html>
'''


if __name__ == '__main__':
    here = os.path.dirname(os.path.abspath(__file__))
    out = os.path.join(here, 'site')
    for name in ('style.css', 'app.js'):
        shutil.copy(os.path.join(here, 'src', name), os.path.join(out, name))
    urls = []
    for code, t in T.items():
        d = os.path.join(out, t['path'])
        os.makedirs(d, exist_ok=True)
        open(os.path.join(d, 'index.html'), 'w', encoding='utf-8').write(page(code))
        urls.append((t['path'], '1.0'))
        for land in LANDINGS.get(code, []):
            ld = os.path.join(d, land['slug'])
            os.makedirs(ld, exist_ok=True)
            open(os.path.join(ld, 'index.html'), 'w', encoding='utf-8').write(page(code, land))
            urls.append((t['path'] + land['slug'] + '/', '0.8'))
    open(os.path.join(out, 'robots.txt'), 'w').write(f'User-agent: *\nAllow: /\nSitemap: {SITE}/sitemap.xml\n')
    body = ''.join(f'<url><loc>{SITE}/{p}</loc><priority>{pr}</priority></url>' for p, pr in urls)
    open(os.path.join(out, 'sitemap.xml'), 'w', encoding='utf-8').write(
        f'<?xml version="1.0" encoding="UTF-8"?><urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">{body}</urlset>')
    for key, cat, bench, src, cost in CATALOG:
        print(f'{key:10} {bench:>10,} → {bench - DISCOUNT:>10,}  ({src}; закупка: {cost})')
    print(len(urls), 'страниц, готово:', out)
