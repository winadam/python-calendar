import datetime

class unscheduledTask:
    def __init__(self,title, length, fun, setUp=0):
        self.title = title
        self.length = length
        self.lengthInHours = length/60.0
        self.fun = fun
        self.setUp = setUp
        self.weight = fun*length

    def createGoogleEvent(self, date, time, calendarID):
        startTime = datetime.datetime.combine(date, time)
        startTimeString = startTime.strftime("%Y-%m-%dT%H:%M:%S-04:00") #FIXME Actually set the correct timezone with daylight savings
        endTime = startTime+datetime.timedelta(minutes=self.length)

        endTimeString = endTime.strftime("%Y-%m-%dT%H:%M:%S-04:00")
        event = {
            'summary': self.title,

            'start': {
                'dateTime': startTimeString,
            },
            'end': {
                'dateTime': endTimeString,

            },

            'reminders': {
                'useDefault': False,
                'overrides': [
                    {'method': 'popup', 'minutes': self.setUp},
                ],
            },
        }

        return event

    def __str__(self):
        return "Name: {}, Length: {}".format(self.title, self.length)
