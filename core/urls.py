from django.urls import path
from . import views

# Tento 'namespace' pomáhá odlišit URL adresy mezi různými aplikacemi v projektu
app_name = 'core'

urlpatterns = [
    # Cesta pro seznam všech pacientů, např. http://localhost:8000/
    path('', views.patient_list, name='patient_list'),
    
    # Cesta pro detail konkrétního pacienta, např. http://localhost:8000/pacient/1/
    path('pacient/<int:patient_id>/', views.patient_detail, name='patient_detail'),
]
