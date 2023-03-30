import sys
import subprocess
import pkg_resources
import configparser
import os
import time
from math import ceil
from sys import platform

__author__ = 'AlexNinetytwo'

__desc__ = ' Kanboard Color Equalizer equalizes the colors of all tasks of your kanboard project to their categories. '

__doc__ = """

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

"""


class Text:

    def __init__(self, text, maxWidth):
        self.text = text
        self.maxWidth = maxWidth

    def formated(self, anchor="LEFT"):
        if len(self.text) > self.maxWidth:
            return self.short()
        match anchor:
            case "LEFT":
                return self.anchorSide(anchor)            
            case "RIGHT":
                return self.anchorSide(anchor)
            case "CENTER":
                return self.anchorCenter()
            
    def anchorSide(self, anchor):
        space = ' ' * (self.maxWidth-len(self.text))
        match anchor:
            case "LEFT":
                return f'{self.text}{space}'
            case "RIGHT":
                return f'{space}{self.text}'
    
    def anchorCenter(self):
        self.mid = ceil(len(self.text)/2)
        leftSpace = (
            (int(self.maxWidth/2))
            -(len(self.text[:self.mid]))
        ) * ' '
        rightSpace = (
            (ceil(self.maxWidth/2))
            -(len(self.text[self.mid:]))
        ) * ' '
        return f'{leftSpace}{self.text}{rightSpace}'
            
    def short(self):
        if len(self.text) > self.maxWidth:
            return f'{self.text[:self.maxWidth-4]}... 'if self.text[self.maxWidth-4]==' ' else f'{self.text[:self.maxWidth-3]}...'
        return self.text
        


# Global variables
size = os.get_terminal_size()
spaceLeft = ' ' * 10
space = size[0] - 20
finshString = Text('', space)
emptySpace = f'{spaceLeft}|{space*" "}|'
winLen = 3
logo = Text('KANBOARD COLOR EQUALIZER', space).formated("CENTER")
descrition = Text(__desc__, space).formated("CENTER")
header = f'{spaceLeft} {"="*(space)}\n{emptySpace}\n{spaceLeft}|{logo}|\n{emptySpace}\n{spaceLeft}|{"_"*(space)}|'
descLine = f'{spaceLeft}|{descrition}|'


# Install missing modules
required = {'inquirer','kanboard'}
installed = {pkg.key for pkg in pkg_resources.working_set}
missing = required - installed
if missing:
    python = sys.executable
    subprocess.check_call([python, '-m', 'pip', 'install', *missing], stdout=subprocess.DEVNULL)


import inquirer
import kanboard
from inquirer import themes
from inquirer.render.console import ConsoleRender
from inquirer import errors

   
class Main:

    def main():
        Draw.redraw()
        confParser = configparser.ConfigParser()
        Organizer.creatConfigFileIfNotExist(confParser)
        address, username, token = Organizer.getaddressTokenAndUsername(confParser)
        Main.mainLoop(address, username, token)

    def mainLoop(address, username, token):
        while True:
            projectNames = Main.menu(address, username, token)
            for project in projectNames:
                Communication.equalizeColors(address, username, token, project)

    def menu(address, username, token):
        global finshString
        myProjects = Communication.getMyProjects(address, username, token)
        UserIsSure = False
        while not UserIsSure:
            questions = [
            inquirer.Checkbox(
                'choice',
                message=Text('Choose the projects you want to equalize tasks colors to their categories colors',space-5).formated(),
                choices=myProjects,
                ),
            ]
            answer = Menu.prompt(questions=questions)['choice']
            if len(answer) > 0:
                UserIsSure = Message.areYouSure(answer)
            else:
                UserIsSure = False
            finshString.text = ''

        finshString.text = ' Finish!'
        return answer

    def stopTheProgram():
        print('\nNo projects detected.\n')
        time.sleep(10)
        exit()

class Organizer:
    
    def creatConfigFileIfNotExist(confParser):
        if (os.path.exists('KCE.ini')):
            pass
        else:
            confParser['API.connection.data'] = {
                'address': 'Insert API address here',
                'username': 'Insert username here',
                'token': 'Insert API token here'
                
            }
            with open('KCE.ini', 'w') as configfile:
                confParser.write(configfile)

    def clean(data):
        data = data.replace(' ','')
        data = data.replace('"','')
        data = data.replace("'","")
        return data

    def getaddressTokenAndUsername(confParser):
        confParser.sections()
        confParser.read('KCE.ini')
        address = confParser['API.connection.data']['address']
        token = confParser['API.connection.data']['token']
        username = confParser['API.connection.data']['username']
        return Organizer.clean(address), Organizer.clean(username), Organizer.clean(token)
    


class Communication:

    def getMyProjects(address, username, token):
        projectList = []
        kanboardModule = kanboard.Client(address, username, token)
        if username == 'jsonrpc':
            myProjects = kanboardModule.get_all_projects() # Admin            
        else:
            myProjects = kanboardModule.get_my_projects()
        if len(myProjects) == 0:
            Main.stopTheProgram()

        for project in myProjects:
            projectList.append(project['name'])    
        return projectList
    
    def equalizeColors(address, username, token, projectName):
        kanboardModule = kanboard.Client(address, username, token)
        projectID = kanboardModule.get_project_by_name(name=projectName)['id']
        tasks = kanboardModule.get_all_tasks(project_id=projectID)
        categoryColors = {}
        for task in tasks:
            categoryColors = Communication.setTaskColor(kanboardModule, task, categoryColors)

    def setTaskColor(kanboardModule, task, categoryColors):
        taskID = task['id']
        categoryID = task['category_id']
        try: #if task has category
            if categoryID in categoryColors:
                kanboardModule.update_task(id=taskID,color_id=categoryColors[categoryID])
            else:
                color = kanboardModule.get_category(category_id=categoryID)['color_id']
                kanboardModule.update_task(id=taskID,color_id=color)
                categoryColors[categoryID] = color 
        except:
            pass
        finally:
            return categoryColors

class Draw:

    def drawUpperFrame():
        print(header)
        print(emptySpace)
        print(descLine)
        print(f'{spaceLeft}|{finshString.formated()}|')

    def redraw():
        if platform == 'linux':
            os.system('clear')
        else:
            os.system('cls')
        Draw.drawUpperFrame()

    def drawMidFrame(amount):
        for i in range(amount):
            print(emptySpace)

    def drawBottomFrame():
        print(emptySpace)
        print(emptySpace)
        print(f'{spaceLeft}|{"_"*space}|')

    def drawChoosen(projects=None):
        if projects != None:
            print(f'{spaceLeft}|{Text(" Choosen projects:", space).formated()}|')
            for project in projects:
                print(f'{spaceLeft}|{Text("     "+project, space).formated()}|')

class Menu(ConsoleRender):

    def __init__(self, event_generator=None, theme=None, *args, **kwargs):
        super().__init__(event_generator, theme, *args, **kwargs)

    def _event_loop(self, render, projects):
        try:
            while True:
                Draw.redraw()
                self._print_status_bar(render)
                Draw.drawChoosen(projects)
                Draw.drawMidFrame(1)
                self._print_header(render)
                self._print_options(render)
                Draw.drawBottomFrame()
                self._process_input(render)
                self._force_initial_column()
                
        except errors.EndOfInput as e:
            self._go_to_end(render)
            return e.selection
 
    def _print_options(self, render):
        for message, symbol, color in render.get_options():
            print(spaceLeft+'| ',end="")
            if hasattr(message, "decode"):  # python 2
                message = message.decode("utf-8")
            self.print_line(" {color}{s} {m:{sp}}{t.normal}|", m=message, color=color, s=symbol, sp=space-8)
        
    def _print_header(self, render):
        base = render.get_header()
        header = base[: self.width - 9] + "..." if len(base) > self.width - 6 else base
        header = f'{header:{space-4}}|'
        msg_template = (
            spaceLeft+"{t.move_up}|{tq.brackets_color}[{tq.mark_color}?{tq.brackets_color}]{t.normal} {msg}"
        )
        self.print_str(
            f"{msg_template}",
            msg=header,
            lf=True,
            tq=self._theme.Question,
        )

    def print_str(self, base, lf=False, **kwargs):
        if lf:
            self._position += 1
        text = base.format(t=self.terminal, **kwargs)
        print(text, end="\n" if lf else "")
        sys.stdout.flush()
        
    def prompt(questions, answers=None, theme=themes.Default(), projects=None):
        render = Menu(theme=theme)
        answers = answers or {}
        try:
            for question in questions:
                answers[question.name] = render.render(question, answers, projects)
            return answers
        except KeyboardInterrupt:
            pass

    def render(self, question, answers=None, projects=None):
        question.answers = answers or {}
        if question.ignore:
            return question.default
        clazz = self.render_factory(question.kind)
        render = clazz(question, terminal=self.terminal, theme=self._theme, show_default=question.show_default)
        self.clear_eos()
        try:
            return self._event_loop(render, projects)
        finally:
            pass

class Message:

    def areYouSure(projects):
        global finshString
        finshString.text = ''
        projectNames = ", ".join(projects)
        questions = [
            inquirer.Confirm(
                'choice',
                message=Text(f'Are you sure you want to change colors of all tasks in "{projectNames}"?', space-10).short()
                )
            ]
        answer = Menu.prompt(questions=questions, projects=projects)['choice']
        return answer

    def throwException(e):
        global finshString
        finshString.text = ''
        Draw.redraw()

        defaultTip = 'Make sure you set up the "KCE.ini" file correctly.'
        if 'HTTP Error 401' in e.args[0]:
            Message.errorMessage(' Invalid access data.', 10, defaultTip)
        elif 'InsertAPIaddress' in e.args[0]:
            Message.errorMessage(' API address is missing.', 10, defaultTip) 
        elif 'urlopen error' in e.args[0]:
            Message.errorMessage(' A connection could not be established because the target computer refused the connection', 10)
        elif 'has no len()' in e.args[0]:
            Message.errorMessage(' Incorrect API address. ', 10, defaultTip)
        elif "'NoneType' object is not subscriptable" in e.args[0]:
            Message.errorMessage(' Bye!', 3)
        else:
            Message.errorMessage(e.args[0], 10)

    def errorMessage(message, countdown, attachment=''):
        message += ' ' + attachment
        message = Text(message, space).formated()
        print(f'{spaceLeft}|{message}|')
        Draw.drawMidFrame(winLen)
        Draw.drawBottomFrame()
        time.sleep(countdown)


if __name__ == '__main__':
    try:
        Main.main()
    except Exception as e:
        try:
            Message.throwException(e)
        except KeyboardInterrupt:
            pass
        


  
