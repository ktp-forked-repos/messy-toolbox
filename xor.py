#!/usr/bin/env python
# vim: ts=4:sw=4:et


import argparse
import sys

parser = argparse.ArgumentParser()
parser.add_argument('-v', action='store', required=True, dest='value',
    help='Value to XOR each byte against.  Start with 0x to specify by hex.')
parser.add_argument('--input', '-i', action='store', required=False, dest='input_file')
parser.add_argument('--output', '-o', action='store', required=False, default=None, dest='output_file')
args = parser.parse_args()

fp_in = sys.stdin
fp_out = sys.stdout

if args.input_file is not None:
    fp_in = open(args.input_file, 'rb')

if args.output_file is not None:
    fp_out = open(args.output_file, 'wb')

if args.value.startswith('0x'):
    value = int(args.value[2:], 16)
else:
    value = int(args.value)

for b in fp_in.read():
    fp_out.write(chr(ord(b) ^ value))
