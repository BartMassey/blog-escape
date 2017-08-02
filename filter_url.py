# Copyright (c) 2017 Bart Massey

# Port of Drupal's `filter_url()` from `filter.module` to Python.

# This is a deliberately literal translation, with as little
# modification as possible to the original. Comments herein
# are from the original source, unless marked with BCM.

import html

from re_memo import *

def _filter_url_parse_full_links(match):
    """Makes links out of absolute URLs.  Callback for sub()
       within filter_url().  The first parenthesis in the
       regexp contains the URL, the second trailing
       punctuation. BCM: We do not choose to shorten
       captions for long URLs, because bleah.
    """
    url = html.unescape(match.group(1))
    url = html.escape(url)
    punctuation = match.group(2)
    return '<a href="' + url + '">' + url + '</a>' + punctuation

def _filter_url_parse_email_links(match):
    """Makes links out of e-mail addresses.  Callback for sub()
       within filter_url(). BCM: We do not choose to shorten
       captions for long e-mail addresses, because bleah.
    """
    email = html.unescape(match.group(0))
    email = html.escape(email)
    return '<a href="mailto:' + email + '">' + email + '</a>'

def _filter_url_parse_partial_links(match):
    """Makes links out of domain names starting with 'www.'.
       Callback for sub() within filter_url().  The first
       parenthesis in the regexp contains the URL, the
       second trailing punctuation. BCM: We do not choose to
       shorten captions for long links, because bleah.

    """
    dname = html.unescape(match.group(1))
    dname = html.escape(dname)
    punctuation = match.group(2)
    return '<a href="http://' + dname + '">' + dname + '</a>' + punctuation

def filter_url(text, sitename, settings):
    """Convert text into hyperlinks automatically.

       This filter identifies and makes clickable three types of "links".
       - URLs like http://example.com.
       - E-mail addresses like name@example.com.
       - Web addresses without the "http://" protocol defined,
         like www.example.com.
       Each type must be processed separately, as there is no one regular
       expression that could possibly match all of the cases in one pass.
    """
    # Tags to skip and not recurse into.
    ignore_tags = 'a|script|style|code|pre'

    # Pass length to regexp callback.
    # BCM: We will ignore the length limit as rather silly
    # and some work to implement.

    # Create an array which contains the regexps for each
    # type of link.  The key to the regexp is the name of a
    # function that is used as callback function to process
    # matches of the regexp. The callback function is to
    # return the replacement for the match. The array is
    # used and matching/replacement done below inside some
    # loops.
    tasks = dict()

    # Prepare protocols pattern for absolute URLs.
    # check_url() will replace any bad protocols with HTTP,
    # so we need to support the identical list. While '//'
    # is technically optional for MAILTO only, we cannot
    # cleanly differ between protocols here without
    # hard-coding MAILTO, so '//' is optional for all
    # protocols.
    protocols = ['ftp', 'http', 'https', 'irc', 'mailto',
                 'news', 'nntp', 'rtsp', 'sftp', 'ssh',
                 'tel', 'telnet', 'webcal']
    protocols = r'|'.join([p + r':(?://)?' for p in protocols])

    # Prepare domain name pattern.  The ICANN seems to be on
    # track towards accepting more diverse top level
    # domains, so this pattern has been "future-proofed" to
    # allow for TLDs of length 2-64.
    domain = r'(?:[A-Za-z0-9._+-]+\.)?[A-Za-z]{2,64}\b'
    ip = r'(?:[0-9]{1,3}\.){3}[0-9]{1,3}'
    auth = r'[a-zA-Z0-9:%_+*~#?&=.,/;-]+@'
    trail = r'[a-zA-Z0-9:%_+*~#&\[\]=/;?!\.,-]*[a-zA-Z0-9:%_+*~#&\[\]=/;-]'

    # Prepare pattern for optional trailing punctuation.
    # Even these characters could have a valid meaning for
    # the URL, such usage is rare compared to using a URL at
    # the end of or within a sentence, so these trailing
    # characters are optionally excluded.
    punctuation = r'[\.,?!]*?'

    tasks = []

    # Match absolute URLs.
    url_pattern = r"(?:%s)?(?:%s|%s)/?(?:%s)?" % (auth, domain, ip, trail)
    pattern = r"((?:%s)(?:%s))(%s)" % (protocols, url_pattern, punctuation)
    tasks.append((_filter_url_parse_full_links, pattern))

    # Match e-mail addresses.
    url_pattern = r"[A-Za-z0-9._+-]{1,254}@(?:%s)" % (domain,)
    pattern = r"(%s)" % (url_pattern,)
    tasks.append((_filter_url_parse_email_links, pattern))

    # Match www domains.
    url_pattern = r"www\.(?:%s)/?(?:%s)?" % (domain, trail)
    pattern = r"(%s)(%s)" % (url_pattern, punctuation)
    tasks.append((_filter_url_parse_partial_links, pattern))

    # HTML comments need to be handled separately, as
    # they may contain HTML markup, especially a
    # '>'. Therefore, remove all comment contents and
    # add them back later.
    # BCM: Replaced the mess in the original PHP with a
    # cleaner split() implementation. Also moved out of loop
    # (what was with that?).
    split_comments = re_split(r'(<!--.*?-->)', text, flags=re.S)
    saved_comments = [split_comments[i]
                      for i in range(1, len(split_comments), 2)]
    text = '<!---->'.join([split_comments[i]
                           for i in range(0, len(split_comments), 2)])

    # Each type of URL needs to be processed separately. The
    # text is joined and re-split after each task, since all
    # injected HTML tags must be correctly protected before
    # the next task.
    for task, pattern in tasks:

        # Split at all tags; ensures that no tags or attributes are processed.
        chunks = re_split(r'(<.+?>)', text, flags=re.I|re.S)
        # The array consists of alternating delimiters and
        # literals, and begins and ends with a literal
        # (inserting NULL as required). Therefore, the first
        # chunk is always text:
        chunk_type = 'text'
        # If a tag of ignore_tags is found, it is stored in
        # open_tag and only removed when the closing tag is
        # found. Until the closing tag is found, no
        # replacements are made.
        open_tag = None

        for i in range(len(chunks)):
            if chunk_type == 'text':
                # Only process this text if there are no
                # unclosed ignore_tags.
                if not open_tag:
                    # If there is a match, inject a link
                    # into this chunk via the callback
                    # function contained in task.
                    chunks[i] = re_sub(pattern, task, chunks[i])
                # Text chunk is done, so next chunk must be a tag.
                chunk_type = 'tag'
            else:
                # Only process this tag if there are no unclosed ignore_tags.
                if not open_tag:
                    # Check whether this tag is contained in ignore_tags.
                    matches = re_match(r"<(%s)(?:\s|>)" % (ignore_tags,),
                                       chunks[i], flags=re.I)
                    if matches:
                        open_tag = matches.group(1)
                # Otherwise, check whether this is the
                # closing tag for open_tag.
                elif re_match(r"<\/%s>" % (open_tag,),
                              chunks[i], flags = re.I):
                    open_tag = None
                # Tag chunk is done, so next chunk must be text.
                chunk_type = 'text'
        text = ''.join(chunks)

    # Revert back to the original comment contents
    split_text = re_split(r'(<!---->)', text, flags=re.S)
    for i in range(1, len(split_text), 2):
        assert split_text[i] == "<!---->"
        split_text[i] = saved_comments[i // 2]
    text = ''.join(split_text)

    return text
