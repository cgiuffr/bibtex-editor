import logging

log_format =            '[%(asctime)s] %(levelname)s: %(message)s'
log_level =             logging.INFO
bibtex_encoding =       'UTF-8'

bibtex_input =          '<your_file_here.bib>'
bibtex_output =         '<your_file_here.bib>'

url_field_names =       ['howpublished', 'url', 'note', 'addendum']
url_field_dest_name =   'howpublished' # which field to use for (misc) urls in output

strip_nonmisc_urls =    True # strip url fields from nonmisc entries
strip_dup_keys =        True # Strip duplicate entry keys

extra_fields_mode =     'drop' # 'drop', 'hide', or None (for fields not in fields_order)

sort_fields =           True # Sort fields according to fields_order
fields_order =          [
    'title', 'author', 'booktitle', 'journal', url_field_dest_name, 'year', 'institution'
]

booktitle_subs =        {
    r'.*IEEE Symposium on Security and Privacy.*' : 'S\&P',
    r'.*USENIX Security.*' : 'USENIX Security',
    r'.*Network and Distributed System Security.*' : 'NDSS',
    r'.*Conference on Computer and Communications Security.*' : 'CCS',
    r'.*Research in Attacks, Intrusions and Defenses.*' : 'RAID',
    r'.*Annual Computer Security Applications Conference.*' : 'ACSAC',

    r'.*Symposium on Operating Systems Principles.*' : 'SOSP',
    r'.*Symposium on Operating Systems Design and Implementation.*' : 'OSDI',
    r'.*European Conference on Computer Systems.*' : 'EuroSys',
    r'.*USENIX Annual Technical Conference.*' : 'USENIX ATC',
    r'.*Architectural Support for Programming Languages and Operating Systems.*' : 'ASPLOS'
}

title_caps =            {
    'Chrome', 'Firefox', 'Valgrind', 'Clang', 'C', 'Linux', 'Windows', 'Spectre', 'Meltdown', 'Intel', 'Mozilla', 'Google', 'Microsoft', 'Apple', 'ARM', 'Rust', 'Java', 'Python', 'JavaScript', 'Xen', 'Rowhammer', 'Rowhammering', 'VTable', 'Android', 'iOS', 'Dr', 'L3'
}
title_strip_caps =      True # Strip existing curly braces
title_camel_caps =      True # Capitalize camel-case words
title_colon_caps =      True # Capitalize after ': '
title_fix_escaping =    True # Fix things like $\{$AMD$\}$

author_drop_commas =    True # {Lastname, Firstname} --> {Firstname Lastname} 

misc_entry_fix_url =    True # Ensure misc entries have a single howpublished={\url{...}} field.

latex_inputs =          [] # Optional list of 'latexfile1', 'latexfile2', etc. to output bibliography for

text_output =           None # Optional text output file

text_output_format = '[{count}] {author + ", " if author else ""}{title}{", in " + venue if venue else ""}{", " + year if year else ""}.\n'