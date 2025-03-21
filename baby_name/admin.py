from django.contrib import admin
from django.utils.translation import gettext_lazy as _

from baby_name.models import Evaluation, Name

    

@admin.register(Evaluation)
class EvaluationAdmin(admin.ModelAdmin):
    list_display = ('name', 'user','score', 'elo')
    list_filter = ('user','score','name__sex')
    search_fields = ["name__name"]
