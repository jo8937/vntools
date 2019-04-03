# -*- coding: utf-8 -*-

import os
import re

from EnexParser import parseNoteXML, parseNoteXMLString

#dirlist = os.listdir("source")
from EvernoteConnector import EvernoteConnector
from collections import Counter

import sys
reload(sys)  
sys.setdefaultencoding('utf8')

class Paragraph(object):
    def __init__(self):
        self.textlist = None
        self.ev = None
        pass

    def getEvernoteConnector(self):
        if self.ev is None:
            self.ev = EvernoteConnector(False)
        return self.ev

    def fromEnex(self, filepath='source/Evernote.enex'):
        self.textlist = parseNoteXML(filepath)


    def fromServer(self):
        self.textlist = []
        ev = self.getEvernoteConnector()
        notes = ev.get_note_dict_in_notebook(notebook_name="1章")
        for n in notes:
            xml = n.get("content_xml")
            txt = parseNoteXMLString(xml)
            self.textlist.extend(txt)

    def executeStats(self):
        l = []
        resultlist = []
        for t in self.textlist:
            s = Statement(t)
            if s.resourceType == "SCG":
                l.append( s.tokens )
            
        c = Counter(l)
        for k, cnt in c.most_common():
            resultline =  "-".join(k) + "\t" + str(cnt)
            resultlist.append(resultline)
            print resultline

        return resultlist

    def updateServerMetadata(self):
        resultlist = self.executeStats()
        ev = self.getEvernoteConnector()
        ev.update_note(os.getenv("EVER_NOTE_TARGET_GUID"), resultlist)

class StatScg():
    chara = ""
    cloth = ""
    emo = ""
    action = ""

    def __init__(self, tpl):
        self.chara, self.cloth, self.emo, self.action = tpl
        
class Statement(object):
    
    prefixDef = {
        "@":"SCG",
        u"＠":"SCG",
        "&":"CG",
        u"＆":"CG",
        ":":"BG",
        u"：":"BG",
        "$":"BGM",
        u"＄":"BGM",
        "#":"EFF",
        u"＃":"EFF"
    }
    resourceType = ""
    line = ""
    tokens = ""

    def __init__(self, line):
        if line is None:
            return
        self.line = line
        if line.strip().startswith(tuple([k for k in self.prefixDef])):
            self.resourceType = self.prefixDef[line[0]]
            #self.tokens = re.findall(r"[\w']+", line[1:]) # re.split(u"[ 　]+",line[1:])
            self.tokens = line[1:].replace(u"　"," ").split()
            self.tokens = tuple([ t for t in self.tokens if t.strip()])
            
      
if __name__ == '__main__':
    p = Paragraph()
    p.fromServer()
    p.updateServerMetadata()