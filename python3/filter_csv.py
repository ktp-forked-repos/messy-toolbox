#!/usr/bin/env python3
import csv
import fnmatch
import re
import logging
import sys

class Filter(object):
    def __init__(self, value=None):
        self.value = value

class StringFilter(Filter):
    def is_filtered(self, data):
        return self.value in data

    def __str__(self):
        return 'str({0})'.format(self.value)

class GlobFilter(Filter):
    def is_filtered(self, data):
        return fnmatch.fnmatch(data, self.value)

    def __str__(self):
        return 'glob({0})'.format(self.value)

class RegexFilter(Filter):
    def is_filtered(self, data):
        return re.search(self.value, data)

    def __str__(self):
        return 're({0})'.format(self.value)

class CSVFilter(object):
    def __init__(self, path):
        self.filters = []
        logging.debug("loading filters from {0}".format(path))
        with open(path, 'r') as fp:
            for row in csv.reader(fp):
                filter_row = []
                for column in row:
                    if column.startswith('s:'):
                        filter_row.append(StringFilter(column[2:]))
                    elif column.startswith('g:'):
                        filter_row.append(GlobFilter(column[2:]))
                    elif column.startswith('r:'):
                        filter_row.append(RegexFilter(column[2:]))
                    else:
                        filter_row.append(None)
                    if filter_row[-1] is not None:
                        logging.debug("loaded {0}".format(filter_row[-1].value))

                self.filters.append(filter_row)

    def is_filtered(self, row):
        for filter_row in self.filters:
            if len(filter_row) != len(row):
                logging.warning("the number of columns in your filter do not match the number of columns in your file")
                return False

            available_filter_count = len([f for f in filter_row if f is not None])
            if available_filter_count == 0:
                continue

            filter_count = 0
            for index, _filter in enumerate(filter_row):
                if _filter is None:
                    continue
                #logging.debug(_filter)
                if _filter.is_filtered(row[index]):
                    logging.debug("FILTER: {0} applies to {1}".format(_filter, row[index]))
                    filter_count += 1

            # row is filtered only if all filters in the row are True
            if filter_count == available_filter_count:
                logging.debug("row filtered")
                return True

        return False

    def apply(self, input_file, output_file=None):
        with open(input_file, 'r') as fp_in:
            reader = csv.reader(fp_in)
            if output_file is None:
                fp_out = sys.stdout
            else:
                fp_out = open(output_file, 'w')

            writer = csv.writer(fp_out, dialect='excel', quoting=csv.QUOTE_MINIMAL)

            try:
                for row in reader:
                    if not self.is_filtered(row):
                        writer.writerow(row)
            finally:
                if fp_out is not sys.stdout:
                    fp_out.close()

if __name__ == '__main__':
    # read the filter file
    import argparse

    parser = argparse.ArgumentParser(description="Filter LR")
    parser.add_argument('input_file', help="The CSV file to read.")
    parser.add_argument('filter_file', help="The CSV filter file.")
    parser.add_argument('-o', '--output-file', dest='output_file', default=None,
        help="Optional output file (defaults to standard output.")
    parser.add_argument('--debug', action='store_true', default=False, dest='debug',
        help="Output verbose debugging logs.")
    args = parser.parse_args()

    logging.basicConfig(level=logging.DEBUG if args.debug else logging.INFO)
    csv_filter = CSVFilter(args.filter_file)
    csv_filter.apply(args.input_file, args.output_file)
    
