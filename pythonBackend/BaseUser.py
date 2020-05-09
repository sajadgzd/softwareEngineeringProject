import sqlite3
import json
from flask import Flask, jsonify, render_template, request, send_from_directory
import uuid


@app.route('/login', methods = ["POST"])
def login():
    jsonData = request.json

    email = jsonData["email"]
    credentials = jsonData["credentials"]

    connection = sqlite3.connect(r"./database.db")
    cursor = connection.cursor()
    cursor.execute("SELECT * FROM users WHERE [email] = ? AND [credentials] = ?"(jsonData["email"].lower(),credentials))
    userData = cursor.fetchone()
    userData = list(userData)
    userData[3] = json.loads(userData[3]) #grouplist
    userData[6] = json.loads(userData[6]) #invitations
    userData[7] = json.loads(userData[7]) #blacklist
    userData[8] = json.loads(userData[8]) #whitelist
    userData[10] = json.loads(userData[10]) #inbox

    if userData is not None:
        return jsonify({
            "data": userData
        })
    else:
        return jsonify({
            "Error": "Sorry, email or password combination does not exist."
        })

@app.route('/inviteToGroup', methods = ["POST"])
def inviteToGroup(senderUserID, groupName, recipientUserID):
    jsonData = request.json

    inviter = jsonData["inviterEmail"].lower()
    inviterFullname = jsonData["inviterFullname"]
    groupName = jsonData["groupName"]
    invitee = jsonData["inviteeEmail"].lower()

    connection = sqlite3.connect(r"./database.db")
    cursor = connection.cursor()
    cursor.execute("SELECT * FROM users WHERE [email] = ?"(invitee,))

    inviteeData = cursor.fetchone()

    inviteeData = list(inviteeData)

    blackList = json.loads(inviteeData[7])
    for blocked in blackList:
        if blocked["email"] == inviter:
            connection.close()
            return jsonify({
            "Message": "Sorry, your invitation has been automatically rejected."
        })

    whiteList = json.loads(inviteeData[8])
    for autoAccept in whiteList:
        if autoAccept["email"] == inviter:
            groupList = json.loads(inviteeData[3])
            groupList.append(groupName)
            groupList = json.dumps(groupList)
            inviteeData[3] = groupList
            cursor.execute("DELETE * FROM users WHERE [email] = ?", (invitee,))
            cursor.execute("INSERT INTO users (email,fullname,password,groupList,reputationScore,status,invitations,blacklist,whitelist,complimentsorcomplaints,inbox) VALUES (?,?,?,?,?,?,?,?,?,?,?)",tuple(inviteeData))
            
            cursor.execute("SELECT * FROM groups WHERE [groupName] = ?",(groupName,))
            groupData = list(cursor.fetchone())
            memberData = json.loads(groupData[5])
            memberData.append({
                "member": invitee,
                "warnings": 0,
                "praises": 0,
                "taskscompleted":0
            })
            memberData = json.dumps(memberData)
            groupData[4] = memberData

            cursor.execute("DELETE * FROM groups WHERE [groupName] = ?",(groupName,))
            cursor.execute("INSERT INTO groups (groupName,status,posts,polls,members) VALUES(?,?,?,?,?)",tuple(groupData))
            connection.commit()
            connection.close()
            return jsonify({
                "Message": "Your invitation has been automatically accepted!"
            })
    
    invitations = json.loads(inviteeData[6])
    invitations.append({
        "fullname": inviterFullname,
        "inviterEmail" :inviter,
        "groupName": groupName
    })

    invitations = json.dumps(invitations)
    cursor.execute("DELETE * FROM users WHERE [email] = ?", (invitee,))
    cursor.execute("INSERT INTO users (email,fullname,password,groupList,reputationScore,status,invitations,blacklist,whitelist,complimentsorcomplaints,inbox) VALUES (?,?,?,?,?,?,?,?,?,?,?)",tuple(inviteeData))
    connection.commit()
    connection.close()
    return jsonify({
        "Message": "Your invitation has been sent!"
    })


@app.route('/handleGroupInvite', methods = ["POST"])
def handleGroupInvite():
    jsonData = request.json
 
    inviter = jsonData["inviterEmail"].lower()
    inviterFullname = jsonData["inviterFullname"]
    groupName = jsonData["groupName"]
    invitee = jsonData["inviteeEmail"].lower()
    message = jsonData["message"]
    response = jsonData["response"]
 
 
    connection = sqlite3.connect(r"./database.db")
    cursor = connection.cursor()
    cursor.execute("SELECT * FROM users WHERE [email] = ?"(invitee,))
    if response.lower() == "accepted":
        #group data base add user
        cursor.execute("SELECT * FROM groups WHERE [groupName] = ?",(groupName,))
        groupData= list(cursor.fetchone())
        memberData = json.loads(groupData[5])
            memberData.append({
                "member": invitee,
                "warnings": 0,
                "praises": 0,
                "taskscompleted":0
            })
            memberData = json.dumps(memberData)
        groupData[4] = memberList
        cursor.execute("DELETE FROM groups WHERE [groupName] = ?",(groupName,))
        cursor.execute("INSERT INTO groups (groupName,status,posts,polls,members) VALUES(?,?,?,?,?)",tuple(groupData))
        connection.commit()
 
        #user databas, add group to invitee list
        cursor.execute("SELECT * FROM users where [email] = ?",(invitee,))
        inviteeData = list(cursor.fetchone())
        groupList = json.loads(inviteeData[3])
        groupList.append(groupName)
        groupList = json.dumps(groupList)
        inviteeData[3] =groupList
        cursor.execute("DELETE FROM users WHERE [email] = ?",(invitee,))
        cursor.execute("INSERT INTO users (email,fullname,password,groupList,reputationScore,status,invitations,blacklist,whitelist,complimentsorcomplaints,inbox) VALUES (?,?,?,?,?,?,?,?,?,?,?)",tuple(inviteeData))
        connection.commit()
 
        #user database, add message to inviter inbox
        cursor.execute("SELECT * FROM users where [email] = ?",(inviter,))
        inviterData = list(cursor.fetchone())
        inboxList = json.loads(inviteeData[10])
        inboxList.append({
            "sender": inviter,
            "message": message
        })
        inboxList = json.dumps(inboxList)
        inviterData[10] =inboxList
        cursor.execute("DELETE FROM users WHERE [email] = ?",(inviter,))
        cursor.execute("INSERT INTO users (email,fullname,password,groupList,reputationScore,status,invitations,blacklist,whitelist,complimentsorcomplaints,inbox) VALUES (?,?,?,?,?,?,?,?,?,?,?)",tuple(inviterData))
        connection.commit()
        connection.close()
        return (jsonify({
            "message": "You've been added to the group {} and your response has been sent to your inviter.".format(groupName)
        }))
    elif response.lower() == "declined":
        #user database, add message to inviter inbox
        cursor.execute("SELECT * FROM users where [email] = ?",(inviter,))
        inviterData = list(cursor.fetchone())
        inboxList = json.loads(inviteeData[10])
        inboxList.append({
            "sender": inviter,
            "message": message
        })
        inboxList = json.dumps(inboxList)
        inviterData[10] =inboxList
        cursor.execute("DELETE FROM users WHERE [email] = ?",(inviter,))
        cursor.execute("INSERT INTO users (email,fullname,password,groupList,reputationScore,status,invitations,blacklist,whitelist,complimentsorcomplaints,inbox) VALUES (?,?,?,?,?,?,?,?,?,?,?)",tuple(inviterData))
        connection.commit()
        connection.close()
        return (jsonify({
            "message": "You have declined your invitation to the group {} and your response has been sent to your inviter.".format(groupName)
        }))

@app.route('/createMeetupPoll', methods = ["POST"])
def createMeetupPoll():
    jsonData = request.json
    groupName = jsonData["groupName"]
    pollCreator = jsonData["creator"]
    pollTitle = jsonData["pollTitle"]
    pollData["uuid"] = str(uuid.uuid4())
    pollPrompt = jsonData["pollPrompt"]
    pollType = "MEETUP"
    pollStatus = "ACTIVE"
    pollOptions = jsonData["pollVoteOptions"]
    pollVoteOptions = {}
    for option in pollOptions:
        pollVoteOptions[option] = 0
    voters = []

    pollData = {}
    pollData["pollCreator"] = pollCreator
    pollData["pollTitle"] = pollTitle
    pollData["pollPromopt"] = pollPrompt
    pollData["pollType"] = pollType
    pollData["uuid"] = str(uuid.uuid4())
    pollData["pollStatus"] = pollStatus
    pollData["pollVoteOptions"] = pollVoteOptions
    pollData["voters"] = voters
    pollData["result"] = None

     
    connection = sqlite3.connect(r"./database.db")
    cursor = connection.cursor()
    cursor.execute("SELECT * FROM  groups WHERE [groupName] = ?"(groupName,))
    groupData = list(cursor.fetchone())

    groupPolls = json.loads(groupName[4])
    groupPolls.append(pollData)
    groupPolls = json.dumps(groupPolls)
    groupData[4] = groupPolls

    cursor.execute("DELETE FROM groups WHERE [groupName] = ?",(groupName,))
    cursor.execute("INSERT INTO groups (groupName,status,posts,polls,members) VALUES(?,?,?,?,?)",tuple(groupData))
    connection.commit()
    connection.close()

    return (jsonify{
        "Message": "Your Create Meetup poll has been created."
    })

@app.route('/createWarningPoll', methods = ["POST"])
def createWarningPoll():
    jsonData = request.json
    groupName = jsonData["groupName"]
    pollCreator = jsonData["pollCreator"]
    targetedMemberEmail = jsonData["email"]
    targetedMemberName = jsonData["fullname"]
    pollTitle = jsonData["pollTitle"]
    pollData["uuid"] = str(uuid.uuid4())
    pollPrompt = jsonData["pollPrompt"]
    pollType = "WARNING"
    pollStatus = "ACTIVE"
    pollOptions = jsonData["pollVoteOptions"]
    pollVoteOptions = {}
    for option in pollOptions:
        pollVoteOptions[option] = 0
    voters = []

    pollData = {}
    pollData["pollCreator"] = pollCreator
    pollData["targetedMemberEmail"] = targetedMemberEmail
    pollData["targetedMemberName"] = targetedMemberName
    pollData["pollTitle"] = pollTitle
    pollData["uuid"] = str(uuid.uuid4())
    pollData["pollPromopt"] = pollPrompt
    pollData["pollType"] = pollType
    pollData["pollStatus"] = pollStatus
    pollData["pollVoteOptions"] = pollVoteOptions
    pollData["voters"] = voters
    pollData["result"] = None

     
    connection = sqlite3.connect(r"./database.db")
    cursor = connection.cursor()
    cursor.execute("SELECT * FROM  groups WHERE [groupName] = ?"(groupName,))
    groupData = list(cursor.fetchone())

    groupPolls = json.loads(groupName[3])
    groupPolls.append(pollData)
    groupPolls = json.dumps(groupPolls)
    groupData[3] = groupPolls

    cursor.execute("DELETE FROM groups WHERE [groupName] = ?",(groupName,))
    cursor.execute("INSERT INTO groups (groupName,status,posts,polls,members) VALUES(?,?,?,?,?)",tuple(groupData))
    connection.commit()
    connection.close()

    return (jsonify{
        "Message": "Your warning poll has been created."
    })

@app.route('/createPraisePoll', methods = ["POST"])
def createPraisePoll():
    jsonData = request.json
    groupName = jsonData["groupName"]
    pollCreator = jsonData["pollCreator"]
    targetedMemberEmail = jsonData["email"]
    targetedMemberName = jsonData["fullname"]
    pollTitle = jsonData["pollTitle"]
    pollData["uuid"] = str(uuid.uuid4())
    pollPrompt = jsonData["pollPrompt"]
    pollType = "PRAISE"
    pollStatus = "ACTIVE"
    pollOptions = jsonData["pollVoteOptions"]
    pollVoteOptions = {}
    for option in pollOptions:
        pollVoteOptions[option] = 0
    voters = []

    pollData = {}
    pollData["pollCreator"] = pollCreator
    pollData["targetedMemberEmail"] = targetedMemberEmail
    pollData["targetedMemberName"] = targetedMemberName
    pollData["pollTitle"] = pollTitle
    pollData["uuid"] = str(uuid.uuid4())
    pollData["pollPromopt"] = pollPrompt
    pollData["pollType"] = pollType
    pollData["pollStatus"] = pollStatus
    pollData["pollVoteOptions"] = pollVoteOptions
    pollData["voters"] = voters
    pollData["result"] = None

     
    connection = sqlite3.connect(r"./database.db")
    cursor = connection.cursor()
    cursor.execute("SELECT * FROM  groups WHERE [groupName] = ?"(groupName,))
    groupData = list(cursor.fetchone())

    groupPolls = json.loads(groupName[3])
    groupPolls.append(pollData)
    groupPolls = json.dumps(groupPolls)
    groupData[3] = groupPolls

    cursor.execute("DELETE FROM groups WHERE [groupName] = ?",(groupName,))
    cursor.execute("INSERT INTO groups (groupName,status,posts,polls,members) VALUES(?,?,?,?,?)",tuple(groupData))
    connection.commit()
    connection.close()

    return (jsonify{
        "Message": "Your Praise poll has been created."
    })


@app.route('/createKickPoll', methods = ["POST"])
def createKickPoll():
    jsonData = request.json
    groupName = jsonData["groupName"]
    pollCreator = jsonData["pollCreator"]
    targetedMemberEmail = jsonData["email"]
    targetedMemberName = jsonData["fullname"]
    pollTitle = jsonData["pollTitle"]
    pollData["uuid"] = str(uuid.uuid4())
    pollPrompt = jsonData["pollPrompt"]
    pollType = "KICK"
    pollStatus = "ACTIVE"
    pollOptions = jsonData["pollVoteOptions"]
    pollVoteOptions = {}
    for option in pollOptions:
        pollVoteOptions[option] = 0
    voters = []

    pollData = {}
    pollData["pollCreator"] = pollCreator
    pollData["targetedMemberEmail"] = targetedMemberEmail
    pollData["targetedMemberName"] = targetedMemberName
    pollData["pollTitle"] = pollTitle
    pollData["uuid"] = str(uuid.uuid4())
    pollData["pollPromopt"] = pollPrompt
    pollData["pollType"] = pollType
    pollData["pollStatus"] = pollStatus
    pollData["pollVoteOptions"] = pollVoteOptions
    pollData["voters"] = voters
    pollData["result"] = None

     
    connection = sqlite3.connect(r"./database.db")
    cursor = connection.cursor()
    cursor.execute("SELECT * FROM  groups WHERE [groupName] = ?"(groupName,))
    groupData = list(cursor.fetchone())

    groupPolls = json.loads(groupName[3])
    groupPolls.append(pollData)
    groupPolls = json.dumps(groupPolls)
    groupData[3] = groupPolls

    cursor.execute("DELETE FROM groups WHERE [groupName] = ?",(groupName,))
    cursor.execute("INSERT INTO groups (groupName,status,posts,polls,members) VALUES(?,?,?,?,?)",tuple(groupData))
    connection.commit()
    connection.close()

    return (jsonify{
        "Message": "Your Kick poll has been created."
    })

@app.route('/createCloseGroupPoll', methods = ["POST"])
def createCloseGroupPoll():
    jsonData = request.json
    groupName = jsonData["groupName"]
    pollCreator = jsonData["creator"]
    pollTitle = jsonData["pollTitle"]
    pollData["uuid"] = str(uuid.uuid4())
    pollPrompt = jsonData["pollPrompt"]
    pollType = "CLOSE"
    pollStatus = "ACTIVE"
    pollOptions = jsonData["pollVoteOptions"]
    pollVoteOptions = {}
    for option in pollOptions:
        pollVoteOptions[option] = 0
    voters = []

    pollData = {}
    pollData["pollCreator"] = pollCreator
    pollData["pollTitle"] = pollTitle
    pollData["uuid"] = str(uuid.uuid4())
    pollData["pollPromopt"] = pollPrompt
    pollData["pollType"] = pollType
    pollData["pollStatus"] = pollStatus
    pollData["pollVoteOptions"] = pollVoteOptions
    pollData["voters"] = voters
    pollData["result"] = None

     
    connection = sqlite3.connect(r"./database.db")
    cursor = connection.cursor()
    cursor.execute("SELECT * FROM  groups WHERE [groupName] = ?"(groupName,))
    groupData = list(cursor.fetchone())

    groupPolls = json.loads(groupName[4])
    groupPolls.append(pollData)
    groupPolls = json.dumps(groupPolls)
    groupData[4] = groupPolls

    cursor.execute("DELETE FROM groups WHERE [groupName] = ?",(groupName,))
    cursor.execute("INSERT INTO groups (groupName,status,posts,polls,members) VALUES(?,?,?,?,?)",tuple(groupData))
    connection.commit()
    connection.close()

    return (jsonify{
        "Message": "Your Close Group has been created."
    })

@app.route('/issueMeetupVote', methods = ["POST"])
def issueMeetupVote(pollName, UserID, decision):
    jsonData = request.json

    pollResponse = jsonData["pollResponse"] #Option they selected
    pollResponder = jsonData["email"]
    pollUUID = jsonData["pollUUID"]
    groupName = jsonData["groupName"]


    connection = sqlite3.connect(r"./database.db")
    cursor = connection.cursor()
    cursor.execute("SELECT * FROM  groups WHERE [groupName] = ?"(groupName,))

    groupData = list(cursor.fetchone())
    groupPolls = json.loads(groupData[4])
    for index,poll in enumerate(groupPolls):
        if poll["uuid"] == pollUUID:
            poll["voters"].append(pollResponder)
            pollVoteOptions = poll["pollVoteOptions"]
            pollVoteOptions[pollResponse] += 1 
            poll["pollVoteOptions"] = pollVoteOptions
            groupPolls[index] = poll
            break
    groupPolls = json.dumps(groupPolls)
    groupData[4] = groupPolls
    cursor.execute("DELETE FROM groups WHERE [groupName] = ?",(groupName,))
    cursor.execute("INSERT INTO groups (groupName,status,posts,polls,members) VALUES(?,?,?,?,?)",tuple(groupData))
    connection.commit()

    groupPolls = json.loads(groupPolls)
    sumVotes = 0
    for index,poll in enumerate(groupPolls):
        if poll["uuid"] == pollUUID:
            pollVoteOptions = poll["pollVoteOptions"]
            for option,voteCount in pollVoteOptions.items():
                sumVotes += voteCount
            break
    totalMembers = len(groupData[5])

    maxResponseCount = 0
    answer = None
    if sumVotes == totalMembers:
        for index,poll in enumerate(groupPolls):
            if poll["uuid"] == pollUUID:
                pollVoteOptions = poll["pollVoteOptions"]
                for option,voteCount in pollVoteOptions.items():
                    if voteCount > maxResponseCount:
                        maxResponseCount = voteCount
                        answer = option
                poll["result"] = answer
                poll["pollStatus"] = "CLOSED"
                groupPolls[index] = poll
                break

        groupPolls = json.dumps(groupPolls)
        groupData[4] = groupPolls
        cursor.execute("DELETE FROM groups WHERE [groupName] = ?",(groupName,))
        cursor.execute("INSERT INTO groups (groupName,status,posts,polls,members) VALUES(?,?,?,?,?)",tuple(groupData))
        connection.commit()
    connection.close()

    return (jsonify({
        "Message": "Your vote has been submitted."
    }))




@app.route('/issueWarningVote', methods = ["POST"])
def issueWarningVote(pollName, UserID, decision):
   jsonData = request.json

    pollResponse = jsonData["pollResponse"] #Option they selected
    pollResponder = jsonData["email"]
    pollUUID = jsonData["pollUUID"]
    groupName = jsonData["groupName"]


    connection = sqlite3.connect(r"./database.db")
    cursor = connection.cursor()
    cursor.execute("SELECT * FROM  groups WHERE [groupName] = ?"(groupName,))

    groupData = list(cursor.fetchone())
    memberPolls = json.loads(groupData[3])
    for index,poll in enumerate(memberPolls):
        if poll["uuid"] == pollUUID:
            poll["voters"].append(pollResponder)
            pollVoteOptions = poll["pollVoteOptions"]
            pollVoteOptions[pollResponse] += 1 
            poll["pollVoteOptions"] = pollVoteOptions
            memberPolls[index] = poll
            break
    

    memberPolls = json.dumps(memberPolls)
    groupData[3] = memberPolls
    cursor.execute("DELETE FROM groups WHERE [groupName] = ?",(groupName,))
    cursor.execute("INSERT INTO groups (groupName,status,posts,polls,members) VALUES(?,?,?,?,?)",tuple(groupData))
    connection.commit()

    memberPolls = json.loads(memberPolls)
    sumVotes = 0
    for index,poll in enumerate(memberPolls):
        if poll["uuid"] == pollUUID:
            pollVoteOptions = poll["pollVoteOptions"]
            for option,voteCount in pollVoteOptions.items():
                sumVotes += voteCount
            break
    totalMembers = len(groupData[5])

    maxResponseCount = 0
    answer = None
    if sumVotes == totalMembers-1:
        for index,poll in enumerate(memberPolls):
            if poll["uuid"] == pollUUID:
                pollVoteOptions = poll["pollVoteOptions"]
                for option,voteCount in pollVoteOptions.items():
                    if voteCount > maxResponseCount:
                        maxResponseCount = voteCount
                        answer = option
                poll["result"] = answer
                poll["pollStatus"] = "CLOSED"
                memberPolls[index] = poll
                break
        
        if maxResponseCount == totalMembers-1:
            memberPolls = json.dumps(memberPolls)
            groupData[3] = memberPolls
            cursor.execute("DELETE FROM groups WHERE [groupName] = ?",(groupName,))
            cursor.execute("INSERT INTO groups (groupName,status,posts,polls,members) VALUES(?,?,?,?,?)",tuple(groupData))
        connection.commit()
    connection.close()

    ####HELPER

    return (jsonify({
        "Message": "Your vote has been submitted."
    }))

@app.route('/issuePraiseVote', methods = ["POST"])
def issuePraiseVote(pollName, UserID, decision):
   jsonData = request.json

    pollResponse = jsonData["pollResponse"] #Option they selected
    pollResponder = jsonData["email"]
    pollUUID = jsonData["pollUUID"]
    groupName = jsonData["groupName"]


    connection = sqlite3.connect(r"./database.db")
    cursor = connection.cursor()
    cursor.execute("SELECT * FROM  groups WHERE [groupName] = ?"(groupName,))

    groupData = list(cursor.fetchone())
    memberPolls = json.loads(groupData[3])
    for index,poll in enumerate(memberPolls):
        if poll["uuid"] == pollUUID:
            poll["voters"].append(pollResponder)
            pollVoteOptions = poll["pollVoteOptions"]
            pollVoteOptions[pollResponse] += 1 
            poll["pollVoteOptions"] = pollVoteOptions
            memberPolls[index] = poll
            break
    

    memberPolls = json.dumps(memberPolls)
    groupData[3] = memberPolls
    cursor.execute("DELETE FROM groups WHERE [groupName] = ?",(groupName,))
    cursor.execute("INSERT INTO groups (groupName,status,posts,polls,members) VALUES(?,?,?,?,?)",tuple(groupData))
    connection.commit()

    memberPolls = json.loads(memberPolls)
    sumVotes = 0
    for index,poll in enumerate(memberPolls):
        if poll["uuid"] == pollUUID:
            pollVoteOptions = poll["pollVoteOptions"]
            for option,voteCount in pollVoteOptions.items():
                sumVotes += voteCount
            break
    totalMembers = len(groupData[5])

    maxResponseCount = 0
    answer = None
    if sumVotes == totalMembers-1:
        for index,poll in enumerate(memberPolls):
            if poll["uuid"] == pollUUID:
                pollVoteOptions = poll["pollVoteOptions"]
                for option,voteCount in pollVoteOptions.items():
                    if voteCount > maxResponseCount:
                        maxResponseCount = voteCount
                        answer = option
                poll["result"] = answer
                poll["pollStatus"] = "CLOSED"
                memberPolls[index] = poll
                break
        
        if maxResponseCount == totalMembers-1:
            memberPolls = json.dumps(memberPolls)
            groupData[3] = memberPolls
            cursor.execute("DELETE FROM groups WHERE [groupName] = ?",(groupName,))
            cursor.execute("INSERT INTO groups (groupName,status,posts,polls,members) VALUES(?,?,?,?,?)",tuple(groupData))
        connection.commit()
    connection.close()
    
    ####HELPER

    return (jsonify({
        "Message": "Your vote has been submitted."
    }))

@app.route('/issueKickVote', methods = ["POST"])
def issueKickVote(pollName, UserID, decision):
   jsonData = request.json

    pollResponse = jsonData["pollResponse"] #Option they selected
    pollResponder = jsonData["email"]
    pollUUID = jsonData["pollUUID"]
    groupName = jsonData["groupName"]


    connection = sqlite3.connect(r"./database.db")
    cursor = connection.cursor()
    cursor.execute("SELECT * FROM  groups WHERE [groupName] = ?"(groupName,))

    groupData = list(cursor.fetchone())
    memberPolls = json.loads(groupData[3])
    for index,poll in enumerate(memberPolls):
        if poll["uuid"] == pollUUID:
            poll["voters"].append(pollResponder)
            pollVoteOptions = poll["pollVoteOptions"]
            pollVoteOptions[pollResponse] += 1 
            poll["pollVoteOptions"] = pollVoteOptions
            memberPolls[index] = poll
            break
    

    memberPolls = json.dumps(memberPolls)
    groupData[3] = memberPolls
    cursor.execute("DELETE FROM groups WHERE [groupName] = ?",(groupName,))
    cursor.execute("INSERT INTO groups (groupName,status,posts,polls,members) VALUES(?,?,?,?,?)",tuple(groupData))
    connection.commit()

    memberPolls = json.loads(memberPolls)
    sumVotes = 0
    for index,poll in enumerate(memberPolls):
        if poll["uuid"] == pollUUID:
            pollVoteOptions = poll["pollVoteOptions"]
            for option,voteCount in pollVoteOptions.items():
                sumVotes += voteCount
            break
    totalMembers = len(groupData[5])

    maxResponseCount = 0
    answer = None
    if sumVotes == totalMembers-1:
        for index,poll in enumerate(memberPolls):
            if poll["uuid"] == pollUUID:
                pollVoteOptions = poll["pollVoteOptions"]
                for option,voteCount in pollVoteOptions.items():
                    if voteCount > maxResponseCount:
                        maxResponseCount = voteCount
                        answer = option
                poll["result"] = answer
                poll["pollStatus"] = "CLOSED"
                memberPolls[index] = poll
                break
        
        if maxResponseCount == totalMembers-1:
            memberPolls = json.dumps(memberPolls)
            groupData[3] = memberPolls
            cursor.execute("DELETE FROM groups WHERE [groupName] = ?",(groupName,))
            cursor.execute("INSERT INTO groups (groupName,status,posts,polls,members) VALUES(?,?,?,?,?)",tuple(groupData))
        connection.commit()
    connection.close()

    ####HELPER

    return (jsonify({
        "Message": "Your vote has been submitted."
    }))

@app.route('/issueComplimentVote', methods = ["POST"])
def issueCompliment(UserId, complimentComment):
    #if (userID exists in the user database):
    #   print(UserID.complimentDatabase.append(UserId, complimentComment))
    #   return success status
    #
    #else:
    #   print("The user you are trying to issue a compliment to, doesnt't exist")
    pass

def addToWhiteBox(UserID):
    #if (userID exists in the user database):
    #   if (userID exists in self.whitebox database):
    #       print("User already added to whitebox")
    #   
    #   else:
    #        add user to the self.whitebox database
    #        print("User added to your blackbox")
    #
    # else:
    #   print("The user you are trying to whitelist doesn't exist")

def addToBlackBox(userID):
    #if (userID exists in the user database):
    #   if (userID exists in self.blackbox database):
    #       print("User already to blackbox")
    #   
    #   else:
    #        add user to the self.blackbox database
    #        print("User banned")
    #
    # else:
    #   print("The user you are trying to ban doesn't exist")