from tim_gui.api import TimAPI
from tim_gui.api.models import ItemUpdate, UserCreate, UserUpdate
from requests.exceptions import RequestException


def main():
    try:
        api = TimAPI()
        api.login(username="teste@email.com", password="teste")
        api.update_user_me(UserUpdate(is_admin=True))
        print(api.get_user_me())
    except RequestException as e:
        print(f"error->{e=}")

if __name__ == "__main__":
    main()
