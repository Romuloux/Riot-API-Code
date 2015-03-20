## What is this?
This is a repo with code I use to get and analyze match data from Riot's League of Legends API.

I use the RiotWatcher code (see below) to pull game data. Other files are ones I have created to do various things.

## Forked from RiotWatcher
This RiotWatcher code was forked from RiotWatcher v1.2.4

I made a modification to automattically retry server errors, otherwise it is the same.

See https://github.com/pseudonym117/Riot-Watcher/blob/master/riotwatcher.py for the original version.

## Pulling data
My addition is the get\_match\_data.py file that gives a fairly clean way to pull API data.

There is plenty of room for your own modifications. It will definitely help to read through the code.

It relies on the RiotWatcher code, so that is why it is included.

You manually have to add your own unpulled\_summonerIds.txt file that contains at least one summonerId that you want to pull. Multiple summonerIds should be put on different lines.

This code will start where it let off unless you tell it to reset. In this case, you it is expected that you have copied in your backed up (or new) set of summonerId data. If you won't want to pull data that you have already pulled, you will have to comment out the lines in the main() function that overwrite the pulled\_\*.txt files within the reset `if` statement.

You can reset by running `python get_match_data.py reset`.

## Analysis

### Role Identification

I have written code to identify which role each champion plays in and in what % of the games. An example excel file with these results is included (data was from 400,000 games collected using the above mentioned method and only using diamond tier summoners). This code can be found in the role id folder. To run the code, numpy and scipy are necessary, among minor other things which were likely included with your python install. The code takes a little while to run, so dont expect it to produce results immediately.
