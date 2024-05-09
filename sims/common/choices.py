from django.db import models

PACK_CHOICES = (
    (1, "Trả trước"),
    (2, "Trả sau"),
)
MIN_PRICES_RANGE = (
((0, '0'), (500000, '500.000'), (1000000, '1.000.000'), (3000000, '3.000.000'), (5000000, '5.000.000'), (10000000, '10.000.000'), (30000000, '30.000.000'), (50000000, '50.000.000'), (80000000, '80.000.000'), (100000000, '100.000.000'), (150000000, '150.000.000'), (200000000, '200.000.000'), (300000000, '300.000.000'), (500000000, '500.000.000'), (1000000000, '1.000.000.000'))
)
MAX_PRICES_RANGE= (
((500000, '500.000'), (1000000, '1.000.000'), (3000000, '3.000.000'), (5000000, '5.000.000'), (10000000, '10.000.000'), (30000000, '30.000.000'), (50000000, '50.000.000'), (80000000, '80.000.000'), (100000000, '100.000.000'), (150000000, '150.000.000'), (200000000, '200.000.000'), (300000000, '300.000.000'), (500000000, '500.000.000'), (1000000000, '1.000.000.000'), (5000000000, '5.000.000.000'), (10000000000, '10.000.000.000'), (15000000000, '15.000.000.000'), (20000000000, '20.000.000.000'), (25000000000, '25.000.000.000'), (30000000000, '30.000.000.000'), (35000000000, '35.000.000.000'), (40000000000, '40.000.000.000'), (45000000000, '45.000.000.000'), (50000000000, '50.000.000.000'), ('', '(không có)'))
)
# id sim tra gop
CATE_INSTALLMENT_ID=200
SIM_PRICE_DISPLAY_FIELD='pb'

CATEGORY_CHOICES = (
    (67, "Sim Lặp kép"),
    (68, "Sim Tứ quý"),
    (70, "Sim Ông địa"),
    (71, "Sim Đôi"),
    (72, "Sim Thần tài"),
    (73, "Sim Lộc phát"),
    (74, "Sim Taxi"),
    (76, "Sim Dễ nhớ"),
    (77, "Sim Năm sinh"),
    (78, "Sim Số độc"),
    (79, "Sim Gánh đảo"),
    (80, "Sim Tam hoa"),
    (81, "Sim Tiến lên"),
    (82, "Sim VIP"),
    (84, "Sim tự chọn"),
    (86, "Số máy bàn"),
    (99, "Sim Ngũ Quý"),
    (100, "Sim Lục Quý"),
    (102, "Tam hoa kép"),
    (103, "Sim Tứ Quý Giữa"),
    (104, "Sim Ngũ Quý Giữa"),
    (105, "Sim Lục Quý Giữa"),
    (106, "Sim Đầu cổ"),
    (110, "Sim hợp mệnh Thủy"),
    (111, "Sim hợp mệnh Hỏa"),
    (112, "Sim hợp mệnh Mộc"),
    (113, "Sim hợp mệnh Thổ"),
    (114, "Sim hợp mệnh Kim"),
    (115, "Sim Đại Cát"),
    (116, "Sim Cát"),
    (117, "Sim Bình"),
    (118, "Sim Hung"),
    (119, "Sim Đại Hung"),
    (120, "Sim Kép"),
    (121, "Sim Kép 3"),
    (122, "Sim Kép 4"),
    (123, "Sim Lặp"),
    (124, "Sim Lặp 3"),
    (125, "Sim Lặp 4"),
    (126, "Sim Taxi Lặp 3"),
    (127, "Sim Taxi Lặp 2"),
    (128, "Sim Taxi Lặp 4"),
    (CATE_INSTALLMENT_ID, "Sim trả góp"),
)

NHA_MANG_CHOICES = (
    (1, "viettel"),
    (2, "vinaphone"),
    (3, "mobifone"),
    (4, "vietnamobile"),
    (5, "gmobile"),
    (7, "mayban"),
    (8, "itelecom"),
    (9, "wintel"),
)
SORTING_CHOICES = (
    (0, "Ngẫu nhiên"),
    (-1, "Tăng dần"),
    (1, "Giảm dần"),
)

class INSTALLMENT_TYPE_CHOICES(models.IntegerChoices):
    PERCENT = 1, "% / tháng",
    VND = 2, "đồng / triệu",

class STATUS_CHOICES(models.IntegerChoices):
    NEW = 1, "Mới đặt"
    PROCESSING = 2, "Đang xử lý"
    DELIVERING = 3, "Đang giao"
    DELIVERED = 4, "Đã giao"
    COMPLETED = 5, "Hoàn tất"
    FAIL = 6, "Thất bại"
    CANCELED = 7, "Hủy",
#Trang thai thu chi của bảng AccountReceive
class STATUS_AR_CHOICES(models.IntegerChoices):
    NEW = 1, "Tạm tính"
    PAID = 2, "Đã thanh toán"
class TYPE_AR_CHOICES(models.IntegerChoices):
    THO = 1, "Thợ"
    KH = 2, "KH"

class PAY_METHOD_CHOICES(models.IntegerChoices):
    CASH = 1, "Tiền mặt"
    BANK = 2, "Chuyển khoản"

class REQUEST_CHOICES(models.IntegerChoices):
    COMMON = 1, "Đơn thường"
    REQUEST = 2, "Yêu cầu"
    PRESENT = 3, "Đơn tặng"
    INSTALLMENT = 4, "Đơn trả góp"
class STORE_TYPES(models.IntegerChoices):
    KHO_MIX = 1, "Hỗn hợp (Kho Sim và Kho AppSim)"
    KHO_APPSIM = 2, "Kho App Sim"
    KHO_SIM = 3, "Kho SIM"

DEFAULT_STORE_TYPE = STORE_TYPES.KHO_MIX

INSTALLMENT_PAYMENT_CHOICES = (
    (10, "10%"),
    (20, "20%"),
    (30, "30%"),
    (40, "40%"),
    (50, "50%"),
    (60, "60%"),
    (70, "70%"),
    (80, "80%"),
    (90, "90%"),
)

INSTALLMENT_TERM_CHOICES = (
    (3, "3 tháng"),
    (6, "6 tháng"),
    (9, "9 tháng"),
    (12, "12 tháng"),
    (15, "15 tháng"),
    (18, "18 tháng"),
    (21, "21 tháng"),
    (24, "24 tháng"),
)

DATE_FILTER_CHOICES = (
    ('today', 'Hôm nay'),
    ('yesterday', 'Hôm qua'),
    ('last_7_days', '7 ngày trước'),
    ('this_month', 'Tháng hiện tại'),
    ('last_6_months', '6 tháng trước'),
    ('this_year', 'Trong năm'),
    ('longer', 'Lâu hơn'),
)

TRANSPORT_CHOICES = (
    (0, "Tự giao dịch"),
    (1, "Giao dịch hộ"),
    (2, "COD"),
    (3, "Cấp lại sim"),
)

class STATUS_PAY_CHOICES(models.IntegerChoices):
    UN_PAIDED= 0, "Chưa thanh toán",
    PAIDING = 1, "Đang thanh toán",
    PAID = 2, "Đã thanh toán"



def get_label_from_value(choices, value):
    for choice_value, choice_label in choices:
        if choice_value == value:
            return choice_label
    return value