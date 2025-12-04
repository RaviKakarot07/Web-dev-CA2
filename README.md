# Web-dev-CA2
Repository for Web development CA2. 

Project Developed by Ravi Rameshkumar Mishra. 

The project has a basic functionality of storing posts/thoughts bny users who create an account on the webpage. Any user who wants to use the functionality can sign-up on the page and start their usage. 
Webpage has a user-friendly UI where the user can add, view, edit or delete their posts. All the posts are kept anonymous.
There is an Admin user for the webapp which is the only person who can see/view all the users posts as well as the login ID's. They can add posts of their own aswell.

SETUP -
The project has 2 crucial Python files called 'main.py' and 'database_setup.py' which are required to run the app. 
Any type of complier/IDE can be used to run the files. I have used Pycharm for my project. 
This is a python based project which will host our WebApp using Flask. The version is defined in the 'requirements.txt' file.
Along with these Python files, there are multiple HTML files that are complied in the 'Templates' folders which will define the function of the WebApp.

For the structure of the webpage, I have used a free-source template called ' SB Admin 2'. This template consists of files in CSS and JS that create the visual look of the Website. The template is available at - https://startbootstrap.com/theme/sb-admin-2
The CSS and JS files from the template are compliled within the 'static' folder.

To get the project up and running --
1. Install Pycharm or any other IDE like Visual studio. Ensure that python is installed on your machine.
2. Create a new virtual environment for the project.
3. Inside your project, open the terminal and install the file 'requirements.txt'. This will install Flask in your environment which is the only thing needed.
4. Now, create/copy the 'main.py' and 'database_setup.py' into your environment.
5. The first thing to be done is run the 'database_setup.py' file to setup the working database. Running the file will create a Db called 'site.db' within your environment.
6. 


