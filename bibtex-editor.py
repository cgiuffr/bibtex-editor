#!/usr/bin/python3

import sys
import logging
import re
import pprint

from collections import defaultdict

import bibtexparser
import bibtexparser.model as m

stats = {
    'latex_cites_found': 0,
    'entries_dropped': 0,
    'dup_keys': 0,
    'dup_titles': 0,
    'fields_dropped_or_hidden': 0,
    'booktitles_replaced': 0,
    'title_caps_stripped': 0,
    'title_camel_caps_added': 0,
    'title_colon_caps_added': 0,
    'title_caps_replaced': 0,
    'title_escapes_fixed': 0,
    'author_commas_dropped': 0,
    'misc_entries_fixed': 0
}

title_idx = {}


def process_entry_extra_fields(params, entry):
    if not params.extra_fields_mode:
        return

    extra_fields = []
    should_strip_urls = params.strip_nonmisc_urls and entry.entry_type != 'misc'
    for f in entry.fields:
        if should_strip_urls and f.key == params.url_field_dest_name:
            extra_fields.append(f)
        elif not f.key in params.fields_order:
            extra_fields.append(f)

    for f in extra_fields:
        myfield = entry.get(f.key)
        stats['fields_dropped_or_hidden'] += 1
        if params.extra_fields_mode == 'hide':
            myfield.key = 'HIDE' + myfield.key
        else:
            entry.pop(f.key)

    return


def process_entry_booktitle(params, entry):
    bt = entry.get('booktitle')
    if not bt:
        return

    for pattern, replacement in params.booktitle_subs.items():
        (match, num_subs) = re.subn(
            pattern, replacement, bt.value, flags=re.IGNORECASE)
        if num_subs > 0:
            bt.value = match
            stats['booktitles_replaced'] += num_subs
            break

    return


def process_entry_title(library, params, entry):
    title = entry.get('title')
    if not title:
        return False

    title_hash = re.sub(r'[^\w]', '', title.value).lower()
    if title_hash in title_idx:
        e = title_idx[title_hash]
        e_title = e.get('title')
        logging.warning(
            f'Found duplicate titles:\n - "{e.key}" -> "{e_title.value}"\n - "{entry.key}" -> "{title.value}"')
        stats['dup_titles'] += 1
        if params.strip_dup_titles:
            library.remove(entry)
            return True
    else:
        title_idx[title_hash] = entry

    if params.title_fix_escaping:
        p1 = re.escape('$\{$')
        p2 = re.escape('$\}$')
        (title.value, num_subs) = re.subn(rf'{p1}', '{', title.value)
        (title.value, num_subs) = re.subn(rf'{p2}', '}', title.value)
        if num_subs > 0:
            stats['title_escapes_fixed'] += num_subs

    if params.title_strip_caps:
        (title.value, num_subs) = re.subn(rf'{{', '', title.value)
        (title.value, num_subs) = re.subn(rf'}}', '', title.value)
        if num_subs > 0:
            stats['title_caps_stripped'] += num_subs

    if params.title_camel_caps:
        (match, num_subs) = re.subn(
            rf'(?<!{{)\b(\w+[A-Z]\w*)\b(?!}})', rf'{{\1}}', title.value)
        if num_subs > 0:
            title.value = match
            stats['title_camel_caps_added'] += num_subs

    if params.title_colon_caps:
        (match, num_subs) = re.subn(rf'(:\s)([a-zA-Z])(\w*)', lambda m: m.group(
            1) + rf'{{' + m.group(2).upper() + m.group(3) + rf'}}', title.value)
        if num_subs > 0:
            title.value = match
            stats['title_colon_caps_added'] += num_subs

    for cap in params.title_caps:
        (match, num_subs) = re.subn(
            rf'(?<!{{)\b({re.escape(cap)})\b(?!}})', rf'{{{cap}}}', title.value, flags=re.IGNORECASE)
        if num_subs > 0:
            title.value = match
            stats['title_caps_replaced'] += num_subs

    return False


def process_entry_author(params, entry):
    author = entry.get('author')
    if not author or not re.match(r'.*,.*', author.value):
        return

    tokens = re.split(r'\s+and\s+', author.value, flags=re.IGNORECASE)
    authors = []
    for t in tokens:
        names = re.split(r'\s*,\s*', t)
        if len(names) < 2:
            full_name = t
        else:
            full_name = names[-1] + " " + " ".join(names[:-1])
        authors.append(full_name)
    author.value = " and ".join(authors)
    stats['author_commas_dropped'] += 1

    return


def process_misc_url_field(params, entry, field_name):
    f = entry.get(field_name)
    if not f:
        return None

    url = re.sub(rf'\\url{{(.*)}}', r'\1', f.value)
    url = re.sub(rf'}}|{{', '', url)

    f.key = params.url_field_dest_name
    f.value = f'\\url{{{url}}}'
    stats['misc_entries_fixed'] += 1

    for n in params.url_field_names:
        if n != f.key:
            entry.pop(n)

    return f


def process_misc_entry(params, entry):
    if not params.misc_entry_fix_url or entry.entry_type != 'misc':
        return

    f = process_misc_url_field(params, entry, 'howpublished')
    if f:
        return
    for name in params.url_field_names:
        f = process_misc_url_field(params, entry, name)
        if f:
            return

    return


def process_entry_field_order(params, entry):
    if not params.sort_fields:
        return

    entry.fields.sort(
        key=lambda val: 100 if val.key not in params.fields_order else params.fields_order.index(
            val.key)
    )

    return


def process_entry(library, params, entry):
    process_entry_booktitle(params, entry)
    dropped = process_entry_title(library, params, entry)
    if dropped:
        return True
    process_entry_author(params, entry)
    process_misc_entry(params, entry)
    process_entry_extra_fields(params, entry)
    process_entry_field_order(params, entry)

    return False


def field_to_text(params, entry, key):
    f = entry.get(key)
    if not f:
        return ''
    val = re.sub(rf'}}|{{|(\\url)', '', f.value).replace("\n", "")
    val = re.sub(r'\s+', ' ', val)
    if key == 'author':
        val = re.sub(r'\s+and\s+', ', ', val, flags=re.IGNORECASE)
    elif key not in params.url_field_names:
        val = re.sub(r"(?:(?<=\W)|^)\w(?=\w)",
                     lambda x: x.group(0).upper(), val)

    return val


def entry_to_text(params, entry, count):
    author = field_to_text(params, entry, 'author')
    title = field_to_text(params, entry, 'title')
    booktitle = field_to_text(params, entry, 'booktitle')
    journal = field_to_text(params, entry, 'journal')
    url = field_to_text(params, entry, params.url_field_dest_name)
    institution = field_to_text(params, entry, 'institution')
    venue = booktitle if booktitle else \
        journal if journal else \
        url if url else ""
    year = field_to_text(params, entry, 'year')

    return eval(f"f'''{params.text_output_format}'''")


def main():
    try:
        import params
    except ImportError:
        print("Please create params.py based on params_default.py first.")
        sys.exit(1)

    logging.basicConfig(format=params.log_format, level=params.log_level)

    # Parse input
    library = bibtexparser.parse_file(
        params.bibtex_input, encoding=params.bibtex_encoding)
    num_error_blocks = len(library.failed_blocks)
    stripped_blocks = []
    if num_error_blocks > 0 and params.strip_dup_keys:
        for b in library.failed_blocks:
            if isinstance(b, bibtexparser.model.DuplicateBlockKeyBlock):
                stripped_blocks.append(b)
                stats['dup_keys'] += 1
    num_error_blocks -= len(stripped_blocks)
    library.remove(stripped_blocks)
    if num_error_blocks > 0:
        logging.error("Some blocks failed to parse:\n- " +
                      '\n- '.join([str(b.error) for b in library.failed_blocks]))
        sys.exit(1)
    logging.info(f"Parsed {len(library.blocks)} blocks, including:"
                 f"\n\t{len(library.entries)} entries"
                 f"\n\t{len(library.comments)} comments"
                 f"\n\t{len(library.strings)} strings and"
                 f"\n\t{len(library.preambles)} preambles")

    # Process any input Latex files
    cites_lst = []
    for input in params.latex_inputs:
        with open(input, 'r') as f:
            data = f.read().replace('\n', ' ')
            matches = re.findall(r"(?:\\cite{)([^}]+)(?:})", data)
            for m in matches:
                tokens = m.split(',')
                cites_lst.extend([t.strip() for t in tokens])
    cites = set(cites_lst)
    stats['latex_cites_found'] = len(cites)

    # Drop entries if needed
    if len(params.latex_inputs) > 0:
        dropped_entries = []
        for e in library.entries:
            if e.key not in cites:
                dropped_entries.append(e)
                continue
        stats['entries_dropped'] = len(dropped_entries)
        for e in dropped_entries:
            library.remove(e)

    # Process entries
    for e in library.entries:
        process_entry(library, params, e)
    logging.info('Stats:')
    pprint.pprint(stats)

    # Write output
    with open(params.bibtex_output, "w", encoding=params.bibtex_encoding) as f:
        bibtexparser.write_file(f, library)

    if not params.text_output:
        return
    with open(params.text_output, "w", encoding=params.bibtex_encoding) as f:
        count = 1
        for e in library.entries:
            f.write(entry_to_text(params, e, count) + "\n")
            count += 1


if __name__ == '__main__':
    main()
