echo off
set NPSS_CONFIG=nt
set NPSS_TOP=C:\NPSS.nt.V165-OPT-Full
set NPSS_DEV_TOP=%NPSS_TOP%\DLMdevkit
set NPSS_TEST_TOP=%NPSS_TOP%\Test
set VBS_HOME=%NPSS_TOP%\VBS
set MICODIR=%NPSS_TOP%
set DCLOD_PATH=%NPSS_TOP%\DLMComponents\nt

set $Model=%CD%

"%NPSS_TOP%\bin\npss.nt.exe" -I . -I "%$Model%\inp" -I "%$Model%\src" -I "%$Model%\view" -I "%$Model%\condor" -I "%$Model%\wrapper" -I "%$Model%\run" -I "%NPSS_TOP%\InterpIncludes" -I "%NPSS_TOP%\MetaData" -I "%NPSS_TOP%\DLMComponents\nt" -I "%NPSS_TOP%\InterpComponents" -I "%NPSS_TOP%\WATEwrapper" -I "%$Model%\inp" -I "%$Model%\src" -I "%$Model%\view" -I "%$Model%\condor" -I "%$Model%\wrapper" -I "%$Model%\run" %* 

:: Run MATLAB Executable to reformat the engine deck
set "INPUT=C:\Users\cchurko3\OneDrive - Georgia Institute of Technology\Desktop\AE8900_Project\AE8900_NPSS_Release1\engine_deck.csv"
"C:\Users\cchurko3\OneDrive - Georgia Institute of Technology\Desktop\AE8900_Project\AE8900_NPSS_Release1\scripts\ParseEngineDeck.exe" "%INPUT%"