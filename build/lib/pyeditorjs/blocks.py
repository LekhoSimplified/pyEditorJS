import typing as t

try:
    import bleach # type: ignore

except ImportError:
    import warnings

    class bleach:
        @staticmethod
        def clean(text: str, tags: list=[], attributes: list=[]):
            warnings.warn("Requested sanitization, but `bleach` is not installed. Not sanitizing...", UserWarning)
            return text


from dataclasses import dataclass
from .exceptions import EditorJsParseError
from .inline import mithril as inline_mithril

__all__ = [
    "EditorJsBlock",
    "HeaderBlock",
    "ParagraphBlock",
    "ListBlock",
    "DelimiterBlock",
    "ImageBlock"
]



def _sanitize(html: str) -> str:
    return bleach.clean(html, tags=['b', 'i', 'u', 'a', 'mark', 'code'], attributes=['href'])


@dataclass
class EditorJsBlock:
    """
        A generic parsed Editor.js block
    """

    _data: dict
    """The raw JSON data of the entire block"""


    @property
    def id(self) -> t.Optional[str]:
        """
            Returns ID of the block, generated client-side.
        """

        return self._data.get("id", None)



    @property
    def type(self) -> t.Optional[str]:
        """
            Returns the type of the block.
        """

        return self._data.get("type", None)


    @property
    def data(self) -> dict:
        """
            Returns the actual block data.
        """

        return self._data.get("data", {})


    def html(self, sanitize: bool=False) -> str:
        """
            Returns the HTML representation of the block.

            ### Parameters:
            - `sanitize` - if `True`, then the block's text/contents will be sanitized.
        """

        raise NotImplementedError()

    def mithril(self, sanitize: bool=False) -> str:
        """
            Returns the MithrilJS representation of the block.

            ### Parameters:
            - `sanitize` - if `True`, then the block's text/contents will be sanitized.
        """

        raise NotImplementedError()



class HeaderBlock(EditorJsBlock):
    VALID_HEADER_LEVEL_RANGE = range(1, 7)
    """Valid range for header levels. Default is `range(1, 7)` - so, `0` - `6`."""

    @property
    def text(self) -> t.Optional[str]:
        """
            Returns the header's text.
        """

        return self.data.get("text", None)


    @property
    def level(self) -> int:
        """
            Returns the header's level (`0` - `6`).
        """

        _level = self.data.get("level", 1)

        if not isinstance(_level, int) or _level not in self.VALID_HEADER_LEVEL_RANGE:
            raise EditorJsParseError(f"`{_level}` is not a valid header level.")

        return _level


    def html(self, sanitize: bool=False) -> str:
        return rf'<h{self.level}>{_sanitize(self.text) if sanitize else self.text}</h{self.level}>'

    def mithril(self, sanitize: bool=False) -> str:
        return f"m('h{self.level}',`{_sanitize(self.text) if sanitize else self.text}`)"


class ParagraphBlock(EditorJsBlock):
    @property
    def text(self) -> t.Optional[str]:
        """
            The text content of the paragraph.
        """

        return self.data.get("text", None)


    def html(self, sanitize: bool=False) -> str:
        return rf'<p>{_sanitize(self.text) if sanitize else self.text}</p>'

    def mithril(self, sanitize: bool=False) -> str:
        return f"m('p',[{inline_mithril(_sanitize(self.text) if sanitize else self.text)}])"



class ListBlock(EditorJsBlock):
    VALID_STYLES = ('unordered', 'ordered')
    """Valid list order styles."""

    @property
    def style(self) -> t.Optional[str]:
        """
            The style of the list. Can be `ordered` or `unordered`.
        """

        return self.data.get("style", None)


    @property
    def items(self) -> t.List[str]:
        """
            Returns the list's items, in raw format.
        """

        return self.data.get("items", [])


    def html(self, sanitize: bool=False) -> str:
        if self.style not in self.VALID_STYLES:
            raise EditorJsParseError(f"`{self.style}` is not a valid list style.")

        _items = [f"<li>{_sanitize(item) if sanitize else item}</li>" for item in self.items]
        _type = "ul" if self.style == "unordered" else "ol"
        _items_html = ''.join(_items)

        return rf'<{_type}>{_items_html}</{_type}>'


    def mithril(self, sanitize: bool=False) -> str:
        if self.style not in self.VALID_STYLES:
            raise EditorJsParseError(f"`{self.style}` is not a valid list style.")

        _items = [f"m('li', [{inline_mithril(_sanitize(item) if sanitize else item)}])" for item in self.items]
        _type = "ul" if self.style == "unordered" else "ol"
        _items_js = ','.join(_items)

        return rf"m('{_type}', [{_items_js}])"


class DelimiterBlock(EditorJsBlock):
    def html(self, sanitize: bool=False) -> str:
        return r'<div class="cdx-block ce-delimiter"></div>'



class ImageBlock(EditorJsBlock):
    @property
    def file_url(self) -> t.Optional[str]:
        """
            URL of the image file.
        """

        return self.data.get("file", {}).get("url", None)


    @property
    def caption(self) -> t.Optional[str]:
        """
            The image's caption.
        """

        return self.data.get("caption", None)


    @property
    def with_border(self) -> bool:
        """
            Whether the image has a border.
        """

        return self.data.get("withBorder", False)


    @property
    def stretched(self) -> bool:
        """
            Whether the image is stretched.
        """

        return self.data.get("stretched", False)


    @property
    def with_background(self) -> bool:
        """
            Whether the image has a background.
        """

        return self.data.get("withBackground", False)


    def html(self, sanitize: bool=False) -> str:
        if self.file_url.startswith("data:image/"):
            _img = self.file_url
        else:
            _img = _sanitize(self.file_url) if sanitize else self.file_url

        parts = [
            rf'<div class="cdx-block image-tool image-tool--filled {"image-tool--stretched" if self.stretched else ""} {"image-tool--withBorder" if self.with_border else ""} {"image-tool--withBackground" if self.with_background else ""}">'
            r'<div class="image-tool__image">',
            r'<div class="image-tool__image-preloader"></div>',
            rf'<img class="image-tool__image-picture" src="{_img}"/>',
            r'</div>'
            rf'<div class="image-tool__caption" data-placeholder="{_sanitize(self.caption) if sanitize else self.caption}"></div>'
            r'</div>'
            r'</div>'
        ]

        return ''.join(parts)
