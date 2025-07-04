@echo off
rem 執行hugo server
cd /d "C:\Users\shawn\workspace\foodie_hugo\foodie-selection"
hugo

rem 移除github資料夾內資料
setlocal

set "target_folder=C:\Users\shawn\workspace\FoodieSelection.github.io"
set "keep1=CNAME"

pushd "%target_folder%"

for %%f in (*.*) do (
    if /I not "%%f"=="%keep1%" (
        del /f /q "%%f"
    )
)

for /d %%d in (*) do (
    if /I not "%%d"==".git" (
        rmdir /s /q "%%d"
    )
)

popd
endlocal

rem 把public資料移到github資料夾
robocopy "C:\Users\shawn\workspace\foodie_hugo\foodie-selection\public" "C:\Users\shawn\workspace\FoodieSelection.github.io" /MOVE /E

pause