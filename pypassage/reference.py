# -*- coding: utf-8 -*-
import bibledata
from collections import defaultdict

## Long term ##
#Implement string parsing



class Passage(object):
    def __init__(self, book, start_chapter=None, start_verse=None, end_chapter=None, end_verse=None, end_book=None, translation="ESV"):
        """
        Intialise and check passage reference. Missing information is filled in where it can be
        safely assumed. Infeasible passages will raise InvalidPassageException.
        
        'book' may be a name (e.g. "Genesis"), a standard abbreviation (e.g. "Gen") or an
        integer (i.e. Genesis = 1, Revelation = 66).
        """
        self.bd = bd = bible_data(translation)

        #Check book start
        if isinstance(book, int) or isinstance(book, long):
            #Book has been provided as an integer (1-66)
            self.start_book_n = int(book)
            if self.start_book_n > 66 or self.start_book_n < 1:
                raise InvalidPassageException()
        else:
            #Assume book has been provided as a string
            self.start_book_n = bd.book_numbers.get(str(book).upper(),None)
            if self.start_book_n == None:
                raise InvalidPassageException()

        #Check book end
        if end_book == None or end_book == '':
            self.end_book_n = self.start_book_n
        else:
            if isinstance(end_book, int) or isinstance(end_book, long):
                #Book has been provided as an integer (1-66)
                self.end_book_n = int(end_book)
                if self.end_book_n > 66 or self.end_book_n < 1:
                    raise InvalidPassageException()
            else:
                #Assume end_book has been provided as a string
                self.end_book_n = bd.book_numbers.get(str(end_book).upper(),None)
                if self.end_book_n == None:
                    raise InvalidPassageException()

        #Check and normalise numeric reference inputs
        (self.start_chapter, self.start_verse, self.end_chapter, self.end_verse) = check_reference(bd, self.start_book_n, start_chapter, start_verse, self.end_book_n, end_chapter, end_verse)

        #Raise exception now if passage is still invalid
        if not self.is_valid():
            raise InvalidPassageException()

        #Finish by setting self.start and self.end integers
        return self.setint()

    """ Old variable name for start_book_n was book_n """
    def get_book_n(self):
        return self.start_book_n
    def set_book_n(self, book_n):
        self.start_book_n = book_n
    book_n = property(get_book_n, set_book_n)

    def setint(self):
        """
        Set integers self.start and self.end, in order to represent passage starting and endings in purely
        numeric form. Primarily useful for efficient database filtering of passages.
        First two numerals are book number (eg. Gen = 01 and Rev = 66). Next three numerals are chapter, and
        final three numerals are verse. Thus Gen 3:5 is encoded as 001003005.
        """
        self.start = (self.start_book_n * 10**6) + (self.start_chapter * 10**3) + self.start_verse
        self.end   = (self.end_book_n * 10**6) + (self.end_chapter * 10**3)   + self.end_verse
        return
    
    def is_valid(self):
        """
        Return boolean denoting whether this Passage object is a valid reference or not. Note that while object
        always ensures passage is valid when it is instantiated, it may have been made invalid at a later time.
        """
        #Does start book exist?
        if isinstance(self.start_book_n, int):
            if self.start_book_n > 66 or self.start_book_n < 1:
                return False
        else: return False
        #What about end book?
        if isinstance(self.end_book_n, int):
            if self.end_book_n < self.start_book_n or self.end_book_n > 66:
                return False
        else: return False
        #Are start_chapter, start_verse, end_chapter, and end_verse all integers?
        if not isinstance(self.start_chapter,int) or not \
          isinstance(self.start_verse,int) or not \
          isinstance(self.end_chapter,int) or not \
          isinstance(self.end_verse,int):
            return False
        #Do start/end chapter/verse exist?
        if self.start_chapter < 1 or self.start_verse < 1 or self.end_chapter < 1 or self.end_verse < 1:
            return False
        if self.bd.number_chapters[self.start_book_n] < self.start_chapter: return False
        if self.bd.number_chapters[self.end_book_n] < self.end_chapter: return False
        if self.bd.last_verses[self.start_book_n, self.start_chapter] < self.start_verse: return False
        if self.bd.last_verses[self.end_book_n, self.end_chapter] < self.end_verse: return False
        #Is end after start?
        if self.start_book_n == self.end_book_n:
            if self.start_chapter > self.end_chapter:
                return False
            elif self.start_chapter == self.end_chapter:
                if self.end_verse < self.start_verse:
                    return False
        #Are either start or end verses missing verses?
        if self.start_verse in self.bd.missing_verses.get((self.start_book_n, self.start_chapter),[]):
            return False
        if self.end_verse in self.bd.missing_verses.get((self.end_book_n, self.end_chapter),[]):
            return False
        #Everything checked; return True
        return True
    
    def number_verses(self, per_book=False):
        """
        Return number of verses in this passage as integer, or if per_book=True,
        as a dictionary keyed to book_n.
        """
        if not self.is_valid():
            return {} if per_book else 0

        if self.start_book_n == self.end_book_n and self.start_chapter == self.end_chapter:
            #Passsage spans just one chapter in one book
            n = self.end_verse - self.start_verse + 1
            missing = self.bd.missing_verses.get((self.start_book_n,self.start_chapter),[])
            for verse in missing:
                if verse >= self.start_verse and verse <= self.end_verse: n -= 1
            if per_book:
                return {self.start_book_n: n}
            else:
                return n
        else:
            #Passage spans multiple chapters or books
            n_book = defaultdict(lambda: 0)
            #Verses from end chapter
            n_book[self.end_book_n] += self.end_verse
            missing_end = self.bd.missing_verses.get((self.end_book_n,self.end_chapter),[])
            for verse in missing_end:
                if verse <= self.end_verse: n_book[self.end_book_n] -= 1
            #Verses from start chapter
            n_book[self.start_book_n] += (self.bd.last_verses[self.start_book_n,self.start_chapter] - self.start_verse + 1)
            missing_start = self.bd.missing_verses.get((self.start_book_n,self.start_chapter),[])
            for verse in missing_start:
                if verse >= self.start_verse: n_book[self.start_book_n] -= 1
            #Verses from in-between chapters
            if self.start_book_n == self.end_book_n:
                #Single-book reference
                for chapter in range(self.start_chapter+1,self.end_chapter):
                    n_book[self.start_book_n] += self.bd.last_verses[self.start_book_n,chapter] - len(self.bd.missing_verses.get((self.start_book_n,chapter),[]))
            else:
                #Verses from intermediate chapters in end book
                for chapter in range(1,self.end_chapter):
                    n_book[self.end_book_n] += self.bd.last_verses[self.end_book_n,chapter] - len(self.bd.missing_verses.get((self.end_book_n,chapter),[]))
                #Verses from intermediate chapters in start book
                for chapter in range(self.start_chapter+1, self.bd.number_chapters[self.start_book_n]+1):
                    n_book[self.start_book_n] += self.bd.last_verses[self.start_book_n,chapter] - len(self.bd.missing_verses.get((self.start_book_n,chapter),[]))
                #Verses from chapters in intermediate books
                for book in range(self.start_book_n+1,self.end_book_n):
                    for chapter in range(1,self.bd.number_chapters[book]+1):
                        n_book[book] += self.bd.last_verses[book,chapter] - len(self.bd.missing_verses.get((book,chapter),[]))
            if per_book:
                return n_book
            else:
                return sum([v for b,v in n_book.items()])
        
    def proportion_of_book(self, per_book=False):
        """
        Return proportion of current book represented by this passage, or if per_book=True,
        a dictionary of proportions keyed to book_n.
        """
        length_perbook = self.number_verses(per_book=True)
        total_perbook = book_total_verses(self.bd, self.start_book_n, self.end_book_n)
        proportions = {}
        for (book_n, n) in length_perbook.items():
            proportions[book_n] = float(n)/total_perbook[book_n]
        if per_book:
            return proportions
        else:
            return sum([p for b,p in proportions.items()])

    def complete_book(self):
        """ Return True if this reference is for a whole book. """
        return (self.start_book_n == self.end_book_n and
                self.start_chapter == self.start_verse == 1 and
                self.end_chapter == self.bd.number_chapters[self.start_book_n] and
                self.end_verse   == self.bd.last_verses[self.start_book_n, self.end_chapter])
    
    def complete_chapter(self, multiple=False):
        """
        Return True if this reference is for a (single) whole chapter.
        Alternatively, if multiple=True, this returns true if reference is for any number of whole chapters.
        """
        single_chapter = (self.start_book_n == self.end_book_n and self.start_chapter == self.end_chapter)
        return (self.start_verse == 1 and
                (multiple == True or single_chapter) and
                self.end_verse == self.bd.last_verses[self.end_book_n, self.end_chapter])

    def truncate(self, number_verses=None, proportion_of_book=None):
        """
        Return truncated version of passage if longer than given restraints, or else return self.

        Arguments:
        number_verses -- Maximum number of verses that passage may be
        proportion_of_book -- Maximum proportion of book that passage may be;
            measured in terms of number of verses.

        For example:
        >>> Passage('Gen').truncate(number_verses=150)
        Passage(book=1, start_chapter=1, start_verse=1, end_chapter=6, end_verse=12)

        """
        #Check current length and length of limits
        current_length = len(self)
        limit = current_length
        if number_verses != None:
            if number_verses < limit: limit = number_verses
        if proportion_of_book != None:
            from math import ceil
            length_perbook = self.number_verses(per_book=True)
            total_perbook = book_total_verses(self.bd, self.start_book_n, self.end_book_n)
            v = 0
            #Iterate through all books in this passage, to check that all books
            #satisfy proportion_of_book constraint. Limit is in first book that
            #violates constraint.
            for book_n in range(self.start_book_n, self.end_book_n+1):
                if length_perbook[book_n] <= proportion_of_book * total_perbook[book_n]:
                    v += length_perbook[book_n]
                else:
                    v += int(ceil(proportion_of_book * total_perbook[book_n]))
                    break
            if v < limit: limit = v
        if current_length <= limit:
            #No need to shorten; return as-is.
            return self
        else:
            #Check that we're non-negative
            if limit < 1: return None
            #We need to shorten this passage. Iterate through chapters until we've reached our quota of verses.
            n = 0
            for book_n in range(self.start_book_n, self.end_book_n+1):
                if book_n == self.start_book_n:
                    start_chapter = self.start_chapter
                else:
                    start_chapter = 1
                if book_n == self.end_book_n:
                    end_chapter = self.end_chapter
                else:
                    end_chapter = self.bd.number_chapters[book_n] 
                for chapter in range(start_chapter, end_chapter+1):
                    if book_n == self.start_book_n and chapter == self.start_chapter:
                        start_verse = self.start_verse
                    else:
                        start_verse = 1
                    if book_n == self.end_book_n and chapter == self.end_chapter:
                        end_verse = self.end_verse
                    else:
                        end_verse = self.bd.last_verses[book_n, chapter]
                    valid_verses = [v for v in range(start_verse, end_verse+1) if v not in self.bd.missing_verses.get((book_n, chapter),[]) ]
                    if n + len(valid_verses) >= limit:
                        return Passage(self.start_book_n, self.start_chapter, self.start_verse, chapter, valid_verses[limit-n-1], book_n)
                    else:
                        n += len(valid_verses)
            #If we've got through the loop and haven't returned a Passage object, something's gone amiss.
            raise Exception("Error: Could not truncate passage. Got to end_verse and still hadn't reached current_length.")
        
    def extend(self, number_verses=None, proportion_of_book=None):
        """
        Return extended version of passage if shorter than given restraints, or else return self.
        Same arguments as used by self.truncate
        
        For example, returning the first 50% of the verses in Genesis:
        >>> Passage('Gen',1,1).extend(proportion_of_book=0.5)
        Passage(book=1, start_chapter=1, start_verse=1, end_chapter=27, end_verse=38)
        
        """
        print "Deprecated function; does not understand multi-book passages. Use PassageDelta object instead."
        #First check if starting reference is valid:
        if (self.start_book_n > 66 or self.start_book_n < 1) or (self.start_chapter < 1 or self.start_chapter > self.bd.number_chapters[self.start_book_n]) or (self.start_verse < 1 or self.start_verse > self.bd.last_verses[self.start_book_n, self.start_chapter]): return None
        #Check current length and length of limits
        current_length = len(self)
        limit = current_length
        if number_verses != None:
            if number_verses > limit: limit = number_verses
        if proportion_of_book != None:
            verses = int(proportion_of_book * book_total_verses(self.bd, self.start_book_n))
            if verses > limit: limit = verses
        if current_length >= limit:
            #No need to extend; return as-is.
            return self
        else:
            #We need to extend this passage. Do this by truncating the longest passage possible.
            end_chapter = self.bd.number_chapters[self.start_book_n]
            end_verse = self.bd.last_verses[self.start_book_n, end_chapter]
            return Passage(self.start_book_n, self.start_chapter, self.start_verse, end_chapter, end_verse).truncate(number_verses=limit)
        
    def reference_string(self, abbreviated = False, dash = "-"):
        """ Return string representation of passage reference. """
        if not self.is_valid(): return 'Invalid passage'
        #Create string
        if self.start_book_n == self.end_book_n:
            #Single-book passage
            book_n = self.start_book_n
            if self.bd.number_chapters[book_n] == 1:
                #Single-chapter book
                book = book_name(self.bd, book_n, abbreviated)
                if self.start_verse == self.end_verse:
                    return book + " " + str(self.start_verse)
                elif self.start_verse == 1 and self.end_verse == self.bd.last_verses[book_n, 1]:
                    return book
                else:
                    return book + " " + str(self.start_verse) + dash + str(self.end_verse)
            else:
                #Multi-chapter book
                if self.start_chapter == self.end_chapter:
                    if book_n == 19:
                        book = book_name(self.bd, book_n, abbreviated, True)
                    else:
                        book = book_name(self.bd, book_n, abbreviated)
                    if self.start_verse == self.end_verse:
                        return book + " " + str(self.start_chapter) + ":" + str(self.start_verse)
                    elif self.start_verse == 1 and self.end_verse == self.bd.last_verses[book_n, self.start_chapter]:
                        return book + " " + str(self.start_chapter)
                    else:
                        return book + " " + str(self.start_chapter) + ":" + str(self.start_verse) + dash + str(self.end_verse)
                else:
                    book = book_name(self.bd, book_n, abbreviated)
                    if self.start_verse == 1 and self.end_verse == self.bd.last_verses[book_n, self.end_chapter]:
                        if self.start_chapter == 1 and self.end_chapter == self.bd.number_chapters[book_n]:
                            return book
                        else:
                            return book + " " + str(self.start_chapter) + dash + str(self.end_chapter)
                    else:
                        return book + " " + str(self.start_chapter) + ":" + str(self.start_verse) + dash + str(self.end_chapter) + ":" + str(self.end_verse)
        else:
            first_book = book_name(self.bd, self.start_book_n, abbreviated)
            last_book = book_name(self.bd, self.end_book_n, abbreviated)
            if self.start_verse == 1 and self.end_verse == self.bd.last_verses[self.end_book_n, self.end_chapter]:
                if self.end_chapter == self.bd.number_chapters[self.end_book_n]:
                    #Whole books
                    return first_book + dash + last_book
                else:
                    #Whole chapter reference
                    return first_book + " " + str(self.start_chapter) + dash + last_book + " " + str(self.end_chapter)
            else:
                return first_book + " " + str(self.start_chapter) + ":" + str(self.start_verse) +\
                       dash + last_book + " " + str(self.end_chapter) + ":" + str(self.end_verse)


    def osis_reference(self):
        """
        Return reference using the formal OSIS cannonical reference system.
        See http://www.bibletechnologies.net/ for details
        """
        return bibledata.osis.normative_book_names[self.start_book_n] + "." + str(self.start_chapter) + "." + str(self.start_verse) + "-" +\
               bibledata.osis.normative_book_names[self.end_book_n] + "." + str(self.end_chapter) + "." + str(self.end_verse)
    
    def text(self, **kwargs):
        """
        Return the Bible text for this passage, AND a boolean indicating
        whether passage was shortened to comply with API conditions.
        """
        return self.bd.get_passage_text(self, **kwargs)

    def __str__(self):
        """
        x.__str__() <==> str(x)
        Return passage string.
        """
        return self.reference_string()
    
    def __unicode__(self):
        """
        x.__unicode__() <==> unicode(x)
        Return unicode version of passage string, using en-dash for ranges.
        """
        return unicode(self.reference_string(dash=u"–"))
    
    def abbr(self):
        """ Return abbreviated passage string """
        return self.reference_string(abbreviated=True)
    
    def uabbr(self):
        """ Return unicode-type abbreviated passage string, using en-dash for ranges. """
        return unicode(self.reference_string(abbreviated=True, dash=u"–"))
    
    def __len__(self):
        """
        x.__len__() <==> len(x)
        Return number of verses in passage.
        """
        return int(self.number_verses())
    
    def __repr__(self):
        """
        x.__repr__() <==> x
        """
        return "Passage(book="+repr(self.start_book_n)+", start_chapter="+repr(self.start_chapter)+", start_verse="+repr(self.start_verse)+", end_book="+repr(self.end_book_n)+", end_chapter="+repr(self.end_chapter)+", end_verse="+repr(self.end_verse)+")"
    
    def __cmp__(self, other):
        """ Object sorting function. Sorting is based on start chapter/verse. """
        return cmp(self.start, other.start)
    
    def __eq__(self,other):
        """
        x.__eq__(y) <==> x == y
        Equality checking.
        """
        if not isinstance(other, Passage): return False
        if (self.start_book_n == other.start_book_n) and (self.start_chapter == other.start_chapter) and (self.start_verse == other.start_verse) and (self.end_book_n == other.end_book_n) and (self.end_chapter == other.end_chapter) and (self.end_verse == other.end_verse):
            return True
        else:
            return False
        
    def __ne__(self,other):
        """
        x.__ne__(y) <==> x != y
        Inequality checking.
        """
        return not self.__eq__(other)
    
    def __add__(self,other):
        """
        x.__add__(y) <==> x + y
        Addition. PassageCollection object returned.
        """
        if isinstance(other,Passage):
            return PassageCollection(self,other)
        elif isinstance(other,PassageCollection):
            return PassageCollection(self,other)
        else:
            return NotImplemented



class PassageCollection(list):
    """
    Class to contain list of Passage objects and derive corresponding reference strings
    """
    def __init__(self, *args):
        """
        PassageCollection initialisation. Passages to be in collection may be passed in directly or as lists.
        For example, the following is valid:
        PassageCollection( Passage('Gen'), Passage('Exo'), [Passage('Mat'), Passage('Mar')])
        """
        passages = []
        for arg in args:
            if isinstance(arg, Passage):
                passages.append(arg)
            elif isinstance(arg, list):
                for item in arg:
                    if isinstance(item, Passage): passages.append(item)
        super(PassageCollection, self).__init__(passages)
                    
    def reference_string(self, abbreviated=False, dash="-"):
        """
        x.reference_string() <==> str(x)
        Return string representation of passage references.
        """
        #First checking easy options.
        if len(self) == 0: return ""
        if len(self) == 1: return str(self[0])
        
        #Filtering out any invalid passages
        passagelist = [p for p in self if p.is_valid()]
        if len(passagelist) == 0: return "Invalid passages"

        #Group any consecutive single-book passages within same book
        groups = []; i=0;
        while i < len(passagelist):
            group_start = i
            book = passagelist[i].start_book_n
            if passagelist[i].start_book_n == passagelist[i].end_book_n:
                #Single-book passage. Find all other single-book passages within the same book
                while i+1 < len(passagelist) and passagelist[i+1].start_book_n == book and passagelist[i+1].end_book_n == book:
                    i += 1
            group_end = i
            groups.append(passagelist[group_start:group_end+1])
            i += 1
        
        #Create strings for each group (of consecutive passages within the same book)
        group_strings = [];
        for group in groups:
            if len(group) == 1:
                group_strings.append(group[0].reference_string(abbreviated))
                continue
            else:
                if group[0].start_book_n != group[0].end_book_n:
                    raise Exception("Error: Could not generate reference string. Multi-book passage group but len(group) != 1.")
            if group[0].bd.number_chapters[group[0].start_book_n] == 1:
                #Group of reference(s) from a single-chapter book
                parts = []
                for p in group:
                    if p.start_verse == p.end_verse:
                        parts.append(str(p.start_verse))
                    else:
                        parts.append(str(p.start_verse) + dash + str(p.end_verse))
                book = book_name(group[0].bd, group[0].start_book_n, abbreviated)
                group_strings.append(book + " " + ", ".join(parts))
            else:
                #Group of references from multi-chapter book
                if (len(group) == 1 and group[0].complete_book() == 1.0):
                    #Special case where there is only one reference in bunch, and that reference is for a whole book.
                    group_strings.append(book_name(group[0].bd, group[0].start_book_n, abbreviated))
                else:
                    #For readability and simplicity, this part of the algorithm is within the MCBGroup class
                    bunched = MCBGroup()
                    for p in group: bunched.add(p)
                    group_strings.append(bunched.reference_string(abbreviated, dash))

        #Return completed string
        return "; ".join(group_strings)
    
    def text(self, **kwargs):
        """
        Return the Bible text for these passages, AND a boolean indicating
        whether passage was shortened to comply with API conditions.
        """
        return "\n\n".join([p.bd.get_passage_text(self, **kwargs) for p in self])

    def __add__(self,other):
        """
        x.__add__(y) <==> x + y
        Addition of PassageCollection objects
        """
        if isinstance(other,Passage):
            return PassageCollection(self,other)
        elif isinstance(other,PassageCollection):
            return PassageCollection(self,other)
        else:
            return NotImplemented
        
    def append(self, passage):
        """ Add a passage to the end of the collection """
        if isinstance(passage, Passage): super(PassageCollection, self).append(passage)

    def extend(self, L):
        """ Extend the collection by appending all the items in the given list """
        if isinstance(L, PassageCollection):
            super(PassageCollection, self).extend(L.passages)
        else:
            super(PassageCollection, self).extend(L)

    def insert(self, i, passage):
        """ Insert passage at a given position """
        if isinstance(passage, Passage): super(PassageCollection, self).insert(i, passage)

    def __str__(self):
        """
        x.__str__() <==> str(x)
        Return passage string
        """
        return self.reference_string()
    
    def __unicode__(self):
        """
        x.__unicode__() <==> unicode(x)
        Return unicode version of passage string. Uses en-dash for ranges.
        """
        return unicode(self.reference_string(dash=u"–"))
    
    def abbr(self):
        """
        Return abbreviated passage string
        """
        return self.reference_string(abbreviated=True)
    
    def uabbr(self):
        """
        Return unicode-type abbreviated passage string. Uses en-dash for ranges.
        """
        return unicode(self.reference_string(abbreviated=True, dash=u"–"))
    
    def __repr__(self):
        """
        x.__repr__() <==> x
        """
        return "PassageCollection(" + ", ".join([repr(x) for x in self]) + ")"



class PassageDelta(object):
    """
    Extension (or contraction) of passages, in chapter or verse increments.
    """
    def __init__(self, chapters=0, verses=0, passage_start=False):
        """
        PassageDelta initialisation.
        To add (or remove) chapters and/or verses to the START of a passage, set
        passage_start=True. Otherwise chapters/verses will be added to the END of a passage.
        """
        self.passage_start = passage_start
        self.delta_chapter = chapters
        self.delta_verse = verses

    def __add__(self,other):
        """
        x.__add__(y) <==> x + y
        Addition of Passage and PassageDelta objects
        """
        if isinstance(other,Passage):
            if not self.passage_start:
                #Add verses to END of passage
                #Check whether passage currently finishes at the end of a chapter
                if other.end_verse == other.bd.last_verses[other.start_book_n, other.end_chapter]:
                    finishes_at_end_of_chapter = True
                else:
                    finishes_at_end_of_chapter = False
                # Compute chapter difference operation first
                (end_book_n,
                    end_chapter,
                    end_verse) = delta_chapter(self.delta_chapter,
                                                other.end_book_n,
                                                other.end_chapter,
                                                other.end_verse,
                                                other.bd,
                                                finishes_at_end_of_chapter=finishes_at_end_of_chapter)
                # Verse difference operation
                (end_book_n,
                    end_chapter,
                    end_verse) = delta_verse(self.delta_verse,
                                                end_book_n,
                                                end_chapter,
                                                end_verse,
                                                other.bd)

                return Passage(other.start_book_n,
                                other.start_chapter,
                                other.start_verse,
                                end_chapter,
                                end_verse,
                                end_book_n)
            else:
                #Add verses to START of passage
                # Compute chapter difference operation first
                (start_book_n,
                    start_chapter,
                    start_verse) = delta_chapter(-self.delta_chapter,
                                                    other.start_book_n,
                                                    other.start_chapter,
                                                    other.start_verse,
                                                    other.bd)
                # Verse difference operation
                (start_book_n,
                    start_chapter,
                    start_verse) = delta_verse(-self.delta_verse,
                                                    start_book_n,
                                                    start_chapter,
                                                    start_verse,
                                                    other.bd)
                
                return Passage(start_book_n, 
                                start_chapter,
                                start_verse,
                                other.end_chapter,
                                other.end_verse,
                                other.end_book_n)
        else:
            return NotImplemented

    def __radd__(self,other):
        return self.__add__(other)

    def __repr__(self):
        """
        x.__repr__() <==> x
        """
        return "PassageDelta(chapters="+repr(self.delta_chapter)+", verses="+repr(self.delta_verse)+", passage_start="+repr(self.passage_start)+")"


def get_passage_text(passage, **kwargs):
    """ Get text of supplied Passage object """
    print "Deprecated function; use Passage.text or PassageCollection.text instead"
    translation = kwargs.get('translation',"ESV")
    return bible_data(translation).get_passage_text(passage, **kwargs)





# === Internal functions ===
def book_name(bible_data, book_n, abbreviated=False, single_psalm=False):
    """ Return full or abbreviated book name. """
    if abbreviated:
        return bible_data.book_names[book_n][2]
    else:
        if single_psalm:
            return "Psalm"
        else:
            return bible_data.book_names[book_n][1]

    
def book_total_verses(bible_data, start_book_n, end_book_n=None):
    """
    Return total number of verses in book or book range,
    as a dictionary keyed book to book_n
    """
    if end_book_n == None:
        end_book_n = start_book_n
    total_verses = defaultdict(lambda: 0)
    for book_n in range(start_book_n, end_book_n+1):
        for chapter in range(1, bible_data.number_chapters[book_n]+1):
            total_verses[book_n] += bible_data.last_verses[book_n,chapter] - len(bible_data.missing_verses.get((book_n,chapter),[]))
    return total_verses


def delta_chapter(chapter_difference, current_book_n, current_chapter, current_verse, bible_data, finishes_at_end_of_chapter=False):
    new_chapter = current_chapter + chapter_difference
    if new_chapter > bible_data.number_chapters[current_book_n]:
        #Got to end of book; need to go to next book
        overflow_chapters = new_chapter - bible_data.number_chapters[current_book_n]
        if current_book_n == 66:
            #Got to the end of the bible; can't go any further
            c = bible_data.number_chapters[current_book_n]
            v = bible_data.last_verses[current_book_n, c]
            return (current_book_n, c, v)
        else:
            return delta_chapter(overflow_chapters, current_book_n+1, 0, current_verse, bible_data, finishes_at_end_of_chapter)
    elif new_chapter < 1:
        #Got to start of book; need to go to previous book
        overflow_chapters = new_chapter - 1
        if current_book_n == 1:
            #Got to start of the bible; can't go any further
            return (1, 1, 1)
        else:
            c = bible_data.number_chapters[current_book_n-1]
            return delta_chapter(overflow_chapters, current_book_n-1, c+1, current_verse, bible_data, finishes_at_end_of_chapter)
    else:
        if finishes_at_end_of_chapter or current_verse > bible_data.last_verses[current_book_n, new_chapter]:
            current_verse = bible_data.last_verses[current_book_n, new_chapter]
        return (current_book_n, new_chapter, current_verse)


def delta_verse(verse_difference, current_book_n, current_chapter, current_verse, bible_data):
    new_verse = current_verse + verse_difference
    if new_verse > bible_data.last_verses[current_book_n, current_chapter]:
        #Got to end of chapter; need to go to next chapter
        overflow_verses =  new_verse - bible_data.last_verses[current_book_n, current_chapter]
        if current_chapter == bible_data.number_chapters[current_book_n]:
            #Got to end of book; need to go to next book
            if current_book_n == 66:
                #Got to end of the bible; can't go any further
                c = bible_data.number_chapters[current_book_n]
                v = bible_data.last_verses[current_book_n, c]
                return (current_book_n, c, v)
            else:
                return delta_verse(overflow_verses, current_book_n+1, 1, 0, bible_data)
        else:
            #Next chapter within the same book
            return delta_verse(overflow_verses, current_book_n, current_chapter+1, 0, bible_data)
    elif new_verse < 1:
        #Got to start of chapter; need to go to previous chapter
        overflow_verses = new_verse - 1
        if current_chapter == 1:
            #Got to start of book; need to go to previous book
            if current_book_n == 1:
                #Got to start of the bible; can't go any further
                return (1, 1, 1)
            else:
                c = bible_data.number_chapters[current_book_n-1]
                v = bible_data.last_verses[current_book_n-1, c]
                return delta_verse(overflow_verses, current_book_n-1, c, v+1, bible_data)
        else:
            c = current_chapter - 1
            v = bible_data.last_verses[current_book_n, c]
            return delta_verse(overflow_verses, current_book_n, c, v+1, bible_data)
    else:
        return (current_book_n, current_chapter, new_verse)


class MCBGroup(object):
    """
    Internal-use class for creating reference strings for groups of passages that are all from the same multi-chapter book
    """
    def __init__(self):
        self.bunches = defaultdict(lambda: []) #Dictionary of reference objects (each within a list), indexed by order that they were added
        self.full_chapter_bunch = defaultdict(lambda: False) #Boolean indicating whether corresponding self.bunches reference is for a full chapter
        self.order = 0
        self.last_full_chapter_loc = -1 #Order of last full-chapter reference
        self.last_partial_chapter = [None, -1] #[chapter, order] of last reference that wasn't a full chapter
        
    def add(self, reference):
        #Set the book_n variable if this is the first passage added
        if self.order == 0:
            self.start_book_n = reference.start_book_n
        else:
            if reference.start_book_n != self.start_book_n: raise Exception
        
        if reference.complete_chapter(multiple=True):
            #Reference is one or more full chapters in length
            if self.last_full_chapter_loc >= 0:
                #Last reference was a full chapter, so add it to previous 'bunch'
                self.bunches[self.last_full_chapter_loc].append(reference)
            else:
                #Add new bunch
                self.bunches[self.order].append(reference)
                self.last_full_chapter_loc = self.order
                self.full_chapter_bunch[self.order] = True
            #Reset last_partial_chapter
            self.last_partial_chapter = [None, -1]
        else:
            #Reference is not a full-chapter length passage
            if reference.start_chapter == reference.end_chapter:
                #Some verse range that is within the same chapter
                if reference.start_chapter == self.last_partial_chapter[0]:
                    #Same chapter as for last passage, so add to previous bunch
                    self.bunches[self.last_partial_chapter[1]].append(reference)
                else:
                    #Different to last passage
                    self.bunches[self.order].append(reference)
                    self.last_partial_chapter = [reference.start_chapter, self.order]
            else:
                #Verse range over two or more chapters, between arbitrary verses (e.g. 5:2-7:28)
                self.last_partial_chapter = [None, -1]
                self.bunches[self.order].append(reference)
            self.last_full_chapter_loc = -1
        self.order += 1
        
    def reference_string(self, abbreviated, dash):
        if self.order == 0:
            #No passages have been added to bunch; return blank.
            return ""

        #Helper functions
        def full_ch_ref(reference, verse_encountered):
            #Chapter string for references that are one or many full chapters
            if verse_encountered:
                if reference.start_chapter == reference.end_chapter:
                    return str(reference.start_chapter) + ":" + str(reference.start_verse) + dash + str(reference.end_verse)
                else:
                    return str(reference.start_chapter) + ":" + str(reference.start_verse) + dash + str(reference.end_chapter) + ":" + str(reference.end_verse)
            else:
                if reference.start_chapter == reference.end_chapter:
                    return str(reference.start_chapter)
                else:
                    return str(reference.start_chapter) + dash + str(reference.end_chapter)
        def verses_only(reference):
            #Verse string
            if reference.start_verse == reference.end_verse:
                return str(reference.start_verse)
            else:
                return str(reference.start_verse) + dash + str(reference.end_verse)

        #List of passage bunches, sorted by order-of-addition
        ordered_bunches = sorted(self.bunches.items(), cmp=lambda x,y: cmp(x[0], y[0]) )
        
        #Iterate through bunches, creating their textual representations
        textual_bunches = []
        verse_encountered = False
        for order, bunch in ordered_bunches:
            if self.full_chapter_bunch[order]:
                #All passages in this bunch are for full chapters
                    textual_bunches.append(", ".join([full_ch_ref(x, verse_encountered) for x in bunch]))
            else:
                #Not a full-chapter bunch.
                verse_encountered = True
                if len(bunch) == 1:
                    #NB: this bunch may be over two or more chapters
                    if bunch[0].start_chapter == bunch[0].end_chapter:
                        textual_bunches.append(str(bunch[0].start_chapter) + ":" + verses_only(bunch[0]))
                    else:
                        textual_bunches.append(str(bunch[0].start_chapter) + ":" + str(bunch[0].start_verse) + dash + str(bunch[0].end_chapter) + ":" + str(bunch[0].end_verse))
                    pass
                else:
                    #Guaranteed (via self.add() algorithm) to be within same chapter
                    textual_bunches.append(", ".join([str(bunch[0].start_chapter) + ":" + verses_only(x) for x in bunch]))
        if abbreviated:
            book = bibledata.book_names[self.start_book_n][2]
        else:
            book = bibledata.book_names[self.start_book_n][1]
        return book + " " + ", ".join(textual_bunches)


def check_reference(bd, start_book_n, start_chapter=None, start_verse=None, end_book_n=None, end_chapter=None, end_verse=None):
    """
    Check and normalise numeric reference inputs (start_chapter, start_verse, end_chapter and end_verse)
    Where possible, missing inputs will be inferred. Thus for example, if start_chapter and end_chapter
    are provided but start_verse and end_verse are not, it will be assumed that the whole chapter was intended.
    """

    if end_book_n == None: end_book_n = start_book_n

    #Check which numbers have been provided.
    sc = sv = ec = ev = True
    if start_chapter == None: sc = False
    if start_verse == None: sv = False
    if end_chapter == None: ec = False
    if end_verse == None: ev = False

    #Require that numbers are not negative.
    if (sc and start_chapter < 1) or (sv and start_verse < 1) or (ec and end_chapter < 1) or (ev and end_verse < 1):
        raise InvalidPassageException("Reference cannot include negative numbers")

    #Now fill out missing information.

    #No chapter/verse information at all: Assume reference was for full book
    if not sc and not sv and not ec and not ev:
        start_chapter = start_verse = 1
        end_chapter = bd.number_chapters[end_book_n]
        end_verse = bd.last_verses[end_book_n, end_chapter]
        return (start_chapter, start_verse, end_chapter, end_verse)

    if start_book_n == end_book_n and bd.number_chapters[start_book_n] == 1:
        #Checks for single-chapter books
        
        if not sc and not sv:
            #No start information at all; assume 1
            start_chapter = start_verse = 1
            sc = sv = True

        if sv and ev and (not sc or start_chapter == 1) and (not ec or end_chapter == 1):
            #Verse range provided properly; start or end chapters either
            #correct (i.e., 1) or missing
            start_chapter = end_chapter = 1
        elif sc and ec and not sv and not ev:
            #Chapter range provided, when it should have been verse range (useful for parsers)
            start_verse = start_chapter
            end_verse = end_chapter
            start_chapter = end_chapter = 1
        elif sc and not ec and not ev:
            #No end chapter or verse provided
            if sv:
                #Start chapter and start verse have been provided. Interpret this as a verse *range*.
                #That is, Passage('Phm',3,6) will be interpreted as Phm 1:3-6
                end_verse = start_verse
                start_verse = start_chapter
                start_chapter = end_chapter = 1
            else:
                #Only start chapter has been provided, but because this is a single-chapter book,
                #this is equivalent to a single-verse reference
                end_verse = start_verse = start_chapter
                start_chapter = end_chapter = 1
        elif sv and not sc and not ec and not ev:
            #Only start verse entered
            end_verse = start_verse
            start_chapter = end_chapter = 1
        else:
            raise InvalidPassageException()
        
    else:
        #Checks for multi-chapter books. There are fewer valid ways to enter these references than for single-chapter books!

        #If start chapter or start_verse are missing, assume 1
        if not sc: start_chapter = 1
        if not sv: start_verse = 1

        #If end chapter is missing, we must assume it is the same as the start chapter (which hopefully is not missing)
        if not ec:
            end_chapter = start_chapter

        #If end verse is missing, we need to do some more digging
        if not ev:
            if start_chapter == end_chapter:
                #Single-chapter reference
                if sv:
                    #Start verse was provided; assume reference is a single-verse reference
                    end_verse = start_verse
                else:
                    #Neither start verse or end verse were provided. start_verse has already
                    #been set to 1 above; set end_verse to be the last verse of the chapter.
                    end_verse = bd.last_verses.get((end_book_n, end_chapter),1)
                    #NB: if chapter doesn't exist, passage won't be valid anyway
            else:
                #Multi-chapter reference
                #Start by truncating end_chapter if necessary
                if end_chapter > bd.number_chapters[end_book_n]:
                    end_chapter = bd.number_chapters[end_book_n]
                    #NB: if start chapter doesn't exist, passage won't be valid anyway
                #Assume end_verse is equal to the last verse of end_chapter
                end_verse = bd.last_verses[end_book_n, end_chapter]

    #Check that end chapter and end verse are both valid; truncate if necessary
    if end_chapter > bd.number_chapters[end_book_n]:
        end_chapter = bd.number_chapters[end_book_n]
        end_verse = bd.last_verses[end_book_n, end_chapter]
    elif end_verse > bd.last_verses[end_book_n, end_chapter]:
        end_verse = bd.last_verses[end_book_n, end_chapter]

    #Check that neither the start or end verses are "missing verses"; shorten if not
    missing_start = bd.missing_verses.get((start_book_n, start_chapter),[])
    while start_verse in missing_start:
        start_verse += 1
    missing_end = bd.missing_verses.get((end_book_n, end_chapter),[])
    while end_verse in missing_end:
        end_verse -= 1
    if end_verse < 1:
        end_chapter -= 1
        end_verse = bd.last_verses[end_book_n, end_chapter]
    
    #Finished checking passage; return normalised values
    return (start_chapter, start_verse, end_chapter, end_verse)


class InvalidPassageException(Exception):
    pass


def bible_data(translation):
    """ Private method to return bible-data module corresponding to given translation """
    if translation == "ESV":
        return bibledata.esv
    else:
        return bibledata.esv


if __name__ == "__main__":
    import doctest
    doctest.testmod()
