import logging

log_format =            '[%(asctime)s] %(levelname)s: %(message)s'
log_level =             logging.INFO
bibtex_encoding =       'UTF-8'

bibtex_input =          '<your_file_here.bib>'
bibtex_output =         '<your_file_here.bib>'

strip_dup_keys =       True # Strip duplicate entry keys

extra_fields =          ['volume', 'number', 'month', 'address', 'annote', 'crossref', 'doi', 'edition', 'editor', 'email', 'organization', 'pages', 'publisher', 'series', 'type', 'note', 'issn', 'isbn', 'location', 'shorttitle', 'abstract', 'eventtitle', 'urldate', 'langid', 'file', 'keywords'] # Optional list of extra 'field1', 'field2', etc. for each entry
extra_fields_mode =     'drop' # 'drop', 'hide', or None

sort_fields =           True # Sort fields according to the order below
fields_order =          ['title', 'author', 'booktitle', 'journal', 'howpublished', 'year']

booktitle_subs = {
                        r'.*IEEE symposium on security and privacy.*' : 'S\&P',
                        r'.*USENIX Security.*' : 'USENIX Security',
                        r'.*Network and Distributed System Security.*' : 'NDSS',
                        r'.*Conference on Computer and Communications Security.*' : 'CCS'
}

title_caps = {
    'Chrome', 'Firefox', 'Valgrind', 'Clang', 'C', 'Linux', 'Windows', 'Spectre', 'Meltdown', 'Intel', 'Mozilla', 'Google', 'Microsoft', 'Apple', 'ARM', 'Rust', 'Java', 'Python', 'JavaScript', 'Xen', 'Rowhammer', 'Rowhammering', 'VTable', 'Android', 'iOS', 'Dr'
}
title_strip_caps =      True # Strip existing curly braces
title_camel_caps =      True # Capitalize camel-case words
title_colon_caps =      True # Capitalize after ': '
title_fix_escaping =    True # Fix things like $\{$AMD$\}$

latex_inputs =          [] # Optional list of 'latexfile1', 'latexfile2', etc. to output bibliography for