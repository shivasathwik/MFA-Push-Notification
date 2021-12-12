# MFA-Push-Notification
MFA Authentication using Browser Push Notification using FCM

This project will illustrate the way how the MFA can be achieved using the browser push notification. This project has three components

Client Application:  The client application is the user's entry point, capable of validating the user's identification and allowing the user to access the resources to which he has access or capturing new user details via registration. The Authenticator app is pooled by the client application, and the login attempt is blocked or successful dependent on the user action.
Notification API:  The Notification API is a service that allows us to perform all CRUD operations on the user database (GCP MSSQL) and the GCP Cloud Store, which stores the user login session and records the activity on the authenticator app. The user browser token data is also captured by the Notification API, which can be used to trigger a browser push notification utilizing the Google Firebase Messaging (FCM) service.
Authenticator Application: The Authenticator Application is a web application that runs in the user's browser and receives notifications from the notification API whenever the user logs in to the client application. We use the concept of a service worker to do this. A service worker is a script that runs in the background on the client's browser and assists us in doing background sync as well as providing browser push notification capability. Only once the user has given permission for the program to transmit notifications from the specific application, in this case the Authenticator application, will the client browser token be kept in the database.
Firebase Cloud Messaging (FCM): Google's Firebase Cloud Messaging is a cross-platform messaging service that allows us to send messages for free while also notifying the user about the login attempt and obtaining their agreement
Firestore: This is the flow's NoSQL database, which aids in storing and retrieving user login actions, as well as capturing user activity on the authenticator app and allowing the notification API to act depending on that action.
GCP MSSQL: This is the cloud relation database which is used to store the user details.





