class Player:
    full_name_en = None
    birthday = None
    batting_style_en = None
    bowling_style_en = None
    role_en = None
    education_en = None
    biography_en = None
    international_carrier_en = None
    test_debut_en = None
    odi_debut_en = None
    t20i_debut_en = None
    website_url = None

    full_name_si = None
    batting_style_si = None
    bowling_style_si = None
    role_si = None
    education_si = None
    biography_si = None
    international_carrier_si = None
    test_debut_si = None
    odi_debut_si = None
    t20i_debut_si = None

    odi_runs = 0
    odi_wickets = 0

    def __init__(self, url):
        self.website_url = url

    def __repr__(self):
        return self.__str__()

    def __str__(self):
        player_details = ""
        player_details += "Full Name (EN) : {}\n\n".format(self.full_name_en)
        player_details += "Full Name (SI) : {}\n\n".format(self.full_name_si)
        player_details += "Birthday : {}\n\n".format(self.birthday)
        player_details += "Batting Style (EN) : {}\n\n".format(self.batting_style_en)
        player_details += "Batting Style (SI) : {}\n\n".format(self.batting_style_si)
        player_details += "Bowling Style (EN) : {}\n\n".format(self.bowling_style_en)
        player_details += "Bowling Style (SI) : {}\n\n".format(self.bowling_style_si)
        player_details += "Role (EN) : {}\n\n".format(self.role_en)
        player_details += "Role (SI) : {}\n\n".format(self.role_si)
        player_details += "Education (EN) : {}\n\n".format(self.education_en)
        player_details += "Education (SI) : {}\n\n".format(self.education_si)
        player_details += "Biography (EN) : {}\n\n".format(self.biography_en)
        player_details += "Biography (SI) : {}\n\n".format(self.biography_si)
        player_details += "Internation Carrier (EN) : {}\n\n".format(self.international_carrier_en)
        player_details += "Internation Carrier (SI) : {}\n\n".format(self.international_carrier_si)
        player_details += "Test Debut : (EN)  {}\n\n".format(self.test_debut_en)
        player_details += "Test Debut : (SI)  {}\n\n".format(self.test_debut_si)
        player_details += "ODI Debut (EN) : {}\n\n".format(self.odi_debut_en)
        player_details += "ODI Debut (SI) : {}\n\n".format(self.odi_debut_si)
        player_details += "T20I Debut (EN) : {}\n\n".format(self.t20i_debut_en)
        player_details += "T20I Debut (SI) : {}\n\n".format(self.t20i_debut_si)
        player_details += "ODI Runs : {}\n\n".format(self.odi_runs)
        player_details += "ODI Wickets : {}\n\n".format(self.odi_wickets)
        player_details += "Web Site URL : {}\n\n".format(self.website_url)

        return player_details

    @staticmethod
    def get_player(player_json_obj):
        player = Player(None)
        for key in player_json_obj:
            setattr(player, key, player_json_obj[key])
        return player
