from os import getenv

from django.contrib.admin import AdminSite
from django.contrib.auth.models import User
from django.http import HttpRequest

from pytest import mark

from MangAdventure.tests.utils import get_test_image

from reader.admin import (
    ArtistAdmin, AuthorAdmin, CategoryAdmin, ChapterAdmin, SeriesAdmin
)
from reader.models import Artist, Author, Category, Chapter, Series

from . import ReaderTestBase


class ReaderAdminTestBase(ReaderTestBase):
    def setup_method(self):
        super().setup_method()
        self.site = AdminSite()
        self.request = HttpRequest()
        self.user = User.objects.get(pk=1)
        self.client.force_login(self.user)
        self.request.user = self.user


class TestChapterAdmin(ReaderAdminTestBase):
    def setup_method(self):
        super().setup_method()
        self.admin = ChapterAdmin(admin_site=self.site, model=Chapter)
        self.series = Series.objects.create(title='test')
        self.chapter = Chapter.objects.create(
            title='Chapter', number=1.5, series=self.series
        )

    def test_number(self):
        assert self.admin._number(self.chapter) == '1.5'

    def test_preview_page(self):
        self.chapter.pages.create(number=1, image=get_test_image())
        assert self.admin.preview(self.chapter).startswith('<img src="')

    def test_preview_none(self):
        assert self.admin.preview(self.chapter) == ''

    def test_toggle_final(self):
        Series.objects.create(title='test2').chapters \
            .create(title='Chapter', number=2)
        self.admin.toggle_final(
            request=self.request, queryset=Chapter.objects.all()
        )
        assert not Chapter.objects.filter(final=False)

    def test_pages(self):
        page = self.chapter.pages.create(number=1, image=get_test_image())
        inline = self.admin.get_inline_instances(self.request, self.chapter)
        assert inline[0].preview(page).startswith('<img src="')
        # TODO: validate formset


class TestSeriesAdmin(ReaderAdminTestBase):
    def setup_method(self):
        super().setup_method()
        self.admin = SeriesAdmin(admin_site=self.site, model=Series)
        self.series = Series.objects.create(title='series')

    def test_cover(self):
        self.series.cover = get_test_image()
        self.series.save()
        assert self.admin.cover_image(self.series).startswith('<img src="')

    def test_cover_none(self):
        assert self.admin.cover_image(self.series) == ''

    def test_toggle_completed(self):
        Series.objects.create(title='series2')
        self.admin.toggle_completed(self.request, Series.objects.all())
        assert not Series.objects.filter(completed=False)


class TestPersonAdmin(ReaderAdminTestBase):
    def setup_method(self):
        super().setup_method()
        self.author_admin = AuthorAdmin(admin_site=self.site, model=Author)
        self.artist_admin = ArtistAdmin(admin_site=self.site, model=Artist)
        self.author = Author.objects.create(name='author')
        self.author.aliases.create(name='author1')
        self.author.aliases.create(name='author2')
        self.artist = Artist.objects.create(name='artist')
        self.artist.aliases.create(name='artist1')
        self.artist.aliases.create(name='artist2')

    @mark.xfail(
        getenv('DB') == 'postgresql',
        reason='PostgreSQL still hates us'
    )  # TODO: appease PostgreSQL
    def test_aliases(self):
        assert self.author_admin.aliases(self.author) == 'author1, author2'
        assert self.artist_admin.aliases(self.artist) == 'artist1, artist2'


class TestCategoryAdmin(ReaderAdminTestBase):
    def setup_method(self):
        super().setup_method()
        self.admin = CategoryAdmin(admin_site=self.site, model=Category)
        self.category = Category.objects.create(
            name='Adventure', description='Test'
        )

    def test_readonly_fields(self):
        fields = self.admin.get_readonly_fields(self.request, self.category)
        assert fields == ('name',)

        fields = self.admin.get_readonly_fields(self.request)
        assert fields == ()
