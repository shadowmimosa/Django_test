from django.contrib import admin

# Register your models here.
from models import *

class TestCaseAdmin(admin.ModelAdmin):
    list_display = ('name', 'parent', 'status', 'pass_num', 'fail_num', 'fail_round', 'elapsedtime')
    search_fields = ('name', 'parent', 'status')

class TestSuiteAdmin(admin.ModelAdmin):
    list_display = ('name', 'status', 'total_run', 'pass_num', 'fail_num', 'fail_round', 'elapsedtime')
    search_fields = ('name',)

class SummaryAdmin(admin.ModelAdmin):
    list_display = ('test_round', 'pass_num', 'fail_num', 'starttime', 'endtime', 'elapsedtime', 'reportfile', 'outputfile')
    search_fields = ('test_round',)

class TestLabAdmin(admin.ModelAdmin):
    list_display = ('name', 'variablefile')
    search_fields = ('name',)

class TestSiteAdmin(admin.ModelAdmin):
    list_display = ('name', 'path', 'pythonpath')
    search_fields = ('name',)
    
admin.site.register(TestCase, TestCaseAdmin)
admin.site.register(TestSuite, TestSuiteAdmin)
admin.site.register(Summary, SummaryAdmin)
admin.site.register(TestLab, TestLabAdmin)
admin.site.register(TestSite, TestSiteAdmin)
