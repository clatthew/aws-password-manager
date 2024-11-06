from src.password_manager import PasswordManager
from pytest import mark, fixture
from unittest.mock import patch
from mypy_boto3_ssm.client import SSMClient
from boto3 import client
from moto import mock_aws
from os import environ

PATCH_PATH = "src.password_manager."


@fixture(scope="session", autouse=True)
def aws_creds():
    environ["AWS_ACCESS_KEY_ID"] = "test"
    environ["AWS_SECRET_ACCESS_KEY"] = "test"
    environ["AWS_SECURITY_TOKEN"] = "test"
    environ["AWS_SESSION_TOKEN"] = "test"
    environ["AWS_DEFAULT_REGION"] = "eu-west-2"


@fixture
def test_pm():
    return PasswordManager()


class Testmain_loop:
    @mark.it("Calls authentication function when first run")
    def test_1(self, test_pm):
        with patch(f"{PATCH_PATH}input", return_value="x"):
            with patch(
                f"{PATCH_PATH}PasswordManager.authentication", return_value=True
            ) as mock_auth:
                test_pm()
                mock_auth.assert_called_once

    @mark.it("Calls authentication function repeatedly until it returns True")
    def test_4(self, test_pm):
        with patch(f"{PATCH_PATH}input", return_value="x"):
            with patch(f"{PATCH_PATH}PasswordManager.authentication") as mock_auth:
                mock_auth.side_effect = [False, False, False, True]
                test_pm()
                assert mock_auth.call_count == 4


class Testmenu:
    # Add a test for exit exiting the loop?
    @mark.it("Menu function displays correct options message")
    def test_intro_message(self, capfd, test_pm):
        with patch(f"{PATCH_PATH}input", return_value="x"):
            test_pm.menu()
        captured = capfd.readouterr()
        expected = (
            "Please specify [e]ntry, [r]etrieval, [d]eletion, [l]isting or e[x]it:"
        )
        result = captured.out[: len(expected)]
        assert result == expected

    @mark.it(
        "Entering invalid input causes next options message to begin with Invalid input."
    )
    def test_invalid(self, capfd, test_pm):
        with patch(f"{PATCH_PATH}input", return_value="y"):
            test_pm.menu()
        with patch(f"{PATCH_PATH}input", return_value="x"):
            test_pm.menu()
        captured = capfd.readouterr()
        std_message = (
            "Please specify [e]ntry, [r]etrieval, [d]eletion, [l]isting or e[x]it:"
        )
        add_message = "Invalid input. "
        expected = add_message + std_message
        result = captured.out[len(std_message) + 1 : len(std_message + expected) + 1]
        assert result == expected

    @mark.it("Entering input e, r, d, l or x calls the respective function:")
    @mark.parametrize(
        "option,func_name",
        [
            ("e", "entry"),
            ("r", "retrieval"),
            ("d", "deletion"),
            ("l", "listing"),
            ("x", "exit"),
        ],
    )
    def test_inputs(self, option, func_name, test_pm):
        with patch(f"{PATCH_PATH}input", return_value=option):
            with patch(f"{PATCH_PATH}PasswordManager.{func_name}") as mock:
                test_pm.menu()
                mock.assert_called_once()


class Testentry:
    pass


class Testretrieval:
    pass


class Testdeletion:
    pass


class Testlisting:
    pass


class Testexit:
    @mark.it("Sets self.running to False when called")
    def test_1(self, test_pm):
        test_pm.running = True
        test_pm.exit()
        assert not test_pm.running

    @mark.it('Echoes "Thank you. Goodbye." to terminal')
    def test_2(self, capfd, test_pm):
        test_pm.exit()
        captured = capfd.readouterr().out
        assert captured == "Thank you. Goodbye.\n"


class Testauthentication:
    pass


class Testcheck_credentials:
    pass


class Testget_secret_ids:
    @fixture
    def ssm_client(self):
        return client("ssm", environ["AWS_DEFAULT_REGION"])

    @mock_aws
    @mark.it("Returns names of parameters added to SSM")
    def test_1(self, ssm_client, test_pm):
        ssm_dir = "/passwordmgr/"
        test_passwords = [
            {
                "Name": f"{ssm_dir}secret_password",
                "Value": "matthew",
                "Type": "String",
                "Overwrite": True,
            },
            {
                "Name": f"{ssm_dir}secreter_password",
                "Value": "matthewer",
                "Type": "String",
                "Overwrite": True,
            },
        ]
        for password in test_passwords:
            ssm_client.put_parameter(**password)
        with patch.object(test_pm, "ssm_client", ssm_client):
            result = test_pm.get_secret_ids()
        assert result == ["secret_password", "secreter_password"]

    @mock_aws
    @mark.it("Returns empty list if no parameters have been added to SSM")
    def test_2(self, ssm_client, test_pm):
        with patch.object(test_pm, "ssm_client", ssm_client):
            result = test_pm.get_secret_ids()
        assert result == []


class Testssm_client:
    @mark.xfail
    @mock_aws
    @mark.it("Returns instance of boto3 client")
    def test_1(self):
        print(type(test_pm.ssm_client))
        assert isinstance(test_pm.ssm_client(), SSMClient)
