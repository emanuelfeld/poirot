======
Poirot
======

.. image:: https://travis-ci.org/emanuelfeld/poirot.svg?branch=master
    :target: https://travis-ci.org/emanuelfeld/poirot

.. image:: https://coveralls.io/repos/github/emanuelfeld/poirot/badge.svg?branch=master
    :target: https://coveralls.io/github/emanuelfeld/poirot?branch=master

.. image:: https://img.shields.io/pypi/v/poirot.svg
    :target: https://pypi.python.org/pypi/poirot

Poirot helps you investigate your repositories. Give him a set of clues (e.g. strings or regular expressions) and he will report back any place they appear in your repository's revision history.

When used as a pre-commit hook, Poirot can warn you if you're about to commit something you might not intend (think passwords, private keys, tokens, and other bits of sensitive or personally identifiable information).

Poirot began as a fork of CFPB's fellow gumshoe, `Clouseau <https://github.com/cfpb/clouseau>`_.

1. `Dependencies`_
2. `Installation`_
3. `Running Poirot from the Command Line`_
4. `Running Poirot as a Pre-Commit Hook`_
5. `Setting up Poirot as a DC Government Employee`_
6. `Getting Involved`_

.. image:: https://raw.githubusercontent.com/DCgov/poirot/master/assets/example1.gif

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
=============
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
* **--output**: File to output results as JSON. Default value: none.

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

Running Poirot as a Pre-Commit Hook
=====================================
By setting up a pre-commit hook to run Poirot, you can have Poirot automatically run whenever you try to commit changes from the command line. 

Poirot will then check these staged changes for whatever patterns you want. If there are any matches, you will have the option to cancel or go ahead with the commit. Then you can fix anything amiss and re-commit.

For a Single Repository
_______________________
To set up a pre-commit hook for a particular repository, first install Poirot and then run the following from the repository's root directory:

.. code:: bash

    curl https://raw.githubusercontent.com/DCgov/poirot/master/pre-commit-poirot > .git/hooks/pre-commit-poirot
    chmod +x .git/hooks/pre-commit-poirot
    echo '.git/hooks/pre-commit-poirot -f \"\" -p \"\"' >> .git/hooks/pre-commit
    chmod +x .git/hooks/pre-commit

The :code:`-f` and :code:`-p` in the second to last line are flags for patterns folder and a comma-separated list of pattern files, respectively. These let you use patterns other than the default, if you would like, by providing their absolute path or URL.

For example, you could change the flag values to :code:`-f "/Users/myusername/Documents/poirot-patterns" -p "https://github.com/DCgov/poirot-patterns/blob/master/financial.txt, https://github.com/DCgov/poirot-patterns/blob/master/id.txt"`.

You can either edit that line before you run it, or edit it after with:

.. code:: bash

    vim .git/hooks/pre-commit

My advice is to fork the `poirot-patterns repository <https://github.com/dcgov/poirot-patterns/>`_ and download it to your computer. Then add the absolute path to that folder as the :code:`-f` flag.

If you go ahead with setting up a patterns folder, then you can easily add, delete, or modify the pattern files without having to keep re-editing the commit hook.

As an aside, if you ever want to commit without running the hook, just use:

.. code:: bash

    git commit --no-verify

For All Repositories
_____________________
To set a Poirot pre-commit hook for all your new repositories, you can add it to your default template with the `init.templatedir <https://git-scm.com/docs/git-init>`_ configuration variable. Then, whenever you :code:`git init` a repository, Poirot will be set to run. The following code will do that for you:

.. code:: bash

    mkdir -p ~/.git_template/hooks
    git config --global init.templatedir '~/.git_template'
    curl https://raw.githubusercontent.com/DCgov/poirot/master/pre-commit-poirot > ~/.git_template/hooks/pre-commit-poirot
    chmod +x ~/.git_template/hooks/pre-commit-poirot
    echo '.git/hooks/pre-commit-poirot -f \"\" -p \"\"' >> ~/.git_template/hooks/pre-commit
    chmod +x ~/.git_template/hooks/pre-commit

As in the `Single Repositories <https://github.com/DCgov/poirot#for-a-single-repository>`_ case, the :code:`-f` and :code:`-p` flags in the second to last line will let you use pattern files other than the default. If you don't care about that, you can run it as is.

For existing repositories, you can re-run :code:`git init` in the repo. Running :code:`git init` will not overwrite things that are already there. It will only add new template files (e.g. this hook).

As in the above section on `Single Repositories <https://github.com/DCgov/poirot#for-a-single-repository>`_, I recommend that you start out by setting up a patterns folder on your computer. You can fork and download the `poirot-patterns repository <https://github.com/dcgov/poirot-patterns/>`_ to get started.

Using a patterns folder avoids most instances that would make you want to make subsequent edits to your global pre-commit hook.

If you do decide to make a change after you have already applied the global pre-commit hook to a repository, you will need to delete the repository's existing pre-commit hook and re-run :code:`git init`. To do that, run the following from the root of the repository:

.. code:: bash

    rm ~/.git/hooks/pre-commit
    git init

Setting up Poirot as a DC Government Employee
================================================
Poirot is part of the standard DC Government open source development toolkit. Once you have Python and pip set up on your computer, run the following from the command line:

.. code:: bash

    pip install poirot civicjson groupthink

This installs Poirot, in addition to the `Civic.JSON-CLI <https://github.com/dcgov/civic.json-cli>`_ (a Python package that helps you document your code projects with a civic.json file), and `Groupthink <https://github.com/dcgov/groupthink>`_ (another Python package that will allow you to manage project set-up scripts).

Next, install the dcgov-cli scripts by running:

.. code:: bash

    groupthink install dcgov

When you want to start an open source DC Government project, go to your new project's directory and run:

.. code:: bash

    dcgov init

This will download the standard DC Government open source `license and contributing files <https://github.com/dcgov/license>`_, set up Poirot as a pre-commit hook to run whenever you attempt to commit changes to the project from the command line, and give you the option to install a civic.json file.

Read more about the `civic.json standard <http://open.dc.gov/civic.json>`_, the `dcgov-cli scripts <https://github.com/dcgov/dcgov-cli>`_, and `groupthink <https://github.com/dcgov/groupthink>`_.

Getting Involved
=================
Hey! Glad you're interested in getting involved, whether by flagging bugs, submitting feature requests, or otherwise improving Poirot.

To get you oriented, there are three project repositories to be aware of:

1. This one here, which contains the Poirot Python package.
2. `DCgov/poirot-patterns <https://github.com/DCgov/poirot-patterns>`_, where we're compiling boilerplate pattern files.
3. `DCgov/poirot-test-repo <https://github.com/DCgov/poirot-test-repo>`_, which we're running the tests on. If you check out the `test directory <https://github.com/DCgov/poirot/tree/master/tests>`_ in this repository, you will find that DCgov/poirot-test-repo has been added as a submodule.

You should also read over the `LICENSE.md <https://github.com/DCgov/poirot/blob/master/LICENSE.md>`_ and `CONTRIBUTING.md <https://github.com/DCgov/poirot/blob/master/CONTRIBUTING.md>`_, which govern the terms under which this project's code and your hypothetical contributions are being made available.

If you're going to modify a Poirot fork and submit pull requests, be sure to add tests to validate your changes.

Running Unit Tests
___________________
Once you've forked or cloned Poirot, you can run the unit tests with:

.. code:: bash

    python setup.py test

To test multiple Python versions at once (current we aim to support 2.7, 3.3, 3.4, and 3.5), you will need each installed in your environment (I recommend using `pyenv <https://github.com/yyuu/pyenv>`_).

The `tox <https://pypi.python.org/pypi/tox>`_ package will let you run the tests in one go. Install tox with pip or easy_install, then simply run it with:

.. code:: bash

    tox

It uses the `tox.ini file <https://github.com/DCgov/poirot/blob/master/tox.ini>`_ to know what to do.
