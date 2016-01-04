======
Poirot
======

Poirot helps you investigate your repositories. Give him a set of clues (e.g. strings or regular expressions) and he will report back any instances they have occurred in your repository's revision history.

When used as a pre-commit hook, Poirot can warn you if you're about to commit something you might not intend (think passwords, private keys, tokens, and other bits of sensitive or personally identifiable information).

Poirot began as a fork of CFPB's fellow gumshoe, `Clouseau <https://github.com/cfpb/clouseau>`_.

Dependencies
=============
* git
* Python 2.7 or 3.3+
* a Unix-based OS (e.g. Mac or Linux) or a UNIX-y shell on Windows (e.g. `Cygwin <https://www.cygwin.com/>`_, `Babun <http://babun.github.io/>`_, or `Git-Bash <https://git-for-windows.github.io/>`_)

Poirot uses these Python packages:

* `Jinja2 <https://pypi.python.org/pypi/Jinja2/>`_ to format its console output
* `tqdm <https://pypi.python.org/pypi/tqdm/>`_ to display a progress bar
* `regex <https://pypi.python.org/pypi/regex/>`_ to allow for POSIX ERE regular expressions

Running Poirot
=============
To invoke Poirot and see his findings, call him from the command line with :code:`big-grey-cells` (for wordy, colorful output) or :code:`little-grey-cells` (for minimalistic output) and with the following optional arguments:

* **--url**: The repository's URL, e.g. :code:`https://github.com/DCgov/poirot.git` or :code:`git@github.com:DCgov/poirot.git`. When included, you will be given the choice to clone or pull from the remote URL. Default value: none.
* **--dir**: The local path to your repository's base directory or the directory you would like to clone or pull to. Default value: the current working directory.
* **--term**: A single term or regular expression to search for. Default value: none.
* **--patterns**: The path to a .txt file with strings or regular expression patterns, each on its own line. You can give a comma-separated list of pattern files, if you wish to include more than one. Default value: none.
* **--staged**: A flag, which when included, restricts search to staged revisions. This is helpful, along with :code:`--dir`, as part of a pre-commit hook.
* **--revlist**: A range of revisions to inspect. Default value: The last commit (i.e. :code:`HEAD^!`) if :code:`--staged` is not included, otherwise none.
* **--before**: Date restriction on revisions. Default value: none.
* **--after**: Date restriction on revisions. Default value: none.
* **--author**: Authorship restriction on revisions. Default value: none.

Examples
_________
Note: in all of the following examples, :code:`big-grey-cells` could be substituted for :code:`little-grey-cells`.

The most basic command Poirot will accept is:

.. code:: bash

  big-grey-cells

That will search the current git directory's last commit (i.e. :code:`HEAD^!`) for the patterns in the default pattern file. :code:`thisisaterm`.

To specify one or more different patterns files, do this instead:

.. code:: bash

  big-grey-cells --patterns='thisisapatternfile.txt'

Or for a single term (like :code:`thisisaterm`):

.. code:: bash

  big-grey-cells --term="thisisaterm"

Say you want to search for :code:`thisisaterm` in the whole revision history of the current branch. Then do:

.. code:: bash

  big-grey-cells --term="thisisaterm" --revlist="all"

You can further restrict the set of revisions Poirot looks through with the :code:`before`, :code:`after`, and :code:`author` options (which correspond to the `same flags in git <https://git-scm.com/docs/git-log>`_). E.g.:

.. code:: bash

  big-grey-cells --term="thisisaterm" --revlist=40dc6d1...3e4c011 --before="2015-11-28" --after="2015-10-01" --author="me@poirot.com"

Perhaps you don't have the repository available locally or you would like to update it from a remote URL. Just add the :code:`url` to your command and it will allow you to clone or pull:

.. code:: bash

  big-grey-cells --url https://github.com/foo/baz.git --term="thisisaterm"

You can also specify a different directory than the current one with :code:`dir`. The following command will clone/pull to the folder :code:`thisotherfolder`, which sits inside of the current directory. If it does not yet exist, it will be created.

.. code:: bash

  big-grey-cells --url https://github.com/foo/baz.git --term="thisisaterm" --dir="thisotherfolder"

To search changes that have been staged for commit, but not yet committed, use the :code:`staged` flag:

.. code:: bash

  big-grey-cells --term="thisisaterm" --staged

