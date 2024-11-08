from boto3 import client
from os import getenv
from json import loads
from getpass import getpass
from src.env_setup import set_aws_creds

class PasswordManager:
    sm_dir = "/passwordmgr/"
    master_credentials = "master_credentials"

    def __init__(self):
        self.sm_client = client("secretsmanager", getenv("AWS_DEFAULT_REGION"))
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
        start_ul = "\033[4m"
        stop_ul = "\033[0m"
        print(
            f"Please specify {start_ul}e{stop_ul}ntry, {start_ul}r{stop_ul}etrieval, {start_ul}d{stop_ul}eletion, {start_ul}l{stop_ul}isting or e{start_ul}x{stop_ul}it:"
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

    def entry(self):
        print("entry")
        

    def retrieval(self):
        print("retrieval")
        # use get_input
        # secret_name = ...
        # self.sm_client.get_secret_value(
        #     SecretId=secret_name
        # )['SecretString']

    def deletion(self):
        # use get_input
        print("deletion")
        secret_name = "club_pengiun"
        self.sm_client.delete_secret(SecretId=secret_name)

    def listing(self):
        # use get_input
        # retrieve list from get_secret_ids
        print("listing")

    def exit(self) -> bool:
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

    def check_credentials(self, username, password):
        master_credentials = self.sm_client.get_secret_value(
            SecretId=f"{PasswordManager.sm_dir}{PasswordManager.master_credentials}"
        )["SecretString"]
        master_credentials_json = loads(master_credentials)
        assert master_credentials_json["username"] == username
        assert master_credentials_json["password"] == password

    def __call__(self):
        set_aws_creds()
        self.main_loop()


def get_secret_ids(sm_client) -> list[str]:
    secret_list = sm_client.list_secrets(
        Filters=[{"Key": "name", "Values": [PasswordManager.sm_dir]}]
    )["SecretList"]
    return [secret["Name"][len(PasswordManager.sm_dir) :] for secret in secret_list]


def get_input(message: str) -> str:
    print(message)
    return input(">>> ")


if __name__ == "__main__":
    PasswordManager()()
