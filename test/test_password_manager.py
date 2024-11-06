from src.password_manager import (
    main_loop,
    menu,
    entry,
    retrieval,
    deletion,
    listing,
    exit,
    authentication,
    check_credentials,
    get_secret_ids,
    ssm_client,
)
from pytest import mark, fixture
from unittest.mock import patch
from mypy_boto3_ssm.client import SSMClient
from boto3 import client
from moto import mock_aws
from os import environ

PATCH_PATH = "src.password_manager."


class Testmain_loop:
    @mark.it("Calls authentication function when first run")
    def test_1(self):
        with patch(f"{PATCH_PATH}menu", return_value=True):
            with patch(f"{PATCH_PATH}authentication") as mock:
                mock.return_value = True
                main_loop()
                mock.assert_called_once()

    @mark.it("Calls authentication function repeatedly until it returns True")
    def test_2(self):
        with patch(f"{PATCH_PATH}menu", return_value=True):
            with patch(f"{PATCH_PATH}authentication") as mock:
                mock.side_effect = [False, False, False, True]
                main_loop()
                assert mock.call_count == 4


class Testmenu:
    # Add a test for exit exiting the loop?
    @mark.it("Menu function displays correct options message")
    def test_intro_message(self, capfd):
        with patch(f"{PATCH_PATH}input", return_value="x"):
            menu()
        captured = capfd.readouterr()
        expected = (
            "Please specify [e]ntry, [r]etrieval, [d]eletion, [l]isting or e[x]it:"
        )
        result = captured.out[: len(expected)]
        assert result == expected

    @mark.it(
        "Entering invalid input causes next options message to begin with Invalid input."
    )
    def test_invalid(self, capfd):
        with patch(f"{PATCH_PATH}input", return_value="y"):
            menu()
        with patch(f"{PATCH_PATH}input", return_value="x"):
            menu()
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
    def test_inputs(self, option, func_name):
        with patch(f"{PATCH_PATH}input", return_value=option):
            with patch(f"{PATCH_PATH}{func_name}") as mock:
                menu()
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
    @mark.it("Returns False when called")
    def test_1(self):
        assert not exit()

    @mark.it('Echoes "Thank you. Goodbye." to terminal')
    def test_2(self, capfd):
        exit()
        captured = capfd.readouterr().out
        assert captured == "Thank you. Goodbye.\n"


class Testauthentication:
    pass


class Testcheck_credentials:
    pass


class Testget_secret_ids:
    @mock_aws
    @fixture
    def ssm_client(self):
        return client("ssm", environ["AWS_DEFAULT_REGION"])

    @mark.it("Returns names of parameters added to SSM")
    def test_1(self, ssm_client):
        test_passwords = [
            {
                "Name": "/passwordmgr/secret_password",
                "Value": "matthew",
                "Type": "String",
                "Overwrite": True,
            },
            {
                "Name": "/passwordmgr/secreter_password",
                "Value": "matthewer",
                "Type": "String",
                "Overwrite": True,
            },
        ]
        for password in test_passwords:
            ssm_client.put_parameter(**password)
        result = get_secret_ids(ssm_client)
        assert result == ["secret_password", "secreter_password"]


class Testssm_client:
    @mark.xfail
    @mock_aws
    @mark.it("Returns instance of boto3 client")
    def test_1(self):
        print(type(ssm_client))
        assert isinstance(ssm_client(), SSMClient)
