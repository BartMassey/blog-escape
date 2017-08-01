# Copyright (c) 2017 Bart Massey

# Port of Drupal's `filter_url()` from `filter.module` to Python.

from re_memo import *

# This is a deliberately literal translation, with as little
# modification as possible to the original. Comments herein
# are from the original source, unless marked with BCM.

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
    #_filter_url_trim(NULL, $filter->settings['filter_url_length']);

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

    # Match absolute URLs.
    url_pattern = r"(?:%s)?(?:%s|%s)/?(?:%s)?" % (auth, domain, ip, trail)
    pattern = r"((?:%s)(?:%s))(%s)" % (protocols, url_pattern, punctuation)
    tasks['_filter_url_parse_full_links'] = pattern

    # Match e-mail addresses.
    url_pattern = r"[A-Za-z0-9._+-]{1,254}@(?:%s)" % (domain,)
    pattern = r"(%s)" % (url_pattern,)
    tasks['_filter_url_parse_email_links'] = pattern

    # Match www domains.
    url_pattern = r"www\.(?:%s)/?(?:%s)?" % (domain, trail)
    pattern = r"(%s)(%s)" % (url_pattern, punctuation)
    tasks['_filter_url_parse_partial_links'] = pattern

    # Each type of URL needs to be processed separately. The
    # text is joined and re-split after each task, since all
    # injected HTML tags must be correctly protected before
    # the next task.
    for task, pattern in tasks.items():
        # HTML comments need to be handled separately, as
        # they may contain HTML markup, especially a
        # '>'. Therefore, remove all comment contents and
        # add them back later.
        # BCM: Replaced the mess in the original PHP with a
        # cleaner split() implementation.
        split_comments = re_split(r'(<!--(?:.*?)-->)?', flags=re.S)
        saved_comments = [split_comments[i]
                          for i in range(0, len(split_comments) + 1, 2)]
        text = '<!---->'.join([split_comments[i]
                               for i in range(1, len(split_comments) + 1, 2)])

        # Split at all tags; ensures that no tags or attributes are processed.
        $chunks = preg_split('/(<.+?>)/is', $text, -1, PREG_SPLIT_DELIM_CAPTURE);
        # PHP ensures that the array consists of alternating delimiters and
        # literals, and begins and ends with a literal (inserting NULL as
        # required). Therefore, the first chunk is always text:
        $chunk_type = 'text';
        # If a tag of $ignore_tags is found, it is stored in $open_tag and only
        # removed when the closing tag is found. Until the closing tag is found,
        # no replacements are made.
        $open_tag = '';

        for ($i = 0; $i < count($chunks); $i++) {
          if ($chunk_type == 'text') {
            # Only process this text if there are no unclosed $ignore_tags.
            if ($open_tag == '') {
              # If there is a match, inject a link into this chunk via the callback
              # function contained in $task.
              $chunks[$i] = preg_replace_callback($pattern, $task, $chunks[$i]);
            }
            # Text chunk is done, so next chunk must be a tag.
            $chunk_type = 'tag';
          }
          else {
            # Only process this tag if there are no unclosed $ignore_tags.
            if ($open_tag == '') {
              # Check whether this tag is contained in $ignore_tags.
              if (preg_match("`<($ignore_tags)(?:\s|>)`i", $chunks[$i], $matches)) {
                $open_tag = $matches[1];
              }
            }
            # Otherwise, check whether this is the closing tag for $open_tag.
            else {
              if (preg_match("`<\/$open_tag>`i", $chunks[$i], $matches)) {
                $open_tag = '';
              }
            }
            # Tag chunk is done, so next chunk must be text.
            $chunk_type = 'text';
          }
        }

        $text = implode($chunks);
        # Revert back to the original comment contents
        _filter_url_escape_comments('', FALSE);
        $text = preg_replace_callback('`<!--(.*?)-->`', '_filter_url_escape_comments', $text);
      }

    return $text;
