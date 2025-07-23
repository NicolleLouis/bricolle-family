from django.test import TestCase
from django.utils import timezone
from unittest.mock import patch

from altered.models import UniqueFlip


class UniqueFlipSignalTests(TestCase):
    @patch('altered.services.altered_fetch_unique_flip_data.requests.get')
    def test_fetch_data_after_create(self, mock_get):
        mock_response = mock_get.return_value
        mock_response.json.return_value = {
            'card': {
                'name': 'Test Name',
                'imagePath': '/img/test.png'
            }
        }
        mock_response.raise_for_status.return_value = None

        flip = UniqueFlip.objects.create(
            unique_id='ABC123',
            bought_price=10,
            bought_at=timezone.now(),
        )

        expected_url = f"https://api.altered.gg/cards/{flip.unique_id}?locale=fr-fr"
        mock_get.assert_called_once_with(expected_url, timeout=30)

        flip.refresh_from_db()
        self.assertEqual(flip.name, 'Test Name')
        self.assertEqual(flip.image_path, '/img/test.png')
