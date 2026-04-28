from django.db import models


class City(models.TextChoices):
    BRIDGEWATCH = "BRIDGEWATCH", "Bridgewatch"
    CAERLEON = "CAERLEON", "Caerleon"
    FORT_STERLING = "FORT_STERLING", "Fort Sterling"
    LYMHURST = "LYMHURST", "Lymhurst"
    MARTLOCK = "MARTLOCK", "Martlock"
    THETFORD = "THETFORD", "Thetford"
    BRECILIEN = "BRECILIEN", "Brecilien"
