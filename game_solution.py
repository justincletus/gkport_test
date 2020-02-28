import random

def unique_random_num(num, val):
    l = len(num)
    for i in num:
        if i == val:
            num.remove(val)
            break
    return num



player1_points = 0
player2_points = 0

values = [1, 2, 3, 4, 5, 6, 7, 8, 9,10]
values2 = values


unique_values = []

random_num = random.choice(values2)

# print(unique_random_num(values2, random_num))

def player_values(values2):
    count = 0
    while(count < 10):
        val = random.choice(values2)
        unique_values.append(val)
        values2 = unique_random_num(values2, val)
        count +=1

    return unique_values

player1 = player_values(values2)

player2 = player_values(player1)

print(player1, player2)


game = 0
while(game < 10):
    player1_num = random.choice(player1)
    player2_num = random.choice(player2)
    player1 = unique_random_num(player1, player1_num)
    player2 = unique_random_num(player2, player2_num)

    if player1_num == player2_num:
        player1_points +=1
        player2_points +=1

    elif (player1_num < player2_num):
        if player1_num == 1:
            player1_points +=1
        else:
            player2_points +=2
    elif (player2_num < player1_num):
        if player2_num == 1:
            player2_points +=1
        else:
            player1_points +=2
    if(player1_points == 5 | player2_points == 5):
        print("I am here")
        break
    game +=1
