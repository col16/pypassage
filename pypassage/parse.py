# -*- coding: utf-8 -*-
import re
from reference import Passage, PassageCollection
from bibledata import book_numbers


pattern = re.compile(ur"""
                     ([123I+]?\s*[a-zA-Z]+)
                     \s*
                     (\d{1,3})        #chapter
                     (?:
                        :
                        (\d{1,3})     #verse
                     )?               #zero or one repetition of the above group
                     (?:
                        [-–—]
                        (\d{1,3})     #chapter or verse, depending on above context
                        (?:
                            :
                            (\d{1,3})     #verse (if valid)
                        )?
                     )?
                     """, re.VERBOSE)


def passages_from_string(passage_string):
    # Check that passage_string isn't just a full book
    book_n = book_numbers.get(passage_string.upper(),None)
    if book_n != None:
        return PassageCollection(Passage(book_n))

    # Attempt full regex match
    match = pattern.search(passage_string)
    if match == None:
        return
    parts = match.groups()

    book = parts[0]
    start_chapter = int(parts[1])
    start_verse = int(parts[2]) if parts[2] != None else None
    end_chapter = int(parts[3]) if parts[3] != None else None
    end_verse = int(parts[4]) if parts[4] != None else None
    if start_verse and end_chapter and not end_verse:
        end_verse = end_chapter
        end_chapter = None

    return PassageCollection(Passage(book, start_chapter, start_verse, end_chapter, end_verse))
