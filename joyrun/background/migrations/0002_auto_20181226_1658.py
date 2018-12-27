# Generated by Django 2.1.4 on 2018-12-26 16:58

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('background', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='moduleinfo',
            name='folder_path',
            field=models.CharField(default='default', max_length=120, verbose_name='模块路径'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='projectinfo',
            name='root_path',
            field=models.CharField(default='default', max_length=120, verbose_name='项目路径'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='testcaseinfo',
            name='file_path',
            field=models.CharField(default='default', max_length=120, verbose_name='用例文件路径'),
            preserve_default=False,
        ),
    ]