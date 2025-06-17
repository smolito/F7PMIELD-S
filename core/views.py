from django.shortcuts import render, get_object_or_404
import pandas as pd
import plotly.express as px
from .models import Pacient

def patient_list(request):
    """
    Zobrazí seznam všech pacientů v databázi.
    """
    pacienti = Pacient.objects.all().order_by('jmeno')
    context = {
        'pacienti': pacienti,
    }
    return render(request, 'core/patient_list.html', context)

def patient_detail(request, patient_id):
    """
    Zobrazí detailní informace o jednom pacientovi a jeho měřeních v grafech.
    """
    pacient = get_object_or_404(Pacient, id=patient_id)
    # Získání všech návštěv pacienta, seřazených podle data návštěvy
    navstevy = pacient.navstevy.all().order_by('datum_navstevy')
    
    # --- Příprava dat pro grafy ---
    
    # Data krevního tlaku
    bp_data = []
    for navsteva in navstevy:
        if hasattr(navsteva, 'krevni_tlak'):
            bp = navsteva.krevni_tlak
            bp_data.append({
                'Datum': navsteva.datum_navstevy,
                'Systolický tlak': bp.systolicky,
                'Diastolický tlak': bp.diastolicky,
            })
    
    # Data reakční doby
    rt_data = []
    for navsteva in navstevy:
        if hasattr(navsteva, 'reakcni_doba'):
            rt = navsteva.reakcni_doba
            rt_data.append({
                'Datum': navsteva.datum_navstevy,
                'Reakční doba (ms)': rt.prumerna_doba_ms,
            })

    # --- Generování grafů pomocí Plotly ---
    plot_divs = {}

    # Graf pro krevní tlak
    if bp_data:
        df_bp = pd.DataFrame(bp_data)
        fig_bp = px.line(df_bp, x='Datum', y=['Systolický tlak', 'Diastolický tlak'], 
                         title="Vývoj krevního tlaku", markers=True)
        plot_divs['krevni_tlak'] = fig_bp.to_html(full_html=False, include_plotlyjs='cdn')

    # Graf pro reakční dobu
    if rt_data:
        df_rt = pd.DataFrame(rt_data)
        fig_rt = px.line(df_rt, x='Datum', y='Reakční doba (ms)',
                         title="Vývoj reakční doby", markers=True)
        plot_divs['reakcni_doba'] = fig_rt.to_html(full_html=False)


    context = {
        'pacient': pacient,
        'navstevy': navstevy,
        'plot_divs': plot_divs,
    }
    
    return render(request, 'core/patient_detail.html', context)
