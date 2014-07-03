#!/usr/bin/env python
# pylvm.py - demonstrate Autodesk 3D viewer authorisation and translation process in Python
#
# Copyright (C) 2014 by Jeremy Tammik, Autodesk Inc.
#
import os.path, shutil

from optparse import OptionParser

_version = '2.0'

_file_missing_prompt = "Error: specified %s file '%s' does not exist.\n"


def parse_credentials(filename):
  "Parse credentials from given text file."
  f = open( filename )
  lines = f.readlines()
  f.close()
  credentials = []
  for line in lines:
    i = line.find('#')
    if -1 < i: line = line[0:i]
    i = line.find(':')
    if -1 < i: line = line[i+1:]
    line = line.strip()
    if 0 < len(line):
      print line
      line = line.strip("\"'")
      credentials.append(line)

  if 4 != len(credentials):
    raise "Invalid credentials: expected 4, read %s lines, %s after stripping comments." % (len(lines),len(credentials))
    credentials = null

  return credentials


def main():
  "Drive Autodesk 3D viewer authorisation and translation process."

  progname = 'pylmv'
  usage = 'usage: %s [options] model' % progname
  parser = OptionParser( usage, version = progname + ' ' + _version )
  parser.add_option( '-c', '--credentials', dest='credentials_filename', help = 'credentials filename', metavar="FILE", default='/a/src/web/viewer/pylmv/credentials.txt' )
  parser.add_option( '-q', '--quiet', action='store_true', dest='quiet', help = 'reduce verbosity' )

  (options, args) = parser.parse_args()

  print options
  print args

  verbose = not options.quiet

  n = len( args )

  if (1 > n) or (1 < n):
    raise SystemExit(parser.print_help() or 1)

  if not os.path.exists( options.credentials_filename ):
    print _file_missing_prompt % ('credentials', options.credentials_filename)
    raise SystemExit(parser.print_help() or 2)

  credentials = parse_credentials(options.credentials_filename)

  if not credentials:
    print "Invalid credentials specified in '%s'." % options.credentials_filename
    raise SystemExit(parser.print_help() or 3)

  model_filename = args[0]

  if not os.path.exists( model_filename ):
    print _file_missing_prompt % ('model', model_filename)
    raise SystemExit(parser.print_help() or 4)


if __name__ == '__main__':
  main()
