"""
Example Django admin.py file for using with BiblePassage model in models.py
"""

from django.contrib import admin
from models import BiblePassage

class BiblePassageOptions(admin.ModelAdmin):
    list_display = ('__unicode__','is_reading','is_primary_passage')

admin.site.register(BiblePassage, BiblePassageOptions)
