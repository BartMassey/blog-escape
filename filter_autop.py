# Copyright (c) 2017 Bart Massey

# Port of Drupal's `_filter_autop.php` to Python.

# Independently written, but heavily inspired by Epstein's
# http://greenash.net.au/thoughts/2010/05/an-autop-django-template-filter/

import re

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

def filter_autop(value):
    """
    Convert line breaks into <p> and <br> in an intelligent fashion.
    Originally based on: http://photomatt.net/scripts/autop
    
    Ported directly from the Drupal _filter_autop() function:
    http://api.drupal.org/api/function/_filter_autop
    """

    # All block level tags
    block = '(?:table|thead|tfoot|caption|colgroup|tbody|tr|td|th|div|dl|dd|dt|ul|ol|li|pre|select|form|blockquote|address|p|h[1-6]|hr)'

    # Split at <pre>, <script>, <style> and </pre>,
    # </script>, </style> tags.  We don't apply any
    # processing to the contents of these tags to avoid
    # messing up code. We look for matched pairs and allow
    # basic nesting. For example: "processed <pre> ignored
    # <script> ignored </script> ignored </pre> processed"
    chunks = re.split('(<(?:!--.*?--|/?(?:pre|script|style|object)[^>]*)>)',
                      text, flags=re.S|re.I)
    ignore = False
    ignoretag = ''
    output = ''
    for i, chunk in zip(range(len(chunks)), chunks):
        if i & 1 == 1:
            # Passthrough comments.
            if chunk.startswith('<!--')
                output.append(chunk)
            else:
                # Opening or closing tag?
                open = $chunk[1] != '/'
