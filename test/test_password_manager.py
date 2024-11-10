from src.password_manager import (
    PasswordManager,
    get_secret_ids,
    underline,
    underline_letter,
)
from json import loads
from pytest import mark, fixture, raises
from unittest.mock import patch, Mock
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


@fixture
def master_credentials():
    return {
        "Name": f"{PasswordManager.sm_dir}{PasswordManager.master_credentials}",
        "SecretString": f"""{{
                "username": "mattyc",
                "password": "passyc"
                }}
            """,
    }


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
    # add test for excluding username, password or url
    @mock_aws
    @mark.it("Allows entry of a new credential with all fields")
    def test_1(self, test_pm):
        test_secret = {
            "Secret Name": "Club Penguin",
            "Username": "icybird87",
            "Password": "nootnoot",
            "URL": "clubpenguin.com",
        }

        with patch(
            f"{PATCH_PATH}input",
            side_effect=[
                test_secret["Secret Name"],
                "u",
                test_secret["Username"],
                "p",
                test_secret["Password"],
                "r",
                test_secret["URL"],
                "s",
                "x",
            ],
        ):
            test_pm.entry()
        result = loads(
            test_pm.sm_client.get_secret_value(
                SecretId=f"{PasswordManager.sm_dir}{test_secret['Secret Name']}"
            )["SecretString"]
        )
        del test_secret["Secret Name"]
        assert result == test_secret

    @mark.it(
        "Doesn't allow new credential to have the same name as the master credentials"
    )
    def test_2(self, test_pm, capfd):
        with patch(
            f"{PATCH_PATH}input",
            side_effect=[PasswordManager.master_credentials, "s", "x"],
        ):
            test_pm.entry()
            result = capfd.readouterr().out
            assert (
                f'Credential name "{PasswordManager.master_credentials}" is not allowed. Please choose a different name.'
                in result
            )

    @mock_aws
    @mark.it(
        "Allows overwriting of credential if a new credential has the same name as an existing credential"
    )
    def test_3(self, test_pm, capfd):
        test_credential_name = "mattyc"
        test_password = "hello66"
        with patch(f"{PATCH_PATH}input", side_effect=[test_credential_name, "s"]):
            test_pm.entry()
        with patch(
            f"{PATCH_PATH}input",
            side_effect=[test_credential_name, "p", test_password, "s", "o"],
        ):
            test_pm.entry()
        with patch(f"{PATCH_PATH}input", side_effect=[test_credential_name]):
            test_pm.retrieval()
            result = capfd.readouterr().out
        assert f"Password: {test_password}" in result

    @mock_aws
    @mark.it("Does not save a credential if the user exits without saving")
    def test_4(self, test_pm):
        test_credential_name = "mattyc"
        with patch(f"{PATCH_PATH}input", side_effect=[test_credential_name, "x"]):
            test_pm.entry()
        assert not get_secret_ids(test_pm.sm_client)

    @mock_aws
    @mark.it(
        "If username, password or url are not entered, the fields aren't stored in the credential"
    )
    def test_5(self, test_pm, capfd):
        test_credential_name = "Club Penguin"
        with patch(f"{PATCH_PATH}input", side_effect=[test_credential_name, "s"]):
            test_pm.entry()
        with patch(f"{PATCH_PATH}input", side_effect=[test_credential_name]):
            test_pm.retrieval()
            result = capfd.readouterr().out
        for field in ["Username", "Password", "URL"]:
            assert field not in result


class Testretrieval:
    @mock_aws
    @mark.it("Full credential info echoed to terminal")
    def test_1(self, test_pm, capfd):
        test_credential = {
            "name": "Club Pengiun",
            "username": "icybird87",
            "password": "nootnoot",
            "url": "clubpenguin.com",
        }
        with patch(
            f"{PATCH_PATH}input",
            side_effect=[
                test_credential["name"],
                "u",
                test_credential["username"],
                "p",
                test_credential["password"],
                "r",
                test_credential["url"],
                "s",
            ],
        ):
            test_pm.entry()
        with patch(f"{PATCH_PATH}input", side_effect=[test_credential["name"]]):
            test_pm.retrieval()
            result = capfd.readouterr().out
        assert (
            f"Credential {underline(test_credential['name'])}:\nUsername: {test_credential['username']}\nPassword: {test_credential['password']}\nURL: {test_credential['url']}"
            in result
        )

    @mock_aws
    @mark.it('Echoes "No credential found..." if credential name does not exist')
    def test_2(self, test_pm, capfd):
        test_credential_name = "Club Penguin"
        with patch(f"{PATCH_PATH}input", side_effect=[test_credential_name]):
            test_pm.retrieval()
            result = capfd.readouterr().out
        assert f'No credential found with name "{test_credential_name}"' in result


class Testdeletion:
    @mock_aws
    @mark.it("Deletes an existing credential")
    def test_1(self, test_pm):
        secret = {
            "Name": f"{PasswordManager.sm_dir}Club Penguin",
            "SecretString": f"""{{
                "username": "icybird87",
                "password": "nootnoot"
                }}
            """,
        }
        test_pm.sm_client.create_secret(**secret)
        assert get_secret_ids(test_pm.sm_client)
        with patch(f"{PATCH_PATH}input", return_value="Club Penguin"):
            test_pm.deletion()
        assert not get_secret_ids(test_pm.sm_client)

    @mark.it("sm_client not called when credential doesn't exist")
    def test_2(self, test_pm):
        with patch(f"{PATCH_PATH}input", return_value="Club Penguin"):
            with patch.object(test_pm, "sm_client") as mock:
                test_pm.deletion()
                assert mock.call_count == 0


class Testlisting:
    @mock_aws
    @mark.it('Echoes "No credentials saved." when no credentials are saved')
    def test_1(self, test_pm, capfd):
        expected = "No credentials saved."
        test_pm.listing()
        result = capfd.readouterr().out
        assert result == expected + "\n"

    @mock_aws
    @mark.it(
        "Echoes names of all available credentials when credentials have been saved"
    )
    def test_2(self, test_pm, capfd):
        expected = "Stored credentials:\n- Club Penguin\n- Runescape\n"
        secrets = [
            {
                "Name": f"{PasswordManager.sm_dir}Club Penguin",
                "SecretString": """
                {
                "Username": "icybird87",
                "Password": "nootnoot",
                "URL": "clubpenguin.com",
                }
            """,
            },
            {
                "Name": f"{PasswordManager.sm_dir}Runescape",
                "SecretString": """{
            "Username": "bigwizzy",
            "Password": "magic",
            "URL": "runescape.com",
            }""",
            },
        ]
        for secret in secrets:
            test_pm.sm_client.create_secret(**secret)
        test_pm.listing()
        result = capfd.readouterr().out
        assert result == expected


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
    @mock_aws
    @mark.it("Returns True when correct credentials are entered")
    def test_1(self, test_pm, sm_client, master_credentials):
        sm_client.create_secret(**master_credentials)
        with patch.object(test_pm, "sm_client", sm_client):
            with patch(f"{PATCH_PATH}input", return_value="mattyc"):
                with patch(f"{PATCH_PATH}getpass", return_value="passyc"):
                    result = test_pm.authentication()
        assert result

    @mock_aws
    @mark.it("Returns False when incorrect username is entered")
    def test_2(self, test_pm, sm_client, master_credentials):
        sm_client.create_secret(**master_credentials)
        with patch.object(test_pm, "sm_client", sm_client):
            with patch(f"{PATCH_PATH}input", return_value="mattyc2"):
                with patch(f"{PATCH_PATH}getpass", return_value="passyc"):
                    result = test_pm.authentication()
        assert not result

    @mock_aws
    @mark.it("Returns False when incorrect password is entered")
    def test_3(self, test_pm, sm_client, master_credentials):
        sm_client.create_secret(**master_credentials)
        with patch.object(test_pm, "sm_client", sm_client):
            with patch(f"{PATCH_PATH}input", return_value="mattyc"):
                with patch(f"{PATCH_PATH}getpass", return_value="passyc2"):
                    result = test_pm.authentication()
        assert not result


class Testcheck_credentials:
    @mock_aws
    @mark.it("Returns nothing when correct credentials are supplied")
    def test_1(self, test_pm, sm_client, master_credentials):
        sm_client.create_secret(**master_credentials)
        with patch.object(test_pm, "sm_client", sm_client):
            assert not test_pm.check_credentials("mattyc", "passyc")

    @mock_aws
    @mark.it("Raises AssertionError when supplied username is incorrect")
    def test_2(self, test_pm, sm_client, master_credentials):
        sm_client.create_secret(**master_credentials)
        with patch.object(test_pm, "sm_client", sm_client):
            with raises(AssertionError):
                test_pm.check_credentials("mattycc", "passyc")

    @mock_aws
    @mark.it("Raises AssertionError when supplied password is incorrect")
    def test_3(self, test_pm, sm_client, master_credentials):
        sm_client.create_secret(**master_credentials)
        with patch.object(test_pm, "sm_client", sm_client):
            with raises(AssertionError):
                test_pm.check_credentials("mattyc", "passycccc")


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


class Testunderline:
    @mark.it("Pre- and appends underline formatting codes to string")
    def test1(self):
        test_string = "hello"
        expected = f"\x1b[4m{test_string}\x1b[0m"
        result = underline(test_string)
        assert result == expected


class Testunderline_letter:
    @mark.it("Underlines first occurrrence of a letter in the word")
    def test_1(self):
        test_string = "hello"
        expected = f"{test_string[:2]}\x1b[4ml\x1b[0m{test_string[3:]}"
        result = underline_letter(test_string, "l")
        assert result == expected

    @mark.it(
        "Returns the original string if the letter to underline is not present in the string"
    )
    def test_2(self):
        test_string = "hello"
        result = underline_letter(test_string, "j")
        assert result == test_string
