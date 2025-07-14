import json
from django.test import TestCase, Client
from django.urls import reverse
from django.utils import timezone

from shopping_list.models import Ingredient, ShoppingListItem
from shopping_list.models.ingredient_history import (
    IngredientHistory,
)  # Ensure correct import
from django.contrib.auth.models import User  # Correct import for the User model


class IngredientHistoryCreationTests(TestCase):

    def setUp(self):
        # Create a user if view requires authentication
        self.user = User.objects.create_user(
            username="testuser", password="password123", is_staff=True
        )
        self.client = Client()
        self.client.login(username="testuser", password="password123")

        # Create an Ingredient
        self.ingredient = Ingredient.objects.create(
            name="Test Apple", is_pantry_staples=False, unit="piece"
        )

        # Create a ShoppingListItem
        self.shopping_list_item = ShoppingListItem.objects.create(
            ingredient=self.ingredient, quantity=2.00
        )

        self.delete_url = reverse("shopping_list:shopping_list_delete")

    def test_ingredient_history_created_on_shopping_list_item_delete(self):
        """
        Test that an IngredientHistory record is created when a ShoppingListItem
        is deleted via the PlannedIngredientController.delete view.
        """
        self.assertEqual(IngredientHistory.objects.count(), 0)
        self.assertEqual(ShoppingListItem.objects.count(), 1)

        # Simulate a POST request to the delete view
        # The view expects a JSON body with 'planned_ingredient_id'
        response = self.client.post(
            self.delete_url,
            data=json.dumps({"planned_ingredient_id": self.shopping_list_item.id}),
            content_type="application/json",
        )

        self.assertEqual(response.status_code, 200)
        response_data = response.json()
        self.assertEqual(response_data["status"], "success")
        self.assertEqual(
            response_data["message"], "Item marked as bought and removed from list."
        )

        # Check that ShoppingListItem is deleted
        self.assertEqual(ShoppingListItem.objects.count(), 0)

        # Check that IngredientHistory record is created
        self.assertEqual(IngredientHistory.objects.count(), 1)
        history_entry = IngredientHistory.objects.first()
        self.assertIsNotNone(history_entry)
        self.assertEqual(history_entry.ingredient, self.ingredient)
        self.assertEqual(
            float(history_entry.quantity), float(self.shopping_list_item.quantity)
        )  # Compare as float due to DecimalField

        # Check bought_date is recent (within a reasonable delta, e.g., 5 seconds)
        self.assertTrue(
            (timezone.now() - history_entry.bought_date).total_seconds() < 5
        )

    def test_delete_missing_id(self):
        """Test delete request with missing planned_ingredient_id."""
        response = self.client.post(
            self.delete_url,
            data=json.dumps({}),  # Empty data
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 400)
        response_data = response.json()
        self.assertEqual(response_data["status"], "error")
        self.assertEqual(response_data["message"], "Missing planned_ingredient_id.")
        self.assertEqual(
            ShoppingListItem.objects.count(), 1
        )  # Item should not be deleted
        self.assertEqual(IngredientHistory.objects.count(), 0)  # No history created

    def test_delete_invalid_id(self):
        """Test delete request with an invalid (non-existent) planned_ingredient_id."""
        response = self.client.post(
            self.delete_url,
            data=json.dumps({"planned_ingredient_id": 9999}),  # Non-existent ID
            content_type="application/json",
        )
        # Django's get_object_or_404 raises Http404, which results in a 404 status code
        self.assertEqual(response.status_code, 404)
        self.assertEqual(
            ShoppingListItem.objects.count(), 1
        )  # Item should not be deleted
        self.assertEqual(IngredientHistory.objects.count(), 0)  # No history created

    def test_delete_invalid_json(self):
        """Test delete request with invalid JSON."""
        response = self.client.post(
            self.delete_url, data="this is not json", content_type="application/json"
        )
        self.assertEqual(
            response.status_code, 400
        )  # HttpResponseBadRequest("Invalid JSON.")
        # The response from HttpResponseBadRequest is not JSON, so no .json()
        self.assertIn("Invalid JSON", response.content.decode())
        self.assertEqual(ShoppingListItem.objects.count(), 1)
        self.assertEqual(IngredientHistory.objects.count(), 0)
