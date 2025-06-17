from django.urls import path
from . import views

# Tento 'namespace' pomáhá odlišit URL adresy mezi různými aplikacemi v projektu
app_name = 'core'

urlpatterns = [
    path('', views.patient_list, name='patient_list'), # vše
    path('pacient/<int:patient_id>/', views.patient_detail, name='patient_detail'), # jeden pac
    path('pacient/<int:patient_id>/export/', views.export_selection, name='export_selection'), # export z jednoho pacienta
]
