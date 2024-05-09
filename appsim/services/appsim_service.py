import requests
import json
from django.contrib import messages

def appsimLogin(request=None, webhook_url=None):
    login_api_url = f"{webhook_url}/v1/api/authen/qlbs/login"
    notification_api_url = f"{webhook_url}/simvn/v1/api/utils/send-notification-webgoi"
    phone = request.POST.get('webhook_phone')
    password = request.POST.get('webhook_password')
    data = {'phone': phone, 'password': password}
    try:
        response = requests.post(login_api_url, data=data)
        if response.status_code == 200:
            api_data = response.json()
            # send notification about logging in
            if api_data['data']:
                agency_id = api_data['data']['user']['user']['agency_id']
                content_data = {
                    'user_id': api_data['data']['user']['user']['user_id'],
                    'common_type': 40,
                    'send_sms': False,
                    'message_sms': f"Nguoi dung {agency_id} da dang nhap vao he thong",
                    'title': f"Đăng nhập",
                    'short_content': f"Người dùng {agency_id} đã đăng nhập vào hệ thống",
                    'content': f"Người dùng {agency_id} đã đăng nhập vào hệ thống",
                }
                try:
                    response = requests.post(notification_api_url, data=content_data)
                    if response.status_code == 200:
                        print(response.json())
                    else:
                        print('Failed to send notification')
                except:
                    print('Error:', e)
                return api_data
            else:
                messages.warning(request, 'Đăng nhập thất bại.')
                return None
        else:
            return None
    except requests.exceptions.RequestException as e:
        messages.warning(request, f'Có lỗi xảy ra trong quá trình đăng nhập.')
        return None
