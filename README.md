---KANBOARD COLOR EQUALIZER---

This script is made for equalizing the colors of all tasks in a Kanban project to their category colors. The user can choose the project from
a list of their projects and confirm whether they want to proceed with the color equalization. The script reads the API access data from a
configuration file and uses the Kanboard API to update the colors of the tasks in the selected project.

---HOW TO USE---

Set up the configuration file: If you are running the program for the first time, a configuration file named "KCEviaAPI.ini" will be created.
You need to provide your API address, API token, and username in this file. Run the program: Run the program by executing the Python script.
You will see a list of your projects. Select the project whose task colors you want to equalize with their categories' colors. Confirm your
selection: After selecting a project, you will be asked to confirm whether you want to change the colors of all tasks in that project to their
category colors. Wait for the program to finish: The program will loop through all the tasks of the selected project and set their colors to
their respective category colors. Once the program finishes, it will print "Finish!" on the console.
