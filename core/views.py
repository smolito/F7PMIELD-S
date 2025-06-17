import json
from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse
from fhir.resources.bundle import Bundle
from fhir.resources.patient import Patient as FhirPatient
from fhir.resources.observation import Observation, ObservationComponent
from fhir.resources.codeableconcept import CodeableConcept
from fhir.resources.coding import Coding
from fhir.resources.quantity import Quantity
from fhir.resources.reference import Reference
from fhir.resources.period import Period
import pandas as pd
import plotly.express as px
from .models import Pacient, Navsteva

# ... stávající funkce patient_list a patient_detail ...

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
    navstevy = pacient.navstevy.all().order_by('-datum_navstevy') # Změna pořadí na nejnovější nahoře
    
    bp_data = []
    for navsteva in navstevy:
        if hasattr(navsteva, 'krevni_tlak'):
            bp = navsteva.krevni_tlak
            bp_data.append({
                'Datum': navsteva.datum_navstevy,
                'Systolický tlak': bp.systolicky,
                'Diastolický tlak': bp.diastolicky,
            })
    
    rt_data = []
    for navsteva in navstevy:
        if hasattr(navsteva, 'reakcni_doba'):
            rt = navsteva.reakcni_doba
            rt_data.append({
                'Datum': navsteva.datum_navstevy,
                'Reakční doba (ms)': rt.prumerna_doba_ms,
            })

    plot_divs = {}
    if bp_data:
        df_bp = pd.DataFrame(bp_data)
        fig_bp = px.line(df_bp, x='Datum', y=['Systolický tlak', 'Diastolický tlak'], 
                         title="Vývoj krevního tlaku", markers=True,
                         labels={'value': 'Hodnota (mmHg)', 'variable': 'Měření'})
        plot_divs['krevni_tlak'] = fig_bp.to_html(full_html=False, include_plotlyjs='cdn')

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

# --- Nová logika pro export ---

def transform_to_fhir_bundle(pacient, visit_ids):
    """
    Transformuje vybraná data pacienta a návštěv do FHIR Bundle.
    """
    bundle = Bundle.construct(type="collection")
    bundle.entry = []

    # Přidání pacienta jako prvního zdroje
    fhir_patient = FhirPatient.construct(id=str(pacient.id))
    # V reálné aplikaci by se mapovala i další data (jméno, pohlaví atd.)
    bundle.entry.append({"resource": fhir_patient.dict()})

    # Získání vybraných návštěv
    selected_visits = Navsteva.objects.filter(id__in=visit_ids)

    for visit in selected_visits:
        subject_ref = Reference.construct(reference=f"Patient/{pacient.id}")
        effective_datetime = visit.datum_navstevy.isoformat()

        # Transformace pro krevní tlak
        if hasattr(visit, 'krevni_tlak'):
            model = visit.krevni_tlak
            fhir_obs = Observation.construct(
                status='final',
                code=CodeableConcept.construct(coding=[Coding.construct(system="http://loinc.org", code="85354-9", display="Blood pressure panel")]),
                subject=subject_ref,
                effectiveDateTime=effective_datetime,
                component=[
                    ObservationComponent.construct(
                        code=CodeableConcept.construct(coding=[Coding.construct(system="http://snomed.info/sct", code=model.SYSTOLICKY_SNOMED, display=model.SYSTOLICKY_DISPLAY)]),
                        valueQuantity=Quantity.construct(value=model.systolicky, unit="mmHg", system="http://unitsofmeasure.org", code="mm[Hg]")
                    ),
                    ObservationComponent.construct(
                        code=CodeableConcept.construct(coding=[Coding.construct(system="http://snomed.info/sct", code=model.DIASTOLICKY_SNOMED, display=model.DIASTOLICKY_DISPLAY)]),
                        valueQuantity=Quantity.construct(value=model.diastolicky, unit="mmHg", system="http://unitsofmeasure.org", code="mm[Hg]")
                    ),
                    ObservationComponent.construct(
                        code=CodeableConcept.construct(coding=[Coding.construct(system="http://snomed.info/sct", code=model.SRDECNI_FREKVENCE_SNOMED, display=model.SRDECNI_FREKVENCE_DISPLAY)]),
                        valueQuantity=Quantity.construct(value=model.srdecni_frekvence, unit="/min", system="http://unitsofmeasure.org", code="/min")
                    )
                ]
            )
            bundle.entry.append({"resource": fhir_obs.dict()})

        # Transformace pro reakční dobu
        if hasattr(visit, 'reakcni_doba'):
            model = visit.reakcni_doba
            fhir_obs = Observation.construct(
                status='final',
                code=CodeableConcept.construct(coding=[Coding.construct(system="http://snomed.info/sct", code=model.PRUMERNA_DOBA_SNOMED, display=model.PRUMERNA_DOBA_DISPLAY)]),
                subject=subject_ref,
                effectiveDateTime=effective_datetime,
                valueQuantity=Quantity.construct(value=model.prumerna_doba_ms, unit="ms", system="http://unitsofmeasure.org", code="ms")
            )
            bundle.entry.append({"resource": fhir_obs.dict()})

        # Transformace pro srozumitelnost řeči
        if hasattr(visit, 'srozumitelnost_reci'):
            model = visit.srozumitelnost_reci
            fhir_obs = Observation.construct(
                status='final',
                code=CodeableConcept.construct(text="Speech Intelligibility Assessment"),
                subject=subject_ref,
                effectiveDateTime=effective_datetime,
                component=[
                    ObservationComponent.construct(
                        code=CodeableConcept.construct(coding=[Coding.construct(system="http://snomed.info/sct", code=model.RYCHLOST_RECI_SNOMED, display=model.RYCHLOST_RECI_DISPLAY)]),
                        valueQuantity=Quantity.construct(value=model.rychlost_reci, unit="slov/min")
                    ),
                    ObservationComponent.construct(
                        code=CodeableConcept.construct(text="Word Error Rate"),
                        valueQuantity=Quantity.construct(value=model.wer_procento, unit="%")
                    )
                ]
            )
            bundle.entry.append({"resource": fhir_obs.dict()})
        
        # Transformace pro deník bolestí hlavy
        if hasattr(visit, 'bolesti_hlavy'):
            model = visit.bolesti_hlavy
            fhir_obs = Observation.construct(
                status='final',
                code=CodeableConcept.construct(text="Headache Diary Summary"),
                subject=subject_ref,
                effectivePeriod=Period.construct(start=model.obdobi_od.isoformat(), end=model.obdobi_do.isoformat()),
                component=[
                    ObservationComponent.construct(
                        code=CodeableConcept.construct(text="Počet dní s bolestí"),
                        valueInteger=model.pocet_dni_s_bolesti
                    ),
                    ObservationComponent.construct(
                        code=CodeableConcept.construct(coding=[Coding.construct(system="http://snomed.info/sct", code=model.PRUMERNA_INTENZITA_SNOMED, display=model.PRUMERNA_INTENZITA_DISPLAY)]),
                        valueInteger=model.prumerna_intenzita
                    )
                ]
            )
            bundle.entry.append({"resource": fhir_obs.dict()})
            
        # Transformace pro klepání prsty (bez SNOMED kódů, jen s textovým popisem)
        if hasattr(visit, 'klepani_prsty'):
            model = visit.klepani_prsty
            fhir_obs = Observation.construct(
                status='final',
                code=CodeableConcept.construct(text="Finger Tapping Test"),
                subject=subject_ref,
                effectiveDateTime=effective_datetime,
                component=[
                     ObservationComponent.construct(
                        code=CodeableConcept.construct(text="Počet poklepů"),
                        valueInteger=model.pocet_poklepu
                    )
                ]
            )
            bundle.entry.append({"resource": fhir_obs.dict()})

    return bundle


def export_selection(request, patient_id):
    pacient = get_object_or_404(Pacient, id=patient_id)

    if request.method == 'POST':
        visit_ids = request.POST.getlist('visit_ids')
        export_format = request.POST.get('format', 'json')

        if not visit_ids:
            # Zde by měla být nějaká chybová hláška
            return render(request, 'core/export_selection.html', {'pacient': pacient, 'navstevy': pacient.navstevy.all(), 'error': 'Musíte vybrat alespoň jednu návštěvu.'})

        # Vytvoření FHIR Bundle
        fhir_bundle = transform_to_fhir_bundle(pacient, visit_ids)
        bundle_dict = fhir_bundle.dict()
        
        if export_format == 'json':
            response = HttpResponse(
                json.dumps(bundle_dict, indent=2),
                content_type='application/json'
            )
            response['Content-Disposition'] = f'attachment; filename="export_pacient_{pacient.id}.json"'
            return response
        else: # txt format
            #txt_output = f"Export dat pro pacienta: {pacient.jmeno}\n"
            #txt_output += "=" * 40 + "\n\n"
            
            for entry in bundle_dict.get("entry", []):
                resource = entry.get("resource")
                if resource:
                    #txt_output += f"--- {resource.get('resourceType', 'N/A')} ---\n"
                    for key, value in resource.items():
                        if value:
                            txt_output += f"{key}: {json.dumps(value, indent=2, ensure_ascii=False)}\n"
                    txt_output += "\n"
            
            response = HttpResponse(txt_output, content_type='text/plain; charset=utf-8')
            response['Content-Disposition'] = f'attachment; filename="export_pacient_{pacient.id}.txt"'
            return response

    # Pokud je to GET požadavek, zobrazí se stránka s výběrem
    navstevy = pacient.navstevy.all().order_by('-datum_navstevy')
    context = {
        'pacient': pacient,
        'navstevy': navstevy,
    }
    return render(request, 'core/export_selection.html', context)
