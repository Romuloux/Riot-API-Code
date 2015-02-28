## Forked from RiotWatcher
This RiotWatcher code was forked from RiotWatcher v1.2.4

I made a modification to automattically retry server errors, otherwise it is the same.

See https://github.com/pseudonym117/Riot-Watcher/blob/master/riotwatcher.py for the original version.

## Pulling data
My addition is the get\_match\_data.py file that gives fairly clean way to pull API data.

There is plenty of room for your own modifications. It will definitely help to read through the code.

It relies on the RiotWatcher code, so that is why it is included.

You manually have to add your own unpulled\_summonerIds.txt  file that contains at least one summonerId that you want to pull. Multiple summonerIds should be put on different lines.

This code will result where it let off unless you tell it to reset. In this case, you it is expected that you have copied in your backed up (or new) set of summonerId data. If you won't want to pull data that you have already pulled, you will have to comment out the lines in the main() function that overwrite these files within the reset if statement.

e.g. `python get_match_data.py reset`
