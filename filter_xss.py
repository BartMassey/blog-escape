#!/usr/bin/python3
# Copyright (c) 2017 Bart Massey
# This work is available under the "MIT license".
# Please see the file COPYING in this distribution
# for license terms.

# Sanitize HTML content.

# This is a fairly literal port of the corresponding Drupal
# functionality.

# Tags that are deemed generally safe for use. Why is "a" there?
# I don't know.
default_allowed_tags = [
    'a', 'em', 'strong', 'cite', 'blockquote', 'code',
    'ul', 'ol', 'li', 'dl', 'dt', 'dd'
]
                         
def validate_utf8(s):
    try:
        s.decode('utf-8')
        return True
    except UnicodeDecodeError:
        return False

def filter_xss(string, sitename, allowed_tags=default_allowed_tags):
    """Return the given HTML-ish content with
       dangerous "XSS" content stripped and
       tags normalized.
    """
    if not validate_utf8(string):
        return ""
    # Remove NULL characters (ignored by some browsers).
    string = string.replace("\0", "")
    # Remove Netscape 4 JS entities.
    string = re_sub(r'&\s*\{[^}]*(\}\s*;?|$)', '', string)
    # Defuse all HTML entities.
    string = string.replace('&', '&amp;', string)
    # Change back only well-formed entities in our whitelist:
    # Decimal numeric entities.
    string = re_sub(r'&amp;#([0-9]+;)', r'&#\1', string)
    # Hexadecimal numeric entities.
    string = re_sub(r'&amp;#[Xx]0*((?:[0-9A-Fa-f]{2})+;)', r'&#x\1', string)
    # Named entities.
    string = re_sub(r'&amp;([A-Za-z][A-Za-z0-9]*;)', r'&\1', string)
    
    return re_sub(r"""
    (
    <(?=[^a-zA-Z!/])  # a lone <
    |                 # or
    <!--.*?-->        # a comment
    |                 # or
    <[^>]*(>|$)       # a string that starts with a <, up until the > or the en\
d of the string
    |                 # or
    >                 # just a >
    )""", filter_xss_split, string, flags=re.X)
