from io import StringIO
from pathlib import Path
from shutil import rmtree

from django.core.management import call_command

from PIL import Image

from groups.models import Group
from reader.models import Chapter, Page, Series

from . import ConfigTestBase


class TestFS2Import(ConfigTestBase):
    def setup_method(self):
        self.fs2_root = (
            Path(__file__).resolve().parent / 'fixtures' / 'foolslide2'
        )
        self.fs2_xml = self.fs2_root / 'foolslide.xml'
        # Setup fs2 content
        series_root = (
            self.fs2_root / 'content' / 'comics' / 'testo_5c757683a638f'
        )
        chapter_root = series_root / '1-0-test_5c757cceb87cc'
        chapter_root.mkdir(parents=True, exist_ok=True)
        cover = Image.new('RGB', size=(655, 1002))
        cover.save(str(series_root / 'cover.jpg'), 'JPEG')
        test_page = Image.new('RGB', size=(655, 1002))
        test_page.save(str(chapter_root / 'test-1.jpg'), 'JPEG')

    def test_fs2_import_valid(self):
        out = StringIO()
        call_command(
            'fs2import', str(self.fs2_root),
            str(self.fs2_xml), '--noinput', stdout=out
        )
        assert 'Successfully imported FoolSlide2 data.' in out.getvalue()
        assert Group.objects.count() == 2
        assert Series.objects.count() == 1
        assert Chapter.objects.count() == 1
        assert Page.objects.count() == 1

    def teardown_method(self):
        super().teardown_method()
        rmtree(self.fs2_root / 'content')
