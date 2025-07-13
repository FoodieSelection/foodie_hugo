@echo off
rem 刪除content資料夾內除了_index.md
setlocal

set "target_folder=C:\Users\shawn\workspace\foodie_hugo\foodie-selection\content"
set "keep1=_index.md"

pushd "%target_folder%"

for %%f in (*.*) do (
    if /I not "%%f"=="%keep1%" if /I not "%%f"=="%keep2%" (
        del /f /q "%%f"
    )
)

for /d %%d in (*) do (
    rmdir /s /q "%%d"
)

popd
endlocal

rem 刪除public資料夾
rmdir /s /q "C:\Users\shawn\workspace\foodie_hugo\foodie-selection\public"

rem 執行python轉檔小程式
cd /d C:\Users\shawn\workspace\foodie_hugo\foodie-selection\scripts
py parseAward.py
py parseAllPage.py
py parseAllStore.py

pause
