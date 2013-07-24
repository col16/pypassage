from reference import PassageCollection as C, Passage as P, InvalidPassageException
import bibledata.esv as bd
from bibledata import text_cache
import unittest

class TestBookData(unittest.TestCase):

    def test_last_verses(self):
        for (book_number, chapters) in bd.number_chapters.items():
            for chapter in range(1,chapters+1):
                if bd.last_verses.get((book_number,chapter),None) == None:
                    self.fail("Could not find last_verses for book "+str(book_number)+" and chapter "+str(chapter))
            if bd.last_verses.get((book_number,chapters+1),None) != None:
                self.fail("last_verses found for book "+str(book_number)+" and chapter "+str(chapter)+", when this book was only supposed to have "+str(chapters)+" chapters")
        for ((book_number, chapter), verses) in bd.missing_verses.items():
            for verse in verses:
                if verse >= bd.last_verses[book_number,chapter]: self.fail("missing verse greater than or equal to corresponding last verse")

    def test_number_chapters_in_bible_A(self):
        self.assertEqual(len(bd.last_verses.items()), 1189)
    def test_number_chapters_in_bible_B(self):
        self.assertEqual(sum([chapters for (book, chapters) in bd.number_chapters.items()]), 1189)
    def test_sum_of_last_verses(self):
        self.assertEqual(sum([verses for (book_chapter,verses) in bd.last_verses.items()]), 31103)
    def test_number_missing_verses(self):
        self.assertEqual(sum([len(x) for (book_chapter,x) in bd.missing_verses.items()]), 17)
    def test_number_verses_in_book(self):
        self.assertEqual(bd.number_verses_in_book[62], 105)

    def test_abbreviations(self):
        found_3 = []
        found_std = []
        for book_n in range(1,67):
            (abbr_3,name,abbr_std) = bd.book_names.get(book_n,(None,None))
            if abbr_3 == None:
                self.fail("Abbreviation not found for book "+str(book_n))
            elif bd.book_numbers.get(abbr_3,None) != book_n:
                self.fail("book_number entry for "+str(abbr_3)+" not the same as its number in book_names dict")
            elif abbr_3 in found_3:
                self.fail("Duplicate found for three-letter code "+str(abbr_3))
            elif abbr_std in found_std:
                self.fail("Duplicate found for standard abbreviation "+str(abbr_std))
            found_3.append(abbr_3)
            found_std.append(abbr_std)


class TestPassage(unittest.TestCase):
    #Testing normal passage validation
    def test_normal_function(self):
        self.assertEqual(P(book='GEN', start_chapter=1, start_verse=1, end_chapter=2, end_verse=1).is_valid(), True)
        self.assertEqual(P(book='genesis', start_chapter=1, start_verse=1, end_chapter=2, end_verse=1).is_valid(), True)

    #Testing passage normalisation
    def test_multi_chapter_books(self):
        self.assertEqual(P(book='GEN', start_chapter=2, start_verse=6, end_chapter=3, end_verse=5).is_valid(), True)
        self.assertEqual(P(book='GEN', start_chapter=2, start_verse=6, end_chapter=3), P('Gen',2,6,3,24))
        self.assertEqual(P(book='GEN', start_chapter=2, start_verse=6, end_verse=7), P('Gen',2,6,2,7))
        self.assertEqual(P(book='GEN', start_chapter=2, end_chapter=3, end_verse=5), P('Gen',2,1,3,5))
        self.assertEqual(P(book='GEN', start_verse=6, end_chapter=3, end_verse=5), P('Gen',1,6,3,5))
        self.assertEqual(P(book='GEN', start_chapter=2, start_verse=6), P('Gen',2,6,2,6))
        self.assertEqual(P(book='GEN', start_chapter=2, end_chapter=3), P('Gen',2,1,3,24))
        self.assertEqual(P(book='GEN', start_chapter=2, end_verse=5), P('Gen',2,1,2,5))
        self.assertEqual(P(book='GEN', start_verse=6, end_chapter=3), P('Gen',1,6,3,24))
        self.assertEqual(P(book='GEN', start_verse=6, end_verse=7), P('Gen',1,6,1,7))
        self.assertEqual(P(book='GEN', end_chapter=3, end_verse=5), P('Gen',1,1,3,5))
        self.assertEqual(P(book='GEN', start_chapter=2), P('Gen',2,1,2,25))
        self.assertEqual(P(book='GEN', start_verse=6), P('Gen',1,6,1,6))
        self.assertEqual(P(book='GEN', end_chapter=3), P('Gen',1,1,3,24))
        self.assertEqual(P(book='GEN', end_verse=5), P('Gen',1,1,1,5))
        self.assertEqual(P(book='GEN'), P('Gen',1,1,50,26))
    def test_single_chapter_books(self):
        self.assertEqual(P(book='PHM', start_chapter=1, start_verse=5, end_chapter=1, end_verse=6), P(book='PHM', start_verse=5, end_verse=6))
        self.assertEqual(P(book='PHM', start_chapter=1, start_verse=5, end_verse=6), P(book='PHM', start_verse=5, end_verse=6))
        self.assertEqual(P(book='PHM', start_verse=5, end_chapter=1, end_verse=6), P(book='PHM', start_verse=5, end_verse=6))
        self.assertEqual(P(book='PHM', start_verse=5, end_verse=6).is_valid(), True)
        self.assertEqual(P(book='PHM', start_chapter=2, end_chapter=3), P(book='PHM', start_verse=2, end_verse=3))
        self.assertEqual(P(book='PHM', start_chapter=1, start_verse=6), P(book='PHM', start_verse=1, end_verse=6))
        self.assertEqual(P(book='PHM', start_chapter=3, start_verse=6), P(book='PHM', start_verse=3, end_verse=6))
        self.assertEqual(P(book='PHM', start_chapter=3), P(book='PHM', start_verse=3, end_verse=3))
        self.assertEqual(P(book='PHM', start_verse=6), P(book='PHM', start_verse=6, end_verse=6))
        self.assertEqual(P(book='PHM',end_verse=9), P(book='PHM', start_verse=1, end_verse=9))
        self.assertEqual(P(book='PHM'), P(book='PHM', start_verse=1, end_verse=25))

    #Testing correction of fixable errors
    def test_fixable(self):
        self.assertEqual(P('Gen',1,1,51,1), P('Gen',1,1,50,26)) #end_chapter is past end of book
        self.assertEqual(P('Gen',1,1,2,26), P('Gen',1,1,2,25)) #end_verse is greater than last verse for that chapter

    #Testing things that can't be fixed
    def test_unfixable(self):
        try:
            P('Ben',1,1,2,1)
            self.fail("P('Ben',1,1,2,1) should have raised exception")
        except InvalidPassageException: pass
        try:
            P('Gen',2,1,1,1) #end_chapter is before start_chapter
            self.fail("P('Gen',2,1,1,1) should have raised exception")
        except InvalidPassageException: pass
        try:
            P('Gen',1,5,1,1) #end_verse is before start_verse
            self.fail("P('Gen',1,5,1,1) should have raised exception")
        except InvalidPassageException: pass
        try:
            P('Gen',51) #start_chapter is past end of book
            self.fail("P('Gen',51) should have raised exception")
        except InvalidPassageException: pass
        try:
            P('Gen',0,1,2,1) #zero (or negative) chapter or verse
            self.fail("P('Gen',0,1,2,1) should have raised exception")
        except InvalidPassageException: pass
        try:
            P('Gen',1,32) #single verse that doesn't exist
            self.fail("P('Gen',1,32) should have raised exception")
        except InvalidPassageException: pass
        try:
            P('Gen',1,32,2,1) #start_verse is greater than last verse for that chapter
            self.fail("P('Gen',1,32,2,1) should have raised exception")
        except InvalidPassageException: pass
    def test_unfixable_single_chapter(self):
        try:
            #This one in particular could be interpretable. But for code/API simplicity and comprehensibility, it has been ignored.
            P('Phm',start_chapter=1,start_verse=1,end_chapter=7)
            self.fail("should have raised exception")
        except InvalidPassageException: pass
        try:
            P('Phm',start_verse=5,end_chapter=7,end_verse=9)
            self.fail("should have raised exception")
        except InvalidPassageException: pass
        try:
            P('Phm',start_chapter=3,end_verse=9)
            self.fail("should have raised exception")
        except InvalidPassageException: pass
        try:
            P('Phm',start_verse=5,end_chapter=7)
            self.fail("should have raised exception")
        except InvalidPassageException: pass
        try:
            P('Phm',end_chapter=7,end_verse=9)
            self.fail("should have raised exception")
        except InvalidPassageException: pass
        try:
            P('Phm',end_chapter=7)
            self.fail("should have raised exception")
        except InvalidPassageException: pass
        try:
            P(book='PHM', start_chapter=6, start_verse=3)
            self.fail("should have raised exception")
        except InvalidPassageException: pass

     
    #Testing passage strings
    def test_passage_strings(self):
        self.assertEqual(str(P(book='GEN', start_chapter=1, start_verse=1, end_chapter=1, end_verse=2)), "Genesis 1:1-2")
        self.assertEqual(str(P(book='GEN', start_chapter=1, start_verse=1, end_chapter=2, end_verse=1)), "Genesis 1:1-2:1")
        self.assertEqual(str(P(book='GEN', start_chapter=1, start_verse=3, end_chapter=2, end_verse=25)), "Genesis 1:3-2:25")
        self.assertEqual(str(P(book='GEN', start_chapter=1, start_verse=1, end_chapter=1, end_verse=31)), "Genesis 1")
        self.assertEqual(str(P(book='GEN', start_chapter=1, start_verse=1, end_chapter=5, end_verse=32)), "Genesis 1-5")
        self.assertEqual(str(P(book='GEN', start_chapter=1, end_chapter=2, end_verse=1)), "Genesis 1:1-2:1")
        self.assertEqual(str(P(book='GEN', start_chapter=1, start_verse=5, end_chapter=2)), "Genesis 1:5-2:25")
    	self.assertEqual(str(P(book='GEN', start_chapter=1, start_verse=1, end_chapter=50, end_verse=26)), "Genesis")
        self.assertEqual(str(P(book='PHM', start_verse=1, end_verse=5)), "Philemon 1-5")
        #Abbreviated version
        self.assertEqual(P(book='GEN', start_chapter=1, start_verse=1, end_chapter=1, end_verse=2).abbr(), "Gn 1:1-2")
        #Passage strings for Psalms, just to be really annoying
        self.assertEqual(str(P(book='PSA', start_chapter=21)), "Psalm 21") #Psalm, singular
        self.assertEqual(str(P(book='PSA', start_chapter=21, start_verse=1)), "Psalm 21:1") #Psalm, singular
        self.assertEqual(str(P(book='PSA', start_chapter=21, end_chapter=22)), "Psalms 21-22") #Psalms, plural

    def test_passage_strings(self):
        self.assertEqual(P(book='GEN', start_chapter=1, start_verse=1, end_chapter=1, end_verse=2).osisRef(), "Gen.1.1-Gen.1.2")
    
    #Testing number of verses within passage
    def test_number_verses(self):
        self.assertEqual(len(P(book='GEN', start_chapter=1, start_verse=1, end_chapter=1, end_verse=3)), 3)
        self.assertEqual(len(P(book='GEN', start_chapter=1, start_verse=1, end_chapter=2, end_verse=1)), 32)        
        self.assertEqual(len(P(book='GEN', start_chapter=1, start_verse=1, end_chapter=20, end_verse=18)), 514)
    def test_number_verses_with_missing_verses_in_middle(self):
        self.assertEqual(len(P(book='MAT', start_chapter=12, start_verse=46, end_chapter=12, end_verse=48)), 2)
        self.assertEqual(len(P(book='MAR', start_chapter=9, start_verse=1, end_chapter=9, end_verse=45)), 44)
        self.assertEqual(len(P(book='MAR', start_chapter=7, start_verse=15, end_chapter=12, end_verse=1)), 193)

    #Proportion of book
    def test_proportion_of_book(self):
        self.assertEqual(P(book='1JO', start_chapter=1, start_verse=1, end_chapter=2, end_verse=1).proportion_of_book(), 11.0/105.0)

    #Testing verses that don't exist
    def test_verse_that_doesnt_exist(self):
        try:
            P(book='MAT', start_chapter=12, start_verse=47, end_chapter=12, end_verse=47)
            self.fail("Single verse-reference that doesn't exist should have raised exception")
        except InvalidPassageException: pass
    def test_automatic_shortening(self):
        self.assertEqual(P(book='MAT', start_chapter=12, start_verse=47, end_chapter=17, end_verse=21),
                         P(book='MAT', start_chapter=12, start_verse=48, end_chapter=17, end_verse=20))
                         
    #Test passage truncation
    def test_trucation(self):
        self.assertEqual(P('Mar', 9, 1, 9, 50).truncate(number_verses=44), P(book=41, start_chapter=9, start_verse=1, end_chapter=9, end_verse=45))
        self.assertEqual(P('Mar', 9, 1, 9, 50).truncate(proportion_of_book = 45./673), P(book=41, start_chapter=9, start_verse=1, end_chapter=9, end_verse=47))
        self.assertEqual(P('Gen').truncate(proportion_of_book = 0.5), P('Gen',1,1,27,38))


class TestPassageCollection(unittest.TestCase):
    def test_init(self):
        self.assertEqual(C(P('Gen'),[P('Mat'),P('Mar')],P('Exo')),
                         C(P('Gen'),P('Mat'),P('Mar'),P('Exo')))
    def test_summation(self):
        r = C(P('Eph',1),P('Mat',1))
        self.assertEqual(P('Eph',1)+P('Mat',1), r)
        self.assertEqual(C(P('Eph',1))+P('Mat',1), r)
        self.assertEqual(P('Eph',1)+C(P('Mat',1)), r)
        self.assertEqual(C(P('Eph',1))+C(P('Mat',1)), r)
    def test_append(self):
        t = C(P('Eph',1))
        t.append(P('Mat',1))
        self.assertEqual(t, C(P('Eph',1),P('Mat',1)))
    def test_extend(self):
        t = C(P('Eph',1))
        t.extend([P('Mat',1),P('Mat',2)])
        self.assertEqual(t, C(P('Eph',1),P('Mat',1),P('Mat',2)))
    def test_insert(self):
        t = C(P('Eph',1),P('Mat',1),P('Mat',2))
        t.insert(1,P('Eph',2))
        self.assertEqual(t, C(P('Eph',1),P('Eph',2),P('Mat',1),P('Mat',2)))
    def test_iteration(self):
        t = C(P('Eph',1),P('Mat',1),P('Mat',2))
        for i, passage in enumerate(t):
            self.assertEqual(passage, t[i])
    def test_string(self):
        #Avoiding ambiguity is the highest priority here!
        #All within the same chapter
        self.assertEqual(str(C(P('Eph',1))), "Ephesians 1")
        self.assertEqual(str(C(P('Eph',1,5))), "Ephesians 1:5")
        self.assertEqual(str(C(P('Eph',1,5,1,9))), "Ephesians 1:5-9")
        self.assertEqual(str(C(P('Eph',1,1,5,33))), "Ephesians 1-5")
        self.assertEqual(str(C(P('Eph',1,1),P('Eph',1,3),P('Eph',1,5))), "Ephesians 1:1, 1:3, 1:5")
        self.assertEqual(str(C(P('Eph',1,9),P('Eph',1,3),P('Eph',1,5))), "Ephesians 1:9, 1:3, 1:5")
        self.assertEqual(str(C(P('Eph',1,9),P('Eph',1,13,1,17))), "Ephesians 1:9, 1:13-17")
        self.assertEqual(str(C(P('Eph',1,1,1,9),P('Eph',1,15))), "Ephesians 1:1-9, 1:15")
        self.assertEqual(str(C(P('Eph',1,1),P('Eph',1,3,1,7),P('Eph',1,15))), "Ephesians 1:1, 1:3-7, 1:15")
        #Different chapters
        self.assertEqual(str(C(P('Eph',1),P('Eph',3),P('Eph',5))), "Ephesians 1, 3, 5")
        self.assertEqual(str(C(P('Eph',1),P('Eph',3),P('Eph',5,9))), "Ephesians 1, 3, 5:9")
        self.assertEqual(str(C(P('Eph',1),P('Eph',3,1,4,9),P('Eph',3,5))), "Ephesians 1, 3:1-4:9, 3:5")
        self.assertEqual(str(C(P('Eph',1,1),P('Eph',3),P('Eph',5))), "Ephesians 1:1, 3:1-21, 5:1-33") #as soon as a verse is mentioned, the following references must all be chapter and verse
        self.assertEqual(str(C(P('Eph',1),P('Eph',3,5),P('Eph',6))), "Ephesians 1, 3:5, 6:1-24")
        self.assertEqual(str(C(P('Eph',1),P('Eph',3,1,4,32),P('Eph',5,5),P('Eph',6))), "Ephesians 1, 3-4, 5:5, 6:1-24")
        self.assertEqual(str(C(P('Eph',1),P('Eph',3,1,3,9),P('Eph',5))), "Ephesians 1, 3:1-9, 5:1-33")
        #Different books
        self.assertEqual(str(C(P('Eph',1),P('Gen',3,2),P('Mat',5))), "Ephesians 1; Genesis 3:2; Matthew 5")
        self.assertEqual(str(C(P('Eph',1),P('Gen',1),P('Gen',3),P('Gen',5),P('Mat',5))), "Ephesians 1; Genesis 1, 3, 5; Matthew 5")
        self.assertEqual(str(C(P('Eph',1),P('Gen',1,1),P('Gen',1,3),P('Gen',1,5),P('Mat',5),P('Mat',9),P('Mat',1))), "Ephesians 1; Genesis 1:1, 1:3, 1:5; Matthew 5, 9, 1")
        self.assertEqual(str(C(P('Eph',1,1,1,2),P('Mat',5))), "Ephesians 1:1-2; Matthew 5")
        self.assertEqual(str(C(P('Eph',1),P('Eph',3),P('Eph',5,9),P('Mat',5))), "Ephesians 1, 3, 5:9; Matthew 5")
        self.assertEqual(str(C(P('Eph',1),P('Eph',3),P('Eph',5,9,6,2),P('Mat',5))), "Ephesians 1, 3, 5:9-6:2; Matthew 5")
        self.assertEqual(str(C(P('Eph',start_chapter=1,end_chapter=3),P('Eph',4))), "Ephesians 1-3, 4")
        self.assertEqual(str(C(P('Eph',1,1),P('Eph',3),P('Eph',5,9),P('Mat',5))), "Ephesians 1:1, 3:1-21, 5:9; Matthew 5")
        self.assertEqual(str(C(P('Eph',1),P('Gen',3,2),P('Gen',3,6),P('Gen',8),P('Mat',5))), "Ephesians 1; Genesis 3:2, 3:6, 8:1-22; Matthew 5")
        self.assertEqual(str(C(P('Eph',1,1),P('Eph',3),P('Eph',5),P('Mat',5))), "Ephesians 1:1, 3:1-21, 5:1-33; Matthew 5")
        self.assertEqual(str(C(P('Eph'),P('Mat',5))), "Ephesians; Matthew 5")
        #Single-chapter books
        self.assertEqual(str(C(P('Phm',1),P('Phm',1,3,1,6),P('Phm',15))), "Philemon 1, 3-6, 15")


class TestPassageLookup(unittest.TestCase):
    def test_esv(self):
        self.assertEqual(bd.get_passage_text(P('Gen',1,1))[0], '   In the beginning, God created the heavens and the earth.')
        self.assertEqual(bd.get_passage_text(P('Gen',1,1),options={"include-passage-references":"true"})[0], 'Genesis 1:1\n   In the beginning, God created the heavens and the earth.')
        self.assertEqual(bd.get_passage_text(P('Gen',1,1))[0], '   In the beginning, God created the heavens and the earth.') #repeated, just to make sure cache didn't remember previous options
    def test_cache(self):
        #Initialise cache, setting total-consecutive-verse limit to 500 and proportion-of-book limit to 0.5
        book_limits = dict([(k,v*0.5) for (k,v) in bd.number_verses_in_book.items()])
        sc = text_cache.SimpleCache(500, book_limits)
        #Testing using Genesis, which has 1533 verses in it. 50% of book is 766 verses.
        #This should put 31 verses into cache
        (p,t) = bd.get_passage_text(P('Genesis',1), cache=sc)
        self.assertEqual(len(sc.cache),1)
        self.assertEqual(t,False) #passage should not have been tuncated
        #Add another 25 verses into cache (just checking normal behaviour)
        (p,t) = bd.get_passage_text(P('Genesis',2), cache=sc)
        self.assertEqual(len(sc.cache),2)
        self.assertEqual(t,False)
        #Now add a long passage: 711 verses. This should be truncated to 500 verses, and thus allow us to add another 210 verses to the cache. If it's not truncated however it will push us one verse over the 50% of book limit.
        (p,t) = bd.get_passage_text(P('Genesis',3,1,27,39), cache=sc)
        self.assertEqual(t,True) #passage should have been truncated
        self.assertEqual(len(sc.cache),3)
        #Now add something that should push two references out of the cache
        (p,t) = bd.get_passage_text(P('Genesis',27,40,34,28), cache=sc)
        self.assertEqual(len(sc.cache),2)
        self.assertEqual(t,False)


#class TestParsing(unittest.TestCase):
#    def test_reference_string_parsing(self):
#        self.assertEqual(passages_from_string("Gen"), C(P('Gen')) )
#        self.assertEqual(passages_from_string("Genesis"), C(P('Gen')) )
#        self.assertEqual(passages_from_string("Gen 1"), C(P('Gen',1)) )
#        self.assertEqual(passages_from_string("Gen 1:1"), C(P('Gen',1,1)) )
#        self.assertEqual(passages_from_string("Gen 1:1a"), C(P('Gen',1,1)) )
#        self.assertEqual(passages_from_string("Gen 1:1b"), C(P('Gen',1,1)) )
#        self.assertEqual(passages_from_string("Gen 1:1-3"), C(P('Gen',1,1,1,3)) )
#        self.assertEqual(passages_from_string("Gen 1:1-2:4"), C(P('Gen',1,1,2,4)) )
#        self.assertEqual(passages_from_string("Gen 1-2"), C(P('Gen',start_chapter=1,end_chapter=2)) )
#        self.assertEqual(passages_from_string("Gen 1-3:2"), C() ) #invalid; should not return any passage
#        self.assertEqual(passages_from_string("Gen 1,3,5"), C(P('Gen',1),P('Gen',3),P('Gen',5)) )
#        self.assertEqual(passages_from_string("Gen 1:1,3,5"), C(P('Gen',1,1),P('Gen',1,3),P('Gen',1,5)) )
#        self.assertEqual(passages_from_string("Gen 1,3:2,5"), C(P('Gen',1),P('Gen',3,2),P('Gen',5)) )
#        self.assertEqual(passages_from_string("Gen 1:1,3:2"), C(P('Gen',1,1),P('Gen',3,2)) )
#        self.assertEqual(passages_from_string("Gen 1:1-4,3:2"), C(P('Gen',1,1,1,4),P('Gen',3,2)) )
#        self.assertEqual(passages_from_string("Gen 1:1;5:2"), C(P('Gen',1,1),P('Gen',5,2)) )
#        self.assertEqual(passages_from_string("Gen 1-3,5:2"), C(P('Gen',start_chapter=1,end_chapter=3),P('Gen',5,2)) )
#        self.assertEqual(passages_from_string("Gen 1:3,5,7;2:4"), C(P('Gen',1,3),P('Gen',1,5),P('Gen',1,7),P('Gen',2,4)) )
#        self.assertEqual(passages_from_string("Gen 1:3;5;7;2:4"), C(P('Gen',1,3),P('Gen',5),P('Gen',7),P('Gen',2,4)) )
#        self.assertEqual(passages_from_string("Gen1.1,3.2"), C(P('Gen',1,1),P('Gen',3,2)) )
#        self.assertEqual(passages_from_string("2 Tim 1:1"), C(P('2Tim',1,1)) )
#        self.assertEqual(passages_from_string("2Tim 1:1"), C(P('2Ti',1,1)) )
#        self.assertEqual(passages_from_string("II Tim 1:1"), C(P('2Ti',1,1)) )
#        self.assertEqual(passages_from_string("Philemon 3-5"), C(P('Phm',start_chapter=3,end_chapter=5)) )
#        self.assertEqual(passages_from_string("Matt and Tim are cool"), C() ) #should not return any passage
#        self.assertEqual(passages_from_string("Matthew and John went skiing"), C() ) #should not return any passage
#        self.assertEqual(passages_from_string("love, 2 Cor"), C(P('2Co')) )
#        self.assertEqual(passages_from_string("Gen 3: the fall"), C(P('Gen',3)) )
#
#        #Long-term, we want to be able to be much more generic still. For example:
#        #self.assertEqual(passages_from_string("Genesis chapter 1, verses 3 to 5"), C(P('Gen',1,3,1,5)) )
#        #self.assertEqual(passages_from_string("Gen ch 1 v1"), C(P('Gen',1,1)) )
#        #self.assertEqual(passages_from_string("Gen 1, v1-3"), C(P('Gen',1,1,1,3)) )


if __name__ == '__main__': #If run as a command line script
    unittest.main()
