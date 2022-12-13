import os

from win32file import CreateFile, SetFileTime, GetFileTime, CloseHandle
from win32file import GENERIC_READ, GENERIC_WRITE, OPEN_EXISTING
from pywintypes import Time  # 可以忽视这个 Time 报错（运行程序还是没问题的）
import piexif
import datetime
import time
import re
from win32com.propsys import propsys, pscon
from pyexiv2 import Image
import shutil


def getMp4OriginTime(src):
    srcName = os.path.basename(src)
    srcName = "".join(srcName.split(".")[0:-1])

    p = re.compile("\d{13}", re.M)
    ret = p.findall(srcName)
    if ret:
        ret = ret[0]
        ts = int(ret) / 1000
        dt = datetime.datetime.fromtimestamp(ts, tz=datetime.timezone.utc)
        return dt.strftime("%Y-%m-%d %H:%M:%S")

    properties = propsys.SHGetPropertyStoreFromParsingName(src)
    dt = properties.GetValue(pscon.PKEY_Media_DateEncoded).GetValue()
    dt = dt + datetime.timedelta(hours=8)
    return dt.strftime("%Y-%m-%d %H:%M:%S")

def getImageOriginTime(src):
    srcName = os.path.basename(src)
    srcName = "".join(srcName.split(".")[0:-1])
    p = re.compile("\d{4}\d{2}\d{2}[_-]\d{6}", re.M)
    ret = p.findall(srcName)
    if ret:
        ret = ret[0]
        if '-' in ret:
            splits = ret.split('-')
        elif '_' in ret:
            splits = ret.split('_')

        t = datetime.datetime.strptime(splits[0]+" "+splits[1], "%Y%m%d %H%M%S")
        strT = t.strftime("%Y-%m-%d %H:%M:%S")
        return strT
    # 微信导出时间戳
    p = re.compile("\d{13}", re.M)
    ret = p.findall(srcName)
    if ret:
        ret = ret[0]
        ts = int(ret) / 1000
        dt = datetime.datetime.fromtimestamp(ts, tz=datetime.timezone.utc)
        return dt.strftime("%Y-%m-%d %H:%M:%S")

    try:
        img = Image(src)
        iptcDict = img.read_iptc()
        if 'Iptc.Application2.DateCreated' in iptcDict:
            fileDate = iptcDict['Iptc.Application2.DateCreated']
            fileTime = iptcDict['Iptc.Application2.TimeCreated']
            return fileDate + " " + fileTime[:8]

        exifDict = img.read_exif()
        if 'Exif.Ima
