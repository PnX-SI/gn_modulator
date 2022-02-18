from werkzeug.datastructures import Headers
import pytest
import json
from flask import testing

from geonature import create_app
from geonature.utils.env import db as db


class JSONClient(testing.FlaskClient):
    def open(self, *args, **kwargs):
        headers = kwargs.pop('headers', Headers())
        if 'Accept' not in headers:
            headers.extend(Headers({
                'Accept': 'application/json, text/plain, */*',
            }))
        if 'Content-Type' not in headers and 'data' in kwargs:
            kwargs['data'] = json.dumps(kwargs['data'])
            headers.extend(Headers({
                'Content-Type': 'application/json',
            }))
        kwargs['headers'] = headers
        return super().open(*args, **kwargs)


@pytest.fixture(scope='session')
def app():
    app = create_app()
    app.testing = True
    app.test_client_class = JSONClient
    app.config['SERVER_NAME'] = 'test.geonature.fr'  # required by url_for

    with app.app_context():
        """
        Note: This may seem redundant with 'temporary_transaction' fixture.
        It is not as 'temporary_transaction' has a function scope.
        This nested transaction is useful to rollback class-scoped fixtures.
        Note: As we does not have a complex savepoint restart mechanism here,
        fixtures must commit their database changes in a nested transaction
        (i.e. in a with db.session.begin_nested() block).
        """
        transaction = db.session.begin_nested()  # execute tests in a savepoint
        yield app
        transaction.rollback()  # rollback all database changes

@pytest.fixture(scope='function')
def temporary_transaction(app):
    """
    We start two nested transaction (SAVEPOINT):
        - The outer one will be used to rollback all changes made by the current test function.
        - The inner one will be used to catch all commit() / rollback() made in tested code.
          After starting the inner transaction, we install a listener on transaction end events,
          and each time the inner transaction is closed, we restart a new transaction to catch
          potential new commit() / rollback().
    Note: When we rollback the inner transaction at the end of the test, we actually rollback
    only the last inner transaction but previous inner transaction may have been committed by the
    tested code! This is why we need an outer transaction to rollback all changes made by the test.
    """
    outer_transaction = db.session.begin_nested()
    inner_transaction = db.session.begin_nested()

    def restart_savepoint(session, transaction):
        nonlocal inner_transaction
        if transaction == inner_transaction:
            session.expire_all()
            inner_transaction = session.begin_nested()

    db.event.listen(db.session, "after_transaction_end", restart_savepoint)

    yield

    db.event.remove(db.session, "after_transaction_end", restart_savepoint)

    inner_transaction.rollback()  # probably rollback not so much
    outer_transaction.rollback()  # rollback all changes made during this test


