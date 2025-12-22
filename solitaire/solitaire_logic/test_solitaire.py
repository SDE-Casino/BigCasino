import pytest
from solitaire import SolitaireGame
from unittest.mock import patch, Mock

def new_deck_helper():
    return {
        "success": True,
        "deck_id": "kgw5s4v0d5b5",
        "shuffled": True,
        "remaining": 52
    }

def draws_helper():
    return [
        {"success": True, "deck_id": "kgw5s4v0d5b5", "cards": [{"code": "8C", "value": "8", "suit": "CLUBS"}], "remaining": 51},
        {"success": True, "deck_id": "kgw5s4v0d5b5", "cards": [{"code": "6S", "value": "6", "suit": "SPADES"}, {"code": "2C", "value": "2", "suit": "CLUBS"}], "remaining": 49},
        {"success": True, "deck_id": "kgw5s4v0d5b5", "cards": [{"code": "4D", "value": "4", "suit": "DIAMONDS"}, {"code": "9S", "value": "9", "suit": "SPADES"}, {"code": "6D", "value": "6", "suit": "DIAMONDS"}], "remaining": 46},
        {"success": True, "deck_id": "kgw5s4v0d5b5", "cards": [{"code": "9D", "value": "9", "suit": "DIAMONDS"}, {"code": "QC", "value": "QUEEN", "suit": "CLUBS"}, {"code": "2D", "value": "2", "suit": "DIAMONDS"}, {"code": "AS", "value": "ACE", "suit": "SPADES"}], "remaining": 42},
        {"success": True, "deck_id": "kgw5s4v0d5b5", "cards": [{"code": "KH", "value": "KING", "suit": "HEARTS"}, {"code": "3D", "value": "3", "suit": "DIAMONDS"}, {"code": "5S", "value": "5", "suit": "SPADES"}, {"code": "0S", "value": "10", "suit": "SPADES"}, {"code": "KS", "value": "KING", "suit": "SPADES"}], "remaining": 37},
        {"success": True, "deck_id": "kgw5s4v0d5b5", "cards": [{"code": "5H", "value": "5", "suit": "HEARTS"}, {"code": "3C", "value": "3", "suit": "CLUBS"}, {"code": "8D", "value": "8", "suit": "DIAMONDS"}, {"code": "JC", "value": "JACK", "suit": "CLUBS"}, {"code": "JD", "value": "JACK", "suit": "DIAMONDS"}, {"code": "JH", "value": "JACK", "suit": "HEARTS"}], "remaining": 31},
        {"success": True, "deck_id": "kgw5s4v0d5b5", "cards": [{"code": "KD", "value": "KING", "suit": "DIAMONDS"}, {"code": "7H", "value": "7", "suit": "HEARTS"}, {"code": "JS", "value": "JACK", "suit": "SPADES"}, {"code": "0H", "value": "10", "suit": "HEARTS"}, {"code": "7D", "value": "7", "suit": "DIAMONDS"}, {"code": "0C", "value": "10", "suit": "CLUBS"}, {"code": "8S", "value": "8", "suit": "SPADES"}], "remaining": 24},
        {"success": True, "deck_id": "kgw5s4v0d5b5", "cards": [{"code": "AD", "value": "ACE", "suit": "DIAMONDS"}, {"code": "3H", "value": "3", "suit": "HEARTS"}, {"code": "9C", "value": "9", "suit": "CLUBS"}, {"code": "4H", "value": "4", "suit": "HEARTS"}, {"code": "7S", "value": "7", "suit": "SPADES"}, {"code": "QD", "value": "QUEEN", "suit": "DIAMONDS"}, {"code": "5C", "value": "5", "suit": "CLUBS"}, {"code": "QS", "value": "QUEEN", "suit": "SPADES"}, {"code": "6C", "value": "6", "suit": "CLUBS"}, {"code": "4C", "value": "4", "suit": "CLUBS"}, {"code": "QH", "value": "QUEEN", "suit": "HEARTS"}, {"code": "8H", "value": "8", "suit": "HEARTS"}, {"code": "5D", "value": "5", "suit": "DIAMONDS"}, {"code": "2S", "value": "2", "suit": "SPADES"}, {"code": "4S", "value": "4", "suit": "SPADES"}, {"code": "KC", "value": "KING", "suit": "CLUBS"}, {"code": "3S", "value": "3", "suit": "SPADES"}, {"code": "0D", "value": "10", "suit": "DIAMONDS"}, {"code": "AC", "value": "ACE", "suit": "CLUBS"}, {"code": "7C", "value": "7", "suit": "CLUBS"}, {"code": "6H", "value": "6", "suit": "HEARTS"}, {"code": "2H", "value": "2", "suit": "HEARTS"}, {"code": "AH", "value": "ACE", "suit": "HEARTS"}, {"code": "9H", "value": "9", "suit": "HEARTS"}], "remaining": 0}
    ]

def test_game_init(mocker):
    mock_get_new_deck = mocker.patch('solitaire.SolitaireGame.get_deck_from_adapter')
    mock_get_new_deck.return_value = new_deck_helper()

    draws = draws_helper()

    mock_draw_cards = mocker.patch('solitaire.SolitaireGame.get_cards_from_adapter')
    mock_draw_cards.side_effect = draws

    # Test game init
    new_game = SolitaireGame()

    assert new_game.deck_id == "kgw5s4v0d5b5"
    assert len(new_game.tableau[0]) == 1
    assert len(new_game.tableau[1]) == 2
    assert len(new_game.tableau[2]) == 3
    assert len(new_game.tableau[3]) == 4
    assert len(new_game.tableau[4]) == 5
    assert len(new_game.tableau[5]) == 6
    assert len(new_game.tableau[6]) == 7
    assert len(new_game.stock) == 24
    assert len(new_game.foundation['HEARTS']) == 0
    assert len(new_game.foundation['CLUBS']) == 0
    assert len(new_game.foundation['SPADES']) == 0
    assert len(new_game.foundation['DIAMONDS']) == 0
    assert len(new_game.talon) == 0

def test_move_card_inside_tableau_accept_red_over_black():
    # Setup the game state
    tableau = [
        [({'code': '2H', 'value': '2', 'suit': 'HEARTS'}, False), ({'code': '5H', 'value': '5', 'suit': 'HEARTS'}, True)],
        [({'code': '8C', 'value': '8', 'suit': 'CLUBS'}, False), ({'code': '6S', 'value': '6', 'suit': 'SPADES'}, True)],
        [], [], [], [], [],
    ]
    game = SolitaireGame(deck_id="kgw5s4v0d5b5", tableau=tableau, auto_setup=False)
    game.move_cards_inside_tableau(0,1)

    assert len(game.tableau[0]) == 1
    assert len(game.tableau[1]) == 3
    assert game.tableau[1][-1][0]['code'] == '5H'
    assert game.tableau[0][-1][1] == True

def test_move_card_inside_tableau_accept_black_over_red():
    # Setup the game state
    tableau = [
        [({'code': '2H', 'value': '2', 'suit': 'HEARTS'}, False), ({'code': '5S', 'value': '5', 'suit': 'SPADES'}, True)],
        [({'code': '8C', 'value': '8', 'suit': 'CLUBS'}, False), ({'code': '6D', 'value': '6', 'suit': 'DIAMONDS'}, True)],
        [], [], [], [], [],
    ]
    game = SolitaireGame(deck_id="kgw5s4v0d5b5", tableau=tableau, auto_setup=False)
    game.move_cards_inside_tableau(0,1)

    assert len(game.tableau[0]) == 1
    assert len(game.tableau[1]) == 3
    assert game.tableau[1][-1][0]['code'] == '5S'
    assert game.tableau[0][-1][1] == True

def test_move_card_inside_tableau_accept_move_king_to_empty_column():
    # Setup the game state
    tableau = [
        [({'code': '8C', 'value': '8', 'suit': 'CLUBS'}, False), ({'code': 'KH', 'value': 'KING', 'suit': 'HEARTS'}, True)],
        [], [], [], [], [], [],
    ]
    game = SolitaireGame(deck_id="kgw5s4v0d5b5", tableau=tableau, auto_setup=False)
    game.move_cards_inside_tableau(0,1)

    assert len(game.tableau[0]) == 1
    assert len(game.tableau[1]) == 1
    assert game.tableau[1][-1][0]['code'] == 'KH'
    assert game.tableau[0][-1][1] == True

#5
def test_move_card_inside_tableau_fail_beacuse_empty_starting_column():
    # Setup the game state
    tableau = [
        [],
        [({'code': '8C', 'value': '8', 'suit': 'CLUBS'}, False), ({'code': '6S', 'value': '6', 'suit': 'SPADES'}, True)],
        [], [], [], [], [],
    ]
    game = SolitaireGame(deck_id="kgw5s4v0d5b5", tableau=tableau, auto_setup=False)

    with pytest.raises(Exception, match="No cards available to move around") as exc:
        game.move_cards_inside_tableau(0,1)

def test_move_card_inside_tableau_fail_beacuse_empty_starting_column():
    # Setup the game state
    tableau = [
        [],
        [({'code': '8C', 'value': '8', 'suit': 'CLUBS'}, False), ({'code': '6S', 'value': '6', 'suit': 'SPADES'}, True)],
        [], [], [], [], [],
    ]
    game = SolitaireGame(deck_id="kgw5s4v0d5b5", tableau=tableau, auto_setup=False)

    with pytest.raises(Exception, match="No cards available to move around") as exc:
        game.move_cards_inside_tableau(0,1,3)

def test_move_card_inside_tableau_fail_beacuse_wrong_card_value():
    # Setup the game state
    tableau = [
        [({'code': '4H', 'value': '4', 'suit': 'HEARTS'}, True)],
        [({'code': '8C', 'value': '8', 'suit': 'CLUBS'}, False), ({'code': '6S', 'value': '6', 'suit': 'SPADES'}, True)],
        [], [], [], [], [],
    ]
    game = SolitaireGame(deck_id="kgw5s4v0d5b5", tableau=tableau, auto_setup=False)

    with pytest.raises(Exception, match="Card move not allowed") as exc:
        game.move_cards_inside_tableau(0,1)

def test_move_card_inside_tableau_fail_beacuse_wrong_card_color():
    # Setup the game state
    tableau = [
        [({'code': '5C', 'value': '5', 'suit': 'CLUBS'}, True)],
        [({'code': '8C', 'value': '8', 'suit': 'CLUBS'}, False), ({'code': '6S', 'value': '6', 'suit': 'SPADES'}, True)],
        [], [], [], [], [],
    ]
    game = SolitaireGame(deck_id="kgw5s4v0d5b5", tableau=tableau, auto_setup=False)

    with pytest.raises(Exception, match="Card move not allowed") as exc:
        game.move_cards_inside_tableau(0,1)

def test_move_card_inside_tableau_fail_beacuse_card_to_empty_column():
    # Setup the game state
    tableau = [
        [({'code': '5C', 'value': '5', 'suit': 'CLUBS'}, True)],
        [({'code': '8C', 'value': '8', 'suit': 'CLUBS'}, False), ({'code': '6S', 'value': '6', 'suit': 'SPADES'}, True)],
        [], [], [], [], [],
    ]
    game = SolitaireGame(deck_id="kgw5s4v0d5b5", tableau=tableau, auto_setup=False)

    with pytest.raises(Exception, match="Only the king can be moved to an empty column") as exc:
        game.move_cards_inside_tableau(1,2)

#10
def test_move_cards_inside_tableau_accept_red_over_black():
    # Setup the game state
    tableau = [
        [({'code': '5H', 'value': '5', 'suit': 'HEARTS'}, True), ({'code': '4S', 'value': '4', 'suit': 'SPADES'}, True), ({'code': '3D', 'value': '3', 'suit': 'DIAMONDS'}, True)],
        [({'code': '8C', 'value': '8', 'suit': 'CLUBS'}, False), ({'code': '6S', 'value': '6', 'suit': 'SPADES'}, True)],
        [], [], [], [], [],
    ]
    game = SolitaireGame(deck_id="kgw5s4v0d5b5", tableau=tableau, auto_setup=False)
    game.move_cards_inside_tableau(0,1,3)

    assert len(game.tableau[0]) == 0
    assert len(game.tableau[1]) == 5
    assert game.tableau[1][-1][0]['code'] == '3D'

def test_move_cards_inside_tableau_accept_black_over_red():
    # Setup the game state
    tableau = [
        [({'code': '5H', 'value': '5', 'suit': 'HEARTS'}, False), ({'code': '4S', 'value': '4', 'suit': 'SPADES'}, True), ({'code': '3D', 'value': '3', 'suit': 'DIAMONDS'}, True)],
        [({'code': '8C', 'value': '8', 'suit': 'CLUBS'}, False), ({'code': '5D', 'value': '5', 'suit': 'DIAMONDS'}, True)],
        [], [], [], [], [],
    ]
    game = SolitaireGame(deck_id="kgw5s4v0d5b5", tableau=tableau, auto_setup=False)
    game.move_cards_inside_tableau(0,1,2)

    assert len(game.tableau[0]) == 1
    assert len(game.tableau[1]) == 4
    assert game.tableau[1][-1][0]['code'] == '3D'
    assert game.tableau[0][-1][1] == True

def test_move_cards_inside_tableau_accept_move_king_to_empty_column():
    # Setup the game state
    tableau = [
        [({'code': 'KH', 'value': 'KING', 'suit': 'HEARTS'}, True), ({'code': 'QS', 'value': 'QUEEN', 'suit': 'SPADES'}, True), ({'code': 'JD', 'value': 'JACK', 'suit': 'DIAMONDS'}, True), ({'code': '9C', 'value': '9', 'suit': 'CLUBS'}, True)],
        [], [], [], [], [], [],
    ]
    game = SolitaireGame(deck_id="kgw5s4v0d5b5", tableau=tableau, auto_setup=False)
    game.move_cards_inside_tableau(0,1,4)

    assert len(game.tableau[0]) == 0
    assert len(game.tableau[1]) == 4
    assert game.tableau[1][-1][0]['code'] == '9C'

def test_move_cards_inside_tableau_accept_move_king_to_empty_column():
    # Setup the game state
    tableau = [
        [({'code': '5D', 'value': '5', 'suit': 'DIAMONDS'}, False), ({'code': 'KH', 'value': 'KING', 'suit': 'HEARTS'}, True), ({'code': 'QS', 'value': 'QUEEN', 'suit': 'SPADES'}, True), ({'code': 'JD', 'value': 'JACK', 'suit': 'DIAMONDS'}, True), ({'code': '9C', 'value': '9', 'suit': 'CLUBS'}, True)],
        [], [], [], [], [], [],
    ]
    game = SolitaireGame(deck_id="kgw5s4v0d5b5", tableau=tableau, auto_setup=False)
    game.move_cards_inside_tableau(0,1,4)

    assert len(game.tableau[0]) == 1
    assert len(game.tableau[1]) == 4
    assert game.tableau[1][-1][0]['code'] == '9C'
    assert game.tableau[0][-1][0]['code'] == '5D'
    assert game.tableau[0][-1][1] == True

def test_move_cards_inside_tableau_fail_because_card_faces_down():
    # Setup the game state
    tableau = [
        [({'code': '5D', 'value': '5', 'suit': 'DIAMONDS'}, False), ({'code': 'KH', 'value': 'KING', 'suit': 'HEARTS'}, False), ({'code': 'QS', 'value': 'QUEEN', 'suit': 'SPADES'}, True), ({'code': 'JD', 'value': 'JACK', 'suit': 'DIAMONDS'}, True), ({'code': '9C', 'value': '9', 'suit': 'CLUBS'}, True)],
        [], [], [], [], [], [],
    ]
    game = SolitaireGame(deck_id="kgw5s4v0d5b5", tableau=tableau, auto_setup=False)

    with pytest.raises(Exception, match="Cannot move face down cards") as e:
        game.move_cards_inside_tableau(0,1,4)

def test_move_cards_inside_tableau_fail_because_wrong_index():
    # Setup the game state
    tableau = [
        [({'code': '5D', 'value': '5', 'suit': 'DIAMONDS'}, False), ({'code': 'KH', 'value': 'KING', 'suit': 'HEARTS'}, False), ({'code': 'QS', 'value': 'QUEEN', 'suit': 'SPADES'}, True), ({'code': 'JD', 'value': 'JACK', 'suit': 'DIAMONDS'}, True), ({'code': '9C', 'value': '9', 'suit': 'CLUBS'}, True)],
        [], [], [], [], [], [],
    ]
    game = SolitaireGame(deck_id="kgw5s4v0d5b5", tableau=tableau, auto_setup=False)

    with pytest.raises(Exception, match="Invalid number of cards to move") as e:
        game.move_cards_inside_tableau(0,1,8)

def test_move_cards_inside_tableau_fail_because_negative_index():
    # Setup the game state
    tableau = [
        [({'code': '5D', 'value': '5', 'suit': 'DIAMONDS'}, False), ({'code': 'KH', 'value': 'KING', 'suit': 'HEARTS'}, False), ({'code': 'QS', 'value': 'QUEEN', 'suit': 'SPADES'}, True), ({'code': 'JD', 'value': 'JACK', 'suit': 'DIAMONDS'}, True), ({'code': '9C', 'value': '9', 'suit': 'CLUBS'}, True)],
        [], [], [], [], [], [],
    ]
    game = SolitaireGame(deck_id="kgw5s4v0d5b5", tableau=tableau, auto_setup=False)

    with pytest.raises(Exception, match="Invalid number of cards to move") as e:
        game.move_cards_inside_tableau(0,1,-2)

def test_move_cards_inside_tableau_fail_beacuse_wrong_card_value():
    # Setup the game state
    tableau = [
        [({'code': '5H', 'value': '5', 'suit': 'HEARTS'}, True), ({'code': '4S', 'value': '4', 'suit': 'SPADES'}, True), ({'code': '3D', 'value': '3', 'suit': 'DIAMONDS'}, True)],
        [({'code': '8C', 'value': '8', 'suit': 'CLUBS'}, True), ({'code': '5D', 'value': '5', 'suit': 'DIAMONDS'}, True)],
        [], [], [], [], [],
    ]
    game = SolitaireGame(deck_id="kgw5s4v0d5b5", tableau=tableau, auto_setup=False)

    with pytest.raises(Exception, match="Card move not allowed") as exc:
        game.move_cards_inside_tableau(0,1,3)

def test_move_cards_inside_tableau_fail_beacuse_wrong_card_color():
    # Setup the game state
    tableau = [
        [({'code': '5H', 'value': '5', 'suit': 'HEARTS'}, True), ({'code': '4S', 'value': '4', 'suit': 'SPADES'}, True), ({'code': '3D', 'value': '3', 'suit': 'DIAMONDS'}, True)],
        [({'code': '8C', 'value': '8', 'suit': 'CLUBS'}, True), ({'code': '5C', 'value': '5', 'suit': 'CLUBS'}, True)],
        [], [], [], [], [],
    ]
    game = SolitaireGame(deck_id="kgw5s4v0d5b5", tableau=tableau, auto_setup=False)

    with pytest.raises(Exception, match="Card move not allowed") as exc:
        game.move_cards_inside_tableau(0,1,2)

#15
def test_move_cards_inside_tableau_fail_beacuse_card_to_empty_column():
    # Setup the game state
    tableau = [
        [({'code': 'KH', 'value': 'KING', 'suit': 'HEARTS'}, True), ({'code': 'QS', 'value': 'QUEEN', 'suit': 'SPADES'}, True), {'code': 'JD', 'value': 'JACK', 'suit': 'DIAMONDS'}, {'code': '9C', 'value': '9', 'suit': 'CLUBS'}],
        [], [], [], [], [], [],
    ]
    game = SolitaireGame(deck_id="kgw5s4v0d5b5", tableau=tableau, auto_setup=False)

    with pytest.raises(Exception, match="Only the king can be moved to an empty column") as exc:
        game.move_cards_inside_tableau(0,1,3)

def test_move_first_card_to_foundation_accept():
    tableau = [
        [({'code': '2S', 'value': '2', 'suit': 'SPADES'}, False),({'code': 'AD', 'value': 'ACE', 'suit': 'DIAMONDS'}, True)],
        [], [], [], [], [], []
    ]
    game = SolitaireGame(deck_id="kgw5s4v0d5b5", tableau=tableau, auto_setup=False)

    game.move_card_to_foundation_from_tableau(0)

    assert len(game.tableau[0]) == 1
    assert len(game.foundation['DIAMONDS']) == 1
    assert game.foundation['DIAMONDS'][-1]['code'] == 'AD'
    assert game.tableau[0][-1][1] == True

def test_move_first_card_to_foundation_fail_because_its_not_ace():
    tableau = [
        [({'code': '4D', 'value': '4', 'suit': 'DIAMONDS'}, True)],
        [], [], [], [], [], []
    ]
    game = SolitaireGame(deck_id="kgw5s4v0d5b5", tableau=tableau, auto_setup=False)

    with pytest.raises(Exception, match="Only ACE can be moved to empty foundation") as e:
        game.move_card_to_foundation_from_tableau(0)

def test_move_first_card_to_foundation_fail_because_empty_column_from():
    tableau = [
        [], [], [], [], [], [], []
    ]
    game = SolitaireGame(deck_id="kgw5s4v0d5b5", tableau=tableau, auto_setup=False)

    with pytest.raises(Exception, match="No cards available in the tableau to be moved into foundation") as e:
        game.move_card_to_foundation_from_tableau(0)

def test_move_card_to_foundation_accept():
    tableau = [[({'code': '2S', 'value': '2', 'suit': 'SPADES'}, False), ({'code': '4D', 'value': '4', 'suit': 'DIAMONDS'}, True)], [], [], [], [], [], []]
    foundation = {
        'DIAMONDS': [{'code': 'AD', 'value': 'ACE', 'suit': 'DIAMONDS'}, {'code': '2D', 'value': '2', 'suit': 'DIAMONDS'}, {'code': '3D', 'value': '3', 'suit': 'DIAMONDS'}],
        'HEARTS': [],
        'CLUBS': [],
        'SPADES': []
    }
    game = SolitaireGame(deck_id="kgw5s4v0d5b5", tableau=tableau, foundation=foundation, auto_setup=False)
    game.move_card_to_foundation_from_tableau(0)

    assert len(game.tableau[0]) == 1
    assert len(game.foundation['DIAMONDS']) == 4
    assert game.tableau[0][-1][1] == True

#20
def test_move_card_to_foundation_fail_because_wrong_value():
    tableau = [[({'code': '4D', 'value': '4', 'suit': 'DIAMONDS'}, True)], [], [], [], [], [], []]
    foundation = {'DIAMONDS': [{'code': 'AD', 'value': 'ACE', 'suit': 'DIAMONDS'}], 'HEARTS': [], 'CLUBS': [], 'SPADES': []}
    game = SolitaireGame(deck_id="kgw5s4v0d5b5", tableau=tableau, foundation=foundation, auto_setup=False)

    with pytest.raises(Exception, match="Card move not allowed") as e:
        game.move_card_to_foundation_from_tableau(0)

def test_move_card_to_foundation_from_tablon_accept():
    talon = [{'code': '3H', 'value': '3', 'suit': 'HEARTS'}]
    foundation = {
        'HEARTS': [{'code': 'AD', 'value': 'ACE', 'suit': 'HEARTS'}, {'code': '2H', 'value': '2', 'suit': 'HEARTS'}],
        'DIAMONDS': [],
        'CLUBS': [],
        'SPADES': []
    }
    game = SolitaireGame(deck_id="kgw5s4v0d5b5", talon=talon, foundation=foundation, auto_setup=False)

    game.move_card_to_foundation_from_talon(game.talon[-1]['suit'])

    assert len(game.talon) == 0
    assert len(game.foundation['HEARTS']) == 3
    assert game,foundation['HEARTS'][-1]['code'] == '3H'

def test_move_card_to_foundation_from_talon_accept_ace():
    talon = [{'code': 'AH', 'value': 'ACE', 'suit': 'HEARTS'}]
    foundation = {
        'HEARTS': [],
        'DIAMONDS': [],
        'CLUBS': [],
        'SPADES': []
    }
    game = SolitaireGame(deck_id="kgw5s4v0d5b5", talon=talon, foundation=foundation, auto_setup=False)

    game.move_card_to_foundation_from_talon(game.talon[-1]['suit'])

    assert len(game.talon) == 0
    assert len(game.foundation['HEARTS']) == 1
    assert game.foundation['HEARTS'][-1]['code'] == 'AH'

def test_move_card_to_foundation_from_talon_fail_becaise_empty_talon():
    talon = []
    foundation = {
        'HEARTS': [],
        'DIAMONDS': [],
        'CLUBS': [],
        'SPADES': []
    }
    game = SolitaireGame(deck_id="kgw5s4v0d5b5", talon=talon, foundation=foundation, auto_setup=False)

    with pytest.raises(Exception, match="No cards available in the talon to be moved into foundation") as e:
        game.move_card_to_foundation_from_talon('HEARTS')

def test_move_card_to_foundation_from_talon_fail_becaise_wrong_value():
    talon = [{'code': '4H', 'value': '4', 'suit': 'HEARTS'}]
    foundation = {
        'HEARTS': [{'code': 'AD', 'value': 'ACE', 'suit': 'HEARTS'}],
        'DIAMONDS': [],
        'CLUBS': [],
        'SPADES': []
    }
    game = SolitaireGame(deck_id="kgw5s4v0d5b5", talon=talon, foundation=foundation, auto_setup=False)

    with pytest.raises(Exception, match="Card move not allowed") as e:
        game.move_card_to_foundation_from_talon('HEARTS')

#25
def test_move_card_to_foundation_from_talon_fail_becaise_wrong_suit():
    talon = [{'code': '3H', 'value': '3', 'suit': 'HEARTS'}]
    foundation = {
        'HEARTS': [{'code': 'AD', 'value': 'ACE', 'suit': 'HEARTS'}, {'code': '2H', 'value': '2', 'suit': 'HEARTS'}],
        'DIAMONDS': [],
        'CLUBS': [],
        'SPADES': []
    }
    game = SolitaireGame(deck_id="kgw5s4v0d5b5", talon=talon, foundation=foundation, auto_setup=False)

    with pytest.raises(Exception, match="The card suit does not match the foundation suit") as e:
        game.move_card_to_foundation_from_talon('DIAMONDS')

def test_move_card_to_tableau_from_talon_accept():
    talon = [{'code': '5H', 'value': '5', 'suit': 'HEARTS'}]
    tableau = [
        [({'code': '6C', 'value': '6', 'suit': 'CLUBS'}, True)],
        [], [], [], [], [], []
    ]
    game = SolitaireGame(deck_id="kgw5s4v0d5b5", talon=talon, tableau=tableau, auto_setup=False)

    game.move_card_to_tableau_from_talon(0)

    assert len(game.talon) == 0
    assert len(game.tableau[0]) == 2
    assert game.tableau[0][-1][0]['code'] == '5H'
    assert game.tableau[0][-1][1] == True

def test_move_card_to_tableau_from_talon_accept_king():
    talon = [{'code': 'KH', 'value': 'KING', 'suit': 'HEARTS'}]
    tableau = [
        [], [], [], [], [], [], []
    ]
    game = SolitaireGame(deck_id="kgw5s4v0d5b5", talon=talon, tableau=tableau, auto_setup=False)

    game.move_card_to_tableau_from_talon(0)

    assert len(game.talon) == 0
    assert len(game.tableau[0]) == 1
    assert game.tableau[0][-1][0]['code'] == 'KH'
    assert game.tableau[0][-1][1] == True

def test_move_card_to_tableau_from_talon_fail_because_empty_talon():
    talon = []
    tableau = [
        [{'code': '6C', 'value': '6', 'suit': 'CLUBS'}],
        [], [], [], [], [], []
    ]
    game = SolitaireGame(deck_id="kgw5s4v0d5b5", talon=talon, tableau=tableau, auto_setup=False)

    with pytest.raises(Exception, match="No cards available in the talon to be moved into tableau") as e:
        game.move_card_to_tableau_from_talon(0)

def test_move_card_to_tableau_from_talon_fail_because_wrong_color_black():
    talon = [{'code': '5S', 'value': '5', 'suit': 'SPADES'}]
    tableau = [
        [({'code': '6C', 'value': '6', 'suit': 'CLUBS'}, True)],
        [], [], [], [], [], []
    ]
    game = SolitaireGame(deck_id="kgw5s4v0d5b5", talon=talon, tableau=tableau, auto_setup=False)

    with pytest.raises(Exception, match="Card move not allowed") as e:
        game.move_card_to_tableau_from_talon(0)

#30
def test_move_card_to_tableau_from_talon_fail_because_wrong_color_red():
    talon = [{'code': '5H', 'value': '5', 'suit': 'HEARTS'}]
    tableau = [
        [({'code': '6D', 'value': '6', 'suit': 'DIAMONDS'}, True)],
        [], [], [], [], [], []
    ]
    game = SolitaireGame(deck_id="kgw5s4v0d5b5", talon=talon, tableau=tableau, auto_setup=False)

    with pytest.raises(Exception, match="Card move not allowed") as e:
        game.move_card_to_tableau_from_talon(0)

def test_move_card_to_tableau_from_talon_fail_because_wrong_value():
    talon = [{'code': '9C', 'value': '9', 'suit': 'CLUBS'}]
    tableau = [
        [({'code': '6D', 'value': '6', 'suit': 'DIAMONDS'}, True)],
        [], [], [], [], [], []
    ]
    game = SolitaireGame(deck_id="kgw5s4v0d5b5", talon=talon, tableau=tableau, auto_setup=False)

    with pytest.raises(Exception, match="Card move not allowed") as e:
        game.move_card_to_tableau_from_talon(0)

def test_move_card_to_tableau_from_talon_fail_because_wrong_value_to_empty_column():
    talon = [{'code': '9C', 'value': '9', 'suit': 'CLUBS'}]
    tableau = [
        [], [], [], [], [], [], []
    ]
    game = SolitaireGame(deck_id="kgw5s4v0d5b5", talon=talon, tableau=tableau, auto_setup=False)

    with pytest.raises(Exception, match="Only the king can be moved to an empty column") as e:
        game.move_card_to_tableau_from_talon(0)

def test_draw_from_stock_accept_empty_talon():
    stock = [
        {"code": "AD", "value": "ACE", "suit": "DIAMONDS"},
        {"code": "3H", "value": "3", "suit": "HEARTS"},
        {"code": "9C", "value": "9", "suit": "CLUBS"},
        {"code": "4H", "value": "4", "suit": "HEARTS"},
        {"code": "7S", "value": "7", "suit": "SPADES"}
    ]
    game = SolitaireGame(deck_id="kgw5s4v0d5b5", stock=stock, auto_setup=False)

    game.draw_from_stock()

    assert len(game.stock) == 2
    assert len(game.talon) == 3
    assert game.talon[-1]['code'] == '9C'
    assert game.talon[-2]['code'] == '4H'
    assert game.talon[-3]['code'] == '7S'

def test_draw_from_stock_accept_normal_talon():
    talon = [
        {"code": "3S", "value": "3", "suit": "SPADES"},
        {"code": "0D", "value": "10", "suit": "DIAMONDS"},
        {"code": "AC", "value": "ACE", "suit": "CLUBS"}
    ]
    stock = [
        {"code": "AD", "value": "ACE", "suit": "DIAMONDS"},
        {"code": "3H", "value": "3", "suit": "HEARTS"},
        {"code": "9C", "value": "9", "suit": "CLUBS"},
        {"code": "4H", "value": "4", "suit": "HEARTS"},
        {"code": "7S", "value": "7", "suit": "SPADES"}
    ]
    game = SolitaireGame(deck_id="kgw5s4v0d5b5", stock=stock, talon=talon, auto_setup=False)

    game.draw_from_stock()

    assert len(game.stock) == 2
    assert len(game.talon) == 6
    assert game.talon[-1]['code'] == '9C'
    assert game.talon[-2]['code'] == '4H'
    assert game.talon[-3]['code'] == '7S'

# 35
def test_draw_from_stock_accept_two_cards():
    talon = [
        {"code": "3S", "value": "3", "suit": "SPADES"},
        {"code": "0D", "value": "10", "suit": "DIAMONDS"},
        {"code": "AC", "value": "ACE", "suit": "CLUBS"}
    ]
    stock = [
        {"code": "4H", "value": "4", "suit": "HEARTS"},
        {"code": "7S", "value": "7", "suit": "SPADES"}
    ]
    game = SolitaireGame(deck_id="kgw5s4v0d5b5", stock=stock, talon=talon, auto_setup=False)

    game.draw_from_stock()

    assert len(game.stock) == 0
    assert len(game.talon) == 5
    assert game.talon[-1]['code'] == '4H'
    assert game.talon[-2]['code'] == '7S'
    assert game.talon[-3]['code'] == 'AC'

def test_draw_from_stock_accept_one_card():
    talon = [
        {"code": "3S", "value": "3", "suit": "SPADES"},
        {"code": "0D", "value": "10", "suit": "DIAMONDS"},
        {"code": "AC", "value": "ACE", "suit": "CLUBS"}
    ]
    stock = [
        {"code": "7S", "value": "7", "suit": "SPADES"}
    ]
    game = SolitaireGame(deck_id="kgw5s4v0d5b5", stock=stock, talon=talon, auto_setup=False)

    game.draw_from_stock()

    assert len(game.stock) == 0
    assert len(game.talon) == 4
    assert game.talon[-1]['code'] == '7S'
    assert game.talon[-2]['code'] == 'AC'
    assert game.talon[-3]['code'] == '0D'

def test_draw_from_stock_fail_because_empty_stock():
    talon = [
        {"code": "3S", "value": "3", "suit": "SPADES"},
        {"code": "0D", "value": "10", "suit": "DIAMONDS"},
        {"code": "AC", "value": "ACE", "suit": "CLUBS"}
    ]
    game = SolitaireGame(deck_id="kgw5s4v0d5b5", talon=talon, auto_setup=False)

    with pytest.raises(Exception, match="No cards available in the stock") as e:
        game.draw_from_stock()

def test_reload_stock_from_talon_accept():
    talon = [
        {"code": "3S", "value": "3", "suit": "SPADES"},
        {"code": "0D", "value": "10", "suit": "DIAMONDS"},
        {"code": "AC", "value": "ACE", "suit": "CLUBS"}
    ]
    game = SolitaireGame(deck_id="kgw5s4v0d5b5", talon=talon, auto_setup=False)

    game.reload_stock_from_talon()

    assert len(game.stock) == 3
    assert len(game.talon) == 0
    assert game.stock[0]['code'] == 'AC'
    assert game.stock[1]['code'] == '0D'
    assert game.stock[2]['code'] == '3S'

def test_reload_stock_from_talon_fail_because_empty_talon():
    game = SolitaireGame(deck_id="kgw5s4v0d5b5", auto_setup=False)

    with pytest.raises(Exception, match="No cards available in the talon to reload the stock") as e:
        game.reload_stock_from_talon()

# 40
def test_reload_stock_from_talon_fail_because_not_empty_stock():
    talon = [
        {"code": "3S", "value": "3", "suit": "SPADES"},
        {"code": "0D", "value": "10", "suit": "DIAMONDS"},
        {"code": "AC", "value": "ACE", "suit": "CLUBS"}
    ]
    stock = [
        {"code": "4H", "value": "4", "suit": "HEARTS"},
        {"code": "7S", "value": "7", "suit": "SPADES"}
    ]
    game = SolitaireGame(deck_id="kgw5s4v0d5b5", stock=stock, talon=talon, auto_setup=False)

    with pytest.raises(Exception, match="Stock can be reloaded only when it is empty") as e:
        game.reload_stock_from_talon()

def test_check_card_move_not_foundation_accept():
    card1 = {"code": "3S", "value": "3", "suit": "SPADES"}
    card2 = {"code": "2D", "value": "2", "suit": "DIAMONDS"}

    game = SolitaireGame(deck_id="kgw5s4v0d5b5", auto_setup=False)

    assert game.check_card_move(card1, card2)

def test_check_card_move_not_foundation_fail_because_wrong_value():
    card1 = {"code": "8S", "value": "8", "suit": "SPADES"}
    card2 = {"code": "2D", "value": "2", "suit": "DIAMONDS"}

    game = SolitaireGame(deck_id="kgw5s4v0d5b5", auto_setup=False)

    assert game.check_card_move(card1, card2) == False

def test_check_card_move_not_foundation_fail_because_same_color_red():
    card1 = {"code": "3H", "value": "3", "suit": "HEARTS"}
    card2 = {"code": "2D", "value": "2", "suit": "DIAMONDS"}

    game = SolitaireGame(deck_id="kgw5s4v0d5b5", auto_setup=False)

    assert game.check_card_move(card1, card2) == False

def test_check_card_move_not_foundation_fail_because_same_color_black():
    card1 = {"code": "3C", "value": "3", "suit": "CLUBS"}
    card2 = {"code": "2S", "value": "2", "suit": "SPADES"}

    game = SolitaireGame(deck_id="kgw5s4v0d5b5", auto_setup=False)

    assert game.check_card_move(card1, card2) == False

#45
def test_check_card_move_foundation_accept():
    card1 = {"code": "2D", "value": "2", "suit": "DIAMONDS"}
    card2 = {"code": "3D", "value": "3", "suit": "DIAMONDS"}

    game = SolitaireGame(deck_id="kgw5s4v0d5b5", auto_setup=False)

    assert game.check_card_move(card1, card2, is_foundation=True)

def test_check_card_move_foundation_fail_because_wrong_value():
    card1 = {"code": "2D", "value": "2", "suit": "DIAMONDS"}
    card2 = {"code": "6D", "value": "6", "suit": "DIAMONDS"}

    game = SolitaireGame(deck_id="kgw5s4v0d5b5", auto_setup=False)

    assert game.check_card_move(card1, card2, is_foundation=True) == False

def test_check_card_move_foundation_fail_because_wrong_suit():
    card1 = {"code": "2D", "value": "2", "suit": "DIAMONDS"}
    card2 = {"code": "3C", "value": "3", "suit": "CLUBS"}

    game = SolitaireGame(deck_id="kgw5s4v0d5b5", auto_setup=False)

    assert game.check_card_move(card1, card2, is_foundation=True) == False

def test_check_win_accept():
    foundation = {
        'HEARTS': [{'code': 'AH', 'value': 'ACE', 'suit': 'HEARTS'},
                   {'code': '2H', 'value': '2', 'suit': 'HEARTS'},
                   {'code': '3H', 'value': '3', 'suit': 'HEARTS'},
                   {'code': '4H', 'value': '4', 'suit': 'HEARTS'},
                   {'code': '5H', 'value': '5', 'suit': 'HEARTS'},
                   {'code': '6H', 'value': '6', 'suit': 'HEARTS'},
                   {'code': '7H', 'value': '7', 'suit': 'HEARTS'},
                   {'code': '8H', 'value': '8', 'suit': 'HEARTS'},
                   {'code': '9H', 'value': '9', 'suit': 'HEARTS'},
                   {'code': '0H', 'value': '10', 'suit': 'HEARTS'},
                   {'code': 'JH', 'value': 'JACK', 'suit': 'HEARTS'},
                   {'code': 'QH', 'value': 'QUEEN', 'suit': 'HEARTS'},
                   {'code': 'KH', 'value': 'KING', 'suit': 'HEARTS'}],
        'DIAMONDS': [{'code': 'AD', 'value': 'ACE', 'suit': 'DIAMONDS'},
                   {'code': '2D', 'value': '2', 'suit': 'DIAMONDS'},
                   {'code': '3D', 'value': '3', 'suit': 'DIAMONDS'},
                   {'code': '4D', 'value': '4', 'suit': 'DIAMONDS'},
                   {'code': '5D', 'value': '5', 'suit': 'DIAMONDS'},
                   {'code': '6D', 'value': '6', 'suit': 'DIAMONDS'},
                   {'code': '7D', 'value': '7', 'suit': 'DIAMONDS'},
                   {'code': '8D', 'value': '8', 'suit': 'DIAMONDS'},
                   {'code': '9D', 'value': '9', 'suit': 'DIAMONDS'},
                   {'code': '0D', 'value': '10', 'suit': 'DIAMONDS'},
                   {'code': 'JD', 'value': 'JACK', 'suit': 'DIAMONDS'},
                   {'code': 'QD', 'value': 'QUEEN', 'suit': 'DIAMONDS'},
                   {'code': 'KD', 'value': 'KING', 'suit': 'DIAMONDS'}],
        'CLUBS': [{'code': 'AC', 'value': 'ACE', 'suit': 'CLUBS'},
                   {'code': '2C', 'value': '2', 'suit': 'CLUBS'},
                   {'code': '3C', 'value': '3', 'suit': 'CLUBS'},
                   {'code': '4C', 'value': '4', 'suit': 'CLUBS'},
                   {'code': '5C', 'value': '5', 'suit': 'CLUBS'},
                   {'code': '6C', 'value': '6', 'suit': 'CLUBS'},
                   {'code': '7C', 'value': '7', 'suit': 'CLUBS'},
                   {'code': '8C', 'value': '8', 'suit': 'CLUBS'},
                   {'code': '9C', 'value': '9', 'suit': 'CLUBS'},
                   {'code': '0C', 'value': '10', 'suit': 'CLUBS'},
                   {'code': 'JC', 'value': 'JACK', 'suit': 'CLUBS'},
                   {'code': 'QC', 'value': 'QUEEN', 'suit': 'CLUBS'},
                   {'code': 'KC', 'value': 'KING', 'suit': 'CLUBS'}],
        'SPADES': [{'code': 'AS', 'value': 'ACE', 'suit': 'SPADES'},
                   {'code': '2S', 'value': '2', 'suit': 'SPADES'},
                   {'code': '3S', 'value': '3', 'suit': 'SPADES'},
                   {'code': '4S', 'value': '4', 'suit': 'SPADES'},
                   {'code': '5S', 'value': '5', 'suit': 'SPADES'},
                   {'code': '6S', 'value': '6', 'suit': 'SPADES'},
                   {'code': '7S', 'value': '7', 'suit': 'SPADES'},
                   {'code': '8S', 'value': '8', 'suit': 'SPADES'},
                   {'code': '9S', 'value': '9', 'suit': 'SPADES'},
                   {'code': '0S', 'value': '10', 'suit': 'SPADES'},
                   {'code': 'JS', 'value': 'JACK', 'suit': 'SPADES'},
                   {'code': 'QS', 'value': 'QUEEN', 'suit': 'SPADES'},
                   {'code': 'KS', 'value': 'KING', 'suit': 'SPADES'}]
    }

    game = SolitaireGame(deck_id="kgw5s4v0d5b5", foundation=foundation, auto_setup=False)

    assert game.check_win()

def test_check_win_fail_because_wrong_foundation_size():
    foundation = {
        'HEARTS': [{'code': 'AH', 'value': 'ACE', 'suit': 'HEARTS'},
                   {'code': '2H', 'value': '2', 'suit': 'HEARTS'},
                   {'code': '3H', 'value': '3', 'suit': 'HEARTS'},
                   {'code': '4H', 'value': '4', 'suit': 'HEARTS'},
                   {'code': '5H', 'value': '5', 'suit': 'HEARTS'},
                   {'code': '6H', 'value': '6', 'suit': 'HEARTS'},
                   {'code': '8H', 'value': '8', 'suit': 'HEARTS'},
                   {'code': '9H', 'value': '9', 'suit': 'HEARTS'},
                   {'code': '0H', 'value': '10', 'suit': 'HEARTS'},
                   {'code': 'JH', 'value': 'JACK', 'suit': 'HEARTS'},
                   {'code': 'QH', 'value': 'QUEEN', 'suit': 'HEARTS'},
                   {'code': 'KH', 'value': 'KING', 'suit': 'HEARTS'}],
        'DIAMONDS': [{'code': 'AD', 'value': 'ACE', 'suit': 'DIAMONDS'},
                   {'code': '2D', 'value': '2', 'suit': 'DIAMONDS'},
                   {'code': '3D', 'value': '3', 'suit': 'DIAMONDS'},
                   {'code': '4D', 'value': '4', 'suit': 'DIAMONDS'},
                   {'code': '5D', 'value': '5', 'suit': 'DIAMONDS'},
                   {'code': '6D', 'value': '6', 'suit': 'DIAMONDS'},
                   {'code': '7D', 'value': '7', 'suit': 'DIAMONDS'},
                   {'code': '8D', 'value': '8', 'suit': 'DIAMONDS'},
                   {'code': '9D', 'value': '9', 'suit': 'DIAMONDS'},
                   {'code': '0D', 'value': '10', 'suit': 'DIAMONDS'},
                   {'code': 'JD', 'value': 'JACK', 'suit': 'DIAMONDS'},
                   {'code': 'QD', 'value': 'QUEEN', 'suit': 'DIAMONDS'},
                   {'code': 'KD', 'value': 'KING', 'suit': 'DIAMONDS'}],
        'CLUBS': [{'code': 'AC', 'value': 'ACE', 'suit': 'CLUBS'},
                   {'code': '2C', 'value': '2', 'suit': 'CLUBS'},
                   {'code': '3C', 'value': '3', 'suit': 'CLUBS'},
                   {'code': '4C', 'value': '4', 'suit': 'CLUBS'},
                   {'code': '5C', 'value': '5', 'suit': 'CLUBS'},
                   {'code': '6C', 'value': '6', 'suit': 'CLUBS'},
                   {'code': '7C', 'value': '7', 'suit': 'CLUBS'},
                   {'code': '8C', 'value': '8', 'suit': 'CLUBS'},
                   {'code': '9C', 'value': '9', 'suit': 'CLUBS'},
                   {'code': '0C', 'value': '10', 'suit': 'CLUBS'},
                   {'code': 'JC', 'value': 'JACK', 'suit': 'CLUBS'},
                   {'code': 'QC', 'value': 'QUEEN', 'suit': 'CLUBS'},
                   {'code': 'KC', 'value': 'KING', 'suit': 'CLUBS'}],
        'SPADES': [{'code': 'AS', 'value': 'ACE', 'suit': 'SPADES'},
                   {'code': '2S', 'value': '2', 'suit': 'SPADES'},
                   {'code': '3S', 'value': '3', 'suit': 'SPADES'},
                   {'code': '4S', 'value': '4', 'suit': 'SPADES'},
                   {'code': '5S', 'value': '5', 'suit': 'SPADES'},
                   {'code': '6S', 'value': '6', 'suit': 'SPADES'},
                   {'code': '7S', 'value': '7', 'suit': 'SPADES'},
                   {'code': '8S', 'value': '8', 'suit': 'SPADES'},
                   {'code': '9S', 'value': '9', 'suit': 'SPADES'},
                   {'code': '0S', 'value': '10', 'suit': 'SPADES'},
                   {'code': 'JS', 'value': 'JACK', 'suit': 'SPADES'},
                   {'code': 'QS', 'value': 'QUEEN', 'suit': 'SPADES'},
                   {'code': 'KS', 'value': 'KING', 'suit': 'SPADES'}]
    }
    game = SolitaireGame(deck_id="kgw5s4v0d5b5", foundation=foundation, auto_setup=False)

    with pytest.raises(Exception, match="Unexpected error in foundation length") as e:
        game.check_win()

def test_check_win_empty_foundation():
    game = SolitaireGame(deck_id="kgw5s4v0d5b5", auto_setup=False)

    assert game.check_win() == False

def test_check_win_not_complete_foundation():
    foundation = {
        'HEARTS': [{'code': 'AH', 'value': 'ACE', 'suit': 'HEARTS'},
                   {'code': '2H', 'value': '2', 'suit': 'HEARTS'},
                   {'code': '3H', 'value': '3', 'suit': 'HEARTS'},
                   {'code': '4H', 'value': '4', 'suit': 'HEARTS'},
                   {'code': '5H', 'value': '5', 'suit': 'HEARTS'},
                   {'code': '6H', 'value': '6', 'suit': 'HEARTS'},
                   {'code': '7H', 'value': '7', 'suit': 'HEARTS'},
                   {'code': '8H', 'value': '8', 'suit': 'HEARTS'},
                   {'code': '9H', 'value': '9', 'suit': 'HEARTS'}],
        'DIAMONDS': [{'code': 'AD', 'value': 'ACE', 'suit': 'DIAMONDS'},
                   {'code': '2D', 'value': '2', 'suit': 'DIAMONDS'},
                   {'code': '3D', 'value': '3', 'suit': 'DIAMONDS'},
                   {'code': '4D', 'value': '4', 'suit': 'DIAMONDS'},],
        'CLUBS': [{'code': 'AC', 'value': 'ACE', 'suit': 'CLUBS'},
                   {'code': '2C', 'value': '2', 'suit': 'CLUBS'},
                   {'code': '3C', 'value': '3', 'suit': 'CLUBS'},
                   {'code': '4C', 'value': '4', 'suit': 'CLUBS'},
                   {'code': '5C', 'value': '5', 'suit': 'CLUBS'},
                   {'code': '6C', 'value': '6', 'suit': 'CLUBS'},
                   {'code': '7C', 'value': '7', 'suit': 'CLUBS'},],
        'SPADES': [{'code': 'AS', 'value': 'ACE', 'suit': 'SPADES'},
                   {'code': '2S', 'value': '2', 'suit': 'SPADES'},
                   {'code': '3S', 'value': '3', 'suit': 'SPADES'},
                   {'code': '4S', 'value': '4', 'suit': 'SPADES'},
                   {'code': '5S', 'value': '5', 'suit': 'SPADES'},
                   {'code': '6S', 'value': '6', 'suit': 'SPADES'},
                   {'code': '7S', 'value': '7', 'suit': 'SPADES'},
                   {'code': '8S', 'value': '8', 'suit': 'SPADES'},]
    }

    game = SolitaireGame(deck_id="kgw5s4v0d5b5", foundation=foundation, auto_setup=False)

    assert game.check_win() == False