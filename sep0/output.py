"""Code to handle the output of SEP 0."""
from __future__ import absolute_import
from __future__ import print_function
import datetime
import sys
import unicodedata

from operator import attrgetter

from . import constants
from .sep import SEP, SEPError

# This is a list of reserved SEP numbers.  Reservations are not to be used for
# the normal SEP number allocation process - just give out the next available
# SEP number.  These are for "special" numbers that may be used for semantic,
# humorous, or other such reasons, e.g. 401, 666, 754.
#
# SEP numbers may only be reserved with the approval of a SEP editor.  Fields
# here are the SEP number being reserved and the claimants for the SEP.
# Although the output is sorted when SEP 0 is generated, please keep this list
# sorted as well.
RESERVED = [(801, "Warsaw")]


indent = u" "


def emit_column_headers(output):
    """Output the column headers for the SEP indices."""
    column_headers = {
        "status": ".",
        "type": ".",
        "number": "SEP",
        "title": "SEP Title",
        "authors": "SEP Author(s)",
    }
    print(constants.table_separator, file=output)
    print(constants.column_format % column_headers, file=output)
    print(constants.table_separator, file=output)


def sort_seps(seps):
    """Sort SEPs into meta, informational, accepted, open, finished,
    and essentially dead."""
    meta = []
    info = []
    provisional = []
    accepted = []
    open_ = []
    finished = []
    historical = []
    deferred = []
    dead = []
    for sep in seps:
        # Order of 'if' statement important.  Key Status values take precedence
        # over Type value, and vice-versa.
        if sep.status == "Draft":
            open_.append(sep)
        elif sep.status == "Deferred":
            deferred.append(sep)
        elif sep.type_ == "Process":
            if sep.status == "Active":
                meta.append(sep)
            elif sep.status in ("Withdrawn", "Rejected"):
                dead.append(sep)
            else:
                historical.append(sep)
        elif sep.status in ("Rejected", "Withdrawn", "Incomplete", "Superseded"):
            dead.append(sep)
        elif sep.type_ == "Informational":
            # Hack until the conflict between the use of "Final"
            # for both API definition SEPs and other (actually
            # obsolete) SEPs is addressed
            if sep.status == "Active" or "Release Schedule" not in sep.title:
                info.append(sep)
            else:
                historical.append(sep)
        elif sep.status == "Provisional":
            provisional.append(sep)
        elif sep.status in ("Accepted", "Active"):
            accepted.append(sep)
        elif sep.status == "Final":
            finished.append(sep)
        else:
            raise SEPError(
                "unsorted (%s/%s)" % (sep.type_, sep.status), sep.filename, sep.number
            )
    return (
        meta,
        info,
        provisional,
        accepted,
        open_,
        finished,
        historical,
        deferred,
        dead,
    )


def verify_email_addresses(seps):
    authors_dict = {}
    for sep in seps:
        for author in sep.authors:
            # If this is the first time we have come across an author, add them.
            if author not in authors_dict:
                authors_dict[author] = [author.email]
            else:
                found_emails = authors_dict[author]
                # If no email exists for the author, use the new value.
                if not found_emails[0]:
                    authors_dict[author] = [author.email]
                # If the new email is an empty string, move on.
                elif not author.email:
                    continue
                # If the email has not been seen, add it to the list.
                elif author.email not in found_emails:
                    authors_dict[author].append(author.email)

    valid_authors_dict = {}
    too_many_emails = []
    for author, emails in authors_dict.items():
        if len(emails) > 1:
            too_many_emails.append((author.first_last, emails))
        else:
            valid_authors_dict[author] = emails[0]
    if too_many_emails:
        err_output = []
        for author, emails in too_many_emails:
            err_output.append("    %s: %r" % (author, emails))
        raise ValueError(
            "some authors have more than one email address "
            "listed:\n" + "\n".join(err_output)
        )

    return valid_authors_dict


def sort_authors(authors_dict):
    authors_list = list(authors_dict.keys())
    authors_list.sort(key=attrgetter("sort_by"))
    return authors_list


def normalized_last_first(name):
    return len(unicodedata.normalize("NFC", name.last_first))


def emit_title(text, anchor, output, *, symbol="="):
    print(".. _{anchor}:\n".format(anchor=anchor), file=output)
    print(text, file=output)
    print(symbol * len(text), file=output)
    print(file=output)


def emit_subtitle(text, anchor, output):
    emit_title(text, anchor, output, symbol="-")


def emit_sep_category(output, category, anchor, seps):
    emit_subtitle(category, anchor, output)
    emit_column_headers(output)
    for sep in seps:
        print(sep, file=output)
    print(constants.table_separator, file=output)
    print(file=output)


def write_sep0(seps, output=sys.stdout):
    # SEP metadata
    today = datetime.date.today().strftime("%Y-%m-%d")
    print(constants.header % today, file=output)
    print(file=output)
    # Introduction
    emit_title("Introduction", "intro", output)
    print(constants.intro, file=output)
    print(file=output)
    # SEPs by category
    (
        meta,
        info,
        provisional,
        accepted,
        open_,
        finished,
        historical,
        deferred,
        dead,
    ) = sort_seps(seps)
    emit_title("Index by Category", "by-category", output)
    emit_sep_category(
        category="Meta-SEPs (SEPs about SEPs or Processes)",
        anchor="by-category-meta",
        seps=meta,
        output=output,
    )
    emit_sep_category(
        category="Other Informational SEPs",
        anchor="by-category-other-info",
        seps=info,
        output=output,
    )
    emit_sep_category(
        category="Provisional SEPs (provisionally accepted; interface may still change)",
        anchor="by-category-provisional",
        seps=provisional,
        output=output,
    )
    emit_sep_category(
        category="Accepted SEPs (accepted; may not be implemented yet)",
        anchor="by-category-accepted",
        seps=accepted,
        output=output,
    )
    emit_sep_category(
        category="Open SEPs (under consideration)",
        anchor="by-category-open",
        seps=open_,
        output=output,
    )
    emit_sep_category(
        category="Finished SEPs (done, with a stable interface)",
        anchor="by-category-finished",
        seps=finished,
        output=output,
    )
    emit_sep_category(
        category="Historical Meta-SEPs and Informational SEPs",
        anchor="by-category-historical",
        seps=historical,
        output=output,
    )
    emit_sep_category(
        category="Deferred SEPs (postponed pending further research or updates)",
        anchor="by-category-deferred",
        seps=deferred,
        output=output,
    )
    emit_sep_category(
        category="Abandoned, Withdrawn, and Rejected SEPs",
        anchor="by-category-abandoned",
        seps=dead,
        output=output,
    )
    print(file=output)
    # SEPs by number
    emit_title("Numerical Index", "by-sep-number", output)
    emit_column_headers(output)
    prev_sep = 0
    for sep in seps:
        if sep.number - prev_sep > 1:
            print(file=output)
        print(constants.text_type(sep), file=output)
        prev_sep = sep.number
    print(constants.table_separator, file=output)
    print(file=output)
    # Reserved SEP numbers
    emit_title("Reserved SEP Numbers", "reserved", output)
    emit_column_headers(output)
    for number, claimants in sorted(RESERVED):
        print(
            constants.column_format
            % {
                "type": ".",
                "status": ".",
                "number": number,
                "title": "RESERVED",
                "authors": claimants,
            },
            file=output,
        )
    print(constants.table_separator, file=output)
    print(file=output)
    # SEP types key
    emit_title("SEP Types Key", "type-key", output)
    for type_ in sorted(SEP.type_values):
        print(u"    %s - %s SEP" % (type_[0], type_), file=output)
        print(file=output)
    print(file=output)
    # SEP status key
    emit_title("SEP Status Key", "status-key", output)
    for status in sorted(SEP.status_values):
        # Draft SEPs have no status displayed, Active shares a key with Accepted
        if status in ("Active", "Draft"):
            continue
        if status == "Accepted":
            msg = "    A - Accepted (Standards Track only) or Active proposal"
        else:
            msg = "    {status[0]} - {status} proposal".format(status=status)
        print(msg, file=output)
        print(file=output)

    print(file=output)
    # SEP owners
    emit_title("Authors/Owners", "authors", output)
    authors_dict = verify_email_addresses(seps)
    max_name = max(authors_dict.keys(), key=normalized_last_first)
    max_name_len = len(max_name.last_first)
    author_table_separator = "=" * max_name_len + "  " + "=" * len("email address")
    print(author_table_separator, file=output)
    _author_header_fmt = "{name:{max_name_len}}  Email Address"
    print(
        _author_header_fmt.format(name="Name", max_name_len=max_name_len), file=output
    )
    print(author_table_separator, file=output)
    sorted_authors = sort_authors(authors_dict)
    _author_fmt = "{author.last_first:{max_name_len}}  {author_email}"
    for author in sorted_authors:
        # Use the email from authors_dict instead of the one from 'author' as
        # the author instance may have an empty email.
        _entry = _author_fmt.format(
            author=author, author_email=authors_dict[author], max_name_len=max_name_len
        )
        print(_entry, file=output)
    print(author_table_separator, file=output)
    print(file=output)
    print(file=output)
    # References for introduction footnotes
    emit_title("References", "references", output)
    print(constants.references, file=output)
    print(constants.footer, file=output)
