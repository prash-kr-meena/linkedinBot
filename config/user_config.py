
open_job_links = [
    "https://www.linkedin.com/jobs/view/3638053478",
    "https://www.linkedin.com/jobs/view/3638057256",
    "https://www.linkedin.com/jobs/view/3638053484",
    "https://www.linkedin.com/jobs/view/3637365200"
]

message_for_1st_connection = "Test message For 1st"
message_for_2nd_connection = "Test message for 2nd"
message_for_3rd_connection = "Test message for 3rd"

search_people_query = "talent"

# Note messages will be done in priority, ie firstly priority will be given to 1st connection
# then to 2nd connection and then 3rd connection
message_to_1st_connections = True
message_to_2nd_connections = True
message_to_3rd_connections = True

# Number of persons to message from a company
NUMBER_OF_PEOPLE_TO_MESSAGE_OF_A_COMPANY = 25
# Note: Don't reset this constant in code, if you want to change assign it to some variable and change that variable

# The idea is that one should apply to max 4 companies
# (ie job_links can be any number, its just total should be from only 4 companies)
# so the total messages sent will be 25 * 4 = 100
# where 100 will not be too much messages
