#!/usr/bin/python3

import sys
import logging
import re

import bibtexparser
import bibtexparser.model as m

stats = {
    'latex_cites_found': 0,
    'entries_dropped': 0,
    'fields_dropped_or_hidden': 0,
    'booktitles_replaced': 0,
    'title_caps_replaced': 0,
    'title_escapes_fixed': 0
}


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

    for cap in params.title_caps:
        (match, num_subs) = re.subn(
            rf'([^{{]\b)({re.escape(cap)})(\b[^}}])', rf'\1{{{cap}}}\3', title.value, flags=re.IGNORECASE)
        if num_subs > 0:
            title.value = match
            stats['title_caps_replaced'] += num_subs

    if params.title_fix_escaping:
        p1 = re.escape('$\{$')
        p2 = re.escape('$\}$')
        (title.value, num_subs) = re.subn(rf'{p1}', '{', title.value)
        (title.value, num_subs) = re.subn(rf'{p2}', '}', title.value)
        if num_subs > 0:
            stats['title_escapes_fixed'] += num_subs

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
    library = bibtexparser.parse_file(params.bibtex_input)
    if len(library.failed_blocks) > 0:
        logging.error("Some blocks failed to parse!")
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
    bibtexparser.write_file(params.bibtex_output, library)


if __name__ == '__main__':
    main()