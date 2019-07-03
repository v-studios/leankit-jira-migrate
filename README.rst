========
 README
========

Goal
====

In the app, we can export LeanKit to CSV but it does not include Card Tasks or Comments.
We try to extract them here, and then format a CSV to import into Jira like we do the bare Cards.

Setup
=====

Setup virtualenv with pyenv::

  pyenv local 3.7.2
  pyenv virtualenv leankit-jira
  pyenv activate leankit-jira
  pip install requests

LeanKit Creds
=============

Set the auth creds for LeanKit so we don't store them in the file::

  export LEANKIT_DOMAIN=mycompany             ## the part before .leankit.com
  export LEANKIT_EMAIL=user@example.com
  export LEANKIT_PASSWD='Your Password Here'

Running
=======

Run it:

  ./migrate.py
  
