# Copyright 2023 Avaiga Private Limited
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may not use this file except in compliance with
# the License. You may obtain a copy of the License at
#
#        http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on
# an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the
# specific language governing permissions and limitations under the License.

import os
import subprocess
import sys

from cookiecutter.main import cookiecutter


def _run_template(main_path, time_out=30):
    """Run the templates on a subprocess and get stdout after timeout"""
    with subprocess.Popen([sys.executable, main_path], stdout=subprocess.PIPE, stderr=subprocess.PIPE) as proc:
        try:
            stdout, stderr = proc.communicate(timeout=time_out)
        except subprocess.TimeoutExpired:
            proc.kill()
            stdout, stderr = proc.communicate()

    # Print the eror if there is any (for debugging)
    if stderr := str(stderr, "utf-8"):
        print(stderr)

    return stdout


def test_default_template(tmpdir):
    cookiecutter(
        template="src/taipy/templates/taipy-default-template",
        output_dir=str(tmpdir),
        no_input=True,
        extra_context={
            "application_name": "foo_app",
            "application_main_file": "main.py",
            "application_title": "bar",
        },
    )

    assert os.listdir(tmpdir) == ["foo_app"]
    assert os.listdir(os.path.join(tmpdir, "foo_app")).sort() == ["requirements.txt", "main.py", "images"].sort()
    with open(os.path.join(tmpdir, "foo_app", "requirements.txt")) as requirements_file:
        # Assert post_gen_project hook is successful
        assert "taipy==" in requirements_file.read()

    stdout = _run_template(os.path.join(tmpdir, "foo_app", "main.py"))

    # Assert the message when the application is run successfully is in the stdout
    assert "[Taipy][INFO]  * Server starting on" in str(stdout, "utf-8")


def test_multi_page_gui_template(tmpdir):
    cookiecutter(
        template="src/taipy/templates/multi-page-gui",
        output_dir=str(tmpdir),
        no_input=True,
        extra_context={
            "application_name": "foo_app",
            "application_main_file": "main.py",
            "application_title": "bar",
        },
    )

    assert os.listdir(tmpdir) == ["foo_app"]
    assert os.listdir(os.path.join(tmpdir, "foo_app")).sort() == ["requirements.txt", "main.py", "pages"].sort()
    with open(os.path.join(tmpdir, "foo_app", "requirements.txt")) as requirements_file:
        # Assert post_gen_project hook is successful
        assert "taipy==" in requirements_file.read()

    stdout = _run_template(os.path.join(tmpdir, "foo_app", "main.py"))

    # Assert the message when the application is run successfully is in the stdout
    assert "[Taipy][INFO]  * Server starting on" in str(stdout, "utf-8")


def test_scenario_management_with_toml_config(tmpdir):
    cookiecutter(
        template="src/taipy/templates/scenario-management",
        output_dir=tmpdir,
        no_input=True,
        extra_context={
            "Your application root folder name": "foo_app",
            "Your application main Python file": "main.py",
            "Your application title": "bar",
            "Use TOML Config": "yes",
        },
    )

    assert os.listdir(tmpdir) == ["foo_app"]
    assert (
        os.listdir(os.path.join(tmpdir, "foo_app")).sort()
        == ["requirements.txt", "main.py", "algos", "config", "pages"].sort()
    )

    # Assert post_gen_project hook is successful
    with open(os.path.join(tmpdir, "foo_app", "requirements.txt")) as requirements_file:
        assert "taipy==" in requirements_file.read()
    assert (
        os.listdir(os.path.join(tmpdir, "foo_app", "config")).sort()
        == ["__init__.py", "config.py", "config.toml"].sort()
    )
    with open(os.path.join(tmpdir, "foo_app", "config", "config.py")) as config_file:
        assert 'Config.load("config/config.toml")' in config_file.read()

    oldpwd = os.getcwd()
    os.chdir(os.path.join(tmpdir, "foo_app"))
    stdout = _run_template("main.py")
    os.chdir(oldpwd)

    # Assert the message when the application is run successfully is in the stdout
    assert "[Taipy][INFO] Configuration 'config/config.toml' successfully loaded." in str(stdout, "utf-8")
    assert "[Taipy][INFO]  * Server starting on" in str(stdout, "utf-8")


def test_scenario_management_without_toml_config(tmpdir):
    cookiecutter(
        template="src/taipy/templates/scenario-management",
        output_dir=tmpdir,
        no_input=True,
        extra_context={
            "Your application root folder name": "foo_app",
            "Your application main Python file": "main.py",
            "Your application title": "bar",
            "Use TOML Config": "no",
        },
    )

    assert os.listdir(tmpdir) == ["foo_app"]
    assert (
        os.listdir(os.path.join(tmpdir, "foo_app")).sort()
        == ["requirements.txt", "main.py", "algos", "config", "pages"].sort()
    )

    # Assert post_gen_project hook is successful
    with open(os.path.join(tmpdir, "foo_app", "requirements.txt")) as requirements_file:
        assert "taipy==" in requirements_file.read()
    assert os.listdir(os.path.join(tmpdir, "foo_app", "config")).sort() == ["__init__.py", "config.py"].sort()
    with open(os.path.join(tmpdir, "foo_app", "config", "config.py")) as config_file:
        config_content = config_file.read()
        assert 'Config.load("config/config.toml")' not in config_content
        assert all([x in config_content for x in ["Config.configure_csv_data_node", "Config.configure_task"]])

    oldpwd = os.getcwd()
    os.chdir(os.path.join(tmpdir, "foo_app"))
    stdout = _run_template("main.py")
    os.chdir(oldpwd)

    # Assert the message when the application is run successfully is in the stdout
    assert "[Taipy][INFO]  * Server starting on" in str(stdout, "utf-8")
