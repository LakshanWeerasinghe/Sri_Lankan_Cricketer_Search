import json

from objects.Player import Player


def read_corpus_en(filename):
    content = None
    with open(filename) as f:
        content = json.load(f)
    return content


def write_corpus(data):
    with open('corpus-en-filtered.json', 'w+', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)


def reduce_text_size(player: Player):

    if player.international_carrier_en:
        international_carrier_en = ' '.join(player.international_carrier_en.split()[0:120])
        setattr(player, "international_carrier_en", international_carrier_en)
    if player.biography_en:
        biography_en = ' '.join(player.biography_en.split()[0:120])
        setattr(player, "biography_en", biography_en)


if __name__ == '__main__':
    player_corpus_en = read_corpus_en('player_corpus_en.json')

    playersJsonObjs = []
    for player_details in player_corpus_en:
        player = Player.get_player(json.loads(player_details))
        reduce_text_size(player)
        playersJsonObjs.append(json.dumps(player.__dict__))

    write_corpus(playersJsonObjs)