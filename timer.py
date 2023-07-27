#!/usr/bin/python3


import uuid, time, json
from datetime import datetime

###
#
#   Timer class for measuring processing times
#   Usage: Create an instance, exposing 6 methods
#       .start:  Start a named timer
#       .stop:  Stop a named timer
#       .group_start: Start a named timer, belonging to a group
#       .group_stop:  Stop a named timer, belonging to a group
#       .print_timers:  Print all individual timers
#       .print_groups:  Print 1 or all groups of timers with stats
#
###
class TimerClass:

    def __init__(self):

        self.timer_groups = {}
        self.timers = {}
        self.debug = True

    ###
    #   tag: string: optional name for timer
    #   Return:  string:  Tag name of timer, keep for stop method
    ###
    def start(self, tag=None):

        if tag == None:
            tag = str(uuid.uuid4())

        startTime = datetime.utcnow()
        self.timers[tag] = {
            "start": startTime,
            "end": None,
            "runTime": 0.0,
            "group": None # only used for group timers
        }

        return tag

    ###
    #   tag: string: required
    #   destroy: Boolean: default True, destroys timer
    #   Return: float: time in seconds from timer session
    ###
    def stop(self, tag, destroy=True):

        if tag not in self.timers:
            self.dprint(str(tag) + " not found in timers")

        self.timers[tag]["end"] = datetime.utcnow()

        seconds = (self.timers[tag]["end"] - self.timers[tag]["start"]).seconds
        micros = (self.timers[tag]["end"] - self.timers[tag]["start"]).microseconds
        seconds = float(seconds + (micros / 1000000))
        self.timers[tag]["runTime"] = seconds

        if destroy:
            del self.timers[tag]

        return seconds

    ###
    #   group_tag: string: required, name of tag group
    #   timer_tag: string: optional, name of individual timer in group
    #   Return: string: Tag name of timer, keep for stop method
    ###
    def group_start(self, group_tag, timer_tag=None):

        if group_tag not in self.timer_groups:
            self.timer_groups[group_tag] = {
                "total_time": 0.0,
                "timer_count": 0,
                "timers": {}
            }

        tag = self.start(timer_tag)
        timer_count = self.timer_groups[group_tag]["timer_count"]
        self.timer_groups[group_tag]["timer_count"] = timer_count + 1
        self.timer_groups[group_tag]["timers"][tag] = self.timers[tag]
        self.timers[tag]["group"] = group_tag

        return tag

    ###
    #   group_tag: string: required, name of tag group
    #   timer_tag: string: required, name of individual timer in group
    #   Return: dictionary: timer group
    ###
    def group_stop(self, group_tag, timer_tag):

        seconds = self.stop(timer_tag, False)
        previous_time = self.timer_groups[group_tag]["total_time"]
        new_total = previous_time + seconds
        self.timer_groups[group_tag]["total_time"] = new_total

        return self.timer_groups[group_tag]

    def print_timers(self):

        timers = []
        for timer in self.timers:
            timers.append({
                timer: self.timers[timer]["runTime"],
                "group": self.timers[timer]["group"]
            })

        print(json.dumps(timers, indent=2))

    ###
    #   group_tag: string: optional, None will print all groups
    ###
    def print_groups(self, group_tag=None):

        groups = []

        # get a specific group
        if group_tag != None:
            if group_tag not in self.timer_groups:
                return "Group " + str(group_tag) + " not found"
            group = self.timer_groups[group_tag]
            groups.append({
                "group_tag": group_tag,
                "total_time": group["total_time"],
                "timer_count": group["timer_count"]
            })

        # get all groups
        else:
            for group_tag in self.timer_groups:
                group = self.timer_groups[group_tag]
                groups.append({
                    "group_tag": group_tag,
                    "total_time": group["total_time"],
                    "timer_count": group["timer_count"]
                })

        print(json.dumps(groups, indent=2))

    def dprint(self, str):

        if self.debug:
            print(str)

def test():

    print("\nRunning tests...\n")

    Timer = TimerClass()

    test_uuid_gen = Timer.start()
    time.sleep(0.2)
    seconds = Timer.stop(test_uuid_gen)
    print("testing uuid generation...\n..." + str(seconds) + " seconds in processing")

    test_tag_given = Timer.start("named_timer")
    time.sleep(0.05)
    seconds = Timer.stop("named_timer")
    print("testing named timer...\n..." + str(seconds) + " seconds in processing")

    test_no_delete = Timer.start()
    time.sleep(0.0001)
    seconds = Timer.stop(test_no_delete, False)
    print("testing timer no delete...\n..." + str(seconds) + " seconds in processing\n")
    print("The following should be one timer")
    time.sleep(0.5)
    Timer.print_timers()

    print("\n")

    ### Testing tiemer groups
    tag1 = Timer.group_start("process1")
    time.sleep(1.3423423)
    Timer.group_stop("process1", tag1)

    tag2 = Timer.group_start("process1")
    time.sleep(0.322342)
    Timer.group_stop("process1", tag2)

    tag3 = Timer.group_start("process2")
    time.sleep(1.2342345353)
    Timer.group_stop("process2", tag3)

    tag4 = Timer.group_start("process2")
    time.sleep(0.6345235)
    Timer.group_stop("process2", tag4)

    tag5 = Timer.group_start("process2")
    time.sleep(1.23423)
    Timer.group_stop("process2", tag5)

    print("Now we'll print all the individual timers\n")
    time.sleep(0.5)
    Timer.print_timers()
    time.sleep(0.5)
    print("\n and then we'll print the timer groups\n")
    time.sleep(0.5)
    Timer.print_groups()

    print("\n")

if __name__ == "__main__":

    test()
