#!/usr/bin/python
# Monty hall problem

import numpy as np

def simulate_prizedoor(nsim):
    answer = np.random.randint(0, 3, size = nsim)
    return answer
    
def simulate_guess(nsim):
    answer = np.random.randint(0, 3, size = nsim)
    return answer

def goat_door(prizedoor, guesses):
	answer = np.zeros(prizedoor.size, dtype=np.int)
	for x in range(0,prizedoor.size):
		y = 0
		while (y < 3):
			if (prizedoor[x] != y and guesses[x] != y):
				answer[x] = y
			y += 1
	return answer

def switch_guess(guesses, goatdoors):
	answer = np.zeros(guesses.size, dtype=np.int)
	for x in range(0,guesses.size):
		y = 0
		while (y < 3):
			if (guesses[x] != y and goatdoors[x] != y):
				answer[x] = y
			y += 1
	return answer

def win_percentage(guesses, prizedoor):
	winrate = 0
	lenght = guesses.size
	for x in xrange(0, lenght):
		if guesses[x] == prizedoor[x]:
			winrate += 1
	winrate / lenght * 100
	return winrate

tries = 10000
prizedoor = simulate_prizedoor(tries)
guesses = simulate_guess(tries)
goats = goat_door(prizedoor, guesses)
print("prizedoor", prizedoor)
print("guesses", guesses)
prizedoor_switch = simulate_prizedoor(tries)
switch = simulate_guess(tries)

goats_switch = goat_door(prizedoor_switch, switch)
switch = switch_guess(switch, goats_switch)

print ("goats", goats)
print ("switch", switch)

print ("winrate for normal ", win_percentage(guesses, prizedoor))
print ("winrate for switch ", win_percentage(switch, prizedoor_switch))

