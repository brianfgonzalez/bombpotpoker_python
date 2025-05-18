type Suit = '♠' | '♥' | '♦' | '♣';
type Rank = '2'|'3'|'4'|'5'|'6'|'7'|'8'|'9'|'10'|'J'|'Q'|'K'|'A';

interface Card {
    suit: Suit;
    rank: Rank;
}

interface Player {
    id: number;
    cards: Card[];
}

export class PokerGame {
    deck: Card[] = [];
    players: Player[] = [];
    firstFlop: Card[] = [];
    secondFlop: Card[] = [];
    numPlayers: number;
    numFlops: number;

    constructor(numPlayers: number, numFlops: number = 2) {
        this.numPlayers = numPlayers;
        this.numFlops = numFlops;
        this.initDeck();
        this.deal();
    }

    private initDeck() {
        const suits: Suit[] = ['♠', '♥', '♦', '♣'];
        const ranks: Rank[] = ['2','3','4','5','6','7','8','9','10','J','Q','K','A'];
        this.deck = [];
        for (const suit of suits) {
            for (const rank of ranks) {
                this.deck.push({ suit, rank });
            }
        }
        this.shuffle();
    }

    private shuffle() {
        for (let i = this.deck.length - 1; i > 0; i--) {
            const j = Math.floor(Math.random() * (i + 1));
            [this.deck[i], this.deck[j]] = [this.deck[j], this.deck[i]];
        }
    }

    private deal() {
        this.players = [];
        for (let i = 0; i < this.numPlayers; i++) {
            this.players.push({ id: i + 1, cards: [this.deck.pop()!, this.deck.pop()!] });
        }
        this.firstFlop = [this.deck.pop()!, this.deck.pop()!, this.deck.pop()!];
        if (this.numFlops > 1) {
            this.secondFlop = [this.deck.pop()!, this.deck.pop()!, this.deck.pop()!];
        }
    }

    getGameState() {
        return {
            players: this.players,
            firstFlop: this.firstFlop,
            secondFlop: this.secondFlop
        };
    }
}
