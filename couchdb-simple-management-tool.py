from requests import get, put, post, delete
from bip_utils import Bip39MnemonicGenerator as bip
from simple_term_menu import TerminalMenu

"""
    CouchDB simple admin tool (native CouchDB API)
    It provides the most commom CouchDB functions, but not all.

    PEP8 compliant
    "Beautiful is better than ugly."
    "Simple is better than complex."
    — The Zen of Python
"""

HEADER_GENERAL = {'Accept': 'application/json',
                  'Content-Type': 'application/json'}
HEADER_ACCEPT = {'Accept': 'application/json'}
ADMIN_USER = 'admin'
ADMIN_PASSWD = 'admin'
HOST = '127.0.0.1:5984'
FULL_URL = f'http://{ADMIN_USER}:{ADMIN_PASSWD}@{HOST}'


def generate_mnemonic_passphrase():

    #  all passwords will be generated by this function
    #  following BIP39 standard - 12 random words (default option)

    global mnemonic_passwd
    mnemonic_passwd = '-'.join(bip.FromWordsNumber(12).split(' '))
    return mnemonic_passwd


def create_all_users_batch():

    #  This function can create several users, DBs and permissions associated
    #  with each user

    from os import path
    file = input('Please type the filename with users (one per line): ')
    if path.exists(file) and path.isfile(file):
        with open(file) as inputfile,\
                open('all_credentials.txt', 'wt') as user_credentials_file:

            user_credentials_file.truncate(0)

            for user in inputfile.read().split():
                login = user
                USER_URL = (f'{FULL_URL}/_users/org.couchdb.user:{login}')
                create_DB_URL = (f'{FULL_URL}/db_{login}')
                create_PERMISSION_URL = (f'{FULL_URL}/db_{login}/_security')

                get_login = get(USER_URL, headers=HEADER_GENERAL)
                if get_login.ok:
                    print(f'User "{login} "already in database.')
                else:

                    user_passwd = generate_mnemonic_passphrase()

                    user_data = {'name': login, 'password': user_passwd,
                                 'roles': [], 'type': 'user'}

                    DB_Permissions = {
                        "members": {
                            "names": [login],
                            "roles": []}}

                    createuser = put(USER_URL,
                                     headers=HEADER_GENERAL, json=user_data)
                    if createuser.ok:
                        print(f'{login}\n{createuser.text}\n')
                        print(
                            f'{login}|{user_passwd}',
                            file=user_credentials_file)

                        createDB = put(create_DB_URL, headers=HEADER_ACCEPT)
                        if createDB.ok:
                            print(f'{login}\n{createDB.text}\n')

                            create_DB_Permission = put(create_PERMISSION_URL,
                                                       headers=HEADER_GENERAL,
                                                       json=DB_Permissions)
                            if create_DB_Permission.ok:
                                print(f'{login}\n{create_DB_Permission.text}')
                    else:
                        print(f'{createuser.text}')
    else:
        print(f'File "{file}" not found or not a regular file.')


def create_DB():

    DB = input('Please type a DB name for creation: ')
    DB = DB.lower()
    create_DB_URL = (f'{FULL_URL}/{DB}')
    get_DB = get(f'{FULL_URL}/{DB}')
    if get_DB.ok:
        print(f'DB name "{DB}" already in CouchDB.')
    else:
        results = put(create_DB_URL, headers=HEADER_ACCEPT)
        if results.ok:
            print(f'DB "{DB}" has been created successfully.')
        else:
            print(f'{results.status_code}{results.text}')


def create_members_user():

    login = input('Username for creation: ')
    USER_URL = (f'{FULL_URL}/_users/org.couchdb.user:{login}')
    get_login = get(USER_URL, headers=HEADER_GENERAL)
    if get_login.ok:
        print(f'User "{login} "already in database.')
    else:
        user_passwd = generate_mnemonic_passphrase()
        user_data = {'name': login,
                     'password': user_passwd,
                     'roles': [],
                     'type': 'user'}
        create_user = put(USER_URL, headers=HEADER_GENERAL, json=user_data)
        if create_user.ok:
            print(f'User "{login}" created. '
                  f'Please write down the password.\n -->  "{user_passwd}"')
        else:
            print(f'{create_user.status_code}')


def create_ADMIN_change_password():

    choices = ["[x] Create ADMIN user",
               "[x] Change ADMIN password"]
    chosen = TerminalMenu(menu_entries=choices,
                          title=f"{'-' * 10} DB PERMISSIONs {'-' * 10}",
                          menu_cursor="> ",
                          menu_cursor_style=("fg_red", "bold"),
                          menu_highlight_style=("bg_black", "fg_red"),
                          cycle_cursor=True).show()
    if chosen == 0:
        login = input('Username for ADMIN creation: ')
        ADMIN_URL = (f'{FULL_URL}/_node/_local/_config/admins/{login}')
        get_login = get(ADMIN_URL, headers=HEADER_GENERAL)
        if get_login.ok:
            print(f'ADMIN user "{login} "already in database.')
        else:
            ADMIN_passwd = generate_mnemonic_passphrase()
            user_data = f'"{ADMIN_passwd}"'
            create_ADMIN = put(ADMIN_URL, data=user_data)
            if create_ADMIN.ok:
                print(f'ADMIN: {login} created. '
                      f'Please write down the password\n '
                      f'-->  "{ADMIN_passwd}"')
            else:
                print(f'Error: {create_ADMIN.status_code}')
    elif chosen == 1:
        login = input('ADMIN login for password change: ')
        ADMIN_URL = (f'{FULL_URL}/_node/_local/_config/admins/{login}')
        ADMIN_passwd = generate_mnemonic_passphrase()
        user_data = f'"{ADMIN_passwd}"'
        create_ADMIN = put(ADMIN_URL, data=user_data)
        if create_ADMIN.ok:
            print(f'ADMIN: {login} created. '
                  f'Please write down the new password\n '
                  f'-->  "{ADMIN_passwd}"')
        else:
            print(f'Error: {create_ADMIN.status_code}')


def change_user_password():

    login = input('Username for password change: ')
    USER_URL = (f'{FULL_URL}/_users/org.couchdb.user:{login}')
    get_login = get(USER_URL, headers=HEADER_GENERAL)
    if get_login.status_code == 404:
        print(f'User "{login}" not found.')
    elif get_login.ok:
        user_passwd = generate_mnemonic_passphrase()
        revision = get_login.json()['_rev']
        HEADER_CHANGE = {'Accept': 'application/json',
                         'Content-Type': 'application/json',
                         'If-Match': revision}
        user_data = {'name': login,
                     'password': user_passwd,
                     'roles': [],
                     'type': 'user'}
    change_passwd = put(USER_URL, headers=HEADER_CHANGE, json=user_data)
    if change_passwd.ok:
        print(f'Password for "{login}" has been changed successfully. '
              f'Please write down the new password.\n -->  "{user_passwd}"')
    else:
        print(f'{change_passwd.status_code}')


def set_members_DB_permission():

    choices = ["[x] Set DB permission for regular users",
               "[x] Reset DB permission"]
    chosen = TerminalMenu(menu_entries=choices,
                          title=f"{'-' * 10} DB PERMISSIONs {'-' * 10}",
                          menu_cursor="> ",
                          menu_cursor_style=("fg_red", "bold"),
                          menu_highlight_style=("bg_black", "fg_red"),
                          cycle_cursor=True).show()

    if chosen == 0:
        login = input('Username for permission on a specific DB: ')
        USER_URL = (f'{FULL_URL}/_users/org.couchdb.user:{login}')
        get_login = get(USER_URL, headers=HEADER_GENERAL)
        if get_login.ok:
            DB = input(f'DB name to grant permission for "{login}": ')
            DB_Permissions = {"members": {"names": [login], "roles": []}}
            current_DB_URL = (f'{FULL_URL}/{DB}')
            get_DB = get(current_DB_URL)
            if get_DB.ok:
                security_PERMISSION_URL = (f'{FULL_URL}/{DB}/_security')
                results = put(security_PERMISSION_URL, headers=HEADER_GENERAL,
                              json=DB_Permissions)
                if results.ok:
                    print(f'DB "{DB}" permission for {login} has been set.')
                else:
                    print(f'{results.status_code}{results.text}')
            else:
                print(f'DB name "{DB}" not in CouchDB.')
        else:
            print(f'User "{login}" not in database.')
    elif chosen == 1:
        DB = input(f'DB name to reset permissions: ')
        reset_DB_Permission = {}
        current_DB_URL = (f'{FULL_URL}/{DB}')
        get_DB = get(current_DB_URL)
        if get_DB.ok:
            security_PERMISSION_URL = (f'{FULL_URL}/{DB}/_security')
            results = put(security_PERMISSION_URL, headers=HEADER_GENERAL,
                          json=reset_DB_Permission)
            if results.ok:
                print(f'DB "{DB}" permission has been reset.')
            else:
                print(f'{results.status_code}{results.text}')
        else:
            print(f'DB name "{DB}" not in CouchDB.')


def list_all_members_users():

    userlist = 0
    ALL_USERS_URL = (f'{FULL_URL}/_users/_all_docs')
    for rows in get(ALL_USERS_URL, headers=HEADER_GENERAL).json()['rows']:
        item = rows['id'].split(':')[1:]
        for user in item:
            print(f'Login: {user}')
        #  print(*item) if item != [] else None  # (*item removes brackets)
        userlist += 1
    print(f'\nTotal: {userlist - 1}')  # does not count "id":"_design/_auth"


def list_all_ADMIN_users():

    adminlist = 0
    ALL_ADMIN_URL = (f'{FULL_URL}//_node/_local/_config/admins/')
    for admin_login in get(ALL_ADMIN_URL, headers=HEADER_GENERAL).json():
        print(f'ADMIN LOGIN: {admin_login}')
        adminlist += 1
    print(f'Total: {adminlist}')


def list_ALL_DBs():

    all_DBs_URL = (f'{FULL_URL}/_all_dbs/')
    get_docs = get(all_DBs_URL)
    for DB in get_docs.json():
        if DB != '_replicator' and DB != '_users':
            print(f'DB name: {DB}')

    print('_replicator and _users are both built-in DBS')


def remove_user():

    login = input('Username for deletion: ')
    USER_URL = (f'{FULL_URL}/_users/org.couchdb.user:{login}')
    get_login = get(USER_URL, headers=HEADER_GENERAL)
    if get_login.status_code == 404:
        print(f'User "{login}" not found.')
    elif get_login.ok:
        revision = get_login.json()['_rev']
        HEADER_DELETE = {'Accept': 'application/json',
                         'Content-Type': 'application/json',
                         'If-Match': revision}
        real_deletion = delete(USER_URL, headers=HEADER_DELETE)
        if real_deletion.ok:
            print(real_deletion.json())


def remove_ADMIN():

    login = input('ADMIN Login for deletion: ')
    ADMIN_URL = (f'{FULL_URL}/_node/_local/_config/admins/{login}')
    get_login = get(ADMIN_URL)
    if get_login.status_code == 404:
        print(f'ADMIN Login "{login}" not found.')
    else:
        real_deletion = delete(ADMIN_URL)
        if real_deletion.ok:
            print(f'ADMIN: {login} deleted.')


def remove_single_DB():

    all_DBs_URL = (f'{FULL_URL}/_all_dbs/')
    get_docs = get(all_DBs_URL)
    for DB in get_docs.json():
        if DB != '_replicator' and DB != '_users':
            print(f'DB name: {DB}')
            DB = input('DB name for deletion: ')
            delete_DB_URL = (f'{FULL_URL}/{DB}')
            delete_all = delete(delete_DB_URL, headers=HEADER_ACCEPT)
            if delete_all.ok:
                print(f'DB "{DB}" removed >> {delete_all.json()}\n')
            else:
                print(f'{delete_all.status_code}{delete_all.json()}')


def remove_all_DBS_and_users():

    all_DBs_URL = (f'{FULL_URL}/_all_dbs/')
    get_docs = get(all_DBs_URL)
    for DB in get_docs.json():
        if DB != '_replicator' and DB != '_users':
            delete_DB_URL = (f'{FULL_URL}/{DB}')
            delete_all = delete(delete_DB_URL, headers=HEADER_ACCEPT)
            if delete_all.ok:
                print(f'DB "{DB}" removed >> {delete_all.json()}\n')
            else:
                print(f'{delete_all.status_code}{delete_all.json()}')

    ALL_USERS_URL = (f'{FULL_URL}/_users/_all_docs')
    for rows in get(ALL_USERS_URL, headers=HEADER_GENERAL).json()['rows']:
        revision = rows['value']['rev']
        item = rows['id'].split(':')[1:]
        for user in item:
            print(f'Login: {user}')
            USER_URL = (f'{FULL_URL}/_users/org.couchdb.user:{user}')
            HEADER_DELETE = {'Accept': 'application/json',
                             'Content-Type': 'application/json',
                             'If-Match': revision}
            real_deletion = delete(USER_URL, headers=HEADER_DELETE)
            if real_deletion.ok:
                print(f'User "{user}" removed >> {real_deletion.json()}')


def main_menu():

    global chosen, menu_loop

    choices = ["[x] Create regular users / DBs from file (batch)",
               "[x] Create regular user",
               "[x] Change regular user's password",
               "[x] List all regular users",
               "[x] Remove a regular user",
               "[x] Create DB",
               "[x] Set DB permission for specific user",
               "[x] List all DBs",
               "[x] Remove all users DBs and its associated users",
               "[x] Remove a single DB",
               "[x] Create ADMIN user / Change password",
               "[x] Remove an ADMIN user",
               "[x] List all ADMIN users",
               "[x] Quit program"]

    print(f"{''}\n")
    chosen = TerminalMenu(menu_entries=choices,
                          title=f"{'-' * 16} AVAILABLE OPTIONS {'-' * 16}",
                          menu_cursor="> ",
                          menu_cursor_style=("fg_red", "bold"),
                          menu_highlight_style=("bg_black", "fg_red"),
                          cycle_cursor=True).show()

    menu_loop = True
    return chosen, menu_loop


if __name__ == "__main__":

    try:

        while True:
            main_menu()
            if chosen == 0:
                create_all_users_batch()
            elif chosen == 1:
                create_members_user()
            elif chosen == 2:
                change_user_password()
            elif chosen == 3:
                list_all_members_users()
            elif chosen == 4:
                remove_user()
            elif chosen == 5:
                create_DB()
            elif chosen == 6:
                set_members_DB_permission()
            elif chosen == 7:
                list_ALL_DBs()
            elif chosen == 8:
                remove_all_DBS_and_users()
            elif chosen == 9:
                remove_single_DB()
            elif chosen == 10:
                create_ADMIN_change_password()
            elif chosen == 11:
                remove_ADMIN()
            elif chosen == 12:
                list_all_ADMIN_users()
            elif chosen == 13:
                break

    except (ValueError, KeyboardInterrupt) as error:
        exit(f'Error >> {error}')
