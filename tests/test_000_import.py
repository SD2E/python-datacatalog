import pytest

@pytest.mark.smoktest
def test_can_import_datacalog():
    import datacatalog

@pytest.mark.smoktest
def test_datacalog_about_version():
    from datacatalog import __about__ as about
    assert about.__version__ is not None
