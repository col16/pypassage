from reference import PassageCollection as C, Passage as P, PassageDelta as D, InvalidPassageException
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
        self.assertEqual(P(book='GEN', start_chapter=1, start_verse=1, end_chapter=2, end_verse=1), P(1,1,1,2,1))
        self.assertEqual(P(book='GEN', start_chapter=1, start_verse=1, end_book='REV', end_chapter=1, end_verse=1).is_valid(), True)
        self.assertEqual(P(book='GEN', end_book='LEV').is_valid(), True)

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

    #Testing of passage if parameters changed manually
    def test_manual_change(self):
        p = P('Gen',1,1)
        #Change end verse
        p.end_verse = 3
        self.assertEqual(p, P('Gen',1,1,1,3))
        #Change book
        p.start_book_n = p.end_book_n = 2
        self.assertEqual(p, P('Exo',1,1,1,3))
        p.book_n = 3 #Deprecated version of start_book_n
        p.end_book_n = 3
        self.assertEqual(p, P('Lev',1,1,1,3))
        #Change start_chapter in a way that would make passage invalid
        p.start_chapter = 4
        self.assertEqual(p.is_valid(), False)

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
            P('Exo',1,1,1,1,'Gen') #end_book is before start_book
            self.fail("P('Exo',1,1,1,1,'Gen') should have raised exception")
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
        #Multiple book passages
        self.assertEqual(str(P('Gen',1,1,4,5,'Exo')), "Genesis 1:1-Exodus 4:5")
        self.assertEqual(str(P('Gen',3,1,2,25,'Exo')), "Genesis 3-Exodus 2")
        self.assertEqual(str(P('Gen',1,1,2,25,'Exo')), "Genesis 1-Exodus 2")
        self.assertEqual(str(P('Gen',1,1,22,21,'Rev')), "Genesis-Revelation")

    def test_osis_passage_strings(self):
        self.assertEqual(P('GEN',1,1,1,2).osis_reference(), "Gen.1.1-Gen.1.2")
        self.assertEqual(P('GEN',1,1,1,2,'Exo').osis_reference(), "Gen.1.1-Exod.1.2")
    
    #Testing number of verses within passage
    def test_number_verses(self):
        #Single verse
        self.assertEqual(len(P('GEN',1,1,1,1)), 1)
        #Within same chapter
        self.assertEqual(len(P('GEN',1,1,1,3)), 3)
        self.assertEqual(P('GEN',1,1,1,3).number_verses(per_book=True), {1:3})
        #Consecutive chapters
        self.assertEqual(len(P('GEN',1,1,2,1)), 32)
        self.assertEqual(P('GEN',1,1,2,1).number_verses(per_book=True), {1:32})
        #More than two chapters
        self.assertEqual(len(P('GEN',1,30,3,2)), 29)
        #Intermediate single-chapter book
        self.assertEqual(len(P('1Jo',5,20,1,2,'3Jo')), 17)
        self.assertEqual(P('1Jo',5,20,1,2,'3Jo').number_verses(per_book=True), {62: 2, 63: 13, 64: 2})
        #Intermediate multi-chapter book
        self.assertEqual(len(P('Heb',12,28,2,2,'1Pe')), 162)
    def test_number_verses_with_missing_verses(self):
        self.assertEqual(len(P('MAT',12,46,12,48)), 2)
        self.assertEqual(len(P('MAR',9,1,9,45)), 44)
        self.assertEqual(len(P('MAR',7,15,12,1)), 193)
        self.assertEqual(len(P('Joh',21,24,1,2,'Rom')), 1007) #All of Acts

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
        #John 1 has 51 verses; truncate to 40
        j1t = P('Joh',1).truncate(number_verses=40)
        self.assertEqual(len(j1t), 40)
        self.assertEqual(j1t, P('Joh',1,1,1,40))
        #John 1-2 is 76 verses total; truncate to 60 (i.e. finishing at 2:9)
        j12t = P('Joh',start_chapter=1,end_chapter=2).truncate(number_verses=60)
        self.assertEqual(len(j12t), 60)
        self.assertEqual(j12t, P('Joh',1,1,2,9))
        #John has 878 verses, after accounting for one missing verse. Truncate to 50% (439 verses)
        jt = P('Joh').truncate(proportion_of_book=0.5)
        self.assertEqual(len(jt), 439)
        self.assertEqual(jt, P('Joh',1,1,10,3))
        #Mark has 673 verses. Truncate to 50%, which should be rounded UP to 337 verses.
        mt = P('Mar').truncate(proportion_of_book=0.5)
        self.assertEqual(len(mt), 337)
        self.assertEqual(mt, P('Mar',1,1,9,15))
        #Truncate Mark to 50 verses (finishing 2:5), but provide number as proportion-of-book
        m50 = P('Mar').truncate(proportion_of_book=50./673)
        self.assertEqual(len(m50), 50)
        self.assertEqual(m50, P('Mar',1,1,2,5))

        #Multi-book passage tests
        #Matthew 28 has 20 verses and Mark 1 has 45 verses. Truncate to 30 verses.
        multi1 = P('Mat',28,1,1,45,'Mar').truncate(number_verses=30)
        self.assertEqual(len(multi1),30)
        self.assertEqual(multi1, P('Mat',28,1,1,10,'Mar'))
        #Mat 28 is significantly less than 50% of the book of Matthew. But adding the
        #whole book of Mark and truncating the total passage to 50% should truncate it
        #at the half-way point through Mark.
        markt = P('Mar').truncate(proportion_of_book=0.5)
        multi2 = P('Mat',28,1,16,20,'Mar').truncate(proportion_of_book=0.5)
        self.assertEqual(markt.end_book_n, multi2.end_book_n)
        self.assertEqual(markt.end_chapter, multi2.end_chapter)
        self.assertEqual(markt.end_verse, multi2.end_verse)
        #Luke 24 has 53 verses, the book of John has 878 verses, and Acts 1 has 26
        #verses (957 verses total). Truncate to 940 verses long.
        multi3 = P('Luk',24,1,1,26,'Act').truncate(number_verses=940)
        self.assertEqual(multi3, P('Luk',24,1,1,9,'Act'))


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
        #A. Single-passage collections
        self.assertEqual(str(C(P('Eph',1))), "Ephesians 1")
        self.assertEqual(str(C(P('Eph',1,5))), "Ephesians 1:5")
        self.assertEqual(str(C(P('Eph',1,5,1,9))), "Ephesians 1:5-9")
        self.assertEqual(str(C(P('Eph',1,1,5,33))), "Ephesians 1-5")
        
        #B. All within the same book and same chapter
        self.assertEqual(str(C(P('Eph',1,1),P('Eph',1,3),P('Eph',1,5))), "Ephesians 1:1, 1:3, 1:5")
        self.assertEqual(str(C(P('Eph',1,9),P('Eph',1,3),P('Eph',1,5))), "Ephesians 1:9, 1:3, 1:5")
        self.assertEqual(str(C(P('Eph',1,9),P('Eph',1,13,1,17))), "Ephesians 1:9, 1:13-17")
        self.assertEqual(str(C(P('Eph',1,1,1,9),P('Eph',1,15))), "Ephesians 1:1-9, 1:15")
        self.assertEqual(str(C(P('Eph',1,1),P('Eph',1,3,1,7),P('Eph',1,15))), "Ephesians 1:1, 1:3-7, 1:15")
        
        #C. Different chapters but same book
        self.assertEqual(str(C(P('Eph',1),P('Eph',3),P('Eph',5))), "Ephesians 1, 3, 5")
        self.assertEqual(str(C(P('Eph',1),P('Eph',3),P('Eph',5,9))), "Ephesians 1, 3, 5:9")
        self.assertEqual(str(C(P('Eph',1),P('Eph',3,1,4,9),P('Eph',3,5))), "Ephesians 1, 3:1-4:9, 3:5")
        #As soon as a verse is mentioned, the following references must all be chapter and verse
        self.assertEqual(str(C(P('Eph',1,1),P('Eph',3),P('Eph',5))), "Ephesians 1:1, 3:1-21, 5:1-33")
        self.assertEqual(str(C(P('Eph',1),P('Eph',3,5),P('Eph',6))), "Ephesians 1, 3:5, 6:1-24")
        self.assertEqual(str(C(P('Eph',1),P('Eph',3,1,4,32),P('Eph',5,5),P('Eph',6))), "Ephesians 1, 3-4, 5:5, 6:1-24")
        self.assertEqual(str(C(P('Eph',1),P('Eph',3,1,3,9),P('Eph',5))), "Ephesians 1, 3:1-9, 5:1-33")
        
        #D. Different books, but individual references all just from one book
        self.assertEqual(str(C(P('Eph',1),P('Gen',3,2),P('Mat',5))), "Ephesians 1; Genesis 3:2; Matthew 5")
        self.assertEqual(str(C(P('Eph',1,1,1,2),P('Mat',5))), "Ephesians 1:1-2; Matthew 5")
        self.assertEqual(str(C(P('Eph'),P('Mat',5))), "Ephesians; Matthew 5")
        #Consecutive passages from same book
        self.assertEqual(str(C(P('Eph',1),P('Gen',1),P('Gen',3),P('Gen',5),P('Mat',5))), "Ephesians 1; Genesis 1, 3, 5; Matthew 5")
        self.assertEqual(str(C(P('Eph',1),P('Gen',1,1),P('Gen',1,3),P('Gen',1,5),P('Mat',5),P('Mat',9),P('Mat',1))), "Ephesians 1; Genesis 1:1, 1:3, 1:5; Matthew 5, 9, 1")
        self.assertEqual(str(C(P('Eph',1),P('Eph',3),P('Eph',5,9),P('Mat',5))), "Ephesians 1, 3, 5:9; Matthew 5")
        self.assertEqual(str(C(P('Eph',1),P('Eph',3),P('Eph',5,9,6,2),P('Mat',5))), "Ephesians 1, 3, 5:9-6:2; Matthew 5")
        self.assertEqual(str(C(P('Eph',start_chapter=1,end_chapter=3),P('Eph',4))), "Ephesians 1-3, 4")
        #As soon as a verse is mentioned, the following references must all be chapter and verse
        self.assertEqual(str(C(P('Eph',1,1),P('Eph',3),P('Eph',5,9),P('Mat',5))), "Ephesians 1:1, 3:1-21, 5:9; Matthew 5")
        self.assertEqual(str(C(P('Eph',1),P('Gen',3,2),P('Gen',3,6),P('Gen',8),P('Mat',5))), "Ephesians 1; Genesis 3:2, 3:6, 8:1-22; Matthew 5")
        self.assertEqual(str(C(P('Eph',1,1),P('Eph',3),P('Eph',5),P('Mat',5))), "Ephesians 1:1, 3:1-21, 5:1-33; Matthew 5")
        
        #E. Single-chapter books
        self.assertEqual(str(C(P('Phm',1),P('Phm',1,3,1,6),P('Phm',15))), "Philemon 1, 3-6, 15")
        self.assertEqual(str(C(P('Mat',1),P('Phm',1,3,1,6),P('Phm',15),P('Rev'))), "Matthew 1; Philemon 3-6, 15; Revelation")

        #F. Multi-book passages
        # Single-passage collection
        self.assertEqual(str(C(P('Gen',1,1,4,5,'Exo'))), "Genesis 1:1-Exodus 4:5")
        self.assertEqual(str(C(P('Gen',1,1,2,25,'Exo'))), "Genesis 1-Exodus 2")
        self.assertEqual(str(C(P('Gen',1,1,22,21,'Rev'))), "Genesis-Revelation")
        # Consecutive passage ending points
        self.assertEqual(str(C(P('Gen',1,1,4,5,'Exo'),P('Exo',4,6))), "Genesis 1:1-Exodus 4:5; Exodus 4:6")
        self.assertEqual(str(C(P('Gen',1,1,2,25,'Exo'),P('Exo',3))), "Genesis 1-Exodus 2; Exodus 3")
        self.assertEqual(str(C(P('Gen',3,1,2,25,'Exo'),P('Exo',3,1))), "Genesis 3-Exodus 2; Exodus 3:1")
        self.assertEqual(str(C(P('Gen',1,1,1,25,'Jude'),P('Rev'))), "Genesis-Jude; Revelation")
        #Consecutive passage starting points
        self.assertEqual(str(C(P('Gen',1),P('Gen',3,1,1,22,'Exo'))), "Genesis 1; Genesis 3-Exodus 1")
        self.assertEqual(str(C(P('Gen',1),P('Gen',2),P('Gen',3,1,1,22,'Exo'))), "Genesis 1, 2; Genesis 3-Exodus 1")
        self.assertEqual(str(C(P('Gen',1,1),P('Gen',1,2),P('Gen',1,3,1,2,'Exo'))), "Genesis 1:1, 1:2; Genesis 1:3-Exodus 1:2")
        self.assertEqual(str(C(P('Gen'),P('Exo',1,1,27,34,'Lev'))), "Genesis; Exodus-Leviticus")

        #G. Abbreviated strings
        self.assertEqual(C(P('Eph',1),P('Gen',3,2),P('Gen',3,6),P('Gen',8),P('Mat',5)).abbr(), 'Eph 1; Gn 3:2, 3:6, 8:1-22; Mt 5')


class TestPassageDelta(unittest.TestCase):

    def test_delta_chapter_with_passage_end(self):
        #Adding chapters to the end of a passage
        #Normal behaviour is to increment end_chapter; leaving end_verse unchanged
        self.assertEqual(P('Gen',1,1,2,3)+D(chapters=1), P('Gen',1,1,3,3))
        self.assertEqual(D(chapters=1)+P('Gen',1,1,2,3), P('Gen',1,1,3,3))
        #If incrementing end_chapter means end_verse is past end of chapter, end_verse is truncated
        self.assertEqual(P('Gen',1,1,1,27)+D(chapters=1), P('Gen',1,1,2,25))
        #Special case for passages that finish at the end of a chapter already:
        #here end verse is equal to the last verse of incremented chapter
        self.assertEqual(P('Gen',3,1,3,24)+D(chapters=1), P('Gen',3,1,4,26))
        #Delta chapter pushing reference out into next book (NB: Gen has 50 chapters, Exo has 40)
        self.assertEqual(P('Gen',1,1)+D(chapters=50), P('Gen',1,1,1,1,'Exo'))
        self.assertEqual(P('Gen',3,1,3,24)+D(chapters=50), P('Gen',3,1,3,22,'Exo'))
        self.assertEqual(P('Gen',1,1)+D(chapters=90), P('Gen',1,1,1,1,'Lev'))
        #Delta chapter taking through to end of the bible (NB: total of 1189 chapters in the bible)
        self.assertEqual(P('Gen',1,1)+D(chapters=1190), P('Gen',1,1,22,21,'Rev'))
    def test_negative_delta_chapter_with_passage_end(self):
        #Here we want to REMOVE chapters from the end of the passage;
        #leaving passage shorter than it was
        self.assertEqual(P('Gen',1,1,3,1)+D(chapters=-1), P('Gen',1,1,2,1))
        #Automatic truncation of end verse
        self.assertEqual(P('Gen',3,1,4,26)+D(chapters=-1), P('Gen',3,1,3,24))
        #Special case for passages finishing at the end of a chapter
        self.assertEqual(P('Gen',1,1,2,25)+D(chapters=-1), P('Gen',1,1,1,31))
        #Delta chapter pushing reference back into previous book
        self.assertEqual(P('Gen',1,1,10,1,'Exo')+D(chapters=-10), P('Gen',1,1,50,1))
        self.assertEqual(P('Gen',1,1,10,1,'Exo')+D(chapters=-20), P('Gen',1,1,40,1))
        #Delta chapter greater than length of passage
        try:
            p = P('Gen',2,1)+D(chapters=-1)
        except InvalidPassageException: pass
        #Special case where passage had started in Gen 1:1
        self.assertEqual(P('Gen',1,1,2,25)+D(chapters=-2), P('Gen',1,1))
    def test_delta_chapter_with_passage_start(self):
        #Adding chapters to the START of a passage
        self.assertEqual(P('Gen',2,1)+D(chapters=1, passage_start=True), P('Gen',1,1,2,1))
        #Adding more chapters than are available
        self.assertEqual(P('Gen',2,1)+D(chapters=3, passage_start=True), P('Gen',1,1,2,1))
        #Delta chapter pushing reference out into previous book
        self.assertEqual(P('Exo',2,1)+D(chapters=3, passage_start=True), P('Gen',49,1,2,1,'Exo'))
        #Truncation of start_verse
        self.assertEqual(P('Gen',4,26)+D(chapters=1, passage_start=True), P('Gen',3,24,4,26))
    def test_negative_delta_chapter_with_passage_start(self):
        #REMOVING chapters from the start of a passage
        self.assertEqual(P('Gen',4,1,5,32)+D(chapters=-1, passage_start=True), P('Gen',5,1,5,32))
        #Delta chapter pushing reference back into next book
        self.assertEqual(P('Gen',1,1,40,38,'Exo')+D(chapters=-50, passage_start=True), P('Exo',1,1,40,38))
        #Delta chapter greater than length of passage
        try:
            p = P('Gen',1,1)+D(chapters=-1, passage_start=True)
        except InvalidPassageException: pass
        #Truncation of start_verse
        self.assertEqual(P('Gen',1,31,5,32)+D(chapters=-1, passage_start=True), P('Gen',2,25,5,32))

    def test_delta_verse_with_passage_end(self):
        #Adding verses to the end of a passage
        self.assertEqual(P('Gen',1,1)+D(verses=1), P('Gen',1,1,1,2))
        #Pushing reference out into next chapter
        self.assertEqual(P('Gen',1,1)+D(verses=50), P('Gen',1,1,2,20))
        #Pushing reference out into next book
        self.assertEqual(P('Gen',1,1)+D(verses=1533), P('Gen',1,1,1,1,'Exo'))
        #Delta chapter taking through to end of the bible
        self.assertEqual(P('Rev',20,1)+D(verses=500), P('Rev',20,1,22,21))
    def test_negative_delta_verse_with_passage_end(self):
        #Removing verses from the end of a passage
        self.assertEqual(P('Gen',1,1,1,31)+D(verses=-1), P('Gen',1,1,1,30))
    def test_delta_verse_with_passage_start(self):
        #Adding verses to the start of a passage
        self.assertEqual(P('Gen',1,2)+D(verses=1, passage_start=True), P('Gen',1,1,1,2))
        #Back into previous chapter
        self.assertEqual(P('Gen',2,1)+D(verses=1, passage_start=True), P('Gen',1,31,2,1))
        self.assertEqual(P('Gen',2,1)+D(verses=31, passage_start=True), P('Gen',1,1,2,1))
        #Back into previous book
        self.assertEqual(P('Exo',1,1)+D(verses=1, passage_start=True), P('Gen',50,26,1,1,'Exo'))
        #Back to start of bible
        self.assertEqual(P('Gen',2,1)+D(verses=100, passage_start=True), P('Gen',1,1,2,1))
    def test_negative_delta_verse_with_passage_start(self):
        #Removing verses from the start of a passage
        self.assertEqual(P('Gen',1,1,1,31)+D(verses=-1, passage_start=True), P('Gen',1,2,1,31))
        #Shorter by a chapter
        self.assertEqual(P('Gen',1,31,2,1)+D(verses=-1, passage_start=True), P('Gen',2,1))
        #Shorter by a book
        self.assertEqual(P('Gen',50,26,1,1,'Exo')+D(verses=-1, passage_start=True), P('Exo',1,1))
        #Delta verse greater than length of passage
        try:
            p = P('Gen',1,1)+D(verses=-1, passage_start=True)
        except InvalidPassageException:
            pass


class TestPassageLookup(unittest.TestCase):
    def test_esv(self):
        self.assertEqual(P('Gen',1,1).text()[0], '   In the beginning, God created the heavens and the earth.')
        self.assertEqual(P('Gen',1,1).text(options={"include-passage-references":"true"})[0], 'Genesis 1:1\n   In the beginning, God created the heavens and the earth.')
        self.assertEqual(P('Gen',1,1).text()[0], '   In the beginning, God created the heavens and the earth.') #repeated, just to make sure cache didn't remember previous options
    def test_cache(self):
        #Initialise cache, setting total-consecutive-verse limit to 500 and proportion-of-book limit to 0.5
        book_limits = dict([(k,v*0.5) for (k,v) in bd.number_verses_in_book.items()])
        sc = text_cache.SimpleCache(500, book_limits)
        #Testing using Genesis, which has 1533 verses in it. 50% of book is 766 verses.
        #This should put 31 verses into cache
        (p,t) = P('Genesis',1).text(cache=sc)
        self.assertEqual(len(sc.cache),1)
        self.assertEqual(t,False) #passage should not have been tuncated
        #Add another 25 verses into cache (just checking normal behaviour)
        (p,t) = P('Genesis',2).text(cache=sc)
        self.assertEqual(len(sc.cache),2)
        self.assertEqual(t,False)
        #Now add a long passage: 711 verses. This should be truncated to 500 verses, and thus allow us to add another 210 verses to the cache. If it's not truncated however it will push us one verse over the 50% of book limit.
        (p,t) = P('Genesis',3,1,27,39).text(cache=sc)
        self.assertEqual(t,True) #passage should have been truncated
        self.assertEqual(len(sc.cache),3)
        #Now add something that should push two references out of the cache
        (p,t) = P('Genesis',27,40,34,28).text(cache=sc)
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
