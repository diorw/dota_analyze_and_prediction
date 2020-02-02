import pymysql
import json
import pandas as pd
conn = pymysql.connect(host = '120.55.167.182',user = 'root',password = 'wda20190707',database = 'dota')
cursor = conn.cursor()

sql = '''
select player_1_hero_id,player_2_hero_id,player_3_hero_id,
       player_4_hero_id,player_5_hero_id,player_6_hero_id,player_7_hero_id
    ,player_8_hero_id,player_9_hero_id,player_10_hero_id,win
from dota.`match`
where game_mode = 22 or game_mode = 3
'''
cursor.execute(sql)
match_data = cursor.fetchall()
match_data = list(match_data)
match_data = list(map(list,match_data))
match_df = pd.DataFrame(match_data)
columns = []
for i in range(1,11):
    columns.append("player_"+str(i)+"_hero_id")
columns.append("target")
match_df.columns = columns

hero_stats = pd.read_csv("../input/hero_stats.csv")
print(hero_stats.columns)

kz,hx,fz,ts,bf,xs,nj,tj = {},{},{},{},{},{},{},{}
for index,row in hero_stats.iterrows():
    kz[row['id']] = row['kong_zhi']
    hx[row['id']] = row['he_xin']
    fz[row['id']] = row['fu_zhu']
    ts[row['id']] = row['tao_sheng']
    bf[row['id']] = row['bao_fa']
    xs[row['id']] = row['xian_shou']
    nj[row['id']] = row['nai_jiu']
    tj[row['id']] = row['tui_jin']

for i in range(8):
    match_df['radiant_$' + str(i)] = 0
    match_df['dire_$' + str(i)] = 0

print(match_df.head(5))

j = 0
for dic in kz,hx,fz,ts,bf,xs,nj,tj:


        # 产生8*2列 夜宴天辉分别8列
        for i in range(5):
            #print(match_df['radiant_$'+str(j)])
            match_df['radiant_$'+str(j)] = match_df['radiant_$'+str(j)]+match_df["player_" + str(i + 1) + "_hero_id"].apply(lambda x: int(dic[int(x)]))

        for i in range(5,10):
            #print(match_df['dire_$' + str(j)])
            match_df['dire_$' + str(j)] = match_df['dire_$' + str(j)]+match_df["player_" + str(i + 1) + "_hero_id"].apply(lambda x: int(dic[int(x)]))
        j = j + 1
print(match_df.head(5))
#
#
match_df.to_csv("../input/temp.csv")


# with open("E://dota_prediction//Hero2vecModel-master//Hero2vecModel-master//input//id_to_heroname.json","r") as fp:
#     id2heroname = json.load(fp)
# print(id2heroname)
# print(match_df.columns)
# for col in match_df.columns:
#     if(col!="target"):
#         print(match_df[col])
#         match_df[col]  = match_df[col].apply(lambda x:id2heroname[str(x)])
#         print(match_df[col])
# match_df.to_csv("match.csv",encoding="utf8")