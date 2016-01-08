======
Poirot
======

Poirot helps you investigate your repositories. Give him a set of clues (e.g. strings or regular expressions) and he will report back any place they appear in your repository's revision history.

When used as a pre-commit hook, Poirot can warn you if you're about to commit something you might not intend (think passwords, private keys, tokens, and other bits of sensitive or personally identifiable information).

Poirot began as a fork of CFPB's fellow gumshoe, `Clouseau <https://github.com/cfpb/clouseau>`_.

Dependencies
=============
* git
* Python 2.7 or 3.3+
* a UNIX-based OS (e.g. Mac or Linux) or a UNIX-y shell on Windows (e.g. `Cygwin <https://www.cygwin.com/>`_, `Babun <http://babun.github.io/>`_, or `Git-Bash <https://git-for-windows.github.io/>`_). It will not work with the default Windows Command Prompt (cmd).

Poirot uses these Python packages:

* `Jinja2 <https://pypi.python.org/pypi/Jinja2/>`_ to format its console output
* `tqdm <https://pypi.python.org/pypi/tqdm/>`_ to display a progress bar
* `regex <https://pypi.python.org/pypi/regex/>`_ to allow for POSIX ERE regular expressions
* `requests <https://pypi.python.org/pypi/requests/>`_ to read remote pattern files

Installation
==============
Poirot is available on PyPi and can be `installed with pip <https://pip.pypa.io/en/stable/installing/>`_ as:

.. code:: bash

  pip install poirot

You may want to install it in a virtual environment, unless you plan on using Poirot in a global commit hook.

In that case, you will have to ensure that you have done a global pip install for any Python versions you are using. E.g., if you want to run it on Python 2.7, 3.3, and 3.5 installed, install Poirot as follows:

.. code:: bash

  pip2.7 install poirot
  pip3.3 install poirot
  pip3.5 install poirot

Running Poirot from the Command Line
========================================
To invoke Poirot and see his findings, call him from the command line with :code:`poirot` and the following optional arguments:

* **--url**: The repository's URL, e.g. :code:`https://github.com/DCgov/poirot.git` or :code:`git@github.com:DCgov/poirot.git`. When included, you will be given the choice to clone or pull from the remote URL. Default value: none.
* **--dir**: The local path to your repository's base directory or the directory you would like to clone or pull to. Default value: the current working directory.
* **--term**: A single term or regular expression to search for. Default value: none.
* **--patterns**: The path to a .txt file with strings or regular expression patterns, each on its own line. These can be the file's URL or its relative or absolute local path. You can give a comma-separated list of pattern files, if you wish to include more than one. Default value: `default.txt <https://github.com/DCgov/poirot/edit/master/poirot/patterns/default.txt>`_.
* **--staged**: A flag, which when included, restricts search to staged revisions. This is helpful, along with :code:`--dir`, as part of a pre-commit hook.
* **--revlist**: A range of revisions to inspect. Default value: The last commit (i.e. :code:`HEAD^!`) if :code:`--staged` is not included, otherwise none.
* **--verbose**: A flag to output verbose, colorful output and pattern-match highlighting. The GIF above gives an example with --verbose included.
* **--before**: Date restriction on revisions. Default value: none.
* **--after**: Date restriction on revisions. Default value: none.
* **--author**: Authorship restriction on revisions. Default value: none.

Examples
_________

The most basic command Poirot will accept is:

.. code:: bash

  poirot

That will search the current git directory's last commit (i.e. :code:`HEAD^!`) for the patterns in `the default pattern file <https://github.com/DCgov/poirot/blob/master/poirot/patterns/default.txt>`_.

To specify one or more different patterns files (each separated by a comma), do this instead:

.. code:: bash

  poirot --patterns='../path/to/thisisapatternfile.txt,/Users/myusername/anotherpatternfile.txt'

The --patterns option also allows files accessible over HTTP, like `this one here <https://raw.githubusercontent.com/DCgov/poirot/master/poirot/patterns/default.txt>`_:

.. code:: bash

  poirot --patterns='https://raw.githubusercontent.com/DCgov/poirot/master/poirot/patterns/default.txt'

To search for a single term (like :code:`password`):

.. code:: bash

  poirot --term="password"

Say you want to search for :code:`password` in the whole revision history of all branches. Then do:

.. code:: bash

  poirot --term="password" --revlist="all"

You can further restrict the set of revisions Poirot looks through with the :code:`before`, :code:`after`, and :code:`author` options (which correspond to the `same flags in git <https://git-scm.com/docs/git-log>`_). E.g.:

.. code:: bash

  poirot --term="password" --revlist=40dc6d1...3e4c011 --before="2015-11-28" --after="2015-10-01" --author="me@poirot.com"

Perhaps you don't have the repository available locally or you would like to update it from a remote URL. Just add the :code:`url` to your command and it will allow you to clone or pull to the current folder.

.. code:: bash

  poirot --url https://github.com/foo/baz.git --term="password"

You can also specify a different directory than the current one with :code:`dir`. The following command will clone/pull to the folder :code:`thisotherfolder`, which sits inside of the current directory. If it does not yet exist, it will be created.

.. code:: bash

  poirot --url https://github.com/foo/baz.git --term="password" --dir="thisotherfolder"

To search changes that have been staged for commit, but not yet committed, use the :code:`staged` flag:

.. code:: bash

  poirot --term="password" --staged
