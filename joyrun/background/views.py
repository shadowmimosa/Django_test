import logging
from django.shortcuts import render

from django.http import HttpResponse, HttpResponseRedirect

from background.models import UserInfo

logger = logging.getLogger()


def login(request):
    """
    登录
    :param request:
    :return:
    """
    if request.method == 'POST':
        username = request.POST.get('account')
        password = request.POST.get('password')

        if UserInfo.objects.filter(username__exact=username).filter(
                password__exact=password).count() == 1:
            logger.info('{username} 登录成功'.format(username=username))
            request.session["login_status"] = True
            request.session["now_account"] = username
            return HttpResponseRedirect('/index/')
        else:
            logger.info(
                '{username} 登录失败, 请检查用户名或者密码'.format(username=username))
            request.session["login_status"] = False
            return render(request, "background/login.html")
    elif request.method == 'GET':
        return render(request, "background/login.html")


def index(request):
    """
    首页
    :param request:
    :return:
    """
    # project_length = ProjectInfo.objects.count()
    # module_length = ModuleInfo.objects.count()
    # test_length = TestCaseInfo.objects.filter(type__exact=1).count()
    # suite_length = TestSuite.objects.count()

    # total = get_total_values()
    # manage_info = {
    #     'project_length': project_length,
    #     'module_length': module_length,
    #     'test_length': test_length,
    #     'suite_length': suite_length,
    #     'account': request.session["now_account"],
    #     'total': total
    # }

    # init_filter_session(request)
    # return render(request, 'background/base.html')
    return render(request, 'background/index.html')

def image(request):
    
    return render(request,'background/image.html')
