import getpass
import json

from src.auth import PASSWORD_ITERATIONS, TEACHERS_FILE, create_password_record, load_teacher_store


def main():
    username = input("Teacher username: ").strip()
    password = getpass.getpass("Teacher password (minimum 12 characters): ")
    confirmation = getpass.getpass("Confirm password: ")

    if not username:
        raise SystemExit("Username cannot be empty")
    if len(password) < 12:
        raise SystemExit("Password must be at least 12 characters")
    if password != confirmation:
        raise SystemExit("Passwords do not match")

    store = load_teacher_store()
    if username in store["teachers"]:
        raise SystemExit("That teacher username already exists")

    store["iterations"] = PASSWORD_ITERATIONS
    store["teachers"][username] = create_password_record(password)
    with TEACHERS_FILE.open("w", encoding="utf-8") as file:
        json.dump(store, file, indent=2)
        file.write("\n")
    print(f"Added teacher {username} to {TEACHERS_FILE}")


if __name__ == "__main__":
    main()