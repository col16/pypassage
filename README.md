# PyPassage

**PyPassage** is a small Python module for working with bible passages/references. It can:

- [verify that a passage is valid](#validity); e.g. telling you that Ephesians 99 and Genesis 3:5-1:2 can't exist
- [render reference strings sensibly](#reference-strings); e.g. knowing that Ephesians 1:1-1:23 should be rendered simply as "Ephesians 1" because there are only 23 verses in that chapter
- [fill in missing information where possible](#missing-information); e.g. inferring that for the inputs of `book="EPH"` and `start_chapter=1`, the whole Ephesians 1 chapter (verses 1 to 23) was intended
- [count the number of verses](#passage-length) in a passage, and [truncate or extend](#passage-truncationextension) a passage to a given number of verses
- [look up actual passage text](#looking-up-passage-text) using external API services



## Basic Usage

```python
from pypassage import Passage
p = Passage(book='Genesis', start_chapter=1, start_verse=1, end_chapter=2, end_verse=3)
```

Books may be specified as their full name (e.g. "Revelation"), a three-letter abbreviation (e.g. "Rev"), the standard ESV abbreviation (e.g. "Rv"), or finally, the book number (e.g. 66).


### Missing Information

Not all fields need to be provided. You may for example specify a single verse:
```python
p = Passage('2 Corinthians',4,7)
```

or a single chapter
```python
p = Passage('Romans',1)
```

or even a complete book
```python
p = Passage('Philippians')
```


## Validity

Invalid passages will throw an InvalidPassageException on instantiation:
```python
>>> p = Passage('Deu', -3)
Traceback (most recent call last):
  File "<stdin>", line 1, in <module>
  File "reference.py", line 45, in __init__
    if (sc and start_chapter < 1) or (sv and start_verse < 1) or (ec and end_chapter < 1) or (ev and end_verse < 1): raise InvalidPassageException()
reference.InvalidPassageException
```

Nevertheless, a valid passage may easily be made invalid after instantiation. Thus to check validity, you may call is_valid():
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

Abbreviated book names can also be used:
```python
>>> Passage('John',1,1,1,18).abbr()
'Jn 1:1-18'
>>> Passage('John',1,1,1,18).uabbr()
u'Jn 1:1\u201318'
```

Adding together passages will return a PassageCollection object, which in turn can generate strings:
```python
>>> c = Passage('Joh',1,1,1,18) + Passage('1Jo',1,1,1,4)
>>> c
PassageCollection(Passage(book=43, start_chapter=1, start_verse=1, end_chapter=1, end_verse=18), Passage(book=62, start_chapter=1, start_verse=1, end_chapter=1, end_verse=4))
>>> str(c)
'John 1:1-18; 1 John 1:1-4'
```

PassageCollection strings within the same book are grouped together intelligently:
```python
>>> from pypassage import PassageCollection
>>> unicode(PassageCollection(Passage('Gen',1),Passage('Gen',3),Passage('Gen',5)))
u'Genesis 1, 3, 5'
```

and where there might be ambiguity, chapters and verses are made explicit:
```python
>>> PassageCollection(Passage('Eph',1),Passage('Gen',3,2),Passage('Gen',3,6),Passage('Gen',8),Passage('Mat',5)).abbr()
'Eph 1; Gn 3 vv. 2, 6, ch. 8; Mt 5'
```

## Passage Length

The number of verses in a passage may be calculated by calling `len`:
```python
>>> len(Passage('Gen'))
1533
```

### Passage truncation/extension

A passage may be extended or truncated to a specific number of verses:
```python
>>> str(Passage('Rom',3,21).extend(number_verses=11))
'Romans 3:21-31'
>>> str(Passage('Rom').truncate(number_verses=200))
'Romans 1:1-8:14'
```

Both functions also accept proportion_of_book arguments:
```python
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

Full html may be fetched, and a dictionary of custom [options](http://www.esvapi.org/api) passed in:
```python
>>> get_passage_text(Passage('Gen',1,1), html=True, options={"include-headings":"true"})
('<div class="esv">\n<div class="esv-text"><h3 id="p01001001.01-1">The Creation of the World</h3>\n<p class="chapter-first" id="p01001001.06-1"><span class="chapter-num" id="v01001001-1">1:1&nbsp;</span>In the beginning, God created the heavens and the earth.</p>\n</div>\n</div>', False)
```

Results are cached (for the same option set) by default using a simple in-memory object. Custom caches may easily be defined. Please refer to ESV [usage restrictions](http://www.esvapi.org/#conditions) to ensure you use retrieved text in an appropriate manner.

At this stage passage data is based only on the ESV bible, but data for additional translations may readily be added (and are welcomed to this project). In the future it is intended that this module will parse arbitrary passage strings, but at this stage book, chapter, and verse must be directly specified.



# Miscellaneous
## Django integration
Sample code for Django integration is given in the `opt/django/` folder. Submission of similar code for other frameworks is welcome!

## Unit tests
A comprehensive set of unit tests are included, which can be run from the command line.

## See also
[python-bible](https://github.com/jasford/python-bible) is a very similar Python module and will be of interest to anyone evaluating a project such as this. [python-scriptures](https://github.com/davisd/python-scriptures) is a package that can extract bible references from plain text.
