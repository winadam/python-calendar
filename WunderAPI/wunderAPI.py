import requests

from HelperFiles.utils import *
from HelperFiles.utils import getInputFromList
from WunderAPI.unscheduledTask import unscheduledTask


class wunder:

    

    def genCreds(self):
        if os.path.isfile("WunderAPI\wunderaccess.json"):
            os.remove("WunderAPI\wunderaccess.json")

        self.token = getWunderAccess(self.oauth)

        with open("WunderAPI\wunderaccess.json", "w") as wunderaccess:
            obj = {
                "access_token": self.token
            }
            wunderaccess.write(json.dumps(obj))

    def __init__(self):
        self.listID = ""
        self.lists = None
        with open("WunderAPI\wunderoauth.json", "r") as wunderoauth:
            self.oauth = json.load(wunderoauth)

        if os.path.isfile("WunderAPI\wunderaccess.json"):
            with open("WunderAPI\wunderaccess.json") as wunderaccess:
                self.token = json.load(wunderaccess)["access_token"]
        else:
            self.genCreds()

        self.headers = {
            "X-Access-Token": self.token,
            "X-Client-ID": self.oauth["client_id"]
        }

        self.headers2 = {
            "X-Access-Token": self.token,
            "X-Client-ID": self.oauth["client_id"],
            "Content-Type":"text/json"
        }

    def request(self,method,url,data=None):
        request = None

        if method == "GET" or method == "DELETE":
            request = requests.request(method,url,params=data,headers=self.headers)
        else:
            request = requests.request(method,url, data=json.dumps(data),headers=self.headers2)

        return self.handleResponse(request)


    def handleResponse(self,req):
        if req.status_code != 200 and req.status_code != 204:
            self.genCreds()
            print "Request returned:{}".format(req.status_code)
            raise RuntimeError(req.url,req.text,req.headers)
            return None

        jsonObj = json.loads(req.text)
        return jsonObj


    def select_list(self):
        listNames = []

        listOfLists = self.getLists()

        for list in listOfLists:
            listNames.append(list["title"])

        list = getInputFromList(listOfLists,listNames)
        return list["id"]

    def getLists(self):
        if self.lists == None:
            self.lists = self.request("GET","http://a.wunderlist.com/api/v1/lists")
        return self.lists


    def setListID(self, newListTitle):
        lists = self.getLists()
        for item in lists:
            if item["title"] == newListTitle:
                print item["id"]
                self.listID = item["id"]

    def get_tasks(self, listID, numberOfTasks):
        originaltasks =  self.request("GET","http://a.wunderlist.com/api/v1/tasks",data={ "list_id":listID })
        tasks = self.parse_tasks(originaltasks)
        tasksToGive = []
        i=0
        j=0
        while i<=numberOfTasks and j<len(tasks):
            i+=tasks[j].length
            if i<=numberOfTasks:
                tasksToGive.append(tasks[j])
                self.change_task_name(originaltasks[j], tasks[j].title)
            if i > numberOfTasks:
                i-=tasks[j].length
            j += 1
        return tasksToGive

    def change_task_name(self, task, title):
        self.request("PATCH", "https://a.wunderlist.com/api/v1/tasks/" + str(task["id"]),data={"revision":task["revision"], "title":title+" #scheduled"})

    def parse_tasks(self, listOfTasks):
        tasksToSchedule = []
        for task in listOfTasks:
            length = 0
            print task
            title = task["title"].split('#')
            if len(title) == 1:
                length = 1
            # change_task_name(task, title[0])
            # number - length, s-number of segements, r-repeat frequency, p-preparation time

            fun = 0
            repeatsFreq = 0 #TODO Add me
            segments = 1
            prep = 5
            for bit in title:
                bit = bit.strip()
                if bit.startswith("#scheduled"):
                    continue
                if bit.isdigit():
                    length = int(bit)
                if bit.startswith("s"):
                    segments = int(bit[1:])
                if bit.startswith("r"):
                    repeatsFreq = int(bit[1:])
                if bit.startswith("p"):
                    prep = int(bit[1:])
                if bit.startswith("i"):
                    fun = int(bit[1:])
            length /= segments
            while segments>0:
                tasksToSchedule.append(unscheduledTask(title[0].strip(), length, fun, setUp=prep))
                segments-=1
        return tasksToSchedule


