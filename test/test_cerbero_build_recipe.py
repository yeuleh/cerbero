# cerbero - a multi-platform build system for Open Source software
# Copyright (C) 2012 Andoni Morales Alastruey <ylatuya@gmail.com>
#
# This library is free software; you can redistribute it and/or
# modify it under the terms of the GNU Library General Public
# License as published by the Free Software Foundation; either
# version 2 of the License, or (at your option) any later version.
#
# This library is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# Library General Public License for more details.
#
# You should have received a copy of the GNU Library General Public
# License along with this library; if not, write to the
# Free Software Foundation, Inc., 59 Temple Place - Suite 330,
# Boston, MA 02111-1307, USA.

import unittest
import os

from cerbero.build import recipe
from cerbero.config import Platform, License
from test.test_common import DummyConfig


class Class1(object):

    test = None

    def __init__(self):
        self.test = 'CODEPASS'

    class1_method = lambda x: None
    compile = lambda x: 'CODEPASS'


class Class2(object):

    class2_method = lambda x: None
    fetch = lambda x: 'CODEPASS'


class RecipeTest(recipe.Recipe):

    btype = Class1
    stype = Class2

    name = 'recipe'
    version = '0.0.0'
    licenses = [License.LGPL]
    deps = ['dep1', 'dep2']
    platform_deps = {Platform.LINUX: ['dep3'], Platform.WINDOWS: ['dep4']}
    post_install = lambda x: 'CODEPASS'

    files_libs = ['librecipe-test']
    files_bins = ['recipe-test']
    files_bins_licenses = [License.GPL]
    platform_files_test = {Platform.LINUX: ['test1']}
    platform_files_test_licenses = {Platform.LINUX: [License.BSD]}


class TestReceiptMetaClass(unittest.TestCase):

    def setUp(self):
        self.config = DummyConfig()
        self.config.local_sources = ''
        self.config.sources = ''
        self.t = RecipeTest(self.config)

    def testReceiptBases(self):
        r = recipe.Recipe(self.config)
        bases = r.__class__.mro()
        self.assertTrue(Class1 not in bases)
        self.assertTrue(Class2 not in bases)

    def testReceiptSubclassBases(self):
        bases = self.t.__class__.mro()
        self.assertTrue(Class1 in bases)
        self.assertTrue(Class2 in bases)

    def testFunctions(self):
        self.assertTrue(hasattr(self.t, 'class1_method'))
        self.assertTrue(hasattr(self.t, 'class2_method'))
        self.assertEquals(self.t.fetch(), 'CODEPASS')
        self.assertEquals(self.t.compile(), 'CODEPASS')
        self.assertEquals(self.t.post_install(), 'CODEPASS')

    def testSubclassesInit(self):
        self.assertEquals(self.t.test, 'CODEPASS')


class TestReceipt(unittest.TestCase):

    def setUp(self):
        self.config = DummyConfig()
        self.config.local_sources = 'path1'
        self.config.sources = 'path2'
        self.recipe = RecipeTest(self.config)

    def testSources(self):
        repo_dir = os.path.join(self.config.local_sources, self.recipe.package_name)
        repo_dir = os.path.abspath(repo_dir)
        build_dir = os.path.join(self.config.sources, self.recipe.package_name)
        build_dir = os.path.abspath(build_dir)

        self.assertEquals(self.recipe.repo_dir, repo_dir)
        self.assertEquals(self.recipe.build_dir, build_dir)

    def testListDeps(self):
        self.recipe.config.target_platform = Platform.LINUX
        self.assertEquals(['dep1', 'dep2', 'dep3'], self.recipe.list_deps())
        self.recipe.config.target_platform = Platform.WINDOWS
        self.assertEquals(['dep1', 'dep2', 'dep4'], self.recipe.list_deps())

    def testRemoveSteps(self):
        self.recipe._remove_steps(['donotexits'])
        self.assertTrue(recipe.BuildSteps.FETCH in self.recipe._steps)
        self.recipe._remove_steps([recipe.BuildSteps.FETCH])
        self.assertTrue(recipe.BuildSteps.FETCH not in self.recipe._steps)
        r = RecipeTest(self.config)
        self.assertTrue(recipe.BuildSteps.FETCH in r._steps)


class TestLicenses(unittest.TestCase):

    def setUp(self):
        self.config = DummyConfig()
        self.config.local_sources = ''
        self.config.sources = ''
        self.recipe = RecipeTest(self.config)

    def testLicenses(self):
        self.assertEquals(self.recipe.licenses, [License.LGPL])

        licenses_libs = self.recipe.list_licenses_by_categories(['libs'])
        self.assertEquals(licenses_libs['libs'], [License.LGPL])
        self.assertEquals(licenses_libs.values(), [[License.LGPL]])
        licenses_bins = self.recipe.list_licenses_by_categories(['bins'])
        self.assertEquals(licenses_bins['bins'], [License.GPL])
        self.assertEquals(licenses_bins.values(), [[License.GPL]])

        self.recipe.platform = Platform.LINUX
        self.recipe.config.target_platform = Platform.LINUX
        licenses_test = self.recipe.list_licenses_by_categories(['test'])
        self.assertEquals(licenses_test['test'], [License.BSD])
        self.assertEquals(licenses_test.values(), [[License.BSD]])
