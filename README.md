# Web-dev-CA2
Repository for Web development CA2. 

Project Developed by Ravi Rameshkumar Mishra. 

The project has a basic functionality of storing posts/thoughts by users who create an account on the webpage. Any user who wants to use the functionality can sign-up on the page and start their usage. 
Webpage has a user-friendly UI where the user can add, view, edit or delete their posts. All the posts are kept anonymous.
There is an Admin user for the webapp which is the only person who can see/view all the users posts as well as the login ID's. They can add posts of their own aswell.

## **SETUP**
The project has 2 crucial Python files called **'main.py'** and **'database_setup.py'** which are required to run the app. 
Any type of complier/IDE can be used to run the files. I have used Pycharm for my project. 
This is a python based project which will host our WebApp using Flask. The version is defined in the 'requirements.txt' file.
Along with these Python files, there are multiple HTML files that are complied in the 'Templates' folders which will define the function of the WebApp.

For the structure of the webpage, I have used a free-source template called 'SB Admin 2'. This template consists of files in CSS and JS that create the visual look of the Website. The template is available at - https://startbootstrap.com/theme/sb-admin-2
The CSS and JS files from the template are compliled within the 'static' folder.

## To get the project up and running
1. Install Pycharm or any other IDE like Visual studio. Ensure that python is installed on your machine.
2. Create a new virtual environment for the project.
3. Inside your project, open the terminal and install the file 'requirements.txt'. This will install Flask in your environment which is the only thing needed.
4. Now, create/copy the 'main.py' and 'database_setup.py' into your environment.
5. The first thing to be done is run the 'database_setup.py' file to setup the working database. Running the file will create a Db called 'site.db' within your environment.
6. We now have a working DB that would store all the user creds and data. When you run the the above python file, a default admin user is created who has maximum privilege.
7. Create a folder within your environment called 'templates' and add all the HTML files in this folder.
8. Similarly, create a folder 'static' and add the CSS and JS folder into it. These files are responsible for loading the webapp and define the GUI.
9. All the requirements of the project are now met and we can now run the 'main.py' file to host our website. Upon running the file we see that the python gives us a weblink where our webapp will be hosted.
10. Open the Link, and we land on the login page of our webapp.

## Vulnerability !
We now have a working website which an user can interact with. The Current code is Vulnerable and can be exploited. 
The below exploits can be leveraged -
1. In the username field on login page, type ---> ' OR 1=1--  with any password to directly gain admin access. [SQL injection]
OR - use --> admin' --  in username and anything as password. -- classic auth bypass.

2. After logging in from a user account, change the part after view in ' http://127.0.0.1:5000/view/3 ' -- this allows to view posts of any user -- IDOR / broken access control

3. On a user login, inject this into the url -->  ' UNION SELECT users.id, users.username, users.password, users.id, users.username FROM users LIMIT 1 OFFSET 0' OR ' UNION SELECT users.id, users.username, users.password, users.id, users.username FROM users LIMIT 1 OFFSET 1'
This will leak the user id and password for the users sequentially -- Dump users by SQL injection in endpoints
 
4. Create a post in any user account as -- content = <script>alert('XSS attack ! Attacker can send the session cookie to their machine. ');</script>
 Classic XSS since the view content mode has XSS sink enabled ( | safe )

## To Fix the code we will make changes in some of our code to secure the webapp. 
There are files called 'safe.py' & 'safe_db.py' within the repository which have a secure version of the code for the webapp. Copy the contents of these files into the main files of our project and we now have a secure version of the webapp.
To run the safe version, the 'safe_db.py' file needs to be run first to create a DB with hashed datasets. The 'safe.py' file can be run next to launch the secure webapp.

## The below are the changes made within the code -
1. A strong secret key is intialised within the flask environment which generates a 32-bit hashed key.
2. Session cookies are set for 'HTTP = true, secure = false & samesite = Lax', which define the secure parameters.
3. Implementing a parameterised query which restricts the login lookup to only username -- "SELECT * FROM users WHERE username = ?"
4. Use hashed passwords via 'werkzeug.security' and configurable initial admin from the safe_db.py file.
5. Check items.user_id == session['user_id'] for non-admins before view/edit/delete, which eradicate the IDOR issue.
6. Removed ( | safe ) parameter from view_record which will prevent XSS.
7. Error handling is implemented which redirects / 403 responses and flash messages.

After making the required changes, the webapp is secured and can function as it was designed to do. 


