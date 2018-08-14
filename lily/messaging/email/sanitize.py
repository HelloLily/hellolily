import bleach

_ALLOWED_TAGS = [
    'a', 'abbr', 'acronym', 'address', 'area', 'article', 'aside', 'b', 'base', 'bdi', 'big', 'blockquote', 'body',
    'br', 'button', 'caption', 'center', 'cite', 'code', 'col', 'colgroup', 'data', 'datalist', 'dd', 'del', 'details',
    'dfn', 'dir', 'div', 'dl', 'dt', 'em', 'fieldset', 'figcaption', 'figure', 'font', 'footer', 'form', 'h1', 'h2',
    'h3', 'h4', 'h5', 'h6', 'head', 'header', 'hr', 'html', 'i', 'img', 'input', 'ins', 'kbd', 'keygen', 'label',
    'legend', 'li', 'link', 'main', 'map', 'mark', 'menu', 'menuitem', 'meta', 'meter', 'nav', 'ol', 'optgroup',
    'option', 'output', 'p', 'pre', 'progress', 'q', 'rp', 'rt', 'ruby', 's', 'samp', 'section', 'select', 'small',
    'span', 'strike', 'strong', 'style', 'sub', 'summary', 'sup', 'table', 'title', 'tbody', 'td', 'textarea', 'tfoot',
    'th', 'thead', 'time', 'tr', 'tt', 'u', 'ul', 'var', 'wbr'
]

_ALLOWED_ATTRIBUTES = [
    'abbr', 'accept', 'accept-charset', 'accesskey', 'action', 'align', 'alt', 'autocomplete', 'autosave', 'axis',
    'bgcolor', 'border', 'cellpadding', 'cellspacing', 'challenge', 'char', 'charoff', 'charset', 'checked', 'cid',
    'cite', 'clear', 'color', 'cols', 'colspan', 'compact', 'contenteditable', 'coords', 'datetime', 'dir', 'disabled',
    'draggable', 'dropzone', 'enctype', 'for', 'frame', 'headers', 'height', 'high', 'href', 'hreflang', 'hspace',
    'ismap', 'keytype', 'label', 'lang', 'list', 'longdesc', 'low', 'max', 'maxlength', 'media', 'method', 'min',
    'multiple', 'name', 'nohref', 'noshade', 'novalidate', 'nowrap', 'open', 'optimum', 'pattern', 'placeholder',
    'prompt', 'pubdate', 'radiogroup', 'readonly', 'rel', 'required', 'rev', 'reversed', 'rows', 'rowspan', 'rules',
    'scope', 'selected', 'shape', 'size', 'span', 'spellcheck', 'src', 'start', 'step', 'style', 'summary', 'tabindex',
    'target', 'title', 'type', 'usemap', 'valign', 'value', 'vspace', 'width', 'wrap'
]

_ALLOWED_STYLES = [
    'background', 'background-attachment', 'background-color', 'background-image', 'background-position',
    'background-repeat', 'border', 'border-bottom', 'border-bottom-color', 'border-bottom-style',
    'border-bottom-width', 'border-collapse', 'border-color', 'border-left', 'border-left-color', 'border-left-style',
    'border-left-width', 'border-right', 'border-right-color', 'border-right-style', 'border-right-width',
    'border-spacing', 'border-style', 'border-top', 'border-top-color', 'border-top-style', 'border-top-width',
    'border-width', 'bottom', 'caption-side', 'clear', 'clip', 'color', 'content', 'counter-increment',
    'counter-reset', 'cursor', 'direction', 'display', 'empty-cells', 'float', 'font', 'font-family', 'font-size',
    'font-style', 'font-variant', 'font-weight', 'height', 'left', 'letter-spacing', 'line-height', 'list-style',
    'list-style-image', 'list-style-position', 'list-style-type', 'margin', 'margin-bottom', 'margin-left',
    'margin-right', 'margin-top', 'max-height', 'max-width', 'min-height', 'min-width', 'opacity', 'orphans',
    'outline', 'outline-color', 'outline-style', 'outline-width', 'overflow', 'padding', 'padding-bottom',
    'padding-left', 'padding-right', 'padding-top', 'page-break-after', 'page-break-before', 'page-break-inside',
    'quotes', 'right', 'table-layout', 'text-align', 'text-decoration', 'text-indent', 'text-transform', 'top',
    'unicode-bidi', 'url', 'vertical-align', 'visibility', 'white-space', 'widows', 'width', 'word-spacing', 'z-index'
]


def sanitize_html_email(html):
    if html is None:
        return None

    return bleach.clean(
        html,
        tags=_ALLOWED_TAGS,
        attributes=_ALLOWED_ATTRIBUTES,
        styles=_ALLOWED_STYLES,
        strip=True,
        strip_comments=True
    )
