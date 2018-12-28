from django import forms
import random
class ContactForm(forms.Form):
    subject = forms.CharField(max_length=100)
    email = forms.EmailField(required=False, label='Your e-mail address')
    message = forms.CharField(widget=forms.Textarea)

    def clean_message(self):
        message = self.cleaned_data['message']
        num_words = len(message.split())
        if num_words < 4:
            raise forms.ValidationError("Not enough words!")
        return message


class TestForm(forms.Form): 
    ACTIVITY_STYLE = (("Test Case1", "Test Case%s" % random.randint(0,20)), ("Test Case2", "Test Case%s" % random.randint(0,20)), ("Test Case3", "Test Case%s" % random.randint(0,20)))    
    testsuite = forms.MultipleChoiceField(label=u'Test Suite1', choices=ACTIVITY_STYLE, widget=forms.CheckboxSelectMultiple())
    labs = forms.ChoiceField(choices=[('nbi3gc','NBI3GC'),('ascii','ASCII')])

    
