
class SoftLanTiming:
    def __init__(self):
        # ['167=0.327', '323=0.967']
        self.timing = 0  # 323
        self.value = 0  # 0.967

    def SetSoftLan(self, t, v):
        self.timing = t
        self.value = v

    def __str__(self):
        return "timing " + str(self.timing) + "  value " + str(self.value)


class ArrowRow:
    def __init__(self):
        self.beat = 0  # 何分か　4～192
        self.arrow = [0, 0, 0, 0]  # 0なし　1通常アロー　2FA開始　3FA終わり　4SA
        self.pos = 0.0  # 位置 4分だと1.0 2.0 3.0 8分だと3.5 4.0 4.5
        self.bpm = 0.0
        self.softlan = SoftLanTiming()

    def __str__(self):
        return str(self.arrow[0]) + str(self.arrow[1]) + str(self.arrow[2]) + str(self.arrow[3]) + " " + str(
            self.beat) + "分 " + str(self.pos) + "位置 " + "bpm" + str(self.bpm) + " 停止" + str(self.softlan.value) + "\n"

    def SetArrow(self, a1, a2, a3, a4):
        self.arrow[0] = a1
        self.arrow[1] = a2
        self.arrow[2] = a3
        self.arrow[3] = a4

    def SetPos(self, p):
        self.pos = p

    def GetPos(self):
        return self.pos

    def SetBpm(self, bpm):
        self.bpm = bpm

    def GetBpm(self):
        return self.bpm

    def SetSoftlan(self, softlan):
        self.softlan = softlan

    def GetSoftlan(self):
        return self.softlan

    def HasNote(self):
        for a in self.arrow:
            if a != 0:
                return True
        return False


class SmMesure:
    arrowRow = []

    def __init__(self):
        self.arrowRow = []
        self.shockArrow = False

    def __str__(self):
        strline = ""
        for row in self.arrowRow:
            strline = strline + str(row)
        return strline

    def AddArrowRow(self, arrow):
        self.arrowRow.append(arrow)

    def GetMesureLength(self):
        return len(self.arrowRow)

    # Stream　開始ノーツ～最終ノーツまでの小節数を返す
    def GetStreamMesure(self):
        firstPos = 0
        endPos = 0
        for i, row in enumerate(self.arrowRow):
            if row.HasNote():
                firstPos = row.pos
                break
        for i, row in enumerate(reversed(self.arrowRow)):
            if row.HasNote():
                endPos = row.pos
                break
        return endPos - firstPos + 1

    def GetEndPos(self):
        endPos = 0
        for i, row in enumerate(reversed(self.arrowRow)):
            if row.HasNote():
                endPos = row.pos
                break
        return endPos

    def GetTotalTime(self):
        totalTime = 0
        endPos = self.GetEndPos()
        findFirstNote = False
        preRow = 0

        voltageTime = []
        for i, row in enumerate(self.arrowRow):
            nowBpm = row.GetBpm()
            if (not findFirstNote) and row.HasNote():
                findFirstNote = True
                preRow = row
                voltageTime.append([0, 0])
                continue
            if row.GetPos() > endPos:
                # 最終ノーツもカウント
                for j, voltage in enumerate(voltageTime):
                    if preRow.HasNote():
                        voltageTime[j][1] = voltageTime[j][1] + 1
                break
            if findFirstNote:
                time = 0
                # このノーツにたどり着いた=一つ直前のbpm時間だけ経過した
                # 4分4分で　bpm60なら　1分間に60ノーツ＝　1秒経過した
                # 4分8分なら　で　bpm60なら　1分間に60ノーツ＝　0.5秒が経過した
                noteTime = (60/preRow.GetBpm() * (row.GetPos() - preRow.GetPos()))
                # さらに停止があればその時間も加算
                stopTime = row.GetSoftlan().value
                totalTime = totalTime + (noteTime + stopTime)

                # ボルテージ（5秒間の最大ノーツ数）
                for j, voltage in enumerate(voltageTime):
                    if voltageTime[j][0] <= 5.0:
                        voltageTime[j][0] = voltageTime[j][0] + (noteTime + stopTime)
                        if row.HasNote():
                            voltageTime[j][1] = voltageTime[j][1] + 1
                if row.HasNote():
                    voltageTime.append([0, 0])

            preRow = row

        # 一番密度が高いものを返す
        maxNote = 0
        for j, voltage in enumerate(voltageTime):
            if voltageTime[j][1] > maxNote:
                maxNote = voltageTime[j][1]
        return totalTime, maxNote

    def SetShockArrowFlag(self, flag):
        self.shockArrow = flag


def CountNotes(measures, bpmList, stopList):
    totalNotes = 0
    totalAir = 0
    totalFreeze = 0
    totalShock = 0
    totalRow = 0
    nowBpm = 0
    if len(bpmList) <= 0:
        print("bpms error")

    nowBpm = bpmList[0].value
    smmesure = SmMesure()
    shockArrow = False
    for measure in measures:
        rowCount = int(len(measure) / 4)
        for i in range(rowCount):

            # 現在の小節　
            me = totalRow * 4 + (i / (rowCount / 4.0))

            # bpm変化のチェック
            for bpm in bpmList:
                if me >= bpm.timing:
                    nowBpm = bpm.value

            # ショックアローは難易度に考慮しないものとする
            if measure.find("M"):
                shockArrow = True
            measure = measure.replace("M", "0")
            # フリーズアローの長さも考慮しないものとする
            measure = measure.replace("3", "0")

            row = measure[i * 4:i * 4 + 4]
            count1 = row.count("1")
            count2 = row.count("2")
            if count1 > 0 or count2 > 0:
                totalNotes = totalNotes + 1
                if count2 > 0:
                    totalFreeze = totalFreeze + 1
                if count1 > 1 or count2 > 1:
                    totalAir = totalAir + 1

            countM = row.count("M")
            if countM > 1:
                totalShock = totalShock + 1

            arrow = ArrowRow()
            arrow.SetArrow(int(row[0]), int(row[1]), int(row[2]), int(row[3]))
            arrow.SetPos(1+me)
            arrow.SetBpm(nowBpm)

            # 停止のチェック
            if len(stopList) > 0:
                for stop in stopList:
                    if me == stop.timing:
                        arrow.SetSoftlan(stop)

            smmesure.AddArrowRow(arrow)

        totalRow = totalRow + 1

    # ショックアロー譜面
    smmesure.SetShockArrowFlag(shockArrow)

    return smmesure, totalNotes, totalAir, totalFreeze, totalShock


