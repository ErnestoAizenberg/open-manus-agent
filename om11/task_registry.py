from tasks.open_url import open_url
from tasks.fill import fill
from tasks.click import click
from tasks.check_checkbox import check_checkbox
from tasks.check_element import check_element
from tasks.check_text import check_text
from tasks.clear_cookies import clear_cookies
from tasks.click_captcha_checkbox import click_captcha_checkbox
from tasks.confirm_registration import confirm_registration
from tasks.extract_code_from_text import extract_code_from_text
from tasks.get_inner_text import get_inner_text
from tasks.go_back import go_back
from tasks.hover import hover
from tasks.load_session import load_session
from tasks.log_registration_result import log_registration_result
from tasks.paste_code import paste_code
from tasks.random_delay import random_delay
from tasks.refresh import refresh
from tasks.save_session import save_session
from tasks.screenshot import screenshot
from tasks.scroll_to import scroll_to
from tasks.select_dropdown import select_dropdown
from tasks.set_user_agent import set_user_agent
from tasks.sleep import sleep
from tasks.solve_captcha import solve_captcha
from tasks.submit_form import submit_form
from tasks.switch_tab import switch_tab
from tasks.uncheck_checkbox import uncheck_checkbox
from tasks.upload_file import upload_file
from tasks.wait_captcha_frame import wait_captcha_frame
from tasks.wait_email import wait_email
from tasks.wait_for import wait_for

task_registry = {
    "open_url": open_url,
    "fill": fill,
    "click": click,
    "check_checkbox": check_checkbox,
    "check_element": check_element,
    "check_text": check_text,
    "clear_cookies": clear_cookies,
    "click_captcha_checkbox": click_captcha_checkbox,
    "confirm_registration": confirm_registration,
    "extract_code_from_text": extract_code_from_text,
    "get_inner_text": get_inner_text,
    "go_back": go_back,
    "hover": hover,
    "load_session": load_session,
    "log_registration_result": log_registration_result,
    "paste_code": paste_code,
    "random_delay": random_delay,
    "refresh": refresh,
    "save_session": save_session,
    "screenshot": screenshot,
    "scroll_to": scroll_to,
    "select_dropdown": select_dropdown,
    "set_user_agent": set_user_agent,
    "sleep": sleep,
    "solve_captcha": solve_captcha,
    "submit_form": submit_form,
    "switch_tab": switch_tab,
    "uncheck_checkbox": uncheck_checkbox,
    "upload_file": upload_file,
    "wait_captcha_frame": wait_captcha_frame,
    "wait_email": wait_email,
    "wait_for": wait_for
}