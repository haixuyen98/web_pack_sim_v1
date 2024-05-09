from django.shortcuts import render
from tenant.forms import TenantRegisterForm
from django.contrib.auth.models import User
from tenant.models import Tenant, Domain, TenantTemplates
import uuid 
from django_tenants.utils import remove_www
from datetime import datetime, timedelta
from django.db import connection
import os

# Create your views here.
def index(request):
    context = {
       
    }
    return render(request, f'main_site/index.html', context)

def register_view(request):
    tenant_templates = TenantTemplates.objects.all()
    response_message = {'status': False, 'message': ''}
    main_site_url = os.environ.get('MAIN_SITE_BASE_URL', 'appsim.com.vn')
    if request.method == 'POST':
        form = TenantRegisterForm(request.POST)
        if form.is_valid():
            try:
                # Process the form data
                form_data = form.cleaned_data
                domain_prefix = form_data.get('domain_prefix')
                # Kiểm tra xem domain_prefix đã tồn tại trong cơ sở dữ liệu chưa
                existing_domain = Domain.objects.filter(domain__icontains=domain_prefix).first()
                if existing_domain:
                    response_message['message'] = "Tên domain đã tồn tại. Vui lòng chọn tên domain khác."
                else:
                    tenant_type = form_data.get('type')
                    source_tenant = Tenant.objects.filter(type=tenant_type, is_template=True, is_default=True).first()
                    if source_tenant:
                        uuid_str = str(uuid.uuid4())
                        uuid_str = uuid_str[:8]
                        schema_name = f'{source_tenant.type}_{uuid_str}'
                        source_tenant.clone_schema(schema_name)
                        user = User.objects.get(username='admin')
                        if user:
                            obj = form.save(commit=False)
                            obj.schema_name = schema_name
                            obj.theme_config = source_tenant.theme_config
                            obj.config = source_tenant.config
                            obj.type = source_tenant.type
                            obj.dns_record = uuid.uuid4()
                            obj.is_template = False
                            obj.is_default = False
                            obj.paid_until = datetime.now().date() + timedelta(days=15)
                            obj.theme_folder = source_tenant.theme_folder
                            obj.user = user
                            form.save_m2m() # Save ManyToManyField relationships if any
                            obj.save()
                            
                            domain = Domain()
                            domain.domain = f"{domain_prefix}.{main_site_url}" # don't add your port or www here!
                            domain.tenant = obj
                            domain.is_primary = True
                            domain.save()
                            
                            connection.set_schema(schema_name)
                            user_tenant = User.objects.get(username='admin')
                            if user_tenant:
                                user_tenant.email = form_data['email']
                                user_tenant.username =form_data['email']
                                user_tenant.set_password(form_data['password'])
                                user_tenant.save()
                            connection.set_schema_to_public()
                            values_array = [form_data['domain_prefix'], form_data['email'], form_data['password']]
                            response_message['values_array'] = values_array
                            response_message['message'] = "Yêu cầu của bạn đã được xử lý thành công!"
                            response_message['status'] = True
                    else:
                        print("No Tenant Template found")
            except Exception as e:
                print(e)
        else:
            print(form.errors,form.cleaned_data)
    else:
        form = TenantRegisterForm()
    return render(request, f'main_site/index.html', {'form': form, 'tenant_templates': tenant_templates, 'response_message': response_message, 'main_site_url': main_site_url})