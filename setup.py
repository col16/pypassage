from distutils.core import setup


setup(
	name = "pypassage",
	packages = ['pypassage','pypassage.bibledata'],
	version = '1.0',
	author = 'Cameron Oliver',
	author_email = 'cameron.oliver@gmail.com',
	url = 'https://github.com/col16/pypassage',
	description = 'Small Python module for working with bible passages/references',
	long_description = """Python module for working with bible passages/references
--------------------------------------------------------

It can:

- verify that a passage is valid; e.g. telling you that Ephesians 99 and Genesis 3:5-1:2 can't exist;
- render reference strings sensibly; e.g. knowing that Ephesians 1:1-1:23 should be rendered simply as "Ephesians 1" because there are only 23 verses in that chapter;
- fill in missing information where possible; e.g. inferring that for the inputs of `book="EPH"` and `start_chapter=1`, the whole Ephesians 1 chapter (verses 1 to 23) was intended;
- count the number of verses in a passage, and truncate or extend a passage to a given number of verses; `and`
- look up actual passage text using external API services.

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
		"Development Status :: 3 - Alpha",
		"Intended Audience :: Developers",
		"Topic :: Software Development :: Libraries",
		"Topic :: Software Development :: Libraries :: Python Modules",
		"Topic :: Religion"
		],
)