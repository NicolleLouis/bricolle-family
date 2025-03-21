from django.contrib import admin
from django.utils.translation import gettext_lazy as _

from baby_name.models import Evaluation, Name


class CustomSexFilter(admin.SimpleListFilter):
    title = _("Sexe")  
    parameter_name = "sex"

    def lookups(self, request, model_admin):
        return [
            ("1", _("Fille")),  # True -> "Fille"
            ("0", _("Garçon")),  # False -> "Garçon"
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
    list_filter = (CustomSexFilter,)
    search_fields = ["name"]
    
    @admin.display(description="Sexe")
    def print_sex (self, obj):
        return "Fille" if obj.sex == True else "Garçon"
    

@admin.register(Evaluation)
class EvaluationAdmin(admin.ModelAdmin):
    list_display = ('name', 'user','score', 'elo')
    list_filter = ('user','score','name__sex')
    search_fields = ["name__name"]
