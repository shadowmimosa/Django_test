from django.db import models


class BaseTable(models.Model):
    create_time = models.DateTimeField('创建时间', auto_now_add=True)
    update_time = models.DateTimeField('更新时间', auto_now=True)

    class Meta:
        abstract = True
        verbose_name = "公共字段表"
        db_table = "BaseTable"


class UserInfo(BaseTable):
    class Meta:
        verbose_name = '用户信息'
        db_table = 'UserInfo'

    username = models.CharField('用户名', max_length=20, unique=True, null=False)
    password = models.CharField('密码', max_length=20, null=False)
    email = models.EmailField('邮箱', null=False, unique=True)
    status = models.IntegerField('有效/无效', default=1)


class TestCaseInfo(BaseTable):
    class Meta:
        verbose_name = "用例信息"
        db_table = 'TestCaseInfo'

    type = models.IntegerField('test/comfig', default=1)
    name = models.CharField('用例/配置名称', max_length=50, null=False)
    # belong_module = models.ForeignKey(ModuleInfo, on_delete=models.CASCADE)
    belong_project = models.CharField('所属项目', max_length=50, null=False)
    include = models.CharField('前置config/test', max_length=1024, null=False)
    author = models.CharField('编写人员', max_length=20, null=False)
    request = models.TextField('请求信息', null=False)


class TestReports(BaseTable):
    class Meta:
        verbose_name = "测试报告"
        db_table = 'TestReports'

    report_name = models.CharField(max_length=40, null=False)
    start_at = models.CharField(max_length=40, null=True)
    status = models.BooleanField()
    testsRun = models.IntegerField()
    successes = models.IntegerField()
    reports = models.TextField()
