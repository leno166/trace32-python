/* *********************************************************************************************
 * @Title: TRACE32 Remote API that use T32_NotifyStateEnable() and T32_CheckStateNotify()
 * @Description:
 *  TRACE32 Remote API sample program illustrating the use of T32_NotifyStateEnable() and
 *  T32_CheckStateNotify() for receiving notifications from TRACE32 PowerView.
 *
 *    Syntax:   t32apinotify  [node=<name_or_IP>]  [port=<num>]
 *    Example:  t32apinotify   node=localhost       port=20000
 *
 *  For remote access TRACE32's configuration file "config.t32" has to contain these lines:
 *
 *    RCL=NETASSIST
 *    PORT=20000
 *
 *  This default port value may be changed but has to match the specified command line value.
 *
 *  ENABLE_NOTIFICATION has to be defined manually if this sample program is compiled without
 *  the provided makefile.
 *
 *
 *  $Id: t32apinotify.c 73238 2016-05-17 09:38:56Z mobermeir $
 *  $LastChangedRevision: 73238 $
 *  $LastChangedBy: mobermeir $
 *
 * @Copyright: (C) 1989-2014 Lauterbach GmbH, licensed for use with TRACE32(R) only
 * *********************************************************************************************
 * $Id: t32apinotify.c 73238 2016-05-17 09:38:56Z mobermeir $
 */

#include "t32.h"
#include <stdio.h>
#include <conio.h>
#include <string.h>
#include <stdlib.h>


static void T32_callbackEditExtern(int dummy, int lineNr, char *fileName);
static void T32_callbackBreakpointConfig(int dummy);
static void T32_callbackBreak(int dummy);
int indexOf_shift (char* base, char* str, unsigned int startIndex) {
	int result;
	unsigned int baselen = strlen(base);
		char* pos=NULL;
	// str should not longer than base
	if (strlen(str) > baselen || startIndex > baselen) {
		result = -1;
	} else {
		if (startIndex < 0 ) {
			startIndex = 0;
		}
		pos = strstr(base+startIndex, str);
		if (pos == NULL) {
			result = -1;
		} else {
			result = pos - base;
		}
	}
	return result;
}
size_t lastIndexOf (char* base, char* str) {
	size_t result;
	// str should not longer than base
	if (strlen(str) > strlen(base)) {
		result = -1;
	} else {
		unsigned int start = 0;
		unsigned int endinit = strlen(base) - strlen(str);
		unsigned int end = endinit;
		int endtmp = endinit;
		while(start != end) {
			start = indexOf_shift(base, str, start);
			end = indexOf_shift(base, str, end);

			// not found from start
			if (start == -1) {
				end = -1; // then break;
			} else if (end == -1) {
				// found from start
				// but not found from end
				// move end to middle
				if (endtmp == (start+1)) {
					end = start; // then break;
				} else {
					end = endtmp - (endtmp - start) / 2;
					if (end <= start) {
						end = start+1;
					}
					endtmp = end;
				}
			} else {
				// found from both start and end
				// move start to end and
				// move end to base - strlen(str)
				start = end;
				end = endinit;
			}
		}
		result = start;
	}
	return result;
}

int main(int argc, char **argv)
{
	char      string[32], cursor[4] = {'/','-','\\','|'};
	int       i, argn = 1, retval = EXIT_SUCCESS;
	uint32_t  result;
	size_t index = lastIndexOf(__FILE__,".");
	char  filename [100];
	if (index == -1) {
		strcpy(filename, __FILE__);
	} else {
		strncpy(filename, __FILE__, index);
	}


	/*** get command line parameters and establish connection ************************************/

	if ((argc > argn) && (!strncmp(argv[argn], "node=", 5) || !strncmp(argv[argn], "NODE=", 5))) {
		T32_Config("NODE=", argv[argn] + 5);
		argn++;
	}

	if ((argc > argn) && (!strncmp(argv[argn], "port=", 5) || !strncmp(argv[argn], "PORT=", 5))) {
		if (T32_Config("PORT=", argv[argn] + 5) != T32_OK) {
			printf("\n\n Invalid port number '%s' specified.\n", argv[argn] + 5);
			retval = EXIT_FAILURE;
		}
		argn++;
	}

	if ((argc != argn) || (retval == EXIT_FAILURE) || (argc == 1)) {
		printf("\n\n Syntax:   %s.exe  [node=<name_or_IP>]  [port=<num>]", filename);
		printf(  "\n Example:  %s.exe   node=localhost       port=20000\n\n", filename);
		if (argc != 1)
			return EXIT_FAILURE;
	}

	printf("\n Connecting...");

	for (i = 0; i < 2; i++) {  /* try twice */
		if (T32_Init() == T32_OK) {
			if (T32_Attach(T32_DEV_ICD) == T32_OK)
				break;
			else
				printf("%s to establish a remote connection with TRACE32 PowerView.%s\n",
					   i==0?"\n\n Failed once":"\n Failed twice", i==0?"\n":" Terminating ...\n");
		}
		else
			printf("%s to initialize the remote connection.%s\n",
				   i==0?"\n\n Failed once":"\n Failed twice", i==0?" ":" Terminating ...\n");

		T32_Exit(); /* reset/close a potentially existing connection */
		if (i == 1)
			return EXIT_FAILURE;
	}

	printf("\r Successfully established a remote connection with TRACE32 PowerView.\n");
	printf("\n See AREA window of TRACE32 PowerView for instructions on how to use the demo.\n");
	printf("\n Press 'q' to quit this dos shell application.\n\n");


	/*** enable notifications in TRACE32 PowerView and display all important information *********/

	T32_Cmd("WINCLEAR APIWin1"); T32_Cmd("WINCLEAR APIWin2");
	T32_Cmd("WINCLEAR APIWin3"); T32_Cmd("WINCLEAR APIWin4");
	T32_Cmd("PRINT");
	T32_Cmd("PRINT");
	T32_Cmd("SETUP.BREAKTRANSFER OFF"); /* disable former settings */
	T32_Cmd("WINPOS 0 0 48% 50% , , APIWin1");
	T32_Cmd("AREA");
	T32_Cmd("WINPOS 0 55% , , , , APIWin2");
	T32_Cmd("SYStem");
	T32_Cmd("EVAL SIMULATOR()");
	if ((T32_EvalGet(&result) == T32_OK) && (result != 0)) { /* assemble loop in case of simulator */
		T32_Cmd("SYStem.Up");
		T32_Cmd("Data.Assemble P:0x0++0x50 nop");
		T32_Cmd("EVAL CPU()");
		T32_EvalGetString(string);     /* for EVAL CPU() size of */
		if (!strncmp(string, "TC", 2)) /* string is sufficient   */
			T32_Cmd("Data.Assemble P:0x50 j 0x0");
		else
			T32_Cmd("Data.Assemble P:0x50 b 0x0");
		T32_Cmd("Register.Set PC P:0x0");
	}
	T32_Cmd("Break.Set REGISTER(PC)+0x10 REGISTER(PC)+0x20 REGISTER(PC)+0x30 REGISTER(PC)+0x40 /SOFT");
	T32_Cmd("WINPOS 50% 0 50% 60% , , APIWin3");
	T32_Cmd("Data.List");
	T32_Cmd("WINPOS 50% 70% 50% 40% , , APIWin4");
	T32_Cmd("Break.List");
	T32_Cmd("SETUP.BREAKTRANSFER ON"); /* enable 'target break' and 'breakpoint change' notification      */
	T32_Cmd("SETUP.EDITEXT ON");       /* enable 'edit source' notification, superfluous if only ASM code */

	T32_Cmd("PRINT");
	T32_Cmd("PRINT");
	T32_Cmd("PRINT \042___remote_API__notification_demo______________________\042");
	T32_Cmd("PRINT");
	T32_Cmd("PRINT \042 Remote application executed 'SETUP.BREAKTRANSFER ON'\042");
	T32_Cmd("PRINT \042 in order to enable target-break-notification and\042");
	T32_Cmd("PRINT \042 breakpoint-change-notification.\042");
	T32_Cmd("PRINT");
	T32_Cmd("PRINT \042 Press GO button to start execution, the remote\042");
	T32_Cmd("PRINT \042 application will be notified when a breakpoint\042");
	T32_Cmd("PRINT \042 is hit.\042");
	T32_Cmd("PRINT");
	T32_Cmd("PRINT \042 Change breakpoint settings in the Data.List or\042");
	T32_Cmd("PRINT \042 Break.List window, the remote application will\042");
	T32_Cmd("PRINT \042 be notified of any changes.\042");
	T32_Cmd("PRINT \042______________________________________________________\042");
	T32_Cmd("PRINT");


	/* tell TRACE32 to report user request for editing source via EDIT.EXTernal command */
	T32_NotifyStateEnable(T32_E_EDIT, (void (__cdecl *)(void)) T32_callbackEditExtern);

	/* tell TRACE32 to report changes in breakpoint configuration */
	T32_NotifyStateEnable(T32_E_BREAKPOINTCONFIG, (void (__cdecl *)(void)) T32_callbackBreakpointConfig);

	/* tell TRACE32 to report when target program stops execution */
	T32_NotifyStateEnable(T32_E_BREAK, (void (__cdecl *)(void)) T32_callbackBreak);


	i = 0;
	while (1) {
		printf("\r %c", cursor[i]);
		fflush(stdout);
		i = ++i % 4;

		/* poll for notification and invoke previously */
		/* registered callback handler if appropriate  */
		T32_CheckStateNotify(0x0 /*dummy*/);

		if(_kbhit()) {
			char ch = (char)_getch();
			if ((ch == 'q') || (ch == 'Q')) {
				printf("\r \nProgram has been terminated by pressing '%c'.\n", ch);
				break;
			}
		}

		_sleep(200);
	}


	if (T32_Exit() == T32_OK) {
		printf("\nSucceeded to close the remote connection with TRACE32 PowerView.\n\n");
		return EXIT_SUCCESS;
	}
	else {
		printf("\nFailed to close the remote connection with TRACE32 PowerView.\n\n");
		return EXIT_FAILURE;
	}
}


/* Callback handler invoked when TRACE32 reports EDIT.EXTernal command.
 * @param dummy:    unused in this sample, is taken from T32_Check StateNotify() call
 * @param lineNr:   line number for placing the cursor
 * @param fileName: name of file to edit
 */
static void T32_callbackEditExtern(int dummy, int lineNr, char *fileName)
{
	static int i = 0;

	/* application may open 3rd party editor */
	printf("\r TRACE32: EDIT.EXTern request with filename %s and line number %d.  (#%d)\n\n", fileName, lineNr, i++);

}


/* Callback handler invoked when the breakpoint configuration changes, e.g. after Break.Set command.
 * @param dummy: unused in this sample, is taken from T32_Check StateNotify() call
 */
static void T32_callbackBreakpointConfig(int dummy)
{
	static int i = 0;

	/* application may request latest breakpoint information */
	printf("\r TRACE32: breakpoint configuration has been changed.  (#%d)\n\n", i++);

}


/* Callback handler invoked when the target program stops execution, e.g. after Break command.
 * @param dummy: unused in this sample, is taken from T32_Check StateNotify() call
 */
static void T32_callbackBreak(int dummy)
{
	static int i = 0;

	/* application may trigger further actions */
	printf("\r TRACE32: execution of target program has been stopped.  (#%d)\n\n", i++);

}

