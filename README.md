# Deprecated sample - not maintained anymore (Summer 2016)

# workflow-python

Demonstrate the Autodesk View and Data API authorisation and translation process in a Python command line script.

## Update

This sample is retired, please refer to other workflow samples.

## Description

The workflow-python sample demonstrates the Autodesk View and Data API authorisation and translation process in a Python command line script, [pyadva.py](pyadva.py).

It closely follows the steps described in the documentation:

* https://developer.autodesk.com > Get Started
* http://developer.api.autodesk.com/documentation/v1/index.html
* http://developer.api.autodesk.com/documentation/v1/vs_quick_start.html

In order to make use of this sample, you need to register your consumer key, of course:

* https://developer.autodesk.com > My Apps

This provides the credentials to save in the file [credentials.txt](credentials.txt).

Currently still work in progress.

At the moment, you should probably take a look at the [workflow-curl-view.and.data.api](https://github.com/Developer-Autodesk/workflow-curl-view.and.data.api) sample using Unix shell scripts and cURL.
It is more fundamental than this Python sample and provides more working functionality than what is planned for this sample.

The Python one will be nice to have one of these days, especially because it might be possible to implement it so that it runs on both Unix and Windows. I hope you are already workhng on some flavour of Unix anyway, though.



## Dependencies

Standard Python installation, the Python requests library, maybe switch to the Python pycurl library instead.

* https://www.python.org
* http://docs.python-requests.org
* http://pycurl.sourceforge.net
* https://github.com/pycurl/pycurl


## Setup/Usage Instructions

Request your consumer key/secret key from https://developer.autodesk.com.


## License

workflow-python is licensed under the terms of the [MIT License](http://opensource.org/licenses/MIT). Please see the [LICENSE](LICENSE) file for full details.

## Written by

Jeremy Tammik, Autodesk Inc.
