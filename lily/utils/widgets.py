from django import forms
from django.utils.encoding import force_unicode
from django.utils.safestring import mark_safe
from django.utils.translation import ugettext as _

class JqueryPasswordInput(forms.PasswordInput):
    class Media:
        js = ('plugins/jquerypasswordstrength/jquery.password_strength.js',)

    def render(self, name, value, attrs=None):
        if value is None:
            value = ''
        final_attrs = self.build_attrs(attrs, type=self.input_type, name=name)
        if value != '':
            # Only add the 'value' attribute if a value is non-empty.
            final_attrs['value'] = force_unicode(self._format_value(value))
            
        if final_attrs.has_key('class'):
            final_attrs['class'] = final_attrs['class'] + ' jquery-password' 
        else:
            final_attrs.update({'class': 'jquery-password'})
                
        output = super(JqueryPasswordInput, self).render(name, value, final_attrs)
        password_checker = u'''
            <div class="password-checker">
               <div class="password-background"><span id="%(strength)s"
            class="password_strength">&nbsp;</span></div>
               <div id="%(text)s" class="password-text">&nbsp;</div>
            </div>
            <script type="text/javascript" language="javascript">
               $(document).ready(function() {
                   $('#id_%(name)s').password_strength({
                       'minLength':6,
                       'container':'#%(strength)s',
                       'textContainer':'#%(text)s',
                       'texts' : {
                           1 : '%(too_weak)s',
                           2 : '%(weak_password)s',
                           3 : '%(normal_strength)s',
                           4 : '%(strong_password)s',
                           5 : '%(ultimate_password)s'
                       }});
                   $('#id_%(name)s').keyup();
               });
            </script>''' % {'name': name, 'strength': name+'-strength', 'text': name+'-text',
               'too_weak': _('Too weak'), 'weak_password': _('Weak password'),
               'normal_strength': _('Normal strength'), 'strong_password': _('Strong password'),
               'ultimate_password': _('Very good password')}
#        return mark_safe(u'%s%s' % (output, password_checker))
        return mark_safe(u'%s' % (output))