import wx
import threading
from functools import wraps

def call_after_and_block(func, *args, **kwargs):
 event = threading.Event()

 @wraps(func)
 def wrapper():
  try:
   event.result = func(*args, **kwargs)
  except Exception, e:
   event.exception = e
  finally:
   event.set()
 wx.CallAfter(wrapper)
 event.wait()
 if hasattr(event, 'exception'):
  raise event.exception
 return event.result
