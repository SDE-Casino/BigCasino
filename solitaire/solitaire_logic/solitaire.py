import requests

# TODO: error handling for HTTP requests

URL = "http://localhost:8000"

value_mapping = {
    'ACE':      1,
    '2':        2,
    '3':        3,
    '4':        4,
    '5':        5,
    '6':        6,
    '7':        7,
    '8':        8,
    '9':        9,
    '10':       10,
    'JACK':     11,
    'QUEEN':    12,
    'KING':     13,
}

class SolitaireGame:
    deck_id = None # deck id from deck adapter
    tableau = None # columns of cards
    foundation = None # goal
    stock = None # draw pile
    talon = None # waste of stock

    def __init__(
            self,
            deck_id=None,
            tableau=None,
            foundation=None,
            stock=None,
            talon=None,
            auto_setup=True
        ):
        if auto_setup:
            data = self.get_deck_from_adapter()
            self.deck_id = data['deck_id']
            self.setup_game()
        else:
            self.deck_id = deck_id
            self.tableau = tableau or []
            self.foundation = foundation or {
                "HEARTS": [],
                "DIAMONDS": [],
                "SPADES": [],
                "CLUBS": [],
            }
            self.stock = stock or []
            self.talon = talon or []

    def _get(self, url):
        """
        Helper for HTTP GET requests
        """
        return requests.get(url)

    def get_deck_from_adapter(self):
        """
        Retrieve a new deck for the game
        """
        response = self._get(f"{URL}/new-deck")

        if response.status_code != 200:
            raise Exception("Failed to retrieve new deck")
        else:
            return response.json()

    def get_cards_from_adapter(self, count):
        """
        Draws card from the deck adapter
        """
        response = self._get(f"{URL}/draw_cards/{self.deck_id}/{count}")

        if response.status_code != 200:
            raise Exception("Failed to draw cards from the deck")
        else:
            return response.json()

    def setup_game(self):
        # draw cards for tableau
        self.tableau = []
        for i in range(7):
            data = self.get_cards_from_adapter(i + 1)
            cards = [(card, False) for card in data['cards']] # False because initially cards are face down
            self.tableau.append([])
            for j in range(len(cards)):
                self.tableau[len(self.tableau) - 1].append(cards[j])
                if j == len(cards) - 1:
                    self.tableau[len(self.tableau) - 1][j] = (self.tableau[len(self.tableau) - 1][j][0], True)

        # draw cards for stock
        data = self.get_cards_from_adapter(24)
        self.stock = data['cards']

        # initialize foundation and talon
        self.foundation = {'HEARTS': [], 'DIAMONDS': [], 'CLUBS': [], 'SPADES': []}
        self.talon = []

    def move_cards_inside_tableau(self, column_from, column_to, n_card=1):
        """
        Move a one card or a group of them inside the tableau
        """
        if len(self.tableau[column_from]) == 0:
            raise Exception("No cards available to move around")

        if n_card <= 0 or n_card > len(self.tableau[column_from]):
            raise Exception("Invalid number of cards to move")

        card_index = len(self.tableau[column_from]) - n_card

        if self.tableau[column_from][card_index][1] == False:
            raise Exception("Cannot move face down cards")

        card = self.tableau[column_from][card_index][0]

        if len(self.tableau[column_to]) == 0:
            if card['value'] != 'KING':
                raise Exception("Only the king can be moved to an empty column")
            else:
                moving_cards = self.tableau[column_from][card_index:]
                self.tableau[column_from] = self.tableau[column_from][:card_index]
                self.tableau[column_to].extend(moving_cards)

                if len(self.tableau[column_from]) > 0:
                    self.tableau[column_from][-1] = (self.tableau[column_from][-1][0], True)
        else:
            if self.check_card_move(self.tableau[column_to][-1][0], card):
                moving_cards = self.tableau[column_from][card_index:]
                self.tableau[column_from] = self.tableau[column_from][:card_index]
                self.tableau[column_to].extend(moving_cards)

                if len(self.tableau[column_from]) > 0:
                    self.tableau[column_from][-1] = (self.tableau[column_from][-1][0], True)
            else:
                raise Exception("Card move not allowed")

    def move_card_to_foundation_from_tableau(self, column_from):
        """
        Move card from tableau to foundation if it is allowed
        """
        if len(self.tableau[column_from]) == 0:
            raise Exception("No cards available in the tableau to be moved into foundation")

        card = self.tableau[column_from][-1][0]
        suit = card['suit']

        if len(self.foundation[suit]) == 0:
            if card['value'] != 'ACE':
                raise Exception("Only ACE can be moved to empty foundation")
            else:
                card = self.tableau[column_from].pop()[0]
                self.foundation[suit].append(card)

                if len(self.tableau[column_from]) > 0:
                    self.tableau[column_from][-1] = (self.tableau[column_from][-1][0], True)
        else:
            target_card = self.foundation[suit][-1]
            if self.check_card_move(target_card, card, is_foundation = True):
                card = self.tableau[column_from].pop()[0]
                self.foundation[suit].append(card)

                if len(self.tableau[column_from]) > 0:
                    self.tableau[column_from][-1] = (self.tableau[column_from][-1][0], True)
            else:
                raise Exception("Card move not allowed")

    def move_card_to_foundation_from_talon(self, foundation_suit):
        """
        Move the upper card from talon to doundation if the move is valid
        """
        if len(self.talon) == 0:
            raise Exception("No cards available in the talon to be moved into foundation")

        card = self.talon[-1]

        if card['suit'] != foundation_suit:
            raise Exception("The card suit does not match the foundation suit")
        elif len(self.foundation[foundation_suit]) == 0:
            if card['value'] != 'ACE':
                raise Exception("Only ACE can be moved to empty foundation")
            else:
                card = self.talon.pop()
                self.foundation[foundation_suit].append(card)
        else:
            target_card = self.foundation[foundation_suit][-1]
            if self.check_card_move(target_card, card, is_foundation = True):
                card = self.talon.pop()
                self.foundation[foundation_suit].append(card)
            else:
                raise Exception("Card move not allowed")

    def move_card_to_tableau_from_talon(self, column_to):
        """
        Move card from talon to tableau if the move is valid
        """
        if len(self.talon) == 0:
            raise Exception("No cards available in the talon to be moved into tableau")

        card = self.talon[-1]

        if len(self.tableau[column_to]) == 0:
            if card['value'] != 'KING':
                raise Exception("Only the king can be moved to an empty column")
            else:
                card = self.talon.pop()
                self.tableau[column_to].append((card, True))
        else:
            target_card = self.tableau[column_to][-1][0]
            if not self.check_card_move(target_card, card):
                raise Exception("Card move not allowed")

            card = self.talon.pop()
            self.tableau[column_to].append((card, True))

    def draw_from_stock(self):
        """
        Draw cards from stock to talon
        """
        if len(self.stock) == 0:
            raise Exception("No cards available in the stock")

        for i in range(3):
            if len(self.stock) == 0:
                break
            card = self.stock.pop()
            self.talon.append(card)

    def reload_stock_from_talon(self):
        """
        Moving all cards from talon back to stock
        """
        if len(self.talon) == 0:
            raise Exception("No cards available in the talon to reload the stock")

        if len(self.stock) != 0:
            raise Exception("Stock can be reloaded only when it is empty")

        while len(self.talon) > 0:
            self.stock.append(self.talon.pop())

    def print_tableau(self):
        for column in self.tableau:
            print(column)

    def check_card_move(self, target_card, moved_card, is_foundation = False):
        """
        When moving a card, I must check if it can be attached to the target card
        """
        target_card_value = target_card['value']
        moved_card_value = moved_card['value']

        target_card_suit = target_card['suit']
        moved_card_suit = moved_card['suit']

        if is_foundation:
            if target_card_suit != moved_card_suit:
                return False
            elif value_mapping[moved_card_value] != value_mapping[target_card_value] + 1:
                return False

            return True
        else:
            if value_mapping[moved_card_value] + 1 != value_mapping[target_card_value]:
                return False
            elif (target_card_suit in ['HEARTS', 'DIAMONDS'] and moved_card_suit in ['HEARTS', 'DIAMONDS']) or \
                (target_card_suit in ['CLUBS', 'SPADES'] and moved_card_suit in ['CLUBS', 'SPADES']):
                return False

            return True

    def check_win(self):
        """
        Check if win conditions are satisfied
        """
        suits = ['HEARTS', 'CLUBS', 'DIAMONDS', 'SPADES']

        for suit in suits:
            if len(self.foundation[suit]) == 0:
                return False

            if self.foundation[suit][-1]['value'] != 'KING':
                return False
            elif len(self.foundation[suit]) != 13:
                raise Exception("Unexpected error in foundation length")

        return True