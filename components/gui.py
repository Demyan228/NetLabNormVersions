import asyncio
from time import time
from common import log
import config
from event_system import EventSystem as es
from aioconsole import ainput
from dearpygui import dearpygui as dpg


class GUI:

    _is_running = True
    _last_render_time = time()
    max_delay = 1 / config.FPS
    model_params = None
    is_train_start = False

    @staticmethod
    def init():
        dpg.create_context()
        dpg.create_viewport(title='Custom Title', width=800, height=700)
        dpg.setup_dearpygui()
        dpg.set_global_font_scale(3)



        with dpg.window(label="Example Window", width=500, height=300):
            dpg.add_text("Hello, world")
            dpg.add_input_text(tag="model_params", label="string", default_value="Linear 16 32")
            dpg.add_slider_float(tag="lr", label="lr", default_value=0.01, max_value=1)
            dpg.add_button(label="Assemble", callback=GUI.assemble_callback)
            dpg.add_text("Setting parameters", tag="status")




    
    @staticmethod
    async def _delay():
        delta = time() - GUI._last_render_time
        delay = max(0, GUI.max_delay - delta)
        await asyncio.sleep(delay)
        GUI._last_render_time = time()

    @staticmethod
    async def update():
        dpg.show_viewport()
        while dpg.is_dearpygui_running():
            await GUI._delay()
            dpg.render_dearpygui_frame()
        es.invoke("APP_QUIT_EVENT", {})


    @staticmethod
    def assemble_callback():
        lr = dpg.get_value("lr")
        model_params = dpg.get_value("model_params").split()
        es.invoke("SET_HYPERPARAMS", {"lr": lr})
        es.invoke("ASSEMBLE_MODEL_EVENT", {"model_params": model_params})


    @staticmethod
    @es.subscribe('APP_START_EVENT')
    async def run(_):
        GUI.init()
        loop = asyncio.get_running_loop()
        loop.create_task(GUI.update())

    @staticmethod
    @es.subscribe('BATCH_DONE_EVENT')
    async def print_batch_info(info):
        dpg.set_value("status", f'[{info["index"]} BATCH TRAINED]')

    @staticmethod
    @es.subscribe('APP_QUIT_EVENT')
    async def quit_handler(event_data):
        GUI._is_running = False
        dpg.destroy_context()
        log('GUI QUIT')
