from datetime import timedelta

from django.utils import timezone

from albion_online.models import CraftProfitabilityDone, Object


class CraftProfitabilityDoneService:
    DONE_WINDOW_HOURS = 12

    def build_recently_done_state(self, objects, selected_city_filter):
        object_ids = [craft_object.id for craft_object in objects if craft_object.id is not None]
        cutoff = timezone.now() - timedelta(hours=self.DONE_WINDOW_HOURS)
        done_crafts = (
            CraftProfitabilityDone.objects.select_related("object")
            .filter(object_id__in=object_ids, completed_at__gte=cutoff)
            .order_by("city", "object__aodp_id", "completed_at", "pk")
        )

        if selected_city_filter != "all":
            done_crafts = done_crafts.filter(city=selected_city_filter)

        recently_done_keys = {
            (done_craft.city, done_craft.object_id)
            for done_craft in done_crafts
        }
        done_signature = "|".join(
            f"{done_craft.city}:{done_craft.object.aodp_id}:{done_craft.completed_at.isoformat()}"
            for done_craft in done_crafts
        ) or "none"
        return recently_done_keys, done_signature

    def mark_done(self, object_aodp_id, city):
        craft_object = Object.objects.filter(aodp_id=object_aodp_id).first()
        if craft_object is None:
            return None
        return CraftProfitabilityDone.objects.update_or_create(
            object=craft_object,
            city=city,
            defaults={
                "completed_at": timezone.now(),
            },
        )
