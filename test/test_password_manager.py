from src.password_manager import PasswordManager, get_input, get_secret_ids
from pytest import mark, fixture, raises
from unittest.mock import patch
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


@fixture
def sm_client():
    return client("secretsmanager", environ["AWS_DEFAULT_REGION"])


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
    @fixture
    def menu_message(self):
        return "Please specify \x1b[4me\x1b[0mntry, \x1b[4mr\x1b[0metrieval, \x1b[4md\x1b[0meletion, \x1b[4ml\x1b[0misting or e\x1b[4mx\x1b[0mit:"

    # Add a test for exit exiting the loop?
    @mark.it("Menu function displays correct options message")
    def test_intro_message(self, capfd, test_pm, menu_message):
        with patch(f"{PATCH_PATH}input", return_value="x"):
            test_pm.menu()
        captured = capfd.readouterr()
        result = captured.out[: len(menu_message)]
        assert result == menu_message

    @mark.it(
        "Entering invalid input causes next options message to begin with Invalid input."
    )
    def test_invalid(self, capfd, test_pm, menu_message):
        with patch(f"{PATCH_PATH}input", return_value="y"):
            test_pm.menu()
        with patch(f"{PATCH_PATH}input", return_value="x"):
            test_pm.menu()
        captured = capfd.readouterr()
        add_message = "Invalid input. "
        expected = add_message + menu_message
        result = captured.out[
            len(menu_message) + 1 : 2 * len(menu_message) + len(add_message) + 1
        ]
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
    @fixture
    def master_credentials(self):
        return {
            "Name": f"{PasswordManager.sm_dir}{PasswordManager.master_credentials}",
            "SecretString":
                f"""{{
                    "username": "mattyc",
                    "password": "passyc"
                    }}
                """
        }
    @mock_aws
    @mark.it("Returns nothing when correct credentials are supplied")
    def test_1(self, test_pm, sm_client, master_credentials):
        sm_client.create_secret(**master_credentials)
        with patch.object(test_pm, "sm_client", sm_client):
            assert not test_pm.check_credentials('mattyc','passyc')
    @mock_aws
    @mark.it("Raises AssertionError when supplied username is incorrect")
    def test_2(self, test_pm, sm_client, master_credentials):
        sm_client.create_secret(**master_credentials)
        with patch.object(test_pm, "sm_client", sm_client):
            with raises(AssertionError):
                test_pm.check_credentials('mattycc', 'passyc')
    @mock_aws
    @mark.it("Raises AssertionError when supplied password is incorrect")
    def test_3(self, test_pm, sm_client, master_credentials):
        sm_client.create_secret(**master_credentials)
        with patch.object(test_pm, "sm_client", sm_client):
            with raises(AssertionError):
                test_pm.check_credentials('mattyc', 'passycccc')


class Testget_secret_ids:

    @mock_aws
    @mark.it("Returns names of parameters added to SM")
    def test_1(self, sm_client):
        sm_dir = "/passwordmgr/"
        test_passwords = [
            {
                "Name": f"{sm_dir}secret_password",
                "SecretString": """{
                "password": "biiiiig99",
                "url": "www.big_secret.com"
            }""",
                "ForceOverwriteReplicaSecret": True,
            },
            {
                "Name": f"{sm_dir}secreter_password",
                "SecretString": """{
                "password": "biiiiigger99",
                "url": "www.bigger_secret.com"
            }""",
                "ForceOverwriteReplicaSecret": True,
            },
        ]
        for password in test_passwords:
            sm_client.create_secret(**password)
        result = get_secret_ids(sm_client)
        assert result == ["secret_password", "secreter_password"]

    @mock_aws
    @mark.it("Returns empty list if no parameters have been added to SM")
    def test_2(self, sm_client):
        result = get_secret_ids(sm_client)
        assert result == []

class Testget_input:
    @mark.it("Displays supplied message in the terminal")
    def test_1(self, capfd):
        test_message = "Diamond Sword to Major Steve"
        with patch(f"src.utils.input", return_value="z"):
            get_input(test_message)
            captured = capfd.readouterr().out
        assert captured == test_message + "\n"

    @mark.it("Returns user's input")
    def test_2(self):
        test_message = "Take your speed potion and put your diamond helmet on"
        test_input = "Check your pickaxe, and may Notch love be with you"
        with patch(f"src.utils.input", return_value=test_input):
            result = get_input(test_message)
        assert result == test_input