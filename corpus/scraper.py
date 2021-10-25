import json
import os
import re
import requests
import wikipedia
from bs4 import BeautifulSoup
from multiprocessing import Pool
from objects.Player import Player

wikipedia.set_lang("en")


def personal_info_extractor(player, soup):
    player_info_attrs = {
        "FULL NAME": "full_name_en",
        "BORN": "birthday",
        "BATTING STYLE": "batting_style_en",
        "BOWLING STYLE": "bowling_style_en",
        "PLAYING ROLE": "role_en",
        "EDUCATION": "education_en"
    }
    personal_info_html_content = soup.find_all('div', class_='player_overview-grid')[0]

    parsed_personal_info = BeautifulSoup(str(personal_info_html_content), 'html.parser')
    personal_info_list = parsed_personal_info.find_all('div', class_='')
    for personal_info_html in personal_info_list:
        item_parser = BeautifulSoup(str(personal_info_html), 'html.parser')
        attr = item_parser.find('p', class_='player-card-heading').text.upper()
        value = item_parser.find('h5').text
        if attr in player_info_attrs:
            setattr(player, player_info_attrs.get(attr), value)


def bio_info_extractor(player, soup):
    bio_info_html_content = soup.find_all('div', class_="more-content-gradient-content")

    parsed_bio_info = BeautifulSoup(str(bio_info_html_content), 'html.parser')
    bio = ""
    for content in parsed_bio_info.select('p'):
        bio += content.extract().text

    # remove the author name
    bio = bio.rsplit('.', 1)[0]
    setattr(player, 'biography_en', bio)


def debut_info_extractor(player, soup):
    player_debut_attrs = {
        "Test": "test_debut_en",
        "ODI": "odi_debut_en",
        "T20I": "t20i_debut_en"
    }

    debut_html_content = soup.find_all('div', class_='more-content black-1000')
    parsed_debut_content = BeautifulSoup(str(debut_html_content), 'html.parser')
    debut_details_list = parsed_debut_content.find_all('div', class_='')
    for debut_details in debut_details_list:
        debut = BeautifulSoup(str(debut_details), 'html.parser')
        debut_format = debut.find('h5', class_='player-matches-subtitle').text[:4].strip()
        debut_info = debut.find_all('span', class_='player-match-link')
        if debut_format in player_debut_attrs:
            if len(debut_info) > 0:
                debut_info = debut.find_all('span', class_='player-match-link')[0].text
                setattr(player, player_debut_attrs.get(debut_format), debut_info)


def extract_player_stats(player, soup):

    table_headers = soup.find_all('h5', class_='table-header')
    tables = soup.find_all('tbody')

    runs_index = 0
    wickets_index = 1
    if table_headers[0].text != 'Batting & Fielding':
        runs_index = 1
        wickets_index = 0

    odi_runs = 0
    if player.test_debut_en:
        odi_runs = BeautifulSoup(str(tables[runs_index]), 'html.parser').find('tr', class_='fix-second-child-color')
        for i in range(15):
            odi_runs = odi_runs.next
    else:
        odi_runs = BeautifulSoup(str(tables[runs_index]), 'html.parser').find('tr', class_='fix-first-child-color')
        for i in range(15):
            odi_runs = odi_runs.next

    odi_wickets = 0
    if player.test_debut_en:
        odi_wickets = BeautifulSoup(str(tables[wickets_index]), 'html.parser').find('tr', class_='fix-second-child-color')
        for i in range(18):
            odi_wickets = odi_wickets.next
    else:
        odi_wickets = BeautifulSoup(str(tables[wickets_index]), 'html.parser').find('tr', class_='fix-first-child-color')
        for i in range(18):
            odi_wickets = odi_wickets.next

    if odi_runs.isnumeric():
        player.odi_runs = int(odi_runs)
    else:
        player.odi_runs = 0

    if odi_wickets.isnumeric():
        player.odi_wickets = int(odi_wickets)
    else:
        player.odi_wickets = 0


def international_carrier_info_extractor(player, soup):
    international_carrier_html_tag = soup.find_all('span', id='International_career')
    if len(international_carrier_html_tag) > 0:
        international_carrier_html_tag = international_carrier_html_tag[0].parent
        text = ""
        while True:
            international_carrier_html_tag = international_carrier_html_tag.next
            tag = str(international_carrier_html_tag)
            if tag[:4] == '<h2>':
                break
            text += tag

        international_carrier_html_content = BeautifulSoup(text, 'html.parser')
        p_tags = international_carrier_html_content.find_all('p')

        international_carrier = ""
        for p_tag in p_tags:
            international_carrier += p_tag.text

        # remove references
        international_carrier = re.sub("\[\d{1,4}\]", "", international_carrier)

        # remove new line characters
        international_carrier = re.sub("\\n", "", international_carrier)

        setattr(player, 'international_carrier_en', international_carrier)


def get_players_espncricinfo_urls():
    PAGE_SIZE = 40
    PLAYER_INFO_BASE_URL = "https://www.espncricinfo.com/player/{}-{}"
    INITIAL_ODI_PLAYER_LIST_API = "https://hs-consumer-api.espncricinfo.com/v1/pages/player/debut?teamId=8&classId=2"
    PAGED_ODI_PLAYERS_LIST_API = "https://hs-consumer-api.espncricinfo.com/v1/pages/player/search?mode=BOTH&page={" \
                                 "}&records={" \
                                 "}&sort=ALPHA_DESC&filterTeamId=8&filterClassId=2&filterDebut=true&selectDebut=true"

    odi_players_urls = []

    initial_odi_players_list_response = requests.get(INITIAL_ODI_PLAYER_LIST_API)
    total_players_count = json.loads(initial_odi_players_list_response.content)['content']['players']['total']

    round_up = lambda x: x if x == int(x) else int(x) + 1
    page_count = round_up(total_players_count / PAGE_SIZE)

    for page_number in range(1, page_count + 1):
        paged_odi_players_list_response = requests.get(PAGED_ODI_PLAYERS_LIST_API.format(page_number, PAGE_SIZE))
        get_odi_players_list = json.loads(paged_odi_players_list_response.content)['results']
        for player in get_odi_players_list:
            odi_players_urls.append(PLAYER_INFO_BASE_URL.format(player["slug"], player["objectId"]))

    return odi_players_urls


def extract_player_info_from_espncricinfo(player):
    player_espncricinfo_page_response = requests.get(player.website_url)
    player_espncricinfo_soup = BeautifulSoup(player_espncricinfo_page_response.content, 'html.parser')

    personal_info_extractor(player, player_espncricinfo_soup)
    bio_info_extractor(player, player_espncricinfo_soup)
    debut_info_extractor(player, player_espncricinfo_soup)
    extract_player_stats(player, player_espncricinfo_soup)


def extract_player_info_from_wikipedia(player):
    if player.full_name_en is not None:
        result = wikipedia.search(player.full_name_en, results=1, suggestion=True)
        if len(result[0]) > 0:
            player_page_url = wikipedia.page(result[0][0]).url
            player_wiki_page_response = requests.get(player_page_url)
            player_wiki_soup = BeautifulSoup(player_wiki_page_response.content, 'html.parser')
            international_carrier_info_extractor(player, player_wiki_soup)


def extract_player_info(player_url):
    player = Player(player_url)
    print(f'Player {player.website_url} extract info started')
    extract_player_info_from_espncricinfo(player)
    extract_player_info_from_wikipedia(player)
    print(f'Player {player.website_url} extract finished started')
    return player


if __name__ == '__main__':

    odi_players_espncricinfo_urls = get_players_espncricinfo_urls()

    all_players = []

    with Pool(os.cpu_count()) as pool:
        result = pool.imap(extract_player_info, odi_players_espncricinfo_urls)
        all_players.extend(result)

    playersJsonObjs = []
    for player in all_players:
        playersJsonObjs.append(json.dumps(player.__dict__))

    with open('player_corpus_en.json', 'w+', encoding='utf-8') as f:
        json.dump(playersJsonObjs, f, ensure_ascii=False, indent=4)
