; --------------------------------------------------------------------------------
; @Title: TRACE32 Remote API - README
; @Description: Readme file for TRACE32 Remote API
; @Author: MOB
; @Copyright: (C) 1989-2017 Lauterbach GmbH, licensed for use with TRACE32(R) only
; --------------------------------------------------------------------------------
; $Id: readme.txt 88249 2017-08-31 06:46:18Z mobermeir $

TRACE32 Remote-API


hrtest:        Console application creating a connection to TRACE32 and
               presenting a menu in the console for sending various API
               commands to TRACE32
               Usage: hrtest <host> [port=<n>]

hrcmd:         Program to sends the PRACTICE command <cmd> from the command
               line to TRACE32 for execution
               Usage: hrtest <host> [port=<n>] <practice-command>

fdxhost:       Host of the FDX feature demontration. See demo/<arch>/fdx for
               the target implementation of FDX. The FDX demos can be executed
               in the TRACE32 instruction set simulator.
               Usage:
               1. Start simulator with API enabled
               2. run fdx.cmm
               3. run fdxhost (fdxhost <host> [port=<n>])
               4. run (Go) application in simulator

notifications: Sample program illustrating the use of notifications in
               the TRACE32 CAPI
               Usage: notifications <host> [port=<n>]

NOTE:          In order to run the demos, TRACE32 has to be started with
               the API port enabled. This can be done by modifying the
               configuration file (see demo\api\capi\config.t32 for
               reference), or by enabling it through T32start
               (Advanced Settings - Interfaces - API Port)
