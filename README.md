# ChangeCameraTime
修改图片或者视频的摄像时间

由于换手机，照片导入到新手机时，经常导致乱序，所以有了这个python脚本。本人没研究过照片视频格式，只是为了解决我的痛点才研究了修改时间的方法。

文件格式:
iphone中的一般为IMG_xxx.jpg, 比较烦人，在拍摄日期丢失了之后，只能手动改脚本设置一个大概的时间。
三星手机一般以日期作为文件格式，可以通过正则获取。
微信导出的格式一般包含时间戳，可以通过正则获取。


文件的时间: 
1. 文件时间，包括创建时间，修改时间，访问时间
2. 照片里的exif信息里存放的拍摄时间，具体看代码
3. 照片里的iptc时间（不懂），具体看代码
4. 视频里的拍摄时间，具体看代码。由于发现视频的拍摄时间不会乱就没有去研究怎么修改视频时间，只是获取了视频时间来修改视频文件的创建时间。

由于修改文件创建时间，windows下比较方便，所以需要依赖一些windows包
依赖pip包
```
pip install pywin32
pip install pyexiv2
pip install piexif
```

参考
https://github.com/bcwyatt/change-photo-name-date-time


在研究中发现了一个java版本可以获取媒体文件时间的maven包，非常好用
https://github.com/drewnoakes/metadata-extractor
