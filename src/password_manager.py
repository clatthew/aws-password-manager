from boto3 import client
from mypy_boto3_ssm.client import SSMClient
from os import getenv


class PasswordManager:
    ssm_dir = "/passwordmgr/"

    def __init__(self):
        self.ssm_client = client("ssm", getenv("AWS_DEFAULT_REGION"))
        self.running = False

    def main_loop(self):
        self.running = True
        AUTHENTICATED = False
        while self.running:
            if not AUTHENTICATED:
                AUTHENTICATED = self.authentication()
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

    def deletion(self):
        print("deletion")

    def listing(self):
        print("listing")

    def exit(self) -> bool:
        print("Thank you. Goodbye.")
        self.running = False

    def authentication(self) -> bool:
        print("enter password:")
        password = input(">>> ")
        if password == "hello":
            return True

    def check_credentials(self) -> bool:
        pass

    def get_secret_ids(self) -> list[str]:
        id_list = self.ssm_client.describe_parameters(
            ParameterFilters=[
                {
                    "Key": "Name",
                    "Option": "BeginsWith",
                    "Values": [PasswordManager.ssm_dir],
                }
            ]
        )
        return [
            parameter["Name"][len(PasswordManager.ssm_dir) :]
            for parameter in id_list["Parameters"]
        ]

    def __call__(self):
        self.main_loop()


if __name__ == "__main__":
    PasswordManager()()
