from django import forms
from django.utils.encoding import force_unicode

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
                
        return super(JqueryPasswordInput, self).render(name, value, final_attrs)