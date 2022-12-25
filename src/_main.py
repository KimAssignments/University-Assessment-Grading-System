
from tabulate import tabulate
from textwrap import dedent
import sys

from ._app import User
from ._log_utils import logger
from ._sub_app import Courses, Students, Results
from ._utils import cls

courses = Courses()
students = Students()
results = Results()
user = User()


def login_screen():
    global LOGIN_USER
    while True:
        cls()
        print(dedent(f'''
            \tPress CTRL+C to quit the program
            \t---------------------------------
            \t    __.__ Login Screen __.__
            \t---------------------------------\n
        '''))

        # Ask for login ID
        LOGIN_USER = input('\n\tLogin ID: ').upper()

        # If login ID is empty, ask again
        if LOGIN_USER.strip() == '':
            input('\n\tPlease enter a valid ID\n\tPress Enter to continue')
            continue

        # If login ID is not empty, check if it exists in the database
        # If it exists, ask for password
        if user.check(username=LOGIN_USER):
            LOGIN_PASS = input('\n\tPassword: ')

            # If password is correct, login
            if user.login(username=LOGIN_USER, password=LOGIN_PASS):
                break
            # If password is incorrect, return to login screen
            else:
                input('\n\tWrong password\n\tPress Enter to continue')
                continue

        # If login ID does not exist, ask for password twice to register
        elif not user.check(username=LOGIN_USER):
            cls()
            print(dedent(f'''
                \tPress CTRL+C to quit the program
                \t---------------------------------
                \t    __.__ Register __.__
                \t      As {LOGIN_USER}
                \t---------------------------------\n
            '''))

            password = input('\n\tPassword: ')
            password_again = input('\n\tPassword (again): ')

            # If passwords do not match, return to login screen
            if password != password_again:
                input('\n\tPasswords do not match\n\tPress Enter to continue')
                continue
            # If passwords match, register
            else:
                if not user.register(LOGIN_USER, password):
                    input('\n\tPress Enter to continue')
                    continue

                break


def menu_screen() -> callable:
    options: dict = {
        "1": courses_screen,
        "2": students_screen,
        "3": results_screen,
        "4": user_screen,
    }

    while True:
        cls()
        print(dedent(f'''
            Press CTRL+C return to login screen
            ---------------------------------
                __.__ Menu __.__
                Welcome {LOGIN_USER}
            ---------------------------------\n
        '''))

        # Print options
        print('\n'.join(
            [
                f'{k}: {v.__name__ if callable(v) else v}'
                for k, v in options.items()
            ]
        ))

        # Ask for option
        choice = input('\n\tOption: ')

        # If option not in the keys, ask again
        if choice not in options.keys():
            input('\n\tPlease enter a valid option\n\tPress Enter to continue')
            continue

        # Return the function
        return options.get(choice)

def courses_screen() -> callable:
    options: dict = {
        "1": courses_add,
        "2": courses_remove,
        "3": courses_update,
        "4": courses_search,
    }

    while True:
        cls()
        print(dedent(f'''
            Press CTRL+C return to menu screen
            ---------------------------------
                __.__ Courses __.__
                Welcome {LOGIN_USER}
            ---------------------------------\n
        '''))

        # Print options
        print('\n'.join(
            [
                f'{k}: {v.__name__ if callable(v) else v}'
                for k, v in options.items()
            ]
        ))

        # Ask for option
        choice = input('\n\tOption: ')

        # If option not in the keys, ask again
        if choice not in options.keys():
            input('\n\tPlease enter a valid option\n\tPress Enter to continue')
            continue

        # Return the function
        return options.get(choice)

def courses_add():
    while True:
        cls()
        print(dedent(f'''
            Press CTRL+C return to courses screen
            ---------------------------------
                __.__ Add Course __.__
                Welcome {LOGIN_USER}
            ---------------------------------\n
        '''))

        # Ask for course code
        course_code = input('\n\tCourse Code: ')

        # If course code is empty, ask again
        if course_code.strip() == '':
            input('\n\tPlease enter a valid course code\n\tPress Enter to continue')
            continue

        # If course code is not empty, add course
        else:
            courses.append(course_code)
            input('\n\tPress Enter to continue')

def courses_remove():
    while True:
        cls()
        print(dedent(f'''
            Press CTRL+C return to courses screen
            ---------------------------------
                __.__ Remove Course __.__
                Welcome {LOGIN_USER}
            ---------------------------------\n
        '''))

        # Ask for course code
        course_code = input('\n\tCourse Code: ')

        # If course code is empty, ask again
        if course_code.strip() == '':
            input('\n\tPlease enter a valid course code\n\tPress Enter to continue')
            continue

        # If course code is not empty, remove course
        else:
            courses.remove(course_code)
            input('\n\tPress Enter to continue')

def courses_update():
    while True:
        cls()
        print(dedent(f'''
            Press CTRL+C return to courses screen
            ---------------------------------
                __.__ Update Course __.__
                Welcome {LOGIN_USER}
            ---------------------------------\n
        '''))

        # Ask for course code
        course_code = input('\n\tCourse Code: ')

        # If course code is empty, ask again
        if course_code.strip() == '':
            input('\n\tPlease enter a valid course code\n\tPress Enter to continue')
            continue

        # If course code is not empty, check if it exists in the database
        df = courses.view(course_code)
        # If dataframe is empty, ask again for new course code
        if df.empty:
            input('\n\tCourse not found\n\tPress Enter to continue')
            continue

        while True:
            cls()
            print(dedent(f'''
                Press CTRL+C return to course update screen
                ---------------------------------
                    __.__ Update Course __.__
                    Welcome {LOGIN_USER}
                ---------------------------------\n
            '''))

            # Print course details
            print(
                tabulate(
                    df,
                    headers='keys',
                    tablefmt='psql'
                )
            )

            try:
                # Ask for key to update
                key = input('\n\tEnter the key to update: ')
                # If key is not whitelisted, ask again
                if key not in courses.children:
                    input('\n\tPlease enter a valid key\n\tPress Enter to continue')
                    continue

                value = input('\n\tEnter the new value: ')
                courses.edit(course_code, **{key: value})
                input('\n\tPress Enter to continue')
                continue

            # If user presses CTRL+C, return to course update screen
            except KeyboardInterrupt:
                break

def courses_search():
    while True:
        cls()
        print(dedent(f'''
            Press CTRL+C return to courses screen
            ---------------------------------
                __.__ Search Course __.__
                Welcome {LOGIN_USER}
            ---------------------------------\n
        '''))

        # Ask for course code
        course_code = input('\n\tCourse Code: ')

        # Search for course code and print results
        df = courses.search(course_code)
        print(
            tabulate(
                df,
                headers='keys',
                tablefmt='psql',
                missingval='N/A',
            )
        )

        input('\n\tPress Enter to continue')
        continue

def students_screen() -> callable:
    options: dict = {
        "1": students_add,
        "2": students_remove,
        "3": students_update,
        "4": students_search,
    }

    while True:
        cls()
        print(dedent(f'''
            Press CTRL+C return to menu screen
            ---------------------------------
                __.__ Students __.__
                Welcome {LOGIN_USER}
            ---------------------------------\n
        '''))

        # Print options
        print('\n'.join(
            [
                f'{k}: {v.__name__ if callable(v) else v}'
                for k, v in options.items()
            ]
        ))

        # Ask for option
        choice = input('\n\tOption: ')

        # If option not in the keys, ask again
        if choice not in options.keys():
            input('\n\tPlease enter a valid option\n\tPress Enter to continue')
            continue

        # Return the function
        return options.get(choice)

def students_add():
    while True:
        cls()
        print(dedent(f'''
            Press CTRL+C return to students screen
            ---------------------------------
                __.__ Add Student __.__
                Welcome {LOGIN_USER}
            ---------------------------------\n
        '''))

        # Ask for student code
        student_code = input('\n\tStudent Code: ')

        # If student code is empty, ask again
        if student_code.strip() == '':
            input('\n\tPlease enter a valid student code\n\tPress Enter to continue')
            continue

        # If student code is not empty, add student
        else:
            students.append(student_code)
            input('\n\tPress Enter to continue')

def students_remove():
    while True:
        cls()
        print(dedent(f'''
            Press CTRL+C return to students screen
            ---------------------------------
                __.__ Remove Student __.__
                Welcome {LOGIN_USER}
            ---------------------------------\n
        '''))

        # Ask for student code
        student_code = input('\n\tStudent Code: ')

        # If student code is empty, ask again
        if student_code.strip() == '':
            input('\n\tPlease enter a valid student code\n\tPress Enter to continue')
            continue

        # If student code is not empty, remove student
        else:
            students.remove(student_code)
            input('\n\tPress Enter to continue')

def students_update():
    while True:
        cls()
        print(dedent(f'''
            Press CTRL+C return to students screen
            ---------------------------------
                __.__ Update Student __.__
                Welcome {LOGIN_USER}
            ---------------------------------\n
        '''))

        # Ask for student code
        student_code = input('\n\tStudent Code: ')

        # If student code is empty, ask again
        if student_code.strip() == '':
            input('\n\tPlease enter a valid student code\n\tPress Enter to continue')
            continue

        # If student code is not empty, check if it exists in the database
        df = students.view(student_code)
        # If dataframe is empty, ask again for new student code
        if df.empty:
            input('\n\tStudent not found\n\tPress Enter to continue')
            continue

        while True:
            cls()
            print(dedent(f'''
                Press CTRL+C return to student update screen
                ---------------------------------
                    __.__ Update Student __.__
                    Welcome {LOGIN_USER}
                ---------------------------------\n
            '''))

            # Print student details
            print(
                tabulate(
                    df,
                    headers='keys',
                    tablefmt='psql'
                )
            )

            try:
                # Ask for key to update
                key = input('\n\tEnter the key to update: ')
                # If key is not whitelisted, ask again
                if key not in students.children:
                    input('\n\tPlease enter a valid key\n\tPress Enter to continue')
                    continue

                value = input('\n\tEnter the new value: ')
                students.edit(student_code, **{key: value})
                input('\n\tPress Enter to continue')
                continue

            # If user presses CTRL+C, return to student update screen
            except KeyboardInterrupt:
                break

def students_search():
    while True:
        cls()
        print(dedent(f'''
            Press CTRL+C return to students screen
            ---------------------------------
                __.__ Search Student __.__
                Welcome {LOGIN_USER}
            ---------------------------------\n
        '''))

        # Ask for student code
        student_code = input('\n\tStudent Code: ')

        # Search for student code and print results
        df = students.search(student_code)
        print(
            tabulate(
                df,
                headers='keys',
                tablefmt='psql',
                missingval='N/A',
            )
        )

        input('\n\tPress Enter to continue')
        continue

def results_screen() -> callable:
    options: dict = {
        "1": results_add,
        "2": results_remove,
        "3": results_update,
        "4": results_search,
    }

    while True:
        cls()
        print(dedent(f'''
            Press CTRL+C return to menu screen
            ---------------------------------
                __.__ Results __.__
                Welcome {LOGIN_USER}
            ---------------------------------\n
        '''))

        # Print options
        print('\n'.join(
            [
                f'{k}: {v.__name__ if callable(v) else v}'
                for k, v in options.items()
            ]
        ))

        # Ask for option
        choice = input('\n\tOption: ')

        # If option not in the keys, ask again
        if choice not in options.keys():
            input('\n\tPlease enter a valid option\n\tPress Enter to continue')
            continue

        # Return the function
        return options.get(choice)

def results_add():
    while True:
        cls()
        print(dedent(f'''
            Press CTRL+C return to results screen
            ---------------------------------
                __.__ Add Result __.__
                Welcome {LOGIN_USER}
            ---------------------------------\n
        '''))

        # Ask for student code and course code
        student_code = input('\n\tStudent Code: ')
        course_code = input('\n\tCourse Code: ')

        # If one of the codes is empty, ask again
        if student_code.strip() == '' or course_code.strip() == '':
            input('\n\tPlease enter a valid student code and course code\n\tPress Enter to continue')
            continue

        # Else, add student code under course
        else:
            results.append(student_code=student_code, course_code=course_code)
            input('\n\tPress Enter to continue')

def results_remove():
    while True:
        cls()
        print(dedent(f'''
            Press CTRL+C return to results screen
            ---------------------------------
                __.__ Remove Result __.__
                Welcome {LOGIN_USER}
            ---------------------------------\n
        '''))

        # Ask for student code and course code
        student_code = input('\n\tStudent Code: ')
        course_code = input('\n\tCourse Code: ')

        # If one of the codes is empty, ask again
        if student_code.strip() == '' or course_code.strip() == '':
            input('\n\tPlease enter a valid student code and course code\n\tPress Enter to continue')
            continue

        # Else, remove student code under course
        else:
            results.delete(student_code=student_code, course_code=course_code)
            input('\n\tPress Enter to continue')

def results_update():
    while True:
        cls()
        print(dedent(f'''
            Press CTRL+C return to results screen
            ---------------------------------
                __.__ Update Result __.__
                Welcome {LOGIN_USER}
            ---------------------------------\n
        '''))

        # Ask for student code and course code
        student_code = input('\n\tStudent Code: ')
        course_code = input('\n\tCourse Code: ')

        # If one of the codes is empty, ask again
        if student_code.strip() == '' or course_code.strip() == '':
            input('\n\tPlease enter a valid student code and course code\n\tPress Enter to continue')
            continue

        # If result code is not empty, check if it exists in the database
        df = results.view(student_code=student_code, course_code=course_code)
        # If dataframe is empty, ask again for new result code
        if df.empty:
            input('\n\tResult not found\n\tPress Enter to continue')
            continue

        while True:
            cls()
            print(dedent(f'''
                Press CTRL+C return to result update screen
                ---------------------------------
                    __.__ Update Result __.__
                    Welcome {LOGIN_USER}
                ---------------------------------\n
            '''))

            # Print result details
            print(
                tabulate(
                    df,
                    headers='keys',
                    tablefmt='psql'
                )
            )

            try:
                # Ask for key to update
                key = input('\n\tEnter the key to update: ')
                # If key is not whitelisted, ask again
                if key not in results.children:
                    input('\n\tPlease enter a valid key\n\tPress Enter to continue')
                    continue

                value = input('\n\tEnter the new value: ')
                results.edit(student_code=student_code, course_code=course_code, **{key: value})
                input('\n\tPress Enter to continue')
                continue

            # If user presses CTRL+C, return to result update screen
            except KeyboardInterrupt:
                break

def results_search():
    while True:
        cls()
        print(dedent(f'''
            Press CTRL+C return to results screen
            ---------------------------------
                __.__ Search Result __.__
                Welcome {LOGIN_USER}
            ---------------------------------\n
        '''))

        # Ask for result code
        code = input('\n\tAny Code: ')

        # Search for result code and print results
        df = results.search(code)
        print(
            tabulate(
                df,
                headers='keys',
                tablefmt='psql',
                missingval='N/A',
            )
        )

        input('\n\tPress Enter to continue')
        continue

def user_screen() -> callable:
    options: dict = {
        "1": user_change_password,
    }

    while True:
        cls()
        print(dedent(f'''
            Press CTRL+C return to menu screen
            ---------------------------------
                __.__ User management __.__
                Welcome {LOGIN_USER}
            ---------------------------------\n
        '''))

        # Print options
        print('\n'.join(
            [
                f'{k}: {v.__name__ if callable(v) else v}'
                for k, v in options.items()
            ]
        ))

        # Ask for option
        choice = input('\n\tOption: ')

        # If option not in the keys, ask again
        if choice not in options.keys():
            input('\n\tPlease enter a valid option\n\tPress Enter to continue')
            continue

        # Return the function
        return options.get(choice)

def user_change_password():
    while True:
        cls()
        print(dedent(f'''
            Press CTRL+C return to menu screen
            ---------------------------------
                __.__ User Change Password __.__
                Welcome {LOGIN_USER}
            ---------------------------------\n
        '''))

        # Ask for old and new passwords
        old_pass = input('\n\tOld Password: ')

        # If old password is incorrect, ask again
        if not user.login(LOGIN_USER, old_pass, silent=True):
            input('\n\tIncorrect password\n\tPress Enter to continue')
            continue

        # Else, ask for new password and change password
        new_pass = input('\n\tNew Password: ')
        user.change_password(LOGIN_USER, old_pass, new_pass)
        input('\n\tPress Enter to continue')
        break


@logger.catch
def main():
    try:
        while True:
            login_screen()
            try:
                while True:
                    function = menu_screen()
                    try:
                        while True:
                            sub_function = function()
                            try:
                                while True:
                                    sub_function()
                            except KeyboardInterrupt:
                                break
                    except KeyboardInterrupt:
                        break
            except KeyboardInterrupt:
                break
    except KeyboardInterrupt:
        sys.exit(0)
