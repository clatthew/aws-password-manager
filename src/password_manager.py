from boto3 import client
from mypy_boto3_ssm.client import SSMClient
from os import getenv


def main_loop():
    running = True
    AUTHENTICATED = False
    while running:
        if not AUTHENTICATED:
            AUTHENTICATED = authentication()
        else:
            running = not menu()


def menu():
    print("Please specify [e]ntry, [r]etrieval, [d]eletion, [l]isting or e[x]it:")
    response = input(">>> ")
    match response:
        case "e":
            entry()
        case "r":
            retrieval()
        case "d":
            deletion()
        case "l":
            listing()
        case "x":
            return exit()
        case _:
            print("Invalid input. ", end="")


def entry():
    print("entry")


def retrieval():
    print("retrieval")


def deletion():
    print("deletion")


def listing():
    print("listing")


def exit() -> bool:
    print("Thank you. Goodbye.")
    return False


def authentication() -> bool:
    print("enter password:")
    password = input(">>> ")
    if password == "hello":
        return True


def check_credentials() -> bool:
    pass


def get_secret_ids(ssm_client) -> list[str] | None:
    folder_prefix = "/passwordmgr/"
    id_list = ssm_client.describe_parameters(
        ParameterFilters=[
            {
                "Key": "Name",
                "Option": "BeginsWith",
                "Values": [folder_prefix],
            }
        ]
    )
    return [
        parameter["Name"][len(folder_prefix) :] for parameter in id_list["Parameters"]
    ]


def ssm_client() -> SSMClient:
    return client("ssm", getenv["AWS_DEFAULT_REGION"])


if __name__ == "__main__":
    main_loop()
