from django.urls import path
from . import views

app_name = 'theme_config'

urlpatterns = [
   path('theme/config', views.index, name='config_index'),
   path('theme/submit-config', views.saveTheme, name='submit_config'),
]
