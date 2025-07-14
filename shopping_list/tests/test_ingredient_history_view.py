import datetime
from django.test import TestCase, Client
from django.urls import reverse
from django.utils import timezone

from django.contrib.auth.models import User

from shopping_list.constants.category import Category
from shopping_list.models import Ingredient
from shopping_list.models.ingredient_history import IngredientHistory


class IngredientHistoryViewTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="tester", password="pass", is_staff=True
        )
        self.client = Client()
        self.client.login(username="tester", password="pass")

        self.apple = Ingredient.objects.create(
            name="Apple", is_pantry_staples=False, unit="pc", category=Category.FRUIT
        )
        self.milk = Ingredient.objects.create(
            name="Milk", is_pantry_staples=False, unit="l", category=Category.DAIRY
        )

        now = timezone.now()
        IngredientHistory.objects.create(
            ingredient=self.apple,
            quantity=2,
            bought_date=now - datetime.timedelta(days=10),
        )
        IngredientHistory.objects.create(
            ingredient=self.apple,
            quantity=3,
            bought_date=now - datetime.timedelta(days=40),
        )
        IngredientHistory.objects.create(
            ingredient=self.milk,
            quantity=1,
            bought_date=now - datetime.timedelta(days=200),
        )

        self.url = reverse("shopping_list:ingredient_history")

    def test_all_time_aggregation(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        items = response.context["items"]
        totals = {i["ingredient__name"]: i["total_quantity"] for i in items}
        self.assertEqual(totals["Apple"], 5)
        self.assertEqual(totals["Milk"], 1)

    def test_last_month_filter(self):
        response = self.client.get(self.url, {"period": "1m"})
        self.assertEqual(response.status_code, 200)
        items = response.context["items"]
        names = [i["ingredient__name"] for i in items]
        self.assertIn("Apple", names)
        self.assertNotIn("Milk", names)
        totals = {i["ingredient__name"]: i["total_quantity"] for i in items}
        self.assertEqual(totals["Apple"], 2)
