#!/usr/bin/python3
# -*- coding: UTF-8 -*-

import os
import re
import sys
import string
import signal
import struct
import getopt

def usage():
    print >> sys.stderr, \
          """
    Usage:
          acrntrace_format.py [options] [formats] [trace_data]

          [options]
          -h: print this message

          Parses trace_data in binary format generated by acrntrace and
          reformats it according to the rules in the [formats] file.
          The rules in formats should have the format ({ and } show grouping
          and are not part of the syntax):

          {event_id}{whitespace}{text format string}

          The textual format string may include format specifiers, such as
          %(cpu)d, %(tsc)d, %(event)d, %(1)d, %(2)d, ....
          The 'd' format specifier outputs in decimal, alternatively 'x' will
          output in hexadecimal and 'o' will output in octal.

          These respectively correspond to the CPU number (cpu), timestamp
          counter (tsc), event ID (event) and the data logged in the trace file.
          There can be only one such rule for each type of event.
          """

def read_format(format_file):
    formats = {}

    fd = open(format_file)

    reg = re.compile('(\S+)\s+(\S.*)')

    while True:
        line = fd.readline()
        if not line:
            break

        if line[0] == '#' or line[0] == '\n':
            continue

        m = reg.match(line)

        if not m: print >> sys.stderr, "Wrong format file"; sys.exit(1)

        formats[str(eval(m.group(1)))] = m.group(2)

    return formats

exit = 0

# structure of trace data (as output by acrntrace)
# TSC(Q) HDR(Q) D1 D2 ...
# HDR consists of event:48:, n_data:8:, cpu:8:
# event means Event ID
# n_data means number of data in trace entry (like D1, D2, ...)
# cpu means cpu id this trace entry belong to
TSCREC = "Q"
HDRREC = "Q"
D2REC  = "QQ"
D4REC = "IIII"
D8REC = "BBBBBBBBBBBBBBBB"
D16REC = "bbbbbbbbbbbbbbbb"

def main_loop(formats, fd):
    global exit
    i = 0


    while not exit:
        try:
            i = i + 1

            line = fd.read(struct.calcsize(TSCREC))
            if not line:
                break
            tsc = struct.unpack(TSCREC, line)[0]

            line = fd.read(struct.calcsize(HDRREC))
            if not line:
                break
            event = struct.unpack(HDRREC, line)[0]
            n_data = event >> 48 & 0xff
            cpu = event >> 56
            event = event & 0xffffffffffff

            d1 = 0
            d2 = 0
            d3 = 0
            d4 = 0
            d5 = 0
            d6 = 0
            d7 = 0
            d8 = 0
            d9 = 0
            d10 = 0
            d11 = 0
            d12 = 0
            d13 = 0
            d14 = 0
            d15 = 0
            d16 = 0

            if n_data == 2:
                line = fd.read(struct.calcsize(D2REC))
                if not line:
                    break
                (d1, d2) = struct.unpack(D2REC, line)

            if n_data == 4:
                line = fd.read(struct.calcsize(D4REC))
                if not line:
                    break
                (d1, d2, d3, d4) = struct.unpack(D4REC, line)

            if n_data == 8:
                line = fd.read(struct.calcsize(D8REC))
                if not line:
                    break
                # TRACE_6C using the first 6 data of fields_8. Actaully we have
                # 16 data in every trace entry.
                (d1, d2, d3, d4, d5, d6, d7, d8,
                 d9, d10, d11, d12, d13, d14, d15, d16) = struct.unpack(D8REC, line)

            if n_data == 16:
                line = fd.read(struct.calcsize(D16REC))
                if not line:
                    break

                (d1, d2, d3, d4, d5, d6, d7, d8,
                 d9, d10, d11, d12, d13, d14, d15, d16) = struct.unpack(D16REC, line)

            args = {'cpu'   : cpu,
                    'tsc'   : tsc,
                    'event' : event,
                    '1'     : d1,
                    '2'     : d2,
                    '3'     : d3,
                    '4'     : d4,
                    '5'     : d5,
                    '6'     : d6,
                    '7'     : d7,
                    '8'     : d8,
                    '9'     : d9,
                    '10'    : d10,
                    '11'    : d11,
                    '12'    : d12,
                    '13'    : d13,
                    '14'    : d14,
                    '15'    : d15,
                    '16'    : d16      }

            try:
                if str(event) in formats.keys():
                    print (formats[str(event)] % args)
            except TypeError:
                if str(event) in formats.key():
                    print (formats[str(event)])
                    print (args)

        except struct.error:
            sys.exit()

def main(argv):
    try:
        opts, arg = getopt.getopt(sys.argv[1:], "h")

        for opt in opts:
            if opt[0] == '-h':
                usage()
                sys.exit()

    except getopt.GetoptError:
        usage()
        sys.exit(1)

    try:
        formats = read_format(arg[0])
        fd = open(arg[1], 'rb')
    except IOError:
        sys.exit(1)

    main_loop(formats, fd)

if __name__ == "__main__":
    main(sys.argv[1:])