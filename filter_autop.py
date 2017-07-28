# Copyright (c) 2017 Bart Massey

# Port of Drupal's `_filter_autop.php` to Python.

# Independently written, but heavily inspired by Epstein's
# http://greenash.net.au/thoughts/2010/05/an-autop-django-template-filter/

import re
# This provides memoized implementations of some re
# functions to avoid recompiling on every run.
from re_memo import *

# Originally based on: http://photomatt.net/scripts/autop
#     
# Ported directly from the Drupal _filter_autop() function:
#   http://api.drupal.org/api/function/_filter_autop
# This is a deliberately literal translation, with as little
# modification as possible to the original. Comments herein
# are from the original source, unless marked with BCM.
def filter_autop(text):
    """Convert line breaks into <p> and <br> in an intelligent fashion."""

    # All block level tags
    block = '(?:table|thead|tfoot|caption|colgroup|tbody|tr|td|th|div|dl|dd|dt|ul|ol|li|pre|select|form|blockquote|address|p|h[1-6]|hr)'

    # Split at <pre>, <script>, <style> and </pre>,
    # </script>, </style> tags.  We don't apply any
    # processing to the contents of these tags to avoid
    # messing up code. We look for matched pairs and allow
    # basic nesting. For example: "processed <pre> ignored
    # <script> ignored </script> ignored </pre> processed"
    chunks = re_split('(<(?:!--.*?--|/?(?:pre|script|style|object)[^>]*)>)',
                   text, flags=re.S|re.I)
    ignore = False
    ignoretag = None
    output = ''
    for i, chunk in zip(range(len(chunks) + 1), chunks):
        if i & 1 == 1:
            # Passthrough comments.
            if chunk[1:4] == '!--':
                # BCM: This looks like a bug to me, but one
                # that Drupal wouldn't see since the only normal
                # comment is <!--break-->, which is apparently
                # prefiltered by Drupal. In any case, this fix
                # prevents doubling the comments.
                # output += chunk
                pass
            else:
                # Opening or closing tag?
                open = chunk[1] != '/'
                tag = re_split('[ >]', chunk[2 - int(open):], maxsplit=2)[0]
                if not ignore:
                    if open:
                        ignore = True
                        ignoretag = tag
                # Only allow a matching tag to close it.
                elif not open and ignoretag == tag:
                    ignore = False
                    ignoretag = None
        elif not ignore:
            # just to make things a little easier, pad the end
            chunk = re_sub(r'\n*$', '', chunk) + "\n\n"
            chunk = re_sub(r'<br />\s*<br />', "\n\n", chunk)
            # Space things out a little
            chunk = re_sub('(<' + block  + '[^>]*>)', "\n\\1", chunk)
            # Space things out a little
            chunk = re_sub('(</' + block + '>)', "\\1\n\n", chunk)
            # take care of duplicates
            chunk = re_sub(r"\n\n+", "\n\n", chunk)
            chunk = re_sub(r'^\n|\n\s*\n$', '', chunk)
            # make paragraphs, including one at the end
            chunk = '<p>' + re_sub(r'\n\s*\n\n?(.)', "</p>\n<p>\\1", chunk) \
                    + "</p>\n";
            # problem with nested lists
            chunk = re_sub(r"<p>(<li.+?)</p>", "\\1", chunk);
            chunk = re_sub(r'<p><blockquote([^>]*)>', "<blockquote\\1><p>",
                        chunk, flags=re.I)
            chunk = chunk.replace(r'</blockquote></p>', '</p></blockquote>')
            # under certain strange conditions it could
            # create a P of entirely whitespace
            chunk = re_sub(r'<p>\s*</p>\n?', '', chunk)
            chunk = re_sub(r'<p>\s*(</?'+ block + '[^>]*>)', "\\1", chunk)
            chunk = re_sub(r'(</?' + block + '[^>]*>)\s*</p>', "\\1", chunk)
            # make line breaks
            chunk = re_sub(r'(?<!<br />)\s*\n', "<br />\n", chunk) 
            chunk = re_sub(r'(</?' + block + '[^>]*>)\s*<br />', "\\1", chunk)
            chunk = re_sub(r'<br />(\s*</?(?:p|li|div|th|pre|td|ul|ol)>)',
                           '\\1', chunk)
            chunk = re_sub(r'&([^#])(?![A-Za-z0-9]{1,8};)', '&amp;\\1', chunk)
        output += chunk
    return output
