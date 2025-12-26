from django.contrib import messages
from django.db.models import Sum
from django.shortcuts import get_object_or_404, redirect, render

from capitalism.constants.jobs import Job
from capitalism.constants.object_type import ObjectType
from capitalism.models import Human, Simulation
from capitalism.services import (
    HumanBuyingPriceValuationService,
    HumanSellingPriceValuationService,
)
from capitalism.services.object_statistics.repartition import (
    HumanObjectRepartitionService,
)


class HumansView:
    template_name = "capitalism/humans.html"
    detail_template_name = "capitalism/human_detail.html"

    @staticmethod
    def _get_filters(request):
        job = request.GET.get("job")
        state = request.GET.get("state")
        name = request.GET.get("name")
        return job, state, name

    @staticmethod
    def home(request):
        if request.method == "POST":
            return HumansView._handle_object_creation(request)

        job_filter, state_filter, name_filter = HumansView._get_filters(request)
        selected_human_id = request.GET.get("human_id")
        if selected_human_id and selected_human_id.isdigit():
            selected_human_id = int(selected_human_id)
        else:
            selected_human_id = None

        humans = Human.objects.order_by("id")

        if job_filter:
            humans = humans.filter(job=job_filter)

        if state_filter == "alive":
            humans = humans.filter(dead=False)
        elif state_filter == "dead":
            humans = humans.filter(dead=True)

        if name_filter:
            humans = humans.filter(name__icontains=name_filter)

        simulation = Simulation.objects.order_by("id").first()

        selected_human = None
        object_summary = []
        if selected_human_id is not None:
            selected_human = Human.objects.filter(id=selected_human_id).first()
            if selected_human:
                labels = dict(ObjectType.choices)
                summary = (
                    selected_human.owned_objects.values("type")
                    .annotate(quantity=Sum("quantity"))
                    .order_by("type")
                )
                object_summary = [
                    {
                        "type": row["type"],
                        "label": labels.get(row["type"], row["type"]),
                        "quantity": int(row["quantity"] or 0),
                    }
                    for row in summary
                ]

        base_query = request.GET.copy()
        if "human_id" in base_query:
            base_query.pop("human_id")
        base_query_string = base_query.urlencode()

        context = {
            "humans": humans,
            "jobs": Job.choices,
            "job_filter": job_filter or "",
            "state_filter": state_filter or "",
            "simulation": simulation,
            "selected_human": selected_human,
            "selected_human_id": selected_human.id if selected_human else None,
            "object_summary": object_summary,
            "base_query": base_query_string,
            "name_filter": name_filter or "",
            "object_types": ObjectType.choices,
        }

        return render(request, HumansView.template_name, context)

    @staticmethod
    def detail(request, human_id: int):
        human = get_object_or_404(
            Human.objects.prefetch_related("owned_objects"),
            id=human_id,
        )

        if request.method == "POST":
            action = request.POST.get("action")
            if action == "delete_objects":
                HumansView._handle_object_delete(request, human)
                return redirect("capitalism:human_detail", human_id=human.id)
            if action == "add_objects":
                HumansView._handle_object_add(request, human)
                return redirect("capitalism:human_detail", human_id=human.id)
            if action == "update_price":
                HumansView._handle_object_price_update(request, human)
                return redirect("capitalism:human_detail", human_id=human.id)

        objects = human.owned_objects.order_by("type", "id")
        desired_prices = HumansView._desired_purchase_prices(human)
        desired_selling = HumansView._desired_selling_prices(human)
        object_repartition = HumansView._object_repartition(human)

        context = {
            "human": human,
            "objects": objects,
            "object_types": ObjectType.choices,
            "desired_object_prices": desired_prices,
            "selling_object_prices": desired_selling,
            "object_repartition": object_repartition,
        }

        return render(request, HumansView.detail_template_name, context)

    @staticmethod
    def _handle_object_creation(request):
        human_id = request.POST.get("human_id")
        object_type = request.POST.get("object_type")
        quantity_raw = request.POST.get("quantity")
        redirect_url = request.get_full_path()

        if not human_id or not human_id.isdigit():
            messages.error(request, "Humain sélectionné invalide.")
            return redirect(redirect_url)

        human = Human.objects.filter(id=int(human_id)).first()
        if human is None:
            messages.error(request, "Humain introuvable.")
            return redirect(redirect_url)

        HumansView._add_objects_to_human(request, human, object_type, quantity_raw)
        return redirect(redirect_url)

    @staticmethod
    def _handle_object_delete(request, human):
        object_type = request.POST.get("object_type")
        quantity_raw = request.POST.get("quantity")

        quantity, label = HumansView._validate_object_params(request, object_type, quantity_raw)
        if quantity is None:
            return

        objects_qs = human.owned_objects.filter(type=object_type).order_by("id")
        if not objects_qs.exists():
            messages.warning(request, "Aucun objet à supprimer pour ce type.")
            return

        remaining = quantity
        for stack in objects_qs:
            if remaining <= 0:
                break
            take = min(stack.quantity, remaining)
            stack.quantity -= take
            remaining -= take
            if stack.quantity <= 0:
                stack.delete()
            else:
                stack.save(update_fields=["quantity"])
        messages.success(
            request,
            f"{quantity - remaining} objet(s) '{label}' supprimé(s) de "
            f"{human.name or f'Human #{human.id}'}.",
        )

    @staticmethod
    def _handle_object_add(request, human):
        object_type = request.POST.get("object_type")
        quantity_raw = request.POST.get("quantity")

        HumansView._add_objects_to_human(request, human, object_type, quantity_raw)

    @staticmethod
    def _add_objects_to_human(request, human, object_type, quantity_raw):
        quantity, label = HumansView._validate_object_params(request, object_type, quantity_raw)
        if quantity is None:
            return False

        human.add_objects(object_type, quantity)

        display_name = human.name or f"Human #{human.id}"
        messages.success(
            request,
            f"{quantity} objet(s) '{label}' ajouté(s) à {display_name}.",
        )
        return True

    @staticmethod
    def _validate_object_params(request, object_type, quantity_raw):
        valid_types = dict(ObjectType.choices)
        if object_type not in valid_types:
            messages.error(request, "Type d'objet invalide.")
            return None, None

        try:
            quantity = int(quantity_raw)
        except (TypeError, ValueError):
            messages.error(request, "La quantité doit être un nombre entier.")
            return None, None

        if quantity <= 0:
            messages.error(request, "La quantité doit être supérieure à zéro.")
            return None, None

        label = valid_types.get(object_type, object_type)
        return quantity, label

    @staticmethod
    def _handle_object_price_update(request, human):
        object_id = request.POST.get("object_id")
        price_raw = request.POST.get("price")

        if not object_id or not object_id.isdigit():
            messages.error(request, "Objet invalide.")
            return

        object_stack = human.owned_objects.filter(id=int(object_id)).first()
        if object_stack is None:
            messages.error(request, "Objet introuvable pour ce human.")
            return

        if price_raw in (None, "", "null"):
            object_stack.price = None
            object_stack.in_sale = False
            object_stack.save(update_fields=["price", "in_sale"])
            messages.success(request, "Le prix de l'objet a été supprimé.")
            return

        try:
            price = float(price_raw)
        except (TypeError, ValueError):
            messages.error(request, "Le prix doit être un nombre.")
            return

        if price < 0:
            messages.error(request, "Le prix doit être positif.")
            return

        formatted_price = round(price + 1e-12, 2)
        object_stack.price = formatted_price
        object_stack.in_sale = True
        object_stack.save(update_fields=["price", "in_sale"])
        HumansView._merge_duplicate_stack(object_stack)
        messages.success(request, "Le prix de l'objet a été mis à jour.")

    @staticmethod
    def _desired_purchase_prices(human):
        valuation_service = HumanBuyingPriceValuationService()
        desired_prices = []

        for object_type, label in ObjectType.choices:
            price = valuation_service.estimate_price(human, object_type)
            if price and price > 0:
                desired_prices.append(
                    {
                        "type": object_type,
                        "label": label,
                        "price": float(price),
                    }
                )

        return desired_prices

    @staticmethod
    def _merge_duplicate_stack(stack):
        duplicates = stack.owner.owned_objects.filter(
            type=stack.type,
            in_sale=stack.in_sale,
            price=stack.price,
        ).exclude(id=stack.id)
        if not duplicates.exists():
            return
        total_quantity = stack.quantity + duplicates.aggregate(total=Sum("quantity"))["total"]
        stack.quantity = int(total_quantity or stack.quantity)
        stack.save(update_fields=["quantity"])
        duplicates.delete()

    @staticmethod
    def _desired_selling_prices(human):
        valuation_service = HumanSellingPriceValuationService()
        selling_prices = []

        for object_type, label in ObjectType.choices:
            price = valuation_service.estimate_price(human, object_type)
            if price and price > 0:
                selling_prices.append(
                    {
                        "type": object_type,
                        "label": label,
                        "price": float(price),
                    }
                )

        return selling_prices

    @staticmethod
    def _object_repartition(human):
        service = HumanObjectRepartitionService(human_id=human.id)
        return service.run()
