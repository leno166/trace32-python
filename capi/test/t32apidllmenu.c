/* **********************************************************************************************
 * @Title: TRACE32 Remote API sample program illustrating the use of various API functions.
 * @Description:
 *   After establishing a remote connection with TRACE32 PowerView a menu offers various
 *   API commands for selection. For accessing real HW the data memory location can be
 *   specified by <hexaddr>.
 *
 *    Syntax:   t32apimenu  [node=<name_or_IP>]  [port=<num>]  [<hexaddr>]
 *    Example:  t32apimenu   node=localhost       port=20000    0x400C000
 *
 *  For remote access TRACE32's configuration file "config.t32" has to contain these lines:
 *
 *    RCL=NETASSIST
 *    PORT=20000
 *
 *  This default port value may be changed but has to match the specified command line value.
 *
 *
 *  $Id: t32apidllmenu.c 76425 2016-08-25 15:01:51Z mzens $
 *  $LastChangedRevision: 76425 $
 *  $LastChangedBy: mzens $
 *
 * @Copyright: (C) 1989-2014 Lauterbach GmbH, licensed for use with TRACE32(R) only
 * *********************************************************************************************
 * $Id: t32apidllmenu.c 76425 2016-08-25 15:01:51Z mzens $
 */

# include "t32.h"
# include <stdio.h>
# include <conio.h>

#ifdef USEDLL
# include <windows.h>
# define  PROGNAME  "t32dllmenu"
#else
# include <string.h>
# include <stdlib.h>
# define  PROGNAME  "t32apimenu"
#endif


int main(int argc, char **argv)
{
	uint32_t  wpbuffer[256] = {0xcafefeca}, rwbuffer[2] = {0xcafefeca, 0xbabebeba};
	uint32_t  m = 0, ui32val[8], address = 0xffffffff, pcval = 0xffffffff;
	uint16_t  ui16val[32];
	int       i, j = 1, k, argn = 1, retval = EXIT_SUCCESS, systemstate;
	char      *endptr, sel[3] = "  ", string[25] = "Data.DUMP D:0x1000      ";

#ifdef USEDLL
	HMODULE   hdll;
	int (*T32_Config)          (const char*, const char*);
	int (*T32_Init)            (void);
	int (*T32_Attach)          (int);
	int (*T32_Terminate)       (int);
	int (*T32_Exit)            (void);
	int (*T32_Ping)            (void);
	int (*T32_Nop)             (void);
	int (*T32_NopFail)         (void);
	int (*T32_Cmd)             (const char*);
	int (*T32_Stop)            (void);
	int (*T32_EvalGet)         (uint32_t*);
	int (*T32_EvalGetString)   (char*);
	int (*T32_Go)              (void);
	int (*T32_Break)           (void);
	int (*T32_Step)            (void);
	int (*T32_ResetCPU)        (void);
	int (*T32_GetState)        (int*);
	int (*T32_ReadMemory)      (uint32_t, int, uint8_t*, int);
	int (*T32_WriteMemory)     (uint32_t, int, uint8_t*, int);
	int (*T32_WriteMemoryPipe) (uint32_t, int, uint8_t*, int);
	int (*T32_ReadPP)          (uint32_t*);
	int (*T32_ReadRegister)    (uint32_t, uint32_t, uint32_t*);
	int (*T32_WriteRegister)   (uint32_t, uint32_t, uint32_t*);
	int (*T32_ReadBreakpoint)  (uint32_t, int, uint16_t*, int);
	int (*T32_WriteBreakpoint) (uint32_t, int, int,       int);
	int (*T32_GetTraceState)   (int, int*, int32_t*, int32_t*, int32_t*);
	int (*T32_ReadTrace)       (int, int32_t, int, uint32_t, uint8_t*);
	int (*T32_TAPAccessShiftIR)(void*, int, const uint8_t*, uint8_t*);


	if (((hdll = LoadLibrary("../dll/t32api.dll")) == NULL) && ((hdll = LoadLibrary("t32api.dll")) == NULL)) {
		printf("Failed to load library 't32api.dll', the library might be missing or erroneous.\n");
		return EXIT_FAILURE;
	}

	T32_Config           = (int (__cdecl *)(const char*, const char*)     )GetProcAddress(hdll, "T32_Config");
	T32_Init             = (int (__cdecl *)(void)                         )GetProcAddress(hdll, "T32_Init");
	T32_Attach           = (int (__cdecl *)(int)                          )GetProcAddress(hdll, "T32_Attach");
	T32_Terminate        = (int (__cdecl *)(int)                          )GetProcAddress(hdll, "T32_Terminate");
	T32_Exit             = (int (__cdecl *)(void)                         )GetProcAddress(hdll, "T32_Exit");
	T32_Ping             = (int (__cdecl *)(void)                         )GetProcAddress(hdll, "T32_Ping");
	T32_Nop              = (int (__cdecl *)(void)                         )GetProcAddress(hdll, "T32_Nop");
	T32_NopFail          = (int (__cdecl *)(void)                         )GetProcAddress(hdll, "T32_NopFail");
	T32_Cmd              = (int (__cdecl *)(const char*)                  )GetProcAddress(hdll, "T32_Cmd");
	T32_Stop             = (int (__cdecl *)(void)                         )GetProcAddress(hdll, "T32_Stop");
	T32_EvalGet          = (int (__cdecl *)(uint32_t*)                    )GetProcAddress(hdll, "T32_EvalGet");
	T32_EvalGetString    = (int (__cdecl *)(char*)                        )GetProcAddress(hdll, "T32_EvalGetString");
	T32_Go               = (int (__cdecl *)(void)                         )GetProcAddress(hdll, "T32_Go");
	T32_Break            = (int (__cdecl *)(void)                         )GetProcAddress(hdll, "T32_Break");
	T32_Step             = (int (__cdecl *)(void)                         )GetProcAddress(hdll, "T32_Step");
	T32_ResetCPU         = (int (__cdecl *)(void)                         )GetProcAddress(hdll, "T32_ResetCPU");
	T32_GetState         = (int (__cdecl *)(int*)                         )GetProcAddress(hdll, "T32_GetState");
	T32_ReadMemory       = (int (__cdecl *)(uint32_t, int, uint8_t*, int) )GetProcAddress(hdll, "T32_ReadMemory");
	T32_WriteMemory      = (int (__cdecl *)(uint32_t, int, uint8_t*, int) )GetProcAddress(hdll, "T32_WriteMemory");
	T32_WriteMemoryPipe  = (int (__cdecl *)(uint32_t, int, uint8_t*, int) )GetProcAddress(hdll, "T32_WriteMemoryPipe");
	T32_ReadPP           = (int (__cdecl *)(uint32_t*)                    )GetProcAddress(hdll, "T32_ReadPP");
	T32_ReadRegister     = (int (__cdecl *)(uint32_t, uint32_t, uint32_t*))GetProcAddress(hdll, "T32_ReadRegister");
	T32_WriteRegister    = (int (__cdecl *)(uint32_t, uint32_t, uint32_t*))GetProcAddress(hdll, "T32_WriteRegister");
	T32_ReadBreakpoint   = (int (__cdecl *)(uint32_t, int, uint16_t*, int))GetProcAddress(hdll, "T32_ReadBreakpoint");
	T32_WriteBreakpoint  = (int (__cdecl *)(uint32_t, int, int,       int))GetProcAddress(hdll, "T32_WriteBreakpoint");
	T32_GetTraceState    = (int (__cdecl *)(int,int*,int32_t*,int32_t*,int32_t*))GetProcAddress(hdll,"T32_GetTraceState");
	T32_ReadTrace        = (int (__cdecl *)(int,int32_t,int,uint32_t,uint8_t*))GetProcAddress(hdll,"T32_ReadTrace");
	T32_TAPAccessShiftIR = (int (__cdecl *)(void*, int, const uint8_t*, uint8_t*))GetProcAddress(hdll,"T32_TAPAccessShiftIR");

	if ((T32_Config == NULL)||(T32_Init  == NULL)||(T32_Attach  == NULL)||(T32_Terminate     == NULL)||
		(T32_Exit   == NULL)||(T32_Ping  == NULL)||(T32_Nop     == NULL)||(T32_NopFail       == NULL)||
		(T32_Cmd    == NULL)||(T32_Stop  == NULL)||(T32_EvalGet == NULL)||(T32_EvalGetString == NULL)||
		(T32_Go     == NULL)||(T32_Break == NULL)||(T32_Step    == NULL)||(T32_ResetCPU      == NULL)||
		(T32_GetState        == NULL)||(T32_ReadMemory      == NULL)||(T32_WriteMemory       == NULL)||
		(T32_WriteMemoryPipe == NULL)||(T32_ReadPP          == NULL)||(T32_ReadRegister      == NULL)||
		(T32_WriteRegister   == NULL)||(T32_ReadBreakpoint  == NULL)||(T32_WriteBreakpoint   == NULL)||
		(T32_GetTraceState   == NULL)||(T32_ReadTrace       == NULL)||(T32_TAPAccessShiftIR  == NULL)  ) {
		printf("\n\n Failure, one or more functions of recently loaded library 't32api.dll' are missing.\n");
		if (FreeLibrary(hdll))
			printf(" The library 't32api.dll' was successfully unloaded.\n");
		else
			printf(" Failed to unloaded the library 't32api.dll'.\n");
		return EXIT_FAILURE;
	}
#endif


	/*** get command line parameters and establish connection *******************************/

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

	if ((argc > argn) && !strncmp(argv[argn], "0x", 2)) {
		address = strtoul(argv[argn], &endptr, 16);
		if ((*endptr == 0) && (strlen(argv[argn]) <= 10)) {
			string[12] = 0;
			strcat_s(string, 25, argv[argn]);
		}
		else {
			printf("\n\n Invalid hexaddress '%s' specified.\n", argv[argn]);
			retval = EXIT_FAILURE;
		}
		argn++;
	}

	if ((argc != argn) || (retval == EXIT_FAILURE) || (argc == 1)) {
		printf("\n\n Syntax:  %s [node=<name_or_IP>] [port=<num>] [<hexaddr>]",  PROGNAME);
		printf(  "\n Example: %s  node=localhost      port=20000   0x400C000\n", PROGNAME);
		printf(  "\n Hexaddress is used by Read/WriteMemory if real hardware is accessed.\n");
		if (argc != 1)
			return EXIT_FAILURE;
	}

	printf("\n\n Connecting...");

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

	printf("\r Successfully established a remote connection with TRACE32 PowerView.");


	/*** setup TRACE32 PowerView in order to display all important information **************/

	T32_Cmd("WINCLEAR APIWin1"); T32_Cmd("WINCLEAR APIWin2");
	T32_Cmd("WINCLEAR APIWin3"); T32_Cmd("WINCLEAR APIWin4");
	T32_Cmd("WINCLEAR APIWin5"); T32_Cmd("WINCLEAR APIWin6");
	T32_Cmd("PRINT");
	T32_Cmd("PRINT");
	T32_Cmd("WINPOS 0 15% , , , , APIWin1");
	T32_Cmd("SYStem");
	T32_Cmd("WINPOS 0 0 40% 35% , , APIWin2");
	T32_Cmd("AREA");
	T32_Cmd("WINPOS 0 60% 40% 45% , , APIWin3");
	T32_Cmd("Register /SpotLight");
	T32_Cmd("EVAL SIMULATOR()");
	retval = T32_EvalGet(ui32val);
	if ((retval != T32_OK) || (ui32val[0] == 0)) {    /* marginal setup in case of */
		T32_Cmd("WINPOS 40% 0 60% 40% , , APIWin4");  /* real HW or eval-failure   */
		T32_Cmd("Data.List");
		T32_Cmd("WINPOS 40% 40% 60% 40% , , APIWin5");
		T32_Cmd(string);
		if (address == 0xffffffff) {
			T32_Cmd("PRINT \042Real hardware is accessed but no address\042");
			T32_Cmd("PRINT \042for data access has been specified,\042");
			T32_Cmd("PRINT \042Read/WriteMemory will access D:0x1000\042");
			T32_Cmd("PRINT");
			printf("\n\n\n Real hardware is accessed but no address for data access\n");
			printf(" has been specified, Read/WriteMemory will access D:0x1000\n");
			address = 0x1000;
		}
	}
	else {
		T32_Cmd("SYStem.Up");
		T32_Cmd("Data.Assemble P:0x0++0x40 nop");
		T32_Cmd("EVAL CPU()");     /* for EVAL CPU() size of */
		T32_EvalGetString(string); /* string is sufficient   */
		if (!strncmp(string, "TC", 2))
			T32_Cmd("Data.Assemble P:0x40 j 0x0");
		else
			T32_Cmd("Data.Assemble P:0x40 b 0x0");
		T32_Cmd("Register.Set PC P:0x0");
		T32_Cmd("WINPOS 40% 0 60% 40% , , APIWin4");
		T32_Cmd("Data.List");
		T32_Cmd("WINPOS 40% 40% 60% 40% , , APIWin5");
		T32_Cmd("Data.Dump D:0x1000");
		address = 0x1000;
	}
	T32_Cmd("WINPOS 40% 75% 60% 25% , , APIWin6");
	T32_Cmd("Break.List");


	/*** select and execute remote API function ****************************************/

	while (1) {

		printf("\n\n Please select an action or exit with 'q':\n\n");
		printf(" p Ping          rm ReadMemory           d do test.cmm\n");
		printf(" s Step          wm WriteMemory          S Stop script\n");
		printf(" g Go            wp WritePipelined       x TestSequence\n");
		printf(" b Break         rr ReadRegister         j JtagTapAccess\n");
		printf(" c CpuState      wr WriteRegister        T TraceData\n");
		printf(" R Reset         rb ReadBreakpoint       i IntegratorData\n");
		printf(" n Nop           wb WriteBreakpoint\n");
		printf(" f NopFail       rp ReadProgCounter      t TerminateTRACE32\n\n");

		i = 0; k = 0;
		sel[0] = 0; sel[1] = 0;
		while ((sel[0] == 0) || (((sel[0] == 'r') || (sel[0] == 'w')) && (sel[1] == 0))) {
			printf("\r >%s%s", sel, i++%4<2 ? "_" : " ");
			fflush(stdout);
			_sleep(250);
			if(_kbhit())
				sel[k++] = (char)_getch();
		}
		printf("\r >%s", sel);
		if ((sel[0] == 'q') || (sel[0] == 'Q')) {
			printf("\n\n Program has been terminated by pressing '%c'.\n", sel[0]);
			break;
		}

		retval = T32_OK;
		switch (sel[0]) {
			case 'p': retval = T32_Ping();             break;
			case 's': retval = T32_Step();             break;
			case 'g': retval = T32_Go();               break;
			case 'b': retval = T32_Break();            break;
			case 'R': retval = T32_ResetCPU();         break;
			case 'n': retval = T32_Nop();              break;
			case 'f':          T32_NopFail();          break;
			case 'd': retval = T32_Cmd("do test.cmm"); break;
			case 'S': retval = T32_Stop();             break;
			case 't': retval = T32_Terminate(0);       break;
			case 'r':
				switch (sel[1]) {
					case 'm':
						retval = T32_ReadMemory(address, T32_MEMORY_ACCESS_DATA, (uint8_t *)ui32val, 8);
						if (retval == T32_OK)
							printf("\n\n Read 8 bytes, started at address D:0x%x, data is: 0x%x 0x%x",
													 address, ui32val[0], ui32val[1]);
						break;

					case 'r':
						retval = T32_ReadRegister(0xfc/*reg2-7*/, 0, ui32val/*[2]-[7] are accessed!!*/);
						if (retval == T32_OK) {
							printf("\n\n Read registers R2-R7, content is:");
							for (i = 2; i < 8; i++)
								printf(" 0x%x", ui32val[i]);
						}
						break;

					case 'p':
						retval = T32_ReadPP(ui32val);
						if (retval == T32_OK)
							printf("\n\n Read register ProgramCounter, content is 0x%x.", ui32val[0]);
						break;

					case 'b':
						retval = T32_ReadPP(ui32val);
						if (retval == T32_OK) {
							retval = T32_ReadBreakpoint(ui32val[0], T32_MEMORY_ACCESS_PROGRAM, ui16val, 32);
							if (retval == T32_OK) {
								printf("\n\n Tested for breakpoints at address P:0x%x--0x%x:\n No active breakpoints.",
														  ui32val[0], ui32val[0] + 31);
								for (i = 0; i < 32; i++)
									if (ui16val[i] != 0)
										printf("\r Breakpoint is active at address P:0x%x\n", ui32val[0] + i);
							}
						}
						break;

					default:
						printf("\n\n Invalid selection!");
				}
				break;

			case 'w':
				switch (sel[1]) {
					case 'm':
						rwbuffer[0] ^= 0x70404070; rwbuffer[1] ^= 0x70404070;

						retval = T32_WriteMemory(address, T32_MEMORY_ACCESS_DATA, (uint8_t *)rwbuffer, 8);
						if (retval == T32_OK)
							printf("\n\n Wrote 8 bytes of new data, started at address D:0x%x,\n"
								   " enter 'rm' for readout.", address);
						break;

					case 'p':
						wpbuffer[0] ^= 0x70404070;
						for (i = 1; i < 256; i++)
							wpbuffer[i] = wpbuffer[0];

						T32_WriteMemoryPipe(address, T32_MEMORY_ACCESS_DATA, (uint8_t *)wpbuffer, 1024/*write 1MByte*/);
						retval = T32_WriteMemoryPipe(0, 0, 0, 0/*request retval*/); /*bugfix*/
						if (retval == T32_OK)
							printf("\n\n Wrote 1024 bytes of new data, started at address D:0x%x, "
								   "see TRACE32 Data.Dump window.", address);
						break;

					case 'r':
						ui32val[0] = m++;
						for (i = 2; i < 8; i++)
							ui32val[i] = ui32val[0] + i;

						retval = T32_WriteRegister(0xfc/*reg2-7*/, 0, ui32val/*[2]-[7] are accessed!!*/);
						if (retval == T32_OK)
							printf("\n\n Wrote new data to registers R2-R7, enter 'rr' for readout.");
						break;

					case 'b':
						if ((j == 1) || (pcval == 0xffffffff)) {
							j = 0; /*set*/
							retval = T32_ReadPP(&pcval);
						}
						else
							j = 1; /*delete*/
						if (retval == T32_OK) {
							retval = T32_WriteBreakpoint(pcval,T32_MEMORY_ACCESS_PROGRAM,(j<<8/*set|clr*/)|(1<<4/*rdBP*/)|(1<<3/*wrBP*/),8);
							if (retval == T32_OK)
								retval = T32_WriteBreakpoint(pcval+16,T32_MEMORY_ACCESS_PROGRAM,(j<<8/*set|clr*/)|(1<<0/*progBP*/),1);
							if (retval == T32_OK)
								printf("\n\n %s breakpoints at adresses P:0x%x--0x%x and P:0x%x,\n enter 'rb' for readout.",
													j==1 ? "Deleted" : "Set", pcval, pcval + 7, pcval + 16);
						}
						break;

					default:
						printf("\n\n Invalid selection!");
				}
				break;

			case 'c':
				retval = T32_GetState(&systemstate);
				if (retval == T32_OK) {
					char states[4][8] = {"down", "halted", "stopped", "running"};
					systemstate &= 0x3; /*safeguard the little trick*/
					printf("\n\n Current system state is: %s", states[systemstate]);
				}
				break;

			case 'x':
				for (i = 0; i < 10; i++) {
					retval = T32_Step();
					if (retval == T32_OK) {
						retval = T32_ReadPP(ui32val);
						if (retval == T32_OK)
							printf("\n Performed single step, value of ProgramCounter is 0x%x.", ui32val[0]);
					}
				}
				break;

			case 'j':
				{   uint8_t buffer[4] = {'a','b','c','d'};
					retval = T32_TAPAccessShiftIR(0, 32, buffer, buffer);
					if (retval == T32_OK)
						printf("\n\n Data received from TAP controller is: 0x%02x 0x%02x 0x%02x 0x%02x",
												buffer[0], buffer[1], buffer[2], buffer[3]);
				}
				break;

			case 'T':
			case 'i':
				{   char    states[4][10] = {"off", "armed", "triggered", "breaked"};
					int     num;
					int32_t total, min, max;
					uint8_t buf[20*4];

					for (i = 0; i < 80; i++)
						buf[i] = 0xaa;
											  /*Trace|Integrator*/
					retval = T32_GetTraceState((sel[0]=='T')?0:1, &systemstate, &total, &min, &max);
					if (retval == T32_OK) {
						systemstate &= 0x3; /*safeguard the little trick*/
						printf("\n\n %s state is: %s", (sel[0]=='T')?"Trace":"Integrator", states[systemstate]);
						printf(", total buffer size is %d.\n", total);
						printf(" Trace records range from entry %d to %d, latest ones are:\n", min, max);
						num = (int)((max - min + 1 > 20) ? 20 : max - min + 1);
						if ((num > 0) && (systemstate == 0/*off*/)) {
							retval = T32_ReadTrace((sel[0]=='T')?0:1, max - num + 1, num, 0x10, buf); /* 4 bytes are written to 'buf' for */
							if (retval == T32_OK) {                                                   /* each mask-bit with value '1'     */
								for (i = 0; i < num * 4; i += 4)
									printf("\n Record %3d:  Physical program address: 0x%02x%02x%02x%02x",
										   max - num + 1 + i/4, buf[i+3], buf[i+2], buf[i+1], buf[i]); /* trace data is always little endian */
							}
						}
					}
				}
				break;

			default:
				printf("\n\n Invalid selection!");
		}
		if (retval != T32_OK)
			printf("\n\n !!!Failed to execute remote command!!!");
		printf("\n\n");
	}


	/*** close remote connection (close port used by dos shell application) ************/

	if (T32_Exit() == T32_OK) {
		printf("\n Succeeded to close the remote connection with TRACE32 PowerView.\n\n");
		return EXIT_SUCCESS;
	}
	else {
		printf("\n Failed to close the remote connection with TRACE32 PowerView.\n\n");
		return EXIT_FAILURE;
	}
}


