# Daily TODO 2023-04-09
# Copyright (C) 2023 by cs-mt (https://github.com/cs-mt)

import sqlite3
from datetime import datetime 
import os 

createTable = False

if not os.path.isfile("todo.db"):
    createTable = True

conn = sqlite3.connect("todo.db")
cur = conn.cursor()

if createTable:
    cur.execute("""
    CREATE TABLE "routines" (
	"id"	INTEGER,
	"title"	TEXT,
	"type"	INTEGER,
	"days"	TEXT,
	"removed"	INTEGER DEFAULT 0,
	PRIMARY KEY("id" AUTOINCREMENT)
);
            """)

    cur.execute("""
            CREATE TABLE "logs" (
	"id"	INTEGER,
	"routine_id"	INTEGER,
	"started_time"	TEXT,
	"finished_time"	TEXT,
	"result"	INTEGER,
	PRIMARY KEY("id" AUTOINCREMENT)
);
            """)

    conn.commit()


def addTODOCompletion(TODOList):
    for x in range(len(TODOList)):
        entry = TODOList[x]

        TODOid = entry[0]

        cur.execute("SELECT id,started_time,finished_time,result FROM logs WHERE routine_id = ?", (TODOid,))
        row = cur.fetchone()

        if row:
          TODOList[x] += row

    return TODOList

# Returns TODO for today.
def getTODO(all=False):
    TODOList = []
    now = datetime.now()

    # Type 0: regular TODO
    todayName = now.strftime("%A")
    cur.execute("SELECT id,title,days FROM routines WHERE type = 0 AND removed = 0 AND days LIKE ? ORDER BY id ASC", ("%," + todayName + ",%",))
    rows = cur.fetchall()
    TODOList += rows

    # Type 1: custom TODO
    todayDate = now.strftime("%Y-%m-%d")
    cur.execute("SELECT id,title,days FROM routines WHERE type = 1 AND removed = 0 AND days = ?", (todayDate,))
    row = cur.fetchall()
    TODOList += row

    if all:
        TODOList = []
        todayName = now.strftime("%A")
        cur.execute("SELECT id,title,days FROM routines WHERE type = 0 AND removed = 0 ORDER BY id ASC")
        rows = cur.fetchall()
        TODOList += rows

    if all:
      return TODOList
    else:
      return addTODOCompletion(TODOList)

def printTODO(TODOList, all=False):
    os.system('cls' if os.name == 'nt' else 'clear')

    if all:
      print("="*96)
      print("| {:^4} | {:^60} | {:^22} |".format("ID", "Title", "Days"))
    else:
      print("="*98)
      print("| {:^4} | {:^60} | {:^6} | {:^6} | {:^6} |".format("ID", "Title", "Start", "End", "Status"))


    for entry in TODOList:
        id = entry[0]
        title = entry[1]
        days = entry[2]

        if days.startswith(","):
            days = days[1:-1].split(",")
            daystxt = ""
            for day in days:
                daystxt += day[0] + day[1] + " "
            days = daystxt

        logStart = "NA"
        logEnd = "NA"
        logResult = "NA"

        if len(entry) > 3:
            logStart = entry[4]
            logEnd = entry[5]
            logResult = entry[6]

        if logStart != "NA":
            datetime_object = datetime.strptime(logStart, '%Y-%m-%d %H:%M:%S')
            logStart = datetime_object.strftime("%H:%M")

        if logEnd != "NA":
            datetime_object = datetime.strptime(logEnd, '%Y-%m-%d %H:%M:%S')
            logEnd = datetime_object.strftime("%H:%M")

        # Print TODO Line
        if all:
          print("| {:^4} | {:60} | {:22} |".format(id, title, days))
        else:
          print("| {:^4} | {:60} | {:^6} | {:^6} | {:^6} |".format(id, title, logStart, logEnd, logResult))

    if all:
      print("="*96)
    else:
      print("="*98)

def markEntry(entryId, markAs):
    if markAs == "remove":
        cur.execute("UPDATE routines SET removed = 1 WHERE id = ?", (entryId,))
        conn.commit()
        TODOList = getTODO()
        printTODO(TODOList) 
        return 

    now = datetime.now()
   
    todayDate = now.strftime("%Y-%m-%d")
    cur.execute("SELECT * FROM logs WHERE routine_id = ? AND started_time LIKE ?", (entryId, todayDate + "%"))
    logRow = cur.fetchone()

    logid = 0

    if logRow:
        logid = logRow[0]
    else:
        if markAs == "reset":
            TODOList = getTODO()
            printTODO(TODOList) 
            return 

        cur.execute("INSERT INTO logs (routine_id, started_time, finished_time, result) VALUES (?, 'NA', 'NA', 'NA')", (entryId,))
        logid = cur.lastrowid

    nowDateTime = now.strftime("%Y-%m-%d %H:%M:%S")

    if markAs == "reset":
        cur.execute("DELETE FROM logs WHERE id = ?", (logid,))
    elif markAs == "start":
        cur.execute("UPDATE logs SET started_time = ?, result = 'WIP' WHERE id = ?", (nowDateTime, logid))
    elif markAs == "complete":
        cur.execute("UPDATE logs SET finished_time = ?, result = 'COMP' WHERE id = ?", (nowDateTime, logid))

    conn.commit()

    TODOList = getTODO()
    printTODO(TODOList) 

def addTODO():
    os.system('cls' if os.name == 'nt' else 'clear')

    title = input("TODO Title: ")
    days = input("TODO Date or Days (e.g. 2023-04-09 or Friday,Saturday,Monday): ")

    isRoutine = False

    try:
      a = datetime.strptime(days, '%Y-%m-%d')
    except:
      isRoutine = True

    if isRoutine:
        cur.execute("INSERT INTO routines (title, type, days) VALUES (?, 0, ?)", (title, "," + days + ","))
    else:
        cur.execute("INSERT INTO routines (title, type, days) VALUES (?, 1, ?)", (title, days))

    conn.commit()

    TODOList = getTODO()
    printTODO(TODOList) 

def programLoop():
    TODOList = getTODO()
    printTODO(TODOList)

    while True:
        print("")
        print("(1) Show TODO List")
        print("(2-[entry number]) Mark entry as started")
        print("(3-[entry number]) Mark entry as completed")
        print("(4-[entry number]) Reset entry")
        print("(5) Add New TODO")
        print("(6) Show all routines")
        print("(7-[entry number]) Remove TODO")
        print("")
        action = input("Choose one: ")

        if action == "1":
            TODOList = getTODO()
            printTODO(TODOList)
            continue
        elif action.startswith("2-"):
            entryNumber = int(action.split("-")[1])
            markEntry(entryNumber, "start")
        elif action.startswith("3-"):
            entryNumber = int(action.split("-")[1])
            markEntry(entryNumber, "complete")
        elif action.startswith("4-"):
            entryNumber = int(action.split("-")[1])
            markEntry(entryNumber, "reset")
        elif action == "5":
            addTODO()
        elif action == "6":
            TODOList = getTODO(all=True)
            printTODO(TODOList, all=True)
        elif action.startswith("7-"):
            entryNumber = int(action.split("-")[1])
            markEntry(entryNumber, "remove")

programLoop()
