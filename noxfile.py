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


@session(python="3.10")
def format(session):
    session.install("black", "isort")
    session.run("black", *PACKAGE_FILES)
    session.run("isort", *PACKAGE_FILES)


@session(python="3.10")
def typecheck(session):
    session.install("mypy", ".")
    session.run("mypy", PACKAGE_NAME)


@session(python="3.10")
def lint(session) -> None:
    session.install("black", "isort")
    session.run("black", "--check", *PACKAGE_FILES)
    session.run("isort", "--check", *PACKAGE_FILES)
