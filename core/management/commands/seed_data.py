import random
from datetime import timedelta

from django.core.management.base import BaseCommand
from django.utils import timezone
from faker import Faker

from core.models import (
    Pacient,
    Navsteva,
    ObservationSrozumitelnostReci,
    ObservationReakcniDoba,
    ObservationKlepaniPrsty,
    ObservationBolestiHlavy,
    ObservationKrevniTlak,
)

class Command(BaseCommand):
    help = 'Naplní databázi umělými daty pro testování.'

    def handle(self, *args, **kwargs):
        self.stdout.write("Mažu stará data...")
        # Smazání všech stávajících dat pro čistý start
        Pacient.objects.all().delete()

        fake = Faker('cs_CZ')  # Použití českého lokálního nastavení

        self.stdout.write("Vytvářím nová data...")

        # Vytvoření pacientů
        pacienti = []
        for _ in range(10):
            pacient = Pacient.objects.create(
                jmeno=fake.name(),
                datum_narozeni=fake.date_of_birth(minimum_age=20, maximum_age=85)
            )
            pacienti.append(pacient)

        # Pro každého pacienta vytvoříme návštěvy a pozorování
        for pacient in pacienti:
            # Vytvoříme 5 návštěv pro každého pacienta
            for i in range(5):
                navsteva = Navsteva.objects.create(
                    pacient=pacient,
                    datum_navstevy=timezone.now() - timedelta(days=i * 60 + random.randint(0, 30)),
                    poznamka=fake.sentence(nb_words=10) if random.choice([True, False]) else ""
                )

                # Náhodně vytvoříme pozorování pro každou návštěvu
                if random.choice([True, True, False]):
                    ObservationKrevniTlak.objects.create(
                        navsteva=navsteva,
                        systolicky=random.randint(110, 160),
                        diastolicky=random.randint(70, 100),
                        srdecni_frekvence=random.randint(60, 90),
                        poloha_pacienta=random.choice(['Vsedě', 'Vleže'])
                    )

                if random.choice([True, False]):
                    ObservationReakcniDoba.objects.create(
                        navsteva=navsteva,
                        typ_podnetu=random.choice(['Vizuální', 'Zvukový']),
                        prumerna_doba_ms=random.randint(250, 500),
                        smerodatna_odchylka_ms=random.uniform(20.0, 50.0)
                    )

                if random.choice([True, False]):
                    ObservationKlepaniPrsty.objects.create(
                        navsteva=navsteva,
                        hodnocena_koncetina=random.choice(['Pravá', 'Levá']),
                        pocet_poklepu=random.randint(30, 60),
                        doba_trvani_s=10
                    )

                if random.choice([True, False, False]): # Menší šance na vytvoření
                    obdobi_do = navsteva.datum_navstevy.date()
                    obdobi_od = obdobi_do - timedelta(days=30)
                    ObservationBolestiHlavy.objects.create(
                        navsteva=navsteva,
                        obdobi_od=obdobi_od,
                        obdobi_do=obdobi_do,
                        pocet_dni_s_bolesti=random.randint(0, 15),
                        prumerna_intenzita=random.randint(1, 10)
                    )

                if random.choice([True, False, False]):
                    ObservationSrozumitelnostReci.objects.create(
                        navsteva=navsteva,
                        referencni_text="Příliš žluťoučký kůň úpěl ďábelské ódy.",
                        wer_procento=random.uniform(5.0, 25.0),
                        rychlost_reci=random.uniform(120.0, 180.0),
                        klinicka_interpretace=random.choice(['Normální nález', 'Mírná dysartrie', 'Zpomalené tempo'])
                    )

        self.stdout.write(self.style.SUCCESS('Databáze byla úspěšně naplněna daty.'))
