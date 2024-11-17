#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright (c) 2024 mcbazza
# Shouts out to: @x0rz, who created the excellent tweets_analyser (https://github.com/x0rz/tweets_analyzer/)
#                And if it wasn't for that asshat Elon, both tweets_analyzer and Twitter would still be working and/or great.
#
# Bazza's Disclaimer:
# As per the licence, please feel free to take this code and run with it as you see fit.
# As long as you abide by the following conditions:
#   * Please include attribution to @mcbazza - https://bsky.app/profile/mcbazza.com
#   * Ensure the shoutout to x0rz is retained
#   * Don't be a dick
#   * Nazis are to be punched
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, version 3 of the License.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#

#region import libraries

from atproto import Client

from datetime import datetime

import re
import argparse
import numpy
from ascii_graph import Pyasciigraph
from ascii_graph.colors import Gre, Yel, Red
from ascii_graph.colordata import hcolor
#endregion

__version__ = '0.1-dev'

try:
    from urllib.parse import urlparse
except ImportError:
    from urlparse import urlparse

from secrets import handle, password

#region Set initial veriables

activity_monthly = {
    ("%2i" % i).replace(" ", "0"): 0 for i in range(12)
}

activity_hourly = {
    ("%2i:00" % i).replace(" ", "0"): 0 for i in range(24)
}

activity_weekly = {
    "%i" % i: 0 for i in range(7)
}

# Here are sglobals used to store data - I know it's dirty, whatever
start_date = 0
end_date = 0
export = ""
jsono = {}
save_folder = "bsky_posts"
color_supported = True
ansi_escape = re.compile(r'\x1B\[[0-?]*[ -/]*[@-~]')
#endregion

#region Parse Args
parser = argparse.ArgumentParser(description=
    "Simple Bluesky Profile Analyzer (https://github.com/mcbazza/bsky_analyzer) version %s" % __version__,
                                 usage='%(prog)s -n <profile_name> [options]')
parser.add_argument('-l', '--limit', metavar='N', type=int, default=1000,
                    help='limit the number of posts to retreive (default=1000)')
# parser.add_argument('-n', '--name', required=True, metavar="profile_name",
parser.add_argument('-n', '--name', metavar="profile_name", default="mcbazza.com",
                    help='target profile_name')
parser.add_argument('--no-color', action='store_true',
                    help='disables colored output')
parser.add_argument('-s', '--summaries', metavar="summaries", default="dw",
                    help='which summary graphs to display (by day/week/month, default=dw)')
args = parser.parse_args()

# The account we're looking up
actor = args.name
#endregion

#region cprint
def cprint(strng):
    if not color_supported:
        strng = ansi_escape.sub('', strng)
    # if args.json is False:
    print(strng)
    # export_string(strng)
#endregion

#region int_to_month(day)
def int_to_month(month):
    months = "Jan Feb Mar Apr May Jun Jul Aug Sep Oct Nov Dec".split()
    return months[int(month) % len(months)]
#endregion

#region int_to_weekday
def int_to_weekday(day):
    weekdays = "Monday Tuesday Wednesday Thursday Friday Saturday Sunday".split()
    return weekdays[int(day) % len(weekdays)]
#endregion

#region print_charts
def print_charts(dataset, title, dwm='D'):
    """ Prints nice charts based on a dict {(key, value), ...} """
    chart = []
    keys = sorted(dataset.keys())
    mean = numpy.mean(list(dataset.values()))
    median = numpy.median(list(dataset.values()))
    
    for key in keys:

        match dwm:
            case "D":
                suffix_text = key
            case "W":
                suffix_text = int_to_weekday(key)
            case "M":
                suffix_text = int_to_month(key)
            case _:
                suffix_text = '??'

        if (dataset[key] >= median * 1.33):
            displayed_key = "%s (\033[92m+\033[0m)" % (suffix_text)
        elif (dataset[key] <= median * 0.66):
            displayed_key = "%s (\033[91m-\033[0m)" % (suffix_text)
        else:
            displayed_key = suffix_text

        chart.append((displayed_key, dataset[key]))

    thresholds = {
        int(mean): Gre, int(mean * 2): Yel, int(mean * 3): Red,
    }

    data = hcolor(chart, thresholds)

    graph = Pyasciigraph(
        separator_length=4,
        multivalue=False,
        human_readable='si',
    )

    for line in graph.graph(title, data):
        if not color_supported:
            ansi_escape = re.compile(r'\x1B\[[0-?]*[ -/]*[@-~]')
            line = ansi_escape.sub('', line)
        print(line)
    cprint("")
#endregion

#region main
def main() -> None:

    global start_date
    global end_date

    client = Client()
    client.login(handle, password)

    data = client.get_profile(actor)
    did = data.did

    display_name = data.display_name
    profile_desc = data.description
    account_created = data.created_at
    posts_count = data.posts_count
    followers_count = data.followers_count
    follows_count = data.follows_count

    # Getting account's metadata
    cprint("[+] Getting @%s account data..." % actor)
    cprint("[+] Followers      : \033[1m%s\033[0m" % str(followers_count))
    cprint("[+] Following      : \033[1m%s\033[0m" % str(follows_count))
    cprint("[+] statuses_count : \033[1m%s\033[0m" % str(posts_count))

    # Count how many posts we process
    post_count = 0

    # Set a cursor, as we can only page through posts max of 100 at a time
    cursor = None

    while True:

        author_feed = client.get_author_feed(
            actor=did,
            filter='posts_and_author_threads',
            cursor=cursor,
            limit=100,
        )

        feed = author_feed.feed

        list_length = len(feed)
        for post_no in range(list_length):

            if post_count > args.limit:
                break

            post_count += 1

            post_created_str = feed[post_no].post.record.created_at
            post_created_len = len(post_created_str)

            # The text format that we receive the date as
            # This is a fudge, as I noted during testing that not all posts came back with milliseconds
            if post_created_len == 24:
                dt_format = "%Y-%m-%dT%H:%M:%S.%fZ"
            else:
                dt_format = "%Y-%m-%dT%H:%M:%SZ"

            post_created = datetime.strptime(post_created_str, dt_format)

            end_date = end_date or post_created
            start_date = post_created

            post_text = feed[post_no].post.record.text
            
            activity_hourly["%s:00" % str(post_created.hour).zfill(2)] += 1
            activity_weekly[str(post_created.weekday())] += 1
            activity_monthly["%s" % str((post_created.month-1)).zfill(2)] += 1

        if not author_feed.cursor:
            break

        if post_count > args.limit:
            break

        # Update the cursor so we process the next group
        cursor = author_feed.cursor

    cprint("[+] Downloaded %d tweets from %s to %s (%d days)" % (post_count, start_date.strftime("%Y-%m-%d %H:%M:%S"), end_date.strftime("%Y-%m-%d %H:%M:%S"), (end_date - start_date).days))

    # Checking if we have enough data (considering it's good to have at least 30 days of data)
    if (end_date - start_date).days < 30 and (post_count < posts_count):
         cprint("[\033[91m!\033[0m] Looks like we do not have enough posts from user, you should consider retrying (--limit)")

    if (end_date - start_date).days != 0:
        cprint("[+] Average number of posts per day: \033[1m%.1f\033[0m" % (posts_count / float((end_date - start_date).days)))

    # Only display the required summary graphs requested
    if "d" in args.summaries.lower(): print_charts(activity_hourly, "Daily activity distribution (per hour)", dwm='D')
    if "w" in args.summaries.lower(): print_charts(activity_weekly, "Weekly activity distribution (per day)", dwm='W')
    if "m" in args.summaries.lower(): print_charts(activity_monthly, "Monthly activity distribution (per month)", dwm='M')
#endregion


#region Call main
if __name__ == '__main__':
    main()
#endregion
