from boto3 import client
from mypy_boto3_ssm.client import SSMClient
from os import getenv


class PasswordManager:
    def __init__(self):
        self.ssm_client = client("ssm", getenv("AWS_DEFAULT_REGION"))
        self.ssm_dir = "/passwordmgr/"
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
        print("Please specify [e]ntry, [r]etrieval, [d]eletion, [l]isting or e[x]it:")
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

    def get_secret_ids(self) -> list[str] | None:
        id_list = self.ssm_client.describe_parameters(
            ParameterFilters=[
                {
                    "Key": "Name",
                    "Option": "BeginsWith",
                    "Values": [self.ssm_dir],
                }
            ]
        )
        return [
            parameter["Name"][len(self.ssm_dir) :]
            for parameter in id_list["Parameters"]
        ]

    def __call__(self):
        self.main_loop()


if __name__ == "__main__":
    pm = PasswordManager()
    pm()
