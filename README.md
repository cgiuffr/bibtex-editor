# bibtex-editor
BibTex Editor. Takes a BibTex file in input and produces a processed one in output. Optionally strips BibTex entries not present in given Latex files.

Dependencies:
* Python 3.7+.
* BibtexParser v2, installation instructions: https://bibtexparser.readthedocs.io/en/main/install.html

Relevant API documentation:
* https://bibtexparser.readthedocs.io/en/main/bibtexparser.html

Usage:

```shell
$ cp params_default.py params.py # and edit params.py
$ ./bibtex-editor.py
```
