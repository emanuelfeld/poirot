======
Poirot
======

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
* **--url**: The repository's URL, e.g. :code:`https://github.com/DCgov/poirot.git` or :code:`git@github.com:DCgov/poirot.git`. Default value: none.
* **--dir**: The local path to your repository's base directory. Default value: the current working directory.
* **--term**: A single term or regular expression to search for. Default value: none.
* **--patterns**: The path to a .txt file with strings or regular expression patterns, each on its own line. You can give a comma-separated list of pattern files, if you wish to include more than one. Default value: `default.txt`.
* **--staged**: A flag, which when included, restricts search to staged revisions. This is helpful as part of a pre-commit hook.
* **--revlist**: A range of revisions to inspect. Default value: The last commit (i.e. HEAD^!) if --staged is not included, otherwise none.
* **--before**: Date restriction on revisions. Default value: none.
* **--after**: Date restriction on revisions. Default value: none.
* **--author**: Authorship restriction on revisions. Default value: none.

.. image:: https://cloud.githubusercontent.com/assets/4269640/12029422/b18daea6-adb8-11e5-94d8-e2e733332a4e.png

Examples
=============
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

