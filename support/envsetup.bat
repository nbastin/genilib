@ECHO OFF
If DEFINED ProgramFiles(x86) Set _programs=%ProgramFiles(x86)%
If Not DEFINED ProgramFiles(x86) Set _programs=%ProgramFiles%

set PYTHONPATH=C:\Python27\Lib;C:\Python27\libs;%_programs%\omniTools-2.7;%_programs%\omniTools-2.7\Library.zip;
set PATH=%PATH%;C:\Python27;C:\Python27\Scripts
