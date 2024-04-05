#!/dist/shows/shared/bin/run pix

import argparse
import datetime
try:
    import offramp
except ImportError:
    from renderfarm import offramp
import showdb
from slackutils import slackMessage

def parseArgs():
    '''Parse args'''
   
    description = "Animhelp bot that pings slack with render updates"
    
    parser = argparse.ArgumentParser(description=description,
                        formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument('-a', "--alert",
    					help='Comma separated list of users to alert in slack')
    parser.add_argument('-ch', '--channel', default='C04KBSR8J30',
    					help='Channel to ping (default=test)')
    parser.add_argument('-u', "--unit",
    					help='Specified show unit for slack')

    actionsGroup = parser.add_argument_group("Actions", "Actions for farmTrooper")
    
    parser.add_argument('-d', '--debug', action='store_true',
    					help='print out results, don\'t send slack message')

    pargs = parser.parse_args()

    return pargs

class Messenger:
	def __init__(self, channel, unit, alertUsers=None, debug=False):
		self.channel = channel
		self.alertUsers = alertUsers
		self.user = "Animhelp Slack Robot"
		self.icon = ":robot:"
		self.debug = debug
		self.unit = unit

	def __repr__(self):
		form = "{0: ^20} {1: ^20} {2: ^20} {3: ^20}"
		filler = ''.ljust(20, '-')

		ret = form.format("Channel", "Alert Users", "As User", "Icon")
		ret += '\n' + form.format(filler, filler, filler, filler)
		ret += '\n' + form.format(self.channel, self.alertUsers, self.user, self.icon)
		return ret

	def sendSlack(self, msg):
		if self.alertUsers:
			msg = "{} {}".format(self.alertUsers, msg)

		if self.debug:
			print(self)
			print(msg)
		else:
			slackMessage(msg, channel=self.channel, user=self.user, icon_emoji=self.icon)

# Utility to calculate and format percentage
def calculateProgressPercentage(numDoneShots, numTotalShots):
    try: 
        percentDone = "{:.1%}".format(float(numDoneShots)/float(numTotalShots))
    except ZeroDivisionError:
        percentDone = 0
    return percentDone
    
# Utility to calculate and format percentage
def calculateProgressPercentage(numDoneShots, numTotalShots):
    try: 
        percentDone = "{:.1%}".format(float(numDoneShots)/float(numTotalShots))
    except ZeroDivisionError:
        percentDone = 0
    return percentDone
    
# Utility function to calculate number of frames into desired footage format
def calculateFramesInFootage(frames):

    result, remainder = divmod(frames, 16)

    return str(result) + "-" + str(remainder)


# Utility function to calculate footage format into number of frames
def convertFootageToFrames(footage):
    
    if '-' in str(footage): 
        split_frames = footage.split('-')

        footageInFrames = int((split_frames[0]) * 16 + split_frames[1])

        return footageInFrames
    else:
        
        footageInFrames = int(footage) * 16

        return footageInFrames

def calculateAnimationProgressInShots(messenger):

    # Combined SQL query to get Total Number of Animation Shots, total number of Animation Done shots,
    # total number of Render-anim shots, and total number of Render Anim Done shots
    animProgress_query = """SELECT 
                        COUNT(CASE WHEN dept='animation' AND status IN ('approved', 'done') AND PCT_NET=100 THEN shot ELSE NULL END) AS ANIM_DONE_SHOTS,
                        COUNT(DISTINCT CASE WHEN dept='render-anim' AND status IN ('approved', 'done') THEN shot ELSE NULL END) AS RENDERANIM_DONE_SHOTS,
                        COUNT(DISTINCT CASE WHEN dept='animation' AND PCT_NET=100 THEN shot ELSE NULL END) AS ANIM_TOTAL_SHOTS,
                        COUNT(DISTINCT CASE WHEN dept='render-anim' THEN shot ELSE NULL END) AS RENDERANIM_TOTAL_SHOTS
                        FROM checkpoints
                        WHERE unit = '{0}' 
                        AND shot_status = 'in' 
                        AND shot NOT LIKE '%H%'
                        AND shot_type IN ('film', 'teaser', 'PIP') 
                        AND prod NOT IN ('test', 'charmd', 'mod', 'light', 'dev', 'vis')
                        """.format(messenger.unit)

    # Combined SQL query to get Total Number of Animation Shots.  Value is manually stored in the weather field of shot d240_1a in the Shots db
    totalAnimShots_query = """SELECT weather AS TOTAL_ANIM_SHOTS
                        FROM shots
                        WHERE unit = 'dream' 
                        AND shot = 'd240_1a' 
                        """.format(messenger.unit)

    # Combined SQL query to get total number of Animation Shots, total number of Animation Done shots,
    # total number of Render-anim shots, and total number of Render Anim Done shots for each of the existing sequences
    seqProgress_query = """SELECT 
                        PROD, 
                        COUNT(CASE WHEN dept='animation' AND status IN ('approved', 'done') AND PCT_NET=100 THEN shot END) AS ANIM_APPROVED_SHOTS,
                        COUNT(CASE WHEN dept='animation' AND PCT_NET=100 THEN shot END) AS TOTAL_ANIM_SHOTS,
                        COUNT(CASE WHEN dept='animation' AND status='done' AND PCT_NET=100 THEN shot END) AS DONE_ANIM_SHOTS,
                        COUNT(DISTINCT CASE WHEN dept='render-anim' THEN shot END) AS TOTAL_RENDERANIM_SHOTS,
                        COUNT(DISTINCT CASE WHEN dept='render-anim' AND status='done' THEN shot END) AS DONE_RENDERANIM_SHOTS
                        FROM checkpoints
                        WHERE 
                        unit = '{0}' 
                        AND shot_status = 'in' 
                        AND shot NOT LIKE '%H%'
                        AND shot_type IN ('film', 'teaser', 'PIP') 
                        AND prod NOT IN ('test', 'charmd', 'mod', 'light', 'dev', 'vis')
                        GROUP BY prod
                        ORDER BY prod
                        """.format(messenger.unit)

    # Fetch Query against database
    try:
        db = showdb.openConnection(login="test123", passwd="test123")
        cursor = db.cursor()
        header, animProgress = showdb.sendSelect(cursor, animProgress_query)
        header, seqProgress = showdb.sendSelect(cursor, seqProgress_query)
        header, totalAnimShots = showdb.sendSelect(cursor, totalAnimShots_query)
        db.close()
    except Exception as e:
        print("DB error: %s" % e)
        return []

    #Get current time
    currentTime = datetime.datetime.now().time()

    if messenger.unit == "dream": 
        totalAnimShotNum = totalAnimShots[0][0]
        totalRAShotNum = totalAnimShots[0][0]
    else:
        totalAnimShotNum = animProgress[0][2]
        totalRAShotNum = animProgress[0][3]

    #Compare time to determine Morning/Afternoon greetings
    greeting = "morning :sunrise:" if currentTime < datetime.time(12) else "afternoon :night_with_stars:"

    #Calculate total percentages
    percentDoneAnim = calculateProgressPercentage(animProgress[0][0], totalAnimShotNum)
    percentDoneRenderAnim = calculateProgressPercentage(animProgress[0][1], totalRAShotNum)

    # Message to send to Slack 
    slackMessage = """Good {}!! 
        Overall percentage of Animation Shots Done {} ({}) 
        Overall percentage of Render Anim Shots Done {} ({}) 
        """.format(greeting,
        str(animProgress[0][0]) + "/" + str(totalAnimShotNum), 
        percentDoneAnim, 
        str(animProgress[0][1]) + "/" + str(totalRAShotNum), 
        percentDoneRenderAnim)
    
    #Adding column headers for slack
    slackMessage += "```{:<8} {:<13} {:<13} {:<13} {:<2}\n".format("Seq", "Anim Appr'd", "Anim Done", "RA Done", "Total Done")
    
    #Looping over each of the sequences and calculating total number of animation shots, animation done shots, render anim shots and render anim done shots
    for item in seqProgress:
        animApprovedPercent = calculateProgressPercentage(item[1], item[2])
        animSeqDonePercent = calculateProgressPercentage(item[3], item[2])
        renderAnimSeqDonePercent = calculateProgressPercentage(item[5], item[4])
        totalSeqDonePercent = calculateProgressPercentage(item[3] + item[5], item[2] + item[4])

        #Appending list of sequence data to slack message
        slackMessage += "{:<8} {:<13} {:<13} {:<13} {:<2}\n".format(
        item[0], 
        str(item[1]) + "/" + str(item[2]) + "(" + animApprovedPercent + ")", 
        str(item[3]) + "/" + str(item[2]) + "(" + animSeqDonePercent + ")", 
        str(item[5]) + "/" + str(item[4]) + "(" + renderAnimSeqDonePercent + ")", 
        str(item[3] + item[5]) + "/" + str(item[2] + item[4]) + "(" + totalSeqDonePercent + ")" )
    slackMessage += "```"
    #Send slack message
    messenger.sendSlack(slackMessage)


def calculateAnimationProgressInFootage(messenger):

    # Combined SQL query to get Total Number of Animation Frames, total number of Animation Done Frames,
    # total number of Render-anim Frames, and total number of Render Anim Done frames
    animFramesProgress_query = """SELECT 
                        SUM(CASE WHEN dept='animation' AND status IN ('approved', 'done') AND PCT_NET=100 THEN frames ELSE 0 END) AS DONE_ANIM_FRAMES,
                        SUM(CASE WHEN dept='render-anim' AND status IN ('approved', 'done') THEN frames ELSE 0 END) AS DONE_RENDERANIM_FRAMES,
                        SUM(CASE WHEN dept='animation' AND PCT_NET=100 THEN frames ELSE 0 END) AS TOTAL_ANIM_FRAMES,
                        SUM(CASE WHEN dept='render-anim' THEN frames ELSE 0 END) AS TOTAL_RENDERANIM_FRAMES
                        FROM checkpoints
                        WHERE 
                        unit = '{0}' 
                        AND shot_status = 'in' 
                        AND shot NOT LIKE '%H%'
                        AND shot_type IN ('film', 'teaser', 'PIP') 
                        AND prod NOT IN ('test', 'charmd', 'mod', 'light', 'dev', 'vis')
                        """.format(messenger.unit)
    
    # Combined SQL query to get Total Number of Animation Footage.  Value is manually stored in the weather field of shot d240_13b in the Shots db
    totalAnimFootage_query = """SELECT weather AS TOTAL_ANIM_FOOTAGE
                        FROM shots
                        WHERE unit ='dream' 
                        AND shot = 'd240_3b' 
                        """.format(messenger.unit)

    # Combined SQL query to get total number of Animation frames, total number of Animation Done Frames,
    # total number of Render-anim frames, and total number of Render Anim Done frames for each of the existing sequences
    seqFramesProgress_query = """SELECT 
                        PROD, 
                        SUM(CASE WHEN dept='animation' AND status IN ('approved', 'done') THEN frames ELSE 0 END)  AS ANIM_APPROVED_FRAMES,
                        SUM(CASE WHEN dept='animation' THEN frames ELSE 0 END) AS TOTAL_ANIM_FRAMES,
                        SUM(CASE WHEN dept='animation' AND status='done' THEN frames ELSE 0 END) AS DONE_ANIM_FRAMES,
                        SUM(CASE WHEN dept='render-anim' THEN frames ELSE 0 END) AS TOTAL_RENDERANIM_FRAMES,
                        SUM(CASE WHEN dept='render-anim' AND status='done' THEN frames ELSE 0 END) AS DONE_RENDERANIM_FRAMES
                        FROM checkpoints
                        WHERE 
                        unit = '{0}' 
                        AND dept IN ('animation', 'render-anim')
                        AND shot_status = 'in' 
                        AND shot NOT LIKE '%H%'
                        AND shot_type IN ('film', 'teaser', 'PIP') 
                        AND prod NOT IN ('test', 'charmd', 'mod', 'light', 'dev', 'vis')
                        GROUP BY prod
                        ORDER BY prod
                        """.format(messenger.unit)

    # Fetch Query against database
    try:
        db = showdb.openConnection(login="test123", passwd="test123")
        cursor = db.cursor()
        header, animProgressInFrames = showdb.sendSelect(cursor, animFramesProgress_query)
        header, totalAnimFootage = showdb.sendSelect(cursor, totalAnimFootage_query)
        header, seqProgressInFrames = showdb.sendSelect(cursor, seqFramesProgress_query)
        db.close()
    except Exception as e:
        print("DB error: %s" % e)
        return []


    if messenger.unit == "dream": 
        totalAnimFootageNumInFrames = convertFootageToFrames(totalAnimFootage[0][0])
        totalRAFootageNumInFrames = convertFootageToFrames(totalAnimFootage[0][0])
    else:
        totalAnimFootageNumInFrames = animProgressInFrames[0][2]
        totalRAFootageNumInFrames = animProgressInFrames[0][3]

    #Calculate total percentages
    percentFramesDoneAnim = calculateProgressPercentage(animProgressInFrames[0][0], totalAnimFootageNumInFrames)
    percentFramesDoneRenderAnim = calculateProgressPercentage(animProgressInFrames[0][1], totalRAFootageNumInFrames)

    # Message to send to Slack 
    slackFootageMessage = """
        :film_projector:  Overall percentage of Animation Footage Done is {} ({})
        Overall percentage of Render Anim Footage Done is {} ({})
        """.format(str(calculateFramesInFootage(animProgressInFrames[0][0])) + "/" + totalAnimFootage[0][0],
            percentFramesDoneAnim, 
            calculateFramesInFootage(animProgressInFrames[0][1]) + "/" + totalAnimFootage[0][0],
            percentFramesDoneRenderAnim)
    #Adding column headers for slack
    slackFootageMessage += "```{:<5} {:<18} {:<18} {:<1}\n".format("Seq", "Anim Appr'd", "Anim Done", "RenderAnim Done")
    
    #Looping over each of the sequences and calculating total number of animation frames, animation done frames, 
    # render anim frames and render anim done frames
    for frames in seqProgressInFrames:
        animFramesApprovedDonePercent = calculateProgressPercentage(frames[1], frames[2])
        animFramesDonePercent = calculateProgressPercentage(frames[3], frames[2])
        renderAnimSeqFramesDonePercent = calculateProgressPercentage(frames[5], frames[4])

        #Appending list of sequence data to slack message
        slackFootageMessage += "{:<5} {:<18} {:<18} {:<1}\n".format(
            frames[0],
            calculateFramesInFootage(frames[1]) + "/" + calculateFramesInFootage(frames[2]) + "(" + animFramesApprovedDonePercent + ")",
            calculateFramesInFootage(frames[3]) + "/" + calculateFramesInFootage(frames[2]) + "(" + animFramesDonePercent + ")",
            calculateFramesInFootage(frames[5]) + "/" + calculateFramesInFootage(frames[4]) + "(" + renderAnimSeqFramesDonePercent + ")" )
    slackFootageMessage += "```"
    #Send slack message
    messenger.sendSlack(slackFootageMessage)

def main():
    options = parseArgs()

    alert = " ".join(["@"+x for x in options.alert.split(',')]) if options.alert else None

    messenger = Messenger(options.channel, options.unit, alert, options.debug)

    calculateAnimationProgressInShots(messenger)

    calculateAnimationProgressInFootage(messenger)



if __name__=="__main__":
    main()
