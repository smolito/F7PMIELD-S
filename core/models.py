from django.db import models
from django.utils import timezone

# Pacient je ústřední entita
class Pacient(models.Model):
    """
    Uchovává základní informace o pacientech.
    """
    jmeno = models.CharField(max_length=200)
    datum_narozeni = models.DateField()

    def __str__(self):
        return f"{self.jmeno} (ID: {self.id})"

# Návštěva slouží jako kontejner pro všechna měření v daný čas
class Navsteva(models.Model):
    """
    Reprezentuje jednu návštěvu pacienta, ke které se vážou pozorování.
    """
    pacient = models.ForeignKey(Pacient, on_delete=models.CASCADE, related_name='navstevy')
    datum_navstevy = models.DateTimeField(default=timezone.now)
    poznamka = models.TextField(blank=True, null=True)

    def __str__(self):
        # Formátování data pro lepší čitelnost
        formatted_date = self.datum_navstevy.strftime('%d. %m. %Y %H:%M')
        return f"Návštěva pacienta {self.pacient.jmeno} dne {formatted_date}"

# --- Tabulky pro jednotlivá pozorování (archetypy) ---

class ObservationSrozumitelnostReci(models.Model):
    navsteva = models.OneToOneField(Navsteva, on_delete=models.CASCADE, related_name='srozumitelnost_reci')
    referencni_text = models.TextField()
    wer_procento = models.FloatField()

    RYCHLOST_RECI_SNOMED = '1197010003'
    RYCHLOST_RECI_DISPLAY = 'Rate of speech'
    rychlost_reci = models.FloatField(
        help_text=f'SNOMED CT: {RYCHLOST_RECI_SNOMED} ({RYCHLOST_RECI_DISPLAY})'
    )
    
    klinicka_interpretace = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"Srozumitelnost řeči pro návštěvu ID: {self.navsteva.id}"

class ObservationReakcniDoba(models.Model):
    navsteva = models.OneToOneField(Navsteva, on_delete=models.CASCADE, related_name='reakcni_doba')
    typ_podnetu = models.CharField(max_length=50)

    PRUMERNA_DOBA_SNOMED = '112460003'
    PRUMERNA_DOBA_DISPLAY = 'Reaction time'
    prumerna_doba_ms = models.IntegerField(
        help_text=f'SNOMED CT: {PRUMERNA_DOBA_SNOMED} ({PRUMERNA_DOBA_DISPLAY})'
    )
    
    smerodatna_odchylka_ms = models.FloatField()

    def __str__(self):
        return f"Reakční doba pro návštěvu ID: {self.navsteva.id}"

class ObservationKlepaniPrsty(models.Model):
    navsteva = models.OneToOneField(Navsteva, on_delete=models.CASCADE, related_name='klepani_prsty')
    hodnocena_koncetina = models.CharField(max_length=50)
    pocet_poklepu = models.IntegerField()
    doba_trvani_s = models.IntegerField()

    def __str__(self):
        return f"Klepání prsty pro návštěvu ID: {self.navsteva.id}"

class ObservationBolestiHlavy(models.Model):
    navsteva = models.OneToOneField(Navsteva, on_delete=models.CASCADE, related_name='bolesti_hlavy')
    obdobi_od = models.DateField()
    obdobi_do = models.DateField()
    pocet_dni_s_bolesti = models.IntegerField()

    PRUMERNA_INTENZITA_SNOMED = '25064002'
    PRUMERNA_INTENZITA_DISPLAY = 'Pain intensity'
    prumerna_intenzita = models.IntegerField(
        help_text=f'SNOMED CT: {PRUMERNA_INTENZITA_SNOMED} ({PRUMERNA_INTENZITA_DISPLAY})'
    )

    def __str__(self):
        return f"Deník bolestí hlavy pro návštěvu ID: {self.navsteva.id}"

class ObservationKrevniTlak(models.Model):
    navsteva = models.OneToOneField(Navsteva, on_delete=models.CASCADE, related_name='krevni_tlak')

    SYSTOLICKY_SNOMED = '271649006'
    SYSTOLICKY_DISPLAY = 'Systolic blood pressure'
    systolicky = models.IntegerField(
        help_text=f'SNOMED CT: {SYSTOLICKY_SNOMED} ({SYSTOLICKY_DISPLAY})'
    )

    DIASTOLICKY_SNOMED = '271650006'
    DIASTOLICKY_DISPLAY = 'Diastolic blood pressure'
    diastolicky = models.IntegerField(
        help_text=f'SNOMED CT: {DIASTOLICKY_SNOMED} ({DIASTOLICKY_DISPLAY})'
    )

    SRDECNI_FREKVENCE_SNOMED = '364075005'
    SRDECNI_FREKVENCE_DISPLAY = 'Heart rate'
    srdecni_frekvence = models.IntegerField(
        help_text=f'SNOMED CT: {SRDECNI_FREKVENCE_SNOMED} ({SRDECNI_FREKVENCE_DISPLAY})'
    )
    
    poloha_pacienta = models.CharField(max_length=50)

    def __str__(self):
        return f"Krevní tlak pro návštěvu ID: {self.navsteva.id}"
