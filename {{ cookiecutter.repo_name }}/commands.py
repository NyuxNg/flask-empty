# -*- coding:utf-8 -*-

from flask.ext.script import Command, Option, prompt_bool

import os


class CreateDB(Command):
    """
    Creates database using SQLAlchemy
    """

    def run(self):
        try:
            from database import create_all

            create_all()
        except ImportError:
            print("Please, make sure database.create_all exists in order to create a db.")


class DropDB(Command):
    """
    Drops database using SQLAlchemy
    """

    def run(self):
        try:
            from database import drop_all

            drop_all()
        except ImportError:
            print("Please, make sure database.drop_all exists in order to drop a db.")


class NewApp(Command):
    """
    Command to easily add a new app to your project
    """
    def get_options(self):
        return [
            Option('name', type=str),
        ]

    def run(self, name):
        APPS_FOLDER = 'apps'
        if os.path.exists(os.path.join(APPS_FOLDER, name)):
            print('App name already exists at apps. Exiting.')

        app_path = os.path.join(APPS_FOLDER, name)
        os.mkdir(app_path)
        os.mkdir(os.path.join(app_path, 'templates'))
        os.mkdir(os.path.join(app_path, 'templates', 'name'))

        # empty __init__.py
        with open(os.path.join(app_path, '__init__.py'), 'w'):
            pass

        with open(os.path.join(app_path, 'models.py'), 'w'):
            pass

        with open(os.path.join(app_path, 'forms.py'), 'w'):
            pass

        with open(os.path.join(app_path, 'views.py'), 'w') as file:
            file.write(""
                "from flask import Blueprint\n"
                "from flask import render_template, flash, redirect, url_for\n\n"
                "app = Blueprint('%(name)s', __name__, template_folder='templates')"
                % {'name': name}
            )


class Test(Command):
    """
    Run tests
    """

    verbosity = 2
    failfast = False

    def get_options(self):
        return [
            Option('--verbosity', '-v', dest='verbose',
                    type=int, default=self.verbosity),
            Option('--failfast', dest='failfast',
                    default=self.failfast, action='store_false')
        ]

    def run(self, verbosity, failfast):
        import sys
        import glob
        import unittest

        exists = os.path.exists
        isdir = os.path.isdir
        join = os.path.join

        project_path = os.path.abspath(os.path.dirname('.'))
        sys.path.insert(0, project_path)

        # our special folder for blueprints
        if exists('apps'):
            sys.path.insert(0, join('apps'))

        loader = unittest.TestLoader()
        all_tests = []

        if exists('apps'):
            for path in glob.glob('apps/*'):
                if isdir(path):
                    tests_dir = join(path, 'tests')

                    if exists(join(path, 'tests.py')):
                        all_tests.append(loader.discover(path, 'tests.py'))
                    elif exists(tests_dir):
                        all_tests.append(loader.discover(tests_dir, pattern='test*.py'))

        if exists('tests') and isdir('tests'):
            all_tests.append(loader.discover('tests', pattern='test*.py'))
        elif exists('tests.py'):
            all_tests.append(loader.discover('.', pattern='tests.py'))

        test_suite = unittest.TestSuite(all_tests)
        unittest.TextTestRunner(
            verbosity=verbosity, failfast=failfast).run(test_suite)
