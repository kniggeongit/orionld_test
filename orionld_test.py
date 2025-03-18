#!/usr/bin/python3

# Software Name: orionld_test
# SPDX-FileCopyrightText: Copyright (c) 2024 Christian Wiese
# SPDX-License-Identifier: 	GPL-3.0-or-later
#
# Author: Christian Wiese <christian.wiese@web.de> et al.
#
# this application creates so many entities until the orion-ld context broker can't read entities behind a threshold
# this applications shows the threshold


import sys, argparse, time,  random

# https://github.com/Orange-OpenSource/python-ngsild-client
import ngsildclient

__TEST_ENTITY_TYPE__    = "TestEntity"
__CONTEXT__             = "https://raw.githubusercontent.com/smart-data-models/dataModel.Parking/master/context.jsonld"
__URN_PREFIX__          = f"urn:ngsi-ld:{__TEST_ENTITY_TYPE__}"

def create_array_of_entities(urn_prefix, context, count, offset:int=0):
    arEntities = []
    for i in range(count):
        nr          = offset + i 
        e_id        = f"{urn_prefix}:{nr}" # "urn:ngsi-ld:TestEntity:1"
        e      = ngsildclient.Entity(__TEST_ENTITY_TYPE__, e_id)
        e.ctx.append(context)
        e.prop("name", f"Test entity No {nr}")
        e.loc( float("%3.6f"%random.uniform(10, 20)), float("%3.6f"%random.uniform(40, 50)))
        arEntities.append(e)
    return arEntities

def query_entities(offset, limit):
    response = client.entities._query(type=__TEST_ENTITY_TYPE__, ctx=context, limit=limit, offset=offset)
    return response

def handle_error(offset, limit, recursion=0 ):

    if limit == 1 :
        
        last_id = None
        iOffset = offset - 1
        
        while True:
            
            arEntitiesRead  = query_entities(offset=iOffset, limit=1)
            iCount          = len(arEntitiesRead)
            
            if len(arEntitiesRead) == 0 : 
                last_id = iOffset
                print(f"test with offset={iOffset} limit=1 FAIL")
                break
            else:
                print(f"test with offset={iOffset} limit=1 OK")
                iOffset += 1

        print(f"endpoint found @ offset={last_id} limit={limit}")
        print(f"can't request entities of type {__TEST_ENTITY_TYPE__} with offset values > %d"%(last_id-1))

    else:

        iOffset = offset
        iLimit  = limit

        while True:
            
            print(f"test with offset={offset} limit={limit}")
            arEntitiesRead  = query_entities(offset=iOffset, limit=iLimit)

            if len(arEntitiesRead) == 0 :
                iLimit      = int(iLimit/2)
                recursion   += 1
                last_id = handle_error(offset=iOffset, limit=iLimit, recursion=recursion )
                break
            
            iOffset     = iOffset + iLimit
            iLimit      = iLimit

            arEntitiesRead  = query_entities(offset=iOffset, limit=iLimit)

            if len(arEntitiesRead) == 0 :
                iLimit      = int(iLimit/2)
                recursion   += 1
                last_id = handle_error(offset=iOffset, limit=iLimit, recursion=recursion )
                break
    
    return last_id

def sec_2_string(seconds):
    hours, rem      = divmod(seconds, 3600)
    min, sec        = divmod(rem, 60)
    txt             = f"{hours:02.0f}:{min:02.0f}:{sec:02.0f}" 
    return txt

if __name__ == "__main__":
    
    argparser   = argparse.ArgumentParser()
    
    argparser.add_argument("--hostname",        type=str,   default="192.168.1.111",    help="orion-ld hostname")
    argparser.add_argument("--port",            type=int,   default=1026,               help="orion-ld port number")
    #argparser.add_argument("--token",           type=str,   default=None,              help="access token (Bearer token)")
    argparser.add_argument('--delete',          action='store_true', default=False,     help="delete test entities")
    argparser.add_argument("--urn_prefix",      type=str,   default=__URN_PREFIX__,     help=f"urn postfix like 'urn:ngsi-ld:{__TEST_ENTITY_TYPE__}' for the entities")
    argparser.add_argument("--context",         type=str,   default=__CONTEXT__,        help="context link")
    argparser.add_argument("--log",             type=int, default=0,                    help="logging level")
    
    args            = argparser.parse_args()

    hostname        = args.hostname
    port            = args.port
    #token           = args.token
    urn_prefix      = args.urn_prefix
    context         = args.context
    bDeleteEntities = args.delete
    log             = args.log

    client = ngsildclient.Client( hostname=hostname, port=port )
    
    #########################
    #
    # Create entities
    #
    #########################
    
    iTestLimitMax   = 1000000
    iStep           = 1000
    iOffset         = 0   

    while iOffset < iTestLimitMax :
        
        print(f"---- offset: {iOffset} step: {iStep} ----")
        ts_start_loop   = time.time()
        
        arEntities      = create_array_of_entities( urn_prefix=urn_prefix, context=context, count=iStep, offset=iOffset )
        
        response        = client.create(arEntities)
        ts_create       = time.time()
        elapesed_time   = ts_create - ts_start_loop
        
        arEntitiesRead  = query_entities(offset=iOffset, limit=iStep)
        
        if len(arEntitiesRead) == 0 :
            print("========================= error detected: read 0 entities ========================")
            err_id = handle_error(offset=iOffset, limit=iStep)
            break
            
        ts_end_loop     = time.time()
        elapesed_time   = ts_end_loop - ts_create 
        print(f"read count=%s  query_time=%3.1f sec"%(len(arEntitiesRead),elapesed_time))
        
        elapesed_time   = ts_end_loop - ts_start_loop 
        iOffset         = iOffset + iStep
        iToDo           = iTestLimitMax - iOffset
        iRounds         = iToDo/iStep
        iExpTime        = iRounds * elapesed_time
        sTime           = sec_2_string(iExpTime)
        print(f"loop_time={elapesed_time:3.1f} sec --> for next {iToDo} entities, I need ca {sTime}" )
        

    #########################
    #
    # Delete entities
    #
    #########################

    if bDeleteEntities :
        iDeleteRound_Counter    = 1
        iDelete_Counter         = 0
        while True :
            arEntitiesRead  = query_entities(offset=0, limit=iStep)
            print(f"delete round {iDeleteRound_Counter} with {len(arEntitiesRead)} entities")
            
            if len(arEntitiesRead) == 0: break
            
            iDelete_Counter = iDelete_Counter + len(arEntitiesRead)
            response = client.delete(arEntitiesRead)
            print(response)
            
        print(f"delete loop ends : {iDelete_Counter} entities deleted")


    print("---end---")
