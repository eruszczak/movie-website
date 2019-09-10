from django.contrib import admin
from django.contrib.auth import get_user_model


# class UserAdmin(admin.ModelAdmin):
#
#     def get_queryset(self, request):
#         return super().get_queryset(request).prefetch_related('content_type')


admin.site.register(get_user_model())
