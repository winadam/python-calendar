import pytz as pytz

from GoogleAPI.googleEvent import googleEvent
from WunderAPI.unscheduledTask import *
from calendarManager import *
from Tkinter import *
from GoogleAPI.googleAPI import *
from WunderAPI.wunderAPI import *
from schedular import *
from PomodoroModule.freeTimeBlock import *
from PomodoroModule.pomodoroScheduler import PomodoroScheduler

class GUI:


    def __init__(self):

        self.google = google()
        self.wunder = wunder()

        #GUI CREATION        

        print "Creating GUI"
    
        root = Tk()

        root.title("Scheduler")
        root.geometry("300x400")

        #Calendar Selection Box

        GoogleCalendarOptions = Listbox(root, selectmode=SINGLE, exportselection=0)
        
        for event in self.google.getCalendars()["items"]:
            GoogleCalendarOptions.insert(END, event["summary"])

        GoogleCalendarOptions.select_set(0)

        GoogleCalendarOptions.bind('<<ListboxSelect>>', self.changeCalendarID)
        GoogleCalendarOptions.grid(row=0, column=0)

        #Wunderlist Selection Box

        print "Creating Wunderlist Box"

        WunderlistOptions = Listbox(root, selectmode=SINGLE, exportselection=0)

        for list in self.wunder.getLists():
            WunderlistOptions.insert(END, list["title"])
            if not self.wunder.listID:
                self.wunder.setListID(list["title"])
        print "Got Lists"
        WunderlistOptions.select_set(0)

        WunderlistOptions.bind('<<ListboxSelect>>', self.changeListID)
        WunderlistOptions.grid(row=1, column=0)

        #Temp do it button

        PopulateCalendar = Button(root, text="Do it", command=self.populateCalendar)

        PopulateCalendar.grid(row=2, column=0)

        root.mainloop()

    def populateCalendar(self):
        print "Filling Calendar..."
        events = self.google.get_events(self.google.calendarID)

        events = self.google.cleanEvents(events)
        #TODO add date selection
        startTime = datetime.datetime.today().replace(hour=9, minute=0, second=0, microsecond=0, tzinfo= Zone(-4,False,'EST')) + \
                    datetime.timedelta(days=2)
        endTime = datetime.datetime.today().replace(hour=17, minute=0, second=0, microsecond=0, tzinfo=Zone(-4,False,'EST')) + \
                  datetime.timedelta(days=2)

        self.schedulerHandler = PomodoroScheduler(events, startTime, endTime)

        taskToSchedule = self.wunder.get_tasks(self.wunder.listID, self.schedulerHandler.maxTasks)
        self.schedulerHandler.scheduleTasks(taskToSchedule, self.google)

        # #Todo make this a polymorphic class so I can choose what scheduling algorithm at runtime
        # self.schedularHandler = schedular()
        #
        # listID = self.wunder.listID
        #
        # listOfTasks = self.wunder.get_tasks(listID)
        #
        # taskToSchedule = self.wunder.parse_tasks(listOfTasks)
        #
        # if taskToSchedule != []:
        #     taskToSchedule = self.schedularHandler.order_tasks(taskToSchedule)
        #
        #     for task in taskToSchedule:
        #         print task
        #
        #     self.schedularHandler.schedule_day(events, taskToSchedule, datetime.date.today()+datetime.timedelta(days=1), self.google.calendarID)

    def changeListID(self, event):
        lb = event.widget
        index = int(lb.curselection()[0])
        value = lb.get(index)
        print value
        self.wunder.setListID(value)

    def changeCalendarID(self, event):
        lb = event.widget
        index = int(lb.curselection()[0])
        value = lb.get(index)
        print value
        self.google.setCalendarID(value)

class Zone(datetime.tzinfo):
    def __init__(self,offset,isdst,name):
        self.offset = offset
        self.isdst = isdst
        self.name = name
    def utcoffset(self, dt):
        return datetime.timedelta(hours=self.offset) + self.dst(dt)
    def dst(self, dt):
            return datetime.timedelta(hours=1) if self.isdst else datetime.timedelta(0)
    def tzname(self,dt):
         return self.name
