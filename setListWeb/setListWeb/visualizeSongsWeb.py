# Backend scipt for Hack-A-Thing Assignment, CS 98
# Optimized for web.
# Author: Alexander Danilowicz and Weiling Huang
#
# Citations:
#	Script originally written by Alex Danilowicz
#	as a personal project. Script ran locally.
#	This version is heavily modified and optimized for web from original version.
#	Author of original setlistfm scraping (where I got the idea): ryanleewatts
# 	Github: https://github.com/ryanleewatts
# 	Original script: https://github.com/ryanleewatts/coding-project/blob/master/scraper/SetlistScript.py
#	Danilowicz original author of all pandas/matplotlib code,
#	as well as modification of original BeautifulSoup code

from bs4 import BeautifulSoup as bs
import requests
import pandas as pd
from matplotlib.pyplot import cm
import matplotlib.pyplot as plt
import matplotlib.ticker as mtick
import numpy as np
import random
from collections import defaultdict
import os
from django.conf import settings

# THINGS YOU MUST CHANGE
#ARTIST = "Radiohead"
#UNIQUE = "radiohead-bd6bd12.html"
#URL_TO_STOP_AT = "united-center-chicago-il-7bea6a40.html" # Note: get rid of HTTPS part
#URL_TO_START_AT = "html" # this url will be the first one to be scraped, if put in

# OPTIONAL THINGS TO CHANGE
YEAR = "2018"
SORT_ALBUM = False # toggle if you want to sort by album or not. if false, sorts by count
#FILE = ARTIST + "-Data" + "-" + YEAR +".xlsx" # filename
#TITLE = "Frequency of Songs during " + ARTIST + "'s Tour"
SONGS_TO_IGNORE = ["I Wish I Knew How It Would Feel to Be Free", "Egyptian Fantasy"]
MAX_PAGES = 1 # max to scrape, not even close to used if URL_TO_STOP set properly
FONT_SIZE_TICKS = 3
FONT_Y = 5 # for labels
OPTIONAL_TITLE_ADDITIONAL = ", North America " + YEAR
#TITLE = TITLE + OPTIONAL_TITLE_ADDITIONAL
color_album_dict = {}

def scrape(artist, unique, startURL, stopURL):
	UNIQUE_URL = "https://www.setlist.fm/setlists/" + unique + "?page="
	SONG_URL = "https://www.setlist.fm/stats/songs/" + unique + "?song="  # notice difference: /stats/
	visited = {} # key song, album is value
	links = []
	dm = []
	#my_file = Path("./" + FILE)
	#if not my_file.is_file(): # only do scraping if file doesn't exist already
	break_bool = False
	start = False
	for i in range(MAX_PAGES):
		print("SCRAPING SCRAPING")
		if break_bool:
			break
		url = UNIQUE_URL + str(i + 1)
		r = requests.get(url)
		print(r.content)
		soup = bs(r.content, "lxml")
		for link in soup.find_all('a', class_='summary url'):

			setlist = (link.get('href'))
			completeurl = 'http://www.setlists.fm' + setlist[2:]
			print("Getting url: " + completeurl) # print the output

			if startURL in completeurl:
				start = True
			if start:
				print("Getting url: " + completeurl) # print the output
				links.append(completeurl)
			# stop at this url
			if stopURL in completeurl:
				break_bool = True
				break # stop at this setlist

	# Scrape every url in that list
	for item in links:
		# 1. Scrape the date
		r = requests.get(item)
		soup = bs(r.content, "lxml")
		for datehtml in soup.find_all('em', class_='link', text=True):
			date = datehtml.text[:-7]
			date = date.partition(",")[0]
			date = date.replace(" ", "")

		# 2. Scrape the setlist
		songs = []
		for songHTML in soup.find_all('div', class_='songPart'):
			songstext = songHTML.text
			thesong = songstext.encode('utf-8').rstrip().strip().decode("utf-8")
			if thesong not in SONGS_TO_IGNORE:
				songs.append(thesong)

		#3. Scrape the album
		for song in songs:
			if song not in visited:
				r = requests.get(SONG_URL + song)
				soup = bs(r.content, "lxml")

				thenext = False
				for album in soup.find_all('span'):
					if thenext:
						thealbum = album.text
						thealbum = thealbum.replace("(Album)", "")
						thealbum = thealbum.replace("(Single)", "")
						thealbum = thealbum.strip("'")
						thealbum = thealbum.rstrip()
						visited[str(song)] = thealbum
						break
					if album.text == "From the release": # album name falls under this span
						thenext = True
			else:
				thealbum = visited[str(song)]

			try:
				dm.append([date, song, thealbum])
			except:
				print("skipping over this song because no setlist data populated yet")

	df = pd.DataFrame(dm, columns=['Date', 'Track', 'Album'])
	print(df)
	visualize_album(df, artist)

def create_clean_df(df):
	total_df = df.copy()
	count = len(total_df['Track'].unique())
	total = len(total_df['Date'].unique())

	albums = df[['Track', 'Album']]
	# put track as index, date in row
	unique_df = df.groupby(df['Track']).nunique() # get count

	# clean up and rename
	del unique_df["Album"]
	del unique_df["Track"]
	unique_df = unique_df.rename(columns={'Date': 'Count_Played'})

	# merge with albums df, I assume there's a better way...
	albums = albums.set_index('Track')
	albums = albums[~albums.index.duplicated(keep='first')]
	unique_df = pd.merge(unique_df, albums, left_index=True, right_index=True)
	print("runing pandas")
	return (total, unique_df)

def visualize_album(df, artist):
	(total, unique_df) = create_clean_df(df)
	album_df = unique_df.copy()
	color_album_dict = return_color_album_dict(album_df['Album'].unique().tolist())

	unique_df['Album'] = pd.Categorical(unique_df['Album'], color_album_dict.keys()) # order it by dictionary

	if SORT_ALBUM: # sort by album, then count
		unique_df = unique_df.sort_values(['Album', 'Count_Played'], ascending=True)
		ORDERCOUNT = ""
	else:
		ORDERCOUNT = "-OrderedByCount"
		unique_df = unique_df.sort_values(['Count_Played', 'Album'], ascending=True)

	# convert to percentages
	unique_df['Frequency'] = unique_df['Count_Played'].div(total).multiply(100)

	ax = unique_df.drop(['Count_Played'], axis=1).plot(kind='barh', legend=True, color=[unique_df.Album.map(color_album_dict)])

	format(ax, color_album_dict, total, unique_df)

	plt.savefig(os.path.join(settings.BASE_DIR, "catalog/static/images/graph.png"), format='png', dpi=175)
	#plt.show()

def format(ax, color_dict, total, df):
	# The following two lines generate custom fake lines that will be used as legend entries:
	markers = [plt.Line2D([0,0],[0,0],color=color, marker='o', linestyle='') for color in color_dict.values()]
	plt.legend(markers, color_dict.keys(), numpoints=1, fontsize='7')

	# formatting labels
	ax.set_xlabel("Frequency" + " (n=" + str(total) + " concerts)")
	fmt = '%.0f%%' # Format you want the ticks, e.g. '40%'
	xticks = mtick.FormatStrFormatter(fmt)
	ax.xaxis.set_major_formatter(xticks)

	ax.set_ylabel("Track (Count: " + str(len(df.index)) + ")")
	plt.yticks(fontsize=FONT_Y)
	plt.title("Data", fontsize=10)

	for i in ax.patches:
		ax.text(i.get_width()+.3, i.get_y()+.38, str(round((i.get_width()*total/100), 1)).replace(".0", ""), fontsize=FONT_SIZE_TICKS, color='dimgrey')

	ax.invert_yaxis()
	plt.tight_layout()


# helper function to sort by date
def sorting(date):
	string = ''.join(x for x in date if x.isdigit())
	return int(string)

def return_color_album_dict(albums_list):
	color_album_dict = {}

	number_of_colors = len(albums_list)
	random_hex_list = ["#"+''.join([random.choice('0123456789ABCDEF') for j in range(6)])
	for i in range(number_of_colors)]

	i = 0
	for album in albums_list:
		color_album_dict[album] = str(random_hex_list[i])
		i += 1

	return color_album_dict
