from django.conf import settings
from django.contrib import admin
from django.db import models


class Simulation(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, null=True, blank=True)
    name = models.CharField(max_length=255, blank=True, null=True)
    house_cost = models.DecimalField(max_digits=12, decimal_places=2)
    initial_contribution = models.DecimalField(max_digits=12, decimal_places=2)
    duration = models.IntegerField()
    annual_rate = models.DecimalField(max_digits=5, decimal_places=2)
    comparative_rent = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    duration_before_usable = models.IntegerField(null=True, blank=True)
    use_real_estate_firm = models.BooleanField(default=True)
    sell_price_change = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)

    @property
    def capital(self):
        return self.house_cost - self.initial_contribution

    @property
    def monthly_interest_rate(self):
        return 0.01 * float(self.annual_rate) / 12

    @property
    def duration_in_month(self):
        return self.duration * 12

    @property
    def sell_price(self):
        if self.sell_price_change is None:
            return self.house_cost
        return (100 + self.sell_price_change) * self.house_cost / 100


@admin.register(Simulation)
class SimulationAdmin(admin.ModelAdmin):
    list_display = ('name', 'user', 'house_cost', 'initial_contribution', 'duration', 'annual_rate', 'comparative_rent')
    list_filter = ('user', 'duration', 'use_real_estate_firm')
    search_fields = ('name', 'user__username')
    readonly_fields = ('capital', 'monthly_interest_rate', 'duration_in_month', 'sell_price')
    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'user')
        }),
        ('House Details', {
            'fields': ('house_cost', 'initial_contribution', 'sell_price_change', 'use_real_estate_firm')
        }),
        ('Loan Details', {
            'fields': ('duration', 'annual_rate')
        }),
        ('Comparison', {
            'fields': ('comparative_rent', 'duration_before_usable')
        }),
        ('Calculated Fields', {
            'fields': ('capital', 'monthly_interest_rate', 'duration_in_month', 'sell_price'),
            'classes': ('collapse',)
        }),
    )
