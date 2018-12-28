from django.db import models
from django.forms import ModelForm
from django import forms

# Create your models here.
class TestCase(models.Model):
    name = models.CharField(max_length=50)
    parent = models.CharField(max_length=50)
    status = models.CharField(max_length=10, blank=True)
    fail_round = models.CharField(max_length=200, blank=True)
    pass_num = models.IntegerField(blank=True, null=True)
    fail_num = models.IntegerField(blank=True, null=True)
    elapsedtime = models.IntegerField(blank=True, null=True)
    
    def __unicode__(self):
        return self.name

    class Meta:
        ordering = ['parent']

class TestSuite(models.Model):
    name = models.CharField(max_length=50)
    status = models.CharField(max_length=10, blank=True)
    fail_round = models.CharField(max_length=200, blank=True)
    total_run = models.IntegerField(blank=True, null=True)
    pass_num = models.IntegerField(blank=True, null=True)
    fail_num = models.IntegerField(blank=True, null=True)
    elapsedtime = models.IntegerField(blank=True, null=True)
    
    def __unicode__(self):
        return self.name

    class Meta:
        ordering = ['name']

class Summary(models.Model):
    starttime = models.CharField(max_length=50, blank=True)
    endtime = models.CharField(max_length=50, blank=True)
    reportfile = models.CharField(max_length=100, blank=True)
    outputfile = models.CharField(max_length=100, blank=True)
    test_round = models.IntegerField(max_length=10, blank=True)
    pass_num = models.IntegerField(max_length=10, blank=True)
    fail_num = models.IntegerField(max_length=10, blank=True)
    elapsedtime = models.IntegerField(blank=True, null=True)
    
class TestLab(models.Model):
    name = models.CharField(max_length=50)
    variablefile = models.CharField(max_length=500, blank=True)
    
    def __unicode__(self):
        return self.name
    class Meta:
        ordering = ['name']

class TestSite(models.Model):
    name = models.CharField(max_length=50)
    path = models.CharField(max_length=100)
    pythonpath = models.CharField(max_length=500, blank=True)

    def __unicode__(self):
        return self.name
    class Meta:
        ordering = ['name']

