/* *********************************************************************************************
 * @Title: Sample program that send PRACTICE command <cmd> from the command line.
 * @Description:
 * The program creates a connection to TRACE32 and sends the PRACTICE
 * command <cmd> from the command line to TRACE32 for execution.
 *
 * The port on which TRACE32 listens for API connections can optionally be
 * set with the port=<n> parameter. The port number must match with
 * the definition in config.t32. The default value is 20000.
 *
 *
 * a binary of this sample can be found in t32/bin/<arch>/
 *
 * Syntax:  t32rem [<ip-address> | <hostname>] [port=<number>] [command]
 *
 * Example: t32rem localhost port=20002 break.set main
 *          t32rem localhost port=20002 break.list
 *
 *          Will open set a break point at "main" and open
 *          the break point window.
 *
 * $Id: t32rem.c 73229 2016-05-17 09:17:23Z mobermeir $
 * $LastChangedRevision: 73229 $
 * $LastChangedBy: mobermeir $
 *
 * @Copyright: (C) 1989-2014 Lauterbach GmbH, licensed for use with TRACE32(R) only
 * *********************************************************************************************
 * $Id: t32rem.c 73229 2016-05-17 09:17:23Z mobermeir $
 */



#include "t32.h"

#if defined(_MSC_VER)
# pragma warning( push )
# pragma warning( disable : 4255 )
#endif

#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#if defined(_MSC_VER)
# pragma warning( pop )
#endif

int main(int argc, char **argp)
{
	int      argn;
	char     cmd[2048];
	uint16_t mode;

	if ( argc < 2 )
	{
			printf( "usage: t32rem <host> [port=<n>] <cmd>\n" );
			exit(2);
	}

	if ( T32_Config( "NODE=", argp[1] ) == -1 )
	{
			printf( "hostname %s not accepted\n", argp[1] );
			exit(2);
	}

	argn = 2;

	if ( argc >= 3 && ((!strncmp(argp[2],"port=", 5)) || (!strncmp(argp[2],"PORT=", 5))))
	{
			if ( T32_Config( "PORT=", argp[2]+5 ) == -1 )
			{
				printf( "port number %s not accepted\n", argp[2] );
				exit(2);
			}
			argn++;
	}

	strcpy( cmd, "" );
	while ( argn < argc )
	{
			if ( (strlen(cmd)+strlen(argp[argn])+1) > (sizeof(cmd)-1) ) {
				printf( "actual command line exceeds maximum internal bufferlength of %d\n", (int)sizeof(cmd)-1 );
				exit(2);
			}
			strcat( cmd, argp[argn] );
			strcat( cmd, " " );
			argn++;
	}

	if ( T32_Init() == -1 )
	{
			printf( "error initializing TRACE32\n" );
			exit(2);
	}

	if (T32_Attach(1) != 0)
	{
			printf("error no device\n");
			exit(2);
	}

	if ( T32_Nop() == -1 )
			goto error;

	if ( T32_Stop() == -1 )
			goto error;

	if ( T32_Cmd( cmd ) == -1 )
			goto error;

	if ( T32_GetMessage( cmd, &mode ) == -1 )
			goto error;

	printf( "command returned ");
	if (mode & 1)
		printf ("General Information, ");
	if (mode & 2)
		printf ("Error, ");
	if (mode & 8)
		printf ("Status Information, ");
	if (mode & 16)
		printf ("Error Information, ");
	if (mode & 32)
		printf ("Temporary Display, ");
	if (mode & 64)
		printf ("Temporary Information, ");
	if (mode & 128)
		printf ("Empty, ");

	printf ("message: %s\n", cmd);

	T32_Exit();

	return 0;

error:
	printf( "error accessing TRACE32\n" );
	T32_Exit();
	return 1;
}


