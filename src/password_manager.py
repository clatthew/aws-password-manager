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
    print(f"response: {response}")
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


def exit():
    print("Thank you. Goodbye.")
    return False


def authentication():
    print("enter password:")
    password = input(">>> ")
    if password == "hello":
        return True


def check_credentials():
    pass


def get_secret_ids():
    pass


if __name__ == "__main__":
    main_loop()
