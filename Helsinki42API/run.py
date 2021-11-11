# # Max requests is 20 per minute

from intra import ic

# Specify Codam as campus_id
campus_id = 14

# #Fetch list of all students
# payload = {
#     "filter[campus_id]":campus_id
# }
# all_students = ic.pages_threaded("campus_users", params=payload)

# for user in all_students:
#     print(user['id'])
#     print(user)

# # #Example user
# # random_user_id = "36085" #Coalition 19
# # random_user_id = "18510" #Coalition 16
# # random_user_id = "45658" #Coalition 34
# # random_user_id = "38105" #Coalition 5
# # random_id = "34455" 
# #  GET /v2/users/:user_id/coalitions_users 
# payload = {
# }
# user_coalition_response = ic.get("users/" + random_user_id + "/coalitions_users", payload)
# data = user_coalition_response.json()
# for entry in data:
#     print(entry)


# # Get all users in coalition X (X == 19)
# user_coalition_response = ic.pages_threaded("coalitions/19/coalitions_users", payload)
# data = user_coalition_response
# print(data)

# #FETCH A SINGLE USER:
# user_id = "34455"
# payload = {
# 	"filter[id]":user_id
# }
# specific_user = ic.pages_threaded("users", params=payload)
# for entry in specific_user:
#     print(entry['login'])    

#FETCH CAMPUS USERS:
ic.progress_bar=True

payload = {
	"range[login]":"4,zzz"
}
specific_user = ic.pages_threaded("campus/14/users", params=payload)
for entry in specific_user:
    print(f"{entry['login']} == {entry['id']}") 



# # user_coalition_response = ic.pages_threaded("coalitions_users", payload)

# # if user_coalition_response.status_code == 200: # Is the status OK?
# data = user_coalition_response

# print(data)
# # for entry in data:
# #     print(entry)

# print(user_coalition_response.status_code)