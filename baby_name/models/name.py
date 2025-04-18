from django.contrib import admin
from django.db import models
from django.utils.translation import gettext_lazy as _


class Name(models.Model):
    name = models.CharField(max_length=200)
    sex = models.BooleanField(
        help_text="True for a girl"
    )
    source = models.CharField(max_length=50)
    tag = models.CharField(max_length=50, null=True, blank=True)

    def __str__(self):
        return self.name

    class Meta:
        unique_together = ('name', 'sex')


class CustomSexFilter(admin.SimpleListFilter):
    title = _("Sexe")
    parameter_name = "sex"

    def lookups(self, request, model_admin):
        return [
            ("1", _("Fille")),
            ("0", _("Garçon")),
        ]

    def queryset(self, request, queryset):
        if self.value() == "1":
            return queryset.filter(sex=True)
        elif self.value() == "0":
            return queryset.filter(sex=False)
        return queryset


@admin.register(Name)
class NameAdmin(admin.ModelAdmin):
    list_display = ('name', 'print_sex')
    list_filter = (CustomSexFilter, 'source', 'tag')
    search_fields = ["name"]
    ordering = ('name',)

    @admin.display(description="Sexe")
    def print_sex(self, obj):
        return "Fille" if obj.sex == True else "Garçon"
