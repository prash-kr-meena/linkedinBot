

open_job_links = [
    "https://www.linkedin.com/jobs/view/3721132004",
    "https://www.linkedin.com/jobs/view/3714309040",
    "https://www.linkedin.com/jobs/view/3704880768",
    "https://www.linkedin.com/jobs/view/3726539082"
]

# --------------------------------------------------------------------

referral_message_for_1st_connection = """
Hey {name}, 
hope this message finds you well.
I am keen to apply for the below opportunity at {company_name}.
A brief chat to learn more and seek your referral would be fantastic.

{job_links}
"""

referral_message_for_2nd_connection = """
Hey {name}, 
hope this message finds you well.
I am keen to apply for the below opportunity at {company_name}.
A brief chat to learn more and seek your referral would be fantastic.

{job_links}
"""

referral_message_for_3rd_connection = """
Hey {name}, 
hope this message finds you well.
I am keen to apply for the below opportunity at {company_name}.
A brief chat to learn more and seek your referral would be fantastic.

{job_links}
"""

# --------------------------------------------------------------------

connection_message_for_1st_connection = "1. hi, how are you {name}"
connection_message_for_2nd_connection = "2. hi, how are you {name}"
connection_message_for_3rd_connection = "3. hi, how are you {name}"

search_people_query = "people"
# search_people_query = "talent"

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
