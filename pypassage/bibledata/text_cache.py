"""
Class(es) to cache bible passage text
"""
from collections import defaultdict


class SimpleCache:
   """
   In-memory passage-text cache that keeps track of how much it has cached and clears oldest items as API limits are violated.
   """
   def __init__(self, consecutive_verse_limit=None, book_specific_limits={}):
      """
      Initialise SimpleCache object
        'consecutive_verse_limit' is an integer representing the maximum number of consecutive verses that may be cached anywhere in the bible
        'book_specific_limits' is a dict keyed to book number that returns the maximum number of verses that may be cached from specific books
      """
      #User-defined limits
      if consecutive_verse_limit is None: consecutive_verse_limit = 1000
      self.absolute_limit = consecutive_verse_limit
      self.book_limits = book_specific_limits
      #Object stores text in self.cache: a dict storing tuples of (book_n, passage_length, passage_text) against user-provided keys
      self.cache = {}
      #Actual lengths of verses cached  is self.lengths, a dict of lists containing (length, key) tuples; keyed to book_n.
      self.lengths = defaultdict(lambda: [])
      
   def __setitem__(self, key, value):
      """
      Dictionary-like function to cache bible text against a user-supplied key.
      'value' should be a tuple of (book_n, passage_length, passage_text)
      """
      (book_n, passage_length, passage_text) = value
      if passage_length > self.absolute_limit: return None
      self.lengths[book_n].append((passage_length, key))
      self.cache[key] = (book_n, passage_length, passage_text)
      #Check total length and discard oldest if necessary
      while sum([x[0] for x in self.lengths[book_n]]) > self.book_limits.get(book_n,1000):
         (l, k) = self.lengths[book_n].pop(0)
         del self.cache[k]

   def __getitem__(self, key):
      """ Return tuple of (book_n, passage_length, passage_text) stored against 'key' """
      return self.cache[key]
   
   def get(self, key, alternative=None):
      """ Return tuple of (book_n, passage_length, passage_text) if it exists for this 'key'; otherwise return 'alternative' """
      return self.cache.get(key, alternative)


