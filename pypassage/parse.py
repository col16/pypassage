# -*- coding: utf-8 -*-
import re
from reference import Passage, PassageCollection
from bibledata import book_numbers


pattern = re.compile(ur"""
                    ([123I+]?\s*[a-zA-Z]+)
                    \s*
                    (?:                
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
                    )?
                    """, re.VERBOSE)


def passages_from_string(input_string):
    passages = []

    # Attempt regex match of book+chapter/verse combinations
    matches = pattern.findall(input_string)

    # Assemble Passage objects
    for parts in matches:
        book = parts[0]
        book_n = book_numbers.get(book.upper(), None)

        if book_n != None:
            start_chapter = int(parts[1]) if parts[1] != "" else None
            start_verse = int(parts[2]) if parts[2] != "" else None
            end_chapter = int(parts[3]) if parts[3] != "" else None
            end_verse = int(parts[4]) if parts[4] != "" else None
            if start_verse and end_chapter and not end_verse:
                end_verse = end_chapter
                end_chapter = None

            passages.append(Passage(book_n, start_chapter, start_verse, end_chapter, end_verse))

    return PassageCollection(passages)
