from boto3 import client
from os import environ
from password_manager import PasswordManager, get_secret_ids
from botocore.exceptions import ClientError
from getpass import getpass
from src.env_setup import set_aws_creds
def setup_credentials():
    print("Create your username and master password for the password manager")
    username = input('New username: ')
    password = get_password_input()
    try:
        set_aws_creds()
        sm_client = client("secretsmanager", environ["AWS_DEFAULT_REGION"])
        if PasswordManager.master_credentials not in get_secret_ids(sm_client):
            sm_client.create_secret(Name=f"{PasswordManager.sm_dir}{PasswordManager.master_credentials}")
        password = {
            "SecretId": f"{PasswordManager.sm_dir}{PasswordManager.master_credentials}",
            "SecretString":
                f"""{{
                    "username": "{username}",
                    "password": "{password}"
                    }}
                """
        }
        sm_client.update_secret(**password)
        print("Master credentials successfully updated.")
    except ClientError:
        print("Connection to AWS SecretsManager failed. Please check your AWS credentials and try again.")



def get_password_input():
    password = getpass('New password: ')
    password2 = getpass('Confirm new password: ')
    if password == password2:
        return password
    print("Your passwords did not match. Please try again.")
    return get_password_input()

if __name__ == "__main__":
    setup_credentials()