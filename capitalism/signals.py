from django.apps import apps
from django.db.models.signals import post_save


def _create_central_government(sender, instance, created, **kwargs):
    if not created:
        return
    central_government_model = apps.get_model("capitalism", "CentralGovernment")
    central_government_model.objects.get_or_create(simulation=instance)


def connect_signals():
    simulation_model = apps.get_model("capitalism", "Simulation")
    post_save.connect(
        _create_central_government,
        sender=simulation_model,
        dispatch_uid="capitalism_create_central_government",
    )
