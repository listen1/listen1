
rm ./media/temp/*
rm -rf ./media/music/*
rm ./media/user/*
rm -rf ./build ./dist
rm -rf ../package_resource/mac/dmg-resource/Listen\ 1.app 

pyinstaller listen1.spec --clean -y

cp -r ./dist/Listen\ 1.app ../package_resource/mac/dmg-resource/

cd ../package_resource/mac/dmg-resource/

rm ../../../dist/listen1_mac.dmg
appdmg listen1.json ../../../dist/listen1_mac.dmg
rm -rf ./Listen\ 1.app
