'''

Input: Text file: ex:textDb.txt
   Unit Inventory file: ex: kkkunitdb20

   Textname='SmalltextDb' : text 파일 ( 인터넷 한글 감의 text 파일)

   decodedTextFile = ' DeStextDb'

Process: Segmentation of Text file using Unit Inventory file


Output:
         Output decodedTextFile


'''
import os
import json

os.getcwd()

class wpm_decoder:
    unitDB = {}
    bSylNum = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
    oSylNum = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]

    def __init__(self, file):
        self.loadUnitDict(file)

        ''' Find Max bSylNum in the initial stage'''
        maxz = 0
        minz = len(self.unitDB)
        for lkey in self.unitDB:
            z = self.findUnitLen(lkey)
            self.oSylNum[z] += self.unitDB[lkey]
            if (z > maxz):
                maxz = z
            if (z < minz):
                minz = z
            if (self.unitDB[lkey] > self.bSylNum[z]):
                self.bSylNum[z] = self.unitDB[lkey]
        print(self.bSylNum)
        z = 0
        while z < maxz:
            self.bSylNum[z + 1] = 2 * (self.bSylNum[z + 1] + self.bSylNum[z])
            z += 1
        ''' Size of unitDB '''
        tcnt = 0
        for lkey in self.unitDB:
            tcnt += self.unitDB[lkey]
        print(' All Tokens in unitDB =', tcnt, ' Unique token=', len(self.unitDB), '\n')

        ''' Reading Basic unit DB obtained during previous iteration'''
        print(' minz=', minz, ' maxz=', maxz, ' bSylNum=', self.bSylNum)

    def findUnitLen(self, list):
        z = len(list)
        lcnt = 0
        if (list[0] == '_'):
            lcnt = 1
        if (list[z - 1] == '_'):
            lcnt += 1
        return z - lcnt


    def Dist(self, list):
        z = self.unitDB.get(list)
        if z == None:
            z1 = 0
        else:
            len = self.findUnitLen(list)
            z1 = z + self.bSylNum[len - 1]
            '''
            if (bSylNum[len-1] > 0 ):
               print(' List=', list, z, bSylNum[len-1] )'''

        '''print( list,'unitDB.get=',z1)'''
        return z1


    def SegUnit(self, phrase):
        ''' insert _ before unit, add _ after unit '''
        count = 0
        LastCount = len(phrase)
        L = []
        while count < LastCount:
            if count == 0:
                token = '_' + phrase[count]
                ''' One Syllable '''
                if count == LastCount - 1: token = token + '_'
            elif count == LastCount - 1:
                token = phrase[count] + '_'
            else:
                token = phrase[count]
            L.append(token)
            '''print (token)'''
            count += 1
        '''print( phrase, len(phrase) ,L)'''
        ''' 0 th Optimal Path  from L[] = [ '_이' '젠_' ]
        '''
        OLP = []
        OLV = []
        OLBP = []
        RLP = []
        ''' for cnt=0 '''
        OLP.append(L[0])
        OLV.append(self.Dist(L[0]))
        OLBP.append(-1)
        '''print(len(L))'''
        cnt = 1
        lastCnt = len(L)
        '''print('LastCnt=',lastCnt,end='\n')'''
        ''' Find Optimal path for each cnt '''
        flag = 1
        while cnt < lastCnt:
            ''' Find optmal path for cnt '''
            tmppath = L[cnt]
            tmpval = OLV[cnt - 1] + self.Dist(L[cnt])
            tmpbp = cnt - 1
            '''print( 'cnt=',cnt,'tmppath=',tmppath,tmpval, tmpbp,end='\n')'''
            ''' Find Max Dist from intial unit to cnt units '''
            lcnt = cnt
            lpath = L[cnt]
            '''print(' ltmpath=',L[cnt],lpath)'''
            while lcnt > 0:
                lpath = L[lcnt - 1] + lpath
                '''print(' lpath=',lpath)'''
                if lcnt == 1:
                    newval = self.Dist(lpath)
                    if (newval > tmpval):
                        '''print('Changed tmpval from ',tmpval,' To ',newval,'path=',lpath,end='\n')'''
                        tmpval = newval
                        tmppath = lpath
                        tmpbp = -1
                        '''Change OLP, OLV list '''
                else:
                    newval = OLV[lcnt - 2] + self.Dist(lpath)
                    '''print(' lcnt=',lcnt,'lpaht=',lpath)'''
                    if newval > tmpval:
                        '''print(' newval',newval,tmpval,'lpath=',lpath,lcnt-2)'''
                        tmpval = newval
                        tmppath = lpath
                        tmpbp = lcnt - 2
                lcnt -= 1

                ''' adding tmppath to OLP '''
            OLP.append(tmppath)
            OLV.append(tmpval)
            OLBP.append(tmpbp)
            cnt += 1

        lcnt = cnt - 1
        '''print(' OLP[',lcnt,'] val=',OLV[lcnt], OLP[lcnt])'''
        RLP = []
        while lcnt > -1:
            bcnt = OLBP[lcnt]
            if bcnt < 0:
                difval = OLV[lcnt]
            else:
                difval = OLV[lcnt] - OLV[bcnt]
            '''print(' OLP[',lcnt,'] val=', difval, 'path:', OLP[lcnt], 'bp=',bcnt)'''
            RLP = [OLP[lcnt]] + RLP
            lcnt = OLBP[lcnt]

        '''if flag==1 :
           lcnt=cnt-1
           print(' OLP[',lcnt,'] val=',OLV[lcnt], OLP[lcnt])
           RLP = []
           print ( ' OLP ', OLV )
           while lcnt > -1 :
              bcnt = OLBP[lcnt]
              if bcnt < 0:
                 difval = OLV[lcnt]
              else:
                 difval = OLV[lcnt] - OLV[bcnt]
              print(' OLP[',lcnt,'] val=', difval, 'path:', OLP[lcnt], 'bp=',bcnt)
              RLP = [OLP[lcnt]] + RLP
              lcnt = OLBP[lcnt]
           print ( ' Final Result ', OLP, RLP )'''

        return RLP

    def loadUnitDict(self, file):
        with open(file, 'r', encoding='utf-8') as myUnitDB:
            self.unitDB = json.load(myUnitDB)

        print('Reading unitDB=', file)

    def decode(self, seg):
        ''' dictionary for two units to be merged in the next step'''
        mdic = {}
        cnt = 0
        OLP = []

        each_line = seg

        odata = []

        unit = each_line.strip().split()
        '''print (unit,end='\n')'''
        for phrase in unit:
            OLP = self.SegUnit(phrase)
            for token in OLP:
                odata.append(token)

        return ' '.join(odata)

if __name__ == '__main__':
    wpm = wpm_decoder('textTrainAllSystemUnitDB1315v2.json')

    text = '내일 12시에 산책가기일정을 등록해줘'
    result = wpm.decode(text)
    print(result)

    text = '생애 등 보험상품의 청약을 위하여 음성녹음을 통해 자필서명을 포함해서 계약서 작성을 대신해서 녹음을 시작하겠습니다.'
    result = wpm.decode(text)
    print(result)

