
import re
import ReadSmFileSub


def CountNotes(filename):
    f = open(filename, 'r', encoding="utf-8")
    data1 = f.read()  # ファイル終端まで全て読んだデータを返す
    f.close()

    # コメント以降を削除
    pattern = "//.*(\r\n|\r|\n)"
    data1 = re.sub(pattern, "", data1)

    # 全改行を削除。これにより、1小節(4分*4つ)を1行にする
    # 0001 → 0001100000011000
    # 1000
    # 0001
    # 1000
    data1 = data1.replace('\n', '')
    data1 = data1.replace('\r', '')
    tags = data1.split(';')

    # 曲名だけはupper掛けれないので、回して処理する
    # title = [s for s in tags if '#TITLE:' in s][0].split(":")[1]
    # なぜかこの構文だと、大文字小文字が混じるとOutRangeになる
    for tag in tags:
        tag.strip()  # 無駄なスペースとか取り除く
        index = tag.find(':')
        if index == -1:
            continue
        strLeft = tag[0:index + 1]  # #TITLE:
        strRight = tag[index + 1:len(tag)]  # ex)TestSong
        strLeft = strLeft.upper()
        if '#TITLE:' in strLeft:
            songName = strRight
            break

    # リスト要素すべてにアッパー
    tags = [tag.upper() for tag in tags]

    # BPM変化を取得し、管理クラスに詰める
    bpms = [s for s in tags if '#BPMS:' in s][0].split(":")[1].split(",")
    bpmList = []
    for bpm in bpms:
        softlan = ReadSmFileSub.SoftLanTiming()
        bpmData = bpm.split("=")
        softlan.SetSoftLan(float(bpmData[0]), float(bpmData[1]))
        bpmList.append(softlan)

    # 停止を取得し、管理クラスに詰める
    # 停止は記述されていない場合があるので空チェックをする
    stopWrk2 = [s for s in tags if '#STOPS:' in s]
    stopList = []
    if len(stopWrk2) > 0:
        stopsWrk = stopWrk2[0].split(":")
        if len(stopsWrk[1]) > 0:
            stops = stopsWrk[1].split(",")
            for stop in stops:
                softlan = ReadSmFileSub.SoftLanTiming()
                stopData = stop.split("=")
                softlan.SetSoftLan(float(stopData[0]), float(stopData[1]))
                stopList.append(softlan)

    notes = [s for s in tags if '#NOTES:' in s]

    print(filename)
    returnData = []
    for note in notes:
        humenData = note.split(":")
        # print(humenData[0]) # notes
        # print(humenData[1]) # dance-single or dance-double

        # シングルのみ対応
        if "SINGLE" not in humenData[1]:
            continue
        # print(humenData[2]) # ?
        humenData[3] = humenData[3].strip()
        # print(humenData[3])  # beginner easy medium hard challenge
        humenData[4] = humenData[4].strip()
        # print(humenData[4]) # diffValue
        # print(humenData[5]) # guage
        # print(humenData[6]) # notes
        measures = humenData[6].split(",")
        # 空白削除
        for i, me in enumerate(measures):
            measures[i] = measures[i].replace(" ", "")

        measure, totalNotes, totalAir, totalFreeze, totalShock = ReadSmFileSub.CountNotes(measures, bpmList, stopList)
        totalTime, voltage = measure.GetTotalTime()

        mapData = {"SongName": songName}
        diffStr = "none"
        diffRank = humenData[3].upper()
        if diffRank == "BEGINNER":
            diffStr = "習"
        elif diffRank == "EASY":
            diffStr = "楽"
        elif diffRank == "MEDIUM":
            diffStr = "踊"
        elif diffRank == "HARD":
            diffStr = "激"
        elif diffRank == "CHALLENGE":
            diffStr = "鬼"
        # 難易度
        mapData["DifficultRank"] = diffStr
        # 難易度(数値)
        mapData["DifficultValue"] = humenData[4]
        # ノーツ数
        mapData["totalNotes"] = totalNotes
        # 開始ノーツから最終ノーツまでの時間（フリーズアローの終点は含めない）
        mapData["totalTime"] = totalTime
        # 1秒間の平均ノーツ数
        mapData["AverageNotes"] = totalNotes / totalTime
        # 一番密度が高い5秒間での、ノーツ数
        mapData["VoltageNotes"] = voltage
        returnData.append(mapData)

    return returnData


