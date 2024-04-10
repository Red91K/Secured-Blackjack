import random
from security import *

NUMBERS = {
    "2": 2,
    "3": 3,
    "4": 4,
    "5": 5,
    "6": 6,
    "7": 7,
    "8": 8,
    "9": 9,
    "10": 10,
    "J": 10,
    "Q": 10,
    "K": 10,
    "A": 11
}
SYMBOLS = ["Diamonds", "Hearts", "Spades", "Clubs"]

class Card:
    def __init__(self, number:str, symbol:str):
        self.number = number
        self.symbol = symbol
        self.value = NUMBERS[self.number]

    def __eq__(self, other):
        return self.value == other.value

    def __str__(self):
        return f"{self.number} {self.symbol}"

class Deck:
    def __init__(self, cards:list):
        self.cards = cards

    def calculate_sum(self):
        card_sum = 0
        a_exists = False
        for card in self.cards:
            if card.number == "A":
                a_exists = True
            card_sum += card.value
        if card_sum > 21 and a_exists:
            return card_sum - 10
        else:
            return card_sum

    def calculate_true_sum(self):
        return 0 if self.calculate_sum() > 21 else self.calculate_sum()

    def draw_card(self, draw_num: int = 1):
        for i in range(draw_num):
            number = random.choice(list(NUMBERS.keys()))
            symbol = random.choice(SYMBOLS)
            self.cards.append(Card(number, symbol))
        return Card(number, symbol)

    def print_deck(self):
        for card in self.cards:
            print(card)


def blackjack(stake):
    multiplier = 2
    
    dealer_deck = Deck([])
    dealer_deck.draw_card(2)

    # index of the two lists correspond to each other
    user_decks = [Deck([])]
    user_decks_status = [True]  # False if done
    user_decks[0].draw_card(2)

    while True:
        # split cards
        for deck_index in range(len(user_decks)):
            if user_decks[deck_index].cards[0] == user_decks[deck_index].cards[1]:
                print(user_decks[deck_index].cards[0])
                print(user_decks[deck_index].cards[1])
                print(f'\nDealer - {dealer_deck.cards[0]}')
                while True:
                    want_split = input("Would you like to split? [Yes/No]\n")
                    if want_split.lower() == "yes":
                        if read_balance(USERNAME, PASSWORD) < stake:
                            print("YOU AREN'T THAT RICH")
                            continue
                        else:
                            list_user_decks = [deck.cards for deck in user_decks]
                            json_user_decks = []
                            for deck in list_user_decks:
                                json_user_decks.append([str(card) for card in deck])
                            
                            add_activity_log(USERNAME, PASSWORD, "Split",{
                                "Current Stake":stake,
                                "After Stake":stake*2,
                                "Current Balance": read_balance(USERNAME, PASSWORD),
                                "User Decks": json_user_decks,
                                "Dealer Deck": [str(card) for card in dealer_deck.cards]
                            })
                            change_balance(USERNAME, PASSWORD, -stake)
                            stake *= 2
                        
                            user_decks.append(Deck([user_decks[deck_index].cards[1]]))
                            user_decks[deck_index] = Deck([user_decks[deck_index].cards[0]])
                            user_decks_status.append(True)
                            break
                    elif want_split.lower() == "no":
                        break
                    else:
                        print("Invalid option, type [Yes] or [No] without brackets.")
        
        print(f'\nDealer - {dealer_deck.cards[0]}')
        # iterate through user's decks, ask user if they want more cards
        for deck_index in range(len(user_decks)):
            if not user_decks_status[deck_index]:
                continue
            
            print(f'User {("Deck #" + str(deck_index + 1)) * (len(user_decks) > 1)}')
            user_decks[deck_index].print_deck()

            while True:
                want_another = input("Your move: [Stay/Hit/Double Down]\n")
                if want_another.lower() == "hit":
                    new_card = user_decks[deck_index].draw_card()
                    print(f"-> {new_card}\n")
                    if user_decks[deck_index].calculate_true_sum() == 0:
                        user_decks_status[deck_index] = False
                    break
                elif want_another.lower() == "stay":
                    user_decks_status[deck_index] = False
                    break
                elif want_another.lower() == "double down":
                    if read_balance(USERNAME, PASSWORD) < stake:
                        print("YOU AREN'T THAT RICH")
                        continue
                    else:
                        list_user_decks = [deck.cards for deck in user_decks]
                        json_user_decks = []
                        for deck in list_user_decks:
                            json_user_decks.append([str(card) for card in deck])
                    
                        add_activity_log(USERNAME, PASSWORD, "Double Down",{
                            "Current Stake":stake,
                            "After Stake":stake*2,
                            "Current Balance": read_balance(USERNAME, PASSWORD),
                            "User Decks": json_user_decks,
                            "Dealer Deck": [str(card) for card in dealer_deck.cards]
                        })
                        change_balance(USERNAME, PASSWORD, -stake)
                        stake *= 2

                        new_card = user_decks[deck_index].draw_card()
                        print(f"-> {new_card}\n")
                        if user_decks[deck_index].calculate_true_sum() == 0:
                            user_decks_status[deck_index] = False
                        break
                        
                else:
                    print("Invalid input")
        
        decks_left = False
        if True in user_decks_status:
            decks_left = True
                
        if not decks_left:
            break
            
    print("\n\nROUND OVER!!!\n\n")
    print("--User--")
    for deck_index in range(len(user_decks)):
        print()
        print(f'{("Deck # " + str(deck_index + 1)) * (len(user_decks) > 1)}')
        user_decks[deck_index].print_deck()
    
    print()
    
    print("--House--")
    while dealer_deck.calculate_sum() < 17:
        dealer_deck.draw_card()
    dealer_deck.print_deck()
    
    if len(user_decks) == 1:
        if user_decks[0].calculate_true_sum() > dealer_deck.calculate_true_sum():
            money_return = stake * multiplier
            print(f"You win! +${money_return:,}")
        elif user_decks[0].calculate_true_sum() < dealer_deck.calculate_true_sum()\
             or (user_decks[0].calculate_true_sum() == 0 and dealer_deck.calculate_true_sum() == 0):
            money_return = 0
            print(f"House wins! +${money_return:,}")
        else:
            money_return = stake
            print(f"Tie! +${money_return:,}")
    else:
        money_return = 0
        for deck_index in range(len(user_decks)):
            print(f'{("User Deck #" + str(deck_index + 1) + "  ") * (len(user_decks) > 1)}', end="")
            if user_decks[deck_index].calculate_true_sum() > dealer_deck.calculate_true_sum():
                print("You Win!")
                money_return += (stake / len(user_decks)) * multiplier
            elif user_decks[deck_index].calculate_true_sum() < dealer_deck.calculate_true_sum()\
                or (user_decks[deck_index].calculate_true_sum() == 0 and dealer_deck.calculate_true_sum() == 0):
                print("House Wins!")
                money_return += 0
            else:
                print("Tie!")
                money_return += (stake / len(user_decks))
    
    print(f"Net Profit = ${money_return - stake:,}")
    
    list_user_decks = [deck.cards for deck in user_decks]
    json_user_decks = []
    for deck in list_user_decks:
        json_user_decks.append([str(card) for card in deck])                        
    add_activity_log(USERNAME, PASSWORD, "Game Over",{
        "Stake":stake,
        "Current Balance": read_balance(USERNAME, PASSWORD),
        "Net Profit":money_return - stake,
        "User Decks": json_user_decks,
        "Dealer Deck": [str(card) for card in dealer_deck.cards]
    })
    change_balance(USERNAME,PASSWORD,money_return)

USERNAME = ""
PASSWORD = ""

while True:
    authenticated = authenticate()
    if not authenticated:
        print("AUTHENTICATION FAILED")
    else:
        USERNAME = authenticated[0]
        PASSWORD = authenticated[1]
        break

while True:
    cur_balance = read_balance(USERNAME, PASSWORD)
    print(f"Hi {USERNAME}, you have ${round(cur_balance,2):,}")
    stake = float(input("How much to bet?\n"))

    if stake > cur_balance:
        print("YOU AREN'T THAT RICH")
        continue
    else:
        add_activity_log(USERNAME, PASSWORD, "Game Start",{
            "Stake":stake,
            "Current Balance": read_balance(USERNAME, PASSWORD),
        })
        change_balance(USERNAME, PASSWORD, -stake)
    
    blackjack(stake)
