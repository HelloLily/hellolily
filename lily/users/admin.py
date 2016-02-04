from django.contrib import admin

from .models import LilyUser, LilyGroup


class LilyUserAdmin(admin.ModelAdmin):

    def save_model(self, request, obj, form, change):
        """
        Override saving LilyUser model in Django Admin to use password encryption.
        """

        if change:
            # Updating existing user.
            orig_obj = LilyUser.objects.get(pk=obj.pk)
            if obj.password != orig_obj.password:
                obj.set_password(obj.password)
        else:
            # Creating new user.
            obj.set_password(obj.password)

        obj.save()


admin.site.register(LilyUser, LilyUserAdmin)
admin.site.register(LilyGroup)
