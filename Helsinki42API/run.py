# # Max requests is 20 per minute

from intra import ic

# Specify Codam as campus_id
campus_id = 14

vela_coalition_id = 60
cetus_coalition_id = 59
pyxis_coalition_id = 58

# #Example users
# Anj = 63997 (Cetus)
# Maarten = 74797 (Pyxis)
# Peer = 57975 (Vela)
# Turlough = 64081 (Vela)
# Lindsay = 64068 (Vela)

temp_student_id = 64068
temp_student_login = "limartin"

# Title IDs:
# 321 = Il Maestro %login
# 82 = [DEPRECATED] %login

# example = Captain %login (1st)
# example = Commodore %login (2nd)
# etc
# example = Landlubber %login (F Tier)

def main():
    print("Program started")
    temp_id = translate_login_to_id("tmullan")
    # fetch_filtered_students()
    # fetch_campus_students(campus_id)
    # who_is_id(temp_student_id)
    # who_is_login(temp_student_login)
    # fetch_coalition_info_by_id(temp_student_id)
    # fetch_student_info(temp_student_id)
    # get_all_users_in_coalition(vela_coalition_id)
    fetch_students_titles(temp_id)
    what_is_title(82)


# Fetch list of all students
def fetch_filtered_students():
    print("Fetching student IDs based on the filters set:")
    ic.progress_bar = True
    payload = {
        "filter[campus_id]": campus_id
    }
    all_students = ic.pages_threaded("campus_users", params=payload)
    for user in all_students:
        print(user['id'])


# FETCH CAMPUS USERS:
def fetch_campus_students(campus):
    print("Fetching all students from specified campus:")
    ic.progress_bar = True
    payload = {
        "range[login]": "4,zzz",
        "sort": "login"
    }
    all_students = ic.pages_threaded("campus/" + str(campus) + "/users", params=payload)
    for entry in all_students:
        print(f"{entry['login']} == {entry['id']}")


def who_is_id(student_id):
    print("Finding the intra login associated with that ID:")
    payload = {
        "filter[id]": student_id,
        "range[login]": "4,zzz",
        "sort": "login"
    }
    specific_user = ic.pages_threaded("campus/" + str(campus_id) + "/users", params=payload)
    for entry in specific_user:
        print(f"{entry['id']} is {entry['login']}")


def who_is_login(login):
    print("Finding the id for the login specified:")
    payload = {
        "filter[login]": login,
        "range[login]": "4,zzz",
        "sort": "login"
    }
    specific_user = ic.pages_threaded("campus/" + str(campus_id) + "/users", params=payload)
    for entry in specific_user:
        print(f"{entry['login']} is {entry['id']}")


def translate_login_to_id(login) -> int:
    print("Returning id for the login specified.")
    payload = {
        "filter[login]": login,
        "range[login]": "4,zzz",
        "sort": "login"
    }
    specific_user = ic.pages_threaded("campus/" + str(campus_id) + "/users", params=payload)
    if specific_user:
        return specific_user[0]['id']
    else:
        print("Error translating id from login")
        return 0


# GET /v2/users/:user_id/coalitions_users
def fetch_coalition_info_by_id(student_id):
    print("Fetching coalition info for specified id:")
    payload = {
    }
    user_coalition_response = ic.get("users/" + str(student_id) + "/coalitions_users", params=payload)
    data = user_coalition_response.json()
    for entry in data:
        print(entry)


# Get all users in coalition
def get_all_users_in_coalition(coalition_id):
    print("Fetching all students from specified coalition:")
    payload = {
        "sort": "user_id"
    }
    user_coalition_response = ic.pages_threaded("coalitions/" + str(coalition_id) + "/coalitions_users", params=payload)
    data = user_coalition_response
    count = 0
    # for entry in data:
    #     entry['rank'] = 0
    for entry in data:
        print(entry)
        count = count + 1
    print(f"Total students in this coalition: {count}")


# FETCH A SINGLE USER:
def fetch_student_info(student_id):
    print("Fetching all general info on student specified by id:")
    payload = {
        "filter[id]": student_id
    }
    specific_user = ic.pages_threaded("users", params=payload)
    for entry in specific_user:
        print(entry)


def fetch_students_titles(student_id):
    print("Fetching all titles the specified student has access to:")
    payload = {
    }
    specific_user = ic.pages_threaded("users/" + str(student_id) + "/titles_users", params=payload)
    for entry in specific_user:
        print(entry)


def what_is_title(title_id):
    print("Printing selected title's info:")
    payload = {
    }
    title_details = ic.pages_threaded("titles/" + str(title_id), params=payload)
    print(title_details)


def who_has_title(title_id):
    # TODO

if __name__ == "__main__":
    main()
