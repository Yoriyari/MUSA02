#===============================================================================
# Lewd v1.2.3
# by Yoriyari
#===============================================================================
# Update History
# ..............................................................................
# 23 Mar 2025 - v1.2.3; Centralized servers whitelisted for NSFW commands.
#               Removed file URL from reply, now relying on post URL embed. -YY
# 28 Apr 2024 - v1.2.2; Made non-whitelisted servers not return a message as to
#				why the command doesn't work. Silence. -YY
# 24 Sep 2023 - v1.2.1; Removed a message listener that just lowercased a
#				message and then did nothing else with it. -YY
# 26 Aug 2021 - v1.2; E621 posts now supply a link to the main page and posts
#               with over 20 species tags are skipped unless the "group" tag is
#               part of the request. -YY
# 08 Aug 2021 - v1.1; Added timer to prevent the same post being returned twice
#               within a short timeframe. -YY
# 21 Mar 2021 - v1.0; Finished file. -YY
#===============================================================================
# Notes
# ..............................................................................
# - It may be preferable for the timer to prevent identical posts being posted
#   only within the same channel for that timeframe, instead of globally. -YY
#===============================================================================
# Description
# ..............................................................................
# lewd.py allows users to request random images from porn sites such as e621.
#===============================================================================

#Import Modules
import discord
from discord.ext import commands, tasks

from common.private_ids import guilds_whitelisted_for_nsfw

import json
import requests
from requests.auth import HTTPBasicAuth

#Cog Setup
class RecentPost:
	def __init__(self, parent, id):
		self.parent = parent
		self.id = id
		self.timer.start()

	@tasks.loop(hours=12.0, count=2)
	async def timer(self):
		if self.timer.current_loop != 0:
			await self.parent.reallow_post(self.id)

class LewdCog(commands.Cog):
	def __init__(self, client):
		self.client = client
		self.recent_posts = []

	@commands.Cog.listener()
	async def on_ready(self):
		print("Lewd cog loaded.")

	def is_post_webm(self, post):
		for tag in post["tags"]["meta"]:
			if tag == "webm":
				return True
		return False

	def get_post_url(self, post):
		post_url = "https://e621.net/posts/" + str(post["id"])
        #post_url = "<" + post_url + ">\n" + post["file"]["url"] # Adds the file URL
		return post_url

	async def reallow_post(self, id):
		for post in self.recent_posts:
			if id == post.id:
				self.recent_posts.remove(post)
				break

	##Browse E621
	@commands.command(aliases=["e6","e62"])
	async def e621(self, ctx, *tags):
		if ctx.guild and ctx.guild.id not in guilds_whitelisted_for_nsfw():
			return
		headers = {"User-Agent":"Random-E621-Posts-Discord-Bot/1.0 (by Fluffybuck on E621)"}
		APIuser = "Fluffybuck"
		APIkey = "qor2sYTS3PawCwrbkx1WJUQQ"
		grabURL = "https://e621.net/posts.json?limit=50&tags=order:random -flash -scat -gore -young"
		for tag in tags:
			grabURL += " " + str(tag)
		req = requests.get(grabURL, headers=headers, auth=HTTPBasicAuth(APIuser,APIkey))
		if req.status_code == 200:
			data = req.json()
			post = "No results!"
			iter = 0
			if len(data["posts"]) > 0:
				while (iter < len(data["posts"]) and iter < 50) and (any(data["posts"][iter]["id"] == post.id for post in self.recent_posts) or (len(data["posts"][iter]["tags"]["species"]) > 20 and "group" not in tags)):
					iter += 1
				if iter == len(data["posts"]) or iter == 50:
					post = "Only duplicates found!"
				else:
					post = self.get_post_url(data["posts"][iter])
					self.recent_posts.append(RecentPost(self, data["posts"][iter]["id"]))
			await ctx.channel.send(post)
		else:
			await ctx.channel.send("Couldn't contact e621. Error code: " + str(req.status_code))

async def setup(client):
    await client.add_cog(LewdCog(client))
