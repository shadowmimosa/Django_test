from models import *

class TestLabChoiceForm(forms.Form):
    labs_db = TestLab.objects.all()
    LABS = []
    for index, lab in enumerate(labs_db):
        lab_item = (lab.name, lab.name)
        LABS.append(lab_item)
    labs = forms.ChoiceField(choices= LABS, widget=forms.RadioSelect())


class TestSiteChoiceForm(forms.Form):
    sites_db = TestSite.objects.all()
    SITES = []
    for index, site in enumerate(sites_db):
        site_item = (site.name, "%s (%s)" % (site.name, site.path))
        SITES.append(site_item)
    sites = forms.ChoiceField(choices= SITES, widget=forms.RadioSelect())

class TestCaseTableForm(ModelForm):
    class Meta:
        model = TestCase
        fields = ('name','parent','status','pass_num','fail_num','fail_round', 'elapsedtime')
        
    def __init__(self, *args, **kwargs):
        super(TestCaseTableForm, self).__init__(*args, **kwargs)
        """
        self.fields['name'].widget.attrs.update({'style' : 'border:1px dashed #ccc;'})
        for v in self.fields:
            self.fields[v].widget.attrs['class'] = 'text ui-widget-content ui-corner-all'
        """
    
class TestSuiteTableForm(ModelForm):
    class Meta:
        model = TestSuite
        fields = ('name','status','total_run','pass_num','fail_num','fail_round', 'elapsedtime')
        
    def __init__(self, *args, **kwargs):
        super(TestSuiteTableForm, self).__init__(*args, **kwargs)
