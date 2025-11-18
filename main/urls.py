from django.urls import path
from main import views

urlpatterns = [
    path('', views.home, name='home'),
    path('gallery/', views.gallery, name='gallery'),
    path('policies/', views.policy_menu, name='policy_menu'),
    path('policies/<str:policy_slug>/', views.get_policy, name='get_policy'),
    path('password-reset/', views.password_reset_view, name='password_reset'),
    path('password-verify/<int:uid>/<str:token>/', views.password_verify_view, name='password_verify'),
    path('activate-account/<int:uid>/<str:token>/', views.activate_account_view, name='activate_account'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('parent_dashboard/', views.parent_dashboard_view, name='parent_dashboard'),
    path('child/<int:child_pk>/', views.child_view, name='child'),
    path('contracts/<int:child_pk>/', views.child_contract_view, name='child_contract'),
    path('save_contract/<int:child_pk>/', views.save_contract_view, name='save_contract'),
    path('consent/<int:child_pk>/', views.child_consent_view, name='child_consent'),
    path('save_consent/<int:child_pk>/', views.save_consent_view, name='save_consent'),
    path('child_record/<int:child_pk>/', views.child_record_view, name='child_record'),
    path('save_child_record/<int:child_pk>/', views.save_child_record_view, name='save_child_record'),
    # Staff Paths
    path('staff_dashboard/', views.staff_dashboard_view, name='staff_dashboard'),
    path('child_register/', views.child_register_view, name='child_register'),
    path('clock_in/<int:child_pk>/', views.clock_in_child, name='clock_in'),
    path('clock_out/<int:child_pk>/', views.clock_out_child, name='clock_out'),
]