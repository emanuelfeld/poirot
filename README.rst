======
Poirot
======

Poirot helps you investigate your repositories. Give him a set of clues (e.g. strings or regular expressions) and he will report back any instances they have occurred in your repository's revision history.

When used as a pre-commit hook, Poirot can warn you if you're about to commit something you might not intend (think passwords, private keys, tokens, and other bits of sensitive or personally identifiable information).

Poirot began as a fork of CFPB's fellow gumshoe, `Clouseau <https://github.com/cfpb/clouseau>`_.

1. Dependencies
2. Installing Poirot
3. Invoking Poirot
4. Examples
5. Using Poirot as a pre-commit hook

Dependencies
=============
* git
* Python 2.7 or 3.3+

Installation
=============
.. code:: bash

  pip install poirot

Options
=============
To invoke Poirot and see his findings, call him from the command line with :code:`big-grey-cells` (wordy, colorful output) or :code:`little-grey-cells` (minimalistic output) and with the following optional arguments:

* **--url**: The repository's URL, e.g. :code:`https://github.com/DCgov/poirot.git` or :code:`git@github.com:DCgov/poirot.git`. When included, you will be given the choice to clone or pull from the remote URL. Default value: none.
* **--dir**: The local path to your repository's base directory or the directory you would like to clone or pull to. Default value: the current working directory.
* **--term**: A single term or regular expression to search for. Default value: none.
* **--patterns**: The path to a .txt file with strings or regular expression patterns, each on its own line. You can give a comma-separated list of pattern files, if you wish to include more than one. Default value: none.
* **--staged**: A flag, which when included, restricts search to staged revisions. This is helpful, along with :code:`--dir`, as part of a pre-commit hook.
* **--revlist**: A range of revisions to inspect. Default value: The last commit (i.e. :code:`HEAD^!`) if :code:`--staged` is not included, otherwise none.
* **--before**: Date restriction on revisions. Default value: none.
* **--after**: Date restriction on revisions. Default value: none.
* **--author**: Authorship restriction on revisions. Default value: none.

.. image:: https://cloud.githubusercontent.com/assets/4269640/12029422/b18daea6-adb8-11e5-94d8-e2e733332a4e.png

Examples
_________
Clone or pull the foo/baz repository to the current working directory. Search the last commit made for the patterns in :code:`default.txt`.

.. code:: bash

  $ big-grey-cells --url https://github.com/foo/baz.git --patterns='patterns/default.txt'

...clone or pull instead to the `here` directory.

.. code:: bash

  $ big-grey-cells --url https://github.com/foo/baz.git --patterns='patterns/default.txt' --dir here

...search all commits made to the current branch.

.. code:: bash

  $ big-grey-cells --url https://github.com/foo/baz.git --patterns='patterns/default.txt' --revlist="all"

...search all commits made to the current branch.

.. code:: bash

  $ big-grey-cells --url https://github.com/foo/baz.git --patterns='patterns/default.txt' --revlist="all"


...search all commits made to the current branch with author Poirot.

.. code:: bash

  $ big-grey-cells --url https://github.com/foo/baz.git --patterns='patterns/default.txt' --revlist="all" --author="Poirot"

...search all staged revisions in the current git repository.

.. code:: bash

  $ big-grey-cells --staged --patterns='patterns/default.txt'


...search staged revisions for the term `password`.

.. code:: bash

  $ big-grey-cells --staged --term="password"

