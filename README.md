# Password manager
Store and retrieve credentials stored in AWS.
## Baisc behaviour

### Main loop
```python
running = True
AUTHENTICATED = False
while running:
    print("Please specify [e]ntry, [r]etrieval, [d]eletion, [l]isting or e[x]it:")
    response = input(">>> "):
    if response == 
        ...
    else:
        print("Invalid input. ", end="")
```
- if one of the allowed keys is entered, call the relevant function
- if one of the non-allowed keys is entered, call invalid input function

### Core functions

#### Entry
- ask for secret identifier, userid and password.
- call authenticate function
- if authentication returns `False`:
    - Return to the main loop
- request input of secretid and secret_value
- confirmation message: `Secret saved.`
#### Retrieval
- call authetication function
- if authentication returns `False`:
    - Return to the main loop
- retrive the requested secret from SSM/s3
- write it to secrets.txt
- confirmation message: `Secrets stored in file secrets.txt.`

#### Deletion
- call authetication function
- if authentication returns `False`:
    - Return to the main loop
- request input of secretid
- call get_secret_ids
- if secretid not in get_secret_id response:
    - echo in terminal:
        ```
        No secret found with id ...
        ```
    - return to the main loop
- delete the secret from SSM/s3

#### Listing
- call get_secret_ids
- if response is None:
    - return to main loop
- echo in terminal:
    ```
    2 secrets available:
        password_club_penguin
        password_minecraft
    ```
#### Exit
```python
print("Thank you. Goodbye.")
running = False
```
### Utility functions

#### Authentication
Return `True` if the user has authenticated themself. Return `False` otherwise.
```python
if AUTHENTICATED:
    return AUTHENTICATED
print("UserId":)
user_id = input(">>> ")
print("Password":)
password = input(">>> ")
if check_credentials(user_id, password):
    AUTHENTICATED = True
    return AUTHENTICATED
print("Authentication failed")
return False
```

#### Check credentials
Takes arguments userid and password. Compare these to the secrets stored in s3/SSM. Return `True` if they match, `False` otherwise.

#### Get secret ids
- call authentication function
- if authentication returns `False`:
    - Return `None`
- retrieve the names of credentials stored in SSM/s3
- return them

## Future ideas
- authentication timeout after certain time
- secret versioning
- store username, password, url, website name etc together as a single entry