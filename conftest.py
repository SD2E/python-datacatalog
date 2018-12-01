def pytest_addoption(parser):
    parser.addoption('--longrun', action='store_true', dest="longrun",
                     default=False, help="Enable tests that might take a long time")
    parser.addoption('--networked', action='store_true', dest="networked",
                     default=False, help="Enable tests that require external network access")
    parser.addoption('--delete', action='store_true', dest="delete",
                     default=False, help="Enable tests that delete database entries")
    parser.addoption('--bootstrap', action='store_true', dest="bootstrap",
                     default=False, help="Run bootstrapping tests for development environment")
