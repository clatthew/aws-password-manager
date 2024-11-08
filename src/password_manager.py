from boto3 import client
from os import getenv


class PasswordManager:
    sm_dir = "/passwordmgr/"

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
        # Collect the secret info
        # use get_input
        secret = {
            "Name": f"{PasswordManager.sm_dir}string",
            "SecretString": """{
                'secret_name': ___,
                'secret_password': ___
            }""",
            "ForceOverwriteReplicaSecret": True,
        }
        self.sm_client.create_secret(**secret)

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
        # use get_input
        print("enter password:")
        password = input(">>> ")
        if password == "hello":
            return True

    def get_input(self, message: str) -> str:
        print(message)
        return input(">>> ")

    def check_credentials(self) -> bool:
        pass

    def get_secret_ids(self) -> list[str]:
        secret_list = self.sm_client.list_secrets(
            Filters=[{"Key": "name", "Values": [self.sm_dir]}]
        )["SecretList"]
        return [secret["Name"][len(self.sm_dir) :] for secret in secret_list]

    def __call__(self):
        self.main_loop()


if __name__ == "__main__":
    PasswordManager()()
