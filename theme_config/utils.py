import os
from appsim.services.appsim_service import appsimLogin
from django.contrib import messages

def loginAppsim(request):
    tenant = request.tenant
    if 'logout' in request.POST and 'appsim_account' in tenant.config:
        del tenant.config['appsim_account']
        for url in tenant.config['webhook_list_url']:
            if url['uuid'] == '01appsim':
                tenant.config['webhook_list_url'].remove(url)
    else:
        appsim_url = os.environ.get('APPSIM_AGENCY_API_URL', 'https://api.appsim.net')
        if appsim_url:
            appsim_login = appsimLogin(request, appsim_url)
            if appsim_login:
                appsim_account = appsim_login['data']['user']['user']
                tenant.config['appsim_account'] = {
                    'appsim_user_id': appsim_account['user_id'],
                    'appsim_agency_id': appsim_account['agency_id'],
                    'appsim_name': appsim_account['name'],
                    'appsim_phone': appsim_account['phone'],
                }
                # check if `'uuid': '01appsim'` exists in webhook list then not append to webhook list
                exists = any(item.get('uuid') == '01appsim' for item in tenant.config['webhook_list_url'])
                if not exists:
                    tenant.config['webhook_list_url'].append({
                        'uuid': '01appsim',
                        'content': '{{"message_sms": "Khach hang da dat mua sim {sim}", "title": "Bạn có đơn hàng đặt mua sim {sim}", "short_content": "Khách hàng đã đặt mua sim {sim}", "content": "Khách hàng đã đặt mua sim {sim}"}}',
                        'webhook_url': appsim_url + '/simvn/v1/api/utils/send-notification-webgoi',
                    })
