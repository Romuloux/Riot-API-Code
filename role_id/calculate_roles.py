import sys
from sklearn.cluster import AffinityPropagation, SpectralClustering
from sklearn import metrics
from sklearn.datasets.samples_generator import make_blobs
import numpy as np
from tools import load_obj, printTable

def main():
	# Setup champion matrices
	champs = load_obj('champion_id_to_name.pkl')
	champId_to_champName = load_obj('champion_id_to_name.pkl')
	champs = [str(champId_to_champName[key]) for key in champId_to_champName]
	champs.sort()
	champs = [str(x) for x in champs]
	champName_to_champID = {v: k for k,v in champId_to_champName.items()}

	# Champ ID --> matrix index
	champID_to_matrixIndex = {}
	for i,c in enumerate(champs):
		champID_to_matrixIndex[champName_to_champID[c]] = i;
	# Matrix index --> Champ ID
	matrixIndex_to_champID = {v: k for k,v in champID_to_matrixIndex.items()}

	matrixIndex_to_champName = {}
	for champid,index in champID_to_matrixIndex.items():
		matrixIndex_to_champName[index] = champId_to_champName[champid]
	champName_to_matrixIndex = {v: k for k,v in matrixIndex_to_champName.items()}
	#print(champName_to_matrixIndex)


	print("Generating Affinity Matrix...")
	affinity = [ [0.0 for i in range(len(champs))] for j in range(len(champs)) ]
	winnersfile = 'winners_temp.txt' #sys.argv[1]
	losersfile = 'losers_temp.txt' #sys.argv[2]
	winners = open(winnersfile).readlines()
	losers = open(losersfile).readlines()
	winners = [set([int(x) for x in line.strip().split(",")]) for line in winners]
	losers =  [set([int(x) for x in line.strip().split(",")]) for line in losers]
	stop = len(winners)
	composition = winners + losers # You can use this line or the below line; in theory I think this should work better, but it is up to you. Try both and look at the results.
	#composition = [winners[i] | losers[i] for i in range(stop)]
	stop = len(composition)

	total = 0.0
	count = 0.0
	for i in range(stop):
		if(champName_to_champID['Lucian'] in composition[i]):
			total += 1.0
			if(champName_to_champID['Ziggs'] in composition[i]):
				count += 1.0
		for champ in composition[i]:
			for other in composition[i]:
				affinity[champID_to_matrixIndex[champ]][champID_to_matrixIndex[other]] += 0.5
				affinity[champID_to_matrixIndex[other]][champID_to_matrixIndex[champ]] += 0.5
	for c1 in range(len(champs)):
		for c2 in range(len(champs)):
			if(c1 == c2): continue
			affinity[c1][c2] = affinity[c1][c2] / (affinity[c2][c2]) #(0.5*affinity[c1][c1]+0.5*affinity[c2][c2])

	for c1 in range(len(champs)):
		affinity[c1][c1] = 0

	averages = [i for i in range(len(champs))]
	for i in averages:
		averages[i] = sum(affinity[i])/len(affinity[i])
	#print(sum(affinity[champName_to_matrixIndex['Urgot']])/len(affinity[champName_to_matrixIndex['Urgot']]))
	for i in range(len(affinity)):
		affinity[i] = [-x/averages[i] for x in affinity[i]]


	#affinity = open('temp.txt').readlines()
	#affinity = [line.strip().split() for line in affinity]
	#affinity = [[float(x) for x in line] for line in affinity]
	affinity = np.array(affinity)
	print(affinity)
	#return 0


	# Check which values of preference result in 5 clusters
	# I am trying values between -10 and 10, you can choose others
	# if you think they could result in 5 clusters.
	preferenceList = []
	preferenceTest = True
	if(preferenceTest):
		#for i in range(-500,500):
		for i in range(-10,10):
			af = AffinityPropagation(affinity='precomputed',preference=i).fit(affinity)
			cluster_centers_indices = af.cluster_centers_indices_
			if(cluster_centers_indices != None):
				n_clusters_ = len(cluster_centers_indices)
				if(n_clusters_ != len(champs)): print(n_clusters_,i)
				if(n_clusters_== 5): preferenceList.append(i)


	# Set a role dictionary by hand to give labels to the clusters
	# Hopefully these will never change
	roles = {
		"Top":     ['Irelia', 'Renekton'],
		"Mid":     ['Ahri',   'Ziggs'],
		"Jungle":  ['Amumu',  'Nautilus'],
		"Adc":     ['Draven', 'Caitlyn'],
		"Support": ['Taric',  'Braum']}

	# Compute Affinity Propagation
	# Set preferenceList to the values you found above that result in 5 clusters
	if(not preferenceTest):	preferenceList = [-3,-4,-5,-6]
	clusterLists = [{} for i in range(len(preferenceList))]
	for ind,preference in enumerate(preferenceList):
		print("Computing Affinity Propagation with preference={0}...".format(preference))
		af = AffinityPropagation(affinity='precomputed',preference=preference).fit(affinity)
		cluster_centers_indices = af.cluster_centers_indices_
		labels = af.labels_
		n_clusters_ = len(cluster_centers_indices)

		print("\nCenter of {0} clusters:".format(n_clusters_))
		print([matrixIndex_to_champName[x] for x in cluster_centers_indices])

		clusters = {}
		for i in range(n_clusters_):
			clusters[i] = []
		for i,cnum in enumerate(labels):
			clusters[cnum].append(i)
		print("\nClusters: {0}".format([len(x) for key,x in clusters.items()]))
		for key in clusters:
			lane = None
			for role,c in roles.items():
				if(all([champName_to_matrixIndex[x] in clusters[key] for x in c])):
					lane = role
			if(lane == None): raise Exception("You need to redefine the roles dictionary. The canonical champions I picked are not correct for this dataset.")
			clusterLists[ind][lane] = [matrixIndex_to_champName[x] for x in clusters[key]]
			print( lane + ':\t' + ', '.join(clusterLists[ind][lane]))
			print('')

	# Compare clusters for different values of "preference"
	# You can pick to use any of these.
	# I use the last one because that one is what the other variables
	# (e.g. cluster_centers_indices) have been calculated for.
	# You can choose a different one, but you have to manually specify it
	# and change some code.
	table = [ ['Champion'], ['changed from lane'], ['to lane:'] ]
	for cluster in clusterLists[1:]: # Compare each i+1 list to the i=0 list
		for key in roles:
			for champ in cluster[key]:
				if(champ not in clusterLists[0][key]):
					fromLane = None
					for role in clusterLists[0]:
						if(champ in clusterLists[0][role]): fromLane = role
					#print("Champion {0}\tchanged from\t{2}\tto {1}".format(champ,key,fromLane))
					table[0].append(champ)
					table[1].append(fromLane)
					table[2].append(key)
	table = printTable(table)
	print(table)
	print('')


	# Calculate and save/print the final table of data that you want to see.
	if(True):
		order = []
		for c in cluster_centers_indices:
			for role in roles:
				if(matrixIndex_to_champName[c] in clusterLists[-1][role]):
					order.append(role)
		table = [ ['Role Matrix'] ]#, ['Jungle'], ['Top'], ['Support'], ['Adc'], ['Mid'] ]
		table.append(['Primary Role'])
		for role in order:
			table.append([role])
		f = open('output.txt','w')
		for champID,champName in matrixIndex_to_champName.items():
			cat_percents = {}
			dists = {}
			# We have a specific champion specified by the above for loop
			# We will calculate the affinity of that champion to all champions in each
			# role. E.g. if champName=='Sivir' then we will look at all the roles (let's
			# assume role=='Jungle' for now) and calculate the affinity between 'Siver'
			# and all the champions who have been identified as 'Jungle'. Then I average
			# all these affinity values together and that is the "affinity" for 'Sivir'
			# to the 'Jungle' role. I store each of these average values into a dictionary
			# called 'cat_percents' which stands for category percents.
			# You can think of the 'affinity' as the distance from one champ to another.
			# The smaller the distance, the more likely they are to play the same role.
			for role in clusterLists[-1]:
				dists[role] = []
				for c in clusterLists[-1][role]:
					c = champName_to_matrixIndex[c]
					dists[role].append((-affinity[c,champID]-affinity[champID,c])/2.0)
					avg_dist = sum(dists[role])/len(dists[role])
				cat_percents[role] = avg_dist

			# Do a bunch of normalization on the outputs of cat_percents to get the numbers to be between 0 and 1.
			cat_min = min(cat_percents.values())
			for role in cat_percents:
				cat_percents[role] = cat_percents[role] - cat_min

			cat_max = max(cat_percents.values())
			for role in cat_percents:
				cat_percents[role] = cat_percents[role]/cat_max
				cat_percents[role] = 1 - cat_percents[role]
			
			cat_sum = sum(cat_percents.values())
			for role in cat_percents:
				cat_percents[role] = cat_percents[role]/cat_sum*100
				cat_percents[role] = round(cat_percents[role],2)

			table[0].append("".join(champName.split())) # Champion name, remove all whitespace
			table[2].append(cat_percents[order[0]]) # Order[0] == e.g Jungle
			table[3].append(cat_percents[order[1]]) # Order[1]
			table[4].append(cat_percents[order[2]]) # Order[2]
			table[5].append(cat_percents[order[3]]) # Order[3]
			table[6].append(cat_percents[order[4]]) # Order[4]

			lane = None
			for role in clusterLists[-1]:
				if(champName in clusterLists[-1][role]):
					lane = role
			table[1].append(lane) # Primary Role
		table = printTable(table)
		print(table)
		f.write(table)
		f.close()
		print('')



if __name__ == '__main__':
	main()