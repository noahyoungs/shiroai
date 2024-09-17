# backend/main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from urllib.parse import parse_qs
from socketio_setup import socketio_mount
from auth.authorize import authorize
import os
from functools import partial, wraps
import asyncio
import traceback
import decimal

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
from slides.on_disconnect import save_progress as slides_save_progress
from slides.llm import complete as slides_get_completion
from slides.script.generate_script import generate_all_scripts
from slides.notes.generate_notes import generate_all_notes
import logging 
from session_log_config import get_child_logger, set_current_user_id, clear_current_user_id

# Create a logger for this file
logger = get_child_logger(os.path.abspath(__file__), level=logging.INFO)

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_methods=["*"],
    allow_headers=["*"],
)

connected_users = {}

sio = socketio_mount(app)

def with_error_handling(func):
    @wraps(func)
    async def wrapper(sid, *args, **kwargs):
        try:
            user_id = connected_users.get(sid, {}).get('user_id')
            if user_id:
                set_current_user_id(user_id)
            result = await func(sid, *args, **kwargs)
            return result
        except Exception as e:
            error_type = type(e).__name__  # Get the type of exception
            error_message = f"An error occurred: {str(e)}"
            
            # Log the error including the type of the exception
            logger.error(f"Error in {func.__name__} [{error_type}]: {error_message}\n{traceback.format_exc()}")
            
            # Emit the disconnect request with the error message and type
            await sio.emit('disconnect_request', {'reason': f"{error_type}: {error_message}"}, to=sid)
        finally:
            clear_current_user_id()
    return wrapper

async def auth_error_handler(status_code: int, reason: str, sid: str):
    logger.error(f"Authentication failed for session {sid}. Reason: {reason}")
    await sio.emit('disconnect_request', {'reason': reason}, to=sid)

async def updateInterface(sid, data):
    logger.info(f"Updating interface for session {sid}")
    connected_users[sid]["interface_data"] = data
    await sio.emit('interface_update', data, to=sid)

def convert_decimal_to_float(data):
    if isinstance(data, dict):
        return {k: convert_decimal_to_float(v) for k, v in data.items()}
    elif isinstance(data, list):
        return [convert_decimal_to_float(i) for i in data]
    elif isinstance(data, decimal.Decimal):
        return float(data)
    else:
        return data


@sio.event
async def connect(sid, environ):
    print(f"Client {sid} connected")
    
    query_string = environ.get('QUERY_STRING', '')
    query_params = parse_qs(query_string)
    presentation_id = query_params.get('presentationID', [None])[0]
    interface = query_params.get('interface_name', [None])[0]
    
    print(f"Presentation ID: {presentation_id}")
    print(f"Interface: {interface}")
    
    connected_users[sid] = {
        "presentation_id": presentation_id,
        "interface": interface,
        "interface_data": {},
        "messages": [],
        "userID": "",
        "memory": {},
        "loadingInterface": False,
    }
    
    cookie_str = environ.get('HTTP_COOKIE', '')
    
    user_id = await authorize(cookie_str, partial(auth_error_handler, sid=sid))
    
    if not user_id:
        return

    print(f"User {user_id} authorized for session {sid}")
    connected_users[sid]["user_id"] = user_id
    set_current_user_id(user_id)
    
    try:
        if connected_users[sid]["interface"] == "ideate" or connected_users[sid]["interface"] == "new":    
            connected_users[sid]["messages"], connected_users[sid]["interface_data"], connected_users[sid]["memory"] = await ideate_initialize(user_id, presentation_id)
        elif connected_users[sid]["interface"] == "research":
            connected_users[sid]["messages"], connected_users[sid]["interface_data"], connected_users[sid]["memory"] = await research_initialize(user_id, presentation_id)
        elif connected_users[sid]["interface"] == "outline":
            connected_users[sid]["messages"], connected_users[sid]["interface_data"], connected_users[sid]["memory"] = await outline_initialize(user_id, presentation_id)
        elif connected_users[sid]["interface"] == "slides":
            connected_users[sid]["messages"], connected_users[sid]["interface_data"], connected_users[sid]["memory"]= await slides_initialize(user_id, presentation_id, emit=partial(sio.emit, to=sid))
        else:
            raise ValueError(f"Interface not found: `{connected_users[sid]['interface']}`")
        
        messagesToSend = [message for message in connected_users[sid]["messages"] if message['role'] != 'system' and message['role'] != 'function']
        
        logger.info(f"Emitting initial messages for user {user_id}")
        await sio.emit('initMessages', messagesToSend, to=sid)
        await sio.emit('interface_update', convert_decimal_to_float(connected_users[sid]["interface_data"]), to=sid)
        
        if connected_users[sid]["interface"] == "outline" and connected_users[sid]["interface_data"]['all_topics'] is None:
            asyncio.create_task(outline_load_topics(user_id, presentation_id, connected_users[sid]["messages"], connected_users[sid]["interface_data"], connected_users[sid]["memory"], emitter=partial(sio.emit, to=sid)))
        
        if connected_users[sid]["interface"] == "slides" and not connected_users[sid]["interface_data"]['slides_created']:
            asyncio.create_task(slides_load_slides(presentation_id=presentation_id, messages=connected_users[sid]["messages"], memory=connected_users[sid]["memory"], emitter=partial(sio.emit, to=sid)))
    
    except Exception as e:
        error_type = type(e).__name__  # Get the type of exception
        error_message = f"An error occurred during connection: {error_type} {str(e)}"
        logger.error(f"Error for user {user_id}: {error_message}\n{traceback.format_exc()}")
        await sio.emit('disconnect_request', {'reason': error_message}, to=sid)
    finally:
        clear_current_user_id()

@sio.event
@with_error_handling
async def message(sid, data):
    logger.info(f"Client {sid} sent message: {data}")
    connected_users[sid]["messages"].append(data)
    
    if not data.get('role') == 'user':
        return
    
    if connected_users[sid]["interface"] == "ideate" or connected_users[sid]["interface"] == "new":
        connected_users[sid]["messages"], completion_messages, proceed = await ideate_get_completion(
            connected_users[sid]["messages"],
            connected_users[sid]["interface"],
            connected_users[sid]["interface_data"],
            updateInterface=partial(updateInterface, sid),
            user=connected_users[sid]["userID"],
            presentation_id=connected_users[sid]["presentation_id"],
            memory=connected_users[sid]["memory"]
        )
    elif connected_users[sid]["interface"] == "research":
        while connected_users[sid]["loadingInterface"]:
            logger.info("Waiting for interface update...")
            await asyncio.sleep(0.5)
    
        connected_users[sid]["messages"], completion_messages, proceed = await research_get_completion(
            connected_users[sid]["presentation_id"],
            connected_users[sid]["messages"],
            connected_users[sid]["interface_data"],
            partial(sio.emit, to=sid),
            memory=connected_users[sid]["memory"],
        )
        
    elif connected_users[sid]["interface"] == "outline":
        connected_users[sid]["messages"], completion_messages, proceed = await outline_get_completion(
            connected_users[sid]["presentation_id"],
            connected_users[sid]["messages"],
            connected_users[sid]["interface_data"],
            emitter=partial(sio.emit, to=sid),
            memory=connected_users[sid]["memory"]
        )
    
    elif connected_users[sid]["interface"] == "slides":
        connected_users[sid]["messages"], completion_messages, proceed = await slides_get_completion(
            presentation_id=connected_users[sid]["presentation_id"],
            messages=connected_users[sid]["messages"],
            emitter=partial(sio.emit, to=sid),
            memory=connected_users[sid]["memory"],
            interface_data=connected_users[sid]["interface_data"],
            max_turns=5
        )
    
    else:
        raise ValueError("Interface not found")
    
    for completion_message in completion_messages:
        await sio.emit('message', completion_message, to=sid)
        
    if proceed:
        await sio.emit('proceed', to=sid)

@sio.event
@with_error_handling
async def interface_update(sid, data):
    logger.info(f"Client {sid} requested interface data update: {str(data)[:100]}")
    if connected_users[sid]["interface"] == "ideate":
        connected_users[sid]["interface_data"] = data
    elif connected_users[sid]["interface"] == "research":

        logger.info("Updating interface...")
        connected_users[sid]["loadingInterface"] = True
        connected_users[sid]["interface_data"] = await research_interface_update(
            connected_users[sid]["presentation_id"],
            connected_users[sid]["interface_data"],
            data)
        if data['action'] == 'refresh_upload':
            async def read_or_summarize_done():
                connected_users[sid]["interface_data"] = await research_interface_update(
                    connected_users[sid]["presentation_id"],
                    connected_users[sid]["interface_data"],
                    {'action': 'refresh'}
                )
                await sio.emit('interface_update', convert_decimal_to_float(connected_users[sid]["interface_data"]), to=sid)

            reading_tasks = []

            for source in connected_users[sid]["interface_data"]['sources']:
                if 'summary' not in source and 'reading_and_summarizing' not in source:
                    reading_task = asyncio.create_task(read_and_summarize_source(
                        source,
                        connected_users[sid]["presentation_id"],
                        read_or_summarize_done
                    ))
                    reading_tasks.append(reading_task)
                    source['reading_and_summarizing'] = True

            await asyncio.gather(*reading_tasks)
            await read_or_summarize_done()

        connected_users[sid]["loadingInterface"] = False
        logger.info("Interface updated")
        await sio.emit('interface_update', convert_decimal_to_float(connected_users[sid]["interface_data"]), to=sid)
    elif connected_users[sid]["interface"] == "outline":
        connected_users[sid]["interface_data"]['outline'] = data['outline']
    elif connected_users[sid]["interface"] == "slides":
        push_value = data.pop('push', None)
        other_keys = data
        
        if push_value:
            logger.info(f"Pushing slides: {push_value}")
            if push_value == '*':
                logger.error("Error: Pushing all slides not implemented yet.")
            else:
                try:
                    # Convert push_value to a list if it's a string
                    slide_ids = [push_value] if isinstance(push_value, str) else push_value

                    if not all(isinstance(x, str) for x in slide_ids):
                        raise ValueError("Push value must be a string or a list of strings")

                    logger.info(f"Fetching slides with IDs: {slide_ids}")
                    await connected_users[sid]["memory"]["slide_list"].fetch_slides(slide_ids)
                    await sio.emit('update_complete', {'status': 'success', 'slide_ids': slide_ids}, to=sid)
                    logger.info(f"Successfully pushed slides: {slide_ids}")
                    
                except Exception as e:
                    error_msg = f"Error pushing slides: {str(e)}\n{traceback.format_exc()}"
                    await sio.emit('update_complete', {'status': 'error', 'message': str(e)}, to=sid)
                    logger.error(error_msg)
        
        connected_users[sid]["interface_data"].update(other_keys)
        
        if data.get('script', {}).get('status', {None}) == 'requested':
            await generate_all_scripts(
                psl=connected_users[sid]["memory"]["slide_list"],
                style_key=data.get('script', {}).get('style_key', 0),
                custom_style=data.get('script', {}).get('custom_style', None),
                max_char_per_slide=data.get('script', {}).get('max_char_per_slide', None),
                interface_data=connected_users[sid]["interface_data"],
                emitter=partial(sio.emit, event='interface_update', to=sid)
            )
        if data.get('notes', {}).get('status', {None}) == 'requested':
            logger.info("Notes generation is not implemented")
    else:
        raise ValueError("Interface not found")
    
@sio.event
@with_error_handling
async def disconnect(sid):
    logger.info(f"Client {sid} disconnected")
    
    if connected_users[sid]["interface"] == "ideate" or connected_users[sid]["interface"] == "new":
        await ideate_save_progress(
            connected_users[sid]["presentation_id"],
            connected_users[sid]["messages"],
            connected_users[sid]["interface_data"],
            connected_users[sid]["memory"]
        )
    elif connected_users[sid]["interface"] == "research":
        await research_save_progress(
            connected_users[sid]["presentation_id"],
            connected_users[sid]["messages"],
            connected_users[sid]["interface_data"],
            connected_users[sid]["memory"]
        )
    elif connected_users[sid]["interface"] == "outline":
        await outline_save_progress(
            connected_users[sid]["presentation_id"],
            connected_users[sid]["messages"],
            connected_users[sid]["interface_data"],
            connected_users[sid]["memory"]
        )
    elif connected_users[sid]["interface"] == "slides":
        await slides_save_progress(
            connected_users[sid]["presentation_id"],
            connected_users[sid]["messages"],
            connected_users[sid]["interface_data"],
            connected_users[sid]["memory"]
        )
    else:
        raise ValueError("Interface not found")
    
    connected_users.pop(sid, None)
    logger.info(f"Client {sid} removed from connected users")