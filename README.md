# Password manager
Manage credentials stored in AWS SecretsManager. All credentials used by PasswordManager will be stored in the /password_manager directory of your SecretsManager. Runs in a mocked AWS environment by default.

## Setup
In terminal, run
- `python -m venv venv`
- `source venv/bin/activate`
- `export PYTHONPATH=$(pwd)`
- `pip install -r requirements.txt`
- `pytest --testdox`

then run password_manager.py using the version of python in your virtual environment.

## Funtionallity
### Authentication
Upon startup, PasswordManager will ask for your master credentials. Enter your username and password to enter the program. The default username is `test` and the default password is `test`. You can change these on lines 8 and 9 of password_manager.py.
### Main menu
Choose between credential <u>e</u>ntry, <u>r</u>etrieval, <u>l</u>isting, <u>d</u>eletion and e<u>x</u>itting the program by entering the option's underlined letter and pressing enter.
### Entry
1. Enter the credential name. This must be unique among the credentials stored by the Password Manager and cannot be "master_credentials".
2. You can now add a username, password and URL to the credential. To edit one of these fields, enter the option's underlined letter and press enter. All three of these fields are optional.
3. To save your credential, enter "s" and press enter. If a credential with this name already exists, you will be asked if you would like to overwrite the existing credential, or return to editing the new credential. After saving, you will be returned to the main menu.
4. Press "x" to exit entry mode without saving.
### Retrieval
Enter the name of the credential you would like to retrieve.
If the credential exists, it will be written to file credentials/credential.txt and you will be returned to the main menu.
If the credential doesn't exist, you will then be returned to the main menu.
### Listing
The names of the credentials stored by you using PasswordManager will be listed in the terminal. These are the the names which can be used in Retrival or Deletion mode. You will be returned to main menu.
### Deletion
Enter the name of a credential to delete it from PasswordManager.

## To do
- Create makefile for running setup
- Add github action to run tests when pushing a commit
- Authentication
    - Implement authentication timeout
    - Exit program if incorrect credentials entered too many times