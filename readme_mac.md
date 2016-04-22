Mac Build Readme
=================

准备
----
1. pip install PySide pyinstaller

2. npm install appdmg -g

方法
----
1. pyinstaller listen1.spec --clean -y

2. cd listen1/dist/Listen\ 1

2. cp -r Listen\ 1.app ../../package_resource/mac/dmg-resource/

3. cd package_resource/mac/dmg_resource

4. appdmg listen1.json ~/Desktop/listen1.dmg

5. 可以参考make.sh，把上述过程自动化

可能出现的错误
-------------
pyside dylib not found:
cd site-packges, use install_name_tool to change @rpath to current directory.

