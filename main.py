import os

from win32file import CreateFile, SetFileTime, GetFileTime, CloseHandle
from win32file import GENERIC_READ, GENERIC_WRITE, OPEN_EXISTING
from pywintypes import Time  # 可以忽视这个 Time 报错（运行程序还是没问题的）
import piexif
import datetime
import time
import re
from win32com.propsys import propsys, pscon
from pyexiv2 import Image
import shutil


def getMp4OriginTime(src):
    srcName = os.path.basename(src)
    srcName = "".join(srcName.split(".")[0:-1])

    p = re.compile("\d{13}", re.M)
    ret = p.findall(srcName)
    if ret:
        ret = ret[0]
        ts = int(ret) / 1000
        dt = datetime.datetime.fromtimestamp(ts, tz=datetime.timezone.utc)
        return dt.strftime("%Y-%m-%d %H:%M:%S")

    properties = propsys.SHGetPropertyStoreFromParsingName(src)
    dt = properties.GetValue(pscon.PKEY_Media_DateEncoded).GetValue()
    dt = dt + datetime.timedelta(hours=8)
    return dt.strftime("%Y-%m-%d %H:%M:%S")

def getImageOriginTime(src):
    srcName = os.path.basename(src)
    srcName = "".join(srcName.split(".")[0:-1])
    p = re.compile("\d{4}\d{2}\d{2}[_-]\d{6}", re.M)
    ret = p.findall(srcName)
    if ret:
        ret = ret[0]
        if '-' in ret:
            splits = ret.split('-')
        elif '_' in ret:
            splits = ret.split('_')

        t = datetime.datetime.strptime(splits[0]+" "+splits[1], "%Y%m%d %H%M%S")
        strT = t.strftime("%Y-%m-%d %H:%M:%S")
        return strT
    # 微信导出时间戳
    p = re.compile("\d{13}", re.M)
    ret = p.findall(srcName)
    if ret:
        ret = ret[0]
        ts = int(ret) / 1000
        dt = datetime.datetime.fromtimestamp(ts, tz=datetime.timezone.utc)
        return dt.strftime("%Y-%m-%d %H:%M:%S")

    try:
        img = Image(src)
        iptcDict = img.read_iptc()
        if 'Iptc.Application2.DateCreated' in iptcDict:
            fileDate = iptcDict['Iptc.Application2.DateCreated']
            fileTime = iptcDict['Iptc.Application2.TimeCreated']
            return fileDate + " " + fileTime[:8]

        exifDict = img.read_exif()
        if 'Exif.Image.DateTime' in exifDict:
            splits = exifDict['Exif.Image.DateTime'].split(" ")
            return splits[0].replace(":", "-") + " " + splits[1]
    except:
        try:
            exif_dict = piexif.load(src)
            t = exif_dict['0th'][piexif.ImageIFD.DateTime]
            return datetime.datetime.strptime(t.decode(), "%Y:%m:%d %H:%M:%S").strftime("%Y-%m-%d %H:%M:%S")
        except:
            return
    return


def modifyFileTime(filePath, createTime, modifyTime, accessTime, offset):
    """
    用来修改任意文件的相关时间属性，时间格式：YYYY-MM-DD HH:MM:SS 例如：2019-02-02 00:01:02
    :param filePath: 文件路径名
    :param createTime: 创建时间
    :param modifyTime: 修改时间
    :param accessTime: 访问时间
    :param offset: 时间偏移的秒数,tuple格式，顺序和参数时间对应
    """
    try:
        format = "%Y-%m-%d %H:%M:%S"  # 时间格式
        cTime_t = timeOffsetAndStruct(createTime, format, offset[0])
        mTime_t = timeOffsetAndStruct(modifyTime, format, offset[1])
        aTime_t = timeOffsetAndStruct(accessTime, format, offset[2])

        fh = CreateFile(filePath, GENERIC_READ | GENERIC_WRITE, 0, None, OPEN_EXISTING, 0, 0)
        createTimes, accessTimes, modifyTimes = GetFileTime(fh)

        createTimes = Time(time.mktime(cTime_t))
        accessTimes = Time(time.mktime(aTime_t))
        modifyTimes = Time(time.mktime(mTime_t))
        SetFileTime(fh, createTimes, accessTimes, modifyTimes)
        CloseHandle(fh)
        return 0
    except:
        return 1


def timeOffsetAndStruct(times, format, offset):
    return time.localtime(time.mktime(time.strptime(times, format)) + offset)

def changPhotoTime(src, photo_time):
    """
    格式：   '2024:04:22 07:58:10'
    :param src:
    :param photo_time:
    :return:
    """
    try:
        exif_dict = piexif.load(src)  # 读取现有Exif信息
        # 设置Exif信息，注意DateTime在ImageIFD里面
        photo_time = photo_time.replace("-", ":")
        exif_dict['0th'][piexif.ImageIFD.DateTime] = photo_time
        exif_dict['0th'][piexif.ImageIFD.PreviewDateTime] = photo_time
        exif_dict['Exif'][piexif.ExifIFD.DateTimeOriginal] = photo_time
        exif_dict['Exif'][piexif.ExifIFD.DateTimeDigitized] = photo_time

        if piexif.ImageIFD.DateTime in exif_dict['1st']:
            exif_dict['1st'][piexif.ImageIFD.DateTime] = photo_time
        if piexif.ImageIFD.PreviewDateTime in exif_dict['1st']:
            exif_dict['1st'][piexif.ImageIFD.PreviewDateTime] = photo_time

        try:
            exif_bytes = piexif.dump(exif_dict)
            piexif.insert(exif_bytes, src)  # 插入Exif信息
            print(f' Done, photo time has been changed to {photo_time}')
        except:
            print(f' Exif dump error')
    except:
        print(' Exif load error')

if __name__ == '__main__':
    # 需要自己配置
    # cTime = "2021-08-15 06:00:02"  # 创建时间
    offset = (0, 1, 2)  # 偏移的秒数（不知道干啥的）

    dirName = "C:\\Users\\SW164\\Desktop\\CoolApk\\"
    for root, dirs, files in os.walk(dirName):
        for f in files:
            src = dirName + f
            # src = dirName + "IMG_1115.JPG"
            print("src: " + src)
            isImage = True
            if src.lower().endswith("mp4") or src.lower().endswith("mov"):
                isImage = False

            if isImage:
                ctime = getImageOriginTime(src)
            else:
                ctime = getMp4OriginTime(src)

            if not ctime:
                continue
            print("ctime: " + ctime)

            if isImage:
                changPhotoTime(src, ctime)
            modifyFileTime(src, ctime, ctime, ctime, offset)

            # ctime = "2019-12-01 12:00:00"
            # modifyFileTime(src, ctime, ctime, ctime, offset)
            # changPhotoTime(src, ctime)

            # ------------ 人为记忆处理 -------------
            # if '2022-02-18' in ctime:
            #     shutil.move(src, dirName + "tmp\\" + f)
            #     continue

            # number = int(f.split(".")[0].split("_")[1])
            # print(number)
            # if 2229 >= number >= 2019:
            #     changPhotoTime(src, "2020-03-25 09:00:00")
            # ------------------------------------------

            # dst = dirName + ctime.replace(":", "") + "_" + f
            # os.rename(src, dst)
            # print("dst: " + dst)

            # print(getOriginTime(src))
            # t = os.stat(src).st_mtime
            # ct = datetime.datetime.fromtimestamp(t)
            # print(ct)
            # exif_dict = piexif.load(src)
            # for i in dir(piexif.ImageIFD):
            #     if "Time" in i:
            #         print(i, eval("piexif.ImageIFD." + i))
            # print("-" * 20)
            # for i in dir(piexif.ExifIFD):
            #     if "Time" in i:
            #         print(i, eval("piexif.ExifIFD." + i))
            # print("-" * 20)
            #
            # for k, v in exif_dict.items():
            #     print(k, v)
            #
            # break


