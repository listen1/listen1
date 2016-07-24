Listen 1
==========

[![Software License](https://img.shields.io/badge/license-MIT-brightgreen.svg)](LICENSE)
[![platform](https://img.shields.io/badge/python-2.7-green.svg)]()

Listen 1 让你用一个网页就能听到多个网站的在线音乐（现已包括网易云音乐，QQ音乐，虾米音乐，豆瓣音乐）。你可以非常的简单的访问和收听在线音乐，而不用受到单个音乐网站资源不全的限制了。

它不仅能搜索多家在线音乐提供商的资源，还能方便的整理你喜欢的音乐，制作自己的歌单。尽兴的享受音乐吧！

支持浏览器：IE 11, Chrome, FireFox, Safari

* 主页：[https://github.com/listen1/listen1](https://github.com/listen1/listen1) 国内请访问[http://githublisten1.coding.me/listen1/](http://githublisten1.coding.me/listen1/)
* 联系邮箱：githublisten1@gmail.com

[![platform](http://i.imgur.com/if4CNr2.png?1)]()


安装
----
#### Windows 环境
Windows安装包（点击下载）：[listen1_windows.zip](https://github.com/listen1/listen1/releases/download/v1.0/listen1_windows_v1_0.zip)

1. 解压缩后，运行msi文件完成安装。
2. 点击桌面的Listen 1图标就会打开Listen 1的应用网页了。  

注意：可能误触发杀毒软件的警报，请忽略。

#### Mac 环境
Mac安装包（点击下载）：[listen1_mac.dmg](https://github.com/listen1/listen1/releases/download/v1.0/listen1_mac_v1_0.dmg)

1. 运行dmg文件完成安装。
2. 点击Listen 1图标就会打开Listen 1的应用网页了。

调试开发
----------
后台基于tornado开发，可以用Python环境直接运行。

1. pip环境下安装在requirements下的package

	pip install -r requirements/dev.txt

2. python app.py
3. 访问 http://localhost:8888/

打包
----
打包注意事项请参考[readme_mac.md](https://github.com/listen1/listen1/blob/master/readme_mac.md)和[readme_windows.md](https://github.com/listen1/listen1/blob/master/readme_windows.md)。

致谢
----
在开发过程中，参考了很多音乐网站API的分析代码和文章，感谢这些开发者的努力。（具体项目网址参考源码）


License
--------
MIT
