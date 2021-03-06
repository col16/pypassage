"""
Example Django models.py file
"""

from django.db import models
from django.core.validators import ValidationError
from pypassage import Passage, InvalidPassageException
from pypassage.bibledata import book_names
from django.conf import settings

# List of (book_n, name) tuples for dropdown list of bible books
book_choices = [(p[1][0], p[1][1]) for p in sorted(
    list(book_names.items()), key=lambda x: x[0])]


class BiblePassage(models.Model):
    start_book = models.CharField(max_length=3, choices=book_choices)
    start_chapter = models.IntegerField(blank=True)
    start_verse = models.IntegerField(blank=True)
    end_book = models.CharField(max_length=3, choices=book_choices, blank=True)
    end_chapter = models.IntegerField(blank=True)
    end_verse = models.IntegerField(blank=True)

    # In a church sermon setting, passages are usually readings, primary
    # passages, both, or neither.
    reading = models.BooleanField(
        default=False,
        help_text="Was this passage read out during the service?")
    primary_passage = models.BooleanField(
        default=False, help_text="Was this passage the topic of the talk?")

    # Starting and finishing integers, in order to represent passage starting
    # and endings in purely numeric form. Primarily useful for efficient
    # database filtering of passages.
    # First two numerals are book number (eg. Gen = 01 and Rev = 66). Next
    # three numerals are chapter, and final three numerals are verse. Thus
    # Gen 3:5 is encoded as 001003005.
    start = models.IntegerField(null=True, editable=False)
    end = models.IntegerField(null=True, editable=False)

    def __init__(self, *args, **kwargs):
        super(BiblePassage, self).__init__(*args, **kwargs)
        try:
            self.build_object()
            self.start = self.p.start
            self.end = self.p.end
        except InvalidPassageException as e:
            pass

    def build_object(self):
        self.p = Passage(self.start_book, self.start_chapter, self.start_verse,
                         self.end_chapter, self.end_verse, self.end_book)

    def clean(self):
        """
        Called (usually by admin page) for model validation
        """
        try:
            self.build_object()
        except InvalidPassageException as e:
            raise ValidationError("Invalid passage")
        self.start_book = book_names[self.p.start_book_n][0]
        self.start_chapter = self.p.start_chapter
        self.start_verse = self.p.start_verse
        self.end_book = book_names[self.p.end_book_n][0]
        self.end_chapter = self.p.end_chapter
        self.end_verse = self.p.end_verse
        self.start = self.p.start
        self.end = self.p.end

    def text(self, **kwargs):
        """
        Fetch biblical text that object represents
        """
        if getattr(self, 'p', None) == None:
            # No pypassage object p; attempt to create it
            if getattr(self, 'start_book', '') == '':
                # Assume passage hasn't yet been initialised; return blank
                return ""
            else:
                try:
                    self.build_object()
                except InvalidPassageException as e:
                    return "Invalid passage"
        (text, self.truncated) = self.p.text(**kwargs)
        return text

    def was_truncated(self):
        """
        Return boolean denoting whether text that was fetched was truncated
        """
        return getattr(self, 'truncated', False)

    def __unicode__(self):
        if getattr(self, 'p', None) == None:
            try:
                self.build_object()
            except InvalidPassageException as e:
                return "Invalid passage"
        return str(self.p)
