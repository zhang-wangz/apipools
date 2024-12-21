# -*- coding: utf-8 -*-

import click
from helper.launcher import startServer, startScheduler
from setting import VERSION

CONTEXT_SETTINGS = dict(help_option_names=['-h', '--help'])


@click.group(context_settings=CONTEXT_SETTINGS)
@click.version_option(version=VERSION)
def cli():
    """ProxyPool cli工具"""


@cli.command(name="schedule")
def schedule():
    """ 启动调度程序 """
    startScheduler()


@cli.command(name="server")
def server():
    """ 启动api服务 """
    startServer()


if __name__ == '__main__':
    cli()
