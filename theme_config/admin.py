from django.contrib import admin
from django.urls import path
from django.template.response import TemplateResponse
from django.shortcuts import redirect
from django.urls import reverse
from django.contrib.auth.views import LoginView
from tenant.models import TenantTemplates
import uuid 
import json
from sims.common.choices import SIM_PRICE_DISPLAY_FIELD, STORE_TYPES
from sims.services.sim_service import getSims, getSellerInfo, getPhoneInfo
from sims.services.helpers import getSimUrlFilter
from core.helpers import autoClearCache
from .utils import loginAppsim
from django.utils import timezone
# Register your models here.
class ThemeConfigAdminSite(admin.AdminSite):
    def each_context(self, request):
        context = super().each_context(request)
        custom_menu_item = {
            'name': 'Custom Item',
            'url': reverse('admin:theme_general_settings'),
        }
        context['custom_menu_item'] = custom_menu_item
        return context
    def get_app_list(self, request, app_label=None):
        app_list = super().get_app_list(request, app_label)
        for app in app_list:
            if app['app_label'] == 'sims':
                # Add the custom menu item to the existing app
                custom_menu = {
                    'name': 'Cài đặt kho',
                    "object_name": "sims",
                    'admin_url': reverse('admin:theme_store_config'),
                    'view': request.user.has_perm('settings.view_setting'),
                }
                custom_menu1 = {
                    'name': 'Tuỳ chỉnh giá',
                    "object_name": "theme_customize_price",
                    'admin_url': reverse('admin:theme_customize_price'),
                    'view': request.user.has_perm('settings.view_setting'),
                }
                custom_menu2 = {
                    'name': 'Tìm số trong kho',
                    "object_name": "theme_search_store",
                    'admin_url': reverse('admin:theme_search_store'),
                    'view': request.user.has_perm('settings.view_setting'),
                }
                app['models'].append(custom_menu)
                app['models'].append(custom_menu1)
                app['models'].append(custom_menu2)

        if request.user.has_perm('settings.view_setting'):
            app_list.append({
                'name': 'Settings',
                'app_label': 'theme_config',
                'models': [{
                    'name': 'Cài đặt chung',
                    "object_name": "theme_general_settings",
                    'admin_url': reverse('admin:theme_general_settings'),
                    'view': request.user.has_perm('settings.view_setting'),
                }, {
                    'name': 'Cài đặt theme',
                    "object_name": "theme_settings",
                    'admin_url': reverse('admin:theme_settings'),
                    'view': request.user.has_perm('settings.view_setting'),
                }]
            })
        return app_list
    def get_urls(self):
        return [
            path(
                "general-settings/",
                self.admin_view(self.general_settings),
                name="theme_general_settings",
            ),
            path(
                "settings/",
                self.admin_view(self.template_list_view),
                name="theme_settings",
            ),
            path(
                "store_config/",
                self.admin_view(self.template_store_config),
                name="theme_store_config",
            ),
            path(
                "customize_price/",
                self.admin_view(self.template_customize_price),
                name="theme_customize_price",
            ),
            path(
                'search_store/',
                self.admin_view(self.template_search_store),
                name="theme_search_store",
            ),
        ] + super().get_urls()
        
    def template_store_config(self, request):
        tenant = request.tenant
        if request.method == 'POST':
            telco_rates = {}
            for key, value in request.POST.items():
                if key.startswith('telco_rates.'):
                    field_name = key.split('telco_rates.')[1]
                    telco_rates[field_name] = value
            is_only_sale_stores = request.POST.get('is_only_sale_stores', '')
            priority_stores = request.POST.get('priority_stores', '')
            store_ignores = request.POST.get('store_ignores', '')
            sim_price_display_field = request.POST.get('sim_price_display_field', '')
            sim_price_display_field = sim_price_display_field if sim_price_display_field else SIM_PRICE_DISPLAY_FIELD
            tenant.config['sim_api_url'] = request.POST.get('sim_api_url', '')
            tenant.config["store_config"] = {
                'priority_stores': [],
                'telco_rates': telco_rates,
                'store_ignores': store_ignores,
                'gte': request.POST.get('gte', ''),
                'lte': request.POST.get('lte', ''),
                'd': request.POST.get('d', ''),
                'l_sec_gte': request.POST.get('l_sec_gte', 60),
                'is_only_sale_stores': is_only_sale_stores,
                'priority_stores': priority_stores,
                'store_type': request.POST.get('store_type', ''),
                'sim_price_display_field': sim_price_display_field,
                'numbers_hidden': request.POST.get('numbers_hidden', '')
            }
            tenant.save()
        context = {
            'theme_folder': tenant.theme_folder,
            'tenant': tenant,
            "page_name": "Cài đặt kho",
            'config': tenant.config,
            'store_config': tenant.config['store_config'] if 'store_config' in tenant.config else {},
            "app_list": self.get_app_list(request),
            "current_time": int(timezone.now().timestamp()),
            **self.each_context(request),
        }
        return TemplateResponse(request, f"admin/{tenant.type}/theme_store_config.html", context)
    def template_list_view(self, request):
        tenant = request.tenant
        theme_type = tenant.type
        base_url = request.build_absolute_uri('/')[:-1]

        context = {
            'items': TenantTemplates.objects.filter(tenant_type=tenant.type),
            'theme_folder': tenant.theme_folder,
            'theme_type': theme_type,
            "page_name": "Cài đặt theme",
            "base_url": base_url,
            "app_list": self.get_app_list(request),
            **self.each_context(request),
        }
        if request.method == 'POST':
            tenant.theme_folder = request.POST.get('template_name')
            autoClearCache(request)
            tenant.save()
            return redirect('admin:theme_settings')
        return TemplateResponse(request, f"admin/{tenant.type}/theme_template_list.html", context)
    
    def general_settings(self, request):
        if request.user.has_perm('settings.view_setting'):
            tenant = request.tenant
            customize_all = tenant.config.get('webhook_list_url')
            if customize_all is None:
                customize_all = []

            if request.method == 'POST':
                uuid_str = request.POST.get('uuid')
                del_uuid = request.POST.get('del_uuid')
                if uuid_str:
                    content = request.POST.get('content')

                    for item in customize_all:
                        if item['uuid'] == uuid_str:
                            if request.POST.get('webhook_url'):
                                item['webhook_url'] = request.POST.get('webhook_url')
                            if content:
                                item['content'] = content
                            break
                elif del_uuid == '' and uuid_str == '':
                    webhook_url = request.POST.get('webhook_url')
                    content = request.POST.get('content')

                    if request.POST.get('webhook_url'):
                        webhook_config_item = {
                            'uuid': str(uuid.uuid4())[:8],
                            'webhook_url': webhook_url,
                        }
                        if content is not None:
                            webhook_config_item['content'] = content
                        customize_all.append(webhook_config_item)
                else:
                    customize_all = [item for item in customize_all if item['uuid'] != del_uuid]
                tenant.config["webhook_list_url"] = customize_all
                post_data = request.POST.dict()
                # remove excessive configs
                keys_to_remove = {'csrfmiddlewaretoken', 'uuid', 'webhook_url', 'content', 'del_uuid', 'webhook_phone', 'webhook_password'}

                if 'logout' in post_data:
                    del post_data['logout']
                for key, value in post_data.items():
                    if key not in keys_to_remove:
                        tenant.config[key] = value

                loginAppsim(request)
                autoClearCache(request)
                tenant.save()
                return redirect('admin:theme_general_settings')

            context = {
                'theme_folder': tenant.theme_folder,
                'tenant': tenant,
                'config': tenant.config,
                'customize_webhook_url': customize_all,
                "page_name": "Cài đặt chung",
                "app_list": self.get_app_list(request),
                **self.each_context(request),
            }
            return TemplateResponse(request, f"admin/{tenant.type}/general_settings.html", context)
        else:
            # Handle unauthorized access
            return self.login_view(request)
    def template_customize_price(self, request):
        tenant = request.tenant
        customize_all = tenant.config.get("appsim_adjust_prices")
        customize_length = len(customize_all)
        list_rounding = [10, 20, 30, 40, 50, 100, 500, 1000]
        # create customize price
        if request.method == "POST":
            if customize_all is None:
                customize_all= []
            uuid_str = request.POST.get('uuid')
            del_uuid = request.POST.get('del_uuid')
            if uuid_str:
                for item in customize_all:
                    if item['uuid']==uuid_str:
                        item['price_from'] = request.POST.get('price_from','0').replace('.','')
                        item['price_to'] = request.POST.get('price_to').replace('.','')
                        item['repair'] = request.POST.get('repair')
                        item['percent'] = request.POST.get('percent')
                        break
            elif del_uuid=='' and uuid_str=='':
                customize_all.append({
                    'uuid': str(uuid.uuid4())[:8],
                    'price_from': request.POST.get('price_from').replace('.',''),
                    'price_to': request.POST.get('price_to').replace('.',''),
                    'repair': request.POST.get('repair'),
                    'percent': request.POST.get('percent'),
                })
            else:
                customize_all = [item for item in customize_all if item['uuid'] != del_uuid]
            tenant.config["appsim_adjust_prices"] = customize_all
            tenant.save()
            return redirect('admin:theme_customize_price')

        context = {
            'theme_folder': tenant.theme_folder,
            "page_name": "Tuỳ chỉnh giá",
            "customize_price_list": customize_all,
            "customize_length": customize_length,
            "list_rounding": list_rounding,
            "app_list": self.get_app_list(request),
            "current_time": int(timezone.now().timestamp()),
            **self.each_context(request),
        }
        return TemplateResponse(request, f"admin/{tenant.type}/theme_customize_price.html", context)

    def template_search_store(self, request):
        tenant = request.tenant
        list_rounding = [10, 20, 30, 40, 50, 100, 500, 1000]
        paramsObj= {
            'store_type': STORE_TYPES.KHO_MIX,
            'limit': 50
        }
        data_form = request.GET
        path = f"/{data_form['path']}/" if data_form.get('path', None) else '/'
        paramsObj['p'] = data_form.get('p',1)
        paramsObj['q'] = data_form.get('q', '')
        filterObj = getSimUrlFilter(path, paramsObj)
        filterObj['from_admin'] = True
        search_store_list = []
        meta_data = {}
        agencies = {}
        agency_ids = []
        phones = ""
        phonesInfo = {}

        if paramsObj['q']:
            data = getSims(filterObj, tenant, request, '/search/query3-not-mix')
            if 'data' in data:
                search_store_list = data['data']
            if 'meta' in data:
                meta_data = data['meta']

            for item in search_store_list:
                if 'highlight' in item and item['highlight']:
                    agency_ids.extend(map(str, item['s3']))
                    phones = phones + "," + item['id']
            sellers = getSellerInfo(agency_ids)
            phonesInfo = getPhoneInfo(phones, tenant)
            if sellers:
                for seller in sellers:
                    seller_id = seller['agency_id']
                    if seller_id is not None:
                        agencies[int(seller_id)] = seller

        context = {
            'request': request,
            'meta_data': meta_data,
            'theme_folder': tenant.theme_folder,
            "page_name": "Tìm số trong kho",
            "search_store_list": search_store_list,
            "agencies": agencies,
            "list_rounding": list_rounding,
            "app_list": self.get_app_list(request),
            "title": filterObj.get("title", 'Tìm số trong kho'),
            "phonesInfo": phonesInfo,
            "current_time": int(timezone.now().timestamp()),
            **self.each_context(request),
        }
        return TemplateResponse(request, f"admin/sims/simstore/sim_type/theme_search_store.html", context)

    def login_view(self, request):
        return LoginView.as_view(template_name='admin/login.html')(request)

admin.site.__class__ = ThemeConfigAdminSite