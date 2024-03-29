# -*- coding: utf-8 -*-
AUTHOR = u'JongMan'
SITENAME = u"The Yearly Prophet"
SITEURL = 'http://theyearlyprophet.com'

DISQUS_SITENAME = "theyearlyprophet"
PDF_GENERATOR = False
DEFAULT_PAGINATION = 5
WITH_PAGINATION = True
TIMEZONE = "America/Chicago"

MD_EXTENSIONS = ('codehilite(force_linenos=False)', 'extra')

FEED_RSS = 'feeds/rss.xml'
FEED_MAX_ITEMS = 20

# global metadata to all the contents
#DEFAULT_METADATA = (('yeah', 'it is'),)

# static paths will be copied under the same name
STATIC_PATHS = ["images"]

# A list of files to copy from the source to the destination
FILES_TO_COPY = (('extra/robots.txt', 'robots.txt'),)
