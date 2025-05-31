from django.test import TestCase
from django.urls import reverse
from altered.models import Game, Deck, Champion, DeckVersion
from altered.forms import GameForm
from django.contrib.auth.models import User


class GameFormTests(TestCase):
    def setUp(self):
        # Create a user
        self.user = User.objects.create_user(username='testuser', password='password')

        # Create a Champion
        self.champion = Champion.objects.create(name='Test Champion', faction='Test Faction')

        # Create a Deck
        self.deck = Deck.objects.create(name='Test Deck', user=self.user, altered_id="test_id")
        self.deck_version = DeckVersion.objects.create(deck=self.deck, version="1.0")


    def test_game_form_valid_data(self):
        form_data = {
            'deck': self.deck.id,
            'comment': 'Test comment',
            'is_win': True,
            'opponent_champion': self.champion.id,
        }
        form = GameForm(data=form_data)
        self.assertTrue(form.is_valid())

    def test_game_form_missing_data(self):
        form_data = {}  # Missing required fields
        form = GameForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('deck', form.errors)
        self.assertIn('is_win', form.errors)
        self.assertIn('opponent_champion', form.errors)


class GameViewTests(TestCase):
    def setUp(self):
        # Create a user
        self.user = User.objects.create_user(username='testuser', password='password')
        self.client.login(username='testuser', password='password')

        # Create a Champion
        self.champion = Champion.objects.create(name='Test Champion', faction='Test Faction')

        # Create a Deck
        self.deck = Deck.objects.create(name='Test Deck', user=self.user, altered_id="test_id")
        self.deck_version = DeckVersion.objects.create(deck=self.deck, version="1.0")

        self.game_form_url = reverse('altered:game_form')

    def test_game_form_view_get(self):
        response = self.client.get(self.game_form_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'altered/game_form.html')
        self.assertIsInstance(response.context['form'], GameForm)

    def test_game_form_view_post_success(self):
        form_data = {
            'deck': self.deck.id,
            'comment': 'Test submission',
            'is_win': False,
            'opponent_champion': self.champion.id,
        }
        response = self.client.post(self.game_form_url, data=form_data)
        self.assertEqual(response.status_code, 302)  # Should redirect on success
        self.assertRedirects(response, self.game_form_url)
        self.assertEqual(Game.objects.count(), 1)
        game = Game.objects.first()
        self.assertEqual(game.comment, 'Test submission')
        self.assertEqual(game.deck, self.deck)
        self.assertEqual(game.opponent_champion, self.champion)
        self.assertFalse(game.is_win)
        self.assertIsNotNone(game.deck_version) # Check that deck_version was set

    def test_game_form_view_post_invalid(self):
        form_data = {}  # Invalid data
        response = self.client.post(self.game_form_url, data=form_data)
        self.assertEqual(response.status_code, 200) # Should re-render the form
        self.assertTemplateUsed(response, 'altered/game_form.html')
        self.assertTrue(response.context['form'].errors)
        self.assertEqual(Game.objects.count(), 0)

# Make sure altered/tests/__init__.py exists
# If altered/models/champion.py or altered/models/deck.py have more required fields for creation,
# those will need to be added in the setUp methods.
