#main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from urllib.parse import parse_qs
import http.cookies
from socketio_setup import socketio_mount  
from auth.authorize import authorize 
import functools
import asyncio

from ideate.llm import get_completion as ideate_get_completion
from ideate.on_connect import initialize as ideate_initialize
from ideate.on_disconnect import save_progress as ideate_save_progress

from research.llm import complete as research_get_completion
from research.on_connect import initialize as research_initialize
from research.on_disconnect import save_progress as research_save_progress
from research.interface_update import interface_update as research_interface_update
from research.read import read_and_summarize_source

from outline.on_connect import initialize as outline_initialize
from outline.on_disconnect import save_progress as outline_save_progress
from outline.llm import complete as outline_get_completion
from outline.load_topics import load_topics as outline_load_topics

from slides.on_connect import initialize as slides_initialize
from slides.load_slides import load_slides as slides_load_slides


app = FastAPI()

app.add_middleware(
    # Origins and credentials are not needed here because their in socketio_setup
    CORSMiddleware,
    allow_methods=["*"],
    allow_headers=["*"],
)

connected_users = {}

sio = socketio_mount(app)  # Ensure you have implemented socketio_mount in socketio_setup module

async def handleDisconnect(sid, reason="Unauthorized"):
    await sio.emit('disconnect_request', {'reason': reason}, room=sid)
    # await sio.disconnect(sid)
    
async def updateInterface(sid, data):
    connected_users[sid]["interfaceData"] = data
    await sio.emit('interface_update', data, room=sid)
    
@sio.event
async def connect(sid, environ):
    print(f"Client {sid} connected")
    
    # Parse query params
    query_string = environ.get('QUERY_STRING', '')
    query_params = parse_qs(query_string)
    presentationID = query_params.get('presentationID', [None])[0]
    interface = query_params.get('interface_name', [None])[0]
    
    print(f"Presentation ID: {presentationID}")
    print(f"Interface: {interface}")
    
    # Store the connection params
    connected_users[sid] = {
        "presentationID": presentationID,
        "interface": interface,
        "interfaceData": {},
        "messages": [],
        "userID": "",
        "memory": {},
        "loadingInterface": False,
    }
    
    # Authorization based on cookie
    cookie_str = environ.get('HTTP_COOKIE', '')
    cookies = http.cookies.SimpleCookie()
    cookies.load(cookie_str)
    
    accessToken = cookies.get("next-auth.session-token", None).value if cookies else None
    
    if accessToken:
        isAuthorized, isAuthenticated, userID = await authorize(presentationID, accessToken)
        if not isAuthenticated:
            await handleDisconnect(sid, "Authentication issue. Please try logging out and logging back in.")
            return
        if not isAuthorized:
            await handleDisconnect(sid, "Authorization issue. Please try logging out and logging back in.")
            return
        print(f"Access token validated for {sid}")
    else:
        print("Access token not found or invalid.")
        await handleDisconnect(sid, "Authorization issue, access token not found. Please try logging out and logging back in.")
        return
    
    # AUTHORIZATION SUCCESSFUL
    
    # Set userID
    connected_users[sid]["userID"] = userID
    
    # Initialize messages and interface
    if connected_users[sid]["interface"] == "ideate" or connected_users[sid]["interface"] == "new":    
        connected_users[sid]["messages"], connected_users[sid]["interfaceData"], connected_users[sid]["memory"] = await ideate_initialize(presentationID)
    elif connected_users[sid]["interface"] == "research":
        connected_users[sid]["messages"], connected_users[sid]["interfaceData"], connected_users[sid]["memory"] = await research_initialize(presentationID)
    elif connected_users[sid]["interface"] == "outline":
        connected_users[sid]["messages"], connected_users[sid]["interfaceData"], connected_users[sid]["memory"] = await outline_initialize(presentationID)
    elif connected_users[sid]["interface"] == "slides":
        connected_users[sid]["messages"], connected_users[sid]["interfaceData"], connected_users[sid]["memory"], connected_users[sid]["all_docs"] = await slides_initialize(presentationID)
        
    else:
        raise ValueError(f"Interface not found: `{connected_users[sid]['interface']}`")
        
    # filter out system and function messages
    messagesToSend = [message for message in connected_users[sid]["messages"] if message['role'] != 'system' and message['role'] != 'function']
    
    # print(f"Messages to send: {messagesToSend}")
    print(f"Emitting initial messages")
    await sio.emit('initMessages', messagesToSend, room=sid)
    await sio.emit('interface_update', connected_users[sid]["interfaceData"], room=sid)
    
    # for outline we have to do extra work before first user message
    if connected_users[sid]["interface"] == "outline" and connected_users[sid]["interfaceData"]['all_topics'] is None:
        # load topics, send emitter as a partial function to emit to the room when done
        asyncio.create_task(outline_load_topics(presentationID, connected_users[sid]["messages"], connected_users[sid]["interfaceData"], connected_users[sid]["memory"], emitter=functools.partial(sio.emit, room=sid)))
        
    # for slides we have to do extra work before first user message
    if connected_users[sid]["interface"] == "slides" and not connected_users[sid]["interfaceData"]['slides_created']:
        # load topics, send emitter as a partial function to emit to the room when done
        asyncio.create_task(slides_load_slides(presentationID=presentationID, messages=connected_users[sid]["messages"], interfaceData=connected_users[sid]["interfaceData"], memory=connected_users[sid]["memory"], emitter=functools.partial(sio.emit), all_docs=connected_users[sid].get("all_docs")))
        

@sio.event
async def message(sid, data):
    print(f"Client {sid} sent message: {data}")
    new_message = {"role": "user", "content": data}
    connected_users[sid]["messages"].append(new_message)
    print(f"New message: {new_message}")
    await sio.emit('message', new_message, room=sid)
    
    # Route based on interface
    if connected_users[sid]["interface"] == "ideate" or connected_users[sid]["interface"] == "new":
        connected_users[sid]["messages"], completion_messages, proceed = await ideate_get_completion(
            connected_users[sid]["messages"],
            connected_users[sid]["interface"],
            connected_users[sid]["interfaceData"],
            updateInterface=lambda dataparam: updateInterface(sid, dataparam),
            user=connected_users[sid]["userID"],
            presentationID=connected_users[sid]["presentationID"],
            memory=connected_users[sid]["memory"]
        )
    elif connected_users[sid]["interface"] == "research":
        
        while connected_users[sid]["loadingInterface"]:
            print("Waiting for interface update...")
            await asyncio.sleep(0.5)
    
        connected_users[sid]["messages"], completion_messages, proceed = await research_get_completion(
            connected_users[sid]["presentationID"],
            connected_users[sid]["messages"],
            connected_users[sid]["interfaceData"],
            functools.partial(sio.emit, room=sid),
            memory=connected_users[sid]["memory"],
        )
        
    elif connected_users[sid]["interface"] == "outline":
        
        connected_users[sid]["messages"], completion_messages, proceed = await outline_get_completion(
            connected_users[sid]["presentationID"],
            connected_users[sid]["messages"],
            connected_users[sid]["interfaceData"],
            emitter=functools.partial(sio.emit, room=sid),
            memory=connected_users[sid]["memory"]
        )
    
    elif connected_users[sid]["interface"] == "slides":
        pass
    
    else:
        raise ValueError("Interface not found")
    for completion_message in completion_messages:
        await sio.emit('message', completion_message, room=sid)
    if proceed:
        await sio.emit('proceed', room=sid)

@sio.event
async def interface_update(sid, data):
    print(f"Client {sid} requested interface data update: {str(data)[:100]}")
    if connected_users[sid]["interface"] == "ideate":
        connected_users[sid]["interfaceData"] = data
    elif connected_users[sid]["interface"] == "research":
        print("Updating interface...")
        connected_users[sid]["loadingInterface"] = True
        connected_users[sid]["interfaceData"] = await research_interface_update(
            connected_users[sid]["presentationID"],
            connected_users[sid]["interfaceData"],
            data)
        if data['action'] == 'refresh_upload':
            # callback for after summarizing is done
            async def read_or_summarize_done():
                connected_users[sid]["interfaceData"] = await research_interface_update(
                    connected_users[sid]["presentationID"],
                    connected_users[sid]["interfaceData"],
                    {'action': 'refresh'}
                )
                await sio.emit('interface_update', connected_users[sid]["interfaceData"], room=sid)

            # create a list to store the reading tasks
            reading_tasks = []

            # for each source in interfaceData['sources'] with no summary
            for source in connected_users[sid]["interfaceData"]['sources']:
                if 'summary' not in source and 'reading_and_summarizing' not in source:
                    # create a task for reading and add it to the list
                    reading_task = asyncio.create_task(read_and_summarize_source(
                        source,
                        connected_users[sid]["presentationID"],
                        read_or_summarize_done
                    ))
                    reading_tasks.append(reading_task)
                    source['reading_and_summarizing'] = True

            # wait for all reading tasks to complete
            await asyncio.gather(*reading_tasks)

            # run the callback code after all reading tasks are finished
            await read_or_summarize_done()

        connected_users[sid]["loadingInterface"] = False
        print("Interface updated")
        await sio.emit('interface_update', connected_users[sid]["interfaceData"], room=sid)
    elif connected_users[sid]["interface"] == "outline":
        # if connected_users[sid]['interfaceData']['all_topics'] == None:
        #     print(f"main 215 Interface Data all_topics none")
        # else:
        #     print(f"main 216 Interface Data all_topics length: {len(connected_users[sid]['interfaceData']['all_topics'])}")
        connected_users[sid]["interfaceData"]['outline'] = data['outline']
        # print(f"Outline updated: {connected_users[sid]['interfaceData']['outline']}")
    elif connected_users[sid]["interface"] == "slides":
        pass
    else:
        raise ValueError("Interface not found")
    
@sio.event
async def disconnect(sid):
    print(f"Client {sid} disconnected")
    
    if connected_users[sid]["interface"] == "ideate" or connected_users[sid]["interface"] == "new":
        await ideate_save_progress(
            connected_users[sid]["presentationID"],
            connected_users[sid]["messages"],
            connected_users[sid]["interfaceData"],
            connected_users[sid]["memory"]
        )
    elif connected_users[sid]["interface"] == "research":
        await research_save_progress(
            connected_users[sid]["presentationID"],
            connected_users[sid]["messages"],
            connected_users[sid]["interfaceData"],
            connected_users[sid]["memory"]
        )
    elif connected_users[sid]["interface"] == "outline":
        await outline_save_progress(
            connected_users[sid]["presentationID"],
            connected_users[sid]["messages"],
            connected_users[sid]["interfaceData"],
            connected_users[sid]["memory"]
        )
        pass
    else :
        raise ValueError("Interface not found")
    
    connected_users.pop(sid, None)
    print(f"Client {sid} removed from connected users")
