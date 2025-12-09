"""
Password Migration Script
==========================

This script migrates existing plaintext passwords to hashed passwords.
Run this ONCE after updating the User model with password hashing.

Usage:
    python migrate_passwords.py

IMPORTANT: Backup your database before running this script!
"""

import sys
sys.dont_write_bytecode = True

from werkzeug.security import generate_password_hash, check_password_hash
from extensions import db
from instance.base import User
from app import app
import os


def is_password_hashed(password):
    """Check if a password is already hashed (starts with hash method identifier)"""
    return password.startswith('pbkdf2:sha256:') or password.startswith('scrypt:') or password.startswith('bcrypt:')


def migrate_passwords():
    """Migrate all plaintext passwords to hashed passwords"""

    print("=" * 60)
    print("Password Migration Script")
    print("=" * 60)
    print()

    # Check if database exists
    db_path = os.path.join(os.path.dirname(__file__), 'instance', 'test.db')
    if not os.path.exists(db_path):
        print("❌ Database not found. Please run the application first to create the database.")
        return

    print(f"📂 Database: {db_path}")
    print()

    with app.app_context():
        # Get all users
        users = User.query.all()

        if not users:
            print("ℹ️  No users found in database.")
            return

        print(f"Found {len(users)} user(s) in database")
        print()

        migrated_count = 0
        already_hashed_count = 0

        for user in users:
            print(f"Processing user: {user.username} (ID: {user.id})")

            # Check if password is already hashed
            if is_password_hashed(user.password):
                print(f"  ✓ Password already hashed")
                already_hashed_count += 1
            else:
                # Store the plaintext password temporarily
                plaintext_password = user.password

                # Hash the password
                hashed_password = generate_password_hash(
                    plaintext_password,
                    method='pbkdf2:sha256',
                    salt_length=16
                )

                # Update the password in database
                user.password = hashed_password

                print(f"  ✓ Password migrated successfully")
                print(f"    Old (plaintext): {plaintext_password[:3]}***")
                print(f"    New (hashed): {hashed_password[:30]}...")

                migrated_count += 1

            print()

        # Commit all changes
        try:
            db.session.commit()
            print("=" * 60)
            print("Migration Summary:")
            print("=" * 60)
            print(f"✅ Total users processed: {len(users)}")
            print(f"✅ Passwords migrated: {migrated_count}")
            print(f"ℹ️  Already hashed: {already_hashed_count}")
            print()
            print("🎉 Migration completed successfully!")
            print()
            print("⚠️  IMPORTANT: Users should now use their original passwords to login.")
            print("   The passwords are now securely hashed in the database.")
            print()

        except Exception as e:
            db.session.rollback()
            print("=" * 60)
            print("❌ ERROR: Migration failed!")
            print("=" * 60)
            print(f"Error: {str(e)}")
            print()
            print("The database has been rolled back to its previous state.")
            print("Please check the error and try again.")
            return


if __name__ == '__main__':
    print()
    print("⚠️  WARNING: This will modify all user passwords in the database!")
    print()

    # Ask for confirmation
    response = input("Do you want to continue? (yes/no): ").lower().strip()

    if response in ['yes', 'y']:
        print()
        migrate_passwords()
    else:
        print()
        print("Migration cancelled.")
        print()
