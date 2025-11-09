from django.contrib.auth import get_user_model
from django.test import RequestFactory, TestCase
from django.urls import reverse

from the_bazaar.constants.character import Character
from the_bazaar.constants.item_size import ItemSize
from the_bazaar.constants.result import Result
from the_bazaar.models import Object
from the_bazaar.views.object_list import ObjectListView


class ObjectBestWinTests(TestCase):
    def test_best_win_derives_from_win_counters(self):
        obj = Object.objects.create(
            name="Silver Specialist",
            character=Character.DOOLEY,
            size=ItemSize.SMALL,
            silver_win_number=2,
        )
        self.assertEqual(obj.best_win, Result.SILVER_WIN)

        obj.gold_win_number = 1
        obj.save(update_fields=["gold_win_number"])
        obj.refresh_from_db()
        self.assertEqual(obj.best_win, Result.GOLD_WIN)

    def test_best_win_is_none_when_no_victories(self):
        obj = Object.objects.create(
            name="No Wins Yet",
            character=Character.MAK,
            size=ItemSize.MEDIUM,
        )
        self.assertIsNone(obj.best_win)


class ObjectListFilterTests(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.user = get_user_model().objects.create_user(
            username="staff",
            password="secret",
            is_staff=True,
        )

    def test_best_win_filter_returns_silver_objects(self):
        silver_object = Object.objects.create(
            name="Silver Relic",
            character=Character.PYGMALIEN,
            size=ItemSize.LARGE,
            silver_win_number=3,
        )
        request = self.factory.get(
            reverse("the_bazaar:object_list"),
            {"best_win": Result.SILVER_WIN},
        )
        request.user = self.user

        response = ObjectListView.as_view()(request)
        response.render()
        objects = list(response.context_data["objects"])
        self.assertIn(silver_object, objects)
