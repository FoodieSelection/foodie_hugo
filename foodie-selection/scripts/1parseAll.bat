@echo off
rem 刪除public資料夾
rmdir /s /q "C:\Users\shawn\workspace\foodie_hugo\foodie-selection\public"

rem 執行python轉檔小程式
cd /d C:\Users\shawn\workspace\foodie_hugo\foodie-selection\scripts
py parseAward.py
py parseAllPage.py
py parseAllStore.py

pause
