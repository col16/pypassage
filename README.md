# PyPassage

**PyPassage** is a small Python module for working with bible passages/references. It can:

- [render reference strings](#reference-strings) sensibly and non-ambiguously; e.g. returning "Ephesians 1" when Ephesians 1:1-1:23 was specified, because there are only 23 verses in that chapter;
- [look up actual passage text](#looking-up-passage-text) using external API services;
- [fill in missing information where possible](#missing-information); e.g. inferring that for the inputs of `book="EPH"` and `start_chapter=1`, the whole Ephesians 1 chapter (verses 1 to 23) was intended;
- [verify that a passage is valid](#validity); e.g. telling you that Ephesians 99 and Genesis 3:5-1:2 can't exist;
- [add verses or chapters](#extending-a-passage) to the start or end of a passage, or [truncate](#passage-truncation) a passage to a given number of verses; such as for satisfying copyright restrictions; *and*
- [count the number of verses](#passage-length) in a passage. 

PyPassage now supports **multi-book passages**, such as 'Psalms-Proverbs'.


## Basic Usage

```python
from pypassage import Passage
p = Passage(book='Genesis', start_chapter=1, start_verse=1, end_chapter=2, end_verse=3)
```

Books may be specified as their full name (e.g. "Revelation"), a three-letter abbreviation (e.g. "Rev"), or the book number (e.g. 66). Passages with a different ending book are created using the `end_book` parameter:

```python
>>> str(Passage(book='Genesis', start_chapter=1, start_verse=1, end_chapter=22, end_verse=21, end_book='Rev'))
'Genesis-Revelation'
```

### Missing Information

Not all fields need to be provided. You may for example specify a single verse, a single chapter, or even a complete book:
```python
p_verse = Passage('2 Corinthians',4,7)
p_chapter = Passage('Romans',1)
p_book = Passage('Philippians')
```


## Validity

Invalid passages will throw an InvalidPassageException on instantiation:
```python
>>> p = Passage('Deu', -3)
Traceback (most recent call last):
  ...
reference.InvalidPassageException
```

Nevertheless, a valid passage may easily be made invalid after instantiation. Thus to check validity, you may call `is_valid()`:
```python
>>> p = Passage('2Co',3,12,3,18)
>>> p.end_verse = 99
>>> p.is_valid()
False
```


## Reference Strings

String representations of the passage reference can be created by simply calling `str` or `unicode`:
```python
>>> str(Passage('John',1,1,1,18))
'John 1:1-18'
>>> unicode(Passage('John',1,1,1,18))
u'John 1:1\u201318'
```
where \u2013 is the unicode en-dash character (used for ranges).

Abbreviated book names can be used:
```python
>>> Passage('John',1,1,1,18).abbr()
'Jn 1:1-18'
>>> Passage('John',1,1,1,18).uabbr()
u'Jn 1:1\u201318'
```

Adding together passages will return a PassageCollection object, which in turn can generate useful reference strings:
```python
>>> c = Passage('Joh',1) + Passage('Joh',3) + Passage('Heb',1,1,1,4)
>>> str(c)
'John 1, 3; Hebrews 1:1-4'
```

and where there might be ambiguity, chapters and verses are made explicit:
```python
>>> PassageCollection(Passage('Eph',1),Passage('Gen',3,2),Passage('Gen',3,6),Passage('Gen',8),Passage('Mat',5)).abbr()
'Eph 1; Gn 3:2, 3:6, 8:1-22; Mt 5'
```

[OSIS-formatted](http://www.bibletechnologies.net/) reference strings can also be obtained:
```python
>>> Passage('Joh',1).osis_reference()
'John.1.1-John.1.51'
```


## Passage Length

The number of verses in a passage may be calculated by calling `len`:
```python
>>> len(Passage('Gen'))
1533
```

### Extending a passage

Chapters and/or verses can be added to the end of a passage by using the PassageDelta class:
```python
>>> from pypassage import PassageDelta
>>> str(Passage('Rom',3,21) + PassageDelta(verses=5))
'Romans 3:21-26'
>>> str(Passage('Rom',1,1) + PassageDelta(chapters=1, verses=10))
'Romans 1:1-2:11'
```

To add verses to the start to the passage, set passage_start=True:
```python
>>> str(Passage('Rom',3,21) + PassageDelta(verses=2, passage_start=True))
'Romans 3:19-21'
```

### Passage truncation

A passage may be truncated if it exceeds a specific number of verses or proportion of the book:
```python
>>> str(Passage('Rom').truncate(number_verses=200))
'Romans 1:1-8:14'
>>> str(Passage('Ephesians').truncate(proportion_of_book=0.5))
'Ephesians 1:1-4:11'
```

Both arguments may provided simultaneously (something that is particularly useful for complying with copyright restrictions). If neither are relevant, the same passage will be returned:
```python
>>> a = Passage('Luke',9,23)
>>> b = a.truncate(number_verses=500,proportion_of_book=0.5)
>>> a is b
True
```


## Looking up passage text

Passage text can be looked up, using the [ESV API](http://www.esvapi.org/) service:
```python
>>> get_passage_text(Passage('Gen',1,1))
('   In the beginning, God created the heavens and the earth.', False)
```

Full HTML may be fetched, and a dictionary of custom [options](http://www.esvapi.org/api) passed in:
```python
>>> get_passage_text(Passage('Gen',1,1), html=True, options={"include-headings":"true"})
('<div class="esv">\n<div class="esv-text"><h3 id="p01001001.01-1">The Creation of the World</h3>\n<p class="chapter-first" id="p01001001.06-1"><span class="chapter-num" id="v01001001-1">1:1&nbsp;</span>In the beginning, God created the heavens and the earth.</p>\n</div>\n</div>', False)
```

Results are cached (for the same option set) by default using a simple in-memory object. Custom caches may easily be defined. Please refer to ESV [usage restrictions](http://www.esvapi.org/#conditions) to ensure you use retrieved text in an appropriate manner.

At this stage passage data is based only on the ESV bible, but data for additional translations may readily be added (and are welcomed to this project). In the future it is intended that this module will parse arbitrary passage strings, but at this stage book, chapter, and verse must be directly specified.


## Django integration
Sample code for Django integration is given in the `opt/django/` folder. Submission of similar code for other frameworks is welcome!


## Has PyPassage been useful to you?
I would love to hear how you've used PyPassage. Drop me a line: cameronoliver+pypassage@gmail.com


## See also
- [python-scriptures](https://github.com/davisd/python-scriptures)
- [python-bible](https://github.com/jasford/python-bible)
