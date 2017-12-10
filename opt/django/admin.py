"""
Example Django admin.py file for using with BiblePassage model in models.py
"""

from django.contrib import admin
from models import BiblePassage

class BiblePassageOptions(admin.ModelAdmin):
	list_display = ('__unicode__','reading','primary_passage')
	fields = ('book','start_chapter','start_verse','end_chapter','end_verse','reading','primary_passage','text')
	readonly_fields = ('text',)

admin.site.register(BiblePassage, BiblePassageOptions)
