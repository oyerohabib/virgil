from django.urls import path
from .views import *
from django.contrib.auth import views

urlpatterns = [
    path('', Dashboard, name="index"),
    
    path('errors/', Errors, name="errors"),
    path('errorsdetail/<int:pk>/', ErrorDetail, name="errorsdetail"),

    path('transactions/', Transactions, name="transactions"),
    path('transactionsdetails/<str:pk>/', TransactionDetail, name="transactionsdetails"),

    path('stations/', Stations, name="stations"),
    path('addstation/', AddStation, name="addstation"),
    path('editstation/<int:pk>/', EditStation, name="editstation"),
    path('deletestation/<int:pk>/', DeleteStation, name="deletestation"),

    path('users/', Users, name="users"),
    path('adduser/', AddUser, name="adduser"),
    path('deleteuser/<str:pk>/', DeleteUser, name="deleteuser"),

    path('profile/', Profile, name="profile"),
    path('viewuserprofile/<str:pk>/', ViewUserProfile, name="viewuserprofile"),

    path('notifications/', NotificationListView.as_view(), name='notifications'),
    path('notifications/<int:pk>/', NotificationDetailView.as_view(), name='notification_detail'),
    path('notifications/unread/', unread, name='unread'),
    path('notifications/mark-all-as-read/', mark_all_as_read, name='mark_all_as_read'),
    path('notifications/clear-all/', clear_all, name='clear_all'),

    path('manager_feedback_message/', manager_feedback_message, name="manager_feedback_message"),
    path('feeds/<int:id>', feeds, name="feeds"),
    path('close_feed/<int:id>', close_feed, name="close_feed"),
    path('manager_feedback_message_reply/', manager_feedback_message_reply, name="manager_feedback_message_reply"),

    path('manager_feedback/', manager_feedback, name="manager_feedback"),
    path('manager_feedback_save/', manager_feedback_save, name="manager_feedback_save"),

    path('password_change/', views.PasswordChangeView.as_view(
        template_name='auth/password/change-password.html',
        success_url = 'password_change_done'), name='password_change'),

    path('password_change/done/', views.PasswordChangeDoneView.as_view(
        template_name='auth/password/change-password-done.html'), name='password_change_done'),

    path('activate/<uidb64>/<token>/', ActivateAccount.as_view(), name='activate'),

    path('password_reset/', views.PasswordResetView.as_view(
             template_name='auth/password/password_reset_form.html',
             subject_template_name='auth/password/password_reset_subject.txt',
             email_template_name='auth/password/password_reset_email.html',
             # success_url='/login/'
         ), name='password_reset'),

    path('password_reset/done/', views.PasswordResetDoneView.as_view(
             template_name='auth/password/password_reset_done.html'
         ), name='password_reset_done'),

    path('reset/<uidb64>/<token>/', views.PasswordResetConfirmView.as_view(
             template_name='auth/password/password_reset_confirm.html'
         ), name='password_reset_confirm'),

    path('reset/done/', views.PasswordResetCompleteView.as_view(
             template_name='auth/password/password_reset_complete.html'
         ), name='password_reset_complete'),

    path('login/', Login, name="login"),
    path('logout/', Logout, name="logout"),

    path('400/', Error404, name="400"),
    path('500/', Error500, name="500"),
]