from distutils.core import setup


setup(
	name = "pypassage",
	packages = ['pypassage','pypassage.bibledata'],
	version = '1.1',
	author = 'Cameron Oliver',
	author_email = 'cameron.oliver@gmail.com',
	url = 'https://github.com/col16/pypassage',
	description = 'Python module for working with bible references',
	long_description = """Python module for working with bible references
--------------------------------------------------------

It can:

- render reference strings sensibly and non-ambiguously; e.g. returning "Ephesians 1" when Ephesians 1:1-1:23 was specified, because there are only 23 verses in that chapter;
- look up actual passage text using external API services;
- fill in missing information where possible; e.g. inferring that for the inputs of `book="EPH"` and `start_chapter=1`, the whole Ephesians 1 chapter (verses 1 to 23) was intended;
- verify that a passage is valid; e.g. telling you that Ephesians 99 and Genesis 3:5-1:2 can't exist;
- add verses or chapters to the start or end of a passage, or [truncate](#passage-truncation) a passage to a given number of verses; such as for satisfying copyright restrictions; `and`
- count the number of verses in a passage. 

Basic Usage:

:: 

  from pypassage import Passage
  p = Passage(book='Genesis', start_chapter=1, start_verse=1, end_chapter=2, end_verse=3)


Documentation
-------------
Full documentation may be found on the `GitHub page
<https://github.com/col16/pypassage>`_.
""",
	classifiers = [
		"Programming Language :: Python",
		"Programming Language :: Python :: 2.7",
		"License :: OSI Approved :: ISC License (ISCL)",
		"Operating System :: OS Independent",
		"Development Status :: 4 - Beta",
		"Intended Audience :: Developers",
		"Topic :: Software Development :: Libraries",
		"Topic :: Software Development :: Libraries :: Python Modules",
		"Topic :: Religion"
		],
)