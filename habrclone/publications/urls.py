from django.urls import path
from . import views

app_name = 'publications'

urlpatterns = [
    path('<type>/<int:id>/', views.PublicationApiView.as_view(), name = 'detail'),
]