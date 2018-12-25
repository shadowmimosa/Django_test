import os
from .operation import add_project_data
from ..models import ProjectInfo, ModuleInfo, TestCaseInfo


def get_testcase(path):
    Json_D = {}

    if '/' in path:
        path.replace('/', '\\')
    foldername = path.split('\\')[-1]

    Json_D[foldername] = {}

    for root, dirs, files in os.walk(path):

        root_folder = root.split('\\')[-1]

        if root == path:
            for index in dirs:
                if 'git' not in index:
                    Json_D[foldername][index] = {}

        elif len(root) > len(path):
            if root_folder in Json_D[foldername].keys():
                Json_D[foldername][root_folder] = files

    return (Json_D)


def initial_testcase(path):
    tests_all = get_testcase(path)
    for key in tests_all:
        if ProjectInfo.objects.get_pro_name(key) < 1:
            ProjectInfo.objects.insert_project(
                project_name=key,
                submitted_personnel='Admin',
                simple_desc='接口测试项目')

        pro = ProjectInfo.objects.get(project_name=key)
        for keys, values in tests_all[key].items():
            if ModuleInfo.objects.get_module_name(keys) < 1:
                ModuleInfo.objects.insert_module(
                    module_name=keys,
                    test_user='Admin',
                    simple_desc='该模块测试用例集合',
                    belong_project=pro)
            mod = ModuleInfo.objects.get(module_name=keys)
            for index in values:
                if TestCaseInfo.objects.filter(belong_project=pro.id).filter(
                        belong_module_id=mod).filter(name=index).count(
                        ) < 1 and 'init' not in index and 'git' not in index:
                    TestCaseInfo.objects.create(
                        name=index,
                        belong_project=pro.id,
                        author='Admin',
                        request='default',
                        belong_module=mod)


def project_info_logic(type=True, **kwargs):
    """
    项目信息逻辑处理
    :param type: boolean:True 默认新增项目
    :param kwargs: dict: 项目信息
    :return:
    """
    if kwargs.get('project_name') is '':
        return '项目名称不能为空'
    if kwargs.get('responsible_name') is '':
        return '负责人不能为空'
    if kwargs.get('test_user') is '':
        return '测试人员不能为空'
    if kwargs.get('dev_user') is '':
        return '开发人员不能为空'
    if kwargs.get('publish_app') is '':
        return '发布应用不能为空'

    return add_project_data(type, **kwargs)