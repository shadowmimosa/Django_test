from django.http import HttpResponse

# # don't need this, if we use the render()
# from django.template import loader
from django.http import Http404
from django.shortcuts import render, get_object_or_404

from .models import Question


def index(request):
    # rewrite the view use the render()
    latest_question_list = Question.objects.order_by('-pub_date')[:5]
    context = {
        'latest_question_list': latest_question_list,
    }
    return render(request, 'polls/index.html', context)

    # # try view with models
    # latest_question_list = Question.objects.order_by('-pub_date')[:5]
    # template = loader.get_template('polls/index.html')
    # context = {
    #     'latest_question_list': latest_question_list,
    # }
    # return HttpResponse(template.render(context, request))

    # # try HttpResponse again
    # latest_question_list=Question.objects.order_by('-pub_date')[:5]
    # output=', '.join([q.question_text for q in latest_question_list])
    # return HttpResponse(output)

    # # first try HttpResponse
    # return HttpResponse("Hello, world. You're at the polls index.")


def detail(request, question_id):
    question = get_object_or_404(Question, pk=question_id)

    # # replace this with the get_object_or_404()
    # try:
    #     question = Question.objects.get(pk=question_id)
    # except Question.DoesNotExist:
    #     raise Http404("Question does not exist")

    # replace it with the render()
    # return HttpResponse("You're looking at question %s." % question_id)

    return render(request, 'polls/detail.html', {'question': question})


def results(request, question_id):
    response = "You're looking at the results oof question %s."
    return HttpResponse(response % question_id)


def vote(request, question_id):
    return HttpResponse("You're voting on question %s." % question_id)
