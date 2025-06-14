import random

class Card:
    """Represents a single playing card with a value and suit."""

    def __init__(self, value, suit):
        self.value = value
        self.suit = suit

    def numeric_value(self):
        """Returns the numeric value of a card, converting face cards appropriately."""
        face_cards = {'J': 11, 'Q': 12, 'K': 13, 'Ace': 14}
        return int(self.value) if self.value.isdigit() else face_cards[self.value]

    def __str__(self):
        return f"{self.value} of {self.suit}"


class Player:
    """Represents the player, tracking health, current weapon, and defeated monsters."""

    def __init__(self):
        self.health = 20
        self.weapon = None
        self.slain_monsters = []

    def equip_weapon(self, new_weapon, discard_pile):
        """Equips a new weapon, discarding the old one and any slain monsters."""
        if self.weapon:
            discard_pile.extend([self.weapon] + self.slain_monsters)
        self.weapon = new_weapon
        self.slain_monsters = []
        print(f"\nYou equip the {new_weapon}.")

    def can_use_weapon_on(self, monster_card):
        """Returns True if the weapon can legally defeat the given monster."""
        if not self.weapon:
            return False
        if not self.slain_monsters:
            return True
        last_val = self.slain_monsters[-1].numeric_value()
        return monster_card.numeric_value() < last_val

    def attack(self, monster_card):
        """Handles combat logic with or without a weapon."""
        value = monster_card.numeric_value()
        if self.weapon and self.can_use_weapon_on(monster_card):
            damage = max(0, value - self.weapon.numeric_value())
            self.slain_monsters.append(monster_card)
            print(f"Used {self.weapon} to defeat {monster_card}, took {damage} damage.")
        else:
            damage = value
            print(f"Fought {monster_card} barehanded. Took {damage} damage.")

        self.health -= damage
        print(f"Health: {self.health}")

    def use_potion(self, potion_card, used_already):
        """Heals the player once per turn, capped at 20 health."""
        if used_already:
            print(f"Already used potion. Discarding {potion_card}.")
            return False

        heal = potion_card.numeric_value()
        before = self.health
        self.health = min(self.health + heal, 20)
        print(f"Healed {potion_card}: {before} → {self.health}")
        return True


class Game:
    """Handles deck creation, gameplay loop, and room mechanics."""

    def __init__(self):
        self.player = Player()
        self.deck = self.build_deck()
        self.discard_pile = []
        self.last_room_skipped = False
        self.room_carryover = []
        random.shuffle(self.deck)

    def build_deck(self):
        """Builds the full Scoundrel deck with removed red face cards and aces."""
        suits = ['Hearts', 'Diamonds', 'Spades', 'Clubs']
        values = ['Ace'] + [str(n) for n in range(2, 11)] + ['J', 'Q', 'K']
        deck = [Card(value, suit) for suit in suits for value in values]

        return [
            card for card in deck
            if not (card.suit == 'Hearts' and card.value in ['J', 'Q', 'K', 'Ace'])
            and not (card.suit == 'Diamonds' and card.value in ['J', 'Q', 'K', 'Ace'])
        ]

    def draw_room(self):
        """Draws 4 cards to form a room, including carryover from previous turn."""
        room = self.room_carryover[:]
        self.room_carryover = []

        while len(room) < 4 and self.deck:
            room.append(self.deck.pop(0))

        return room

    def skip_room(self, room):
        """Handles skipping a room, reshuffling the cards to the bottom."""
        if self.last_room_skipped:
            print("Can't skip two rooms in a row!")
            return False

        self.deck.extend(room)
        random.shuffle(self.deck)
        self.last_room_skipped = True
        print("Room skipped.\n")
        return True

    def play_turn(self):
        """Executes a single player turn."""
        room = self.draw_room()
        if len(room) < 4:
            print("Dungeon exhausted — you win!")
            return False

        print("\nRoom:")
        for index, card in enumerate(room):
            print(f"{index + 1}. {card}")

        if not self.last_room_skipped:
            answer = input("Skip room? (Y/N): ").strip().upper()
            if answer == 'Y' and self.skip_room(room):
                return True

        self.last_room_skipped = False
        potion_used = False

        for _ in range(3):
            while True:
                try:
                    choice = int(input("Choose a card (1–4): ")) - 1
                    if 0 <= choice < len(room):
                        break
                except ValueError:
                    pass
                print("Invalid input.")

            card = room.pop(choice)

            if card.suit in ['Spades', 'Clubs']:
                self.player.attack(card)
                self.discard_pile.append(card)
            elif card.suit == 'Diamonds':
                self.player.equip_weapon(card, self.discard_pile)
            elif card.suit == 'Hearts':
                potion_used = self.player.use_potion(card, potion_used)
                self.discard_pile.append(card)

            if self.player.health <= 0:
                print("\nYou died. Game over.")
                return False

        self.room_carryover = room[:]
        return True


def run_game():
    """Runs the full game loop."""
    print("Welcome to Scoundrel!")
    game = Game()

    while game.deck and game.player.health > 0:
        if not game.play_turn():
            break


if __name__ == "__main__":
    run_game()
