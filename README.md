# Banzai Technical Challenge

1.	Create a view where a user can upload an excel file with a list of contacts.
2.	The excel file should have Name, Phone Number, and Email Address columns.
3.	When a user uploads a file, the contacts with a phone number should be stored in a model and any contacts without a phone number should be ignored.
4.	When processing the list of contacts, the same email address or phone number cannot be uploaded in a time window of 3 minutes. After 3 minutes have passed, a contact with that email or phone number can be uploaded.
5.	Upon upload, the app should thank the user and notify them that the upload is underway.
6.	The file should be processed in an async celery task.
7.	The original excel file should be stored in S3.

[#] Narvik Aghamalian @ 19/12/2020
