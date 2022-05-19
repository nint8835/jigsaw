try:
    from nox_poetry import session
except ImportError:
    from nox import session

PACKAGE_NAME = "jigsaw"
PACKAGE_FILES = [PACKAGE_NAME, "noxfile.py"]


@session(python=["3.7", "3.8", "3.9", "3.10"])
def test(session):
    session.install("pytest", ".")
    session.run("pytest")


@session(python=["3.10"])
def format(session):
    session.install("black")
    session.run("black", *PACKAGE_FILES)
