from django.utils.functional import wraps
from django import template

# Default tag whitelist
whitelist_tags = [
  'comment', 'csrf_token', 'cycle', 'filter', 'firstof', 'for', 'if',
  'ifchanged', 'now', 'regroup', 'spaceless', 'templatetag', 'url',
  'widthratio', 'with', 'block'
]

# Default filter whitelist
whitelist_filters = [
  'add', 'addslashes', 'capfirst', 'center', 'cut', 'date', 'default',
  'default_if_none', 'dictsort', 'dictsortreversed', 'divisibleby', 'escape',
  'escapejs', 'filesizeformat', 'first', 'fix_ampersands', 'floatformat',
  'force_escape', 'get_digit', 'iriencode', 'join', 'last', 'length', 'length_is',
  'linebreaks', 'linebreaksbr', 'linenumbers', 'ljust', 'lower', 'make_list',
  'phone2numeric', 'pluralize', 'pprint', 'random', 'removetags', 'rjust', 'safe',
  'safeseq', 'slice', 'slugify', 'stringformat', 'striptags', 'time', 'timesince',
  'timeuntil', 'title', 'truncatewords', 'truncatewords_html', 'unordered_list',
  'upper', 'urlencode', 'urlize', 'urlizetrunc', 'wordcount', 'wordwrap', 'yesno'
]

# Custom libraries to add to builtins
extra_libraries = [
]

def get_safe_template(tags=None, filters=None, extra=None):
  """
  Cleans the builtin template libraries before running the function (restoring
  the builtins afterwards).

  Removes any builtin tags and filters that are not enumerated in `tags` and
  `filters`, and adds the extra library modules in `extra` to the builtins.

  Does not catch any template exceptions (notably, TemplateSyntaxError and
  TemplateDoesNotExist may be raised).

  See http://djangosnippets.org/snippets/2750/ for more info on this snippet.
  """
  def decorate(func):
    @wraps(func)
    def wrapped(*args, **kwargs):
      # Clean out default libraries
      # Note: template.builtins is merely a convenience import, we have to work
      # with template.base.builtins for this to work right.
      template.base.builtins, default_libs = [], template.base.builtins
      try:
        # Construct new builtin with only whitelisted tags/filters
        whitelist = template.Library()
        for lib in default_libs:
          for tag in lib.tags:
            if tag in tags:
              whitelist.tags[tag] = lib.tags[tag]
          for filter in lib.filters:
            if filter in filters:
              whitelist.filters[filter] = lib.filters[filter]

        # Install whitelist library and extras as builtins
        template.base.builtins.append(whitelist)
        [template.add_to_builtins(e) for e in extra]

        return func(*args, **kwargs)
      finally:
        # Restore the builtins to their former defaults
        template.base.builtins = default_libs
    return wrapped

  if callable(tags):
    # @use_safe_templates
    func = tags
    tags = whitelist_tags
    filters = whitelist_filters
    extra = extra_libraries
    return decorate(func)
  else:
    # @use_safe_templates(...)
    tags = tags or whitelist_tags
    filters = filters or whitelist_filters
    extra = extra or extra_libraries
    return decorate
