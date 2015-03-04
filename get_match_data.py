import sys
import time
from riotwatcher import RiotWatcher, NORTH_AMERICA, LoLException
from tools import save_obj

def secondsToStr(t):
    rediv = lambda ll,b : list(divmod(ll[0],b)) + ll[1:]
    return "%d:%02d:%02d.%03d" % tuple(reduce(rediv,[[t*1000,],1000,60,60]))

#key = #PUT YOUR API KEY HERE
w = RiotWatcher(key)

def get_participants_for_further_pulls(match):
    """ This function takes a riot api 'match' and returns only selected
        participant information. You may add to the returned information
        if you want.
        The return value is a list of dictionaries, one for each
        participant in the match. """
    participants = [ {} for i in range(len(match['participants'])) ]
    for i,p in enumerate(match['participants']):
        participants[i]['highestAchievedSeasonTier'] = p['highestAchievedSeasonTier']
        participants[i]['summonerId'] = match['participantIdentities'][p['participantId']-1]['player']['summonerId']
    return participants

def get_match_information_to_save(match):
    """ This function takes a riot api 'match' and parses
        through it to save only the information you want. You can
        choose to save everything, or only specific things.
        The return value is a dictionary containing only the
        information you want to save for the match. """
    # Uncomment the following line to save all the data
    #return match
    data = {}
    # The below code is an example of specific data to save
    data['matchId'] = match['matchId'] # You MUST at least include this field!
    data['matchMode'] = match['matchMode']
    data['matchCreation'] = match['matchCreation']
    data['matchVersion'] = match['matchVersion']
    data['queueType'] = match['queueType']
    data['mapId'] = match['mapId']
    data['winningChamps'] = []
    data['losingChamps'] = []
    for p in match['participants']:
        if(p['stats']['winner']):
            data['winningChamps'].append(p['championId'])
        else:
            data['losingChamps'].append(p['championId'])
    return data

def parse_match_history(match_history):
    """ This function takes a summoner's match history and
        returns the matchIds from that match history along
        with the full list of matches. There is no reason
        to modify this function. """
    matchIds = [ match['matchId'] for match in match_history['matches'] ]
    return matchIds, match_history['matches']

def pull_this_match(match):
    """ This function takes a match from the *match history* request
        and returns True or False based on whether you want to 
        pull the match. If you want to pull every match, regardless
        of map type, etc. then just return True. """
    # This line parses the match's patch version into a usable format
    # For example, if the patch is 4.20.0.319 then
    # version == [4, 20, 0, 319]
    version = [int(x) for x in match['matchVersion'].split('.')]
    if(match['mapId'] == 11
        and match['queueType'] == 'RANKED_SOLO_5x5'):
        #and version[0] == 5 and version[1] >= 3):
        return True
    else:
        return False

def save_this_match(match):
    """ This function takes a match from the *match* request
        and returns True or False based on whether you want to
        save the match data. If you want to save every match
        then just return True. """
    # I will only save the match if there is a diamond player in it.
    save = False
    for p in match['participants']:
        if(p['highestAchievedSeasonTier'] == 'DIAMOND'):
            save = True
            break
    return save

def pull_this_participant(p):
    """ This function takes a participant from a match and
        returns True or False based on whether you want to 
        pull this summoner's data. """
    # I only want to pull the summoner if it is diamond tier.
    # I can only get highestAchievedSeasonTier  so I'll use that.
    if(p['highestAchievedSeasonTier'] == 'DIAMOND'):
        return True
    else:
        return False



def main():
    # BEFORE YOU RUN THIS FILE, MAKE A BACKUP OF ALL THE DATA IT'S GOING TO USE.
    # This data will be in one of the files opened below, so make copies
    # of all those files in case something goes wrong.

    try:
        if(sys.argv[1] == 'reset'):
            print("WARING: RESETTING ALL DATA IN 2 SECONDS!")
            print("You must manually re-copy your backed up version of unpulled_summoners.txt into that file.")
            print("The actual game data is not deleted, but it will be overwritten.")
            time.sleep(2)
            open('pulled_summoners.txt','w')
            open('pulled_matchIds.txt','w')
            open('paramfile.in','w').write('0')
    except:
        pass
    
    try:
        pulled_matchIds = open('pulled_matchIds.txt','r').readlines()
        pulled_matchIds = [int(x) for x in pulled_matchIds]
    except IOError:
        pulled_matchIds = []
    pulled_matchIds_file =  open('pulled_matchIds.txt','a')

    try:
        pulled_summoners = open('pulled_summoners.txt','r').readlines()
        pulled_summoners = [int(x) for x in pulled_summoners]
    except IOError:
        pulled_summoners = []
    pulled_summoners_file = open('pulled_summoners.txt','a')

    try:
        unpulled_summoners = open('unpulled_summoners.txt','r').readlines()
        unpulled_summoners = [int(x) for x in unpulled_summoners]
    except IOError:
        unpulled_summoners = []

    match_data_to_save = []
    these_pulled_summoners = []
    these_pulled_matches = []
    t_start = time.time()
    num_matches = 0.0
    num_pulled_summoners = 0.0
    pulled_matches = 0.0
    matched_you_actually_wanted = 0.0
    try:
        step = int(open('paramfile.in','r').readline())
    except IOError:
        step = 0
    while(True):
        # Start by getting a new summoner to pull matchID information for
        # If there is a summoner in unpulled_summoners, use that
        # If the unpulled_summoners list is empty, start at the beginning
        # of the summoners we have already pulled (their game data is
        # hopefully out of date by now).
        try:
            new_summoner = unpulled_summoners.pop()
        except IndexError:
            new_summoner = pulled_summoners.pop(0)
            print("Ran out of unpulled summoners, redoing a pulled summoner now. {0}".format(new_team))
        print("Getting match history from summoner: {0}".format(new_summoner))
        try:
            match_history = w.get_match_history(new_summoner,begin_index=0,end_index=15)
        except Exception,e:
            print("An ERROR occurred when pulling match history data for summonerId {0}! {1}".format(new_summoner,e))
            #print traceback.format_exc()
            continue
        try:
            matchIds, matches = parse_match_history(match_history)
        except KeyError,e:
            print("Some field you tried to access did not exist in the pulled summoner data: {0}".format(e))
            continue
        pulled_summoners.append(new_summoner)
        these_pulled_summoners.append(new_summoner)

        # Now we will pull the matches that were in this summoner's match history
        # if we decide it has data we want (see function pull_this_match)
        # If all the information you want is in the match history pull, you
        # can delete the pull request and modify the functions specified
        # however you want.
        for i,match in enumerate(matches):
            if(match['matchId'] not in pulled_matchIds and pull_this_match(match)):
                # Pull match
                print("  Getting match data for matchId {0}...".format(match['matchId']))
                try:
                    match_data = w.get_match(match['matchId'],include_timeline=False)
                except LoLException:
                    pulled_matchIds.append(match_data['matchId'])
                    these_pulled_matches.append(match_data['matchId'])
                    continue
                pulled_matches += 1.0
                # Append the matchId to the pulled matches list
                pulled_matchIds.append(match_data['matchId'])
                these_pulled_matches.append(match_data['matchId'])
                # Get participants in match
                participants = get_participants_for_further_pulls(match_data)
                # Add participants to unpulled summoners if necessary
                for p in participants:
                    # Unforunately, this if statement can take a while if there is enough
                    # data, but it's worth it not to pull data you already have.
                    if(pull_this_participant(p) and p['summonerId'] not in pulled_summoners and p['summonerId'] not in unpulled_summoners):
                        unpulled_summoners.append(p['summonerId'])
                # If the match information is what you want (see the save_this_match function)
                # then append the data you want to save to the list that we will save.
                if(save_this_match(match_data)):
                    # Save only specific information from each match (see the function)
                    match_data = get_match_information_to_save(match_data)
                    match_data_to_save.append(match_data)
                    num_matches += 1
                    matched_you_actually_wanted += 1
        # When we get 100+ games worth of new data, save them all to a new file.
        # This is nice because it prevents your files from becoming enormous,
        # and if you lose one you don't lose them all. It creates a bit more code
        # but I think it's worth it.
        # Note that there will not necessarily be exactly 100 games per file.
        if(num_matches >= 100):
            print("SAVING {0} MATCHES!".format(num_matches))
            # This saves the data as a cPickle. See Python's documentation for more info.
            save_obj(match_data_to_save,'game_data_{0}.pkl'.format(step))
            match_data_to_save = []
            num_matches = 0
            for mid in these_pulled_matches:
                pulled_matchIds_file.write("{0}\n".format(mid))
            # Save (append) the summonerIds we pulled to file
            for summoner in these_pulled_summoners:
                pulled_summoners_file.write("{0}\n".format(summoner))
            these_pulled_summoners = []
            # Save (overwrite) unpulled_summoners to file
            unpulled_summoners_file = open('unpulled_summoners.txt','w')
            for summoner in unpulled_summoners:
                unpulled_summoners_file.write("{0}\n".format(summoner))
            unpulled_summoners_file.close()
            # Increment step
            step += 1
            # Update the parameter file to the step number so that
            # if we restart this python program all our all data
            # does not get erased. Right now the only line in that file
            # is the step number.
            open('paramfile.in','w').write(str(step))
        num_pulled_summoners += 1.0
        print("  Approximate number of successfully pulled matches: {0}".format(pulled_matches))
        print("  Average time per (successful) match request: {0}".format((time.time()-t_start)/matched_you_actually_wanted))
        print("Number of successfully pulled summoners: {0}".format(num_pulled_summoners))
        print("Average time per (successfully pulled) summoner: {0}".format((time.time()-t_start)/num_pulled_summoners))





if __name__ == '__main__':
    main()
