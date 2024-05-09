from django.db import models

verifyUserInfoEndpoint = '/api/merchant/v1/session/verify'
createTransactionEndpoint = '/api/merchant/v1/transaction'
MY_WEBHOOK_TOKEN = 'pCxLpmdCe3mDuf4qT'

telco_fee_ck = {
    1: {
        160000: [
            'Miễn phí 20 phút đầu tiên/cuộc gọi nội mạng, 60 phút thoại ngoại mạng, 60 SMS nội mạng, 3GB tốc độ cao/ngày'
        ],
        120000: [
            'Miễn phí 20 phút/cuộc gọi nội mạng',
            '50 phút ngoại',
            '1,5Gb/ngày',
        ]
    }, 
    2: {
        99000: [
            'Ưu đãi 1500 phút nội mạng VNP (D99V)',
            '30 phút ngoại mạng',
            '1GB/ngày + MyTV OTT',
        ],
        149000: [
            'Ưu đãi 1500 phút nội mạng VNP (D149V)',
            '100 phút gọi ngoại mạng',
            '2GB/ngày + MyTV OTT',
        ],
        249000: [
            'Ưu đãi 2000 phút VNP(TG249)',
            '200p ngoại mạng',
            '2GB/ngày  + MyTV OTT',
        ],
        299000: [
            'Ưu đãi 3000 phút VNP',
            '200p ngoại mạng',
            '2GB/ngày + MyTV OTT',
        ],
        399000: [
            'Ưu đãi 4000p VNP(D399V)',
            '300p ngoại mạng',
            '3GB/ngày',
        ],
    },
    4: {
        0: [
            'Khuyến mại 4GB/ngày',
            'Số tiền cam kết được dùng để gọi nội mạng, ngoại mạng trong tháng',
        ],
        121000: [
            'Khuyến mại 4GB/ngày',
            'Số tiền cam kết được dùng để gọi nội mạng, ngoại mạng trong tháng',
        ]
    },
    8: {
        77000: [
            'Miễn phí cuộc gọi dưới 20 phút nội mạng vinaphone, itel miễn phí',
            'Miễn phí 60 SMS nội mạng',
            '3GB/ngày',
            'Gọi ngoại mạng 690 đồng/phút'
        ],
        99000: [
            '100 phút gọi nội mạng vinaphone, itel miễn phí',
            '20GB tốc độ cao',
            '1GB/ngày tối đa',
        ],
        149000: [
            '1000 phút gọi nội mạng vinaphone, itel miễn phí',
            '25GB tốc độ cao (hết lưu lượng  băng thông về 128/64Kbps)',
            '3GB/ngày tối đa',
            'Gọi ngoại mạng 1,100 đồng/phút',
        ],
        199000: [
            '1000 phút gọi nội mạng vinaphone, itel miễn phí',
            '30GB tốc độ cao (hết lưu lượng băng thông về 128/64Kbps)',
            '5GB/ngày tối đa',
        ],
    }
}

class SOURCE_CHOICES(models.TextChoices):
    MB = 'mb', "MB"

class TRANS_STATUS_CHOICES(models.TextChoices):
    MB = 'mb', "MB"
    PENDING = 'PENDING', 'Đang chờ',
    MOVED_TO_ORDER = 'MOVED_TO_ORDER', 'Chuyển đơn hàng',
    PAID = 'PAID', 'Đã thanh toán',
    FAILED = 'FAILED', 'Đã huỷ',
    PUSH_PENDING='PUSH_PENDING', 'Đã push đơn pending'
    DELETED = 'DELETED', 'Đã xoá'
