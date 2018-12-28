from django.core.mail import send_mail
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.shortcuts import render_to_response
from django.http import HttpResponse
from contact.forms import *
from django import forms

def contact(request):
    if request.method == 'POST':
        form = ContactForm(request.POST)
        if form.is_valid():
            cd = form.cleaned_data
            send_mail(
                cd['subject'],
                cd['message'],
                cd.get('email', 'noreply@example.com'),
                ['siteowner@example.com'],
            )
            return HttpResponseRedirect('/contact/thanks/')
    else:
        form = ContactForm(initial={'subject': 'I love your site!'})
    return render_to_response('contact_form.html', {'form': form})


def testform(request):
    if request.method == 'POST':
        form = TestForm(request.POST)
        if form.is_valid():
            cd = form.cleaned_data
            check_box_list = request.POST.getlist('testsuite')
            import sys
            #sys.stdout.write(form['testsuite'].data)
            for i in range(3):
                render_to_response('test_form.html', {'form': form, "debuglog": form['testsuite'].value}) 
    else:
        form = TestForm(initial={"testsuite": ["Test Case1"], "labs": "nbi3gc"})
    return render_to_response('test_form.html', {'form': form}) 
