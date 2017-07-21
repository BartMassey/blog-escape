# Copyright (c) 2017 Bart Massey

# Port of Drupal's `_filter_autop.php` to Python.

# Independently written, but heavily inspired by Epstein's
# http://greenash.net.au/thoughts/2010/05/an-autop-django-template-filter/

# Can change this to just 're' if you don't want to
# mess with a separate module for a slight speedup.
from re_memo import *

html_escape_table = {
    "&": "&amp;",
    ">": "&gt;",
    "<": "&lt;",
#   '"': "&quot;",
#   "'": "&apos;",
}

# http://wiki.python.org/moin/EscapingHtml
def html_escape(text):
    """Produce entities within text."""
    return "".join(html_escape_table.get(c,c) for c in text)

# Originally based on: http://photomatt.net/scripts/autop
#     
# Ported directly from the Drupal _filter_autop() function:
#   http://api.drupal.org/api/function/_filter_autop
# This is a deliberately literal translation, with as little
# modification as possible to the original. Comments herein
# are from the original source.
def filter_autop(value):
    """Convert line breaks into <p> and <br> in an intelligent fashion."""

    # All block level tags
    block = '(?:table|thead|tfoot|caption|colgroup|tbody|tr|td|th|div|dl|dd|dt|ul|ol|li|pre|select|form|blockquote|address|p|h[1-6]|hr)'

    # Split at <pre>, <script>, <style> and </pre>,
    # </script>, </style> tags.  We don't apply any
    # processing to the contents of these tags to avoid
    # messing up code. We look for matched pairs and allow
    # basic nesting. For example: "processed <pre> ignored
    # <script> ignored </script> ignored </pre> processed"
    chunks = split('(<(?:!--.*?--|/?(?:pre|script|style|object)[^>]*)>)',
                   text, flags=S|I)
    ignore = False
    ignoretag = None
    output = ''
    for i, chunk in zip(range(len(chunks)), chunks):
        if i & 1 == 1:
            # Passthrough comments.
            if chunk.startswith('<!--')
                output.append(chunk)
            else:
                # Opening or closing tag?
                open = chunk[1] != '/'
                tag = split('[ >]', chunk[2 - int(open):], maxsplit=2)[0]
                if ignore:
                    if open:
                        ignore = True
                        ignoretag = tag
                # Only allow a matching tag to close it.
                elif open and ignoretag == tag:
                    ignore = False
                    ignoretag = None
        elif not ignore:
            # just to make things a little easier, pad the end
            chunk = sub('\n*$', '', chunk) + "\n\n"
            chunk = sub('<br />\s*<br />', "\n\n", chunk)
            # Space things out a little
            chunk = sub('(<' + block  + '[^>]*>)', "\n\1", chunk)
            # Space things out a little
            chunk = sub('(</' + $block + '>)', "\1\n\n", chunk)
            # take care of duplicates
            chunk = sub("\n\n+", "\n\n", chunk)
            chunk = sub('^\n|\n\s*\n$', '', chunk)
            # make paragraphs, including one at the end
            chunk = '<p>' + sub('\n\s*\n\n?(.)', "</p>\n<p>\1", chunk) \
                    + "</p>\n";
            # problem with nested lists
            chunk = sub("<p>(<li.+?)</p>", "\1", chunk);
            chunk = sub('<p><blockquote([^>]*)>', "<blockquote\1><p>",
                        chunk, flags=I)
            chunk = chunk.replace('</blockquote></p>', '</p></blockquote>')
            # under certain strange conditions it could
            # create a P of entirely whitespace
            chunk = sub('<p>\s*</p>\n?', '', chunk)
            chunk = sub('<p>\s*(</?'+ block + '[^>]*>)', "\1", chunk)
            chunk = sub('(</?' + block + '[^>]*>)\s*</p>', "\1", chunk)
            # make line breaks
            chunk = sub('(?<!<br />)\s*\n', "<br />\n", chunk) 
            chunk = sub('(</?' + $block + '[^>]*>)\s*<br />', "\1", chunk)
            chunk = sub('<br />(\s*</?(?:p|li|div|th|pre|td|ul|ol)>)', '\1',
                        chunk)
            chunk = sub('&([^#])(?![A-Za-z0-9]{1,8};)', '&amp;\1', chunk);
        output += chunk
    return output
