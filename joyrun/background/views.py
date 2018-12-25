import logging, json
from django.shortcuts import render

from django.http import HttpResponse, HttpResponseRedirect
from django.urls import reverse

from django.views.decorators.csrf import csrf_exempt

from background.models import UserInfo, ProjectInfo, ModuleInfo, TestCaseInfo, EnvInfo, TestReports, TestSuite
from .utils.operation import add_project_data, del_project_data
from .utils.common import project_info_logic, initial_testcase

logger = logging.getLogger()


def login_check(func):
    def wrapper(request, *args, **kwargs):
        if not request.session.get('login_status'):
            return HttpResponseRedirect(
                reverse('background:function', kwargs={'function': 'login'}))
        return func(request, *args, **kwargs)

    return wrapper


@csrf_exempt
def login(request):
    """
    登录
    :param request:
    :return:
    """
    if request.method == 'POST':
        account = request.POST.get('account')
        password = request.POST.get('password')

        if '@thejoyrun.com' in account:
            check_status = UserInfo.objects.filter(
                email__exact=account).filter(password__exact=password).count()
            account_type = 1
        else:
            check_status = UserInfo.objects.filter(
                username__exact=account).filter(
                    password__exact=password).count()
            account_type = 0

        if check_status == 1:
            logger.info('{username} 登录成功'.format(username=account))
            request.session["login_status"] = True
            if account_type == 1:
                account = UserInfo.objects.query_account(account, password)
            request.session["now_account"] = account
            return HttpResponseRedirect(
                reverse('background:function', kwargs={'function': 'index'}))

        logger.info('{username} 登录失败, 请检查用户名或者密码'.format(username=account))
        request.session["login_status"] = False
        msg = "用户名或密码错误！"
        ret = {"msg": msg}

        return render(request, "background/login.html", ret)
    if request.method == 'GET':
        return render(request, "background/login.html")


@login_check
def logout(request):
    """
    注销登录
    :param request:
    :return:
    """

    return HttpResponseRedirect(
        reverse(
            'background:function', kwargs={
                'function': 'login',
                'index': '2'
            }))
    if request.method == 'GET':
        logger.info(
            '{username}退出'.format(username=request.session['now_account']))
        try:
            del request.session['now_account']
            del request.session['login_status']
            init_filter_session(request, type=False)
        except KeyError:
            logging.error('session invalid')
        return HttpResponseRedirect(
            reverse('background:function', kwargs={'function': 'login'}))


@csrf_exempt
def register(request):
    """
    注册
    :param request:
    :return:
    """
    if request.method == 'POST' and False:
        msg = "注册还不能用哈哈哈！登录请 @ShadowMimosa."
        ret = {"msg": msg}
        return render(request, "background/register.html", ret)

    if request.method == 'POST':
        account = request.POST.get('account')
        email = request.POST.get('email')
        password = request.POST.get('password')
        repassword = request.POST.get('repassword')

        if UserInfo.objects.filter(username__exact=account).count():
            msg = "用户名已经注册！请尝试登陆或 @Shadowmimosa."
        elif UserInfo.objects.filter(email__exact=email).count():
            msg = "此邮箱已经注册！请尝试登陆或 @Shadowmimosa."
        elif '@thejoyrun.com' not in email:
            msg = "请使用工作邮箱！"
        elif password != repassword:
            msg = "两次输入的密码不相同！"
        else:
            UserInfo.objects.insert_user(account, password, email)
            request.session["login_status"] = True
            request.session["now_account"] = account
            return HttpResponseRedirect(
                reverse('background:function', kwargs={'function': 'index'}))
        ret = {"msg": msg}
        return render(request, "background/register.html", ret)
    elif request.method == 'GET':
        return render(request, "background/register.html")


@login_check
def index(request):
    """
    首页
    :param request:
    :return:
    """
    project_length = ProjectInfo.objects.count()
    module_length = ModuleInfo.objects.count()
    test_length = TestCaseInfo.objects.filter(type__exact=1).count()
    suite_length = TestSuite.objects.count()

    total = {
        'pass': [10, 20, 30, 40, 50, 60, 70, 80, 90, 100, 90, 60],
        'fail': [90, 80, 70, 60, 50, 40, 30, 20, 10, 0, 10, 40],
        'percent': [
            10.0, 20.0, 30.0, 40.0, 50.0, 60.0, 70.0, 80.0, 90.0, 100.0, 11.0,
            20.0
        ]
    }
    # total = get_total_values()

    manage_info = {
        'project_length': project_length,
        'module_length': module_length,
        'test_length': test_length,
        'suite_length': suite_length,
        'account': request.session["now_account"],
        'total': total
    }

    # init_filter_session(request)

    return render(request, 'background/index.html', manage_info)


@login_check
def project_list(request, id):
    """
    项目列表
    :param request:
    :param id: str or int：当前页
    :return:
    """

    account = request.session["now_account"]
    if request.is_ajax():
        project_info = json.loads(request.body.decode('utf-8'))
        if 'mode' in project_info.keys():
            msg = del_project_data(project_info.pop('id'))
        else:
            msg = project_info_logic(type=False, **project_info)
        return HttpResponse(get_ajax_msg(msg, 'ok'))
    else:
        filter_query = set_filter_session(request)
        pro_list = get_pager_info(ProjectInfo, filter_query,
                                  '/api/project_list/', id)
        manage_info = {
            'account': account,
            'project': pro_list[1],
            'page_list': pro_list[0],
            'info': filter_query,
            'sum': pro_list[2],
            'env': EnvInfo.objects.all().order_by('-create_time'),
            'project_all': ProjectInfo.objects.all().order_by('-update_time')
        }
        return render_to_response('project_list.html', manage_info)


@login_check
def module_list(request, id):
    """
    模块列表
    :param request:
    :param id: str or int：当前页
    :return:
    """
    account = request.session["now_account"]
    if request.is_ajax():
        module_info = json.loads(request.body.decode('utf-8'))
        if 'mode' in module_info.keys():  # del module
            msg = del_module_data(module_info.pop('id'))
        else:
            msg = module_info_logic(type=False, **module_info)
        return HttpResponse(get_ajax_msg(msg, 'ok'))
    else:
        filter_query = set_filter_session(request)
        module_list = get_pager_info(ModuleInfo, filter_query,
                                     '/api/module_list/', id)
        manage_info = {
            'account': account,
            'module': module_list[1],
            'page_list': module_list[0],
            'info': filter_query,
            'sum': module_list[2],
            'env': EnvInfo.objects.all().order_by('-create_time'),
            'project': ProjectInfo.objects.all().order_by('-update_time')
        }
        return render_to_response('module_list.html', manage_info)


@login_check
def test_list(request, id):
    """
    用例列表
    :param request:
    :param id: str or int：当前页
    :return:
    """

    account = request.session["now_account"]
    if request.is_ajax():
        test_info = json.loads(request.body.decode('utf-8'))

        if test_info.get('mode') == 'del':
            msg = del_test_data(test_info.pop('id'))
        elif test_info.get('mode') == 'copy':
            msg = copy_test_data(
                test_info.get('data').pop('index'),
                test_info.get('data').pop('name'))
        return HttpResponse(get_ajax_msg(msg, 'ok'))

    else:
        filter_query = set_filter_session(request)
        test_list = get_pager_info(TestCaseInfo, filter_query,
                                   '/api/test_list/', id)
        manage_info = {
            'account': account,
            'test': test_list[1],
            'page_list': test_list[0],
            'info': filter_query,
            'env': EnvInfo.objects.all().order_by('-create_time'),
            'project': ProjectInfo.objects.all().order_by('-update_time')
        }
        return render_to_response('test_list.html', manage_info)


def image(request):

    return HttpResponse("You're in my heart")
    return render(request, 'background/image.html')


def init_filter_session(request, type=True):
    """
    init session
    :param request:
    :return:
    """
    if type:
        request.session['user'] = ''
        request.session['name'] = ''
        request.session['project'] = 'All'
        request.session['module'] = '请选择'
        request.session['report_name'] = ''
    else:
        del request.session['user']
        del request.session['name']
        del request.session['project']
        del request.session['module']
        del request.session['report_name']


path = 'D:\\test\\JoyrunTestOA\\thejoyrunTestcode'
initial_testcase(path)
print("---> It's in initial database now.")
