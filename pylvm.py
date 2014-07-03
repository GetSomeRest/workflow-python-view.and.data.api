#!/usr/bin/env python
# pylvm.py - demonstrate Autodesk 3D viewer authorisation and translation process in Python
#
# Copyright (C) 2014 by Jeremy Tammik, Autodesk Inc.
#
import md5, os.path, requests, shutil, time
from optparse import OptionParser

_version = '1.0'

BASE_URL = 'https://developer.api.autodesk.com'
BUCKET_KEY = 'jeremy_translate_bucket'

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

  if 2 != len(credentials):
    raise "Invalid credentials: expected two entries, consumer key and secret;\nread %s lines, %s after stripping comments." % (len(lines),len(credentials))
    credentials = null

  return credentials


def main():
  "Drive Autodesk 3D viewer authorisation and translation process."

  progname = 'pylmv'
  usage = 'usage: %s [options] model' % progname
  parser = OptionParser( usage, version = progname + ' ' + _version )
  parser.add_option( '-c', '--credentials', dest='credentials_filename', help = 'credentials filename', metavar="FILE", default='/a/src/web/viewer/pylmv/j/credentials.txt' )
  parser.add_option( '-q', '--quiet', action='store_true', dest='quiet', help = 'reduce verbosity' )

  (options, args) = parser.parse_args()

  print options
  print args

  verbose = not options.quiet

  n = len( args )

  if (1 > n) or (1 < n):
    raise SystemExit(parser.print_help() or 1)

  model_filename = args[0]

  if not os.path.exists( model_filename ):
    print _file_missing_prompt % ('model', model_filename)
    raise SystemExit(parser.print_help() or 2)

  # Step 1: Register and create application, retrieve credentials

  if not os.path.exists( options.credentials_filename ):
    print _file_missing_prompt % ('credentials', options.credentials_filename)
    raise SystemExit(parser.print_help() or 3)

  credentials = parse_credentials(options.credentials_filename)

  if not credentials:
    print "Invalid credentials specified in '%s'." % options.credentials_filename
    raise SystemExit(parser.print_help() or 4)

  consumer_key = credentials[0]
  consumer_secret = credentials[1]

  # Step 2: Get your access token

  # curl \
  # --data "client_id=obQDn8P0GanGFQha4ngKKVWcxwyvFAGE&client_secret=eUruM8HRyc7BAQ1e&grant_type=client_credentials" \
  # https://developer.api.autodesk.com/authentication/v1/authenticate \
  # --header "Content-Type: application/x-www-form-urlencoded" -k

  url = 'https://developer.api.autodesk.com/authentication/v1/authenticate'

  data = {
    'client_id' : consumer_key,
    'client_secret' : consumer_secret,
    'grant_type' : 'client_credentials'
  }

  headers = {
    'Content-Type' : 'application/x-www-form-urlencoded'
  }

  r = requests.post(url, data=data, headers=headers)

  print r.status_code
  print r.headers['content-type']
  print type(r.content)
  content = eval(r.content)
  print content
  # -- example results --
  # 200
  # application/json
  # {"token_type":"Bearer","expires_in":1799,"access_token":"ESzsFt7OZ90tSUBGh6JrPoBjpdEp"}

  if 200 != r.status_code:
    print "Authentication returned status code %s." % r.status_code
    raise SystemExit(5)

  access_token = content['access_token']

  print access_token

  # Step 3: Create a bucket

  # curl -k \
  # --header "Content-Type: application/json" --header "Authorization: Bearer fDqpZKYM7ExcC2694eQ1pwe8nwnW" \
  # --data '{\"bucketKey\":\"mybucket\",\"policy\":\"transient\"}' \
  # https://developer.api.autodesk.com/oss/v1/buckets

  url = 'https://developer.api.autodesk.com/oss/v1/buckets'

  data = {
    'bucketKey' : BUCKET_KEY,
    'policy' : 'transient'
  }

  headers = {
    'Content-Type' : 'application/json',
    'Authorization' : 'Bearer ' + access_token
  }

  r = requests.post(url, data=data, headers=headers)

  print r.status_code
  print r.headers['content-type']
  print r.content
  # -- example results --
  # 400
  # None

  # Step 4: Upload a file

if __name__ == '__main__':
  main()
