============
deployer-fsm
============

Create deployment scripts from example and in place practice

We all forget things in deploy scripts. what if the deployment was mutable and error recovering for when one machine is not the same as another?

deployer-fsm aims to create robust deployment scripts and automation through handling error codes in a Finite State Machine.

The following installs and runs deployer-fsm. after exiting it will create a `script-out.sh` file. The hope is this is your deployment script.

.. code-block:: console
        
    $ pip3 install deployer-fsm
    $ deployer-fsm
    $ bash ./script-out.sh


for help, see:

.. code-block:: console

    $ deployer-fsm -h

.. image:: https://img.shields.io/pypi/v/deployer-fsm.svg
        :target: https://pypi.python.org/pypi/deployer-fsm

.. image:: https://img.shields.io/travis/lsmith-zenoscave/deployer.svg
        :target: https://travis-ci.com/lsmith-zenoscave/deployer

.. image:: https://readthedocs.org/projects/deployer-fsm/badge/?version=latest
        :target: https://deployer-fsm.readthedocs.io/en/latest/?badge=latest
        :alt: Documentation Status


.. image:: https://pyup.io/repos/github/lsmith-zenoscave/deployer/shield.svg
     :target: https://pyup.io/repos/github/lsmith-zenoscave/deployer/
     :alt: Updates



Deployment management and editing with fabric


* Free software: BSD license
* Documentation: https://deployer-fsm.readthedocs.io.


Features
--------

* TODO

Credits
-------

This package was created with Cookiecutter_ and the `audreyr/cookiecutter-pypackage`_ project template.

.. _Cookiecutter: https://github.com/audreyr/cookiecutter
.. _`audreyr/cookiecutter-pypackage`: https://github.com/audreyr/cookiecutter-pypackage
