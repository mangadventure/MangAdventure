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
        self.fs2_root = Path(__file__).parent / 'fixtures' / 'foolslide2'
        self.fs2_xml = self.fs2_root / 'foolslide.xml'
        # Setup fs2 content
        series_root = (self.fs2_root / 'content' / 'comics' /
                       'testo_5c757683a638f')
        chapter_root = series_root / '1-0-test_5c757cceb87cc'
        Path(chapter_root).mkdir(parents=True, exist_ok=True)
        cover = Image.new('RGB', size=(655, 1002))
        cover.save(series_root / 'cover.jpg')
        test_page = Image.new('RGB', size=(655, 1002))
        test_page.save(chapter_root / 'test-1.jpg')

    def test_fs2_import_valid(self):
        out = StringIO()
        call_command('fs2import', self.fs2_root.resolve(),
                     self.fs2_xml.resolve(), '-y', stdout=out)
        assert 'Successfully imported FoolSlide2 data.' in out.getvalue()
        assert len(Group.objects.all()) == 2
        assert len(Series.objects.all()) == 1
        assert len(Chapter.objects.all()) == 1
        assert len(Page.objects.all()) == 1

    def teardown_method(self):
        rmtree(self.fs2_root / 'content')
