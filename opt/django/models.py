"""
Example Django models.py file
"""

from django.db import models
from django.core.validators import ValidationError
from pypassage import Passage, InvalidPassageException, get_passage_text
from pypassage.bibledata import book_names

book_choices = [(p[1][0],p[1][1]) for p in sorted(book_names.items(),cmp=lambda x,y: cmp(x[0], y[0]))] #a list of (book_n, name) tuples

class BiblePassage(models.Model):
    book = models.CharField(max_length=3, choices=book_choices)
    start_chapter = models.IntegerField(blank=True)
    start_verse = models.IntegerField(blank=True)
    end_chapter = models.IntegerField(blank=True)
    end_verse = models.IntegerField(blank=True)
    #In a church sermon setting, passages are usually readings, primary passages, both, or neither.
    reading = models.BooleanField(default=False)
    primary_passage = models.BooleanField(default=False)
    #Starting and finishing integers
    start = models.IntegerField(null=True,editable=False)
    end = models.IntegerField(null=True,editable=False)
    def __init__(self, *args, **kwargs):
        super(BiblePassage,self).__init__(*args, **kwargs)
        try:
            self.build_object()
            self.start = self.p.start
            self.end = self.p.end
        except passager.reference.InvalidPassageException, e:
            pass
    def build_object(self):
        self.p = Passage(self.book, self.start_chapter, self.start_verse, self.end_chapter, self.end_verse)
    def clean(self):
        """
        Called (usually by admin page) for model validation
        """
        try:
            self.build_object()
        except InvalidPassageException, e:
            raise ValidationError("Invalid passage")
        self.start_chapter = self.p.start_chapter
        self.start_verse = self.p.start_verse
        self.end_chapter = self.p.end_chapter
        self.end_verse = self.p.end_verse
        self.start = self.p.start
        self.end = self.p.end
    def text(self):
        """
        Fetch biblical text that object represents
        """
        if getattr(self,'p', None) == None:
            try:
                self.build_object()
            except InvalidPassageException, e:
                return u"Invalid passage"
        (text, self.truncated) = get_passage_text(self.p)
        return text
    def was_truncated(self):
        """
        Return boolean denoting whether text that was fetched was truncated
        """
        return getattr(self,'truncated', False)
    def __unicode__(self):
        if getattr(self,'p', None) == None:
            try:
                self.build_object()
            except InvalidPassageException, e:
                return u"Invalid passage"
        return unicode(self.p)
