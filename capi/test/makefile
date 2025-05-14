
#
#      NMAKE makefile for building TRACE32 Remote API sample programs
#
#                 Please use Microsoft Visual Studio NMAKE
#
#  Select e.g. "Start > All Programs > Microsoft Visual Studio 2010 > Visual Studio Tools >
#  Visual Studio Command Prompt(2010)" in order to open a shell for compiling the various
#  demo applications. Recommended lib for linking: \Microsoft SDKs\Windows\v7.0A\Lib\User32.Lib
#
#
#  $Id: makefile 88205 2017-08-30 09:16:10Z fsirl $
#  $LastChangedRevision: 88205 $
#  $LastChangedBy: fsirl $
#
#  (c) Lauterbach GmbH
#


!IF DEFINED(PLATFORM)
!ERROR 64bit Visual Studio Command Shell cannot be used for building demo executables, please use 32bit Visual Studio Command Shell
!ENDIF

!IF EXIST(release)||EXIST(debug)
CLEAN = rd /S /Q
!IF EXIST(release)
CLEAN = $(CLEAN) release
!ENDIF
!IF EXIST(debug)
CLEAN = $(CLEAN) debug
!ENDIF
!ELSE
CLEAN =	@echo nothing to clean
!ENDIF

!IFDEF DEBUG
OF     = debug
CFLAGS = /Od /Zi /Fd"$(OF)\vc80.pdb" /DDEBUG
LFLAGS = /subsystem:CONSOLE,5.00 /DEBUG
!ELSE
OF     = release
CFLAGS = /Gd /Ot
LFLAGS = /subsystem:CONSOLE,5.00
!ENDIF

CC         = cl /c /Gs /w44996 /W3 -I"../src"
APITARGETS = t32apicmd.exe t32apinotify.exe t32apimenu.exe t32fdxhost.exe
SEARCH     = {.;..\src}

help:
	@echo.
	@echo. nmake help ... show this help
	@echo.
	@echo. nmake all .... same as "nmake rel"
	@echo.
	@echo. nmake clean .. delete working directories .\release\ and .\debug\
	@echo.
	@echo.

clean:
	$(CLEAN)

all:    $(APITARGETS:.exe=) t32dllmenu

rel:    all

dbg:
	nmake DEBUG=1 /NOLOGO all

$(OF):
	md $@

$(APITARGETS:.exe=) t32dllmenu:  $(OF) $(@B).exe
	copy $(OF)\$(@B).exe $(@B).exe

$(APITARGETS):   $(OF)\$(@B).obj $(OF)\hremote.obj $(OF)\hlinknet.obj
	link  $(LFLAGS) /out:"$(OF)\$@" $** ws2_32.lib

t32dllmenu.exe:  $(OF)\$(@B).obj
	link  $(LFLAGS) /out:"$(OF)\$@" $**

$(OF)\t32apicmd.obj $(OF)\t32fdxhost.obj: $(@B).c $(SEARCH)t32.h makefile
	$(CC) $(CFLAGS) /Fo$@ %s

$(OF)\t32apimenu.obj: t32apidllmenu.c  $(SEARCH)t32.h makefile
	$(CC) $(CFLAGS) /Fo$@ %s

$(OF)\t32dllmenu.obj: t32apidllmenu.c  $(SEARCH)t32.h makefile
	$(CC) $(CFLAGS) /Fo$@ %s -DUSEDLL

$(OF)\t32apinotify.obj:        $(@B).c $(SEARCH)t32.h makefile
	$(CC) $(CFLAGS) /Fo$@ %s -DENABLE_NOTIFICATION

$(OF)\hremote.obj:    $(SEARCH)$(@B).c $(SEARCH)t32.h makefile
	$(CC) $(CFLAGS) /Fo$@ %s -DENABLE_NOTIFICATION

$(OF)\hlinknet.obj:   $(SEARCH)$(@B).c $(SEARCH)t32.h makefile
	$(CC) $(CFLAGS) /Fo$@ %s

