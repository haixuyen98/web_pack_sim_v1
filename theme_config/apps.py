from django.apps import AppConfig


class ThemeConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'theme_config'
    depends_on = ['tenant']
    theme_color_templates = [
        {
            "title": "Mặc định",
            "main_color": "#206FEE", 
            "second_color": "#F0F0F0",
            "color_bg": "#FFFFFF",
            "text_color": "#3D444D",
            "text_highlight": "#FC5553",
            "color_bg_menu": "#E5E7EB",
            "color_text_menu": "#000000"
        },
        {
            "title": "Tươi mới",
            "main_color": "#E97A39", 
            "second_color": "#F0F0F0",
            "color_bg": "#FFFFFF",
            "text_color": "#3D444D",
            "text_highlight": "#16819C",
            "color_bg_menu": "#FEF9E0",
            "color_text_menu": "#000000"
        },
        {
            "title": "Rực rỡ",
            "main_color": "#DD1A21", 
            "second_color": "#F0F0F0",
            "color_bg": "#FFFFFF",
            "text_color": "#3D444D",
            "text_highlight": "#007A57",
            "color_bg_menu": "#FFF0F0",
            "color_text_menu": "#000000"
        },
        {
            "title": "Xanh mát",
            "main_color": "#187551", 
            "second_color": "#F0F0F0",
            "color_bg": "#FFFFFF",
            "text_color": "#3D444D",
            "text_highlight": "#FFAE00",
            "color_bg_menu": "#F0FFF4",
            "color_text_menu": "#000000"
        }
    ]
    font_family_templates = [
        {
            "font": "Inter"
        },
        {
            "font": "Roboto"
        },
        {
            "font": "Open Sans"
        },
        {
            "font": "Lato"
        },
        {
            "font": "Oswald"
        },
        {
            "font": "Montserrat"
        },
        {
            "font": "Source Sans Pro"
        },
    ]

    theme_config_default = {
        "seo": {
            "headScript": "",
            "description": "",
            "footerScript": ""
        },
        "color": {
            "color_bg": "#FFFFFF",
            "font_size": "16",
            "main_color": "#E97A39",
            "text_color": "#3D444D",
            "font_family": "Source Sans Pro",
            "second_color": "#F0F0F0",
            "color_bg_menu": "#FEF9E0",
            "text_highlight": "#16819C",
            "color_text_menu": "#000000"
        },
        "email": "mun@gmail.com",
        "banner": {
            "banner1": "/media/sim_galaxy/banner2.svg",
            "banner2": "/media/sim_galaxy/sim_uIXW93g.svg",
            "banner3": "/media/sim_galaxy/banner1_WyOiOLI.svg",
            "url_banner1": "https://simthanglong.vn/",
            "url_banner2": "https://simthanglong.vn/",
            "url_banner3": "",
            "title_banner1": "banner1",
            "title_banner2": "banner2",
            "title_banner3": "banner3"
        },
        "robots": "User-agent: *\nDisallow: /",
        "sidebar": [
            {
            "title": "SIM THEO NHÀ MẠNG",
            "content": "{% sidebar_telco_block %}",
            "is_hide": "0",
            "editable": "",
            "position": 1,
            "hide_title": ""
            },
            {
            "title": "SIM THEO GIÁ",
            "content": "{% sidebar_prices_block 'SIM THEO GIÁ' %}",
            "is_hide": "0",
            "editable": "",
            "position": 2,
            "hide_title": ""
            },
            {
            "title": "LOẠI SIM",
            "content": "{% sidebar_types_block 'LOẠI SIM'%}",
            "is_hide": "0",
            "editable": "",
            "position": 3,
            "hide_title": ""
            },
            {
            "title": "SIM THEO MỆNH",
            "content": "{% sidebar_fates_block 'SIM THEO MỆNH'%}",
            "is_hide": "0",
            "editable": "",
            "position": 4,
            "hide_title": ""
            },
            {
            "title": "TỪ KHOÁ PHỔ BIẾN",
            "content": "{% sidebar_tags_block 'TỪ KHOÁ PHỔ BIẾN'%}",
            "is_hide": "0",
            "editable": "",
            "position": 5,
            "hide_title": ""
            }
        ],
        "support": {
            "zalo": "https://zalo.me/2372820392814000301",
            "email": "doanapsim1@gmail.com",
            "title1": "Hotline hihi",
            "title2": "Tư vấn phong thủy",
            "twitter": "https://twitter.com/",
            "youtube": "https://www.youtube.com/",
            "facebook": "https://www.facebook.com/simdoanhnhandotvn",
            "hotline1": "0988.222.000",
            "hotline2": "1900.2222",
            "linkedin": "https://www.linkedin.com/",
            "messenger": "https://www.messenger.com/",
            "business_hours": "07:30 - 21:30",
            "download_and_certification": "<div class=\"description\">\r\n<div class=\"description__title-head--certification\"><a class=\"description__title-head\" href=\"#\" title=\"CÔNG TY CỔ PHẦN SIM.VN\">TẢI ỨNG DỤNG </a></div>\r\n\r\n<div class=\"description__img-app\"><a href=\"#\" title=\"Google Play\"><img alt=\"google-play\" src=\"/static/galaxy/images/footer/google-play.svg\" /> </a> <a href=\"#\" title=\"App Store\"> <img alt=\"app-store\" src=\"/static/galaxy/images/footer/app-store.svg\" /> </a></div>\r\n\r\n<div class=\"description__title-head--certification\"><a class=\"description__title-head\" href=\"#\" title=\"CHỨNG NHẬN KẾT NỐI\">CHỨNG NHẬN KẾT NỐI</a></div>\r\n<a class=\"description__img-app\" href=\"#\" title=\"Bộ công thương\"><img alt=\"Bộ công thương\" class=\"img-bct\" src=\"/static/galaxy/images/footer/bocongthuong.svg\" /><img alt=\"Thành lập từ\" class=\"img-tlt\" src=\"/static/galaxy/images/footer/thanhlaptu.svg\" /><img alt=\"Cục sở hữu trí tuệ\" class=\"img-cshtt\" src=\"/static/galaxy/images/footer/cucsohuutritue.svg\" /> </a></div>\r\n"
        },
        "menu_top": [
            {
            "link": "/",
            "title": "TRANG CHỦ",
            "position": 1
            },
            {
            "link": "/sim-tra-gop",
            "title": "SIM TRẢ GÓP",
            "position": 2
            },
            {
            "link": "/dinh-gia-sim",
            "title": "ĐỊNH GIÁ SIM",
            "position": 3
            },
            {
            "link": "/dat-sim-theo-yeu-cau",
            "title": "ĐẶT SIM THEO YÊU CẦU",
            "position": 4
            },
            {
            "link": "/tin-tuc/camketbanhang",
            "title": "CAM KẾT BÁN HÀNG",
            "position": 5
            },
            {
            "link": "/tin-tuc/hng-dn-tim-sim",
            "title": "HƯỚNG DẪN TÌM SIM",
            "position": 6
            },
            {
            "link": "/tin-tuc/giao-sim",
            "title": "GIAO SIM ",
            "position": 7
            },
            {
            "link": "/tin-tuc/",
            "title": "TIN TỨC",
            "position": 8
            }
        ],
        "footer_link": [
            {
            "link": "/tin-tuc/dieu-khoan-va-dieu-kien-giao-dich/",
            "title": "Điều khoản và điều kiện giao dịch"
            },
            {
            "link": "/tin-tuc/chinh-sach-bao-mat",
            "title": "Chính sách bảo mật"
            },
            {
            "link": "/tin-tuc/cach-mua-sim-va-thanh-toan/",
            "title": "Cách mua sim và thanh toán"
            },
            {
            "link": "/tin-tuc/chinh-sach-doi-tra",
            "title": "Chính sách đổi trả"
            },
            {
            "link": "/tin-tuc/lien-he",
            "title": "Liên hệ"
            },
            {
            "link": "https://galaxy.simthanglong.net/sitemap.xml",
            "title": "Sitemap"
            }
        ],
        "sim_api_url": "https://appsim-api.simthanglong.net",
        "order_webhook": "",
        "notification_url": ""
    }