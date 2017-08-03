#!/usr/bin/python3
# Copyright (c) 2017 Bart Massey
# This work is available under the "MIT license".
# Please see the file COPYING in this distribution
# for license terms.

# Sanitize HTML content.

from re_memo import *

# This is a fairly literal port of the corresponding Drupal
# functionality.

# Tags that are deemed generally safe for use. Why is "a" there?
# I don't know.
default_allowed_tags = [
    'a', 'em', 'strong', 'cite', 'blockquote', 'code',
    'ul', 'ol', 'li', 'dl', 'dt', 'dd'
]
                         
def filter_xss(string, sitename, allowed_tags=default_allowed_tags):
    """Return the given HTML-ish content with
       dangerous "XSS" content stripped and
       tags normalized.

       BCM: We assume we've been handed valid UTF-8 and
       don't do anything special to check or clean this.
    """
    # Remove NULL characters (ignored by some browsers).
    string = string.replace("\0", "")
    # Remove Netscape 4 JS entities.
    string = re_sub(r'&\s*\{[^}]*(\}\s*;?|$)', '', string)
    # Defuse all HTML entities.
    string = string.replace(r'&', r'&amp;')
    # Change back only well-formed entities in our whitelist:
    # Decimal numeric entities.
    string = re_sub(r'&amp;#([0-9]+;)', r'&#\1', string)
    # Hexadecimal numeric entities.
    string = re_sub(r'&amp;#[Xx]0*((?:[0-9A-Fa-f]{2})+;)', r'&#x\1', string)
    # Named entities.
    string = re_sub(r'&amp;([A-Za-z][A-Za-z0-9]*;)', r'&\1', string)
    
    # Process a string of HTML attributes, returning a
    # cleaned-up version.
    def filter_xss_attributes(attr):
        attrarr = list
        mode = 0
        attrname = ''

        while len(attr) != 0:
            # Was the last operation successful?
            working = False

            if mode ==  0:
                # Attribute name, href for instance.
                match = re_match(r'^([-a-zA-Z]+)', attr)
                if match:
                    attrname = match.group(1).lower()
                    # BCM: 'on' ???
                    skip = attrname == 'style' or attrname[0:2] == 'on'
                    working = True
                    mode = 1
                    attr = re_sub('^[-a-zA-Z]+', '', attr)

            elif mode == 1:
                # Equals sign or valueless ("selected").
                if re_match(r'^\s*=\s*', attr):
                    working = True
                    mode = 2
                    attr = re_sub(r'^\s*=\s*', '', attr)
                elif re_match(r'^\s+', attr):
                    working = True
                    mode = 0
                    if not skip:
                        attrarr.append(attrname)
                    attr = re_sub(r'^\s+', '', attr)
          
            elif mode == 2:
                # Attribute value, a URL after href= for
                # instance.  BCM: Changed the flow of
                # control pretty substantially here because
                # Python has no assignment in conditionals
                # and to remove duplicate code.
                for q, qpat in [('"', '"'),
                                ("'", "'"),
                                ("", r"\s\"'")]:
                    attr_pat = r'^%s([^%s]*)%s(\s+|$)' % (q, qpat, q)
                    match = re_match(attr_pat, attr)
                    if match:
                        thisval = match.group(1)
                        if not skip:
                            if q == '':
                                q = '"'
                            asgn_pat = r"%%s=%s%%s%s" % (q, q)
                            attrarr.append(asgn_pat % (attrname, thisval))
                            working = True
                        mode = 0
                        attr = preg_replace(attr_pat, '', attr)
                        break

            if not working:
                # Not well formed; remove and try again.
                attr = re_sub("""
                  ^
                  (
                  "[^"]*("|$)     # - a string that starts with a double quote, up until the next double quote or the end of the string
                  |               # or
                  \'[^\']*(\'|$)| # - a string that starts with a quote, up until the next quote or the end of the string
                  |               # or
                  \S              # - a non-whitespace character
                  )*              # any number of the above three
                  \s*             # any number of whitespaces
                """, '', attr, flags=re.X)
                mode = 0

        # The attribute list ends with a valueless attribute like "selected".
        if mode == 1 and not skip:
            attrarr.append(attrname)
        return attrarr

    # Return cleaned-up version of XHTML element.
    def filter_xss_split(match):
        tag = match.group(0)
        if tag[0] != '<':
            # We matched a lone ">" character.
            assert tag == '>'
            return '&gt;'
        elif len(tag) == 1:
            # We matched a lone "<" character.
            assert tag == '<'
            return '&lt;'

        matches = \
          re_match(r'^<\s*(/\s*)?([a-zA-Z0-9\-]+)([^>]*)>?|(<!--.*?-->)$',
                   tag)
        if not matches:
            # Seriously malformed.
            return ''

        slash = matches.group(1)
        if slash:
            slash = slash.strip()
        elem = matches.group(2)
        if elem:
            elem = elem.lower()
        attrlist = matches.group(3)
        comment = matches.group(4)

        if (comment):
            elem = '!--'

        if elem not in set(allowed_tags):
          # Disallowed HTML element.
          return ''

        # BCM: Because of the last bit, we normally will
        # throw away comments. This is probably not the
        # intent, but there you are. Use '!--' in allowed
        # tags to save comments. Ugh.
        if comment:
            return comment

        if slash != '':
            return "</%s>" % (elem,)

        # Is there a closing XHTML slash at the end of the attributes?
        attrlist, count = re_subn(r'(\s?)/\s*$', r'\1', attrlist)
        if count > 0:
            xhtml_slash = ' /'
        else:
            xhtml_slash = ''

        # Clean up attributes.
        attr2 = ' '.join(filter_xss_attributes(attrlist))
        attr2 = re_sub(r'[<>]', '', attr2)
        if len(attr2) > 0:
            attr2 = ' ' + attr2

        return "<%s%s%s>" % (elem, attr2, xhtml_slash)
        
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
