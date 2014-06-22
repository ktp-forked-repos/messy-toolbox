#!/usr/bin/env python2.7

import csv
import sys
import argparse
import re

parser = argparse.ArgumentParser()
parser.add_argument('--show-headers', '-H', action='store_true', required=False, dest='show_headers')
parser.add_argument('--fields', '-f', action='store', nargs='*', required=False, dest='fields')
parser.add_argument('--separator', '-s', action='store', required=False, default=' ', dest='separator')
parser.add_argument('--align', '-a', action='store_true', required=False, default=False, dest='align')
parser.add_argument('file', action='store')
args = parser.parse_args()

headers = []
fields = None
alignment = None

for line in open(args.file, 'rb'):
    # skip lines with nulls (wtf?)
    if '\0' in line:
        continue

    row = csv.reader([line]).next()

    if len(row) < 1:
        continue

    if len(headers) < 1:
        headers = row

    if args.show_headers:
        for x in xrange(len(headers)):
            print "[{0}] {1}".format(x, headers[x])

        sys.exit(0)

    if fields is None:
        fields = headers
        if args.fields > 0:
            fields = args.fields

        # turn fields into indexes
        fields = [int(f) if re.match('^[0-9]+$', f) else headers.index(f) for f in fields]
        if args.align:
            alignment = [len(row[i]) for i in fields]

    # alignment requires second pass
    if args.align:
        try:
            alignment = [len(row[fields[i]]) if len(row[fields[i]]) > alignment[i] else alignment[i] for i in xrange(0, len(fields))]
        except Exception, e:
            pass
        continue

    try:
        print args.separator.join([row[i] for i in fields])
    except Exception, e:
        pass

if args.align:
    format_strings = ['{:' + str(x) + 's}' for x in alignment]
    #print format_strings
    #print fields
    # second pass if we specified alignment
    for line in open(args.file, 'rb'):
        # skip lines with nulls (wtf?)
        if '\0' in line:
            continue

        row = csv.reader([line]).next()

        if len(row) < 1:
            continue

        try:
            print args.separator.join([format_strings[i].format(row[int(fields[i])]) for i in xrange(0, len(fields))])
        except Exception, e:
            pass
