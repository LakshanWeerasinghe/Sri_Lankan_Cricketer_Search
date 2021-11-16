import json
import os
from multiprocessing import Pool

from googletrans import Translator

from objects.Player import Player

translator = Translator()


def read_corpus_en(filename):
    content = None
    with open(filename) as f:
        content = json.load(f)
    return content


def write_corpus(data):
    with open('final-corpus.json', 'w+', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)


batting_styles = {
    "Right hand bat": "දකුණත් පිතිකරු",
    "Left hand bat": "වමත් පිතිකරු"
}

bowling_styles = {
    "Right arm offbreak": "දකුණත් පිටදග",
    "Right arm fast medium": "දකුණත් මදවේග-වේග",
    "Right arm medium": "දකුණත් මදවේග",
    "Slow left arm orthodox": "වමත් ඕතඩොක්ස්",
    "Legbreak": "දකුණත් පාදග",
    "Left arm fast medium": "වමත් මදවේග-වේග",
    "Left arm medium fast": "වමත් මදවේග-වේග",
    "Right arm fast": "දකුණත් වේග",
    "Left arm medium, Slow left arm orthodox": "වමත් මදවේග වමත් ඕතඩොක්ස්"
}

roles = {
    "Bowler": "පන්දු යවන්නා",
    "Allrounder": "තුන් ඉරියව් ක්‍රීඩකයා",
    "Batter": "පිතිකරු",
    "Wicketkeeper batter": "කඩුලු රකින පිතිකරු",
    "Middle order batter": "මැදපෙළ පිතිකරු",
    "Top order batter": "මුල්පෙළ පිතිකරු",
    "Opening batter": "ආරම්භක පිතිකරු",
    "Batting allrounder": "පිතිකරන තුන් ඉරියව් ක්‍රීඩකයා",
    "Bowling allrounder": "පන්දු යවන තුන් ඉරියව් ක්‍රීඩකයා",
}

schools = {
    "Prince of Wales College, Moratuwa": "වේල්ස් කුමර විද්‍යාලය",
    "Richmond College, Galle": "රිච්මන්ඩ් විද්‍යාලය",
    "Ananda College, Colombo": "ආනන්ද විද්‍යාලය",
    "Royal College, Colombo": "රාජකීය විද්‍යාලය",
    "St. Aloysius' College, Galle": "ශාන්ත ඇලෝසියස් විද්‍යාලය",
    "St. Joseph's College, Colombo": "කොළඹ ශාන්ත ජෝශප් විද්‍යාලය",
    "De Mazenod College, Kandana": "මැසනොද් විද්‍යාලය කඳාන",
    "Nalanda College, Colombo": "නාලන්දා විද්‍යාලය",
    "St. Peter's College, Colombo": "ශාන්ත පීතර විද්‍යාලය, කොළඹ",
}


def english_to_sinhala_converter(player: Player):
    if player.full_name_en:
        player.full_name_si = translator.translate(player.full_name_en, src='en', dest='si').text

    if player.batting_style_en:
        player.batting_style_si = batting_styles.get(player.batting_style_en)

    if player.bowling_style_en:
        player.bowling_style_si = bowling_styles.get(player.bowling_style_en)

    if player.role_en:
        player.role_si = roles.get(player.role_en)

    if player.education_en:
        if schools.get(player.education_en):
            player.education_si = schools.get(player.education_en)
        else:
            player.education_si = translator.translate(player.education_en, src='en', dest='si').text

    if player.biography_en:
        player.biography_si = translator.translate(player.biography_en, src='en', dest='si').text

    if player.international_carrier_en:
        player.international_carrier_si = translator.translate(player.international_carrier_en, src='en',
                                                               dest='si').text

    if player.test_debut_en:
        player.test_debut_si = translator.translate(player.test_debut_en, src='en', dest='si').text

    if player.odi_debut_en:
        player.odi_debut_si = translator.translate(player.odi_debut_en, src='en', dest='si').text

    if player.t20i_debut_en:
        player.t20i_debut_si = translator.translate(player.t20i_debut_en, src='en', dest='si').text


def player_preprocessor(player_dict):
    player = Player.get_player(json.loads(player_dict))
    english_to_sinhala_converter(player)
    print(player)
    return player


if __name__ == '__main__':
    player_corpus_en = read_corpus_en('corpus-en-filtered.json')

    all_players = []
    with Pool(os.cpu_count()) as pool:
        result = pool.imap(player_preprocessor, player_corpus_en)
        all_players.extend(result)

    playersJsonObjs = []
    for player in all_players:
        playersJsonObjs.append(json.dumps(player.__dict__))

    write_corpus(playersJsonObjs)
