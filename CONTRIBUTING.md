Contributing
------------

Fork dlce-eva/commonnexus and install the development environment:

```sh
$ pip install virtualenv  # might require sudo/admin privileges
$ git clone https://github.com/<YOUR-GITHUB-HANDLE>/commonnexus.git
$ cd commonnexus
$ git submodule --init update  # We use the NEXUS examples from DendroPy in tests
$ python -m virtualenv .venv
$ source .venv/bin/activate  # Windows: .venv\Scripts\activate.bat
$ pip install -r requirements.txt  # installs the cloned version with dev-tools in development mode
```
