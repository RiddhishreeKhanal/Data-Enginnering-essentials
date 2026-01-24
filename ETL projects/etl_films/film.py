import requests
import pandas as pd
from bs4 import BeautifulSoup

url = 'https://web.archive.org/web/20230902185655/https://en.everybodywiki.com/100_Most_Highly-Ranked_Films'
db_name = 'Movies.db'
table_name = 'Top_50'
csv_path = 'ETL projects/etl_films/top_50_films.csv'
df = pd.DataFrame(columns=["Average Rank","Film","Year"])
count = 0

html_page = requests.get(url).text
data = BeautifulSoup(html_page, 'html.parser')

tables = data.find_all('tbody')
rows = tables[0].find_all('tr')

for row in rows:
    if count < 50 :
        col = row.find_all('td')
        if len(col)!=0:
            data_dict = {"Average Rank": int(col[0].contents[0]),
                         "Film": str(col[1].get_text(strip=True)),
                         "Year": int(col[2].contents[0])}
            df1 = pd.DataFrame(data_dict, index=[0])

            df = pd.concat([df,df1], ignore_index= True)

            count+=1
    else:
        break

print(df.to_string(index=False))

#saving to csv
df.to_csv(csv_path, index=False)

#saving to json
df.to_json("ETL projects/etl_films/top_50_films.json", 
           orient="records", 
           indent=4)

