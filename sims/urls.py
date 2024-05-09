from django.urls import path, re_path
from . import views

app_name = 'sims'

urlpatterns = [
    re_path(r'^(?P<simNumber>[0-9]{10,12})/$', views.simDetailPage, name='sim_detail'),
    path('sims-submit-order/<str:sim>/', views.submitSimOrder, name='submitSimOrder'),
    path('sim-phong-thuy/', views.fengShuiPage, name='feng_shuipage'),
    path('xem-phong-thuy/', views.SimFortunePage, name='feng_fortune'),
    path('boi-sim-phong-thuy/', views.SimFengShuiFortunePage, name='feng_shui_fortune'),
    path('sim-<slug:slug>/', views.simListPage, name='sim_page'),
    path('p/dat-sim-thanh-cong/', views.passSimOrderPage, name='passSimOrderPage'),
    path('p/dat-sim-that-bai/', views.failSimOrderPage, name='failSimOrderPage'),
    path('p/<slug:slug>/', views.viewPage, name='viewPage'),
    path('', views.homePage, name='sim_homepage'),
    path('dat-sim-theo-yeu-cau/', views.orderSimRequiredPage, name='orderSimRequired'),
    path('yeu-cau-thanh-cong/', views.passSimRequiredPage, name='passSimRequiredPage'),
    path('dinh-gia-sim/', views.sim_valuation, name='sim_valuation'),
]
