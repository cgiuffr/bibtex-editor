#!/usr/bin/python3

import sys
import logging
import re

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
    'title_escapes_fixed': 0
}

title_idx = set()


def process_entry_extra_fields(params, entry):
    if not params.extra_fields_mode:
        return

    for field in params.extra_fields:
        myfield = entry.pop(field)
        if myfield:
            stats['fields_dropped_or_hidden'] += 1
            if params.extra_fields_mode == 'hide':
                myfield.key = 'HIDE' + myfield.key
                entry.set_field(myfield)

    return


def process_entry_booktitle(params, entry):
    bt = entry.pop('booktitle')
    if not bt:
        return

    for pattern, replacement in params.booktitle_subs.items():
        (match, num_subs) = re.subn(
            pattern, replacement, bt.value, flags=re.IGNORECASE)
        if num_subs > 0:
            bt.value = match
            stats['booktitles_replaced'] += num_subs
            break

    entry.set_field(bt)
    return


def process_title(params, entry):
    title = entry.pop('title')
    if not title:
        return

    title_hash = re.sub(r'[^\w]', '', title.value).lower()
    if title_hash in title_idx:
        logging.warning(f'Found possible duplicate title: "{title.value}"')
        stats['dup_titles'] += 1
    else:
        title_idx.add(title_hash)

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

    entry.set_field(title)
    return


def process_entry(params, entry):
    process_entry_extra_fields(params, entry)
    process_entry_booktitle(params, entry)
    process_title(params, entry)

    return


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
    ignored_blocks = []
    if num_error_blocks > 0 and params.ignore_dup_keys:
        for b in library.failed_blocks:
            if isinstance(b, bibtexparser.model.DuplicateBlockKeyBlock):
                ignored_blocks.append(b)
                stats['dup_keys'] += 1
    num_error_blocks -= len(ignored_blocks)
    library.remove(ignored_blocks)
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

    # Process entries
    if len(params.latex_inputs) > 0:
        dropped_entries = []
        for e in library.entries:
            if e.key not in cites:
                dropped_entries.append(e)
                continue
            process_entry(params, e)
        stats['entries_dropped'] = len(dropped_entries)
        for e in dropped_entries:
            library.remove(e)
    logging.info(f'Stats={stats}')

    # Write output
    with open(params.bibtex_output, "w", encoding=params.bibtex_encoding) as f:
        bibtexparser.write_file(f, library)


if __name__ == '__main__':
    main()
