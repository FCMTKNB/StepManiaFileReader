
import re
import ReadSmFile
from pathlib import Path
import csv
import pprint

p = Path("SongsTest")
smList = list(p.glob("**/*.sm"))

mapDataList = []
for sm in smList:
    data = ReadSmFile.CountNotes(sm)
    mapDataList.extend(data)
    # print(data)

with open('AllSmSong.csv', 'w') as f:
    writer = csv.DictWriter(f, ['SongName', 'DifficultRank', 'DifficultValue',
                                'totalNotes', 'totalTime',
                                'AverageNotes', 'VoltageNotes'])
    writer.writeheader()
    for mapData in mapDataList:
        print(mapData)
        writer.writerow(mapData)