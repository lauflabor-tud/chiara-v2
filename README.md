chiara-v2
=========

##This is the second version of the data exchange platform 'chiara'. Restructered into the django framework.

Chiara is a recursive acronym for *C*iara *I*s *a* *r*ecursive *a*cronym. This
software is designed to share large data sets between multiple users. It uses
the webdav technology, which is also used for several "web drives". 

In contrast to code repositories (e.g. git), data sets of several tens or
hundreds of gigabytes are not easy to share across the web, especially if you
are only interested in a specific part of the dataset, or if you want to see if
the dataset contains what you are looking for. Further, access restrictions are
often not as fine-grained as you would like for data sets.

This is where *Chiara* comes into play. It allows you to upload your data,
manage rights, update the datasets (while keeping the older versions
available), and share them with people you like. Users can either download
entire collections via webdav, or view and download individual files over the
web interface.


