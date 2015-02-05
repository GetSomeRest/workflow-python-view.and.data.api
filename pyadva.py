#!/usr/bin/env python
# pyadva.py - demonstrate Autodesk View and Data API authorisation and translation process in Python
#
# Copyright (C) 2014 by Jeremy Tammik, Autodesk Inc.
#
import base64, json, md5, os.path, requests, shutil, time
from optparse import OptionParser

_version = '1.0'

BASE_URL = 'https://developer.api.autodesk.com/'
BUCKET_KEY = 'jtbucket'

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
  usage = 'usage: %s [options]' % progname
  parser = OptionParser( usage, version = progname + ' ' + _version )
  parser.add_option( '-b', '--bucketskip', action='store_true', dest='bucketskip', help = 'skip bucket creation' )
  parser.add_option( '-c', '--credentials', dest='credentials_filename', help = 'credentials filename', metavar="FILE", default='/a/src/web/viewer/pylmv/j/credentials.txt' )
  parser.add_option( '-m', '--model', dest='model_filename', help = 'model filename', metavar="FILE", default='/a/rvt/two_columns.rvt' )
  parser.add_option( '-q', '--quiet', dest='quiet', action='store_true', default=True, help = 'reduce verbosity' )
  parser.add_option( '-u', '--urn', dest='urn', help = 'specify urn of already uploaded model file', default='dXJuOmFkc2sub2JqZWN0czpvcy5vYmplY3Q6anRidWNrZXQvdHdvX2NvbHVtbnNfcnZ0' )

  (options, args) = parser.parse_args()

  print options
  print args

  verbose = not options.quiet

  if 1 < len( args ):
    raise SystemExit(parser.print_help() or 1)

  model_filepath = options.model_filename

  if not model_filepath:
    print 'Please specify a model file to process.'
    raise SystemExit(parser.print_help() or 2)

  if not os.path.exists( model_filepath ):
    print _file_missing_prompt % ('model', model_filepath)
    raise SystemExit(parser.print_help() or 3)

  # Step 1: Register and create application, retrieve credentials

  if not os.path.exists( options.credentials_filename ):
    print _file_missing_prompt % ('credentials', options.credentials_filename)
    raise SystemExit(parser.print_help() or 4)

  credentials = parse_credentials(options.credentials_filename)

  if not credentials:
    print "Invalid credentials specified in '%s'." % options.credentials_filename
    raise SystemExit(parser.print_help() or 5)

  consumer_key = credentials[0]
  consumer_secret = credentials[1]

  # Step 2: Get your access token

  # curl -k \
  # --data "client_id=obQDn8P0GanGFQha4ngKKVWcxwyvFAGE&client_secret=eUruM8HRyc7BAQ1e&grant_type=client_credentials" \
  # https://developer.api.autodesk.com/authentication/v1/authenticate \
  # --header "Content-Type: application/x-www-form-urlencoded"

  url = BASE_URL + 'authentication/v1/authenticate'

  data = {
    'client_id' : consumer_key,
    'client_secret' : consumer_secret,
    'grant_type' : 'client_credentials'
  }

  headers = {
    'Content-Type' : 'application/x-www-form-urlencoded'
  }

  r = requests.post(url, data=data, headers=headers)

  content = eval(r.content)

  if verbose or 200 != r.status_code:
    print r.status_code
    print r.headers['content-type']
    print type(r.content)
    print content
    # -- example results --
    # 200
    # application/json
    # {"token_type":"Bearer","expires_in":1799,"access_token":"ESzsFt7OZ90tSUBGh6JrPoBjpdEp"}

  if 200 != r.status_code:
    print "Authentication returned status code %s." % r.status_code
    raise SystemExit(6)

  access_token = content['access_token']

  print 'Step 2 returns access token', access_token

  # Step 3: Create a bucket

  if not options.bucketskip:

    # Check for prior existence:

    # curl -k -X GET \
    # -H "Authorization: Bearer lEaixuJ5wXby7Trk6Tb77g6Mi8IL" \
    # https://developer.api.autodesk.com/oss/v1/buckets/mybucket/details

    url = BASE_URL + 'oss/v1/buckets/' + BUCKET_KEY + '/details'

    headers = {
      'Authorization' : 'Bearer ' + access_token
    }

    print 'Step 3: Check whether bucket exists'
    print 'curl -k -X GET -H "Authorization: Bearer %s" %s' % (access_token, url)

    print url
    print headers

    r = requests.get(url, headers=headers)

    if verbose:
      print r.status_code
      print r.headers['content-type']
      print r.content
      # -- example results --
      # 200
      # application/json; charset=utf-8
      # {
      #  "key":"jtbucket",
      #  "owner":"NjEasFuPL6WAsNctq3VCgXDnTUBGa858",
      #  "createDate":1404399358062,
      #  "permissions":[{"serviceId":"NjEasFuPL6WAsNctq3VCgXDnTUBGa858","access":"full"}],
      #  "policyKey":"transient"
      # }

    if 200 != r.status_code:

      # Create a new bucket:

      # curl -k \
      # --header "Content-Type: application/json" --header "Authorization: Bearer fDqpZKYM7ExcC2694eQ1pwe8nwnW" \
      # --data '{\"bucketKey\":\"mybucket\",\"policy\":\"transient\"}' \
      # https://developer.api.autodesk.com/oss/v1/buckets

      url = BASE_URL + 'oss/v1/buckets'

      data = {
        'bucketKey' : BUCKET_KEY,
        'policy' : 'transient'
      }

      headers = {
        'Content-Type' : 'application/json',
        'Authorization' : 'Bearer ' + access_token
      }

      print 'Step 3: Create a bucket'
      print 'curl -k -H "Authorization: Bearer %s" -H "Content-Type:application/json" --data "{\\"bucketKey\\":\\"%s\\",\\"policy\\":\\"transient\\"}" %s' % (access_token, BUCKET_KEY, url)

      print url
      print json.dumps(data)
      print headers

      r = requests.post(url, data=json.dumps(data), headers=headers)

      if verbose or 200 != r.status_code:
        print r.status_code
        print r.headers['content-type']
        print r.content
        # -- example results --
        # The Python request call failed, but the curl
        # command that it generated worked and produced
        # the following result:
        #
        # {
        #  "key":"jtbucket",
        #  "owner":"NjEasFuPL6WAsNctq3VCgXDnTUBGa858",
        #  "createDate":1404399358062,
        #  "permissions":[{"serviceId":"NjEasFuPL6WAsNctq3VCgXDnTUBGa858","access":"full"}],
        #  "policyKey":"transient"
        # }

      if 200 != r.status_code:
        print "Bucket creation returned status code %s." % r.status_code
        raise SystemExit(7)

  # Step 4: Upload a file

  if options.urn:
    urn = options.urn
  else:
    # curl -k \
    # --header "Authorization: Bearer K16B98iaYNElzVheldlUAUqOoMRC" --header "Content-Length: 308331" \
    # -H "Content-Type:application/octet-stream" --header "Expect:" \
    # --upload-file "skyscpr1.3ds"
    # -X PUT https://developer.api.autodesk.com/oss/v1/buckets/mybucket/objects/skyscpr1.3ds

    filesize = os.path.getsize( model_filepath )
    model_filename = os.path.basename( model_filepath ).replace('.','_')

    url = 'https://developer.api.autodesk.com/oss/v1/buckets/' + BUCKET_KEY + '/objects/' + model_filename

    headers = {
      'Content-Type' : 'application/octet-stream',
      'Content-Length' : str(filesize),
      'Authorization' : 'Bearer ' + access_token,
      'Expect' : ''
    }

    print "Step 4: starting upload of model file '%s', %s bytes..." % (model_filename,filesize)

    print 'curl -k -H "Authorization: Bearer %s" -H "Content-Length: %s" -H "Content-Type:application/octet-stream" -H "Expect:" -T "%s" -X PUT %s' % (access_token, filesize, model_filepath, url)

    with open(model_filepath, 'rb') as f:
      #files = { model_filename : f }
      #r = requests.put(url, headers=headers, files=files)
      #uploading does not aceept multi-parts objects. 
      #see http://docs.python-requests.org/en/latest/api/
      # files: Dictionary of 'name': file-like-objects (or {'name': ('filename', fileobj)}) for multipart encoding upload.
      # data:  Dictionary, bytes, or file-like object to send in the body of the Request.
      r = requests.put(url, headers=headers, data=f) 

    #with open(model_filepath, 'rb') as f:
    #  request = requests.put(url, headers=headers, data=f)

    if verbose:
      print r.status_code
      print r.headers['content-type']
      print r.content
      # -- example results --
      # The Python request call failed, but the curl
      # command that it generated worked and produced
      # the following result:
      #
      # {
      #   "bucket-key" : "jtbucket",
      #   "objects" : [ {
      #     "location" : "https://developer.api.autodesk.com/oss/v1/buckets/jtbucket/objects/two_columns_rvt",
      #     "size" : 4165632,
      #     "key" : "two_columns_rvt",
      #     "id" : "urn:adsk.objects:os.object:jtbucket/two_columns_rvt",
      #     "sha-1" : "cb15374248562743c5a99e0bdb0535f508a19848",
      #     "content-type" : "application/octet-stream"
      #   } ]
      # }

    urn = r.content['objects']['id']
    print 'id:', urn

    # import base64
    # base64.b64encode("urn:adsk.objects:os.object:jtbucket/two_columns_rvt")
    # 'dXJuOmFkc2sub2JqZWN0czpvcy5vYmplY3Q6anRidWNrZXQvdHdvX2NvbHVtbnNfcnZ0'

    urn = base64.b64encode(urn)
    print 'urn:', urn

  # Step 6: Register Data with the Viewing Services

  # curl -k \
  # -H "Content-Type: application/json" \
  # -H "Authorization:Bearer 1f4bEhzvxJ9CMvMPSHD4gXO4SYEr" \
  # -i -d "{\"urn\":\"dXJuOmFkc2sub2JqZWN0czpvcy5vYmplY3Q6bXlidWNrZXQvc2t5c2NwcjEuM2Rz\"}" \
  # https://developer.api.autodesk.com/viewingservice/v1/register

  url = BASE_URL + 'viewingservice/v1/register'

  data = {
    'urn' : urn,
  }

  headers = {
    'Content-Type' : 'application/json',
    'Authorization' : 'Bearer ' + access_token
  }

  print 'Step 6: Register data'
  print 'curl -k -H "Authorization: Bearer %s" -H "Content-Type:application/json" -i -d "{\\"urn\\":\\"%s\\"}" %s' % (access_token, urn, url)

  print url
  print json.dumps(data)
  print headers

  r = requests.post(url, data=json.dumps(data), headers=headers)

  if verbose or 200 != r.status_code:
    print r.status_code
    print r.headers['content-type']
    print r.content
    # -- example results --
    # The Python request call failed, but the curl
    # command that it generated worked and produced
    # the following result:
    #

  if 200 != r.status_code:
    print "Register data returned status code %s." % r.status_code
    raise SystemExit(9)


if __name__ == '__main__':
  main()
