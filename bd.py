# bd.py

# Carregar os arquivos CSV
file_paths = [
    "https://www.football-data.co.uk/mmz4281/2324/E0.csv", #England Premier League
    "https://www.football-data.co.uk/mmz4281/2223/E0.csv", #England Premier League
    "https://www.football-data.co.uk/mmz4281/2122/E0.csv", #England Premier League
    "https://www.football-data.co.uk/mmz4281/2021/E0.csv", #England Premier League
    "https://www.football-data.co.uk/mmz4281/1920/E0.csv", #England Premier League
    "https://www.football-data.co.uk/mmz4281/1819/E0.csv", #England Premier League
    "https://www.football-data.co.uk/mmz4281/1718/E0.csv", #England Premier League
    "https://www.football-data.co.uk/mmz4281/1617/E0.csv", #England Premier League
    "https://www.football-data.co.uk/mmz4281/1516/E0.csv", #England Premier League
    "https://www.football-data.co.uk/mmz4281/1415/E0.csv", #England Premier League
    "https://www.football-data.co.uk/mmz4281/2324/E1.csv", #England Championship 
    "https://www.football-data.co.uk/mmz4281/2223/E1.csv", #England Championship 
    "https://www.football-data.co.uk/mmz4281/2122/E1.csv", #England Championship 
    "https://www.football-data.co.uk/mmz4281/2021/E1.csv", #England Championship 
    "https://www.football-data.co.uk/mmz4281/1920/E1.csv", #England Championship 
    "https://www.football-data.co.uk/mmz4281/1819/E1.csv", #England Championship 
    "https://www.football-data.co.uk/mmz4281/1718/E1.csv", #England Championship 
    "https://www.football-data.co.uk/mmz4281/1617/E1.csv", #England Championship 
    "https://www.football-data.co.uk/mmz4281/1516/E1.csv", #England Championship 
    "https://www.football-data.co.uk/mmz4281/1415/E1.csv", #England Championship 
    "https://www.football-data.co.uk/mmz4281/2324/E2.csv", #England League 1
    "https://www.football-data.co.uk/mmz4281/2223/E2.csv", #England League 1
    "https://www.football-data.co.uk/mmz4281/2122/E2.csv", #England League 1
    "https://www.football-data.co.uk/mmz4281/2021/E2.csv", #England League 1
    "https://www.football-data.co.uk/mmz4281/1920/E2.csv", #England League 1
    "https://www.football-data.co.uk/mmz4281/1819/E2.csv", #England League 1
    "https://www.football-data.co.uk/mmz4281/1718/E2.csv", #England League 1 
    "https://www.football-data.co.uk/mmz4281/1617/E2.csv", #England League 1
    "https://www.football-data.co.uk/mmz4281/1516/E2.csv", #England League 1
    "https://www.football-data.co.uk/mmz4281/1415/E2.csv", #England League 1

    "https://www.football-data.co.uk/mmz4281/2324/SC0.csv", #Scotland Premier League
    "https://www.football-data.co.uk/mmz4281/2223/SC0.csv", #Scotland Premier League
    "https://www.football-data.co.uk/mmz4281/2122/SC0.csv", #Scotland Premier League
    "https://www.football-data.co.uk/mmz4281/2021/SC0.csv", #Scotland Premier League
    "https://www.football-data.co.uk/mmz4281/1920/SC0.csv", #Scotland Premier League
    "https://www.football-data.co.uk/mmz4281/1819/SC0.csv", #Scotland Premier League
    "https://www.football-data.co.uk/mmz4281/1718/SC0.csv", #Scotland Premier League
    "https://www.football-data.co.uk/mmz4281/1617/SC0.csv", #Scotland Premier League
    "https://www.football-data.co.uk/mmz4281/1516/SC0.csv", #Scotland Premier League
    "https://www.football-data.co.uk/mmz4281/1415/SC0.csv", #Scotland Premier League

    "https://www.football-data.co.uk/mmz4281/2324/SC1.csv", #Scotland Divison 1
    "https://www.football-data.co.uk/mmz4281/2223/SC1.csv",
    "https://www.football-data.co.uk/mmz4281/2122/SC1.csv",
    "https://www.football-data.co.uk/mmz4281/2021/SC1.csv",
    "https://www.football-data.co.uk/mmz4281/1920/SC1.csv",
    "https://www.football-data.co.uk/mmz4281/1819/SC1.csv",
    "https://www.football-data.co.uk/mmz4281/1718/SC1.csv",
    "https://www.football-data.co.uk/mmz4281/1617/SC1.csv",
    "https://www.football-data.co.uk/mmz4281/1516/SC1.csv",
    "https://www.football-data.co.uk/mmz4281/1415/SC1.csv",

    "https://www.football-data.co.uk/mmz4281/2324/SC2.csv", #Scotland Divison 2
    "https://www.football-data.co.uk/mmz4281/2223/SC2.csv",
    "https://www.football-data.co.uk/mmz4281/2122/SC2.csv",
    "https://www.football-data.co.uk/mmz4281/2021/SC2.csv",
    "https://www.football-data.co.uk/mmz4281/1920/SC2.csv",
    "https://www.football-data.co.uk/mmz4281/1819/SC2.csv",
    "https://www.football-data.co.uk/mmz4281/1718/SC2.csv",
    "https://www.football-data.co.uk/mmz4281/1617/SC2.csv",
    "https://www.football-data.co.uk/mmz4281/1516/SC2.csv",
    "https://www.football-data.co.uk/mmz4281/1415/SC2.csv",

    "https://www.football-data.co.uk/mmz4281/2324/SC3.csv", #Scotland Divison 3
    "https://www.football-data.co.uk/mmz4281/2223/SC3.csv",
    "https://www.football-data.co.uk/mmz4281/2122/SC3.csv",
    "https://www.football-data.co.uk/mmz4281/2021/SC3.csv",
    "https://www.football-data.co.uk/mmz4281/1920/SC3.csv",
    "https://www.football-data.co.uk/mmz4281/1819/SC3.csv",
    "https://www.football-data.co.uk/mmz4281/1718/SC3.csv",
    "https://www.football-data.co.uk/mmz4281/1617/SC3.csv",
    "https://www.football-data.co.uk/mmz4281/1516/SC3.csv",
    "https://www.football-data.co.uk/mmz4281/1415/SC3.csv",
    
    "https://www.football-data.co.uk/mmz4281/2324/D1.csv", #Germany Bundesliga
    "https://www.football-data.co.uk/mmz4281/2223/D1.csv",
    "https://www.football-data.co.uk/mmz4281/2122/D1.csv",
    "https://www.football-data.co.uk/mmz4281/2021/D1.csv",
    "https://www.football-data.co.uk/mmz4281/1920/D1.csv",
    "https://www.football-data.co.uk/mmz4281/1819/D1.csv",
    "https://www.football-data.co.uk/mmz4281/1718/D1.csv",
    "https://www.football-data.co.uk/mmz4281/1617/D1.csv",
    "https://www.football-data.co.uk/mmz4281/1516/D1.csv",
    "https://www.football-data.co.uk/mmz4281/1415/D1.csv",

    "https://www.football-data.co.uk/mmz4281/2324/D2.csv", #Germany Bundesliga 2
    "https://www.football-data.co.uk/mmz4281/2223/D2.csv",
    "https://www.football-data.co.uk/mmz4281/2122/D2.csv",
    "https://www.football-data.co.uk/mmz4281/2021/D2.csv",
    "https://www.football-data.co.uk/mmz4281/1920/D2.csv",
    "https://www.football-data.co.uk/mmz4281/1819/D2.csv",
    "https://www.football-data.co.uk/mmz4281/1718/D2.csv",
    "https://www.football-data.co.uk/mmz4281/1617/D2.csv",
    "https://www.football-data.co.uk/mmz4281/1516/D2.csv",
    "https://www.football-data.co.uk/mmz4281/1415/D2.csv",

    

    
    
    "https://www.football-data.co.uk/new/ARG.csv",
    "https://www.football-data.co.uk/new/AUT.csv",
    "https://www.football-data.co.uk/new/BRA.csv",
    "https://www.football-data.co.uk/new/CHN.csv",
    "https://www.football-data.co.uk/new/DNK.csv",
    "https://www.football-data.co.uk/new/FIN.csv",
    "https://www.football-data.co.uk/new/IRL.csv",
    "https://www.football-data.co.uk/new/JPN.csv",
    "https://www.football-data.co.uk/new/MEX.csv",
    "https://www.football-data.co.uk/new/NOR.csv",
    "https://www.football-data.co.uk/new/POL.csv",
    "https://www.football-data.co.uk/new/ROU.csv",
    "https://www.football-data.co.uk/new/RUS.csv",
    "https://www.football-data.co.uk/new/SWE.csv",
    "https://www.football-data.co.uk/new/SWZ.csv",
    "https://www.football-data.co.uk/new/USA.csv",

    "https://raw.githubusercontent.com/scooby75/bdfootball/main/albania-first-division-matches-2022-to-2023-stats.csv",
    "https://raw.githubusercontent.com/scooby75/bdfootball/main/albania-superliga-matches-2022-to-2023-stats.csv",
    "https://raw.githubusercontent.com/scooby75/bdfootball/main/australia-a-league-matches-2021-to-2022-stats.csv",
    "https://raw.githubusercontent.com/scooby75/bdfootball/main/australia-a-league-matches-2022-to-2023-stats.csv",
    "https://raw.githubusercontent.com/scooby75/bdfootball/main/australia-a-league-matches-2023-to-2024-stats.csv",
    "https://raw.githubusercontent.com/scooby75/bdfootball/main/azerbaijan-first-division-matches-2021-to-2022-stats.csv",
    "https://raw.githubusercontent.com/scooby75/bdfootball/main/azerbaijan-first-division-matches-2022-to-2023-stats.csv",
    "https://raw.githubusercontent.com/scooby75/bdfootball/main/azerbaijan-first-division-matches-2023-to-2024-stats.csv",
    "https://raw.githubusercontent.com/scooby75/bdfootball/main/cambodia-cambodian-league-matches-2021-to-2021-stats.csv",
    "https://raw.githubusercontent.com/scooby75/bdfootball/main/cambodia-cambodian-league-matches-2022-to-2022-stats.csv",
    "https://raw.githubusercontent.com/scooby75/bdfootball/main/cambodia-cambodian-league-matches-2023-to-2023-stats.csv",
    "https://raw.githubusercontent.com/scooby75/bdfootball/main/chile-primera-division-matches-2021-to-2021-stats.csv",
    "https://raw.githubusercontent.com/scooby75/bdfootball/main/chile-primera-division-matches-2022-to-2022-stats.csv",
    "https://raw.githubusercontent.com/scooby75/bdfootball/main/chile-primera-division-matches-2023-to-2023-stats.csv",
    "https://raw.githubusercontent.com/scooby75/bdfootball/main/costa-rica-primera-division-fpd-matches-2021-to-2022-stats.csv",
    "https://raw.githubusercontent.com/scooby75/bdfootball/main/costa-rica-primera-division-fpd-matches-2022-to-2023-stats.csv",
    "https://raw.githubusercontent.com/scooby75/bdfootball/main/costa-rica-primera-division-fpd-matches-2023-to-2024-stats.csv",
    "https://raw.githubusercontent.com/scooby75/bdfootball/main/egypt-second-division-matches-2021-to-2022-stats.csv",
    "https://raw.githubusercontent.com/scooby75/bdfootball/main/egypt-second-division-matches-2022-to-2023-stats.csv",
    "https://raw.githubusercontent.com/scooby75/bdfootball/main/egypt-second-division-matches-2023-to-2024-stats.csv",
    "https://raw.githubusercontent.com/scooby75/bdfootball/main/greece-super-league-matches-2021-to-2022-stats.csv",
    "https://raw.githubusercontent.com/scooby75/bdfootball/main/greece-super-league-matches-2022-to-2023-stats.csv",
    "https://raw.githubusercontent.com/scooby75/bdfootball/main/greece-super-league-matches-2023-to-2024-stats.csv",
    "https://raw.githubusercontent.com/scooby75/bdfootball/main/hong-kong-hong-kong-premier-league-matches-2022-to-2023-stats.csv",
    "https://raw.githubusercontent.com/scooby75/bdfootball/main/hong-kong-hong-kong-premier-league-matches-2023-to-2024-stats.csv",
    "https://raw.githubusercontent.com/scooby75/bdfootball/main/hungary-nb-ii-matches-2021-to-2022-stats.csv",
    "https://raw.githubusercontent.com/scooby75/bdfootball/main/hungary-nb-ii-matches-2022-to-2023-stats.csv",
    "https://raw.githubusercontent.com/scooby75/bdfootball/main/hungary-nb-ii-matches-2023-to-2024-stats.csv",
    "https://raw.githubusercontent.com/scooby75/bdfootball/main/hungary-nb-i-matches-2021-to-2022-stats.csv",
    "https://raw.githubusercontent.com/scooby75/bdfootball/main/hungary-nb-i-matches-2022-to-2023-stats.csv",
    "https://raw.githubusercontent.com/scooby75/bdfootball/main/hungary-nb-i-matches-2023-to-2024-stats.csv",
    "https://raw.githubusercontent.com/scooby75/bdfootball/main/indonesia-liga-1-matches-2021-to-2022-stats.csv",
    "https://raw.githubusercontent.com/scooby75/bdfootball/main/indonesia-liga-1-matches-2022-to-2023-stats.csv",
    "https://raw.githubusercontent.com/scooby75/bdfootball/main/indonesia-liga-1-matches-2023-to-2024-stats.csv",
    "https://raw.githubusercontent.com/scooby75/bdfootball/main/mexico-liga-mx-matches-2021-to-2022-stats.csv",
    "https://raw.githubusercontent.com/scooby75/bdfootball/main/mexico-liga-mx-matches-2022-to-2023-stats.csv",
    "https://raw.githubusercontent.com/scooby75/bdfootball/main/mexico-liga-mx-matches-2023-to-2024-stats.csv",
    "https://raw.githubusercontent.com/scooby75/bdfootball/main/peru-primera-division-matches-2021-to-2021-stats.csv",
    "https://raw.githubusercontent.com/scooby75/bdfootball/main/peru-primera-division-matches-2022-to-2022-stats.csv",
    "https://raw.githubusercontent.com/scooby75/bdfootball/main/peru-primera-division-matches-2023-to-2023-stats.csv",
    "https://raw.githubusercontent.com/scooby75/bdfootball/main/romania-liga-i-matches-2021-to-2022-stats.csv",
    "https://raw.githubusercontent.com/scooby75/bdfootball/main/romania-liga-i-matches-2022-to-2023-stats.csv",
    "https://raw.githubusercontent.com/scooby75/bdfootball/main/romania-liga-i-matches-2023-to-2024-stats.csv",
    "https://raw.githubusercontent.com/scooby75/bdfootball/main/south-korea-k-league-1-matches-2021-to-2021-stats.csv",
    "https://raw.githubusercontent.com/scooby75/bdfootball/main/south-korea-k-league-1-matches-2022-to-2022-stats.csv",
    "https://raw.githubusercontent.com/scooby75/bdfootball/main/south-korea-k-league-1-matches-2023-to-2023-stats.csv",
    "https://raw.githubusercontent.com/scooby75/bdfootball/main/south-korea-k-league-2-matches-2021-to-2021-stats.csv",
    "https://raw.githubusercontent.com/scooby75/bdfootball/main/south-korea-k-league-2-matches-2022-to-2022-stats.csv",
    "https://raw.githubusercontent.com/scooby75/bdfootball/main/south-korea-k-league-2-matches-2023-to-2023-stats.csv",
    "https://raw.githubusercontent.com/scooby75/bdfootball/main/thailand-thai-league-t1-matches-2021-to-2022-stats.csv",
    "https://raw.githubusercontent.com/scooby75/bdfootball/main/thailand-thai-league-t1-matches-2022-to-2023-stats.csv",
    "https://raw.githubusercontent.com/scooby75/bdfootball/main/thailand-thai-league-t1-matches-2023-to-2024-stats.csv"

    
    
]
