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
# example = Landlubber %login (F)

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
    # fetch_students_titles(temp_id)
    # what_is_title(82)
    # who_has_title(321)
    give_coalition_titles(vela_coalition_id)


def give_coalition_titles(coalition_id):
    # Make snapshot of all coalition members
    # (reduces number of API calls, prevents ranks changing whilst titles still being calculated)
    snapshot_bundle = make_coalition_state_snapshot(coalition_id)
    # Determine student's title based on rank (calculate 'abstract' titles)
    student_rank_info = calculate_coalition_ranks(snapshot_bundle)
    # Sort the list by rank because why not
    student_rank_info = sort_by_rank(student_rank_info)
    # Fetch title_id based on abstract rank and title_config.yml
    student_rank_info = append_title_ids(student_rank_info, coalition_id)
    #TODO make append_title_ids

    # (Optional) add readable intra login to student_rank_info
    if 1 == 1:
        student_rank_info = append_login_names(student_rank_info)
        for entry in student_rank_info:
            print(entry)

    # Check all custom 'rank titles' -> for all ids that don't belong, bestow that ID a new title
    # When you bestow a 'rank' title, remove all other 'rank titles'


def make_coalition_state_snapshot(coalition_id) -> object:
    snapshot = get_all_users_in_coalition(coalition_id)
    number_of_students = 0
    lowest_rank = 1
    for entry in snapshot:
        number_of_students += 1
        if entry['rank'] > lowest_rank:
            lowest_rank = entry['rank']
    snapshot_bundle = [snapshot, number_of_students, lowest_rank]
    return snapshot_bundle


def calculate_coalition_ranks(snapshot_bundle):
    coalition_snapshot = snapshot_bundle[0]
    number_of_students = snapshot_bundle[1]
    lowest_rank = snapshot_bundle[2]
    x = 0
    student_rank_info = [[] for x in range(number_of_students)]
    x = 0
    for entry in coalition_snapshot:
        student_rank_info[x] = [entry['user_id'], entry['rank'], get_abstract_title(entry['rank'], lowest_rank), "title_id", "username"]
        x += 1
    return student_rank_info


# Returns a symbol that represents the kind of title the user should have
# Either a value between 1 and 'n', for the top n individual ranks,
# or a letter A-F for the tiered titles
def get_abstract_title(current_rank, lowest_rank):
    individual_ranks = 30
    # Students at the lowest rank default to the lowest title
    if current_rank >= lowest_rank:
        return "F"
    # The top 'individual_ranks' students that are above lowest rank have a unique title
    if current_rank <= individual_ranks:
        return str(current_rank)
    # All students between the top 30 and the lowest rank are carved up into 5 tiers
    tier_size = (lowest_rank - individual_ranks) / 5
    if current_rank <= individual_ranks + (tier_size * 1):
        return "A"
    if current_rank <= individual_ranks + (tier_size * 2):
        return "B"
    if current_rank <= individual_ranks + (tier_size * 3):
        return "C"
    if current_rank <= individual_ranks + (tier_size * 4):
        return "D"
    return "E"


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


def append_login_names(student_rank_info):
    print("Fetching all students from specified campus:")
    ic.progress_bar = True
    payload = {
        "range[login]": "4,zzz",
        "sort": "login"
    }
    all_students = ic.pages_threaded("campus/" + str(campus_id) + "/users", params=payload)
    for entry in student_rank_info:
        for kvp in all_students:
            if kvp['id'] == entry[0]:
                entry[4] = kvp['login']
    return student_rank_info


def sort_by_rank(student_rank_info):
    # reverse = None (Sorts in Ascending order)
    # key is set to sort using second element of
    # sublist lambda has been used
    return sorted(student_rank_info, key=lambda x: x[1])


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
def get_all_users_in_coalition(coalition_id) -> object:
    # print("Fetching all students from specified coalition:")
    payload = {
        "sort": "user_id"
    }
    data = ic.pages_threaded("coalitions/" + str(coalition_id) + "/coalitions_users", params=payload)
    return data


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


# Shows all students that have the specified title, regardless of whether it is 'selected'
def who_has_title(title_id):
    print("Printing selected title's info:")
    payload = {
        # Doesn't take any params so the below is useless
        "filter[campus_id]": campus_id,
        "sort": "user_id"
    }
    title_details = ic.pages_threaded("titles/" + str(title_id) + "/titles_users", params=payload)
    for entry in title_details:
        print(entry['user_id'])


if __name__ == "__main__":
    main()
