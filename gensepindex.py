#!/usr/bin/env python
"""Auto-generate SEP 0 (SEP index).

Generating the SEP index is a multi-step process.  To begin, you must first
parse the SEP files themselves, which in and of itself takes a couple of steps:

    1. Parse metadata.
    2. Validate metadata.

With the SEP information collected, to create the index itself you must:

    1. Output static text.
    2. Format an entry for the SEP.
    3. Output the SEP (both by category and numerical index).

"""
from __future__ import absolute_import, with_statement
from __future__ import print_function

import sys
import os
import codecs

from operator import attrgetter

from sep0.output import write_sep0
from sep0.sep import SEP, SEPError


def main(argv):
    if not argv[1:]:
        path = "."
    else:
        path = argv[1]

    seps = []
    if os.path.isdir(path):
        for file_path in os.listdir(path):
            if file_path.startswith("sep-0000."):
                continue
            abs_file_path = os.path.join(path, file_path)
            if not os.path.isfile(abs_file_path):
                continue
            if file_path.startswith("sep-") and file_path.endswith((".txt", "rst")):
                with codecs.open(abs_file_path, "r", encoding="UTF-8") as sep_file:
                    try:
                        sep = SEP(sep_file)
                        if sep.number != int(file_path[4:-4]):
                            raise SEPError(
                                "SEP number does not match file name",
                                file_path,
                                sep.number,
                            )
                        seps.append(sep)
                    except SEPError as e:
                        errmsg = "Error processing SEP %s (%s), excluding:" % (
                            e.number,
                            e.filename,
                        )
                        print(errmsg, e, file=sys.stderr)
                        sys.exit(1)
        seps.sort(key=attrgetter("number"))
    elif os.path.isfile(path):
        with open(path, "r") as sep_file:
            seps.append(SEP(sep_file))
    else:
        raise ValueError("argument must be a directory or file path")

    with codecs.open("sep-0000.rst", "w", encoding="UTF-8") as sep0_file:
        write_sep0(seps, sep0_file)


if __name__ == "__main__":
    main(sys.argv)
