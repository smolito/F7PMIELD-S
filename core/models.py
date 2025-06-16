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
    rychlost_reci = models.FloatField()
    klinicka_interpretace = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"Srozumitelnost řeči pro návštěvu ID: {self.navsteva.id}"

class ObservationReakcniDoba(models.Model):
    navsteva = models.OneToOneField(Navsteva, on_delete=models.CASCADE, related_name='reakcni_doba')
    typ_podnetu = models.CharField(max_length=50) # např. 'Vizuální', 'Zvukový'
    prumerna_doba_ms = models.IntegerField()
    smerodatna_odchylka_ms = models.FloatField()

    def __str__(self):
        return f"Reakční doba pro návštěvu ID: {self.navsteva.id}"

class ObservationKlepaniPrsty(models.Model):
    navsteva = models.OneToOneField(Navsteva, on_delete=models.CASCADE, related_name='klepani_prsty')
    hodnocena_koncetina = models.CharField(max_length=50) # např. 'Pravá', 'Levá'
    pocet_poklepu = models.IntegerField()
    doba_trvani_s = models.IntegerField()

    def __str__(self):
        return f"Klepání prsty pro návštěvu ID: {self.navsteva.id}"

class ObservationBolestiHlavy(models.Model):
    navsteva = models.OneToOneField(Navsteva, on_delete=models.CASCADE, related_name='bolesti_hlavy')
    obdobi_od = models.DateField()
    obdobi_do = models.DateField()
    pocet_dni_s_bolesti = models.IntegerField()
    prumerna_intenzita = models.IntegerField() # např. na škále 1-10

    def __str__(self):
        return f"Deník bolestí hlavy pro návštěvu ID: {self.navsteva.id}"

class ObservationKrevniTlak(models.Model):
    navsteva = models.OneToOneField(Navsteva, on_delete=models.CASCADE, related_name='krevni_tlak')
    systolicky = models.IntegerField()
    diastolicky = models.IntegerField()
    srdecni_frekvence = models.IntegerField()
    poloha_pacienta = models.CharField(max_length=50) # např. 'Vsedě', 'Vleže'

    def __str__(self):
        return f"Krevní tlak pro návštěvu ID: {self.navsteva.id}"
