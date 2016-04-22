Windows Build Readme
=====================

准备
-----
1. 包含pyinstaller和PySide的pip环境

2. wix （windows打包工具）


方法
-----
1. 用pyinstaller生成dist文件

2. 用heat命令对dist下的文件生成wix的fragment文件
heat dir "Listen 1" -cg "projectFiles" -ag -out projectFiles.wxs 

3. 修改生成projectFiles.wxs里的安装路径，把TARGETDIR替换为实际目录，比如ProgramFilesFolder
move projectFiles.wxs ./Listen 1

4. candle编译wxs
candle.exe listen1.wxs
candle.exe projectFiles.wxs

4. light编译wxobj
light.exe listen1.wixobj projectFiles.wixobj -o c:\listen1.msi


注意事项
--------

1. 避免在有中文的路径下运行，可能导致文件找不到

