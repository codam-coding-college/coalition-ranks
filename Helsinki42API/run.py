# # Max requests is 20 per minute
import os
import yaml

from intra import ic

# Specify Codam as campus_id
campus_id = 14
staff_privileges = 0
print_summary = 0
vela_coalition_id = 60
# Vela title IDs = 424-459
cetus_coalition_id = 59
pyxis_coalition_id = 58


def main():
    print("Program started")
    give_coalition_titles(vela_coalition_id)


def give_coalition_titles(coalition_id):
    # First we make a snapshot of the current state of the coalition and its members with one API call
    # (this reduces the overall number of API calls & prevents ranks changing whilst titles are still being calculated)
    snapshot_bundle = make_coalition_state_snapshot(coalition_id)

    # Then we make a 2D array,
    # per student it has fields for a student's id, rank, 'abstract_title', intra title_id, and username.
    # The actual title_id and username are added later, these initially just have placeholders.
    student_rank_info = make_student_rank_info(snapshot_bundle)

    # Before we can translate the users 'abstract_title' (that indicates what type of title the user should have)
    # to the users actual title_id, we must fetch the title_ids for this coalition. We store these in title_id_array.
    title_id_array = make_title_id_array(coalition_id)

    # Now we add the title_id to the entries in student_rank_info, based on those specified by title_id_array
    student_rank_info = append_title_ids(student_rank_info, title_id_array)

    # Next we fetch information about who has what titles, retrieving two separate 2D arrays from the same API call
    title_status_bundle = make_title_status_array(title_id_array)

    # The first 2D array we retrieve from title_status_bundle is ids_that_have_title.
    # It contains all the student_ids that already have one of our custom coalition titles,
    # all ids that have the highest title are saved at the first index
    # and a list of all ids that have the title_id corresponding to the lowest rank are saved in the last (36th) index.
    ids_that_have_title = title_status_bundle[0]

    # The second 2D array we retrieve from title_status_bundle is title_deletion_ids.
    # Intra makes a unique id for every student_id that has a title_id, and this unique id is needed to delete that
    # instance of the title for that user.
    # These 'deletion_ids' are saved separately and passed to the relevant function when a title needs to be removed.
    title_deletion_ids = title_status_bundle[1]

    # First we give all students the title they should have
    # (this means all students always have at least one custom coalition title, and are never title-less).
    # We only explicitly give a student a new title if they don't have it already, however.
    bestow_all_titles(student_rank_info, title_id_array, ids_that_have_title)

    # Then we check all our custom coalition rank based titles, and delete any titles a user should not have anymore.
    remove_unwarranted_titles(student_rank_info, title_id_array, ids_that_have_title, title_deletion_ids)

    # To print an optional summary of who has what title, set print_summary to 1 in the above global variables.
    # This does slow down the program however,
    # as it makes a separate API call to fetch the login names of all un-anonymised Codam students.
    if print_summary == 1:
        student_rank_info = append_login_names(student_rank_info)
        for entry in student_rank_info:
            print(entry)


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


def get_all_users_in_coalition(coalition_id) -> object:
    payload = {
        "sort": "user_id"
    }
    data = ic.pages_threaded("coalitions/" + str(coalition_id) + "/coalitions_users", params=payload)
    return data


def make_student_rank_info(snapshot_bundle):
    coalition_snapshot = snapshot_bundle[0]
    number_of_students = snapshot_bundle[1]
    lowest_rank = snapshot_bundle[2]
    student_rank_info = [[] for _ in range(number_of_students)]
    x = 0
    for entry in coalition_snapshot:
        student_rank_info[x] = [entry['user_id'], entry['rank'], get_abstract_title(entry['rank'], lowest_rank),
                                "title_id", "username"]
        x += 1
    # Sort the list by rank because why not
    student_rank_info = sort_by_rank(student_rank_info)
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


def sort_by_rank(student_rank_info):
    return sorted(student_rank_info, key=lambda x: x[1])


def make_title_id_array(coalition_id):
    title_id_array = [0 for _ in range(36)]
    coalition_spec = 'vela'
    if coalition_id == cetus_coalition_id:
        coalition_spec = 'cetus'
    if coalition_id == pyxis_coalition_id:
        coalition_spec = 'pyxis'
    base_dir = os.path.dirname(os.path.realpath(__file__))
    with open(base_dir + '/title_config.yml', 'r') as cfg_stream:
        config = yaml.load(cfg_stream, Loader=yaml.BaseLoader)
        x = 0
        for _ in range(36):
            title_id_array[x] = config['all_titles'][coalition_spec][str(x + 1)]
            x += 1
    return title_id_array


def append_title_ids(student_rank_info, title_id_array):
    for entry in student_rank_info:
        entry[3] = make_abstract_title_concrete(entry[2], title_id_array)
    return student_rank_info


def make_abstract_title_concrete(abstract_title, title_array):
    if abstract_title == "A":
        return title_array[30]
    if abstract_title == "B":
        return title_array[31]
    if abstract_title == "C":
        return title_array[32]
    if abstract_title == "D":
        return title_array[33]
    if abstract_title == "E":
        return title_array[34]
    if abstract_title == "F":
        return title_array[35]
    abstract_title = int(abstract_title)
    if abstract_title <= 30:
        return title_array[abstract_title - 1]


def make_title_status_array(title_id_array):
    title_status_array = [[] for _ in range(36)]
    title_status_ids = [[] for _ in range(36)]
    x = 0
    for entry in title_id_array:
        title_bundle = who_has_title(entry)
        title_status_array[x] = title_bundle[0]
        title_status_ids[x] = title_bundle[1]
        x += 1
    title_bundle = [title_status_array, title_status_ids]
    return title_bundle


# Shows all students that have the specified title, regardless of whether it is 'selected'
def who_has_title(title_id):
    payload = {
    }
    title_details = ic.pages_threaded("titles/" + str(title_id) + "/titles_users", params=payload)
    user_id_array = []
    id_array = []
    for entry in title_details:
        user_id_array.append(entry['user_id'])
        id_array.append(entry['id'])
    id_array_bundle = [user_id_array, id_array]
    return id_array_bundle


def bestow_all_titles(student_rank_info, title_id_array, title_status_array):
    for student in student_rank_info:
        give_title_if_not_owned(student, title_id_array, title_status_array)
    return student_rank_info


def give_title_if_not_owned(student, title_id_array, title_status_array):
    student_user_id = student[0]
    student_title_id = student[3]
    title_id_index = get_title_index(student_title_id, title_id_array)
    for entry in title_status_array[title_id_index]:
        if entry == student_user_id:
            return 0
    give_title(student_title_id, student_user_id)
    return 1


def get_title_index(title_id, title_id_array):
    x = 0
    for entry in title_id_array:
        if entry == title_id:
            return x
        x += 1
    return x


def give_title(title_id, student_id):
    title_id = int(title_id)
    if staff_privileges == 1:
        payload = {
            "titles_user[title_id]": title_id,
            "titles_user[user_id]": student_id
        }
        ic.post("titles_users", params=payload)
    else:
        print(f"Attempting to give title_id {title_id} to student with id {student_id}")


def remove_unwarranted_titles(student_rank_info, title_id_array, ids_that_have_title, title_deletion_ids):
    title_index = 0
    for list_of_ids in ids_that_have_title:
        given_title = title_id_array[title_index]
        title_list_to_destroy_from = title_deletion_ids[title_index]
        for student_id in list_of_ids:
            match_id_to_title(student_id, student_rank_info, given_title, ids_that_have_title[title_index],
                              title_list_to_destroy_from)
        title_index += 1


def match_id_to_title(student_id, student_rank_info, given_title, list_of_ids, title_list_to_destroy_from):
    for student in student_rank_info:
        if student[0] == student_id:
            if student[3] == given_title:
                return 0
    index = get_student_index(student_id, list_of_ids)
    title_to_destroy = int(title_list_to_destroy_from[index])
    remove_title(given_title, student_id, title_to_destroy)
    return 1


def remove_title(title_id, student_id, title_to_destroy):
    if staff_privileges == 1:
        payload = {
        }
        ic.delete(f"titles_users/{title_to_destroy}", params=payload)
    else:
        print(f"Attempting to remove title_id {title_id} from student with id {student_id} (value {title_to_destroy})")


def get_student_index(student_id, list_of_ids):
    x = 0
    for index in list_of_ids:
        if index == student_id:
            return x
        x += 1
    return 0


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


if __name__ == "__main__":
    main()
