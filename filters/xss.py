# Copyright (c) 2017 Bart Massey
# This work is available under the "MIT license".
# Please see the file COPYING in this distribution
# for license terms.

# Sanitize HTML content.

from re_memo import *
from make_logger import *

# Change to True for logging to stderr
xss_log = make_logger("filter_xss", False)

# This is a literal-minded port of the corresponding Drupal
# functionality. Some security-important stuff has been
# left out because hard to implement and not obviously OK,
# handled elsewhere in this implementation, etc.

# Tags that are deemed generally safe for use. Why is "a" there?
# I don't know.
default_allowed_tags = [
    'a', 'em', 'strong', 'cite', 'blockquote', 'code',
    'ul', 'ol', 'li', 'dl', 'dt', 'dd'
]
                         
def filter_xss(string, allowed_tags=default_allowed_tags):
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
        xss_log("---%s" % (attr,))
        attrarr = list()
        mode = 0
        attrname = None

        while len(attr) != 0:
            # Was the last operation successful?
            working = False

            xss_log("  --%d %s" % (mode, attr))

            if mode ==  0:
                # Attribute name, href for instance.
                # BCM: Here and just below, added _
                # to id pattern. Apparently something
                # in Drupal is already expected to have
                # transformed it into - before we get here?
                # Or maybe we're traversing the filters
                # in the wrong order, or something?
                match = re_match(r'^([-_a-zA-Z]+)', attr)
                if match:
                    attrname = match.group(1).lower()
                    # BCM: 'on' ???
                    skip = attrname == 'style' or attrname[0:2] == 'on'
                    working = True
                    mode = 1
                    attr = re_sub('^[-_a-zA-Z]+', '', attr)

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
                for q in ['"', "'", ""]:
                    if q == "":
                        qpat = r"\s\"'"
                    else:
                        qpat = q
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
                        attr = re_sub(attr_pat, '', attr)
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
        xss_log(attrarr)
        xss_log("---complete\n")
        return attrarr

    # Return cleaned-up version of XHTML element.
    def filter_xss_split(match):
        string = match.group(0)
        if string[0] != '<':
            # We matched a lone ">" character.
            assert string == '>'
            return '&gt;'
        elif len(string) == 1:
            # We matched a lone "<" character.
            assert string == '<'
            return '&lt;'

        matches = \
          re_match(r'^<\s*(/\s*)?([a-zA-Z0-9\-]+)([^>]*)>?|(<!--.*?-->)$',
                   string)
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

        if slash:
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
        
    result = re_sub(r"""
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
    return result

# All tags that should be clean and OK.
admin_tags = [
    'a', 'abbr', 'acronym', 'address', 'article', 'aside',
    'b', 'bdi', 'bdo', 'big', 'blockquote', 'br', 'caption',
    'cite', 'code', 'col', 'colgroup', 'command', 'dd', 'del',
    'details', 'dfn', 'div', 'dl', 'dt', 'em', 'figcaption',
    'figure', 'footer', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6',
    'header', 'hgroup', 'hr', 'i', 'img', 'ins', 'kbd', 'li',
    'mark', 'menu', 'meter', 'nav', 'ol', 'output', 'p', 'pre',
    'progress', 'q', 'rp', 'rt', 'ruby', 's', 'samp', 'section',
    'small', 'span', 'strong', 'sub', 'summary', 'sup', 'table',
    'tbody', 'td', 'tfoot', 'th', 'thead', 'time', 'tr', 'tt',
    'u', 'ul', 'var', 'wbr' ]

def filter_xss_admin(string):
    """Do minimal filtering and format canonicalization."""
    return filter_xss(string, allowed_tags=admin_tags)
