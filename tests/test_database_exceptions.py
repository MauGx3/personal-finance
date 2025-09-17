"""Test for database exception handling improvements."""

import pytest
from unittest.mock import patch
import sys
import os

# Add src to path for importing the database module
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from personal_finance.database import DatabaseManager


class TestDatabaseManagerExceptions:
    """Test that DatabaseManager raises proper exceptions instead of using assert."""

    def test_get_session_raises_runtime_error_when_session_local_none(self):
        """Test that get_session raises RuntimeError when SessionLocal is None."""
        # Create a DatabaseManager with SQL backend but mock SessionLocal to None
        with patch.dict(os.environ, {'DATABASE_URL': 'sqlite:///test.db'}):
            db_manager = DatabaseManager()
            # Force SessionLocal to None to simulate the error condition
            db_manager.SessionLocal = None
            
            with pytest.raises(RuntimeError, match="SessionLocal is not initialized for SQL backend"):
                with db_manager.get_session():
                    pass

    def test_get_session_works_normally_with_valid_session_local(self):
        """Test that get_session works normally when SessionLocal is properly initialized."""
        with patch.dict(os.environ, {'DATABASE_URL': 'sqlite:///test.db'}):
            db_manager = DatabaseManager()
            # SessionLocal should be properly initialized for SQL backend
            assert db_manager.SessionLocal is not None
            
            # This should not raise an exception
            with db_manager.get_session() as session:
                assert session is not None

    def test_mongodb_backend_bypasses_session_local_check(self):
        """Test that MongoDB backend doesn't check SessionLocal."""
        with patch.dict(os.environ, {'DATABASE_URL': 'mongodb://localhost/test'}):
            with patch('personal_finance.database.MongoClient'):
                db_manager = DatabaseManager()
                # For MongoDB, SessionLocal should be None
                assert db_manager.SessionLocal is None
                
                # This should not raise an exception for MongoDB backend
                with db_manager.get_session() as session:
                    assert session is not None