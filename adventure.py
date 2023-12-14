import json
import os
import random

'''
Allows the user to navigate around a (text based) world.
Data comes from adventure.json
'''

START = 'Whiterun'
FINISH = "Dining Hall"
MAP_NAME = "custom.json"
inventory = list()

def main():
	"""Load the game map from a JSON file, ensuring that 'START' is present in the map."""
	data = json.load(open(MAP_NAME))
	assert START in data, "START not in map"
	play_game(data)


def play_game(data):
	"""Intilize player data by asking for there name, take appropariate action for new and existing users. Print menu"""
	print('Welcome to the ICS 31 Adventure Game:\n')
	player_data = intilize_player_data()
	print_menu(data, player_data)


def finish_game(player_data):
	"""Print winning message. Rest player information as if they were new."""
	print("You win!!!\n You have returned home.")
	create_player(player_data[0])
	exit()

def return_special_items_list(map_data, player_data):
	"""Check for itens not in user inventory and returns list of items avaiable for pick up."""
	player_location = player_data[1]["location"]
	map_location = map_data[player_location]
	object_list = list()
	for map_object in map_location["objects"]:
		if map_object["type"] == "special" and not map_object["name"] in inventory:
			object_list.append(map_object["name"])
	return object_list


def move(map_data, player_data, user_input):
	"""Move user to location, and saves data."""
	player_database = call_player_database()
	player_name = player_data[0]
	player_location = player_data[1]["location"]
	if map_data[player_location]["moves"][user_input] == FINISH:
		finish_game(player_data)
	player_database[player_name]["location"] = map_data[player_location]["moves"][user_input]
	player_new_data = write_player_database(player_name, player_database)
	options_menu(map_data, player_new_data)


def pickup_item(player_data, user_input):
	"""Add item to user inventory and saves."""
	player_database = call_player_database()
	player_name = player_data[0]
	player_database[player_name]["inventory"].append(user_input)
	inventory.append(user_input)
	write_player_database(player_name, player_database)


def move_user(data, current, move):
	"""Return next location."""
	return data[current]["moves"][move]


def see_objects_location(data, current):
	"""Chceck if any objects are in map,"""
	object_list = list()
	if check_items_describe(data, current):
		for item in data[current]["objects"]:
			if not item["name"] in inventory:
				object_list.append(item["name"])
	statement = " and ".join(object_list)
	if not len(object_list) == 0:
		return "You see " + statement + ".\n"
	else:
		return ""


def check_items_describe(map_data, current):
	"""Check if there are items in the map location."""
	map_location = map_data[current]
	return "objects" in map_location


def describe(data, current):
	"""Describe location, items in map, and posible options."""
	text = ''
	text += f'{data[current]["text"]}\n'
	text += see_objects_location(data, current)
	text += "\nYour options are:\n"
	map_directions = list(data[current]["moves"].keys())
	for direction in map_directions:
		text += f"'{direction}' to go to {data[current]['moves'][direction]}\n"
	# if check_items_describe(data, current):
	# 	for object in data[current]["objects"]:
	# 		if object["type"] == "special" and not object["name"] in inventory:
	# 			text += f"pick up >{object['name']}<\n"
	return text


def options_menu(map_data, player_data):
	"""Describes location, and get user input."""
	player_location = player_data[1]["location"]
	map_directions = list(map_data[player_location]["moves"].keys())
	item_pickup_list = list()
	print(describe(map_data, player_location))
	if check_items_describe(map_data, player_location):
		item_pickup_list = return_special_items_list(map_data, player_data)
	user_input = input("What would you like to do next?\n").lower()
	if user_input in map_directions:
		move(map_data, player_data, user_input)
	elif user_input in item_pickup_list:
		pickup_item(player_data, user_input)
		item_pickup_list.remove(user_input)
		options_menu(map_data, player_data)
	elif user_input == 'exit' or user_input == 'quit':
		exit()
	else:
		options_menu(map_data, player_data)


def print_menu(map_data, player_data):
	"""Check if player location is a location, if not reset character."""
	player_location = player_data[1]["location"]
	if player_location in map_data:
		options_menu(map_data, player_data)
	else:
		new_player_data = create_player(player_data[0])
		options_menu(map_data, new_player_data)


def random_start():
	"""Get random location from map."""
	map_data = call_map_data()
	locations_lists = list(map_data.keys())
	random_index = random.randrange(len(locations_lists))
	random_location = locations_lists[random_index]
	return random_location


def call_player_database():
	"""Return all player data."""
	if os.path.exists('player_database.json'):
		with open('player_database.json', 'r') as file:
			data = json.load(file)
	else:
		data = dict()
	return data


def write_player_database(player_name, updated_database):
	"""Update player data, return updated player data."""
	with open('player_database.json', 'w') as file:
		json.dump(updated_database, file, indent = 4)
	return [player_name, updated_database[player_name]]


def intilize_player_data():
	"""Ask for uername."""
	database = call_player_database()
	player_username = input("Enter your player name:\n").lower()
	while len(player_username) == 0:
		player_username = input("Enter your player name:\n").lower()
	if player_username in database:
		return load_player_data(player_username)
	else:
		return create_player(player_username)


def load_player_data(player_name):
	"""Load returning player data."""
	database = call_player_database()
	player_data = [player_name, database[player_name]]
	global inventory
	inventory = database[player_name]["inventory"]
	return player_data


def call_map_data():
	"""Call map data."""
	data = json.load(open(MAP_NAME))
	return data

def create_player(player_name):
	"""Create new player., and creating neccessary data strcture."""
	database = call_player_database()
	database[player_name] = dict()
	database[player_name]["location"] = random_start()
	database[player_name]["inventory"] = list()
	global inventory
	inventory = list()
	return write_player_database(player_name, database)


if __name__ == '__main__':
	main()
	# print(describe(call_map_data(), "Whiterun"))