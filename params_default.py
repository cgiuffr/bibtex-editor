import logging

log_format =            '[%(asctime)s] %(levelname)s: %(message)s'
log_level =             logging.INFO

bibtex_input =          '<your_file_here.bib>'
bibtex_output =         '<your_file_here.bib>'

extra_fields =          ['volume', 'number', 'month', 'address', 'annote', 'crossref', 'doi', 'edition', 'editor', 'email', 'organization', 'pages', 'publisher', 'series', 'type', 'note', 'issn', 'isbn'] # Optional list of extra 'field1', 'field2', etc. for each entry
extra_fields_mode =     'drop' # 'drop', 'hide', or None

booktitle_subs = {
                        r'.*IEEE symposium on security and privacy.*' : 'S\&P',
                        r'.*USENIX Security.*' : 'USENIX Security',
                        r'.*Network and Distributed System Security.*' : 'NDSS',
                        r'.*Conference on Computer and Communications Security.*' : 'CCS'
}

title_caps = {
    'Chrome', 'Clang', 'C/C++', 'C++', 'Linux', 'LLVM', 'Spectre', 'ASLR', 'KASLR', 'Intel', 'TSX', 'SMAP', 'SMEP', 'OS'
}
title_fix_escaping =    True # Fix things like $\{$AMD$\}$

latex_inputs =          [] # Optional list of 'latexfile1', 'latexfile2', etc. to output bibliography for