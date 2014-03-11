=====
s3pip
=====

A pip wrapper that uses Amazon's S3 for package data.


Usage
^^^^^

Installation::

    $ pip install s3pip

Set an environment variable containing the name of your bucket.

.. code-block:: bash

    $ export S3_PIP_BUCKET_NAME=my_own_pypi_bucket

Now you can use s3pip just like pip

.. code-block:: bash

    $ s3pip install requests
      Downloading/unpacking requests
        Found item in S3 /simple/requests/index.html
        Found item in S3 /packages/2.7/r/requests/requests-2.2.1-py2.py3-none-any.whl
        Downloading requests-2.2.1-py2.py3-none-any.whl (625kB): 625kB downloaded
      Installing collected packages: requests
      Successfully installed requests
      Cleaning up...
