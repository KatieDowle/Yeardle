import time
import random
import math
import sqlite3 
from datetime import date
from tkinter import *

connection = sqlite3.connect("Yeardle.db")
    
def generate_years(years):
    current_year = date.today().year
    all_years = []
    while len(all_years) <= 10:
        for year in years: 
            if year not in all_years:
                all_years.append(year)
            random_year = year + random.randint(-15,15)
            if (random_year <= current_year) and (random_year not in all_years):
                all_years.append(random_year)
    all_years = all_years[:10] 
    random.shuffle(all_years)
    return all_years
    
def get_leaderboard(): 
    query = "SELECT * FROM Users order by highscore desc" 
    results= connection.execute(query) 
    return list(results)

def update_user_score(username,high_score,high_level):
    query = "UPDATE Users set highscore=?, level=? where username = ? "
    connection.execute(query,(high_score,high_level,username))
    connection.commit()

def verify_user(username):
    query="select * from Users where username=?"
    result = list(connection.execute(query,(username,)))
    if len(result) == 0:
        query = "INSERT INTO Users (username,highscore,level) values (?,?,?)"
        result=[username,0,0]
        connection.execute(query,(username,0,0))
        connection.commit()
        return result
    return result[0]
        
def generate_questions_from_db():    
    questions =list(connection.execute("select * from Questions order by random() limit 50")) 
    data = []
    years = []
    categories = []
    events=[]
    for question in questions:
        event = question[0]
        year = question[1]
        category = question[2]
        if year not in years and category not in categories:
            years.append(year)
            categories.append(category)
            events.append(event)
    years = years[:4]
    data = data[:4]
    all_years = generate_years(years)
    return ({"questions": events, "all_years": all_years, "answers": years})

class Yeardle(Tk):
    def __init__(self):
        Tk.__init__(self)
        self.configure(width=1000,height=500,bg = "magenta")
        self.user=None 
        self.high_score=None
        self.high_level=None
        #Links
        self.game=None #GameScreen        
        
        #GUI Widgets
        self.info_screen=Frame(self,width=800,height=400,bg="yellow")
        self.maintitle=Label(self.info_screen,text="   Y E A R D L E   ", font=("Arial",40),bg="black",fg="yellow")
        self.maintitle.pack()
        self.message=Label(self.info_screen,text="message",bg="yellow")
        self.stats=Label(self.info_screen,text="stats",bg="blue",fg="yellow",font=("Arial",20))
        self.playbutton=Button(self.info_screen,text="Play/Continue/Quit",bg="green")
        self.cancel=Button(self,text="Cancel",command=self.display_info,bg="red")
        self.unameentry = Entry(self.info_screen) 
        self.leaderboard=Listbox(self.info_screen,width=40,font=("consolas",12),bg="blue",fg="yellow") #font needs to be monospaced
        self.leaderboard.bind("<<ListboxSelect>>",self.nameselect) 
        self.display_info(1)
        
    def nameselect(self,data):
        player=str(self.leaderboard.get(ANCHOR)).strip() 
        player=" ".join(player.split()).split()[1] 
        self.unameentry.delete(0,END)
        self.unameentry.insert(0,player)
        
    def get_user_details(self):
        details = verify_user(self.user)
        self.high_score=details[1] 
        self.high_level=details[2]
        
    def get_leaderboard_position(self):
        pos=1
        for player in get_leaderboard():
            if player[0]==self.user:
                return pos
            pos+=1

    def display_stats(self):
        self.stats["text"]=f"""Score: {self.game.score}\nLevel: {self.game.current_level}\nHigh Score: {self.game.high_score}\nLeaderboard# {self.get_leaderboard_position()}"""
            
        self.stats.pack()

    def display_info(self,state=1):
        #state codes
        #1. This is a brand new game so ask for username, display the leaderboard, and have quit of game on button
        #2. It is game over from an existing game
        #3. The user has lost a life from an existing game
        #4. The user has proceeded to the next level
        self.info_screen.place(x=320,y=50)
        if state == 1:
            if self.game: 
                self.game.destroy()
            self.message.configure(text="Welcome to Yeardle, Please type a username below or select from the list")
            self.message.pack()
            self.unameentry.pack()
            self.stats.forget()
            self.leaderboard.delete(0,END) #clear the leaderboard
            for pos,user in enumerate(get_leaderboard()):   
                rank = str(pos+1)+" "*(3-len(str(pos+1)))
                player = user[0] + " "*(20-len(user[0]))
                score = str(user[1]) + " "*(4-len(str(user[1])))
                level = str(user[2]) + " "*(4-len(str(user[2])))
                value=f"{rank} {player} {score} L{level}"
                self.leaderboard.insert(pos,value)
            self.leaderboard.pack()
            self.playbutton.configure(text="Game On", command=self.game_on)
            self.playbutton.pack()
        elif state == 2:
            self.game.place(x=-1000,y=-1000) #hide the game screen
            msg=f"Game Over - your score was {self.game.score} and you reached Level {self.game.current_level}"
            if self.game.score > self.high_score:
                pos = self.get_leaderboard_position()
                msg+=f"\nThis is a new high score - your position is now: {pos}"
            self.message.configure(text=msg)
            self.display_stats()
            self.playbutton.configure(text="OK",command=self.display_info)
        elif state == 3:
            self.game.place(x=-1000,y=-1000) #hide the game screen
            self.message.configure(text=f"You have lost a life - you have {self.game.lives_remaining} remaining")
            self.leaderboard.forget()
            self.unameentry.forget()
            self.stats.pack()
            self.playbutton.configure(text="Continue",command=self.game.start_level)
            self.display_stats()
        elif state == 4:
            self.game.place(x=-1000,y=-1000) #hide the game screen
            self.message.configure(text=f"Congratulations you have completed level {self.game.current_level-1}")
            self.display_stats()
            self.leaderboard.forget()
            self.unameentry.forget()
            self.playbutton.configure(text="Continue",command=self.game.start_level)
            
    def game_on(self):
        self.user=self.unameentry.get()
        if self.user and len(self.user) > 3 and " " not in self.user and len(self.user)<21:
            self.get_user_details()
            self.game=GameScreen(self)
            self.game.game_on()
        else:
            self.message.configure(text=f"Please enter a valid username")
            

class BonusBall(Canvas):
    def __init__(self,parent,average_bonus_ball_time,years,answers):
        Canvas.__init__(self,parent)
        self.parent=parent
        self.years= years 
        self.answers = answers 
        #create a square canvas and place the word YEAR with a red cross on it within a circle
        self.configure(width=80,height=80,bg="magenta",highlightthickness=0, relief='ridge')
        self.create_oval(5,5,75,75,fill = "purple")
        self.create_text(40,40,text = "YEAR",font = ("Arial",15,"bold"),fill = "lightblue")
        self.create_line(15,15,65,65,fill = "red",width = 2)
        self.create_line(15,65,65,15,fill = "red",width = 2)
        self.bind("<Button-1>",self.scored) #bind to left mouse button
        self.average_bonus_ball_time = average_bonus_ball_time
        self.vertical_acceleration = -9.8 #set vertical acceleration to gravity approximation
        self.reset()
        self.move()

    def reset(self): #removes ball from screen and resets start values
        self.bonus_start = False
        self.flight_time = 0 #set the current flight time of ball to 0
        self.place(x=-100,y=-100)# this makes the ball dissapear
        self.start_y = random.randint(150,300) #sets vertical launch position
        if random.randint(0,1):
            self.start_x = 0 #start ball from left of screen
        else:
            self.start_x = 1000 #start ball from right of screen
        self.angle_to_horizontal = random.randint(1,60)
        self.start_velocity = random.randint(3,7)
        
    def move(self):
        if self.bonus_start == True:
            self.flight_time += 0.005
            angle_in_radians = self.angle_to_horizontal * (math.pi / 180)
            horizontal_displacement = self.start_velocity * math.cos(angle_in_radians) * self.flight_time
            vertical_displacement = (self.start_velocity * math.sin(angle_in_radians) * self.flight_time) +(0.5 * self.vertical_acceleration * self.flight_time**2)
            if self.start_x == 0:
                x = int(self.start_x + horizontal_displacement * 200)
            else:
                x = int(self.start_x - horizontal_displacement * 200)
            y = int(self.start_y + vertical_displacement * 400)
            self.place(x=x,y=500 - y)# flips y coordinate as screen runs top to bottom
            if x > 1000 or x < 0: self.reset() #ball has gone outside bounds of screen
        else:
            r = random.randint(0,100*self.average_bonus_ball_time)
            if r == 5 and len(self.years) >= self.parent.max_bonus_balls: 
                self.bonus_start = True
        self.after(10, self.move)

    def scored(self,data):  
        potentials = []
        self.parent.score+=5
        for year in self.year_widgets:
            if year.year not in self.answers and year.in_position == False:
                potentials.append(year)
        random.shuffle(potentials)#this randomly shuffles the years that could be removed
        print (potentials[0].year,self.years)
        self.years.remove(potentials[0].year)
        self.year_widgets.remove(potentials[0])
        potentials[0].destroy()
        self.reset()
            
class DropZone(Frame):
    def __init__(self,parent):
        Frame.__init__(self,parent)
        self.parent=parent #reference to the GameScreen class
        #GUI Properties
        self.configure(width=80,height=300,bg="blue")
        self.results= Canvas(self,width=40, height=40,bg="blue",highlightthickness=0, relief='ridge')
        self.results.place(x=20,y=5)
        self.done_button = Button(self, text = "DONE", bg = "deeppink", fg = "white", font = ("Arial",14),command = self.show_result)
        self.done_button.place(x=5,y=250)
        self.done_button["state"]="disabled"
        self.targets = []
        y_coord = 50
        for target in range(0,4):
            lbl = Label(self, width=6,bg = "cyan")
            lbl.place(x=15,y=y_coord)
            lbl.position = target
            lbl.update()
            self.targets.append(lbl)
            y_coord += 50    

    def show_result(self):
        res = self.parent.check_answers()
        if res:
            x = 0
            y = 0
            count = 1
            for r in res:
                if r == "1":
                    colour = "black"
                else:
                    colour = "white"
                self.results.create_oval(x,y,x+15,y+15,fill = colour , outline = colour)
                if count == 1 :
                    x += 17
                elif count == 2 :
                    y += 17
                    x -= 17
                elif count == 3 :
                    x += 17
                count += 1
            self.done_button.place(x=-100,y=-100)#remove the done button
            Label(self,text=str(self.parent.attempt-1),font=("Arial",20),bg="yellow").place(x=30,y=250)


class YearWidget(Label):
    POS_COUNT = 0  
    COLOURS=["Yellow","Red","Green"] 
    def __init__(self,parent,year,x,y,dropzone,guesses):
        Label.__init__(self,parent)
        self.year=year
        self.dropzone= dropzone
        self.guesses = guesses
        self.place(x=x,y=y)
        self.original_x = x
        self.original_y = y
        self.in_position = False
        self.colour_index=0
        self.configure(text = str(year),bg=YearWidget.COLOURS[self.colour_index] ,font=("Arial",10))
        self.bind("<Button-1>", self.left_mouse_button_clicked)
        self.bind("<B1-Motion>", self.mouse_moving_and_left_button_clicked)
        self.bind("<ButtonRelease-1>",self.left_button_released)
        self.bind("<Button-3>",self.right_mouse_button_clicked)

    #event 1 - left mouse button clicked
    def left_mouse_button_clicked(self,data):
        self.mouse_x = data.x
        self.mouse_y = data.y
    
    #event 2 - left mouse button held down and mouse moving
    def mouse_moving_and_left_button_clicked(self,data):
        new_x = self.winfo_x() + data.x - self.mouse_x
        new_y = self.winfo_y() + data.y - self.mouse_y
        self.place(x=new_x,y=new_y)
    
    #event 3 - let go of left mouse button
    def left_button_released(self,data):
        is_target = False
        x1 = self.winfo_x() - self.mouse_x + data.x
        y1 = self.winfo_y() - self.mouse_y + data.y
        
        width1 = self.winfo_width()
        height1 = self.winfo_height()
        drop_zone_x= self.dropzone.winfo_x()
        drop_zone_y= self.dropzone.winfo_y()
        
        for target in self.dropzone.targets:
            x2 = target.winfo_x()+drop_zone_x
            y2 = target.winfo_y()+drop_zone_y
            width2 = target.winfo_width()
            height2 = target.winfo_height()
            result = self.is_overlap(x1,y1,width1,height1,x2,y2,width2,height2)
            if result == True:
                if not self.in_position: YearWidget.POS_COUNT+=1
                self.guesses[target.position] = self.year
                target.configure(text=self.year,bg="black",fg="white")
                is_target = True
                self.in_position=True
                self.place(x = x2, y=y2)
                self["bg"] = "hotpink"
                self.configure(font=("Helvetica",18,"bold"))
        
        if not is_target:
            self.return_to_base() #return year widget to original position
        if YearWidget.POS_COUNT == 4:
            self.dropzone.done_button["state"] = "normal"
        else:
            self.dropzone.done_button["state"] = "disabled"

    def right_mouse_button_clicked(self,data):
        if self.colour_index == len(YearWidget.COLOURS)-1:
            self.colour_index=0
        else: self.colour_index+=1
        self.configure(bg=YearWidget.COLOURS[self.colour_index] ,font=("Arial",10))

    def is_overlap(self,x1,y1,width1,height1,x2,y2,width2,height2):
        vertex1 = [x1,y1]
        vertex2 =  [x1+width1,y1]
        vertex3 = [x1+width1,y1+height1]
        vertex4 = [x1,y1+height1]
        vertices = [vertex1,vertex2,vertex3,vertex4]
        for vertex in vertices:
            x = vertex[0]
            y = vertex[1]
            if (x>x2 and x<(x2 + width2)) and (y>y2 and y<(y2 + height2)):
                return True
        vertex1 = [x2,y2]
        vertex2 =  [x2+width2,y2]
        vertex3 = [x2+width2,y2+height2]
        vertex4 = [x2,y2+height2]
        vertices = [vertex1,vertex2,vertex3,vertex4]
        for vertex in vertices:
            x = vertex[0]
            y = vertex[1]
            if (x>x1 and x<(x1 + width1)) and (y>y1 and y<(y1 + height1)):
                return True
        return False

    def return_to_base(self):
        self.place(x=self.original_x, y=self.original_y)
        self.configure(bg=YearWidget.COLOURS[self.colour_index],font=("Arial",10))
        if self.in_position:
            self.in_position=False
            YearWidget.POS_COUNT -=1

class GameScreen(Frame):
    def __init__(self,yeardle):
        Frame.__init__(self,yeardle)
        self.configure(width=1000,height=600)
        self.in_play=False
        self.yeardle=yeardle
        self.configure(bg = "magenta")
        self.user=yeardle.user
        self.high_score=yeardle.high_score
        self.high_level=yeardle.high_level
        self.scoreboard = None
        
    def destroy_widgets(self):
        if self.scoreboard:
            self.scoreboard.destroy()
            self.bonus_ball.destroy()
            self.questionpanel.destroy()
            for yearwidget in self.year_widgets:
                yearwidget.destroy()
            for dropzone in self.dropzones: 
                dropzone.destroy()
        
    def game_on(self):
        self.score=0
        self.lives_remaining=3
        self.current_level=1
        self.time_allowed=300
        self.bonus_ball_frequency=10#every 10 seconds
        self.max_bonus_balls=6
        self.start_level()

    def start_level(self):
        self.destroy_widgets()
        self.place(x=0,y=0)
        self.in_play=True
        self.dropzones=[]
        self.attempt = 1
        self.guesses = [0,0,0,0]
        data = generate_questions_from_db()
        self.answers = data["answers"]
        print(self.answers)
        self.questions = data["questions"]
        self.years = data["all_years"]        
        self.bonus_ball = BonusBall(self,self.bonus_ball_frequency,self.years,self.answers) 
        self.dropzone=DropZone(self)
        self.dropzones.append(self.dropzone)
        self.dropzone_pos=550
        self.dropzone.place(x=self.dropzone_pos,y=60)
        self.scoreboard = ScoreBoard(self)
        self.scoreboard.place(x=0,y=0)
        self.questionpanel = QuestionPanel(self,self.questions)
        self.questionpanel.place(x=0,y=110)
        YearWidget.POS_COUNT=0
        self.year_widgets = []
        current_y = 60
        current_x = 10
        for year in self.years:
            current_year = YearWidget(self,year,current_x,current_y,self.dropzone,self.guesses)
            current_x += 40
            self.year_widgets.append(current_year)
        #pass a reference to years, year_widgets and answers to bonus ball
        self.bonus_ball.year_widgets= self.year_widgets 

    def winner(self):
        points = self.current_level * (6- self.attempt) * 20 
        self.score+=points
        self.current_level+=1
        self.time_allowed =int(self.time_allowed*.9) #reduce time allowed
        if self.max_bonus_balls > 0:
            self.max_bonus_balls -=1
        self.bonus_ball_frequency =int(self.bonus_ball_frequency*1.1)
        self.scoreboard.update_scoreboard()
        self.in_play=False
        self.yeardle.display_info(4)

    def loser(self):
        self.in_play=False
        self.lives_remaining -=1
        if self.lives_remaining==0:
            self.yeardle.display_info(2)
        else:
            self.yeardle.display_info(3)

    def check_answers(self):
        correct_place = 0
        incorrect_place = 0
        for i in range(0,4):
            if self.guesses[i] == self.answers[i]:
                correct_place += 1
            elif self.guesses[i] in self.answers:
                incorrect_place += 1
        result = "1"*correct_place + "0" * incorrect_place
        if result == "1111":
            self.winner()
            return False
        elif self.attempt == 5:
            self.loser()
            return False
        else:            
            #create a new dropzone
            self.dropzone=DropZone(self)        
            self.dropzones.append(self.dropzone)
            self.dropzone_pos+=82    
            self.dropzone.place(x=self.dropzone_pos,y=60)
            for year_widget in self.year_widgets:
                year_widget.return_to_base()
                year_widget.lift()
                year_widget.dropzone=self.dropzone
            self.attempt+=1
            return result

class QuestionPanel(Frame):
    def __init__(self,parent,questions):
        Frame.__init__(self,parent)
        self.configure(width=510,height=200,bg="magenta")
        y_val = 0
        for question in questions:
            lbl = Label(self,text = question,font=("Arial",10),wraplength=500,bg="blue",fg="white")
            lbl.place(x=10,y=y_val)
            y_val += 50

class ScoreBoard(Frame):
    def __init__(self,parent):
        Frame.__init__(self,parent)
        self.parent=parent
        self.configure(width=1000,height=50,bg="green")
        self.title=Label(self,text="Y E A R D L E",font=("Constantia",26),bg="green",fg="yellow")
        self.title.place(x=400,y=4)
        self.current_time = time.time()
        self.timer=Label(self,text="TIME: ",font=("Arial",18),bg="red",fg="white")
        self.timer.place(x=5,y=5)
        self.score=Label(self,text=str(self.parent.score), bg="green",fg="white",font=("Arial",18))
        self.score.place(x=800,y=5)
        self.level=Label(self,text=str(self.parent.current_level), font=("Arial",18),bg="green",fg="white")
        self.level.place(x=950,y=5)
        self.lives=Canvas(self,width=70,height=30,bg="green")
        self.lives.place(x=700,y=5)
        self.user_details=Label(self,text=f"{self.parent.user}: {self.parent.high_score} L{self.parent.high_level}",font=("Arial",16),bg="yellow",fg="green")
        self.user_details.place(x=140,y=7)
        self.update_scoreboard()

    def update_scoreboard(self):
        elapsed = time.time() - self.current_time
        time_remaining= self.parent.time_allowed-int(elapsed)
        if time_remaining < 0: 
            self.parent.loser()
        self.timer["text"]=str(time_remaining)
        self.score["text"]="SCORE: "+str(self.parent.score)
        self.level["text"]="L"+str(self.parent.current_level)
        if self.parent.score > self.parent.high_score:
            self.parent.high_score=self.parent.score
            self.parent.high_level = self.parent.current_level
            self.user_details['text']=f"{self.parent.user}\n{self.parent.high_score} L{self.parent.high_level}"
            update_user_score(self.parent.user,self.parent.high_score,self.parent.high_level)
        x=5
        for i in range(self.parent.lives_remaining):
            self.lives.create_oval(x,5,x+20,25,fill="blue")
            x+=22
        if self.parent.in_play: self.after(1000,self.update_scoreboard)

#STARTS THE GAME!    
yeardle= Yeardle()
yeardle.geometry("1000x500")
yeardle.title("Yeardle!")
yeardle.mainloop()
