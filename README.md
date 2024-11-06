# Password manager
Store and retrieve credentials stored in AWS.
## Basic behaviour
Master password stored in secrets manager. Make a second script to allow the user to store a master password.
### Main loop
```python
    running = True
    AUTHENTICATED = False
    while running:
        if not AUTHENTICATED:
            AUTHENTICATED = authentication()
        else:
            running = not menu()
```
### Menu
- if one of the allowed keys is entered, call the relevant function
- if one of the non-allowed keys is entered, call invalid input function
```python
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
```
### Core functions

#### Entry
- ask for secret identifier, userid and password.
- request input of secretid and secret_value
- confirmation message: `Secret saved.`
#### Retrieval
- retrive the requested secret from secrets manager
- write it to secrets.txt
- confirmation message: `Secrets stored in file secrets.txt.`

#### Deletion
- request input of secretid
- call get_secret_ids
- if secretid not in get_secret_id response:
    - echo in terminal:
        ```
        No secret found with id ...
        ```
    - return to the main loop
- delete the secret from secrets manager

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
return True
```
### Utility functions

#### Authentication
Return `True` if the user has authenticated themself. Return `False` otherwise.
```python
print("UserId":)
user_id = input(">>> ")
print("Password":)
password = input(">>> ")
return check_credentials(user_id, password):
```

#### Check credentials
Takes arguments userid and password. Compare these to the secrets stored in secrets manager. Return `True` if they match, `False` otherwise.

#### Get secret ids
- call authentication function
- if authentication returns `False`:
    - Return `None`
- retrieve the names of credentials stored in secrets manager
- return them

#### get_user_input
- show a message to the user and return their input

#### get_value_from_sm
- retrieve the requested 

## Future ideas
- authentication timeout after certain time
- secret versioning
- store username, password, url, website name etc together as a single entry
- quit program after maximum number of authentication attempts reached