from django.contrib import admin
from django.db import models
from django.contrib.admin import SimpleListFilter


class DeckActiveFilter(SimpleListFilter):
    title = 'deck active status'
    parameter_name = 'deck_active'

    def lookups(self, request, model_admin):
        return (
            ('yes', 'Active'),
            ('no', 'Inactive'),
        )

    def queryset(self, request, queryset):
        if self.value() == 'yes':
            return queryset.filter(deck__is_active=True)
        if self.value() == 'no':
            return queryset.filter(deck__is_active=False)
        return queryset


class DeckVersion(models.Model):
    version_number = models.IntegerField()
    deck = models.ForeignKey('altered.Deck', on_delete=models.PROTECT, related_name='versions')
    content = models.TextField(null=True, blank=True)
    change_cost = models.DecimalField(max_digits=6, decimal_places=2, default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    cards = models.ManyToManyField(
        'altered.Card',
        through='altered.CardWithQuantity',
        related_name='deck_versions',
        blank=True,
    )

    def __str__(self):
        return f"{self.deck.name} (v{self.version_number})"


@admin.register(DeckVersion)
class DeckVersionAdmin(admin.ModelAdmin):
    list_display = ('deck', 'version_number', 'change_cost')
    list_filter = (DeckActiveFilter, 'deck',)
    ordering = ('version_number',)

    def get_queryset(self, request):
        """
        Override default queryset to only show versions of active decks by default.
        """
        queryset = super().get_queryset(request)
        return queryset.filter(deck__is_active=True)
