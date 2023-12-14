"""
Custom storages.

.. seealso::

    https://docs.djangoproject.com/en/5.0/ref/files/storage/
"""

from pathlib import Path
from typing import Iterator
from urllib.parse import quote, urlencode

from django.conf import settings
from django.contrib.staticfiles.finders import FileSystemFinder
from django.contrib.staticfiles.storage import StaticFilesStorage
from django.core.files.storage import FileSystemStorage

from sass import compile as sassc

#: Variables used to generate ``static/styles/_variables.scss``.
SCSS_VARS = """\
$main-bg: %(MAIN_BG_COLOR)s;
$alter-bg: %(ALTER_BG_COLOR)s;
$main-fg: %(MAIN_TEXT_COLOR)s;
$alter-fg: %(ALTER_TEXT_COLOR)s;
$shadow-color: %(SHADOW_COLOR)s;
$font-family: %(FONT_NAME)s;
"""


def _is_newer(a: Path, b: Path) -> bool:
    """Check if file ``a`` is newer than file ``b``."""
    return a.stat().st_mtime > b.stat().st_mtime


class ProcessedStaticFilesFinder(FileSystemFinder):
    """Static files finder that for processed files."""
    def find_location(self, root: str, path: str,
                      prefix: str | None = None) -> str | None:
        if path.startswith('COMPILED'):
            root = root.removesuffix('styles') + 'COMPILED'
            return super().find_location(root, path, 'COMPILED')
        return super().find_location(root, path, prefix)


class ProcessedStaticFilesStorage(StaticFilesStorage):
    """Static files storage class with postprocessing."""
    def __init__(self, *args, **kwargs):  # pragma: no cover
        super().__init__(*args, **kwargs)

        self._src = Path(self.location)
        self._dst = Path(self.location, 'COMPILED')
        self._dst.mkdir(exist_ok=True)

        content = SCSS_VARS % settings.CONFIG
        variables = Path(self.location, 'styles', '_variables.scss')
        if not variables.exists() or variables.read_text() != content:
            variables.write_text(content)

        extra = Path(self.location, 'styles', 'extra.scss')
        if not extra.exists():
            extra.touch(0o644)

    def url(self, name: str | None) -> str:
        url = super().url(name)
        if name is None or not name.endswith('.scss'):
            return url
        return url.replace('styles', 'COMPILED').replace('.scss', '.css')

    def post_process(self, paths: dict[str, tuple[FileSystemStorage, str]],
                     dry_run: bool = False, **kwargs
                     ) -> Iterator[tuple[str, str, bool] | None]:
        """
        Post process static files.

        This is used to compile SCSS stylesheets.

        :param paths: The static file paths.
        :param dry_run: Don't do anything if ``True``.

        :return: Yields a tuple for each static file.
        """
        if dry_run:  # pragma: no cover
            return
        for k, v in paths.items():
            src: Path = self._src / k
            if src.suffix == '.scss' and src.name[0] != '_':
                dst = self._dst / src.with_suffix('.css').name
                if not dst.exists() or _is_newer(src, dst):  # pragma: no cover
                    dst.write_text(
                        sassc(filename=str(src), output_style='compressed')
                    )
                yield k, str(dst), True
            else:
                yield k, v[1], False


class CDNStorage(FileSystemStorage):
    """
    Storage class that may use an image CDN.

    The options are statically_, weserv_ & photon_.

    :param fit: A tuple of width & height to fit the image in.

    .. _statically: https://statically.io/docs/using-images/
    .. _weserv: https://images.weserv.nl/docs/
    .. _photon: https://developer.wordpress.com/docs/photon/
    """

    def __init__(self, fit: tuple[int, int] | None = None):
        super().__init__()
        self._cdn: str = settings.CONFIG['USE_CDN']
        self._fit = {'w': fit[0], 'h': fit[1]} if fit else {}

    def _statically_url(self, name: str) -> str:
        domain = settings.CONFIG['DOMAIN']
        base = f'https://cdn.statically.io/img/{domain}/'
        fit = ','.join('%s=%d' % i for i in self._fit.items())
        return base + fit + self.base_url + name

    def _weserv_url(self, name: str) -> str:
        domain = settings.CONFIG['DOMAIN']
        base = 'https://images.weserv.nl/?url='
        scheme = settings.ACCOUNT_DEFAULT_HTTP_PROTOCOL
        url = f'{scheme}://{domain}{self.base_url}{name}'
        params = {**self._fit, 'l': 0, 'q': 100}
        qs = '&'.join('%s=%d' % i for i in params.items())
        return base + quote(url, '') + '&' + qs + '&we'

    def _photon_url(self, name: str) -> str:
        domain = settings.CONFIG['DOMAIN']
        scheme = settings.ACCOUNT_DEFAULT_HTTP_PROTOCOL
        base = f'{scheme}://i3.wp.com/'
        qs = {'ssl': '1'} if scheme == 'https' else {}
        if name.lower().endswith(('.jpg', '.jpeg')):
            qs['quality'] = '100'
        if self._fit:
            qs['fit'] = f'{self._fit["w"]},{self._fit["h"]}'
        return base + domain + self.base_url + name + '?' + urlencode(qs)

    def url(self, name: str) -> str:
        """
        Return the URL where the contents of the file
        referenced by ``name`` can be accessed.

        :param name: The name of the file.

        :return: The URL of the file.
        """
        if not hasattr(self, method := f'_{self._cdn}_url'):
            domain = settings.CONFIG['DOMAIN']
            scheme = settings.ACCOUNT_DEFAULT_HTTP_PROTOCOL
            return f'{scheme}://{domain}{self.base_url}{name}'
        return getattr(self, method)(name)


__all__ = [
    'SCSS_VARS', 'ProcessedStaticFilesFinder',
    'ProcessedStaticFilesStorage', 'CDNStorage'
]
