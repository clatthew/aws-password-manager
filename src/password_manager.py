from boto3 import client
from botocore.exceptions import ClientError
from json import loads, dumps
from getpass import getpass
from moto import mock_aws


class PasswordManager:
    sm_dir = "/passwordmgr/"
    master_credentials = "master_credentials"

    def __init__(self):
        self.sm_client = client("secretsmanager", "eu-west-2")
        self.running = False

    def main_loop(self):
        self.running = True
        authenticated = False
        while self.running:
            if not authenticated:
                authenticated = self.authentication()
            else:
                self.menu()

    def menu(self):
        print(
            f'Please specify {underline_letter("entry", "e")}, {underline_letter("retrieval", "r")}, {underline_letter("deletion", "d")}, {underline_letter("listing", "l")} or {underline_letter("exit", "x")}:'
        )
        response = input(">>> ")
        match response:
            case "e":
                self.entry()
            case "r":
                self.retrieval()
            case "d":
                self.deletion()
            case "l":
                self.listing()
            case "x":
                self.exit()
            case _:
                print("Invalid input. ", end="")

    def entry(self) -> dict:
        name = input("New credential name: ")
        fields = {
            "credential_name": {
                "display_name": "Credential Name",
                "content": name,
                "id_letter": "C",
            },
            "user_name": {
                "display_name": "Username",
                "content": "[empty]",
                "id_letter": "U",
            },
            "password": {
                "display_name": "Password",
                "content": "[empty]",
                "id_letter": "P",
            },
            "url": {"display_name": "URL", "content": "[empty]", "id_letter": "R"},
        }
        editing = True
        while editing:
            print("Select field to edit:")
            for field in fields:
                print(
                    f"{underline_letter(fields[field]['display_name'], fields[field]['id_letter'])}: {fields[field]['content']}"
                )
            print(
                f"or {underline_letter('save', 's')}, or {underline_letter('exit', 'x')} without saving."
            )
            response = input(">>> ")
            field = None
            match response.lower():
                case "c":
                    field = fields["credential_name"]
                case "u":
                    field = fields["user_name"]
                case "p":
                    field = fields["password"]
                case "r":
                    field = fields["url"]
                case "s":
                    credential_name = fields["credential_name"]["content"]
                    if credential_name == PasswordManager.master_credentials:
                        print(
                            f'Credential name "{PasswordManager.master_credentials}" is not allowed. Please choose a different name.'
                        )
                    elif credential_name in get_secret_ids(self.sm_client):
                        print(
                            f'Credential name "{credential_name}" already in use. Would you like to {underline_letter("overwrite", "o")} or {underline_letter("choose", "c")} a different name?'
                        )
                        responded = False
                        while not responded:
                            response = input(">>> ")
                            match response:
                                case "o":
                                    responded = True
                                    editing = False
                                    self.delete_secret(credential_name)
                                    self.save_secret(fields)
                                case "c":
                                    responded = True
                    else:
                        editing = False
                        self.save_secret(fields)
                case "x":
                    editing = False
            if field:
                field["content"] = input(f"Enter {field['display_name']}: ")

    def save_secret(self, fields: dict):
        secret_string = dumps(
            {
                fields[field]["display_name"]: fields[field]["content"]
                for field in fields
                if fields[field]["content"] != "[empty]" and field != "credential_name"
            }
        )
        secret = {
            "Name": f"{PasswordManager.sm_dir}{fields['credential_name']['content']}",
            "SecretString": secret_string,
            "ForceOverwriteReplicaSecret": True,
        }
        self.sm_client.create_secret(**secret)
        print(
            f"Credential {fields['credential_name']['content']} saved to SecretsManager."
        )

    def retrive_secret(self, credential_name: str) -> dict | None:
        try:
            return self.sm_client.get_secret_value(
                SecretId=f"{PasswordManager.sm_dir}{credential_name}"
            )
        except ClientError:
            return None

    def retrieval(self):
        credential_name = input("Name of credential to retrieve: ")
        password = self.retrive_secret(credential_name)
        if password:
            password_dict = loads(password["SecretString"])
            print(f"Credential {underline(credential_name)}:")
            if not password_dict:
                print("No fields to display.")
            for entry in password_dict:
                print(f"{entry}: {password_dict[entry]}")
        else:
            print(f'No credential found with name "{credential_name}"')

    def delete_secret(self, credential_name) -> dict | None:
        try:
            return self.sm_client.delete_secret(
                SecretId=f"{PasswordManager.sm_dir}{credential_name}",
                ForceDeleteWithoutRecovery=True,
            )
        except ClientError:
            return None

    def deletion(self):
        credential_name = input("Name of credential to delete: ")
        if credential_name in get_secret_ids(self.sm_client):
            self.delete_secret(credential_name)
            print(f'Successfully deleted credential "{credential_name}".')
        else:
            print(f'No credential found with name "{credential_name}".')

    def listing(self):
        secrets = get_secret_ids(self.sm_client)
        if secrets:
            print("Stored credentials:")
            for secret in secrets:
                print(f"- {secret}")
        else:
            print("No credentials saved.")

    def exit(self):
        print("Thank you. Goodbye.")
        self.running = False

    def authentication(self) -> bool:
        print("Please enter your username and password.")
        username = input("Username: ")
        password = getpass("Password: ")
        try:
            self.check_credentials(username, password)
            print("Authentication successful.")
            return True
        except AssertionError:
            print("Authentication failed.")
            return False

    def check_credentials(self, username: str, password: str):
        master_credentials = self.sm_client.get_secret_value(
            SecretId=f"{PasswordManager.sm_dir}{PasswordManager.master_credentials}"
        )["SecretString"]
        master_credentials_json = loads(master_credentials)
        assert master_credentials_json["username"] == username
        assert master_credentials_json["password"] == password

    def __call__(self):
        self.main_loop()


def get_secret_ids(sm_client) -> list[str]:
    secret_list = sm_client.list_secrets(
        Filters=[{"Key": "name", "Values": [PasswordManager.sm_dir]}]
    )["SecretList"]
    return [
        secret["Name"][len(PasswordManager.sm_dir) :]
        for secret in secret_list
        if secret["Name"]
        != f"{PasswordManager.sm_dir}{PasswordManager.master_credentials}"
    ]


def underline_letter(word: str, letter_to_underline: str) -> str:
    try:
        pos = word.index(letter_to_underline)
        return word[:pos] + underline(word[pos]) + word[pos + 1 :]
    except ValueError:
        return word


def underline(word: str) -> str:
    ul = {"start": "\033[4m", "stop": "\033[0m"}
    return ul["start"] + word + ul["stop"]


if __name__ == "__main__":
    with mock_aws():
        pm = PasswordManager()
        pm.sm_client.create_secret(
            **{
                "Name": f"{PasswordManager.sm_dir}{PasswordManager.master_credentials}",
                "SecretString": f"""{{
                "username": "test",
                "password": "test"
                }}
            """,
            }
        )
        pm()
