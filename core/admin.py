from django.contrib import admin
from .models import (
    Pacient,
    Navsteva,
    ObservationSrozumitelnostReci,
    ObservationReakcniDoba,
    ObservationKlepaniPrsty,
    ObservationBolestiHlavy,
    ObservationKrevniTlak,
)

# --- Inline modely pro zobrazení v detailu Návštěvy ---
# Tento přístup umožňuje editovat všechna pozorování na jedné stránce.

class ObservationKrevniTlakInline(admin.TabularInline):
    model = ObservationKrevniTlak
    extra = 1  # Počet prázdných formulářů pro nové záznamy
    verbose_name_plural = 'Měření krevního tlaku'

class ObservationReakcniDobaInline(admin.TabularInline):
    model = ObservationReakcniDoba
    extra = 1
    verbose_name_plural = 'Měření reakční doby'

class ObservationKlepaniPrstyInline(admin.TabularInline):
    model = ObservationKlepaniPrsty
    extra = 1
    verbose_name_plural = 'Měření klepání prsty'

class ObservationBolestiHlavyInline(admin.TabularInline):
    model = ObservationBolestiHlavy
    extra = 1
    verbose_name_plural = 'Záznam o bolestech hlavy'

class ObservationSrozumitelnostReciInline(admin.TabularInline):
    model = ObservationSrozumitelnostReci
    extra = 1
    verbose_name_plural = 'Záznam o srozumitelnosti řeči'


# --- Vlastní administrace pro model Návštěva ---

@admin.register(Navsteva)
class NavstevaAdmin(admin.ModelAdmin):
    """
    Umožňuje zobrazit a spravovat všechna přidružená měření
    přímo v detailu návštěvy.
    """
    list_display = ('pacient', 'datum_navstevy')
    list_filter = ('datum_navstevy',)
    search_fields = ('pacient__jmeno',)
    
    # Propojení inline modelů
    inlines = [
        ObservationKrevniTlakInline,
        ObservationReakcniDobaInline,
        ObservationKlepaniPrstyInline,
        ObservationBolestiHlavyInline,
        ObservationSrozumitelnostReciInline,
    ]

# --- Vlastní administrace pro model Pacient ---

class NavstevaInlineForPacient(admin.TabularInline):
    """
    Zobrazí seznam návštěv přímo v detailu pacienta.
    """
    model = Navsteva
    extra = 1
    fields = ('datum_navstevy', 'poznamka')
    readonly_fields = ('datum_navstevy',) # Návštěvy by se měly vytvářet v sekci Návštěvy
    show_change_link = True # Odkaz na detailní úpravu návštěvy
    verbose_name_plural = 'Historie návštěv'


@admin.register(Pacient)
class PacientAdmin(admin.ModelAdmin):
    """
    Zobrazuje historii návštěv pacienta.
    """
    list_display = ('jmeno', 'datum_narozeni')
    search_fields = ('jmeno',)
    inlines = [NavstevaInlineForPacient]
