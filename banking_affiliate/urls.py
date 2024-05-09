from django.urls import include, path
from . import views

app_name = 'banking_affiliate'

urlpatterns = [
    # Other URL patterns in your project
    path('api/mb/get-transaction-info', views.get_transaction_info, name='get_transaction_info'),
    path('api/mb/get-user-info', views.get_user_info, name='get_user_info'),
    path('api/mb/push-mb-pending-topsim/<str:token>', views.push_mb_pending_topsim_webhook, name='push_mb_pending_topsim_webhook'),
    path('banking-submit-order/<str:sim>/', views.submitSimOrder, name='submitSimOrder'),
    path('banking/banking-statement-waiting/', views.banking_statement_waiting, name='banking_statement_waiting'),
    path('api/webhook/mb/callback-statement', views.callback_after_payment_statement, name='callback_after_payment_statement'),
    path('mb-dat-sim-thanh-cong/', views.callback_after_bank_successful, name='callback_after_bank_successful'),
    
]
