# vFiber
To install VirtualFiber clone this repository and run

`pip install requirements.txt`

Fiber exchange is implemented in `src/adexchange/adexchange.py`

To start a vFiber cluster define the servers on which the cluster's adexchange
will run by changing the `ADEX` object in `/src/settings.py`

Similarly define locations for the Seller object by changing `SELLER` in the
same file.

Make sure that MySQL server is running on `127.0.0.1`

Log into MySQL and create a database called `VirtualFiber`
within that database run the commands in `VFiber/src/adexchange/dbSchema.txt`

Now you can start a vFiber cluster run
`python VFiber/src/startVFCluster.py`

in a new terminal window run
`python VFiber/src/startClient.py`
