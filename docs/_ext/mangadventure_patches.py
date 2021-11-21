from typing import get_type_hints, Any, List, Optional, Type, Tuple

from django.db.models.base import Model
from django.db.models.fields import AutoField
from django.db.models.fields.related_descriptors import (
    ForeignKeyDeferredAttribute,
    ReverseManyToOneDescriptor,
    ReverseOneToOneDescriptor,
)
from django.db.models.manager import ManagerDescriptor
from django.db.models.query import QuerySet
from django.db.models.query_utils import DeferredAttribute

from sphinx.application import Sphinx
from sphinx.ext.autodoc import DataDocumenter, Options, PropertyDocumenter


def _get_module(cls: Optional[Type]) -> str:
    if not hasattr(cls, '__module__'):
        return 'builtins'
    if not cls.__module__.startswith('django'):
        return cls.__module__.lstrip('_')
    django_references = {
        'django.db.models',
        'django.forms',
        'django.contrib.admin',
        'django.http',
        'django.core.files',
        'django.apps',
        'django.core.management',
    }
    excluded_names = {
        'QuerySet',
        'FieldFile',
        'FileSystemStorage',
        'BaseInlineFormSet',
    }
    for ref in django_references:
        if cls.__name__ in excluded_names:
            continue
        if cls.__module__.startswith(ref):
            return ref
    return cls.__module__


def _patched_add_directive_header(self: DataDocumenter, sig: str):
    # Don't document values of settings
    if self.modname == 'MangAdventure.settings':
        super(DataDocumenter, self).add_directive_header(sig)
    else:
        self._original_add_directive_header(sig)


def _patched_can_document_member(cls: Type[PropertyDocumenter],
                                 member: Any, membername: str,
                                 isattr: bool, parent: Any) -> bool:
    return member.__class__.__name__ == 'cached_property' or \
        cls._original_can_document_member(member, membername, isattr, parent)


def apply_patches(app: Sphinx):
    import sphinx_autodoc_typehints

    sphinx_autodoc_typehints.get_annotation_module = _get_module

    PropertyDocumenter._original_can_document_member = \
        PropertyDocumenter.can_document_member
    PropertyDocumenter.can_document_member = \
        classmethod(_patched_can_document_member)

    DataDocumenter._original_add_directive_header = \
        DataDocumenter.add_directive_header
    DataDocumenter.add_directive_header = _patched_add_directive_header

    ManagerDescriptor.__get__ = lambda self, *args, **kwargs: self.manager

    QuerySet.__repr__ = lambda self: self.__class__.__name__


def skip_django_junk(app: Sphinx, what: str, name: str,
                     obj: Any, skip: bool, options: Options) -> bool:
    junk = (
        ForeignKeyDeferredAttribute,
        ReverseManyToOneDescriptor,
        ReverseOneToOneDescriptor,
    )
    if isinstance(obj, junk):
        return True
    if isinstance(obj, property):
        return name == 'media' or skip
    if isinstance(obj, DeferredAttribute):
        return isinstance(obj.field, AutoField) or skip
    return name == 'do_not_call_in_templates' or skip


def process_signature(app: Sphinx, what: str, name: str, obj: Any, options:
                      Options, signature: Optional[str], return_annotation:
                      Optional[str]) -> Tuple[Optional[str], Optional[str]]:
    if what != 'class':
        return signature, return_annotation
    if issubclass(obj, Model):
        signature, return_annotation = '(*args, **kwargs)', None
    for idx, base in enumerate(obj.__bases__):
        module = _get_module(base)
        if module != 'builtins':
            obj.__bases__[idx].__module__ = module
    return signature, return_annotation


def process_docstring(app: Sphinx, what: str, name: str, obj:
                      Any, options: Options, lines: List[str]):
    if obj is None or not lines:
        return
    # this class is broken for some reason
    if name[:28] == 'users.forms.UserProfileForm.':
        cls = {
            'email': 'EmailField', 'avatar': 'ImageField'
        }.get(name[28:], 'CharField')
        lines[0] = f':class:`~django.forms.{cls}` - {lines[0]}'
        return
    if what == 'attribute':
        cls = getattr(obj, 'field', obj).__class__
    elif what == 'property':
        func = getattr(obj, 'fget', obj.func)
        cls = get_type_hints(func)['return']
    else:
        return
    if cls.__module__ == 'builtins':
        qname = cls.__name__
    elif cls.__name__ in {'dict', 'list', 'tuple'}:
        qname = f'typing.{cls.__name__.capitalize()}'
    else:
        qname = f'{_get_module(cls)}.{cls.__name__}'
    lines[0] = f':class:`~{qname}` – {lines[0]}'


def setup(app: Sphinx):
    app.connect('builder-inited', apply_patches)
    app.connect('autodoc-skip-member', skip_django_junk)
    app.connect('autodoc-process-signature', process_signature)
    app.connect('autodoc-process-docstring', process_docstring)
    app.add_css_file('css/style.css')
