"""
Security Validation Tests
=========================

Simple tests to validate security implementations.
Run these tests after applying security updates.

Usage:
    python test_security.py
"""

import sys
sys.dont_write_bytecode = True

import os
from datetime import datetime


def print_header(text):
    """Print a formatted header"""
    print("\n" + "=" * 60)
    print(f"  {text}")
    print("=" * 60)


def print_test(name, passed, message=""):
    """Print test result"""
    status = "✅ PASS" if passed else "❌ FAIL"
    print(f"{status} - {name}")
    if message:
        print(f"       {message}")


def test_env_file():
    """Test .env file existence and content"""
    print_header("Testing Environment Configuration")

    # Test .env exists
    env_exists = os.path.exists('.env')
    print_test(".env file exists", env_exists)

    if env_exists:
        with open('.env', 'r') as f:
            content = f.read()

        # Test SECRET_KEY is set
        has_secret = 'SECRET_KEY=' in content and 'your-secret-key-here' not in content
        print_test("SECRET_KEY is configured", has_secret,
                  "Make sure SECRET_KEY is not the default value")

        # Test FLASK_DEBUG is set
        has_debug_config = 'FLASK_DEBUG=' in content
        print_test("FLASK_DEBUG is configured", has_debug_config)

        if 'FLASK_DEBUG=True' in content:
            print_test("FLASK_DEBUG=False in production", False,
                      "WARNING: Debug mode is enabled!")


def test_gitignore():
    """Test .gitignore protects sensitive files"""
    print_header("Testing .gitignore Configuration")

    if os.path.exists('.gitignore'):
        with open('.gitignore', 'r') as f:
            content = f.read()

        tests = [
            ('.env', '.env in .gitignore'),
            ('*.db', 'Database files in .gitignore'),
            ('*.pem', 'Certificate files in .gitignore'),
            ('__pycache__', 'Python cache in .gitignore'),
        ]

        for pattern, description in tests:
            print_test(description, pattern in content)
    else:
        print_test(".gitignore exists", False, "File not found")


def test_password_hashing():
    """Test password hashing implementation"""
    print_header("Testing Password Hashing")

    try:
        from instance.base import User
        from datetime import datetime

        # Test User class has hashing methods
        has_set_password = hasattr(User, 'set_password')
        print_test("User.set_password() method exists", has_set_password)

        has_check_password = hasattr(User, 'check_password')
        print_test("User.check_password() method exists", has_check_password)

        if has_set_password and has_check_password:
            # Test hashing works
            test_user = User(
                username="test_user",
                password="test_password",
                name="Test User",
                type="User",
                write_date=datetime.now()
            )

            # Check password is hashed
            is_hashed = test_user.password != "test_password"
            print_test("Password is hashed", is_hashed,
                      f"Hashed: {test_user.password[:30]}...")

            # Check password verification works
            correct_check = test_user.check_password("test_password")
            print_test("Password verification works (correct)", correct_check)

            incorrect_check = not test_user.check_password("wrong_password")
            print_test("Password verification works (incorrect)", incorrect_check)

    except Exception as e:
        print_test("Password hashing implementation", False, str(e))


def test_config_file():
    """Test config.py exists and is valid"""
    print_header("Testing Configuration File")

    config_exists = os.path.exists('config.py')
    print_test("config.py exists", config_exists)

    if config_exists:
        try:
            from config import get_config, Config

            # Test Config class
            has_secret_key = hasattr(Config, 'SECRET_KEY')
            print_test("Config has SECRET_KEY", has_secret_key)

            has_csrf = hasattr(Config, 'WTF_CSRF_ENABLED')
            print_test("Config has CSRF settings", has_csrf)

            has_rate_limit = hasattr(Config, 'RATELIMIT_STORAGE_URL')
            print_test("Config has rate limiting settings", has_rate_limit)

            # Test get_config function
            config = get_config()
            print_test("get_config() returns configuration", config is not None)

        except Exception as e:
            print_test("config.py is valid", False, str(e))


def test_dependencies():
    """Test required dependencies are installed"""
    print_header("Testing Dependencies")

    dependencies = [
        ('flask', 'Flask'),
        ('flask_wtf', 'Flask-WTF (CSRF)'),
        ('flask_limiter', 'Flask-Limiter (Rate Limiting)'),
        ('dotenv', 'python-dotenv'),
        ('werkzeug.security', 'Werkzeug (Password Hashing)'),
        ('gunicorn', 'Gunicorn (WSGI Server)'),
    ]

    for module, name in dependencies:
        try:
            __import__(module)
            print_test(f"{name} installed", True)
        except ImportError:
            print_test(f"{name} installed", False,
                      f"Install with: pip install {name}")


def test_app_imports():
    """Test app.py has security imports"""
    print_header("Testing App Security Imports")

    if os.path.exists('app.py'):
        with open('app.py', 'r') as f:
            content = f.read()

        tests = [
            ('flask_wtf.csrf', 'CSRF Protection imported'),
            ('flask_limiter', 'Rate Limiter imported'),
            ('CSRFProtect', 'CSRFProtect used'),
            ('Limiter', 'Limiter used'),
            ('get_config', 'Config imported'),
        ]

        for pattern, description in tests:
            print_test(description, pattern in content)

        # Check debug is not hardcoded
        debug_hardcoded = 'debug=True' in content and 'debug_mode' not in content
        print_test("Debug mode not hardcoded", not debug_hardcoded,
                  "Debug should be controlled by environment variable")
    else:
        print_test("app.py exists", False)


def test_migration_script():
    """Test password migration script exists"""
    print_header("Testing Migration Script")

    script_exists = os.path.exists('migrate_passwords.py')
    print_test("migrate_passwords.py exists", script_exists)

    if script_exists:
        with open('migrate_passwords.py', 'r') as f:
            content = f.read()

        has_hash = 'generate_password_hash' in content
        print_test("Migration uses password hashing", has_hash)


def test_documentation():
    """Test documentation files exist"""
    print_header("Testing Documentation")

    docs = [
        ('SECURITY.md', 'Security guide'),
        ('DEPLOYMENT.md', 'Deployment guide'),
        ('QUICKSTART.md', 'Quick start guide'),
        ('CHANGELOG_SECURITY.md', 'Security changelog'),
    ]

    for filename, description in docs:
        exists = os.path.exists(filename)
        print_test(description, exists)


def test_deployment_files():
    """Test deployment configuration files exist"""
    print_header("Testing Deployment Files")

    files = [
        ('gunicorn_config.py', 'Gunicorn configuration'),
        ('wsgi.py', 'WSGI entry point'),
        ('nginx.conf.example', 'Nginx configuration'),
        ('systemd.service.example', 'Systemd service'),
        ('setup.sh', 'Setup script'),
    ]

    for filename, description in files:
        exists = os.path.exists(filename)
        print_test(description, exists)


def test_security_summary():
    """Print security implementation summary"""
    print_header("Security Implementation Summary")

    checks = []

    # Check password hashing
    try:
        from instance.base import User
        has_hashing = hasattr(User, 'check_password')
        checks.append(("Password Hashing (PBKDF2-SHA256)", has_hashing))
    except:
        checks.append(("Password Hashing (PBKDF2-SHA256)", False))

    # Check .env
    has_env = os.path.exists('.env')
    checks.append(("Fixed SECRET_KEY (.env)", has_env))

    # Check config
    has_config = os.path.exists('config.py')
    checks.append(("Centralized Configuration", has_config))

    # Check CSRF
    if os.path.exists('app.py'):
        with open('app.py', 'r') as f:
            content = f.read()
        has_csrf = 'CSRFProtect' in content
        has_limiter = 'Limiter' in content
        checks.append(("CSRF Protection (Flask-WTF)", has_csrf))
        checks.append(("Rate Limiting (Flask-Limiter)", has_limiter))
    else:
        checks.append(("CSRF Protection (Flask-WTF)", False))
        checks.append(("Rate Limiting (Flask-Limiter)", False))

    # Check .gitignore
    if os.path.exists('.gitignore'):
        with open('.gitignore', 'r') as f:
            content = f.read()
        protects_env = '.env' in content
        checks.append((".env Protected in .gitignore", protects_env))
    else:
        checks.append((".env Protected in .gitignore", False))

    print("\nImplemented Security Features:")
    for feature, implemented in checks:
        status = "✅" if implemented else "❌"
        print(f"  {status} {feature}")

    passed = sum(1 for _, impl in checks if impl)
    total = len(checks)
    percentage = (passed / total) * 100

    print(f"\nSecurity Score: {passed}/{total} ({percentage:.0f}%)")

    if percentage == 100:
        print("\n🎉 All security features implemented correctly!")
    elif percentage >= 80:
        print("\n⚠️  Most security features implemented, but some are missing.")
    else:
        print("\n❌ Critical security features are missing. Please review the implementation.")


def main():
    """Run all tests"""
    print("\n" + "=" * 60)
    print("  SECURITY VALIDATION TESTS")
    print("=" * 60)
    print(f"  Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)

    try:
        test_env_file()
        test_gitignore()
        test_config_file()
        test_dependencies()
        test_password_hashing()
        test_app_imports()
        test_migration_script()
        test_deployment_files()
        test_documentation()
        test_security_summary()

        print("\n" + "=" * 60)
        print("  TESTS COMPLETED")
        print("=" * 60)
        print("\nNext Steps:")
        print("1. Fix any failed tests above")
        print("2. Run: python migrate_passwords.py (if you have existing users)")
        print("3. Test the application: python app.py")
        print("4. Review SECURITY.md for production deployment")
        print("\n")

    except Exception as e:
        print(f"\n❌ Test suite failed with error: {str(e)}")
        import traceback
        traceback.print_exc()


if __name__ == '__main__':
    main()
