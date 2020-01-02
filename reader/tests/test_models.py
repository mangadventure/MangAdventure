from django.urls import reverse

from pytest import raises

from MangAdventure.tests import get_test_image, get_valid_zip_file

from reader.models import Artist, Author, Category, Chapter, Page, Series

from . import ReaderTestBase


class TestAuthor(ReaderTestBase):
    @staticmethod
    def create_author():
        return Author.objects.create(name='Author')

    def test_create(self):
        author = self.create_author()
        assert str(author) == 'Author'

    def test_alias(self):
        author = self.create_author()
        author.aliases.create(alias='test')
        assert len(author.aliases.all()) == 1


class TestArtist(ReaderTestBase):
    @staticmethod
    def create_artist():
        return Artist.objects.create(name='Artist')

    def test_create(self):
        artist = self.create_artist()
        assert str(artist) == 'Artist'

    def test_alias(self):
        artist = self.create_artist()
        artist.aliases.create(alias='test')
        assert len(artist.aliases.all()) == 1


class TestCategory(ReaderTestBase):
    @staticmethod
    def create_category():
        return Category.objects.get_or_create(name='Adventure',
                                              description='Epic')[0]

    def test_create(self):
        category = self.create_category()
        assert str(category) == 'Adventure'
        assert category.id == 'adventure'


class TestSeries(ReaderTestBase):
    @staticmethod
    def create_series(title: str = 'My Series', **kwargs):
        series = Series.objects.get_or_create(title=title, **kwargs)[0]
        series.authors.add(TestAuthor.create_author())
        series.artists.add(TestArtist.create_artist())
        series.categories.add(TestCategory.create_category())
        return series

    def test_create(self):
        series = self.create_series()
        assert str(series) == 'My Series'

    def test_get_absolute_url(self):
        series = self.create_series()
        assert series.get_absolute_url() == reverse('reader:series', kwargs={
            'slug': series.slug})

    def test_get_directory(self):
        series = self.create_series()
        assert str(series.get_directory()) == 'series/my-series'

    def test_alias(self):
        series = self.create_series()
        series.aliases.create(alias='test')
        assert len(series.aliases.all()) == 1


class TestChapter(ReaderTestBase):
    @staticmethod
    def create_chapter(number: int = 0.5, volume: int = 1, **kwargs):
        series = TestSeries.create_series()
        chapter = Chapter.objects.get_or_create(title='Chapter', number=number,
                                                volume=volume, series=series,
                                                **kwargs)[0]
        return chapter

    def test_create(self):
        chapter = self.create_chapter()
        assert str(chapter) == 'My Series - 1/0.5: Chapter'
        assert chapter._tuple == (1, 0.5)
        assert type(hash(chapter))

    def test_get_directory(self):
        chapter = self.create_chapter()
        assert str(chapter.get_directory()) == 'series/my-series/1/0.5'

    def test_get_absolute_url(self):
        chapter = self.create_chapter()
        assert chapter.get_absolute_url() == reverse('reader:chapter', kwargs={
            'slug': chapter.series.slug, 'vol': chapter.volume,
            'num': chapter.number
        })

    def test_relations(self):
        chapter1 = self.create_chapter(volume=2, number=1)
        chapter2 = self.create_chapter(volume=1, number=1)
        chapter3 = self.create_chapter(volume=2, number=2)
        # Next / prev
        assert chapter1.prev == chapter2
        assert chapter1.next == chapter3
        # lt / gt
        assert chapter2 < chapter1 < chapter3
        assert chapter3 > chapter1 > chapter2
        assert chapter1 > (1, 1)
        assert chapter1 < (2, 2)
        with raises(TypeError):
            assert chapter1 > 1
        with raises(TypeError):
            assert chapter1 < 1
        # eq
        assert chapter1 == chapter1
        assert chapter1 == (2, 1)

    def test_file(self):
        chapter = self.create_chapter()
        chapter.file = get_valid_zip_file()
        chapter.save()
        assert len(chapter.pages.all()) == 1
        assert chapter.zip()

    def test_dates(self):
        chapter = self.create_chapter()
        assert chapter.uploaded_date.endswith('GMT')
        assert chapter.uploaded_date == chapter.modified_date

    def test_twitter(self):
        chapter = self.create_chapter()
        chapter.groups.create(name='my group', twitter='TestAccount')
        assert chapter.twitter_creator == '@TestAccount'


class TestPage(ReaderTestBase):
    @staticmethod
    def create_page(number: int = 1):
        chapter = TestChapter.create_chapter()
        file = get_test_image()
        return Page.objects.create(chapter=chapter, image=file, number=number)

    def test_crate(self):
        page = self.create_page()
        assert str(page) == 'My Series - 1/0.5 [random-name.jpg]'
        assert hash(page)

    def test_get_absolute_url(self):
        page = self.create_page()
        assert page.get_absolute_url() == reverse('reader:page', kwargs={
            'slug': 'my-series', 'vol': 1, 'num': 0.5, 'page': 1
        })

    def test_preload(self):
        page = self.create_page()
        for i in range(2, 6):
            self.create_page(i)
        assert len(page.preload.all()) == 3

    def test_relations(self):
        page1 = self.create_page(1)
        page2 = self.create_page(2)
        # lt, gt
        assert page1 < page2
        assert page2 > page1
        assert page1 > 0
        assert page1 < 2
        with raises(TypeError):
            assert page1 > '0'
        with raises(TypeError):
            assert page1 < '2'
        # eq
        assert not page1 == page2
        assert page1 == 1
        assert not page1 == 'test'