# Copyright (c) 2017 Bart Massey
# This work is available under the "MIT license".
# Please see the file COPYING in this distribution
# for license terms.

# Filter URLs to be root-relative and have consistent file
# naming.

from re_memo import *

# Given the domainname of the Drupal site (to be removed)
# and the page content string, return the page content
# string with the URLs cleaned up.
def filter_urlclean(content, sitename):
    # Escape the dots in the sitename.
    sitename = re_sub(r'\.', r'\.', sitename)
    # Rewrite hrefs and srcs.
    target = '(href|HREF) *= *"https?://%s/([^"]*)' % (sitename,)
    content = re_sub(target, r'href="/\2', content)
    # Rewrite srcs.
    target = '(src|SRC) *= *"https?://%s/([^"]*)' % (sitename,)
    content = re_sub(target, r'src="/\2', content)
    # Rewrite odd filepaths.
    target = '(src|href)="/sites/%s/files/' % (sitename,)
    content = re_sub(target,r'\1="/files/', content)
    target = '(src|href)="/system/files/'
    content = re_sub(target,r'\1="/files/', content)
    target = '(src|href)="/files/images/'
    content = re_sub(target,r'\1="/files/', content)
    target = '(src|href)="/files/files/'
    content = re_sub(target,r'\1="/files/', content)
    # All done.
    return content
