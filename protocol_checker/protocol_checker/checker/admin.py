from django.contrib import admin

# Register your models here.

from .models import *

admin.site.register(Request)
admin.site.register(SuccessResponse)
admin.site.register(FailResponse)

admin.site.register(Config)
admin.site.register(TestConfig)

# admin.site.register(CurrentTest)
# admin.site.register(CompletedTest)
# admin.site.register(CheckingProcedure)
