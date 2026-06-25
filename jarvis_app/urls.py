from django.urls import path
from . import views

app_name = 'jarvis_app'

urlpatterns = [
    path('', views.index, name='index'),
    path('api/command/', views.process_voice_command, name='process_command'),
    path('api/clear/', views.clear_conversation, name='clear'),
    path('api/status/', views.get_status, name='status'),
]
